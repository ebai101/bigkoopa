import os
import sys
import json
import base64
import pprint
import logging
import asyncio
import websockets
from typing import Callable
from concurrent.futures import ThreadPoolExecutor

from bigkoopa import api, error


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


# wrapper for turtle task functions to standardize return behavior
class TurtleTask:

    def __init__(self, target: Callable):
        self.target = target

    # call the target function on a turtle, return the turtle
    def __call__(self, turtle: api.Turtle):
        self.target(turtle)
        return turtle


# websockets server that communicates with turtles and manages connections
class TurtleSwarm:

    def __init__(self, target, max_size: int):

        # basic setup
        self.addr = 'localhost'
        self.port = 42069
        self.target = target
        self.max_size = max_size
        self.turtles: set[api.Turtle] = set()
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
        t_id = res_data['result']

        # add turtle to swarm
        turtle = api.Turtle(t_id, websocket)

        self.turtles.add(turtle)
        self.log.info(
            f'added turtleID {t_id}, {len(self.turtles)} turtle(s) in swarm')

    # unregister a turtle client
    async def __unregister(self, turtle: api.Turtle, err: Exception):
        self.turtles.remove(turtle)
        self.log.info(
            f'turtleID {turtle.t_id} disconnected: {len(self.turtles)} turtles(s) in swarm'
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
    async def turtle_worker(self, turtle: api.Turtle):
        turtle.startup()
        self.log.debug(f'starting worker for turtleID {turtle.t_id}')

        while turtle.running:
            # wait for new command
            command = await turtle.cmd_queue.async_q.get()
            turtle.cmd_queue.async_q.task_done()

            if command == '__done__':
                # turtle task has finished
                await turtle.websocket.close()
                return

            # send command, wait for result
            self.log.debug(f'command received: {command}')
            try:
                res = await self.run_command(turtle, command)
                await turtle.res_queue.async_q.put(res)
                turtle.res_queue.async_q.task_done()
            except error.TurtleEvalError as e:
                self.log.error(e)

    # constructs a packet and sends it to a turtle
    # returns the command result
    async def run_command(self, turtle: api.Turtle, command: str):
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
        if res_packet['status'] == -1:
            raise error.TurtleEvalError(res_packet['result'])
        return res_packet

    # set the debug level for all member turtles
    def set_turtle_log_level(self, level: int):
        for t in self.turtles:
            t.log.setLevel(level)

    def run(self, log_level: int = logging.INFO):
        self.log.setLevel(log_level)

        # setup
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        exec = ThreadPoolExecutor(max_workers=self.max_size)
        start_server = websockets.serve(self.__response_handler, self.addr,
                                        self.port)
        prompt = Prompt()
        turtle_workers = {}

        # done callback for turtle tasks
        def __task_done(fut):
            t: api.Turtle = fut.result()
            t.shutdown()
            self.log.info(f'turtle ID {t.t_id} finished')

        # submits a task and adds a worker
        def __create_task(executor: ThreadPoolExecutor, function: Callable,
                          turtle: api.Turtle):
            self.log.info(f'starting target: {function.__name__}')
            turtle.running = True
            task = TurtleTask(function)
            fut = executor.submit(task, turtle)
            fut.add_done_callback(__task_done)
            turtle_workers[turtle.t_id] = asyncio.ensure_future(
                self.turtle_worker(turtle))

        # start listening for turtles
        loop.run_until_complete(start_server)
        self.log.info('starting server, waiting for connections...')
        loop.run_until_complete(prompt('press enter to run'))
        self.log.info('running program...')
        self.set_turtle_log_level(log_level)

        # build worker list and executor tasks
        if isinstance(self.target, Callable):
            # distribute single task to entire swarm
            self.log.debug('received single task')
            for turtle in self.turtles:
                __create_task(exec, self.target, turtle)
        elif isinstance(self.target, dict):
            # distribute tasks to specific turtles
            self.log.debug('received target dictionary')
            if not 'default' in self.target:
                self.log.warning(
                    'no default function passed to turtleswarm, only specified turtle IDs will run'
                )
            for turtle in self.turtles:
                if turtle.t_id in self.target:
                    __create_task(exec, self.target[turtle.t_id], turtle)
                elif 'default' in self.target:
                    __create_task(exec, self.target['default'], turtle)

        # finally, run all the workers
        loop.run_until_complete(asyncio.gather(*turtle_workers.values()))
        self.log.info('all done!')
