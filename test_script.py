from src.swarm import TurtleAPI, TurtleSwarm

# set up the swarm server and the turtle API adapter
swarm = TurtleSwarm()
t = TurtleAPI(swarm)

for i in range(2):
    t.forward()
    t.up()
    t.back()
    t.down()

# call this to start the program
swarm.run()
