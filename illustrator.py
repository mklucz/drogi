import matplotlib.pyplot as plt
import numpy as np
import png
from pathfinder import Pathfinder

class Illustrator:
    def __init__(self, processed_osm, filename_to_save_with):
        self.processed_osm = processed_osm
        self.filename_to_save_with = filename_to_save_with

    def draw_walkways(self, filename_to_save_with):
        way_list = self.way_list
        fig = plt.figure(frameon=False)
        subplot = fig.add_subplot(111)
        fig.subplots_adjust(bottom = 0)
        fig.subplots_adjust(top = 1)
        fig.subplots_adjust(right = 1)
        fig.subplots_adjust(left = 0)
        subplot.set_xlim((self.minlon, self.maxlon))
        subplot.set_ylim((self.minlat, self.maxlat))
        subplot.axis("off")
        subplot.tick_params(axis='both', left='off', top='off', right='off', bottom='off', labelleft='off',
                            labeltop='off', labelright='off', labelbottom='off')
        for e in way_list:
            if e.category == "walkway":
                subplot.plot(list(e.line.xy[0]), list(e.line.xy[1]), color="black", aa=False, linewidth=0.1)
            elif e.category == "crossing":
                subplot.plot(list(e.line.xy[0]), list(e.line.xy[1]), color="black", aa=False, linewidth=0.1)
            elif e.category == "steps":
                subplot.plot(list(e.line.xy[0]), list(e.line.xy[1]), color="black", aa=False, linewidth=0.1)
        plt.gca().xaxis.set_major_locator(plt.NullLocator())
        plt.gca().yaxis.set_major_locator(plt.NullLocator())
        plt.savefig(filename_to_save_with, dpi=200, bbox_inches="tight", pad_inches=0)
    
    def draw_walked_path(way_map, walking_function):
        path = getattr(Pathfinder, walking_function)(way_map)
        array_to_return = np.zeros_like(way_map.array, dtype="B")
        for step in path:
            y, x = step[0], step[1]
            array_to_return[x][y] = 1
        return array_to_return

    def render_array_as_png(path_array, filename, bitdepth):
        f = open(filename, "wb")
        size = (len(path_array[0]), len(path_array))
        writer = png.Writer(*size, greyscale=True, bitdepth=bitdepth)
        writer.write(f, path_array)
        f.close()
