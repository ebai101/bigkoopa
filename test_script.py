from turtleswarm import swarm, api, util


def fast(t: api.Turtle):
    # util.spawner(t)
    t.refuel()
    util.fast_excavate(t, (4, 256, 4), api.LEFT)


def slow(t: api.Turtle):
    t.refuel()
    util.excavate(t, (4, 256, 4), api.LEFT)


s = swarm.TurtleSwarm(digg, 16)
s.run()
