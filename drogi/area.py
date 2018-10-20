from drogi.waymap import Bounds


class Area:
    def __init__(self, name, bounds):
        self.name = name
        self.bounds = Bounds(bounds)
