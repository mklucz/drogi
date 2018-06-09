import drogi
import os
MAP_COLORS = {"walkable": {(0, 0, 0, 255): 1}, "unwalkable": {(255, 255, 255, 255): 0}}
new_map = drogi.WayMap(os.path.dirname(__file__) + "/map.osm", MAP_COLORS)
print(len(new_map.graph))