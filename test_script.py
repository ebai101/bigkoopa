import logging
from turtleswarm import swarm, api, util


def test1(t: api.Turtle):
    t.turn_left()


def test2(t: api.Turtle):
    t.turn_right()


def test3(t: api.Turtle):
    t.turn_around()


targets = {3: test1, 2: test2, 'default': test3}

s = swarm.TurtleSwarm(targets, 16)
s.run(log_level=logging.DEBUG)
