#!/usr/bin/env python3

import asyncio
import websockets
import threading
import sys

import turtle_manager

class WSServer:

    _incoming = asyncio.Queue()
    _manager = turtle_manager.TurtleManager()

    async def get_message(self):
        msg_in = await self._ws.recv()
        await self._incoming.put(msg_in)

    async def send_message(self, message):
        await self._ws.send(message)

    async def consume(self):
        msg = await self._incoming.get()
        self._manager.parse_turtle_response(msg)

    async def produce(self):
        msg_out = await self._manager.outgoing.get()
        return msg_out

    def serve_forever(self):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        start_server = websockets.serve(self.handler, 'localhost', 42069)
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
                return_when=asyncio.FIRST_COMPLETED
            )

            if listener_task in done:
                await self.consume()
            else:
                listener_task.cancel()

            if producer_task in done:
                msg_to_send = producer_task.result()
                await self.send_message(msg_to_send)
            else:
                producer_task.cancel()


def repl():
    print(input('> '))

if __name__ == '__main__':
    s = WSServer()
    t = threading.Thread(target=s.serve_forever, daemon=True)
    t.start()
    while True:
        try:
            repl()
        except KeyboardInterrupt:
            asyncio.get_event_loop().stop()
            sys.exit()
