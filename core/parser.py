from __future__ import annotations

from typing import Union, Optional
from pathlib import Path
from urllib import parse
import cProfile
import hashlib
import pathlib
import regex
import json
import os

RE_NON_ASCII = regex.compile(r'%u[0-9A-F]{4,6}')
RE_NON_ASCII_CAP = regex.compile(r'[^\x00-\x7F]')
ASCIIRE = regex.compile(r'([\x00-\x7F]+)')
_hexdigits = '0123456789abcdefABCDEF'
BYTEHEX = {(a + b).encode(): bytes.fromhex(a + b) for a in _hexdigits for b in _hexdigits}
EXCLUDED = list()
TEMP_INTREGITY_CHECK_FILENAME = 'temp_integrity_check.json'


def get_hash_sig(file: str) -> str:
    BLOCK = 1048576  # 1MB
    sha256 = hashlib.sha256()
    with open(file, 'rb') as f:
        buf = f.read(BLOCK)
        while buf:
            sha256.update(buf)
            buf = f.read(BLOCK)
    return sha256.hexdigest()


def parser_integrity_check(input_file: Union[str, Path], args=None) -> tuple[bool, str, str]:
    try:
        parser = _temp_file_gen(Path(input_file), args)
    except UnicodeDecodeError:
        return False, 'N/A', 'N/A'
    source_sig = get_hash_sig(parser.source)
    true_source_sig = get_hash_sig(parser.true_source)

    valid = source_sig == true_source_sig
    os.remove(parser.output)
    os.remove(parser.source)

    if args:
        args[0].value = b'finished'
        args[3].value = valid
        args[4].value = true_source_sig.encode('utf-8')
        args[5].value = source_sig.encode('utf-8')
    return valid, true_source_sig, source_sig


def _temp_file_gen(input_file: Path, args=None) -> SavParser:
    output = f'{input_file.parent}/{TEMP_INTREGITY_CHECK_FILENAME}'
    parser = SavParser(input_file, output=output, overwrite_source=False)
    parser.unpack_to_file(args=args)
    parser.pack(args=args)
    return parser


def unquote(text: str) -> str:
    search = RE_NON_ASCII.findall(text)

    if search is not None:
        filtered = []
        for s in search:
            trimmed = s[2:]
            unc = int(trimmed, 16)
            if unc > 0x10ffff:  # Max unicode character
                trimmed = trimmed[:-1]
                unc = int(trimmed, 16)
            filtered.append((trimmed, chr(unc)))
        filtered = dict((f'%u{f[0]}', f[1]) for f in filtered)
        for k, v in filtered.items():
            text = text.replace(k, v)
    
    bits = ASCIIRE.split(text)
    res = [bits[0]]

    for i in range(1, len(bits), 2):
        cstr = bits[i].encode('utf-8')
        cbits = cstr.split(b'%')

        cres = [cbits[0]]
        for item in cbits[1:]:
            try:
                cres.append(BYTEHEX[item[:2]])
                cres.append(item[2:])
            except KeyError:
                cres.append(b'%')
                cres.append(item)
        res.append(b''.join(cres).decode('utf-8', 'replace'))
        res.append(bits[i + 1])
    return ''.join(res)


def quote(text: str) -> str:
    search = RE_NON_ASCII_CAP.findall(text)
    text = parse.quote(text)

    excluded = dict((parse.quote(k), k) for k in EXCLUDED)
    if search:
        search = dict((parse.quote(k), f'%u{ord(k):0X}') for k in set(search))
        excluded.update(search)
    pattern = regex.compile('|'.join(regex.escape(k) for k in excluded))
    text = pattern.sub(lambda m: excluded[m.group(0)], text)
    return text


