import matplotlib.pyplot as plt
import numpy as np
import png
import pickle
import random
import overpass
import psycopg2
import re
import json

from shapely.geometry import LineString, MultiLineString
# from skimage import feature
from networkx.algorithms.shortest_paths.astar import astar_path
from networkx import Graph
from networkx.exception import NetworkXNoPath
from datetime import datetime
from math import sqrt

from .osmhandler import *
from .illustrator import Illustrator
from .pathfinder import Pathfinder

BOUNDS_DICT = {
    "Lublin" : (51.1942, 22.4145, 51.3040, 22.6665),
    "small_test" : (51.2412000, 22.5079000, 51.2470000, 22.5115000)
}

class WayMap:
    """Contains GIS-type data describing physical layout of ways in a particular area"""

    def __init__(self, bounds_to_fetch, filename=None):
        """
        Args:
            bounds_to_fetch(4-tuple): geographic bounding box of the area to be.
                mapped, in the following order: (minlat, minlon, maxlat, maxlon)
            filename(str): filename to save the fetched extract as.
        """
        self.minlat = bounds_to_fetch[0]
        self.minlon = bounds_to_fetch[1]
        self.maxlat = bounds_to_fetch[2]
        self.maxlon = bounds_to_fetch[3]
        if filename is None:
            filename = "extract_" + str(datetime.now()).replace(" ", "_") + ".osm"
        api = overpass.API(timeout=600)
        map_query = overpass.MapQuery(self.minlat, self.minlon, self.maxlat, self.maxlon)
        response = api.get(map_query, responseformat="xml")
        with open(filename, "w") as f:
            f.write(response)
        self.handler = OSMHandler(filename)
        self.handler.apply_file(filename, locations=True)
        self.way_list = self.handler.way_list
        self.bounds = (self.minlat, self.minlon, self.maxlat, self.maxlon)
        self.graph = Graph(WayGraph(self.way_list))

    def save_as_png(self, filename, partial_bounds=None):
        """
        Renders the map and saves it as a png in current working directory
            Args:
                filename(str): filename to save the png as.
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
        fig.subplots_adjust(bottom = 0)
        fig.subplots_adjust(top = 1)
        fig.subplots_adjust(right = 1)
        fig.subplots_adjust(left = 0)
        subplot.set_xlim((p_minlon, p_maxlon))
        subplot.set_ylim((p_minlat, p_maxlat))
        subplot.axis("off")
        subplot.tick_params(axis="both", which="both", left=False, top=False, right=False, bottom=False, labelleft=False,
                            labeltop=False, labelright=False, labelbottom=False, length=0, width=0, pad=0)
        for e in self.way_list:
            if e.category == "walkway":
                subplot.plot(list(e.line.xy[0]), list(e.line.xy[1]), color="black", aa=False, linewidth=0.1)
            elif e.category == "crossing":
                subplot.plot(list(e.line.xy[0]), list(e.line.xy[1]), color="black", aa=False, linewidth=0.1)
            elif e.category == "steps":
                subplot.plot(list(e.line.xy[0]), list(e.line.xy[1]), color="black", aa=False, linewidth=0.1)
        plt.gca().xaxis.set_major_locator(plt.NullLocator())
        plt.gca().yaxis.set_major_locator(plt.NullLocator())
        # plt.autoscale(tight=False, enable=False)
        plt.savefig(filename, dpi=100, bbox_inches="tight", pad_inches=0)


class WorkRun():
    """Runs a set of simulations"""
    def __init__(self,
                 bounds,
                 num_of_trips=1,
                 origin_choice="random",
                 destination_choice="random",
                 allowed_means_of_transport="walking",
                 max_radius_of_trip = 0.01,
                 dbname="thirdtest",
                 dbuser="mklucz"):
        """
        Top level class that conducts the simulations by getting the data, 
        turning it into a pathfind-able form, traversing it repeatedly and 
        saving the paths in a postgres database.
        """
        super(WorkRun, self).__init__()
        self.bounds = bounds
        self.num_of_trips = num_of_trips
        self.origin_choice = origin_choice
        self.destination_choice = destination_choice
        self.allowed_means_of_transport = allowed_means_of_transport
        self.max_radius_of_trip = max_radius_of_trip
        self.dbname = dbname
        self.dbuser = dbuser
        self.way_map = WayMap(self.bounds)
        
        self.table_name = str(datetime.now()).replace(" ", "") # + "_" + str(bounds).replace(" ", "")
        self.table_name = re.sub("[^0-9]", "", self.table_name)
        self.table_name = "_" + self.table_name
        
        conn = psycopg2.connect("dbname=" + self.dbname + " user=" + self.dbuser)
        cur = conn.cursor()
        creating_query = ("""CREATE TABLE %s (id serial NOT NULL PRIMARY KEY, 
                                        "start" numeric ARRAY[2],
                                        "end" numeric ARRAY[2],
                                        "path" json
                                         );""")
        cur.execute(creating_query % self.table_name)
        conn.commit()
        # cur.execute("""SELECT table_name FROM information_schema.tables
        #                WHERE table_schema = 'public'""")
        # for table in cur.fetchall():
        #     print(table)
        
        self.points_list = list(self.way_map.graph)
        if len(self.points_list) < 2:
            raise ValueError("Not enough points on map")
        
        for trip in range(self.num_of_trips):
            if self.origin_choice == "random":
                start = random.choice(self.points_list)
                print("XXXX\n\n", start)
            if self.destination_choice == "random":
                end_candidate = random.sample(self.points_list, 1)

            new_trip = Trip(self.way_map, start, end)
            self.insert_trip_into_db(new_trip)
        
    def straightline_distance(p1, p2):
        x_dist = abs(p1[0] - p2[0])
        y_dist = abs(p1[1] - p2[1])
        return sqrt(x_dist**2 + y_dist**2)


    def find_random_destination_inside_radius(start):
        max_radius = self.max_radius_of_trip
        end_candidate = random.sample(self.points_list, 1)




    def insert_trip_into_db(self, trip):
        conn = psycopg2.connect("dbname=" + self.dbname + " user=" + self.dbuser)
        cur = conn.cursor()
        inserting_query = """INSERT INTO %s(start, "end", "path")
                           VALUES ('%s', '%s', '%s');"""
        cur.execute(inserting_query % (self.table_name,
                                       str(list(trip.start)).replace('[', '{').replace(']', '}'),
                                       str(list(trip.end)).replace('[', '{').replace(']', '}'),
                                       json.dumps(trip.path.list_of_nodes)))
        conn.commit()
        conn.close()


class Trip():
    """docstring for Trip"""
    def __init__(self, way_map, start, end):
        super(Trip, self).__init__()
        self.way_map = way_map
        self.start = start
        self.end = end
        self.path = Path(self.way_map, self.start, self.end)
        if len(self.path) >= 2:
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
        self.linestring = MultiLineString(self.list_of_nodes)
        self.length = self.linestring.length
        self.straightline_length = LineString(self.start, self.end).length
           

class WayGraph(dict):
    """docstring for WayGraph"""
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


def paths_adder(way_map, num_of_paths, walking_function):
    holder_array = np.zeros_like(way_map.array, dtype="B")
    for i in range(num_of_paths):
        print("path: ", i)
        new_path = Illustrator.draw_walked_path(way_map, walking_function)
        np.add(holder_array, new_path, out=holder_array)
    return holder_array
    pass


if __name__ == '__main__':

    pass
