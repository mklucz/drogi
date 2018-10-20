import psycopg2

from math import ceil
from datetime import datetime
from collections import namedtuple

from .waymap import Bounds


class Scorer:
    def __init__(self, area, db_name, db_user, tile_size=0.001):
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
    def __init__(self, area, db_conn, tile_size=0.001):
        self.area = area
        self.bounds = self.area.bounds
        self.db_conn = db_conn
        self.tile_size = tile_size
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


TimeSpan = namedtuple("TimeSpan", ("begin", "end"))


class Tile:
    def __init__(self, bounds, parentboard):
        self.bounds = bounds
        self.parentboard = parentboard
        self.area_name = self.parentboard.area.name

    def fetch_paths_from_db(self, time_span):
        paths = []
        for table_name in self.fetch_table_names_for_area():
            if self.table_inside_time_span(table_name, time_span):
                paths.extend(self.fetch_paths_from_table(table_name))
        return paths

    def fetch_paths_from_table(self, table_name):
        test_query = """SELECT "path" FROM {} WHERE
                        ("start"[0] > 0);""".format(table_name)
        test_query2 = """SELECT "start"[2] FROM {}""".format(table_name)
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
                   """.format(table_name,
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

