# import matplotlib.pyplot as plt
import numpy as np
import png
import pickle
import shapely.ops
# from skimage import feature
# from pympler import asizeof
from pathfinding.core.grid import Grid
from osmhandler import *
from illustrator import Illustrator
from pathfinder import Pathfinder

MAP_COLORS = {"walkable": {(0, 0, 0, 255): 1}, "unwalkable": {(255, 255, 255, 255): 0}}


class WayMap:
    def __init__(self, map_file, map_colors):
        self.map_file = map_file
        self.map_colors = map_colors
        self.array, self.image_attributes = WayMap.process_png_into_array(map_file, map_colors)
        self.grid = Grid(matrix=self.array)

    def process_png_into_array(map_file, map_colors):
        reader_object = png.Reader(map_file)
        size_x, size_y, contents_iterator, image_attributes = reader_object.read()
        lenght_of_pixel = image_attributes["planes"]
        new_list = []
        for row in contents_iterator:
            new_list.append(list(zip(*[iter(row)] * lenght_of_pixel)))
        for sublist in new_list:
            for i in range(len(sublist)):
                if sublist[i] in map_colors["walkable"]:
                    sublist[i] = map_colors["walkable"][sublist[i]]
                elif sublist[i] in map_colors["unwalkable"]:
                    sublist[i] = 0
            sublist = tuple(sublist)
        new_list = np.asarray(new_list, dtype="B")
        image_attributes["map_colors"] = map_colors
        return new_list, image_attributes


class Path:
    def __init__(self, array_size, start, end, length):
        pass

class Graph(dict):
    """docstring for Graph"""
    def __init__(self, way_list):
        super(Graph, self).__init__()
        self.way_list = way_list
        # self.lines = shapely.ops.linemerge([e[0] for e in self.way_list])
        # print(way_list[1])
        for way in self.way_list:
            linestring = way[0]
            category = way[1]
            x = linestring.coords.xy[0]
            y = linestring.coords.xy[1]
            for i in range(len(x)):
                xy = (x[i], y[i])
                if i == 0:
                    if xy not in self:
                        self[xy] = [(x[i + 1], y[i + 1])]
                    else:
                        self[xy].append((x[i + 1], y[i + 1]))
                elif i == len(x) - 1:
                    if xy not in self:
                        self[xy] = [(x[i - 1], y[i - 1])]
                    else:
                        self[xy].append((x[i - 1], y[i - 1]))
                else:
                    if xy not in self:
                        self[xy] = [(x[i + 1], y[i + 1]), (x[i - 1], y[i - 1])]
                    else:
                        self[xy].append((x[i + 1], y[i + 1]))
                        self[xy].append((x[i - 1], y[i - 1]))
            


def paths_adder(way_map, num_of_paths, walking_function):
    holder_array = np.zeros_like(way_map.array, dtype="B")
    for i in range(num_of_paths):
        print("path: ", i)
        new_path = Illustrator.draw_walked_path(way_map, walking_function)
        np.add(holder_array, new_path, out=holder_array)
    return holder_array
    pass


if __name__ == '__main__':
    # a = OSMHandler(mapka)
    # a.apply_file(mapka, locations=True)

    # pickle.dump([[e.line, e.category] for e in a.way_list], open("ogorek", "wb"))

    lines = pickle.load(open("ogorek", "rb"))
    g = Graph(lines)
    print(len(g))
    # graph = {}
    # multiline = shapely.ops.linemerge([e[0] for e in lines])
    # for single_line in multiline:
    #     x = single_line.coords.xy[0]
    #     y = single_line.coords.xy[1]
    #     for i in range(len(x)):
    #         xy = (x[i], y[i])
    #         if i == 0:
    #             if xy not in graph:
    #                 graph[xy] = [(x[i + 1], y[i + 1])]
    #             else:
    #                 graph[xy].append((x[i + 1], y[i + 1]))
    #         elif i == len(x) - 1:
    #             if xy not in graph:
    #                 graph[xy] = [(x[i - 1], y[i - 1])]
    #             else:
    #                 graph[xy].append((x[i - 1], y[i - 1]))
    #         else:
    #             if xy not in graph:
    #                 graph[xy] = [(x[i + 1], y[i + 1]), (x[i - 1], y[i - 1])]
    #             else:
    #                 graph[xy].append((x[i + 1], y[i + 1]))
    #                 graph[xy].append((x[i - 1], y[i - 1]))

    # print(len(graph))

    # Illustrator.linestrings_to_graph(a)
    # Illustrator.draw_walkways(a, "Illustrator5.png")
    # b = WayMap("Illustrator5.png", MAP_COLORS)

    # # print(type(b))
    # Illustrator.render_array_as_png(paths_adder(b, 4, "find_path_between_random_spots"), "illustrator_test2.png", 2)

    pass
