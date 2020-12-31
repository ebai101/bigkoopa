from turtleswarm import swarm, api


# this does not make a big hole
def big_hole(t: api.Turtle):
    t.select(1)
    t.suck_up()
    t.refuel()

    while True:
        if not t.dig_down():
            break
        else:
            t.down()

        for j in range(3):
            t.dig()
            t.forward()
        t.turnLeft()
        t.dig()
        t.forward()
        t.turnLeft()

        for i in range(3):
            t.dig()
            t.forward()
        t.turnRight()
        t.dig()
        t.forward()
        t.turnRight()

        for i in range(3):
            t.dig()
            t.forward()
        t.turnLeft()
        t.dig()
        t.forward()
        t.turnLeft()

        for i in range(3):
            t.dig()
            t.forward()
        t.turnLeft()
        for i in range(3):
            t.forward()
        t.turnLeft()


# create a new swarm with big_hole() as the target
s = swarm.TurtleSwarm(big_hole, 16)

# run the target on all turtles
s.run()
