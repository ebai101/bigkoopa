import os
import sys
import json
import base64
import pprint
import logging
import asyncio
import websockets
import turtleswarm
from typing import Callable
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
        print('> ', msg, end=end, flush=flush)
        return (await self.q.get()).rstrip('\n')


# websockets server that communicates with turtles and manages connections
class TurtleSwarm:

    def __init__(self, target: Callable, max_size: int):

        # basic setup
        self.addr = 'localhost'
        self.port = 42069
        self.max_size = max_size
        self.target = target
        self.turtles: set[turtleswarm.api.Turtle] = set()
        self.response_map: dict['str', asyncio.Queue] = {}

        # logging
        self.log = logging.getLogger('swarm')
        ch = logging.StreamHandler()
        fm = logging.Formatter('[%(levelname)s] - %(name)s - %(message)s')
        ch.setFormatter(fm)
        self.log.addHandler(ch)

    # generates a nonce to uniquely identify packets
    def __generate_nonce(self) -> str:
        return base64.b64encode(os.urandom(8), altchars=b'-_').decode('utf-8')

    # register a turtle client
    async def __register(self, websocket: websockets.WebSocketServerProtocol):
        # get turtle registration info
        cmd_packet = {
            'command': 'return os.getComputerID()',
            'nonce': self.__generate_nonce()
        }
        await websocket.send(json.dumps(cmd_packet))
        res_packet = await websocket.recv()
        res_data = json.loads(res_packet)
        t_id = res_data['result'][0]

        # add turtle to swarm
        turtle = turtleswarm.api.Turtle(self, t_id, websocket)

        self.turtles.add(turtle)
        self.log.info(
            f'added turtleID {t_id}, {len(self.turtles)} turtle(s) in swarm')

    # unregister a turtle client
    async def __unregister(self, turtle, err):
        self.turtles.remove(turtle)
        self.log.info(
            f'turtleID {turtle.t_id} disconnected: {err}, {len(self.turtles)} turtles(s) in swarm'
        )

    # handles incoming messages
    # finds the matching nonce and causes the associated run_command call to return
    async def __response_handler(self,
                                 websocket: websockets.WebSocketServerProtocol,
                                 path: str):
        await self.__register(websocket)
        try:
            async for packet in websocket:
                p = json.loads(packet)
                self.log.debug(f'received response packet: {pprint.pformat(p)}')
                if p['nonce'] in self.response_map:
                    # delivers the response packet to the proper queue
                    queue = self.response_map[p['nonce']]
                    await queue.put(p)
                    self.response_map.pop(p['nonce'])
                else:
                    self.log.error(
                        f'packet {p["nonce"]} has no response queue!')
        except Exception as err:
            # find turtle and unregister it
            this_turtle = [t for t in self.turtles if t.websocket == websocket]
            await self.__unregister(this_turtle[0], err)

    # worker task for each turtle. sets up the turtle and runs the command loop
    async def turtle_worker(self, turtle):
        turtle.initialize()
        await turtle.command_loop()

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
        self.log.debug(f'sending command packet: {pprint.pformat(cmd_packet)}')
        await turtle.websocket.send(json.dumps(cmd_packet))
        res_packet = await self.response_map[cmd_packet['nonce']].get()

        # handle the response
        if not res_packet['status']:
            raise turtleswarm.error.TurtleEvalError(res_packet['result'])
        return res_packet['result']

    # set the target function to be run on each turtle in the swarm
    def set_target(self, target: Callable):
        self.target = target

    # set the debug level for all member turtles
    def set_turtle_log_level(self, level: int):
        for t in self.turtles:
            t.log.setLevel(level)

    def run(self, log_level: int = logging.INFO):
        self.log.setLevel(log_level)

        # set up server
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        start_server = websockets.serve(self.__response_handler, self.addr,
                                        self.port)
        prompt = Prompt()

        # start
        loop.run_until_complete(start_server)
        self.log.info('starting server, waiting for connections...')
        loop.run_until_complete(prompt('press enter to run'))
        self.log.info('running program...')

        e = ThreadPoolExecutor(max_workers=self.max_size)
        self.set_turtle_log_level(log_level)

        for t in self.turtles:
            self.log.info(f'starting target: {self.target.__name__}')
            loop.run_in_executor(e, self.target, t)
        loop.run_until_complete(
            asyncio.gather(*[self.turtle_worker(t) for t in self.turtles]))
