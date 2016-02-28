#a Imports
from gjslib.math.line_sets import c_set_of_lines

#a c_point_mapping
class c_point_mapping(object):
    #f __init__
    def __init__(self):
        self.reset()
        pass
    #f reset
    def reset(self):
        self.image_mappings = {}
        self.descriptions = {}
        self.reference_positions = {}
        self.positions = {}
        self.images = {}
        pass
    #f get_images
    def get_images(self):
        return self.images.keys()
    #f get_image
    def get_image(self, image_name):
        return self.images[image_name]
    #f load_data_add_image
    def load_data_add_image(self, data):
        image_name = data[0]
        image_filename = data[1]
        image_size = (int(data[2])+0.0,int(data[3])+0.0)
        self.add_image(image=data[0], filename=image_filename, size=image_size)
        pass
    #f load_data_add_point
    def load_data_add_point(self, data):
        self.add_named_point(data[0],data[1])
        pass
    #f load_data_add_reference
    def load_data_add_reference(self, data):
        self.add_named_point(data[0])
        pass
    #f load_data_add_mapping
    def load_data_add_mapping(self, data):
        image = data[0]
        point = data[1]
        xy = (float(data[2]),float(data[3]))
        self.add_named_point(data[1])
        self.add_image_location(point, image, xy)
        pass
    #f load_data
    def load_data(self, data_filename):
        data_load_callbacks = {}
        data_load_callbacks["Images"] = (self.load_data_add_image,4)
        data_load_callbacks["Points"] = (self.load_data_add_point,2)
        data_load_callbacks["References"] = (self.load_data_add_reference,4)
        data_load_callbacks["Mapping"] = (self.load_data_add_mapping,4)
        f = open(data_filename,"r")
        if not f:
            raise Exception("Failed to read point mapping file '%s'"%data_filename)
        data_stage = "Images"
        for l in f:
            l = l.strip()
            if len(l)==0: continue
            if l[0]=='#': continue
            if l[1]=='-':
                if l[2:-1] in ["Images", "Points", "References", "Mapping"]:
                    data_stage = l[2:-1]
                    pass
                else:
                    raise Exception("Bad separator '%s' in mapping file"%l)
                continue
            data = l.split(',')
            for i in range(len(data)):
                data[i] = data[i].strip()
                pass
            (cb,min_args) = data_load_callbacks[data_stage]
            if len(data)<min_args:
                raise Exception("Needed more arguments (at least %d) in line '%s' of mapping file for '%s'"%(min_args,l,data_stage))
            cb(data)
            pass
        f.close()
        pass
    #f add_named_point
    def add_named_point(self,name,description=None):
        if name not in self.image_mappings:
            self.image_mappings[name] = {}
            pass
        if description is not None:
            self.descriptions[name]=description
            pass
        pass
    #f add_image
    def add_image(self,image, filename=None, size=(1.0,1.0), projection=None):
        if image not in self.images:
            self.images[image] = {}
            self.images[image]["filename"] = filename
            self.images[image]["projection"] = projection
            self.images[image]["size"] = size
            pass
        pass
    #f add_image_location
    def add_image_location(self,name,image,xy,uniform=False,verbose=False):
        if uniform:
            if uniform: xy = ((xy[0]+1.0)/2.0, (1.0-xy[1])/2.0)
            size = self.images[image]["size"]
            xy = (xy[0]*size[0],xy[1]*size[1])
            pass
        if verbose:
            v = "Setting point %s in image %s to %s"
            if image in self.image_mappings[name]:
                v = "Moving point %s in image %s to %s"
                pass
            print v%(name,image,str(xy))
            pass
        self.image_mappings[name][image] = xy
        pass
    #f set_projection
    def set_projection(self,image,projection):
        self.images[image]["projection"] = projection
        pass
    #f get_mapping_names
    def get_mapping_names(self):
        return self.image_mappings.keys()
    #f get_xy
    def get_xy(self, name, image ):
        if name not in self.image_mappings:
            return None
        if image not in self.image_mappings[name]:
            return None
        return self.uniform_mapping(name,image)
    #f uniform_mapping
    def uniform_mapping(self, name, image):                                
        xy = self.image_mappings[name][image]
        scaled_xy = (-1.0+2.0*xy[0]/(self.images[image]["size"][0]+0.0), 1.0-2.0*xy[1]/(self.images[image]["size"][1]+0.0))
        return scaled_xy
    #f find_line_sets
    def find_line_sets(self):
        line_sets = {}
        for n in self.image_mappings:
            line_sets[n] = c_set_of_lines()
            for img_name in self.image_mappings[n].keys():
                p = self.images[img_name]["projection"]
                if p is not None:
                    xy = self.uniform_mapping(n,img_name)
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
    #f get_approx_position
    def get_approx_position(self, name ):
        return self.positions[name]
    #f Done
    pass

