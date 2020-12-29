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
        self.commands: list[dict['str', 'str']] = []
        self.response_map: dict['str', asyncio.Queue] = {}

    # register a turtle client
    async def __register(self, websocket):
        self.turtles.add(websocket)
        # TODO: add registration packet to get computer id
        print('found turtle')

    # unregister a turtle client
    async def __unregister(self, websocket):
        self.turtles.remove(websocket)

    # send a TurtlePacket and wait for a response
    async def send_packet(self, websocket, packet: dict):
        self.response_map[packet['nonce']] = asyncio.Queue()

        p = json.dumps(packet).encode('utf-8')
        print(repr(p))

        await websocket.send(p)
        return await self.response_map[packet['nonce']].get()

    # worker task for each turtle
    # sends all turtle commands in the proper order
    async def turtle_worker(self, turtle):
        for command in self.commands:
            await self.send_packet(turtle, command)

    # spawns a turtle worker for each task
    async def spawn_turtle_workers(self):
        tasks = [
            asyncio.create_task(self.turtle_worker(t)) for t in self.turtles
        ]
        for t in tasks:
            await t

    # adds a command to the command list
    # called from a TurtleAPI instance
    def add_command(self, command: dict[str, str]):
        self.commands.append(command)

    # handles incoming messages
    # searches response_map for a matching nonce and puts the response in the queue
    async def handler(self, websocket, path: str):
        await self.__register(websocket)
        try:
            async for packet in websocket:
                p = json.loads(packet)
                if p['nonce'] in self.response_map:
                    self.response_map[p['nonce']].put(p)
        except:
            self.__unregister(websocket)

    def run(self):
        # set up server
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        start_server = websockets.serve(self.handler, self.addr, self.port)
        prompt = Prompt()

        # start
        loop.run_until_complete(start_server)
        loop.run_until_complete(
            prompt('started server, waiting for connections...'))
        loop.run_until_complete(self.spawn_turtle_workers())


# turtle api functions
class TurtleAPI:

    def __init__(self, swarm: TurtleSwarm):
        self.swarm = swarm

    def __generate_nonce(self) -> str:
        return base64.b64encode(os.urandom(8), altchars=b'-_').decode('utf-8')

    def forward(self):
        self.swarm.add_command({
            'data': 'return turtle.forward()',
            'nonce': self.__generate_nonce()
        })

    def back(self):
        self.swarm.add_command({
            'data': 'return turtle.back()',
            'nonce': self.__generate_nonce()
        })

    def up(self):
        self.swarm.add_command({
            'data': 'return turtle.up()',
            'nonce': self.__generate_nonce()
        })

    def down(self):
        self.swarm.add_command({
            'data': 'return turtle.down()',
            'nonce': self.__generate_nonce()
        })

    def getComputerId(self):
        self.swarm.add_command({})
