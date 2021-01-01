import logging
from turtleswarm import swarm, api, util


def test(t: api.Turtle):

    t.peripheral_get_names()

    # util.clear_cave(t, 50, api.LEFT)


# create a new swarm with test() as the target
s = swarm.TurtleSwarm(test, 16)

# run the target on all turtles
s.run(log_level=logging.DEBUG)
