import osmium
import shapely.wkb as wkblib
import xml.etree.ElementTree
import matplotlib.pyplot as plt
import png
import numpy as np
from skimage import feature
from pathfinding.core.diagonal_movement import DiagonalMovement
from pathfinding.core.grid import Grid
from pathfinding.finder.a_star import AStarFinder
from random import randint



walkable_tags = ["footway", "bridleway", "steps", "path, living_street", "pedestrian",
                "residential", "crossing"]
wkb_factory = osmium.geom.WKBFactory()
mapka = "map.osm"

def get_bounds(osm_xml_file):
    for line in open(osm_xml_file):
        if "<bounds" in line:
            loaded_xml = xml.etree.ElementTree.fromstring(line)
            return loaded_xml.get("minlat"), loaded_xml.get("minlon"), loaded_xml.get("maxlat"), loaded_xml.get("maxlon")

class WalkwayContainer:
    def __init__(self, way, category):
        self.way = way
        self.category = category
        self.line = wkblib.loads(wkb_factory.create_linestring(way), hex=True)

class WayListHandler(osmium.SimpleHandler):
    def __init__(self, osm_file):
        osmium.SimpleHandler.__init__(self)
        self.osm_file = osm_file
        self.minlat, self.minlon, self.maxlat, self.maxlon = [float(e) for e in get_bounds(osm_file)]
        self.way_list = []
    
    def draw_walkways(self, way_list):
        
        walkway_map = plt.figure(frameon=False, facecolor="black")
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
        walkable_tags = ["footway", "bridleway", "living_street", "pedestrian",
                        "residential"]
        try:
            tag = w.tags["highway"]
            if tag in walkable_tags:
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
   
    def chunks(l, n):
        """Yield successive n-sized chunks from l.
        https://stackoverflow.com/questions/312443/how-do-you-split-a-list-into-evenly-sized-chunks"""
        for i in range(0, len(l), n):
            yield l[i:i + n]

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
        image_attributes["map_colors"] = map_colors
        return new_list, image_attributes

class Pathfinder:
    def __init__(self, processed_map):
        self.walkways_array = processed_map[0]
        self.image_attributes = processed_map[1]

    def pick_random_spot(processed_map_object):
        height, width = (processed_map_object.image_attributes["size"])
        while True:
            picked_x, picked_y = randint(0, height - 1), randint(0, width - 1)
            # print(picked_x, picked_y)
            # print(processed_map[0])
            # print(processed_map[0][picked_x])
            if processed_map_object.processed_map[picked_y][picked_x] > 0:
                return picked_x, picked_y


    def find_path_between_random_spots(processed_map_object):
        # print(processed_map_object)
        grid = Grid(matrix=processed_map_object.processed_map)
        # starting_coords = 
        start = grid.node(*Pathfinder.pick_random_spot(processed_map_object))
        end = grid.node(*Pathfinder.pick_random_spot(processed_map_object))

        finder = AStarFinder(diagonal_movement=DiagonalMovement.always)
        path, runs = finder.find_path(start, end, grid)

        print('operations:', runs, 'path length:', len(path))
        # print(grid.grid_str(path=path, start=start, end=end))
        # print(runs)
        return path

    def draw_walked_path(processed_map_object):
        path = Pathfinder.find_path_between_random_spots(processed_map_object)
        array_to_return = np.zeros_like(processed_map_object.processed_map, dtype="B")
        for step in path:
            y, x = step[0], step[1]
            array_to_return[x][y] = 1
        return array_to_return

    def render_array_as_png(path_array, filename):
        f = open(filename, "wb")
        size = (len(path_array[0]), len(path_array))
        writer = png.Writer(*size, greyscale=True, bitdepth=8)
        writer.write(f, path_array)
        f.close()






# littleH = MapProcessor("littleH.png", {"walkable": {(0, 0, 0, 255) : 1}, "unwalkable": {(255, 255, 255, 255) : 0}})
# path_array = Pathfinder.draw_walked_path(littleH)
def paths_adder(processed_map_object):
    holder_array = np.zeros_like(processed_map_object.processed_map, dtype="B")
    for i in range(250):
        print("path: ", i)
        new_path = Pathfinder.draw_walked_path(processed_map_object)
        np.add(holder_array, new_path, out=holder_array)
    return holder_array
    pass

if __name__ == '__main__':
    # print(Pathfinder.find_path_between_random_spots(([[[1] for i in range(10)] for j in range(10)], {"size": (10, 10)})))
    # print(Pathfinder.find_path_between_random_spots(littleH))
    # Pathfinder.render_array_as_png(path_array, "pypng_test.png")
    # print(Pathfinder.find_path_between_random_spots(MapProcessor.process_png_into_array("littleH.png", {"walkable": {(0, 0, 0, 255) : 1}, "unwalkable": {(255, 255, 255, 255) : 0}})))
    # print(MapProcessor.process_png_into_array("littleH.png", {"walkable": {(0, 0, 0, 255) : 1}, "unwalkable": {(255, 255, 255, 255) : 0}}))
    
    # h = WayListHandler(mapka)
    # h.apply_file(mapka, locations=True)
    # h.draw_walkways(h.way_list)
    big_map = MapProcessor("rendered_walkways01.png", {"walkable": {(0, 0, 0, 255) : 1}, "unwalkable": {(255, 255, 255, 255) : 0}})
    # big_path = Pathfinder.draw_walked_path(big_map)
    Pathfinder.render_array_as_png(paths_adder(big_map), "adder_test255.png")
    pass

