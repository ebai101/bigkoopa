#!/usr/bin/env python3

import asyncio
import websockets
import sys
import http.server
import socketserver

import turtleswarm


class WSServer:

    def __init__(self):
        self.addr = 'localhost'
        self.port = 42069
        self.outgoing = asyncio.Queue()
        self.manager = turtleswarm.TurtleManager()

    # opens socket on addr/port and handles messages with handler
    def serve_forever(self):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        start_server = websockets.serve(self.handler, self.addr, self.port)
        asyncio.get_event_loop().run_until_complete(start_server)
        asyncio.get_event_loop().run_forever()

    async def consumer_handler(self, websocket, path):
        async for message in websocket:
            await self.manager.ingest(message)

    async def producer_handler(self, websocket, path):
        while True:
            message = await self.outgoing.get()
            await websocket.send(message)

    async def handler(self, websocket, path):
        consumer_task = asyncio.ensure_future(
            self.consumer_handler(websocket, path))
        producer_task = asyncio.ensure_future(
            self.producer_handler(websocket, path))
        done, pending = await asyncio.wait([consumer_task, producer_task],
                                           return_when=asyncio.FIRST_COMPLETED)
        for task in pending:
            task.cancel()


class DLServer:

    def __init__(self):
        self.addr = 'localhost'
        self.port = 42070

    class Handler(http.server.SimpleHTTPRequestHandler):

        def __init__(self, *args, **kwargs):
            super().__init__(directory='lua', **kwargs)

    def serve_forever(self):
        socketserver.TCPServer.allow_reuse_address = True
        with socketserver.TCPServer((self.addr, self.port),
                                    self.Handler) as httpd:
            print('serving Lua files at http://%s:%d' % (self.addr, self.port))
            httpd.serve_forever()


if __name__ == '__main__':
    WSServer().serve_forever()