class SavParser(object):
    def __init__(self, source: Union[str, Path], output: Optional[Union[str, Path]] = 'auto',
                 overwrite_source: Optional[bool] = False) -> None:
        if not os.path.exists(source):
            raise FileNotFoundError(f'File {source} does not exists')
        self._source = pathlib.Path(source)
        
        if not output:
            output = f'{self._source.parent}/parsed.json'
        self.output = pathlib.Path(output)
        self.overwrite_source = overwrite_source

        # Only used if template is provided
        self._keep_parsed = dict()

    @property
    def source(self) -> str:
        if self.overwrite_source:
            return str(self._source)
        src_name = '.'.join(self._source.name.split('.')[:-1])
        src = pathlib.Path(f'{self._source.parent}/{src_name}-repack{self._source.suffix}')
        return str(src)
    
    @property
    def true_source(self) -> str:
        return str(self._source)
    
    @staticmethod
    def unquote(text: str, args=None) -> str:
        if args:
            args[0].value = b'Searching Non ASCII characters...'
        search = RE_NON_ASCII.findall(text)

        if search is not None:
            filtered = []
            for s in search:
                trimmed = s[2:]
                unc = int(trimmed, 16)
                if unc > 0x10ffff:  # Max unicode character
                    trimmed = trimmed[:-1]
                    unc = int(trimmed, 16)
                filtered.append((trimmed, chr(unc)))
            filtered = dict((f'%u{f[0]}', f[1]) for f in filtered)
            pattern = regex.compile('|'.join(regex.escape(k) for k in filtered))
            text = pattern.sub(lambda m: filtered[m.group(0)], text)
        
        bits = ASCIIRE.split(text)
        nbits = len(bits)
        res = [bits[0]]

        if args:
            args[0].value = b'Starting...'
            args[2].value = nbits - (nbits % 2) - 1

        for i in range(1, nbits, 2):
            cstr = bits[i].encode('utf-8')
            cbits = cstr.split(b'%')

            cres = [cbits[0]]
            for item in cbits[1:]:
                try:
                    cres.append(BYTEHEX[item[:2]])
                    cres.append(item[2:])
                except KeyError:
                    cres.append(b'%')
                    cres.append(item)
            res.append(b''.join(cres).decode('utf-8', 'replace'))
            res.append(bits[i + 1])
            if args:
                args[1].value = i
        if args:
            args[0].value = b'Done'
        return ''.join(res)

    def unpack(self, args=None) -> dict:
        with open(self.true_source, 'r', encoding='utf-8') as file:
            data = file.readline()
            file.close()

        data = self.unquote(data, args=args)
        if args:
            args[0].value = b'Saving...'
        return json.loads(data)
    
    def unpack_to_file(self, output: Optional[Union[str, Path]] = None, args=None) -> None:
        if not output:
            output = self.output
        with open(output, 'wb') as file:
            d = json.dumps(self.unpack(args=args), indent=4, ensure_ascii=False)
            file.write(d.encode('utf-8'))
            file.close()

    def pack(self, filename: Optional[Union[str, Path]] = None, args=None) -> None:
        if not filename:
            filename = self.source
        with open(self.output, 'rb') as file:
            data = json.loads(file.read())
            file.close()
        
        data = json.dumps(data, separators=(',', ':'), ensure_ascii=False)
        data = quote(data)
        with open(filename, 'w', encoding='utf-8') as file:
            file.write(data)
            file.close()

    # def unpack_with_template(self, tmpl: dict) -> None:
    #     with open(self.true_source, 'r', encoding='utf-8') as file:
    #         data = file.readline()
    #         file.close()

    #     data = unquote(data)
    #     data = json.loads(data)
    #     self._keep_parsed = data
    #     data = tl.get_value_from_template(data, tmpl)
    #     with open(self.output, 'wb') as file:
    #         d = json.dumps(data, indent=4, ensure_ascii=False)
    #         file.write(d.encode('utf-8'))
    #         file.close()

    # def pack_with_template(self, tmpl: dict) -> None:
    #     with open(self.output, 'rb') as file:
    #         values = json.loads(file.read())
    #         file.close()
        
    #     data = tl.set_value_from_template(self._keep_parsed, values, tmpl)
    #     data = json.dumps(data, separators=(',', ':'), ensure_ascii=False)
    #     data = quote(data)

    #     with open(self.source, 'w', encoding='utf-8') as file:
    #         file.write(data)
    #         file.close()
