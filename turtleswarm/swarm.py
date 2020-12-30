import os
import sys
import json
import base64
import asyncio
import websockets
from turtleswarm import api
from typing import Callable
from pprint import pprint as pp


# asyncio input prompt from stackoverflow
class Prompt:

    def __init__(self, loop=None):
        self.loop = loop or asyncio.get_event_loop()
        self.q = asyncio.Queue(loop=self.loop)
        self.loop.add_reader(sys.stdin, self.got_input)

    def got_input(self):
        asyncio.ensure_future(self.q.put(sys.stdin.readline()), loop=self.loop)

    async def __call__(self, msg, end='\n', flush=False):
        print(msg, end=end, flush=flush)
        return (await self.q.get()).rstrip('\n')


# exception for errors returned from the turtle
class TurtleEvalError(Exception):

    def __init__(self, message):
        super().__init__(message)


# websockets server that communicates with turtles and manages connections
class TurtleSwarm:

    def __init__(self, target: Callable):
        self.addr = 'localhost'
        self.port = 42069
        self.target = api.TurtleProgram(self, target)
        self.turtles = set()
        self.response_map: dict['str', asyncio.Queue] = {}

    # generates a nonce to uniquely identify packets
    def __generate_nonce(self) -> str:
        return base64.b64encode(os.urandom(8), altchars=b'-_').decode('utf-8')

    # register a turtle client
    async def __register(self, websocket: websockets.WebSocketServerProtocol):
        self.turtles.add(websocket)
        print('found turtle')

    # unregister a turtle client
    async def __unregister(self, websocket: websockets.WebSocketServerProtocol):
        self.turtles.remove(websocket)

    # handles incoming messages
    # finds the matching nonce and causes the associated run_command call to return
    async def __response_handler(self,
                                 websocket: websockets.WebSocketServerProtocol,
                                 path: str):
        await self.__register(websocket)
        try:
            async for packet in websocket:
                p = json.loads(packet)
                if p['nonce'] in self.response_map:
                    # delivers the response packet to the proper queue
                    await self.response_map[p['nonce']].put(p)
        except:
            await self.__unregister(websocket)

    async def __spawn_turtle_workers(self):
        tasks = [asyncio.create_task(self.target.run(t)) for t in self.turtles]
        [await t for t in tasks]

    # constructs a packet and sends it, then awaits the response
    # returns the response packet
    async def run_command(self, websocket: websockets.WebSocketClientProtocol,
                          command: str):
        packet = {
            'command': f'return {command}',
            'nonce': self.__generate_nonce()
        }

        # set up a Queue to wait for this packet's response
        self.response_map[packet['nonce']] = asyncio.Queue()
        await websocket.send(json.dumps(packet))

        # wait for response
        res = await self.response_map[packet['nonce']].get()
        self.response_map.pop(packet['nonce'])  # remove map entry

        # handle the response
        if not res['status']:
            raise TurtleEvalError(res['result'])
        print(
            f"turtle {res['t_id']}: ran {res['command'].replace('return ','')}, returned {res['result']}"
        )
        return res['result']

    # set the target function to be run on each turtle in the swarm
    def set_target(self, target: Callable):
        self.target = target

    def run(self):
        # set up server
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        start_server = websockets.serve(self.__response_handler, self.addr,
                                        self.port)
        prompt = Prompt()

        # start
        loop.run_until_complete(start_server)
        print('starting server, waiting for connections...')
        loop.run_until_complete(prompt('press enter to run'))
        print('running program...')
        loop.run_until_complete(self.__spawn_turtle_workers())
