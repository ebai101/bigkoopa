from src.swarm import TurtleAPI, TurtleSwarm

swarm = TurtleSwarm()
t = TurtleAPI(swarm)


def dance():
    for i in range(2):
        t.forward()
        t.up()
        t.back()
        t.down()


swarm.execute(dance)
