import osmium
import shapely.wkb as wkblib
import xml.etree.ElementTree
import matplotlib.pyplot as plt
import png
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
                subplot.plot(list(e.line.xy[0]), list(e.line.xy[1]), color="blue")
            elif e.category == "crossing":
                subplot.plot(list(e.line.xy[0]), list(e.line.xy[1]), color="blue")
            elif e.category == "steps":
                subplot.plot(list(e.line.xy[0]), list(e.line.xy[1]), color="blue")
        plt.gca().xaxis.set_major_locator(plt.NullLocator())
        plt.gca().yaxis.set_major_locator(plt.NullLocator())
        plt.savefig("rendered_walkways.png", dpi=300, bbox_inches="tight", pad_inches=0)

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
        return new_list, image_attributes #TODO: put this in an object like a civilized man

class Pathfinder:
    def __init__(self, processed_map):
        self.walkways_array = processed_map[0]
        self.image_attributes = processed_map[1]

    def pick_random_spot(processed_map):
        height, width = (processed_map[1]["size"])
        while True:
            picked_x, picked_y = randint(0, height - 1), randint(0, width - 1)
            # print(picked_x, picked_y)
            # print(processed_map[0])
            # print(processed_map[0][picked_x])
            if processed_map[0][picked_y][picked_x] > 0:
                return picked_x, picked_y


    def find_path(walkways_array):
        # print(walkways_array)
        grid = Grid(matrix=walkways_array[0])
        # starting_coords = 
        start = grid.node(*Pathfinder.pick_random_spot(walkways_array))
        end = grid.node(*Pathfinder.pick_random_spot(walkways_array))

        finder = AStarFinder(diagonal_movement=DiagonalMovement.always)
        path, runs = finder.find_path(start, end, grid)

        print('operations:', runs, 'path length:', len(path))
        print(grid.grid_str(path=path, start=start, end=end))



if __name__ == '__main__':
    # print(Pathfinder.find_path(MapProcessor.process_png_into_array("littleL.png", {"walkable": {(0, 0, 0) : 1}, "unwalkable": {(255, 255, 255, 255) : 0}})))
    print(Pathfinder.find_path(MapProcessor.process_png_into_array("littleH.png", {"walkable": {(0, 0, 0, 255) : 1}, "unwalkable": {(255, 255, 255, 255) : 0}})))
    # print(MapProcessor.process_png_into_array("littleH.png", {"walkable": {(0, 0, 0, 255) : 1}, "unwalkable": {(255, 255, 255, 255) : 0}}))
    # # h = WayListHandler(mapka)
    # h.apply_file(mapka, locations=True)
    # h.draw_walkways(h.way_list)
    pass

