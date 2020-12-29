from src.api import TurtleAPI as Turtle

t = Turtle()

for i in range(2):
    t.forward()
    t.up()
    t.back()
    t.down()
