import drogi
import shapely.geometry as shg
import shapely.ops as sho
from matplotlib import pyplot as plt
# import os
# import pickle
# import datetime
# from pympler import asizeof
# 51.2452000, 22.5079000, 51.2510000, 22.5135000)
import datetime
# import warnings
# import matplotlib.cbook
# warnings.filterwarnings("ignore", category=matplotlib.cbook.mplDeprecation)
#

my_run = drogi.WorkRun("lublin_small", num_of_trips=1000)
my_canvas = drogi.Canvas(my_run.way_map.bounds_to_fetch)
my_run.way_map.render_on_canvas(my_canvas,
                                 color="black",
                                 aa=True,
                                 linewidth=0.5,
                                 alpha=0.5)
for trip in my_run.list_of_trips:
    dev_factor = trip.path.deviation_factor
    trip.path.render_on_canvas(my_canvas,
                               color="blue",
                               aa=False,
                               linewidth=0.7,
                               alpha=0.3)
    for obstacle in trip.path.obstacles:
        obstacle.render_on_canvas(my_canvas,
                                  color="red",
                                  alpha=((dev_factor / 1) / 100),
                                  linewidth=0,
                                  edgecolor=None)

my_canvas.save("lublin_dev_factor2.png", dpi=150)
# print(datetime.datetime.now())
# new_run = drogi.WorkRun("bigger_test", num_of_trips=20000)
# print(datetime.datetime.now())
# my_canvas = drogi.Canvas(new_run.way_map.bounds_to_fetch)
# new_run.way_map.render_on_canvas(my_canvas,
#                                  color="black",
#                                  aa=False,
#                                  linewidth=0.1,
#                                  alpha=0.2)
# my_canvas.save("just_walkways.png")
# for trip in new_run.list_of_trips:
#     trip.path.render_on_canvas(my_canvas,
#                                color="blue",
#                                aa=False,
#                                linewidth=0.1,
#                                alpha=0.01)
#     for obstacle in trip.path.obstacles:
#         obstacle.render_on_canvas(my_canvas,
#                                   color="red",
#                                   alpha=0.005,
#                                   linewidth=0,
#                                   edgecolor=None)
# curr_time = str(datetime.datetime.utcnow()).replace(" ", "_")
# print(datetime.datetime.now())
#
# my_canvas.save("bigger_test" + curr_time + ".png")
# new_run = drogi.WorkRun("lublin_small", num_of_trips=100)
# my_canvas = drogi.Canvas(new_run.way_map.bounds_to_fetch)
# new_run.way_map.render_on_canvas(my_canvas,
#                                  color="black",
#                                  aa=True,
#                                  linewidth=0.7,
#                                  alpha=0.5)
# # my_canvas.save("lublin_small4.png", dpi=150)
#
# for trip in new_run.list_of_trips:
#     trip.path.render_on_canvas(my_canvas,
#                                color="red",
#                                aa=True,
#                                linewidth=1,
#                                alpha=0.1)
# my_canvas.save("lublin_with_paths2.png", dpi=150)
#
