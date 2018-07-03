import drogi
import os
# import pickle
# import datetime
# from pympler import asizeof

new_run = drogi.WorkRun((51.2452000, 22.5079000, 51.2510000, 22.5135000),
						num_of_trips=3,
						)
new_run.way_map.save_as_png("test.png")
# new_map = drogi.WayMap((51.2412000, 22.5079000, 51.2470000, 22.5115000))
# new_map.save_as_png("newwaymap.png")
# print(new_map.response[:100])

# new_map = drogi.WayMap(os.path.dirname(__file__) + "/sample.osm")
# new_map.save_as_png("part_test_full.png")
# new_map.save_as_png("newtest.png")

# new_run = drogi.WorkRun(osm_file=sample, num_of_trips=10)
# print(new_run.chunks[0].trips[0].way_map is new_run.chunks[0].trips[1].way_map)

# start_run = datetime.datetime.now()
# berlin_run = drogi.WorkRun(osm_file=berlin_sample, num_of_trips=1)
# print(datetime.datetime.now() - start_run)
# print(asizeof.asizeof(berlin_run))
# ghurken = open("berlin-pickle", "wb")
# pickle.dump(berlin_run.chunks[0].way_map.graph, ghurken)
