from math import ceil
from random import choice


class DestinationChooserAid(list):
    """Helper to speed up random destination choosing by holding available
    destinations in boxes of size max_trip_radius ** 2.
    With this we can, upon randomly selecting an origin point, fetch
    possible destinations in the origin point's box (or "box"), along with those
    of its eight neighbouring boxes, like so:
    NNN
    NON
    NNN
    We can then pick a random point from the sum of these nine lists and check
    if it's withing max_trip_radius of origin. It will be in 3.14 / 9 cases,
    which beats the pickles out of trying the same with a point from anywhere
    at all.
    """
    def __init__(self, way_map, points_list, max_trip_radius):
        super(DestinationChooserAid, self).__init__()
        """

        Args:
            way_map: a WayMap instance to base on.
            max_trip_radius: expressed in degrees.
        """
        self.way_map = way_map
        self.points_list = points_list
        self.max_trip_radius = max_trip_radius
        self.horizontal_stretch = abs(self.way_map.minlon - self.way_map.maxlon)
        self.vertical_stretch = abs(self.way_map.minlat - self.way_map.maxlat)
        self.num_of_rows = ceil(self.horizontal_stretch / self.max_trip_radius)
        self.num_of_cols = ceil(self.vertical_stretch / self.max_trip_radius)
        self.array = self.Array(self.num_of_rows, self.num_of_cols)
        self.trimmed_points_list = []
        for point in self.points_list:
            x, y = point[0], point[1]
            row_to_insert = (x - self.way_map.minlon) // self.max_trip_radius
            if row_to_insert < 0 or row_to_insert > self.num_of_rows - 1:
                continue
            col_to_insert = (y - self.way_map.minlat) // self.max_trip_radius
            if col_to_insert < 0 or col_to_insert > self.num_of_cols - 1:
                continue
            self.array[int(row_to_insert)][int(col_to_insert)].append(point)
            self.trimmed_points_list.append(point)

    def find_random_destination(self, starting_point):
        start_x = starting_point[0]
        start_y = starting_point[1]
        start_row = int((start_x - self.way_map.minlon) // self.max_trip_radius)
        start_col = int((start_y - self.way_map.minlat) // self.max_trip_radius)
        rows_to_pick_from = [start_row, ]
        if start_row > 0:
            rows_to_pick_from.append(start_row - 1)
            if start_row < self.num_of_rows:
                rows_to_pick_from.append(start_row)
        cols_to_pick_from = [start_col, ]
        if start_col > 0:
            cols_to_pick_from.append(start_col - 1)
            if start_col < self.num_of_cols:
                cols_to_pick_from.append(start_col)
        points_to_pick_from = []
        for row in rows_to_pick_from:
            for col in cols_to_pick_from:
                points_to_pick_from += self.array[row][col]
        return choice(points_to_pick_from)

    class Array(list):
        """Array of rows containing fields containing map points."""
        def __init__(self, num_of_rows, num_of_cols):
            super(DestinationChooserAid.Array, self).__init__()
            self.num_of_rows = num_of_rows
            self.num_of_cols = num_of_cols
            for row in range(self.num_of_rows):
                self.append(DestinationChooserAid.Row(self.num_of_cols, row))

    class Row(list):
        """Row containing individual fields."""
        def __init__(self, num_of_cols, row):
            super(DestinationChooserAid.Row, self).__init__()
            self.num_of_cols = num_of_cols
            for col in range(self.num_of_cols):
                self.append(DestinationChooserAid.Field(row, col))

    class Field(list):
        """Smallest constituent of a DestinationChooserArray."""
        def __init__(self, row, col):
            super(DestinationChooserAid.Field, self).__init__()
            self.row = row
            self.col = col

        def get_neighbors(self):
            return self.row, self.col
