import matplotlib.pyplot as plt
import numpy as np
import png
from skimage import feature


from pympler import asizeof

from osmprocessor import *
from illustrator import Illustrator
from pathfinder import Pathfinder

MAP_COLORS = {"walkable": {(0, 0, 0, 255) : 1}, "unwalkable": {(255, 255, 255, 255) : 0}}

class ArrayMaker:
    def __init__(self, map_file, map_colors):
        self.map_file = map_file
        self.map_colors = map_colors
    
    def process_png_into_array(map_file, map_colors):
        reader_object = png.Reader(map_file)
        size_x, size_y, contents_iterator, image_attributes = reader_object.read()
        lenght_of_pixel = image_attributes["planes"]
        new_list = []
        for row in contents_iterator:
            new_list.append(list(zip(*[iter(row)]*lenght_of_pixel)))
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

class MapArray:
    def __init__(self, map_file, map_colors):
        self.map_file = map_file
        self.map_colors = map_colors        
        self.array, self.image_attributes = ArrayMaker.process_png_into_array(map_file, map_colors)

class Path:
    def __init__(self, array_size, start, end, length):
        pass
        
class WayListHandler(osmium.SimpleHandler):
    def __init__(self, osm_file):
        osmium.SimpleHandler.__init__(self)
        self.osm_file = osm_file
        self.minlat, self.minlon, self.maxlat, self.maxlon = [float(e) for e in get_bounds(osm_file)]
        self.way_list = []
    
    def draw_walkways(self, way_list):
        
        walkway_map = plt.figure(frameon=False)
        subplot = walkway_map.add_subplot(111)
        walkway_map.subplots_adjust(bottom = 0)
        walkway_map.subplots_adjust(top = 1)
        walkway_map.subplots_adjust(right = 1)
        walkway_map.subplots_adjust(left = 0)
        subplot.set_xlim((self.minlon, self.maxlon))
        subplot.set_ylim((self.minlat, self.maxlat))
        subplot.axis("off")
        subplot.tick_params(axis='both', left='off', top='off', right='off', bottom='off', labelleft='off',
                            labeltop='off', labelright='off', labelbottom='off')
        for e in way_list:
            if e.category == "walkway":
                subplot.plot(list(e.line.xy[0]), list(e.line.xy[1]), color="black", aa=False, linewidth=1.0)
            elif e.category == "crossing":
                subplot.plot(list(e.line.xy[0]), list(e.line.xy[1]), color="black", aa=False, linewidth=1.0)
            elif e.category == "steps":
                subplot.plot(list(e.line.xy[0]), list(e.line.xy[1]), color="black", aa=False, linewidth=1.0)
        plt.gca().xaxis.set_major_locator(plt.NullLocator())
        plt.gca().yaxis.set_major_locator(plt.NullLocator())
        plt.savefig("rendered_walkways01.png", dpi=200, bbox_inches="tight", pad_inches=0)

    def way(self, w):
        try:
            tag = w.tags["highway"]
            if tag in WALKABLE_TAGS_FLAT:
                self.way_list.append(WalkwayContainer(w, "walkway"))
            if tag == "crossing":
                self.way_list.append(WalkwayContainer(w, "crossing"))              
            if tag == "steps":
                self.way_list.append(WalkwayContainer(w, "steps"))
        except:
            pass

class MapProcessor:
    def __init__(self, map_file, map_colors):
        self.map_file = map_file
        self.map_colors = map_colors
        self.processed_map, self.image_attributes = MapProcessor.process_png_into_array(map_file, map_colors)
   
    def process_png_into_array(map_file, map_colors):
        reader_object = png.Reader(map_file)
        size_x, size_y, contents_iterator, image_attributes = reader_object.read()
        lenght_of_pixel = image_attributes["planes"]
        new_list = []
        for row in contents_iterator:
            new_list.append(list(zip(*[iter(row)]*lenght_of_pixel)))
        for i, sublist in enumerate(new_list):
            for j, value in enumerate(sublist):
                if value in map_colors["walkable"]:
                    sublist[j] = map_colors["walkable"][value]
                elif value in map_colors["unwalkable"]:
                    sublist[j] = 0
            new_list[i] = tuple(sublist)
        image_attributes["map_colors"] = map_colors
        return new_list, image_attributes

def paths_adder(processed_map_object):
    holder_array = np.zeros_like(processed_map_object.array, dtype="B")
    for i in range(4):
        print("path: ", i)
        new_path = Illustrator.draw_walked_path(processed_map_object)
        np.add(holder_array, new_path, out=holder_array)
    return holder_array
    pass

if __name__ == '__main__':
    a = OSMProcessor(mapka)
    a.apply_file(mapka, locations=True)
    Illustrator.draw_walkways(a, "Illustrator4.png")
    
    # b = ArrayMaker.process_png_into_array("Illustrator4.png", MAP_COLORS)

    b = MapArray("Illustrator4.png", MAP_COLORS)
    print(type(b))
    Illustrator.render_array_as_png(paths_adder(b), "illustrator_test.png")
    # print(type(b[0]))
    # print(b[0].shape)
    # print(asizeof.asizeof(b[0]))
    
    # big_map = MapProcessor("rendered_walkways01.png", {"walkable": {(0, 0, 0, 255) : 1}, "unwalkable": {(255, 255, 255, 255) : 0}})
    # big_path = Pathfinder.draw_walked_path(big_map)
    # Pathfinder.render_array_as_png(paths_adder(big_map), "adder_test255.png")
    pass

