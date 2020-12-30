# exception for errors returned from the turtle
class TurtleEvalError(Exception):

    def __init__(self, message):
        super().__init__(message)
