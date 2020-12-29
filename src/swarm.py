import os
import sys
import json
import base64
import asyncio
import websockets


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

    def __init__(self):
        self.addr = 'localhost'
        self.port = 42069
        self.turtles = set()
        self.commands: list[str] = []
        self.response_map: dict['str', asyncio.Queue] = {}

# generates a nonce to uniquely identify packets

    def __generate_nonce(self) -> str:
        return base64.b64encode(os.urandom(8), altchars=b'-_').decode('utf-8')

    # register a turtle client
    async def __register(self, websocket):
        self.turtles.add(websocket)
        print('found turtle')

    # unregister a turtle client
    async def __unregister(self, websocket):
        self.turtles.remove(websocket)

    # constructs a packet and sends it, then awaits the response
    # returns the response packet
    async def run_command(self, websocket, command: str):
        # construct packet
        packet = {
            'command': f'return {command}',
            'nonce': self.__generate_nonce()
        }
        p = json.dumps(packet)

        # send and await response
        self.response_map[packet['nonce']] = asyncio.Queue()
        await websocket.send(p)
        res = await self.response_map[packet['nonce']].get()
        print(
            f"turtle {res['t_id']} ran {res['command'].replace('return ', '')}: returned {res['result']}"
        )

    # worker task for each turtle
    # sends all turtle commands in the proper order
    async def turtle_worker(self, turtle):
        for command in self.commands:
            await self.run_command(turtle, command)

    # spawns a turtle worker for each task
    async def spawn_turtle_workers(self):
        tasks = [
            asyncio.create_task(self.turtle_worker(t)) for t in self.turtles
        ]
        for t in tasks:
            await t

    # handles incoming messages
    # searches response_map for a matching nonce and puts the response in the queue
    async def handler(self, websocket, path: str):
        await self.__register(websocket)
        try:
            async for packet in websocket:
                p = json.loads(packet)
                if p['nonce'] in self.response_map:
                    # delivers the response packet to the proper queue
                    await self.response_map[p['nonce']].put(p)
        except:
            await self.__unregister(websocket)

    def run(self):
        # set up server
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        start_server = websockets.serve(self.handler, self.addr, self.port)
        prompt = Prompt()

        # start
        loop.run_until_complete(start_server)
        print('starting server, waiting for connections...')
        loop.run_until_complete(prompt('press enter to run'))
        print('running program...')
        loop.run_until_complete(self.spawn_turtle_workers())


# turtle api functions
class TurtleAPI:

    def __init__(self, swarm: TurtleSwarm):
        self.swarm = swarm

    # moves the turtle forward one block
    def forward(self):
        self.swarm.commands.append('turtle.forward()')

    # moves the turtle back one block
    def back(self):
        self.swarm.commands.append('turtle.back()')

    # moves the turtle up one block
    def up(self):
        self.swarm.commands.append('turtle.up()')

    # moves the turtle down one block
    def down(self):
        self.swarm.commands.append('turtle.down()')

    # evaluates an arbitrary lua command
    def eval(self, cmd):
        self.swarm.commands.append(cmd)
