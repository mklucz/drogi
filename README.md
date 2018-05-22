# drogi

## What is this thing?

What I'm aiming to accomplish here is building a tool that'll allow for a quick and straightforward way to tell how a given area's walkability could be improved. In other words: given a map of walkways, where does one add a connection or a set of connections for the greatest improvement in average travel times. Or, still in other words, where to build a sidewalk to get the most bang for your buck.

All in the spirit of new urbanism and reducing car dependancy, concepts about which you can read in other places on the web, should you feel so inclined.

## How is it supposed to work?

#### Getting the data

Thankfully this part is pretty straightforward. At https://download.geofabrik.de/ we can get OpenStreetMap .osm data as convenient, city-sized extracts. But for the purposes of this readme we won't, at least not yet. Instead I grabbed an extract of my neighbourhood, it's smaller and in a sense means I get more intimate domain knowledge of what I'm looking at.

The file contatining the extract is the map.osm and we're processing it using WayListHandler class. The following calls...

```python
h = WayListHandler("map.osm")
h.apply_file("map.osm", locations=True)
h.draw_walkways(h.way_list)
```
...will result in the following picture being created:

![extracted walkways](rendered_walkways.png)

