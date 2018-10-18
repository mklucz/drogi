import matplotlib.pyplot as plt
import random
import psycopg2
import re
import json
import datetime

from .waymap import WayMap
from .data import BOUNDS_DICT
from .trip import Trip, Path
from .destination_chooser import DestinationChooserAid
        

class WorkRun:
    """Runs a set of simulations"""
    def __init__(self,
                 area,
                 num_of_trips=1,
                 origin_choice="random",
                 destination_choice="random",
                 allowed_means_of_transport="walking",
                 max_trip_radius=0.01,
                 db_name=None,
                 db_user=None,
                 debug=True):
        """
        Top level class that conducts the simulations by getting the data, 
        turning it into a pathfind-able form, traversing it repeatedly and 
        saving the paths in a postgres database.
        """
        self.area = area
        if isinstance(self.area, tuple) and len(self.area) == 4:
            self.bounds = self.area
        else:
            try:
                self.bounds = BOUNDS_DICT[self.area]
            except (KeyError, TypeError):
                raise AttributeError(
                    "area must be a 4-tuple or a BOUNDS_DICT key")
        self.num_of_trips = num_of_trips
        self.origin_choice = origin_choice
        self.destination_choice = destination_choice
        self.allowed_means_of_transport = allowed_means_of_transport
        self.max_trip_radius = max_trip_radius
        self.debug = debug
        self.way_map = WayMap(self.area)
        self.list_of_trips = []
        self.points_list = list(self.way_map.graph)
        self.dest_chooser_aid = self.create_destination_chooser_aid()

        self.db_name = db_name
        self.db_user = db_user
        if self.db_name and self.db_user:
            self.feed_db = True
            self.db_connection = psycopg2.connect("dbname=" + self.db_name +
                                                  " user=" + self.db_user)
            self.table_name = str(datetime.datetime.now()).replace(" ", "")
            self.table_name = re.sub("[^0-9]", "", self.table_name)
            self.table_name = self.area + self.table_name
            self.create_db_table(self.db_connection)
        else:
            self.feed_db = False

        self.run_trips()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        if exc_type is not None:
            return False
        return True

    def create_destination_chooser_aid(self):
        if len(self.points_list) < 2:
            raise ValueError("Not enough points on map")
        dest_chooser_aid = DestinationChooserAid(self.way_map,
                                                 self.points_list,
                                                 self.max_trip_radius)
        self.points_list = dest_chooser_aid.trimmed_points_list
        return dest_chooser_aid

    def create_db_table(self, db_connection):
        creating_query = ("""CREATE TABLE %s (id serial NOT NULL PRIMARY KEY, 
                                             "start" numeric ARRAY[2],
                                             "end" numeric ARRAY[2],
                                             "path" json
                                             );""")
        db_connection.cursor().execute(creating_query % self.table_name)
        db_connection.commit()

    def run_trips(self):
        for trip in range(self.num_of_trips):
            if self.debug:
                if trip % 100 == 0:
                    print(trip, datetime.datetime.now())
            start = random.choice(self.points_list)
            end = self.dest_chooser_aid.find_random_destination(start)
            if start == end:
                continue
            try:
                new_trip = Trip(self.way_map, start, end)
            except (ValueError, AttributeError):
                continue
            self.list_of_trips.append(new_trip)
            if self.feed_db:
                self.insert_trip_into_db(new_trip, self.db_connection)

    def insert_trip_into_db(self, trip, db_connection):
        inserting_query = """INSERT INTO %s(start, "end", "path")
                           VALUES ('%s', '%s', '%s');"""
        db_connection.cursor().execute(
                    inserting_query %
                    (self.table_name,
                     str(list(trip.start)).replace('[', '{').replace(']', '}'),
                     str(list(trip.end)).replace('[', '{').replace(']', '}'),
                     json.dumps(trip.path.list_of_nodes)))
        db_connection.commit()



class Canvas:
    """An object representing a canvas on which to visualize spatial data.
    I.e. a representation of a  stretch of land on which you can draw the roads
    themselves, trips taken on these roads, areas of interest and so on."""
    def __init__(self, bounds, size_factor=400):
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
        size = ((maxlon - minlon) * size_factor, (maxlat - minlat) * size_factor)
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

    def save(self, img_filename, **kwargs):
        plt.savefig(img_filename, bbox_inches="tight", pad_inches=0, **kwargs)
