import os
import datetime
import overpass
import matplotlib.pyplot as plt

from networkx import Graph

from .osmhandler import OSMHandler
from .data import BOUNDS_DICT


class WayMap:
    """Contains GIS-type data describing physical layout of ways in a particular
    area."""

    def __init__(self, area, filename=None):
        """
        Args:
            area(str): geographical area to be fetched and turned into a map
            filename(str): filename to save the fetched extract as.
        """
        self.area = area
        self.bounds_to_fetch = BOUNDS_DICT[area]
        self.minlat = self.bounds_to_fetch[0]
        self.minlon = self.bounds_to_fetch[1]
        self.maxlat = self.bounds_to_fetch[2]
        self.maxlon = self.bounds_to_fetch[3]
        self.filename_to_use = filename
        self.oldfile_name = None
        for existing_file in os.listdir(os.getcwd()):
            if existing_file.startswith(self.area):
                cached_extract_mtime = \
                    datetime.datetime.utcfromtimestamp(
                        os.path.getmtime(existing_file))
                if (datetime.datetime.utcnow() - cached_extract_mtime <
                        datetime.timedelta(days=7)):
                    self.filename_to_use = existing_file
                else:
                    self.oldfile_name = existing_file
        print(self.filename_to_use)
        if self.filename_to_use is None:
            # if self.oldfile_name:
            #     os.remove(self.oldfile_name)
            curr_time = str(datetime.datetime.utcnow()).replace(" ", "_")
            self.filename_to_use = self.area + curr_time + ".osm"
            api = overpass.API(timeout=600)
            map_query = overpass.MapQuery(self.minlat, self.minlon,
                                          self.maxlat, self.maxlon)
            response = api.get(map_query, responseformat="xml")
            with open(self.filename_to_use, "w") as f:
                f.write(response)
        self.handler = OSMHandler(self.filename_to_use)
        self.handler.apply_file(self.filename_to_use, locations=True)
        self.way_list = self.handler.way_list
        self.bounds = (self.minlat, self.minlon, self.maxlat, self.maxlon)
        self.graph = Graph(WayGraph(self.way_list))

    def save_as_png(self, img_filename, partial_bounds=None):
        """
        Renders the map and saves it as a png in current working directory
            Args:
                img_filename(str): filename to save the png as.
                partial_bounds(4-tuple, optional): 4 points describing the
                    rectangle to be rendered, if None the whole map is rendered.
            Returns:
                None
        """
        if partial_bounds is None:
            partial_bounds = self.bounds
        if not isinstance(partial_bounds, tuple) or len(partial_bounds) != 4:
            raise AttributeError("partial_bounds must be a 4-tuple")
        p_minlat, p_maxlat = partial_bounds[0], partial_bounds[2]
        p_minlon, p_maxlon = partial_bounds[1], partial_bounds[3]
        if (p_minlon < self.minlon or p_maxlon > self.maxlon or
                p_minlat < self.minlat or p_maxlat > self.maxlat):
            raise ValueError("partial_bounds out of WayMap's bounds")
        size = ((p_maxlon - p_minlon) * 400, (p_maxlat - p_minlat) * 400)
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
        for e in self.way_list:
            if e.category == "walkway":
                subplot.plot(list(e.line.xy[0]), list(e.line.xy[1]), color="black", aa=False, linewidth=0.1)
            elif e.category == "crossing":
                subplot.plot(list(e.line.xy[0]), list(e.line.xy[1]), color="black", aa=False, linewidth=0.1)
            elif e.category == "steps":
                subplot.plot(list(e.line.xy[0]), list(e.line.xy[1]), color="black", aa=False, linewidth=0.1)
        plt.gca().xaxis.set_major_locator(plt.NullLocator())
        plt.gca().yaxis.set_major_locator(plt.NullLocator())
        plt.savefig(img_filename, dpi=100, bbox_inches="tight", pad_inches=0)

    def render_on_canvas(self, canvas, **kwargs):
        """
        Renders the waymap on given canvas.
        Args:
            canvas: a Canvas object.
            **kwargs: arguments to pass to pyplot's plot function. Refer to
                https://matplotlib.org/api/_as_gen/matplotlib.lines.Line2D.html
                for the full list of possible arguments.

        Returns:
            None
        """
        for e in self.way_list:
            if e.category == "walkway":
                canvas.subplot.plot(list(e.line.xy[0]),
                                    list(e.line.xy[1]),
                                    **kwargs)
            elif e.category == "crossing":
                canvas.subplot.plot(list(e.line.xy[0]),
                                    list(e.line.xy[1]),
                                    **kwargs)
            elif e.category == "steps":
                canvas.subplot.plot(list(e.line.xy[0]),
                                    list(e.line.xy[1]),
                                    **kwargs)


class WayGraph(dict):
    """Graph representation for pathfinding."""
    def __init__(self, way_list):
        super(WayGraph, self).__init__()
        self.way_list = way_list
        for way in self.way_list:
            linestring = way.line
            category = way.category
            x = linestring.coords.xy[0]
            y = linestring.coords.xy[1]
            for i in range(len(x)):
                xy = (x[i], y[i])
                xy = tuple([round(e, 6) for e in xy])
                if i == 0:
                    if xy not in self:
                        self[xy] = [(x[i + 1], y[i + 1])]
                    else:
                        self[xy].append((x[i + 1], y[i + 1]))
                elif i == len(x) - 1:
                    if xy not in self:
                        self[xy] = [(x[i - 1], y[i - 1])]
                    else:
                        self[xy].append((x[i - 1], y[i - 1]))
                else:
                    if xy not in self:
                        self[xy] = [(x[i + 1], y[i + 1]), (x[i - 1], y[i - 1])]
                    else:
                        self[xy].append((x[i + 1], y[i + 1]))
                        self[xy].append((x[i - 1], y[i - 1]))
