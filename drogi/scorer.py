import psycopg2


class Scorer:
    def __init__(self, db_name=None, db_user=None, tile_size=0.001):
        self.db_name = db_name
        self.db_user = db_user
        self.tile_size = tile_size
        self.db_conn = psycopg2.connect("dbname=" + self.db_name +
                                        " user=" + self.db_user)
        self.scoreboard = ScoreBoard(self.db_conn, self.tile_size)
    pass


class ScoreBoard:
    def __init__(self, db_conn, tile_size=0.001):
        self.db_conn = db_conn
        self.tile_size = tile_size


class Tile:
    pass
