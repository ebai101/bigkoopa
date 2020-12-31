import turtleswarm


# excavates a hole of dim (x,y,z)
# dir indicates which direction the turtle will turn (using TurtleAPI.turn()): left is False, right is True
def excavate(t: turtleswarm.api.Turtle, dim: tuple[int, int, int], dir: bool):

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
def clear_cave(t: turtleswarm.api.Turtle, dim: int, dir: bool):

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
