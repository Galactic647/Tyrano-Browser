from typing import Optional

import websockets
import asyncio
import aiohttp
import socket
import json

SKIP_PROPERTIES = (
    '__proto__',
    'length'
)


async def check_port_async(port, timeout: Optional[float] = 0.1) -> bool:
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setblocking(False)
        await asyncio.wait_for(
            asyncio.get_event_loop().sock_connect(sock, ('127.0.0.1', port)),
            timeout=timeout,
        )
        sock.close()
    except (OSError, ConnectionRefusedError, asyncio.TimeoutError):
        return False
    return True

def check_port(port, timeout: Optional[float] = 0.1) -> bool:
    return asyncio.run(check_port_async(port, timeout)) 

async def wait_for_port_async(port, timeout: Optional[float] = 5) -> bool:
    start = asyncio.get_running_loop().time()
    while True:
        if await check_port_async(port):
            return True
        await asyncio.sleep(0.1)
        if timeout is not None and asyncio.get_running_loop().time() - start > timeout:
            return False
        
def wait_for_port(port, timeout: Optional[float] = 5) -> bool:
    return asyncio.run(wait_for_port_async(port, timeout))

async def get_cdp_ws_url_async(port) -> str:
    # TODO needs to find out a way to find the actual websocket url
    # and not just hardcoding the index
    async with aiohttp.ClientSession() as session:
        async with session.get(f'http://localhost:{port}/json') as response:
            data = await response.json()
            return data[1]['webSocketDebuggerUrl']

def get_cdp_ws_url(port) -> str:
    return asyncio.run(get_cdp_ws_url_async(port))


class RuntimeMethods:
    EVALUATE = "Runtime.evaluate"
    GET_PROPERTIES = "Runtime.getProperties"


class CDPHandler(object):
    def __init__(self, websocket_url) -> None:
        self.websocket_url = websocket_url
        self.websocket = None

        self.pending = dict()

        self._msg_id = 0
        self._listener_task = None
        self._active = False

    async def _get_id(self) -> int:
        self._msg_id += 1
        return self._msg_id

    async def connect(self) -> None:
        self.websocket = await websockets.connect(self.websocket_url)
        self._listener_task = asyncio.create_task(self._listener())
        self._active = True

    async def close(self) -> None:
        self._active = False
        await self._listener_task
        await self.websocket.close()

    async def _listener(self) -> None:
        try:
            while self._active:
                message = json.loads(await self.websocket.recv())
                if 'id' in message:
                    future = self.pending.pop(message['id'])

                    if future is not None:
                        future.set_result(message)
                else:
                    raise NotImplementedError(message)
                await asyncio.sleep(0.01)
        except websockets.ConnectionClosed:
            pass
    
    async def send(self, method, params):
        msg = {
            "id": await self._get_id(),
            "method": method,
            "params": params
        }
        future = asyncio.get_event_loop().create_future()
        self.pending[msg['id']] = future

        await self.websocket.send(json.dumps(msg))
        return await future
    
    async def get_properties(self, object_id) -> dict:
        result = await self.send(RuntimeMethods.GET_PROPERTIES,{"objectId": object_id, "ownProperties": True})
        return result['result']['result']

    async def _get_value(self, key, value):
        result = dict()
        
        if value['type'] == 'object':
            object_id = value['objectId']
            properties = await self.get_properties(object_id)

            data = list()
            for prop in properties:
                k = prop['name']
                v = prop['value']

                if k in SKIP_PROPERTIES:
                    continue

                if v['type'] in ('string', 'number', 'boolean'):
                    data.append(v['value'])
                else:
                    data.append(await self._get_value(k, v))

            if value['subtype'] == 'array' and key.isdigit():
                return data
            result[key] = data
        elif value['type'] in ('string', 'number', 'boolean'):
            result[key] = value['value']
        else:
            raise NotImplementedError(value)
        
        return result

    async def get_value(self, expression) -> dict:
        response = await self.send(RuntimeMethods.EVALUATE, {"expression": expression, "returnByValue": False})

        object_id = response['result']['result']['objectId']
        properties = await self.get_properties(object_id)
        
        data = dict()
        for prop in properties:
            if prop['name'] in SKIP_PROPERTIES:
                continue
            result = await self._get_value(prop['name'], prop['value'])
            data.update(result)
        return data

    async def _construct_expression(self, target, data):
        data = json.dumps(data)
        return f'Object.assign({target}, {data})'

    async def set_value_json(self, target, data) -> None:
        expression = await self._construct_expression(target, data)
        await self.send(RuntimeMethods.EVALUATE, {"expression": expression})

    async def set_value(self, target, value) -> None:
        if isinstance(value, dict):
            raise ValueError('Dictionary detected, use set_value_json instead')
        await self.send(RuntimeMethods.EVALUATE, {'expression': f'{target} = {value!r}'})
