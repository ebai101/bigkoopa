from turtleswarm import api


# attempts to refuel the turtle using objects from the turtle's inventory
def refuel_from_inventory(t: api.Turtle, goal_fuel_count: int = 0) -> bool:
    init_fuel_count = t.get_fuel_level()
    last_slot = t.get_selected_slot()

    # if we don't need fuel, consider it a success
    if init_fuel_count == -1:
        return True

    # if no amount specified, fill as much as possible
    if goal_fuel_count == 0:
        goal_fuel_count = t.get_fuel_limit()

    while init_fuel_count < goal_fuel_count:
        for n in range(1, 17):
            if t.get_item_count(n) > 0:
                t.select(n)
                if t.refuel(1):
                    # this item is usable fuel, keep refueling
                    while t.get_item_count(
                            n) > 0 and t.get_fuel_level() < goal_fuel_count:
                        t.refuel(1)
                    if t.get_fuel_level() >= goal_fuel_count:
                        # fueled up
                        t.select(last_slot)
                        return True
        t.select(last_slot)
        return False
    return True


# attempts to refuel the turtle from an adjacent chest
# the chest should be the only adjacent peripheral, and should only contain fuel
def refuel_from_chest(t: api.Turtle, item_count: int = 0) -> bool:
    side = t.peripheral_get_names()[0]

    if side == 'left':
        t.turn_left()
        t.suck(item_count)
        t.turn_right()
    elif side == 'right':
        t.turn_right()
        t.suck(item_count)
        t.turn_left()
    elif side == 'back':
        t.turn_around()
        t.suck(item_count)
        t.turn_around()
    elif side == 'front':
        t.suck(item_count)
    elif side == 'top':
        t.suck_up(item_count)
    elif side == 'bottom':
        t.suck_down(item_count)

    return refuel_from_inventory(t)


# excavates a hole of dim (x,y,z)
# dir indicates which direction the turtle will turn (using TurtleAPI.turn()): left is False, right is True
def excavate(t: api.Turtle, dim: tuple[int, int, int], dir: bool):

    if dim[0] <= 0 or dim[1] <= 0 or dim[2] <= 0:
        raise ValueError('dimensions must be nonzero positive numbers')

    cur_depth = 0
    while cur_depth < dim[1]:
        if not t.dig_down():
            break
        else:
            t.down()

        for i in range(dim[2]):
            for j in range(dim[0] - 1):
                t.dig()
                t.forward()
            if i < dim[2] - 1:
                t.turn(dir)
                t.dig()
                t.forward()
                t.turn(dir)
            else:
                t.turn(not dir)
            dir = not dir

        # transform dimensions to deal with nonsquare holes
        dim = (dim[2], dim[1], dim[0])
        cur_depth += 1


# clears out a 3-high square cave (dim+1,dim). uses dig, dig_up and dig_down for improved speed
# intended use is with 4 turtles to produce a cave with dimensions (2*dim+1,2*dim+1)
# dir indicates which direction the turtle will turn, can be LEFT or RIGHT
def clear_cave(t: api.Turtle, dim: int, dir: bool):

    if dim <= 0:
        raise ValueError('dim must be a nonzero positive number')

    t.dig_up()
    t.dig_down()
    for i in range(dim + 1):
        for j in range(dim - 1):
            t.dig()
            t.forward()
            t.dig_up()
            t.dig_down()
        if i < dim:
            t.turn(dir)
            t.dig()
            t.forward()
            t.dig_up()
            t.dig_down()
            t.turn(dir)
        else:
            if not dim % 2:
                t.turn_around()
                [t.forward() for k in range(dim - 1)]
            else:
                dir = not dir
            t.turn(dir)
            [t.forward() for k in range(dim)]
            t.turn(dir)
        dir = not dir