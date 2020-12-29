import os
import sys
import asyncio
import websockets
import concurrent.futures


# websockets server that communicates with turtles and manages connections
class WSServer:

    def __init__(self):
        self.addr = 'localhost'
        self.port = 42069
        self.outgoing = asyncio.Queue()
        self.turtleswarm = TurtleSwarm(self)

    # opens socket on addr/port and handles messages with handler
    def serve_forever(self):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        start_server = websockets.serve(self.handler, self.addr, self.port)
        asyncio.get_event_loop().run_until_complete(start_server)
        asyncio.get_event_loop().run_forever()

    async def submit(self, message):
        await self.outgoing.put(message)

    async def consumer_handler(self, websocket, path):
        async for message in websocket:
            await self.turtleswarm.receive(message)

    async def producer_handler(self, websocket, path):
        while True:
            message = await self.outgoing.get()
            await websocket.send(message)

    async def handler(self, websocket, path):
        consumer_task = asyncio.ensure_future(
            self.consumer_handler(websocket, path))
        producer_task = asyncio.ensure_future(
            self.producer_handler(websocket, path))
        done, pending = await asyncio.wait(
            [consumer_task, producer_task],
            return_when=asyncio.tasks.FIRST_COMPLETED)
        for task in pending:
            task.cancel()


if __name__ == '__main__':
    WSServer().serve_forever()
