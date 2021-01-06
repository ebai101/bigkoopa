from bigkoopa import swarm, api, util

droplist = [
    "minecraft:stone",
    "minecraft:dirt",
    "minecraft:cobblestone",
    "minecraft:sand",
    "minecraft:gravel",
    "minecraft:dye",
]


def diggin(t: api.Turtle):
    t.refuel()
    util.clear_cave(t, 30, api.LEFT, droplist)


s = swarm.TurtleSwarm(diggin, 16)
s.run()
