class Scorer:
    def __init__(self, db_name=None, db_user=None, tile_size=0.001):
        self.db_name = db_name
        self.db_user = db_user
        self.tile_size = tile_size
        self.scoreboard = ScoreBoard(, self.tile_size)
    pass


class ScoreBoard:
    def __init__(self, workrun, tile_size=0.001):
        self.workrun = workrun
        self.tile_size = tile_size

