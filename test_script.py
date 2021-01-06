from turtleswarm import swarm, api, util


def fast(t: api.Turtle):
    t.refuel()
    util.excavate(t, (4, 256, 4), api.LEFT)


def slow(t: api.Turtle):
    t.refuel()
    util.slow_excavate(t, (4, 256, 4), api.LEFT)


s = swarm.TurtleSwarm({0: fast, 1: slow}, 16)
s.run()
