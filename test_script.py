from turtleswarm import swarm, api


# this does not make a big hole
def big_hole(t: api.Turtle):
    t.forward()


# create a new swarm with dance() as the target
s = swarm.TurtleSwarm(big_hole)

# run the target on all turtles
s.run()
