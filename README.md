# drogi

## What is this thing?

What I'm aiming to accomplish here is building a tool for analyzing city maps in terms of walkability, driveability, bikeability and so on. Its intended ultimate purpose is generating large amounts of data, as well as creating a simple way to visualize infrastructure trouble spots in a given area.

All in the spirit of new urbanism, urban renaissance, sustainability and reducing car dependency, concepts about which you can read in other places on the web, should you feel so inclined.

## How is it supposed to work?

#### Getting the data

Thankfully this part is pretty straightforward. At [GeoFabrik GmbH's site](https://download.geofabrik.de/) we can get OpenStreetMap .osm data as convenient extracts. But for the purposes of this readme we won't, at least not yet. Instead I manually grabbed an extract of my neighbourhood, it's smaller and in a sense means I get more intimate domain knowledge of what I'm looking at.

#### Processing the data

As I mentioned I intend to use this thing to generate data. For that reason I have decided to design it around a concept of a **WorkRun** which will consist of fetching the data, piece by piece, gluing it together to make a city-sized graph and walking it repeatedly. The patterns that emerge from all the walked paths can then be used to infer deductions.
The WorkRun class is used in the following way:
```python
import drogi
new_run = drogi.WorkRun(osm_file="sample_osm", num_of_trips=10)
```
What's happening inside is the walkable ways from the .osm map get converted into `shapely.LineString` objects and then a graph, represented as a dictionary, is built from those. The representation is pretty standard for Python, the following graph:

![graph example](img/graph.png)

Becomes:
```python
{'A': ['B', 'C'],
 'B': ['A', 'C', 'D'],
 'C': ['A', 'B', 'D', 'E'],
 'D': ['B', 'C'],
 'E': ['C']}
```
Only instead of strings we're using two-tuples of  `(latitude, longitude)`.

#### Finding paths

We then pick two points, randomly for the time being, and using the [networkx](https://github.com/networkx)'s module A\* algorithm find the shortest path between them. It's proved fast enough for the inputs I've been playing with, especially compared to the previous implementation, which was a simple `numpy.ndarray` of ones and zeros, also traversed using A\*.
The paths are saved as `Path` objects and among other things, can be used to render a picture like this:

![rendered paths](img/255_overlaid.png)

To be perfectly honest this is from a previous version and it's using legacy functions that I've since deleted, but it looks pretty so I'm keeping it ;)
