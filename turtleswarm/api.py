import janus
import asyncio
import websockets
import turtleswarm


class Turtle:

    def __init__(self, swarm: turtleswarm.swarm.TurtleSwarm,
                 websocket: websockets.WebSocketServerProtocol):
        self.swarm = swarm
        self.running = True
        self.websocket = websocket
        self.cmd_queue = janus.Queue()
        self.res_queue = janus.Queue()

    def __run(self, command):
        self.cmd_queue.sync_q.put(command)
        return self.res_queue.sync_q.get()

    async def command_loop(self):
        while self.running:
            # wait for new command
            command = await self.cmd_queue.async_q.get()
            self.cmd_queue.async_q.task_done()

            # send command, wait for result
            try:
                res = await self.swarm.run_command(self, command)
                await self.res_queue.async_q.put(res)
                self.res_queue.async_q.task_done()
            except turtleswarm.swarm.TurtleEvalError as e:
                print(e)

# TURTLE API FUNCTIONS #

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
