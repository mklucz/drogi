from math import sqrt
from networkx.algorithms.shortest_paths.astar import astar_path
from networkx.exception import NetworkXNoPath
from shapely.geometry import LineString
from shapely.ops import polygonize


class Trip:
    """docstring for Trip"""
    def __init__(self, way_map, start, end):
        self.way_map = way_map
        self.start = start
        self.end = end
        self.path = Path(self.way_map, self.start, self.end)
        if len(self.path.list_of_nodes) >= 2:
            self.is_traversible = True
        else:
            self.is_traversible = False


class Path:
    """docstring for Path"""
    def __init__(self, way_map, start, end):
        self.way_map = way_map
        self.start = start
        self.end = end
        try:
            self.list_of_nodes = astar_path(self.way_map.graph,
                                            self.start,
                                            self.end)
        except NetworkXNoPath:
            self.list_of_nodes = []
        self.linestring = LineString(self.list_of_nodes)
        self.straightline_length = Path.straightline_distance(self.start,
                                                              self.end)
        self.straightline = LineString([self.start, self.end])
        self.deviation_factor = (self.linestring.length /
                                 self.straightline_length)
        self.obstacles = []
        for polygon in list(polygonize([self.linestring,
                                        self.straightline])):
            self.obstacles.append(Obstacle(self.way_map,
                                           self.start,
                                           self.end,
                                           polygon))

    def render_on_canvas(self, canvas, **kwargs):
        x_list = [p[0] for p in self.list_of_nodes]
        y_list = [p[1] for p in self.list_of_nodes]
        canvas.subplot.plot(x_list, y_list, **kwargs)

    @staticmethod
    def straightline_distance(p1, p2):
        x_dist = abs(p1[0] - p2[0])
        y_dist = abs(p1[1] - p2[1])
        return sqrt(x_dist**2 + y_dist**2)


class Obstacle:
    """Represents anything that causes a path to deviate from straight line."""
    def __init__(self, way_map, start, end, polygon):
        self.way_map = way_map
        self.start = start
        self.end = end
        self.polygon = polygon
        self.area = polygon.area

    def render_on_canvas(self, canvas, **kwargs):
        """
        Renders the obstacle on given canvas.
        Args:
            canvas: a Canvas object.
            **kwargs: arguments to pass to pyplot's plot function. Refer to
                https://matplotlib.org/api/_as_gen/matplotlib.patches.Polygon.html
                for the full list of possible arguments.

        Returns:
            None
        """
        x, y = self.polygon.boundary.xy
        canvas.subplot.fill(x, y, **kwargs)
