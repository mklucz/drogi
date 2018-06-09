from pathfinding.core.diagonal_movement import DiagonalMovement
from pathfinding.core.grid import Grid
from pathfinding.finder.a_star import AStarFinder
from pathfinding.finder.finder import ExecutionRunsException
from random import randint

class Pathfinder:
    def __init__(self, processed_map):
        self.walkways_array = processed_map[0]
        self.image_attributes = processed_map[1]

    def pick_random_spot(processed_map_object):
        height, width = (processed_map_object.image_attributes["size"])
        while True:
            picked_x, picked_y = randint(0, height - 1), randint(0, width - 1)
            if processed_map_object.array[picked_y][picked_x] > 0:
                return picked_x, picked_y


    def find_path_between_random_spots(way_map, max_runs=32000):
        grid = way_map.grid
        start = grid.node(*Pathfinder.pick_random_spot(way_map))
        end = grid.node(*Pathfinder.pick_random_spot(way_map))

        finder = AStarFinder(diagonal_movement=DiagonalMovement.always, max_runs=max_runs)
        try:
            path, runs = finder.find_path(start, end, grid)
        except ExecutionRunsException:
            grid.cleanup()
            return []
        print('operations:', runs, 'path length:', len(path))
        grid.cleanup()
        return path
