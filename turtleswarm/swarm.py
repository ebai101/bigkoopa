import os
import sys
import json
import base64
import asyncio
import websockets
import turtleswarm
from typing import Callable
from pprint import pprint as pp
from concurrent.futures import ThreadPoolExecutor


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


# websockets server that communicates with turtles and manages connections
class TurtleSwarm:

    def __init__(self, target: Callable, max_size: int):
        self.addr = 'localhost'
        self.port = 42069
        self.max_size = max_size
        self.target = target
        self.turtles: set[turtleswarm.api.Turtle] = set()
        self.response_map: dict['str', asyncio.Queue] = {}

    # generates a nonce to uniquely identify packets
    def __generate_nonce(self) -> str:
        return base64.b64encode(os.urandom(8), altchars=b'-_').decode('utf-8')

    # register a turtle client
    async def __register(self, turtle):
        self.turtles.add(turtle)
        print(f'found {len(self.turtles)} turtles')

    # unregister a turtle client
    async def __unregister(self, turtle):
        self.turtles.remove(turtle)

    # handles incoming messages
    # finds the matching nonce and causes the associated run_command call to return
    async def __response_handler(self,
                                 websocket: websockets.WebSocketServerProtocol,
                                 path: str):
        await self.__register(turtleswarm.api.Turtle(self, websocket))
        try:
            async for packet in websocket:
                p = json.loads(packet)
                if p['nonce'] in self.response_map:
                    # delivers the response packet to the proper queue
                    queue = self.response_map[p['nonce']]
                    await queue.put(p)
                    self.response_map.pop(p['nonce'])
        except:
            for t in self.turtles:
                if t.websocket == websocket:
                    await self.__unregister(t)

    # constructs a packet and sends it to a turtle
    # returns the command result
    async def run_command(self, turtle, command: str):
        cmd_packet = {
            'command': f'return {command}',
            'nonce': self.__generate_nonce()
        }

        # map this packets nonce to the turtle, to direct the response to this instance
        self.response_map[cmd_packet['nonce']] = asyncio.Queue()

        # send and await response
        await turtle.websocket.send(json.dumps(cmd_packet))
        res_packet = await self.response_map[cmd_packet['nonce']].get()

        # handle the response
        pp(res_packet)
        if not res_packet['status']:
            raise turtleswarm.error.TurtleEvalError(res_packet['result'])
        print(
            f"turtle {res_packet['t_id']}: ran {res_packet['command'].replace('return ','')}, returned {res_packet['result']}"
        )
        return res_packet['result']

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

        e = ThreadPoolExecutor(max_workers=self.max_size)
        for t in self.turtles:
            loop.run_in_executor(e, self.target, t)
        loop.run_until_complete(
            asyncio.gather(*[t.command_loop() for t in self.turtles]))
