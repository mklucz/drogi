import timeit
from pathfinding.core.grid import Grid
print(timeit.timeit("Grid(1000, 1000)", setup="from pathfinding.core.grid import Grid", number=10))