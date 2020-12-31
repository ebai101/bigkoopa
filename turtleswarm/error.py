# exception for when turtles run out of fuel
class TurtleOutOfFuelError(Exception):

    def __init__(self):
        super().__init__()


# generic exception for lua errors
class TurtleEvalError(Exception):

    def __init__(self, message):
        super().__init__(message)
