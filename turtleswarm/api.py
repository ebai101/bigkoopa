import janus
import pprint
import logging
import asyncio
import websockets
import turtleswarm
from typing import Callable

LEFT = False
RIGHT = True


class Turtle:

    def __init__(self, swarm: turtleswarm.swarm.TurtleSwarm, t_id: int,
                 websocket: websockets.WebSocketServerProtocol):

        # basic setup
        self.t_id = t_id
        self.swarm = swarm
        self.running = True
        self.websocket = websocket
        self.cmd_queue = janus.Queue()
        self.res_queue = janus.Queue()

        # logging
        self.log = logging.getLogger(f'turtle_{t_id}')
        ch = logging.StreamHandler()
        fm = logging.Formatter('[%(levelname)s] - %(name)s - %(message)s')
        ch.setFormatter(fm)
        self.log.addHandler(ch)

    def initialize(self):
        # initialization code to run on turtle startup
        # TODO: add stuff to do here
        self.log.debug('initializing')

    async def command_loop(self):
        self.log.debug('starting command loop')
        while self.running:
            # wait for new command
            command = await self.cmd_queue.async_q.get()
            self.cmd_queue.async_q.task_done()
            self.log.debug(f'command received: {command}')

            # send command, wait for result
            try:
                res = await self.swarm.run_command(self, command)
                await self.res_queue.async_q.put(res)
                self.res_queue.async_q.task_done()
            except turtleswarm.error.TurtleEvalError as e:
                self.log.error(e)

# INTERNAL API FUNCTIONS #

    def __run(self, lib: str, command: str, *args):
        # internal run command, tracks commands and results as well as turtle stats

        # parse args list
        command_fmt = f'{lib}.{command}{str(args[0]).replace(",)", ")")}'

        # send command and block for response
        self.cmd_queue.sync_q.put(command_fmt)
        result = self.res_queue.sync_q.get()

        # parse response (TODO: add errors)
        self.log.info(f'{command_fmt} -> {result}')

        return result

    def __turtle(self, command: str, *args):
        # runs a turtle command
        return self.__run('turtle', command, args)

    def __peripheral(self, command: str, *args):
        # runs a peripheral command
        return self.__run('peripheral', command, args)

    def __eval(self, eval_str: str):
        # runs an arbitrary lua expression on the turtle. can be dangerous.
        self.cmd_queue.sync_q.put(eval_str)
        return self.res_queue.sync_q.get()

