from turtleswarm import swarm

# for i in range(2):
#     t.forward()
#     t.up()
#     t.back()
#     t.down()


def dance(turtle):
    turtle.eval('1 + 2')
    turtle.forward()


# create a new swarm with dance() as the target
s = swarm.TurtleSwarm(dance)

# run the target on all turtles
s.run()
