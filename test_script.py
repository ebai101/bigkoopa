import logging
from turtleswarm import swarm, api, util


def test(t: api.Turtle):

    util.refuel_from_chest(t, 32)
    util.clear_cave(t, 49, api.LEFT)


# create a new swarm with test() as the target
s = swarm.TurtleSwarm(test, 16)

# run the target on all turtles
s.run(log_level=logging.INFO)
