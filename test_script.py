from turtleswarm import swarm
from random import random


def dance(t):
    t.eval('1 + 2')
    t.eval(f'os.sleep({random() * 3 + 1})')
    t.eval('"done!"')


# create a new swarm with dance() as the target
s = swarm.TurtleSwarm(dance)

# run the target on all turtles
s.run()
