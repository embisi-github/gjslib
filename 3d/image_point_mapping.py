#a Imports
from gjslib.math.line_sets import c_set_of_lines

#a c_point_mapping
class c_point_mapping(object):
    #f __init__
    def __init__(self):
        self.mappings = {}
        self.positions = {}
        self.images = {}
        pass
    #f load_data
    def load_data(self):
        pass
    #f add_named_point
    def add_named_point(self,name):
        if name not in self.mappings:
            self.mappings[name] = {}
            pass
        pass
    #f add_image
    def add_image(self,image):
        if image not in self.images:
            self.images[image] = {}
            self.images[image]["projection"] = None
            pass
        pass
    #f add_image_location
    def add_image_location(self,name,image,xy):
        self.mappings[name][image] = xy
        pass
    #f set_projection
    def set_projection(self,image,projection):
        self.images[image]["projection"] = projection
        pass
    #f get_xy
    def get_xy(self, name, image ):
        if name not in self.mappings:
            return None
        if image not in self.mappings[name]:
            return None
        return self.mappings[name][image]
    #f find_line_sets
    def find_line_sets(self):
        line_sets = {}
        for n in self.mappings:
            m = self.mappings[n]
            line_sets[n] = c_set_of_lines()
            for img_name in m:
                p = self.images[img_name]["projection"]
                if p is not None:
                    xy = m[img_name]
                    line = p.model_line_for_image(xy)
                    line_sets[n].add_line(line[0],line[1])
                    pass
                pass
            line_sets[n].generate_meeting_points()
            #print n, line_sets[n].line_meetings
            pass
        self.line_sets = line_sets
        pass
    #f approximate_positions
    def approximate_positions(self):
        for n in self.line_sets:
            self.positions[n] = self.line_sets[n].posn
            pass
        pass
    #f Done
    pass

