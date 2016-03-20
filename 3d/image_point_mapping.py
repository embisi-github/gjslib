#a Imports
from gjslib.math.line_sets import c_set_of_lines
from gjslib.math.quaternion import c_quaternion
import image_projection

#a c_point_mapping
class c_point_mapping(object):
    #f __init__
    def __init__(self, images_dir=""):
        self.reset()
        self.images_dir = images_dir
        self.object_guess_locations = {}
        self.object_guess_locations["clk.center"] = (  0.0, -0.32,  8.4)
        self.object_guess_locations["lspike.t"]   = ( -3.3,  0.0, 10.9)
        self.object_guess_locations["rspike.t"]   = (  3.3,  0.0, 10.9)
        self.object_guess_locations["cp"]         = (  0.0,  -2.0, 4.2)
        #self.object_guess_locations["cp"]         = (  0.0,  -1.5, 3.8)

        self.object_guess_locations["calc.t.bl"]   = ( 10.2, 18.993, 2.01)
        self.object_guess_locations["calc.b.fr"]   = ( 24.0,  0.00, 0.01)
        self.object_guess_locations["clips.b.fr"]  = ( 0.0,   0.05, 0.02)
        self.object_guess_locations["clips.t.fr"]  = ( 0.02,   0.08, 7.60)

        self.object_guess_locations["clips.b.fr"]  = ( 0.0,   0.05, 0.1)
        self.object_guess_locations["clips.t.fr"]  = ( 0.02,   0.08, 8.00)
        # 8.10 has error 0.0011090
        # 8.01 has error 0.0001089
        # 8.00 has error 0.0001028
        # 7.95 has error 0.0001499
        # 7.90 has error 0.0002159
        # 7.80 has error 0.0003883
        # 7.70 has error 0.0006423
        # 7.60 has error 0.0009146
        self.object_guess_locations["clips.t.fr"]  = ( -0.01,   0.08, 8.00)
        # x=0.02 has error 0.0001028
        # x=0.00 has error 0.00009813
        # x=-0.01 has error 0.00009819
        self.object_guess_locations["clips.t.fr"]  = ( 0.00,   0.11, 8.00)
        # y=0.08 has error 0.00009813
        # y=0.09 has error 0.00009220
        # y=0.10 has error 0.00008804
        # y=0.11 has error 0.00008661
        # y=0.13 has error 0.00009180
        # window is 0.656 of a tile
        # top of window is 1.33 tiles above ground
        self.object_guess_locations["flsq1.0"]   = ( 0.0, 0.0, 0.0)
        #self.object_guess_locations["flsq3.3"]   = ( 0.0, -3.0, 0.0)
        self.object_guess_locations["flsq4.2"]   = ( 3.0, -3.0, 0.0)
        self.object_guess_locations["flsq5.3"]   = ( 0.0, -5.0, 0.0)
        #self.object_guess_locations["flsq2.0"]   = ( 2.0, 0.0, 0.0)
        #self.object_guess_locations["drsq1.1"]   = ( 0.15, 1.5, 1.33)
        #self.object_guess_locations["drsq1.1"]   = ( 0.15, 1.5, 1.30)
        #self.object_guess_locations["drsq1.1"]   = ( 0.15, 1.5, 1.31)
        #self.object_guess_locations["drsq1.1"]   = ( 0.13, 1.5, 1.31)
        #self.object_guess_locations["drsq1.1"]   = ( 0.13, 1.51, 1.31)
        self.object_guess_locations["drsq3.0"]   = ( 0.13, 1.51, 3.50)
        self.object_guess_locations["drsq3.0"]   = ( 0.13, 1.51, 3.45)
        self.object_guess_locations["drsq3.0"]   = ( 0.13, 1.50, 3.515)
        self.object_guess_locations["drsq3.0"]   = ( 0.13, 1.50, 3.48)
        pass
    #f reset
    def reset(self):
        self.image_mappings = {}
        self.descriptions = {}
        self.reference_positions = {}
        self.positions = {}
        self.images = {}
        self.images_for_point_resoluion = []
        pass
    #f get_images
    def get_images(self):
        return self.images.keys()
    #f get_image_data
    def get_image_data(self, image_name):
        return self.images[image_name]
    #f load_data_add_image
    def load_data_add_image(self, data):
        image_name = data[0]
        image_filename = self.images_dir+data[1]
        image_size = (int(data[2])+0.0,int(data[3])+0.0)
        use_for_points = True
        if len(data)<5 or not int(data[4]):
            use_for_points = False
            pass
        self.add_image(image=data[0], filename=image_filename, size=image_size, use_for_points=use_for_points)
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
    #f load_data_set_projection
    def load_data_set_projection(self, data):
        image = data[0]
        self.images[image]["projection"].load_projection_strings(data[1:])
        pass
    #f load_data
    def load_data(self, data_filename):
        data_load_callbacks = {}
        data_load_callbacks["Images"] = (self.load_data_add_image,4)
        data_load_callbacks["Points"] = (self.load_data_add_point,2)
        data_load_callbacks["References"] = (self.load_data_add_reference,4)
        data_load_callbacks["Projections"] = (self.load_data_set_projection,9)
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
                if l[2:-1] in data_load_callbacks:
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

        return
    #f save_data
    def save_data(self, data_filename):
        f = open(data_filename,"w")

        point_names = self.image_mappings.keys()
        point_names.sort()

        image_names = self.images.keys()
        image_names.sort()

        print >>f, "--Images:"
        for name in image_names:
            image = self.images[name]
            print >>f,"%s,%s,%d,%d,%d"%(name,image["filename"],image["size"][0],image["size"][1],image["use_for_points"])
            pass
        print >>f, "\n"

        print >>f, "--Projections:"
        for name in image_names:
            if "projection" not in self.images[name]:
                continue
            proj = self.images[name]["projection"]
            if proj is None:
                continue
            text = proj.save_projection_string()
            if text is None:
                continue
            print >>f, "%s,%s"%(name,text)
            pass
        print >>f, "\n"

        print >>f, "--Points:"
        for name in point_names:
            desc = ""
            if name in self.descriptions:
                desc = self.descriptions[name]
            print >>f, "%s,%s"%(name,desc)
            pass
        print >>f, "\n"

        print >>f, "--References:"
        print >>f, "\n"

        print >>f, "--Mapping:"
        for name in point_names:
            for image in image_names:
                if image in self.image_mappings[name]:
                    xy = self.image_mappings[name][image]
                    print >>f, "%s,%s,%f,%f"%(image,name,xy[0],xy[1])
                    pass
                pass
            pass
        print >>f, "\n"
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
    def add_image(self,image, filename=None, size=(1.0,1.0), use_for_points=True):
        if image not in self.images:
            projection = image_projection.c_image_projection(name=image,
                                                             image_filename=filename,
                                                             size=size)
            self.images[image] = {}
            self.images[image]["filename"] = filename
            self.images[image]["projection"] = projection
            self.images[image]["size"] = size
            self.images[image]["use_for_points"] = use_for_points
            if use_for_points:
                self.images_for_point_resoluion.append(image)
                pass
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
        undo_op = (name,image,None)
        if image in self.image_mappings[name]:
            old_xy = self.image_mappings[name][image]
            undo_op = (name,image,(old_xy[0],old_xy[1]))
            pass
        self.image_mappings[name][image] = xy
        return undo_op
    #f delete_image_location
    def delete_image_location(self,name,image,verbose=False):
        if image not in self.image_mappings[name]:
            if verbose:
                print "Requested deleting point %s that is not in image %s"%(name,image)
                pass
            return None
        if verbose:
            print "Deleting point %s in image %s"%(name,image)
            pass
        undo_op = (name,image,self.image_mappings[name][image])
        del(self.image_mappings[name][image])
        return undo_op
    #f undo_add_image_location
    def undo_add_image_location(self, undo_op, verbose=False):
        (name, image, xy) = undo_op
        if xy is None:
            self.delete_image_location(name,image,verbose=verbose)
            pass
        else:
            self.add_image_location(name,image,xy,verbose=verbose)
            pass
        pass
    #f undo_delete_image_location
    def undo_delete_image_location(self, undo_op, verbose=False):
        if undo_op is None:
            return
        (name, image, xy) = undo_op
        self.add_image_location(name,image,xy,verbose=verbose)
        pass
    #f set_projection
    def set_projection(self, image, projection):
        self.images[image]["projection"].set_projection(projection)
        pass
    #f get_projection
    def get_projection(self, image):
        return self.images[image]["projection"].get_projection()
    #f use_for_points
    def use_for_points(self, image, value=None, toggle=None):
        if toggle is not None:
            value = 1 ^ self.images[image]["use_for_points"]
            pass
        if value is not None:
            self.images[image]["use_for_points"] = value
            if value is 0 and image in self.images_for_point_resoluion:
                self.images_for_point_resoluion.remove(image)
                pass
            if value is 1 and image not in self.images_for_point_resoluion:
                self.images_for_point_resoluion.append(image)
                pass
            pass
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
        image_map = self.image_mappings[name]
        if image not in image_map:
            return None
        xy = image_map[image]
        scaled_xy = (-1.0+2.0*xy[0]/(self.images[image]["size"][0]+0.0), 1.0-2.0*xy[1]/(self.images[image]["size"][1]+0.0))
        return scaled_xy
    #f find_line_sets
    def find_line_sets(self):
        line_sets = {}
        for n in self.image_mappings: # for each mapping of a point
            line_sets[n] = c_set_of_lines()
            for img_name in self.images_for_point_resoluion:
                p = self.images[img_name]["projection"]
                if p is None:
                    continue
                xy = self.uniform_mapping(n,img_name)
                if xy is None: 
                    continue
                line = p.model_line_for_image(xy)
                if line is None:
                    continue
                line_sets[n].add_line(line[0],line[1])
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
        if name not in self.positions:
            return None
        return self.positions[name]
    #f get_xyz
    def get_xyz(self, name, use_references=True ):
        if use_references:
            if name in self.object_guess_locations:
                return self.object_guess_locations[name]
            pass
        return self.get_approx_position(name)
    #f initial_orientation
    def initial_orientation(self, image=None, **kwargs):
        for image_name in self.images.keys():
            if (image is not None) and image!=image_name:
                continue
            proj = self.images[image_name]["projection"]
            projection = proj.guess_initial_orientation(point_mappings=self, **kwargs)
            print "self.images['%s']['projection'] = %s"%(image_name,str(projection))
            pass
    #f optimize_projections
    def optimize_projections(self, image=None, **kwargs):
        for image_name in self.images.keys():
            if (image is not None) and image!=image_name:
                continue
            proj = self.images[image_name]["projection"]
            projection = proj.optimize_projection(point_mappings=self, **kwargs)
            print "self.images['%s']['projection'] = %s"%(image_name,str(projection))
            pass
        pass
    #f Done
    pass

