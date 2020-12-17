#!/usr/bin/env python3

import asyncio
import websockets
import threading
import sys
import http.server
import socketserver

import manager


class WSServer:

    addr = 'localhost'
    port = 42069
    incoming = asyncio.Queue()
    manager = manager.TurtleManager()

    async def get_message(self):
        msg_in = await self._ws.recv()
        await self.incoming.put(msg_in)

    async def send_message(self, message):
        await self._ws.send(message)

    async def consume(self):
        msg = await self.incoming.get()
        self.manager.parse_turtle_response(msg)

    async def produce(self):
        msg_out = await self.manager.outgoing.get()
        return msg_out

    def serve_forever(self):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        start_server = websockets.serve(self.handler, self.addr, self.port)
        asyncio.get_event_loop().run_until_complete(start_server)
        asyncio.get_event_loop().run_forever()

    async def handler(self, websocket, path):
        loop = asyncio.get_event_loop()
        self._ws = websocket

        while True:
            listener_task = asyncio.ensure_future(self.get_message())
            producer_task = asyncio.ensure_future(self.produce())
            done, pending = await asyncio.wait(
                [listener_task, producer_task],
                return_when=asyncio.FIRST_COMPLETED)

            if listener_task in done:
                await self.consume()
            else:
                listener_task.cancel()

            if producer_task in done:
                msg_to_send = producer_task.result()
                await self.send_message(msg_to_send)
            else:
                producer_task.cancel()


class DLServer:

    _addr = 'localhost'
    _port = 42070

    class Handler(http.server.SimpleHTTPRequestHandler):

        def __init__(self, *args, **kwargs):
            super().__init__(directory='lua', **kwargs)

    def serve_forever(self):
        socketserver.TCPServer.allow_reuse_address = True
        with socketserver.TCPServer((self._addr, self._port),
                                    self.Handler) as httpd:
            print('serving Lua files at http://%s:%d' %
                  (self._addr, self._port))
            httpd.serve_forever()


def repl():
    print(input('> '))


if __name__ == '__main__':
    wss = WSServer()
    dls = DLServer()
    wss_t = threading.Thread(target=wss.serve_forever, daemon=True)
    dls_t = threading.Thread(target=dls.serve_forever, daemon=True)
    wss_t.start()
    dls_t.start()

    while True:
        try:
            repl()
        except KeyboardInterrupt:
            asyncio.get_event_loop().stop()
            sys.exit()
