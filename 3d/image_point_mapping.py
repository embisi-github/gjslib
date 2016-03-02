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
    #f get_image_data
    def get_image_data(self, image_name):
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
        self.images['main']['projection'] = {'xscale': 1.0, 'camera': [6.550000000000024, -13.525000000000007, 18.895000000000003], 'yscale': 1.5, 'target': [9.150000000000048, 0.0, 4.875000000000011], 'up': [-0.33350891961340084, -0.0828258108440976, 0.9391015310371504]}
        self.images['img_1']['projection'] = {'xscale': 1.0, 'camera': [6.374999999999991, -6.975000000000014, 11.72500000000007], 'yscale': 1.3, 'target': [-2.399999999999995, 0.0, 5.374999999999998], 'up': [0.03234892372532482, 0.3206458702150309, 0.9466465935331194]}
        self.images['main']['projection'] = {'xscale': 1.0, 'camera': [4.399999999999993, -15.425000000000034, 19.794999999999952], 'yscale': 1.5, 'target': [9.650000000000055, 0.0, 5.400000000000018], 'up': [-0.3950709969815411, -0.33635069378035787, 0.8548608764807776]}
        self.images['img_1']['projection'] = {'xscale': 1.0, 'camera': [5.499999999999979, -7.350000000000019, 12.725000000000085], 'yscale': 1.3, 'target': [-3.3499999999999917, 0.0, 3.9499999999999793], 'up': [-0.017569450567893528, 0.3400796697024401, 0.9402324886227988]}
        self.images['main']['projection'] = {'xscale': 1.0, 'camera': [6.550000000000024, -13.525000000000007, 18.895000000000003], 'yscale': 1.5, 'target': [9.150000000000048, 0.0, 4.875000000000011], 'up': [-0.33350891961340084, -0.0828258108440976, 0.9391015310371504]}
        self.images['img_1']['projection'] = {'xscale': 1.0, 'camera': [6.374999999999991, -6.975000000000014, 11.72500000000007], 'yscale': 1.3, 'target': [-2.399999999999995, 0.0, 5.374999999999998], 'up': [0.03234892372532482, 0.3206458702150309, 0.9466465935331194]}

        self.images["main"]["projection"]  = {"camera":(-6.0,-12.0,2.0), "target":(5.0,0.0,4.0), "up":(0.0,0.0,1.0), "xscale":1.0, "yscale":1.5}
        self.images["img_1"]["projection"] = {"camera":(+7.0,-6.0,6.7), "target":(-1.0,0.0,5.5), "up":(0.0,0.0,1.0), "xscale":1.0, "yscale":1.3}
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
        if name not in self.positions:
            return None
        return self.positions[name]
    #f get_xyz
    def get_xyz(self, name, use_references=False ):
        object_guess_locations = {}
        object_guess_locations["clk.center"] = (  0.0, -0.25,  8.4)
        object_guess_locations["lspike.t"]   = ( -3.0,  0.0, 10.9)
        object_guess_locations["rspike.t"]   = (  3.0,  0.0, 10.9)
        if use_references:
            return None
        if name in object_guess_locations:
            return object_guess_locations[name]
        return self.get_approx_position(name)
    #f optimize_projections
    def optimize_projections(self,
                             image=None,
                             use_references = False,
                             scale_iterations=100,
                             target_iterations=100,
                             camera_iterations=1000,
                             delta_scale=0.05,
                             verbose=False):
        for image_name in self.images.keys():
            if (image is not None) and image!=image_name:
                continue
            proj = self.images[image_name]["projection"]
            base_projection = proj.projection
            for k in range(scale_iterations):
                (xsc,ysc)=(1.0,1.0)
                for j in range(target_iterations):
                    done = False
                    for i in range(camera_iterations):
                        (d,p) = proj.guess_better_projection(self, base_projection, use_references, proj.camera_deltas, delta_scale=delta_scale, scale_error_weight=0.1, verbose=verbose)
                        if len(d)==0:
                            print "Iteration",j,i
                            done = True
                            break
                        base_projection = p
                        pass
                    (d,p) = proj.guess_better_projection(self, base_projection, use_references, proj.target_deltas, delta_scale=delta_scale/20.0, verbose=verbose)
                    base_projection = p
                    if len(d)!=0: done=False
                    (d,p) = proj.guess_better_projection(self, base_projection, use_references, proj.up_deltas, delta_scale=delta_scale/100.0, verbose=verbose)
                    base_projection = p
                    if len(d)!=0: done=False
                    if done:
                        break
                    pass
                if done:
                    #(d,p) = proj.guess_better_projection(self, base_projection, use_references, proj.scale_deltas, verbose=verbose)
                    #base_projection = p
                    #if len(d)!=0: done=False
                    pass
                if done:
                    break
                pass
            (d,p) = proj.guess_better_projection(self, base_projection, use_references, verbose=verbose)
            proj.set_projection(base_projection)
            print "self.images['%s']['projection'] = %s"%(image_name,str(base_projection))
            pass
        pass
    #f Done
    pass

