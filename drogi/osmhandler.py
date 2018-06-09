import osmium
import shapely.wkb as wkblib
import xml.etree.ElementTree

WALKABLE_TAGS = ["footway", "bridleway", "steps", "path, living_street", "pedestrian",
                 "residential", "crossing"]
WALKABLE_TAGS_FLAT = ["footway", "bridleway", "living_street", "pedestrian",
                      "residential"]
WKB_FACTORY = osmium.geom.WKBFactory()
mapka = "map.osm"

class WalkwayContainer:
    def __init__(self, way, category):
        self.way = way
        self.category = category
        self.line = wkblib.loads(WKB_FACTORY.create_linestring(way), hex=True)

class OSMHandler(osmium.SimpleHandler):
    """Handler for .osm files"""
    def __init__(self, osm_file):
        osmium.SimpleHandler.__init__(self)
        self.osm_file = osm_file
        self.minlat, self.minlon, self.maxlat, self.maxlon = [float(e) for e in self.get_bounds(osm_file)]
        self.way_list = []

    def get_bounds(self, osm_file):
        for line in open(osm_file):
            if "<bounds" in line:
                loaded_xml = xml.etree.ElementTree.fromstring(line)
                return loaded_xml.get("minlat"), loaded_xml.get("minlon"), loaded_xml.get("maxlat"), loaded_xml.get("maxlon")
    
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