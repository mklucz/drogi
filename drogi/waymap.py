import os
import datetime
import overpass

from networkx import Graph

from .osm_handler import OSMHandler
from .data import BOUNDS_DICT


class WayMap:
    """Contains GIS-type data describing physical layout of ways in a particular
    area."""

    def __init__(self, area, from_file=False, osm_file=None):
        """
        Args:
            area(str): geographical area to be fetched and turned into a map
        """
        self.area = area
        self.from_file = from_file
        self.osm_file = osm_file
        self.bounds_to_fetch = BOUNDS_DICT[area]
        self.minlat = self.bounds_to_fetch[0]
        self.minlon = self.bounds_to_fetch[1]
        self.maxlat = self.bounds_to_fetch[2]
        self.maxlon = self.bounds_to_fetch[3]
        self.extracts_path = os.getcwd() + '/extracts/'

        if from_file:
            self.filename_to_use = os.getcwd() + self.osm_file
        else:
            self.filename_to_use = None
            self.oldfile_name = None
            self.check_for_cached_extract()

        if self.filename_to_use is None:
            if self.oldfile_name:
                os.remove(self.extracts_path + self.oldfile_name)
            curr_time = str(datetime.datetime.utcnow()).replace(" ", "_")
            self.filename_to_use = self.area + curr_time + ".osm"

            api = overpass.API(timeout=600)
            map_query = overpass.MapQuery(self.minlat, self.minlon,
                                          self.maxlat, self.maxlon)
            response = api.get(map_query, responseformat="xml")
            with open(self.extracts_path + self.filename_to_use, "w") as f:
                f.write(response)
            self.filename_to_use = self.extracts_path + self.filename_to_use

        self.handler = OSMHandler(self.filename_to_use)
        self.handler.apply_file(self.filename_to_use,
                                locations=True)

        self.way_list = self.handler.way_list
        self.bounds = (self.minlat, self.minlon, self.maxlat, self.maxlon)
        self.graph = Graph(WayGraph(self.way_list))

    def fetch_extract(self):
        pass

    def check_for_cached_extract(self):

        for existing_file in os.listdir(self.extracts_path):
            if existing_file.startswith(self.area) and existing_file.endswith(".osm"):
                cached_extract_mtime = \
                    datetime.datetime.utcfromtimestamp(
                        os.path.getmtime(self.extracts_path + existing_file))
                if (datetime.datetime.utcnow() - cached_extract_mtime <
                        datetime.timedelta(days=7)):
                    self.filename_to_use = existing_file
                else:
                    self.oldfile_name = existing_file
        

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


class Bounds:
    def __init__(self, bounds):
        self.bounds = bounds
        self.minlat = bounds[0]
        self.minlon = bounds[1]
        self.maxlat = bounds[2]
        self.maxlon = bounds[3]

    def __repr__(self):
        return "Bounds({}).".format(str(self.bounds))
