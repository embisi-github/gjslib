#a Imports
from gjslib.math.line_sets import c_set_of_lines
from gjslib.math.quaternion import c_quaternion
import image_projection

#a c_point_mapping
class c_point_mapping(object):
    #f __init__
    def __init__(self):
        self.reset()
        self.object_guess_locations = {}
        #self.object_guess_locations["clk.center"] = (  0.0, -0.32,  8.4)
        #self.object_guess_locations["lspike.t"]   = ( -3.3,  0.0, 10.9)
        #self.object_guess_locations["rspike.t"]   = (  3.3,  0.0, 10.9)

        self.object_guess_locations["calc.t.bl"]   = ( 10.2, 19.0, 2.0)
        self.object_guess_locations["calc.b.fr"]   = ( 24.0,  0.0, 0.0)
        self.object_guess_locations["clips.b.fr"]  = ( 0.0,   0.0, 0.0)
        # for fov of 55
        # 7.0  had error 176 after 6 iterations for left, 330 for middle
        # 7.5  had error 97  after 6 iterations for left, 199 for miaddle
        # 8.0  had error 51  after 6 iterations for left, 97 for middle
        # 8.25 had error 56  after 6 iterations for left, 78 for middle
        # 8.5  had error 65  after 60 iterations for left, 102 for middle

        # 8.25 FOV 55 had error 56  after 6 iterations for left, 78 for middle
        # 8.25 FOV 53 had error 86  after 6 iterations for left, 83 for middle
        # 8.00 FOV 53 had error 97  after 6 iterations for left, 83 for middle
        # 8.00 FOV 56 had error 53.4 after 6 iterations for left, 83 for middle
        # 8.25 FOV 56 had error 53.9 after 6 iterations for left, 110 for middle
        # 8.25 FOV 55 had error 50  after 30 iterations for left, 100 for middle
        self.object_guess_locations["clips.t.fr"]  = ( 0.0,   0.0, 8.25)

        # Rearranged the points a bit
        # 8.00 FOV 55 error 26 after 10 iterations for left, 81 for middle
        self.object_guess_locations["clips.t.fr"]  = ( 0.0,   0.0, 8.00)
        # 7.8 yields 19.8 error on full optimization
        self.object_guess_locations["clips.t.fr"]  = ( 0.0,   0.0, 7.80)
        # 7.7 yields 13.4 error on full optimization
        self.object_guess_locations["clips.t.fr"]  = ( 0.0,   0.0, 7.70)
        # 7.6 yields 9.3 error on full optimization
        self.object_guess_locations["clips.t.fr"]  = ( 0.0,   0.0, 7.60)
        # 7.5 yields 11.3 error on full optimization
        self.object_guess_locations["clips.t.fr"]  = ( 0.0,   0.0, 7.50)
        # 7.63 yields 9.93 error on full optimization, 9.76 on reoptimization
        self.object_guess_locations["clips.t.fr"]  = ( 0.0,   0.0, 7.63)

        # Tweaking away... error 2.811 on middle
        self.object_guess_locations["calc.t.bl"]   = ( 10.2, 18.993, 2.01)
        self.object_guess_locations["calc.b.fr"]   = ( 24.0,  0.00, 0.01)
        self.object_guess_locations["clips.b.fr"]  = ( 0.0,   0.05, 0.02)
        self.object_guess_locations["clips.t.fr"]  = ( 0.02,   0.08, 7.60)

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
    #f get_image_data
    def get_image_data(self, image_name):
        return self.images[image_name]
    #f load_data_add_image
    def load_data_add_image(self, data):
        image_name = data[0]
        image_filename = data[1]
        image_size = (int(data[2])+0.0,int(data[3])+0.0)
        self.add_image(image=data[0], filename=image_filename, size=image_size)
        proj = image_projection.c_image_projection(name=image_name,
                                                   image_filename=image_filename,
                                                   size=image_size)
        self.set_projection(image_name, proj)
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
        print data
        image = data[0]
        self.images[image]["projection"].load_projection_strings(data[1:])
        pass
    #f load_data
    def load_data(self, data_filename):
        data_load_callbacks = {}
        data_load_callbacks["Images"] = (self.load_data_add_image,4)
        data_load_callbacks["Points"] = (self.load_data_add_point,2)
        data_load_callbacks["References"] = (self.load_data_add_reference,4)
        data_load_callbacks["Projections"] = (self.load_data_set_projection,10)
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
        # horizontal FOV for 35mm camera: 12.5mm:110 15mm:100 18mm:90 20mm:85 23mm:75 28mm:65 31mm:60 35mm:55 40mm:50 50mm:40 54mm:35 65mm:30 80mm:35 100mm:20
        # yaw is left-right (-ve,+ve)
        # pitch is -ve up
        # roll is clockwise +ve
        # Can now do initial plus optimization (at delta_scale 0.1)
        # This you do with the reference objects
        self.images['img_1']['projection'] = {'fov': 68.33999999999999, 'camera': [5.303600000000904, -8.318100000001156, 9.881700000000029], 'orientation': c_quaternion({'r': 0.7545, 'i': 0.5657, 'j': 0.2373, 'k': 0.2330}), 'aspect': 1.3}
        self.images['main']['projection'] = {'fov': 84.575, 'camera': [-4.695799999997939, -14.592999999998563, 2.773999999999937], 'orientation': c_quaternion({'r': 0.6208, 'i': 0.7191, 'j':-0.2353, 'k':-0.2052}), 'aspect': 1.5}

        # Refine img_1 with delta_scale 0.01 on reference objects
        self.images['img_1']['projection'] = {'fov': 68.33999999999999, 'camera': [5.200500000001144, -8.421200000000916, 9.918599999999943], 'orientation': c_quaternion({'r': 0.7575, 'i': 0.5655, 'j': 0.2342, 'k': 0.2269}), 'aspect': 1.3}
        self.images['main']['projection'] = {'fov': 84.575, 'camera': [-4.29609999999887, -14.992699999997631, 2.773999999999937], 'orientation': c_quaternion({'r': 0.6243, 'i': 0.7206, 'j':-0.2353, 'k':-0.1888}), 'aspect': 1.5}
        # Now change FOV delta - made it bigger, fov does not change (obviously) - so move it down to 0.01
        self.images['main']['projection'] = {'fov': 84.575, 'camera': [-3.9960999999995517, -15.292699999996932, 2.773999999999937], 'orientation': c_quaternion({'r': 0.6278, 'i': 0.7215, 'j':-0.2301, 'k':-0.1802}), 'aspect': 1.5}

        # Now one-then-other optimization
        self.images['main']['projection'] = {'fov': 84.575, 'camera': [-3.7760999999990874, -15.51269999999642, 2.773999999999937], 'orientation': c_quaternion({'r': 0.6305, 'i': 0.7222, 'j':-0.2243, 'k':-0.1751}), 'aspect': 1.5}
        self.images['img_1']['projection'] = {'fov': 68.33999999999999, 'camera': [5.100500000001377, -8.321200000001149, 9.918599999999943], 'orientation': c_quaternion({'r': 0.7589, 'i': 0.5645, 'j': 0.2363, 'k': 0.2225}), 'aspect': 1.3}

        #After moving some points - main is still moving in the same old direction
        self.images['img_1']['projection'] = {'fov': 68.33999999999999, 'camera': [4.993600000001626, -8.472800000000795, 9.90229999999998], 'orientation': c_quaternion({'r': 0.7607, 'i': 0.5670, 'j': 0.2328, 'k': 0.2133}), 'aspect': 1.3}        
        self.images['main']['projection'] = {'fov': 84.575, 'camera': [-3.5760999999986653, -15.712699999995953, 2.773999999999937], 'orientation': c_quaternion({'r': 0.6330, 'i': 0.7226, 'j':-0.2194, 'k':-0.1705}), 'aspect': 1.5}
        pass
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
            print >>f,"%s,%s,%d,%d"%(name,image["filename"],image["size"][0],image["size"][1])
            pass
        print >>f, "\n"

        print >>f, "--Projections:"
        for name in image_names:
            proj = self.images[name]["projection"]
            if proj is not None:
                print >>f, "%s,%s"%(name,proj.save_projection_string())
                pass
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
                ##if img_name not in ["main", "img_1"]: continue
                p = self.images[img_name]["projection"]
                if p is not None:
                    xy = self.uniform_mapping(n,img_name)
                    line = p.model_line_for_image(xy)
                    if line is not None:
                        line_sets[n].add_line(line[0],line[1])
                        pass
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
        if name not in self.positions:
            return None
        return self.positions[name]
    #f get_xyz
    def get_xyz(self, name, use_references=False ):
        # clk.center (  0.0, -0.2,   8.4)  error 7.421E-5
        # clk.center (  0.0, -0.25,  8.4)  error 7.265E-5
        # clk.center (  0.0, -0.30,  8.4)  error 0.8185E-5
        # clk.center (  0.0, -0.32,  8.4)  error 0.1824E-5
        # That was with tower spikes +-3.0
        if use_references:
            return None
        if name in self.object_guess_locations:
            return self.object_guess_locations[name]
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

