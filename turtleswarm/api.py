import asyncio
import websockets
from typing import Callable


# turtle api functions
class TurtleAPI:

    def __init__(self, websocket: websockets.WebSocketClientProtocol):
        self.websocket = websocket

    # runs a turtle command
    def __run(self, command):
        task = asyncio.create_task(
            self.swarm.run_command(self.websocket, command))
        return asyncio.wait(task)

# TURTLE FUNCTIONS #

    def forward(self):
        # moves the turtle forward one block
        return self.__run('turtle.forward()')

    def back(self):
        # moves the turtle back one block
        return self.__run('turtle.back()')

    def up(self):
        # moves the turtle up one block
        return self.__run('turtle.up()')

    def down(self):
        # moves the turtle down one block
        return self.__run('turtle.down()')

# EXTENDED API FUNCTIONS #

    def eval(self, cmd):
        # evaluates an arbitrary lua command
        return self.__run(cmd)

    def get_swarm_size(self):
        # returns the number of turtles in the swarm
        return len(self.swarm.turtles)


# callable for a target function for each turtle
class TurtleProgram:

    def __init__(self, swarm: swarm.TurtleSwarm, target: Callable):
        self.swarm = swarm
        self.target = target

    async def run(self, websocket):
        await self.target(TurtleAPI(self.swarm, websocket))
