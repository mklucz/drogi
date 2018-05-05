import osmium
import shapely.wkb as wkblib
import xml.etree.ElementTree
from matplotlib import pyplot, image
# from imageio import imwrite
# from numpy import ndarray
import png

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
        self.minlat, self.minlon, self.maxlat, self.maxlon = [float(e) for e in get_bounds(osm_file)]
        self.way_list = []
    
    def draw_walkways(self, way_list):
        walkway_map = pyplot.figure(frameon=False)
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
        pyplot.gca().xaxis.set_major_locator(pyplot.NullLocator())
        pyplot.gca().yaxis.set_major_locator(pyplot.NullLocator())
        pyplot.savefig("savefig_test.png", dpi=300, bbox_inches="tight", pad_inches=0)

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
        
if __name__ == '__main__':
    h = WayListHandler(dzielnia)
    h.apply_file(dzielnia, locations=True)
    h.draw_walkways(h.way_list)

