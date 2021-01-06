# tracks a turtle's relative position in space. useful for performing fuel calculations
class TurtleTracker:

    def __init__(self):
        self.x: int = 0
        self.y: int = 0
        self.z: int = 0

        # int in the range [0,4]. assuming the direction the turtle starts in is north,
        # 1 is east, 2 is south, 3 is west.
        self.heading: int = 0

    def process_move(self, move_type: str):
        pass
