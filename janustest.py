import janus
import asyncio
from random import random
from concurrent.futures import ThreadPoolExecutor


class Turtle:

    def __init__(self, id):
        self.id = id
        self.running = True
        self.cmd_queue = janus.Queue()
        self.res_queue = janus.Queue()

    def run_command(self, command):
        self.cmd_queue.sync_q.put(command)
        return self.res_queue.sync_q.get()

    async def command_loop(self):

        while self.running:
            command = await self.cmd_queue.async_q.get()
            cmd_time = random() * 3 + 1

            print(
                f'running command {command} on turtle {self.id}, will take {cmd_time:.2f} seconds'
            )
            await asyncio.sleep(cmd_time)
            res = command * 2

            print(f'finished command {command} on turtle {self.id}')
            self.cmd_queue.async_q.task_done()
            await self.res_queue.async_q.put(res)


def dance(turtle):
    turtle.running = True

    print(turtle.run_command('foo'))
    print(turtle.run_command('bar'))

    turtle.running = False
    print('dance is done')


async def main():

    loop = asyncio.get_running_loop()
    executor = ThreadPoolExecutor()
    turtles = [Turtle(x) for x in range(5)]

    for t in turtles:
        fut = loop.run_in_executor(executor, dance, t)
    await asyncio.gather(*[t.command_loop() for t in turtles])


asyncio.run(main())
