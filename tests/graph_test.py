import drogi
import os
MAP_COLORS = {"walkable": {(0, 0, 0, 255): 1}, "unwalkable": {(255, 255, 255, 255): 0}}
sample = os.path.dirname(__file__) + "/map.osm"
# new_map = drogi.WayMap(os.path.dirname(__file__) + "/map.osm", MAP_COLORS)
new_run = drogi.WorkRun(osm_file=sample, num_of_trips=10)
print(new_run.chunks[0].trips[0].way_map is new_run.chunks[0].trips[1].way_map)

