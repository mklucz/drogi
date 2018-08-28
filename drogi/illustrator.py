import matplotlib.pyplot as plt
import png

class Illustrator:
    def __init__(self, way_map, filename_to_save_with):
        self.way_map = way_map
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

    def render_array_as_png(path_array, filename, bitdepth):
        f = open(filename, "wb")
        size = (len(path_array[0]), len(path_array))
        writer = png.Writer(*size, greyscale=True, bitdepth=bitdepth)
        writer.write(f, path_array)
        f.close()

    # def process_png_into_array(map_file, map_colors):
    #     reader_object = png.Reader(map_file)
    #     size_x, size_y, contents_iterator, image_attributes = reader_object.read()
    #     lenght_of_pixel = image_attributes["planes"]
    #     new_list = []
    #     for row in contents_iterator:
    #         new_list.append(list(zip(*[iter(row)] * lenght_of_pixel)))
    #     for sublist in new_list:
    #         for i in range(len(sublist)):
    #             if sublist[i] in map_colors["walkable"]:
    #                 sublist[i] = map_colors["walkable"][sublist[i]]
    #             elif sublist[i] in map_colors["unwalkable"]:
    #                 sublist[i] = 0
    #         sublist = tuple(sublist)
    #     new_list = np.asarray(new_list, dtype="B")
    #     image_attributes["map_colors"] = map_colors
    #     return new_list, image_attributes