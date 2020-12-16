#!/usr/bin/env python3

import asyncio
import websockets

async def dance(websocket):
    for i in range(4):
        await turtle('forward', websocket)
        await turtle('up', websocket)
        await turtle('back', websocket)
        await turtle('down', websocket)
        await turtle('left', websocket)
        await turtle('dong', websocket)

async def turtle(command, websocket) -> bool:
    print('>>',command)
    await websocket.send(command)
    res = await websocket.recv()
    print('<<',res)

async def main(websocket: websockets.WebSocketServerProtocol, path: str) -> None:
    await websocket.recv()
    print('Connected to server')
    await dance(websocket)


start_server = websockets.serve(main, "localhost", 8765)

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
