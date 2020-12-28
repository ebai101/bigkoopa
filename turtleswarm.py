import os
import sys
import json
import base64
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
        done, pending = await asyncio.wait([consumer_task, producer_task],
                                           return_when=asyncio.FIRST_COMPLETED)
        for task in pending:
            task.cancel()


# container for json data passed between client and server
# automatically packs/unpacks json on instantiation
class TurtlePacket:

    packet_types = ['eval', 'eval_r', 'wakeup', 'wakeup_r']

    def __init__(self, p: str):
        self.packet = p
        self.turtle_id, self.data, self.type, self.nonce = self.unpack()

    def __init__(self, t_id: int, data: str, type: str):
        self.turtle_id = t_id
        self.__set_type(type)
        self.__set_data(data)
        self.__create_nonce()
        self.packet = self.to_json()

    def __set_type(self, type: str):
        if type not in self.packet_types:
            raise ValueError('invalid packet type "{}"'.format(type))
        self.type = type

    def __set_data(self, cmd: str):
        if self.type == 'eval':
            self.data = 'return {}'.format(cmd)
        elif self.type == 'wakeup':
            self.data = 'wakeup'

    def __create_nonce(self):
        self.nonce = base64.b64encode(os.urandom(8), altchars=b'-_')

    def unpack(self):
        p = json.loads(self.packet)
        return (p['turtle_id'], p['command'], p['type'], p['nonce'])

    def to_json(self):
        return json.dumps({
            'turtle_id': self.turtle_id,
            'command': self.data,
            'type': self.type,
            'nonce': self.nonce
        })


class TurtleSwarm:

    def __init__(self, wss):
        self.wss = wss
        self.turtles = {}

    # sends wakeup broadcast to get turtle info
    async def wakeup(self):
        pass

    # sends eval message for a specific turtle
    async def eval(self, message, id):
        pass

    # process incoming response messages
    def receive(self, message: TurtlePacket):
        if message.type == 'wakeup_r':
            self.turtles[message.turtle_id]


if __name__ == '__main__':
    WSServer().serve_forever()