# TURTLE API FUNCTIONS #

    def craft(self, quantity: int = None) -> bool:
        # craft items using ingredients anywhere in the turtle's inventory and place results in the active slot.
        # if a quantity is specified, it will craft only up to that many items, otherwise, it will craft as many of the items as possible.
        return self.__turtle('craft', quantity)

    def forward(self) -> bool:
        # Try to move the turtle forward
        return self.__turtle('forward')

    def back(self) -> bool:
        # Try to move the turtle backward
        return self.__turtle('back')

    def up(self) -> bool:
        # Try to move the turtle up
        return self.__turtle('up')

    def down(self) -> bool:
        # Try to move the turtle down
        return self.__turtle('down')

    def turn_left(self) -> bool:
        # Turn the turtle left
        return self.__turtle('turnLeft')

    def turn_right(self) -> bool:
        # Turn the turtle right
        return self.__turtle('turnRight')

    def select(self, slot_num: int) -> bool:
        # Make the turtle select slot slot_num (1 is top left, 16 (9 in 1.33 and earlier) is bottom right)
        return self.__turtle('select', slot_num)

    def get_selected_slot(self) -> int:
        # Returns the currently selected inventory slot
        return self.__turtle('getSelectedSlot')

    def get_item_count(self, slot_num: int = None) -> int:
        # Counts how many items are in the currently selected slot or, if specified, slot_num slot
        return self.__turtle('getItemCount', slot_num)

    def get_item_space(self, slot_num: int = None) -> int:
        # Counts how many remaining items you need to fill the stack in the currently selected slot or, if specified, slot_num slot
        return self.__turtle('getItemSpace', slot_num)

    def get_item_detail(self, slot_num: int = None) -> dict:
        # Returns the ID string, count and damage values of currently selected slot or, if specified, slot_num slot
        return self.__turtle('getItemDetail', slot_num)

    def equip_left(self) -> bool:
        # Attempts to equip an item in the current slot to the turtle's left side, switching the previously equipped item back into the inventory
        return self.__turtle('equipLeft')

    def equip_right(self) -> bool:
        # Attempts to equip an item in the current slot to the turtle's right side, switching the previously equipped item back into the inventory
        return self.__turtle('equipRight')

    def attack(self, tool_side: str = None) -> bool:
        # Attacks in front of the turtle
        if tool_side and tool_side != 'left' and tool_side != 'right':
            raise ValueError('tool_side must be "left", "right", or None')
        else:
            return self.__turtle('attack', tool_side)

    def attack_up(self, tool_side: str = None) -> bool:
        # Attacks above the turtle
        if tool_side and tool_side != 'left' and tool_side != 'right':
            raise ValueError('tool_side must be "left", "right", or None')
        else:
            return self.__turtle('attackUp', tool_side)

    def attack_down(self, tool_side: str = None) -> bool:
        # Attacks under the turtle
        if tool_side and tool_side != 'left' and tool_side != 'right':
            raise ValueError('tool_side must be "left", "right", or None')
        else:
            return self.__turtle('attackDown', tool_side)

    def dig(self, tool_side: str = None) -> bool:
        # Breaks the block in front. With hoe: tills the dirt in front of it.
        if tool_side and tool_side != 'left' and tool_side != 'right':
            raise ValueError('tool_side must be "left", "right", or None')
        else:
            return self.__turtle('dig', tool_side)

    def dig_up(self, tool_side: str = None):
        # Breaks the block above.
        if tool_side and tool_side != 'left' and tool_side != 'right':
            raise ValueError('tool_side must be "left", "right", or None')
        else:
            return self.__turtle('digUp', tool_side)

    def dig_down(self, tool_side: str = None):
        # Breaks the block below. With hoe: tills the dirt beneath the space below it.
        if tool_side and tool_side != 'left' and tool_side != 'right':
            raise ValueError('tool_side must be "left", "right", or None')
        else:
            return self.__turtle('digDown', tool_side)

    def place(self, sign_text: str = None):
        # Places a block of the selected slot in front. Engrave sign_text on signs if provided. Collects water or lava if the currently selected slot is an empty bucket.
        return self.__turtle('place', sign_text)

    def place_up(self, sign_text: str = None):
        # Places a block of the selected slot above. Collects water or lava if the currently selected slot is an empty bucket.
        return self.__turtle('placeUp', sign_text)

    def place_down(self, sign_text=None):
        # Places a block of the selected slot below. Collects water or lava if the currently selected slot is an empty bucket.
        return self.__turtle('placeDown', sign_text)

    def detect(self) -> bool:
        # Detects if there is a block in front. Does not detect mobs.
        return self.__turtle('detect')

    def detect_up(self) -> bool:
        # Detects if there is a block above
        return self.__turtle('detectUp')

    def detect_down(self) -> bool:
        # Detects if there is a block below
        return self.__turtle('detectDown')

    def inspect(self) -> list:
        # Returns the ID string and metadata of the block in front of the Turtle
        return self.__turtle('inspect')

    def inspect_up(self) -> list:
        # Returns the ID string and metadata of the block above the Turtle
        return self.__turtle('inspectUp')

    def inspect_down(self) -> list:
        # Returns the ID string and metadata of the block below the Turtle
        return self.__turtle('inspectDown')

    def compare(self) -> bool:
        # Detects if the block in front is the same as the one in the currently selected slot
        return self.__turtle('compare')

    def compare_up(self) -> bool:
        # Detects if the block above is the same as the one in the currently selected slot
        return self.__turtle('compare')

    def compare_down(self) -> bool:
        # Detects if the block below is the same as the one in the currently selected slot
        return self.__turtle('compare')

    def compare_to(self, slot: int) -> bool:
        # Compare the current selected slot and the given slot to see if the items are the same. Returns true if they are the same, false if not.
        return self.__turtle('compareTo', slot)

    def drop(self, count: int = None) -> bool:
        # "Drops all items in the selected slot, or specified, drops count items.
        # If there is a inventory on the side (i.e in front of the turtle) it will try to place into the inventory, returning false if the inventory is full."
        return self.__turtle('drop', count)

    def drop_up(self, count: int = None) -> bool:
        # "Drops all items in the selected slot, or specified, drops count items.
        # If there is a inventory on the side (i.e above the turtle) it will try to place into the inventory, returning false if the inventory is full."
        return self.__turtle('dropUp', count)

    def drop_down(self, count: int = None) -> bool:
        # "Drops all items in the selected slot, or specified, drops count items.
        # If there is a inventory on the side (i.e below the turtle) it will try to place into the inventory, returning false if the inventory is full."
        return self.__turtle('dropDown', count)

    def suck(self, amount: int = None) -> bool:
        # Picks up an item stack of any number, from the ground or an inventory in front of the turtle, then places it in the selected slot.
        # If the turtle can't pick up the item, the function returns false.
        return self.__turtle('suck', amount)

    def suck_up(self, amount: int = None) -> bool:
        # Picks up an item stack of any number, from the ground or an inventory above the turtle, then places it in the selected slot.
        # If the turtle can't pick up the item, the function returns false.
        return self.__turtle('suckUp', amount)

    def suck_down(self, amount: int = None) -> bool:
        # Picks up an item stack of any number, from the ground or an inventory below the turtle, then places it in the selected slot.
        # If the turtle can't pick up the item, the function returns false.
        return self.__turtle('suckDown', amount)

    def refuel(self, quantity: int = None) -> bool:
        # "If the current selected slot contains a fuel item, it will consume it to give the turtle the ability to move.
        # is only needed in needfuel mode. If the current slot doesn't contain a fuel item, it returns false.
        # If a quantity is specified, it will refuel only up to that many items, otherwise, it will consume all the items in the slot."
        return self.__turtle('refuel', quantity)

    def get_fuel_level(self) -> int:
        # Returns the current fuel level of the turtle, this is the number of blocks the turtle can move.
        # If turtleNeedFuel = 0 then it returns -1.
        res = self.__turtle('getFuelLevel')
        return -1 if res == 'unlimited' else res

    def get_fuel_limit(self) -> int:
        # Returns the maximum amount of fuel a turtle can store - by default, 20,000 for regular turtles, 100,000 for advanced.
        # If turtleNeedFuel = 0 then it returns -1.
        res = self.__turtle('getFuelLimit')
        return -1 if res == 'unlimited' else res

    def transfer_to(self, slot: int, quantity: int = None) -> bool:
        # Transfers quantity items from the selected slot to slot. If quantity isn't specified, will attempt to transfer everything in the selected slot to slot.
        return self.__turtle('transferTo', slot, quantity)

