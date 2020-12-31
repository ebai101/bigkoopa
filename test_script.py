from turtleswarm import swarm, api, util


def test(t: api.Turtle):
    # util.excavate(t, (4, 256, 4), api.LEFT)
    # util.clear_cave(t, 5, api.LEFT)
    t.forward()


# create a new swarm with big_hole() as the target
s = swarm.TurtleSwarm(test, 16)

# run the target on all turtles
s.run(debug=True)
