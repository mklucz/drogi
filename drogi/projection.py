class Point:
    __slots__ = ("lat", "lon", "bounds")

    def __init__(self, lat, lon, bounds):
        self.lat = lat
        self.lon = lon
        self.bounds = bounds


class Projection:
    def __init__(self, bounds, renderable):
        self.bounds = bounds