# PERIPHERAL API FUNCTIONS #

    def peripheral_is_present(self, side: str) -> bool:
        # Returns True if a peripheral is connected on side.
        return self.__peripheral('isPresent', side)

    def peripheral_get_type(self, side: str) -> bool:
        # Returns the type of peripheral connected on side, as a string. If no peripheral is connected, returns None.
        return self.__peripheral('getType', side)

    def peripheral_get_methods(self, side: str) -> list:
        # Returns a list of the names of all the methods of the peripheral connected on side. If no peripheral is connected, returns None.
        return self.__peripheral('getMethods', side)

    def peripheral_call(self, side: str, method: str, *args):
        # Calls a method on a peripheral. The arguments (apart from side and method) and the return values depend on the method being called.
        # If no peripheral is connected, returns None.
        return self.__peripheral('call', side, method, args)

    def peripheral_wrap(self, side: str):
        return self.__build_peripheral_object(self.__peripheral('wrap', side))

    def __build_peripheral_object(self, peripheral: list):
        self.log.debug(pprint.pformat(peripheral))
        return True


# ADDITIONAL API FUNCTIONS #

    def turn(self, dir: bool) -> bool:
        # turn left or right based on a boolean
        # if dir is False, turn left, otherwise turn right
        if dir:
            return self.__turtle('turnRight')
        return self.__turtle('turnLeft')

    def turn_around(self) -> bool:
        # turns the turtle left twice, facing it the opposite direction
        return self.__turtle('turnLeft') and self.__turtle('turnLeft')

    def eval(self, cmd: str):
        # runs an arbitrary lua command on the turtle. can be dangerous
        return self.__eval(cmd)

    def get_swarm_size(self) -> int:
        # returns the number of turtles in the swarm
        return len(self.swarm.turtles)
