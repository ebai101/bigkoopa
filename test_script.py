from turtleswarm import swarm, api, util


def digg(t: api.Turtle):
    t.refuel()
    util.fast_excavate(t, (4, 256, 4), api.LEFT)


s = swarm.TurtleSwarm(digg, 16)
s.run()
