import matplotlib.pyplot as plt

from math import sqrt
from networkx.algorithms.shortest_paths.astar import astar_path
from networkx.exception import NetworkXNoPath
from shapely.geometry import LineString


class Trip:
    """docstring for Trip"""
    def __init__(self, way_map, start, end):
        super(Trip, self).__init__()
        self.way_map = way_map
        self.start = start
        self.end = end
        self.path = Path(self.way_map, self.start, self.end)
        if len(self.path.list_of_nodes) >= 2:
            self.is_traversible = True
        else:
            self.is_traversible = False


class Path(LineString):
    """docstring for Path"""
    def __init__(self, way_map, start, end):
        super(Path, self).__init__()
        self.way_map = way_map
        self.start = start
        self.end = end
        try:
            self.list_of_nodes = astar_path(self.way_map.graph, self.start, self.end)
        except NetworkXNoPath:
            self.list_of_nodes = []
        self.straightline_length = self.straightline_distance(self.start, self.end)

    def save_as_png(self, img_filename):
        partial_bounds = self.way_map.bounds
        p_minlat, p_maxlat = partial_bounds[0], partial_bounds[2]
        p_minlon, p_maxlon = partial_bounds[1], partial_bounds[3]
        size = ((p_maxlon - p_minlon) * 400, (p_maxlat - p_minlat) * 400)
        x_list = [p[0] for p in self.list_of_nodes]
        y_list = [p[1] for p in self.list_of_nodes]
        fig = plt.figure(frameon=False, figsize=size)
        subplot = fig.add_subplot(111)
        fig.subplots_adjust(bottom=0)
        fig.subplots_adjust(top=1)
        fig.subplots_adjust(right=1)
        fig.subplots_adjust(left=0)
        subplot.set_xlim((p_minlon, p_maxlon))
        subplot.set_ylim((p_minlat, p_maxlat))
        subplot.axis("off")
        subplot.tick_params(axis="both", which="both", left=False, top=False, right=False, bottom=False,
                            labelleft=False, labeltop=False, labelright=False, labelbottom=False,
                            length=0, width=0, pad=0)
        subplot.plot(x_list, y_list, color="red", aa=False, linewidth=0.1)
        plt.gca().xaxis.set_major_locator(plt.NullLocator())
        plt.gca().yaxis.set_major_locator(plt.NullLocator())
        plt.savefig(img_filename, dpi=100, bbox_inches="tight", pad_inches=0)

    def straightline_distance(self, p1, p2):
        x_dist = abs(p1[0] - p2[0])
        y_dist = abs(p1[1] - p2[1])
        return sqrt(x_dist**2 + y_dist**2)
