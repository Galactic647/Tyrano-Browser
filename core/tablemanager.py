import hashlib
import struct
import json
import os


def to_varint(x: int, signed=False) -> bytes:
    if signed:
        x = (x << 1) ^ (x >> 31)

    if x < 0x7F:
        return x.to_bytes(1, byteorder='big')

    result = list()

    while True:
        value = x & 0x7F
        x >>= 7

        if x:
            result.append(value | 0x80)
        else:
            result.append(value)
            break
    return bytes(result)

def from_varint(data, signed=False) -> int:
    value = 0
    for shift, byte in enumerate(data):
        flag = byte >> 7
        v = byte & 0x7F
        if flag:
            if not value:
                value = v
            else:
                value = (v << (shift * 7)) | value
        else:
            value = (v << (shift * 7)) | value
            break
    if signed:
        return (value >> 1) ^ -(value & 1)
    return value

def from_varint_file(file, signed=False):
    value = 0
    extra = 0
    while True:
        byte = int.from_bytes(file.read(1), byteorder='big')
        flag = byte >> 7
        v = byte & 0x7F
        if flag:
            if not value:
                value = v
            else:
                value = (v << (extra * 7)) | value
            extra += 1
        else:
            value = (v << (extra * 7)) | value
            break
    if signed:
        return (value >> 1) ^ -(value & 1)
    return value


# Save File Binary Format
# Header
# - [9 bytes] Magic Header: "TBR-CTLBF"
# - [5 bytes] Version: e.g. "1.0.0"
# - [32 bytes] Hash: SHA256 hash of the data
# - [1+ byte] Item count varint (unsigned)

# Item Structure
# - [1 byte] Is header
# - [1+ byte] Name length varint (unsigned)
# - [Name length bytes] Name string
# - If not header
#   - [1 byte] Path type: 0 = f, 1 = tf, 2 = sf
#   - [1+ byte] Path length varint (unsigned)
#   - [Path length bytes] Path string
#   - [1 byte] Data type: 0 = null/none, 1 = string, 2 = int/varint, 3 = float, 4 = bool
#   - if type == 1
#     - [1+ byte] Data length varint (unsigned)
#     - [Data length bytes] Data string
#   - if type == 2
#     - [1+ bytes] Data varint (signed)
#   - if type == 3
#     - [8 bytes] Data float
#   - if type == 4
#     - [1 byte] Data bool
# - [3 bytes] RGB color
# - [1 byte] Has children
# - if has children:
#   - [1+ byte] Child count varint (unsigned)
# - Repeat structure


def _save_table(f, item: list):
    is_header = 1 if not item['path'] and not item['value'] else 0
    f.write(is_header.to_bytes(1, byteorder='big'))

    name = item['name']
    f.write(to_varint(len(name)))
    f.write(name.encode('utf-8'))

    if not is_header:
        path = item['path']
        ptype = path.split('.')[1]
        path = '.'.join(path.split('.')[2:])

        if ptype == 'f':
            ptype = 0
        elif ptype == 'tf':
            ptype = 1
        elif ptype == 'sf':
            ptype = 2
        else:
            raise Exception(f'Unknown path type {ptype}')

        f.write(ptype.to_bytes(1, byteorder='big'))
        f.write(to_varint(len(path)))
        f.write(path.encode('utf-8'))

        value = item['value']
        try:
            value = json.loads(value)
        except json.JSONDecodeError:
            pass

        if value is None:
            dtype = 0
        elif isinstance(value, str):
            dtype = 1
        elif isinstance(value, int):
            dtype = 2
        elif isinstance(value, float):
            dtype = 3
        elif isinstance(value, bool):
            dtype = 4
        else:
            raise TypeError(f'Unknown type {type(value)}')

        f.write(dtype.to_bytes(1, byteorder='big'))

        if dtype == 1:
            f.write(to_varint(len(value)))
            f.write(value.encode('utf-8'))
        elif dtype == 2:
            f.write(to_varint(value, signed=True))
        elif dtype == 3:
            f.write(struct.pack('>f', value))
        elif dtype == 4:
            f.write(int(value).to_bytes(1, byteorder='big'))
    
    f.write(struct.pack('>BBB', *item['color']))

    has_children = 1 if item['children'] else 0
    f.write(has_children.to_bytes(1, byteorder='big'))

    if has_children:
        f.write(to_varint(len(item['children'])))
        for child in item['children']:
            _save_table(f, child)

def save_table(file, table: list):
    with open(file, 'wb') as f:
        f.write(b'TBR-CTLBF')
        f.write(b'0.0.1')
        f.write(hashlib.sha256(json.dumps(table, sort_keys=True).encode('utf-8')).digest())

        f.write(to_varint(len(table)))

        for item in table:
            _save_table(f, item)
        f.close()

def _load_table(f):
    data = dict()

    is_header = int.from_bytes(f.read(1), byteorder='big')
    name_length = from_varint_file(f)
    data['name'] = f.read(name_length).decode('utf-8')

    if not is_header:
        ptype = int.from_bytes(f.read(1), byteorder='big')
        path_length = from_varint_file(f)
        path = f.read(path_length).decode('utf-8')
        
        if ptype == 0:
            data['path'] = 'stat.f.' + path
        elif ptype == 1:
            data['path'] = 'variable.tf.' + path
        elif ptype == 2:
            data['path'] = 'variable.sf.' + path

        dtype = int.from_bytes(f.read(1), byteorder='big')

        if dtype == 0:
            data['value'] = None
        elif dtype == 1:
            value_length = from_varint_file(f)
            data['value'] = f.read(value_length).decode('utf-8')
        elif dtype == 2:
            data['value'] = from_varint_file(f, signed=True)
        elif dtype == 3:
            data['value'] = struct.unpack('>f', f.read(4))[0]
        elif dtype == 4:
            data['value'] = bool(int.from_bytes(f.read(1), byteorder='big'))
    else:
        data['path'] = ''
        data['value'] = ''

    data['color'] = struct.unpack('>BBB', f.read(3))

    has_children = int.from_bytes(f.read(1), byteorder='big')
    if has_children:
        count = from_varint_file(f)
        data['children'] = list()
        for i in range(count):
            data['children'].append(_load_table(f))
    else:
        data['children'] = list()

    return data

def load_table(file):
    if not os.path.exists(file):
        raise FileNotFoundError(file)
    with open(file, 'rb') as f:
        if f.read(9) != b'TBR-CTLBF':
            raise Exception('Invalid table file')

        version = f.read(5).decode('utf-8')
        # Do backward compatibility
        # Nothing for now

        hash_ = f.read(32)
        data = list()

        count = from_varint_file(f)
        for i in range(count):
            data.append(_load_table(f))
        f.close()

        if hash_ != hashlib.sha256(json.dumps(data, sort_keys=True).encode('utf-8')).digest():
            raise Warning('Hash mismatch for save file')

        return data
