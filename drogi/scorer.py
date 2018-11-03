import psycopg2
import numpy as np

from math import ceil
from datetime import datetime
from collections import namedtuple
from shapely.geometry import LineString

from .waymap import Bounds

TimeSpan = namedtuple("TimeSpan", ("begin", "end"))

YEAR_2018 = TimeSpan(begin=datetime.strptime("20180101", "%Y%m%d"),
                     end=datetime.now())


class Scorer:
    def __init__(self, area, db_name, db_user, tile_size=0.0001):
        self.area = area
        self.bounds = self.area.bounds
        self.db_name = db_name
        self.db_user = db_user
        self.tile_size = tile_size
        self.db_conn = psycopg2.connect("dbname=" + self.db_name +
                                        " user=" + self.db_user)
        self.scoreboard = ScoreBoard(self.area, self.db_conn, self.tile_size)
    pass


class ScoreBoard:
    def __init__(self, area, db_conn, tile_size=0.0001, time_span=YEAR_2018):
        self.area = area
        self.bounds = self.area.bounds
        self.db_conn = db_conn
        self.tile_size = tile_size
        self.time_span = time_span
        self.tiles = self.initialize_tiles()

    def initialize_tiles(self):
        num_of_cols = ceil(abs(self.bounds.minlat - self.bounds.maxlat)
                           / self.tile_size)
        num_of_rows = ceil(abs(self.bounds.minlon - self.bounds.maxlon)
                           / self.tile_size)
        return [[self.make_tile(col, row) for col in range(num_of_cols)]
                for row in range(num_of_rows)]

    def make_tile(self, col, row):
        return Tile(
            Bounds((self.bounds.minlat + (self.tile_size * row),
                    self.bounds.minlon + (self.tile_size * col),
                    self.bounds.minlat + (self.tile_size * row) + self.tile_size,
                    self.bounds.minlon + (self.tile_size * col) + self.tile_size)),
            self)

    @property
    def avg_dev_factors_array(self):
        new_array = []
        for row in self.tiles:
            new_row = []
            for col in row:
                new_row.append(float(col))
            new_array.append(new_row)
        return new_array

class Tile:
    def __init__(self, bounds, parentboard):
        self.bounds = bounds
        self.parentboard = parentboard
        self.area_name = self.parentboard.area.name
        self.paths = self.fetch_paths_from_db(self.parentboard.time_span)

    def fetch_paths_from_db(self, time_span):
        paths = []
        for table_name in self.fetch_table_names_for_area():
            if self.table_inside_time_span(table_name, time_span):
                paths.extend(self.fetch_paths_from_table(table_name))
        return paths

    def fetch_paths_from_table(self, table_name):
        query = """SELECT "path" FROM {} WHERE
                   ("start"[1] > {} AND
                    "start"[1] < {} AND
                    "start"[2] > {} AND
                    "start"[2] < {})
                   OR
                   ("end"[1] > {} AND
                    "end"[1] < {} AND
                    "end"[2] > {} AND
                    "end"[2] < {});
                   """.format(table_name.lower(),
                              self.bounds.minlon,
                              self.bounds.maxlon,
                              self.bounds.minlat,
                              self.bounds.maxlat,
                              self.bounds.minlon,
                              self.bounds.maxlon,
                              self.bounds.minlat,
                              self.bounds.maxlat)
        curr = self.parentboard.db_conn.cursor()
        curr.execute(query)
        return [e[0] for e in curr.fetchall()]

    def fetch_table_names_for_area(self):
        query = """SELECT table_name FROM information_schema.tables
                   WHERE table_name LIKE '%{}%';""".format(self.area_name)
        curr = self.parentboard.db_conn.cursor()
        curr.execute(query)
        return [e[0] for e in curr.fetchall()]

    def table_inside_time_span(self, table_name, time_span):
        time_portion = table_name.replace(self.area_name, "")
        time_of_table = datetime.strptime(time_portion, "%Y%m%d%H%M%S")
        return time_span.begin < time_of_table < time_span.end

    @property
    def avg_dev_factor(self):
        dev_factors = []
        for path in self.paths:
            try:
                linestring = LineString(path)
                straightline = LineString((path[0], path[-1]))
                dev_factors.append(linestring.length / straightline.length)
            except IndexError:
                continue
        if len(dev_factors) == 0:
            return 0
        return (1 / (sum(dev_factors) / len(dev_factors))) * 255

    def __float__(self):
        return float(self.avg_dev_factor)