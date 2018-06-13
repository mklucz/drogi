import drogi
import os
import pickle
import datetime
from pympler import asizeof

new_map = drogi.WayMap(os.path.dirname(__file__) + "/sample.osm")
# new_map.save_part_as_png("part_test.png", (100, 100, 100))
new_map.save_part_as_png("part_test_full.png")
# new_map.save_as_png("newtest.png")

# new_run = drogi.WorkRun(osm_file=sample, num_of_trips=10)
# print(new_run.chunks[0].trips[0].way_map is new_run.chunks[0].trips[1].way_map)




# start_run = datetime.datetime.now()
# berlin_run = drogi.WorkRun(osm_file=berlin_sample, num_of_trips=1)
# print(datetime.datetime.now() - start_run)
# print(asizeof.asizeof(berlin_run))
# ghurken = open("berlin-pickle", "wb")
# pickle.dump(berlin_run.chunks[0].way_map.graph, ghurken)
