import janus
import asyncio
import websockets
import turtleswarm

LEFT = False
RIGHT = True


class Turtle:

    def __init__(self, swarm: turtleswarm.swarm.TurtleSwarm, t_id: int,
                 websocket: websockets.WebSocketServerProtocol):
        self.t_id = t_id
        self.swarm = swarm
        self.running = True
        self.websocket = websocket
        self.cmd_queue = janus.Queue()
        self.res_queue = janus.Queue()

    def startup(self):
        # initialization code to run on turtle startup
        print(f'starting up turtle {self.t_id}')

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
            except turtleswarm.error.TurtleEvalError as e:
                print(e)

# INTERNAL API FUNCTIONS #

    def __run(self, command: str):
        # internal run command, tracks commands and results as well as turtle stats
        self.cmd_queue.sync_q.put(command)
        result = self.res_queue.sync_q.get()

        if result[0] == False:
            if result[1] == 'Out of fuel':
                raise turtleswarm.error.TurtleOutOfFuelError()

        return result

# TURTLE API FUNCTIONS #

    def craft(self, quantity: int = None) -> bool:
        # craft items using ingredients anywhere in the turtle's inventory and place results in the active slot.
        # if a quantity is specified, it will craft only up to that many items, otherwise, it will craft as many of the items as possible.
        if quantity:
            return self.__run(f'turtle.craft({quantity})')
        return self.__run('turtle.craft()')

    def forward(self) -> bool:
        # Try to move the turtle forward
        return self.__run('turtle.forward()')

    def back(self) -> bool:
        # Try to move the turtle backward
        return self.__run('turtle.back()')

    def up(self) -> bool:
        # Try to move the turtle up
        return self.__run('turtle.up()')

    def down(self) -> bool:
        # Try to move the turtle down
        return self.__run('turtle.down()')

    def turn_left(self) -> bool:
        # Turn the turtle left
        return self.__run('turtle.turnLeft()')

    def turn_right(self) -> bool:
        # Turn the turtle right
        return self.__run('turtle.turnRight()')

    def select(self, slot_num: int) -> bool:
        # Make the turtle select slot slot_num (1 is top left, 16 (9 in 1.33 and earlier) is bottom right)
        return self.__run(f'turtle.select({slot_num})')

    def get_selected_slot(self) -> int:
        # Returns the currently selected inventory slot
        return self.__run('turtle.getSelectedSlot()')

    def get_item_count(self, slot_num: int = None) -> int:
        # Counts how many items are in the currently selected slot or, if specified, slot_num slot
        if slot_num:
            return self.__run(f'turtle.getItemCount({slot_num})')
        return self.__run('turtle.getItemCount()')

    def get_item_space(self, slot_num: int = None) -> int:
        # Counts how many remaining items you need to fill the stack in the currently selected slot or, if specified, slot_num slot
        if slot_num:
            return self.__run(f'turtle.getItemSpace({slot_num})')
        return self.__run('turtle.getItemSpace()')

    def get_item_detail(self, slot_num: int = None) -> dict:
        # Returns the ID string, count and damage values of currently selected slot or, if specified, slot_num slot
        if slot_num:
            return self.__run(f'turtle.getItemDetail({slot_num})')
        return self.__run('turtle.getItemDetail()')

    def equip_left(self) -> bool:
        # Attempts to equip an item in the current slot to the turtle's left side, switching the previously equipped item back into the inventory
        return self.__run('turtle.equipLeft()')

    def equip_right(self) -> bool:
        # Attempts to equip an item in the current slot to the turtle's right side, switching the previously equipped item back into the inventory
        return self.__run('turtle.equipRight()')

    def attack(self, tool_side: str = None) -> bool:
        # Attacks in front of the turtle
        if tool_side == 'left' or tool_side == 'right':
            return self.__run(f'turtle.attack("{tool_side}")')
        elif tool_side == None:
            return self.__run('turtle.attack()')
        else:
            raise ValueError('tool_side must be "left", "right", or None')

    def attack_up(self, tool_side: str = None) -> bool:
        # Attacks above the turtle
        if tool_side == 'left' or tool_side == 'right':
            return self.__run(f'turtle.attackUp("{tool_side}")')
        elif tool_side == None:
            return self.__run('turtle.attackUp()')
        else:
            raise ValueError('tool_side must be "left", "right", or None')

    def attack_down(self, tool_side: str = None) -> bool:
        # Attacks under the turtle
        if tool_side == 'left' or tool_side == 'right':
            return self.__run(f'turtle.attackDown("{tool_side}")')
        elif tool_side == None:
            return self.__run('turtle.attackDown()')
        else:
            raise ValueError('tool_side must be "left", "right", or None')

    def dig(self, tool_side: str = None) -> bool:
        # Breaks the block in front. With hoe: tills the dirt in front of it.
        if tool_side == 'left' or tool_side == 'right':
            return self.__run(f'turtle.dig("{tool_side}")')
        elif tool_side == None:
            return self.__run('turtle.dig()')
        else:
            raise ValueError('tool_side must be "left", "right", or None')

    def dig_up(self, tool_side: str = None):
        # Breaks the block above.
        if tool_side == 'left' or tool_side == 'right':
            return self.__run(f'turtle.digUp("{tool_side}")')
        elif tool_side == None:
            return self.__run('turtle.digUp()')
        else:
            raise ValueError('tool_side must be "left", "right", or None')

    def dig_down(self, tool_side: str = None):
        # Breaks the block below. With hoe: tills the dirt beneath the space below it.
        if tool_side == 'left' or tool_side == 'right':
            return self.__run(f'turtle.digDown("{tool_side}")')
        elif tool_side == None:
            return self.__run('turtle.digDown()')
        else:
            raise ValueError('tool_side must be "left", "right", or None')

    def place(self, sign_text: str = None):
        # Places a block of the selected slot in front. Engrave sign_text on signs if provided. Collects water or lava if the currently selected slot is an empty bucket.
        if sign_text:
            return self.__run(f'turtle.place("{sign_text}")')
        return self.__run('turtle.place()')

    def place_up(self, sign_text: str = None):
        # Places a block of the selected slot above. Collects water or lava if the currently selected slot is an empty bucket.
        if sign_text:
            return self.__run(f'turtle.placeUp("{sign_text}")')
        return self.__run('turtle.placeUp()')

    def place_down(self, sign_text=None):
        # Places a block of the selected slot below. Collects water or lava if the currently selected slot is an empty bucket.
        if sign_text:
            return self.__run(f'turtle.placeDown("{sign_text}")')
        return self.__run('turtle.placeDown()')

    def detect(self) -> bool:
        # Detects if there is a block in front. Does not detect mobs.
        return self.__run('turtle.detect()')

    def detect_up(self) -> bool:
        # Detects if there is a block above
        return self.__run('turtle.detectUp()')

    def detect_down(self) -> bool:
        # Detects if there is a block below
        return self.__run('turtle.detectDown()')

    def inspect(self) -> list:
        # Returns the ID string and metadata of the block in front of the Turtle
        return self.__run('turtle.inspect()')

    def inspect_up(self) -> list:
        # Returns the ID string and metadata of the block above the Turtle
        return self.__run('turtle.inspectUp()')

    def inspect_down(self) -> list:
        # Returns the ID string and metadata of the block below the Turtle
        return self.__run('turtle.inspectDown()')

    def compare(self) -> bool:
        # Detects if the block in front is the same as the one in the currently selected slot
        return self.__run('turtle.compare()')

    def compare_up(self) -> bool:
        # Detects if the block above is the same as the one in the currently selected slot
        return self.__run('turtle.compare()')

    def compare_down(self) -> bool:
        # Detects if the block below is the same as the one in the currently selected slot
        return self.__run('turtle.compare()')

    def compare_to(self, slot: int) -> bool:
        # Compare the current selected slot and the given slot to see if the items are the same. Returns true if they are the same, false if not.
        return self.__run(f'turtle.compareTo({slot})')

    def drop(self, count: int = None) -> bool:
        # "Drops all items in the selected slot, or specified, drops count items.
        # If there is a inventory on the side (i.e in front of the turtle) it will try to place into the inventory, returning false if the inventory is full."
        if count:
            return self.__run(f'turtle.drop({count})')
        return self.__run('turtle.drop()')

    def drop_up(self, count: int = None) -> bool:
        # "Drops all items in the selected slot, or specified, drops count items.
        # If there is a inventory on the side (i.e above the turtle) it will try to place into the inventory, returning false if the inventory is full."
        if count:
            return self.__run(f'turtle.dropUp({count})')
        return self.__run('turtle.dropDown()')

    def drop_down(self, count: int = None) -> bool:
        # "Drops all items in the selected slot, or specified, drops count items.
        # If there is a inventory on the side (i.e below the turtle) it will try to place into the inventory, returning false if the inventory is full."
        if count:
            return self.__run(f'turtle.dropDown({count})')
        return self.__run('turtle.dropDown()')

    def suck(self, amount: int = None) -> bool:
        # Picks up an item stack of any number, from the ground or an inventory in front of the turtle, then places it in the selected slot.
        # If the turtle can't pick up the item, the function returns false.
        if amount:
            return self.__run(f'turtle.suck({amount})')
        return self.__run('turtle.suck()')

    def suck_up(self, amount: int = None) -> bool:
        # Picks up an item stack of any number, from the ground or an inventory above the turtle, then places it in the selected slot.
        # If the turtle can't pick up the item, the function returns false.
        if amount:
            return self.__run(f'turtle.suckUp({amount})')
        return self.__run('turtle.suckUp()')

    def suck_down(self, amount: int = None) -> bool:
        # Picks up an item stack of any number, from the ground or an inventory below the turtle, then places it in the selected slot.
        # If the turtle can't pick up the item, the function returns false.
        if amount:
            return self.__run(f'turtle.suckDown({amount})')
        return self.__run('turtle.suckDown()')

    def refuel(self, quantity: int = None) -> bool:
        # "If the current selected slot contains a fuel item, it will consume it to give the turtle the ability to move.
        # is only needed in needfuel mode. If the current slot doesn't contain a fuel item, it returns false.
        # If a quantity is specified, it will refuel only up to that many items, otherwise, it will consume all the items in the slot."
        if quantity:
            return self.__run(f'turtle.refuel({quantity})')
        return self.__run('turtle.refuel()')

    def get_fuel_level(self) -> int:
        # Returns the current fuel level of the turtle, this is the number of blocks the turtle can move.
        # If turtleNeedFuel = 0 then it returns "unlimited".
        return self.__run('turtle.getFuelLevel()')

    def get_fuel_limit(self) -> int:
        # Returns the maximum amount of fuel a turtle can store - by default, 20,000 for regular turtles, 100,000 for advanced.
        # If turtleNeedFuel = 0 then it returns "unlimited".
        res = self.__run('turtle.getFuelLimit()')
        if res == 'unlimited':
            return 0
        else:
            return res

    def transfer_to(self, slot: int, quantity: int = None) -> bool:
        # Transfers quantity items from the selected slot to slot. If quantity isn't specified, will attempt to transfer everything in the selected slot to slot.
        if quantity:
            return self.__run(f'turtle.transferTo({slot}, {quantity})')
        return self.__run(f'turtle.transferTo({slot})')


# ADDITIONAL API FUNCTIONS #

    def turn(self, dir: bool) -> bool:
        # turn left or right based on a boolean
        # if dir is False, turn left, otherwise turn right
        if dir:
            return self.__run('turtle.turnRight()')
        return self.__run('turtle.turnLeft()')

    def turn_around(self) -> bool:
        # turns the turtle left twice, facing it the opposite direction
        return self.__run('turtle.turnLeft()') and self.__run(
            'turtle.turnLeft()')

    def eval(self, cmd: str):
        # evaluates an arbitrary lua command
        return self.__run(cmd)

    def get_swarm_size(self) -> int:
        # returns the number of turtles in the swarm
        return len(self.swarm.turtles)
