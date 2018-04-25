import osmium
import shapely.wkb as wkblib
import xml.etree.ElementTree
from matplotlib import pyplot

class WalkwayCounterHandler(osmium.SimpleHandler):
    def __init__(self):
        osmium.SimpleHandler.__init__(self)
        self.num_nodes = 0
    
    def count_walkway(self, tags):
        walkable_tags = ["footway", "bridleway", "steps", "path, living_street", "pedestrian",
                        "residential", "crossing"]
        try:
            if tags['highway'] in walkable_tags:
                self.num_nodes += 1
        except:
            pass

    def node(self, n):
        self.count_walkway(n.tags)

    def way(self, w):
        self.count_walkway(w.tags)

    def relation(self, r):
        self.count_walkway(r.tags)

wkb_factory = osmium.geom.WKBFactory()
dzielnia = "map.osm"

def get_bounds(osm_xml_file):
    for line in open(osm_xml_file):
        if "<bounds" in line:
            loaded_xml = xml.etree.ElementTree.fromstring(line)
            return loaded_xml.get("minlat"), loaded_xml.get("minlon"), loaded_xml.get("maxlat"), loaded_xml.get("maxlon")

class WayListHandler(osmium.SimpleHandler):
    def __init__(self, osm_file):
        osmium.SimpleHandler.__init__(self)
        self.osm_file = osm_file
        minlat, minlon, maxlat, maxlon = get_bounds(osm_file)
        self.way_list = []
    
    def draw_walkways(self, way_list):
        walkway_map = pyplot.figure()
        subplot = walkway_map.add_subplot(111)
        for e in way_list[:2]:
            subplot.plot(list(e.xy[0]), list(e.xy[1]))
            print(list(zip(list(e.xy[0]), list(e.xy[1]))))
        pyplot.show()

    def way(self, w):
        walkable_tags = ["footway", "bridleway", "steps", "path, living_street", "pedestrian",
                        "residential", "crossing"]
        try:
            if w.tags['highway'] in walkable_tags:
                linestring = wkb_factory.create_linestring(w)
                line = wkblib.loads(linestring, hex=True)
                self.way_list.append(line)
        except:
            pass
        
if __name__ == '__main__':
    # print(get_bounds(dzielnia))
    h = WayListHandler(dzielnia)
    h.apply_file(dzielnia, locations=True)
    print("Zeroth element: ", type(h.way_list[0]))
    h.draw_walkways(h.way_list)

# if __name__ == '__main__':

#     h = WalkwayCounterHandler()

#     h.apply_file("map.osm", locations=True, idx='sparse_mem_array')

#     print("Number of nodes: %d" % h.num_nodes)
