import matplotlib.pyplot as plt
import random
import psycopg2
import re
import json
import datetime

from .waymap import WayMap
from .data import BOUNDS_DICT
from .trip import Trip, Path
        

class WorkRun:
    """Runs a set of simulations"""
    def __init__(self,
                 area,
                 num_of_trips=1,
                 origin_choice="random",
                 destination_choice="random",
                 allowed_means_of_transport="walking",
                 max_radius_of_trip=0.01,
                 dbname="thirdtest",
                 dbuser="mklucz"):
        """
        Top level class that conducts the simulations by getting the data, 
        turning it into a pathfind-able form, traversing it repeatedly and 
        saving the paths in a postgres database.
        """
        self.area = area
        self.bounds = BOUNDS_DICT[self.area]
        self.num_of_trips = num_of_trips
        self.origin_choice = origin_choice
        self.destination_choice = destination_choice
        self.allowed_means_of_transport = allowed_means_of_transport
        self.max_radius_of_trip = max_radius_of_trip
        self.dbname = dbname
        self.dbuser = dbuser
        self.way_map = WayMap(self.area)
        self.list_of_trips = []

        self.table_name = str(datetime.datetime.now()).replace(" ", "")
        self.table_name = re.sub("[^0-9]", "", self.table_name)
        self.table_name = "_" + self.table_name

        conn = psycopg2.connect("dbname=" + self.dbname +
                                " user=" + self.dbuser)
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
            start = random.choice(self.points_list)
            end = self.find_random_destination_inside_radius(start)
            new_trip = Trip(self.way_map, start, end)
            self.list_of_trips.append(new_trip)
            self.insert_trip_into_db(new_trip)

    def find_random_destination_inside_radius(self, start):
        max_radius = self.max_radius_of_trip
        while True:
            end_candidate = random.choice(self.points_list)
            if end_candidate != start:
                if Path.straightline_distance(None, start, end_candidate) \
                        < max_radius:
                    return end_candidate

    def insert_trip_into_db(self, trip):
        conn = psycopg2.connect("dbname=" + self.dbname +
                                " user=" + self.dbuser)
        cur = conn.cursor()
        inserting_query = """INSERT INTO %s(start, "end", "path")
                           VALUES ('%s', '%s', '%s');"""
        cur.execute(inserting_query %
                    (self.table_name,
                     str(list(trip.start)).replace('[', '{').replace(']', '}'),
                     str(list(trip.end)).replace('[', '{').replace(']', '}'),
                     json.dumps(trip.path.list_of_nodes)))
        conn.commit()
        conn.close()


class Canvas:
    """An object representing a canvas on which to visualize spatial data.
    I.e. a representation of a  stretch of land on which you can draw the roads
    themselves, trips taken on these roads, areas of interest and so on."""
    def __init__(self, bounds):
        """
        Prepares a pyplot figure by removing all the margins, padding, axis,
        ticks, labels etc.
        Args:
            bounds(4-tuple): 4 points describing the rectangle to be rendered.
        """
        if not isinstance(bounds, tuple) or len(bounds) != 4:
            raise AttributeError("partial_bounds must be a 4-tuple")
        minlat, maxlat = bounds[0], bounds[2]
        minlon, maxlon = bounds[1], bounds[3]
        size = ((maxlon - minlon) * 400, (maxlat - minlat) * 400)
        self.fig = plt.figure(frameon=False, figsize=size)
        self.subplot = self.fig.add_subplot(111)
        self.fig.subplots_adjust(bottom=0)
        self.fig.subplots_adjust(top=1)
        self.fig.subplots_adjust(right=1)
        self.fig.subplots_adjust(left=0)
        self.subplot.set_xlim((minlon, maxlon))
        self.subplot.set_ylim((minlat, maxlat))
        self.subplot.axis("off")
        self.subplot.tick_params(axis="both",
                                 which="both",
                                 left=False,
                                 top=False,
                                 right=False,
                                 bottom=False,
                                 labelleft=False,
                                 labeltop=False,
                                 labelright=False,
                                 labelbottom=False,
                                 length=0,
                                 width=0,
                                 pad=0)
        plt.gca().xaxis.set_major_locator(plt.NullLocator())
        plt.gca().yaxis.set_major_locator(plt.NullLocator())

    def save(self, img_filename):
        plt.savefig(img_filename, dpi=100, bbox_inches="tight", pad_inches=0)
