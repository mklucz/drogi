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
class WalkwayContainer:
    def __init__(self, way, category):
        self.way = way
        self.category = category
        self.line = wkblib.loads(wkb_factory.create_linestring(way), hex=True)

class WayListHandler(osmium.SimpleHandler):
    def __init__(self, osm_file):
        osmium.SimpleHandler.__init__(self)
        self.osm_file = osm_file
        minlat, minlon, maxlat, maxlon = get_bounds(osm_file)
        self.way_list = []
    
    def draw_walkways(self, way_list):
        walkway_map = pyplot.figure()
        subplot = walkway_map.add_subplot(111)
        for e in way_list:
            if e.category == "walkway":
                subplot.plot(list(e.line.xy[0]), list(e.line.xy[1]), color="blue")
            elif e.category == "crossing":
                subplot.plot(list(e.line.xy[0]), list(e.line.xy[1]), color="red")
            elif e.category == "steps":
                subplot.plot(list(e.line.xy[0]), list(e.line.xy[1]), color="green")

        pyplot.show()

    def way(self, w):
        walkable_tags = ["footway", "bridleway", "living_street", "pedestrian",
                        "residential"]
        try:
            tag = w.tags["highway"]
            if tag in walkable_tags:
                self.way_list.append(WalkwayContainer(w, "walkway"))
            if tag == "crossing":
                self.way_list.append(WalkwayContainer(w, "crossing"))
                # linestring = wkb_factory.create_linestring(w)
                # line = wkblib.loads(linestring, hex=True)
                # self.way_list.append({"line":line, "category":"crossing"})                
            if tag == "steps":
                self.way_list.append(WalkwayContainer(w, "steps"))
                # linestring = wkb_factory.create_linestring(w)
                # line = wkblib.loads(linestring, hex=True)
                # self.way_list.append({"line":line, "category":"steps"})
        except:
            pass
        
if __name__ == '__main__':
    h = WayListHandler(dzielnia)
    h.apply_file(dzielnia, locations=True)
    h.draw_walkways(h.way_list)
