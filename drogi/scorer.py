import psycopg2

from math import ceil

from .waymap import Bounds


class Scorer:
    def __init__(self, bounds, db_name, db_user, tile_size=0.001):
        self.bounds = bounds
        self.db_name = db_name
        self.db_user = db_user
        self.tile_size = tile_size
        self.db_conn = psycopg2.connect("dbname=" + self.db_name +
                                        " user=" + self.db_user)
        self.scoreboard = ScoreBoard(self.db_conn, self.bounds, self.tile_size)
    pass


class ScoreBoard:
    def __init__(self, db_conn, bounds, tile_size=0.001):
        self.db_conn = db_conn
        self.bounds = bounds
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
                    self.bounds.minlon + (self.tile_size * col) + self.tile_size)))


class Tile:
    def __init__(self, bounds):
        self.bounds = bounds
    pass
