#a Imports
import math
from gjslib.math import matrix, vectors, statistics

#a c_image_projection
class c_image_projection(object):
    camera_deltas = [{"camera":(-0.1,0.0,0.0),"up":(0.0,0.0,0.0)},
                     {"camera":(+0.1,0.0,0.0),"up":(0.0,0.0,0.0)},
                     {"camera":(0.0,-0.1,0.0),"up":(0.0,0.0,0.0)},
                     {"camera":(0.0,+0.1,0.0),"up":(0.0,0.0,0.0)},
                     {"camera":(0.0,0.0,-0.1),"up":(0.0,0.0,0.0)},
                     {"camera":(0.0,0.0,+0.1),"up":(0.0,0.0,0.0)},
                     {}]
    target_deltas = [{"target":(-0.1,0.0,0.0)},
                     {"target":(+0.1,0.0,0.0)},
                     #{"target":(0.0,-0.1,0.0)},
                     #{"target":(0.0,+0.1,0.0)},
                     {"target":(0.0,0.0,-0.1)},
                     {"target":(0.0,0.0,+0.1)},
                     {}]
    up_deltas = [ {"up":(-0.01,0.0,0.0)},
                  {"up":(+0.01,0.0,0.0)},
                  {"up":(0.0,-0.01,0.0)},
                  {"up":(0.0,+0.01,0.0)},
                  {"up":(0.0,0.0,-0.01)},
                  {"up":(0.0,0.0,+0.01)},
                  {}]
    scale_deltas = [ {"scale_update":(0.999,1.001,0.5)} ]
    #f __init__
    def __init__(self,name,image_filename,size=(1.0,1.0)):
        self.name = name
        self.image_filename = image_filename
        self.mvp = None
        self.ip = None
        self.size = size
        pass
    #f set_projection
    def set_projection(self, projection=None, deltas=None, camera=(0.0,0.0,0.0), target=(0.0,0.0,0.0), up=(0.0,0.0,1.0), xscale=1.0, yscale=1.0, delta_scale=1.0, resultant_projection=None ):
        if projection is not None:
            camera = projection["camera"]
            target = projection["target"]
            up     = projection["up"]
            xscale = projection["xscale"]
            yscale = projection["yscale"]
            pass
        if deltas is not None:
            if "camera" in deltas: camera = vectors.vector_add(camera, deltas["camera"], scale=delta_scale)
            if "target" in deltas: target = vectors.vector_add(target, deltas["target"], scale=delta_scale)
            if "up" in deltas:     up     = vectors.vector_add(up,     deltas["up"],     scale=delta_scale)
            if "xscale" in deltas: xscale = xscale * deltas["xscale"]
            if "yscale" in deltas: yscale = yscale * deltas["yscale"]
            pass
        up = vectors.vector_normalize(up)
        self.mvp = matrix.c_matrix4x4( r0=(xscale,0.0,0.0,0.0),
                                       r1=(0.0,yscale,0.0,0.0),
                                       r2=(0.0,0.0,1.0,0.0),
                                       r3=(0.0,0.0,-1.0,0.0),)
        m = matrix.c_matrix3x3()
        self.camera = camera[:]
        self.target = target[:]
        self.scales = (xscale,yscale)
        self.projection = { "camera":camera[:],
                            "target":target[:],
                            "up":    up[:],
                            "xscale":xscale,
                            "yscale":yscale}
        m.lookat( camera, target, up )
        if deltas is not None:
            if "up" in deltas:
                up = (m.matrix[3], m.matrix[4], m.matrix[5])
                pass
            pass
        #print m
        self.mvp.mult3x3(m=m)
        self.mvp.translate(camera, scale=-1)
        #print self.mvp
        self.ip = self.mvp.projection()
        self.ip.invert()
        if resultant_projection is not None:
            resultant_projection["camera"] = camera[:]
            resultant_projection["target"] = target[:]
            resultant_projection["up"]     = up[:]
            resultant_projection["xscale"] = xscale
            resultant_projection["yscale"] = yscale
            pass
        pass
    #f image_of_model
    def image_of_model(self,xyz):
        xy = self.mvp.apply(xyz,perspective=True)
        img_xy = ((1.0+xy[0])/2.0*self.size[0], (1.0-xy[1])/2.0*self.size[1])
        return (xy,img_xy)
    #f model_line_for_image
    def model_line_for_image(self,xy):
        dirn = [xy[0],xy[1],-1]
        dirn = self.ip.apply(dirn)
        return (self.camera, dirn)
    #f mapping_error
    def mapping_error(self, name, xyz, xy, corr=None, epsilon=1E-6, verbose=False ):
        abs_error = 0
        (img_uvzw, img_xy) = self.image_of_model(xyz)
        error = ( (xy[0]-img_uvzw[0])*(xy[0]-img_uvzw[0]) +
                  (xy[1]-img_uvzw[1])*(xy[1]-img_uvzw[1]))
        abs_error += error
        (xscale,yscale) = (10000.0, 10000.0)
        if img_uvzw[0]<-epsilon or img_uvzw[0]>epsilon:
            xscale = xy[0] / img_uvzw[0] * self.scales[0]
            pass
        if img_uvzw[1]<-epsilon or img_uvzw[1]>epsilon:
            yscale = xy[1] / img_uvzw[1] * self.scales[1]
            pass
        if corr is not None:
            corr[0].add_entry(xy[0], img_uvzw[0])
            corr[1].add_entry(xy[1], img_uvzw[1])
            corr[2] *= xscale
            corr[3] *= yscale
            pass
        if verbose:
            print "%16s"%name, error, xscale,yscale, "xy %s:%s"%(str(xy), str(img_uvzw[0:2]))
            pass
        return abs_error
    #f optimize_projection
    def optimize_projection(self,
                            point_mappings,
                             use_references = False,
                             scale_iterations=100,
                             target_iterations=100,
                             camera_iterations=1000,
                             delta_scale=0.05,
                             verbose=False):

        base_projection = self.projection
        for k in range(scale_iterations):
            (xsc,ysc)=(1.0,1.0)
            for j in range(target_iterations):
                done = False
                for i in range(camera_iterations):
                    (d,p) = self.guess_better_projection(point_mappings, base_projection, use_references, self.camera_deltas, delta_scale=delta_scale, scale_error_weight=0.1, verbose=verbose)
                    if len(d)==0:
                        print "Iteration",j,i
                        done = True
                        break
                    base_projection = p
                    pass
                (d,p) = self.guess_better_projection(point_mappings, base_projection, use_references, self.target_deltas, delta_scale=delta_scale/20.0, verbose=verbose)
                base_projection = p
                if len(d)!=0: done=False
                (d,p) = self.guess_better_projection(point_mappings, base_projection, use_references, self.up_deltas, delta_scale=delta_scale/100.0, verbose=verbose)
                base_projection = p
                if len(d)!=0: done=False
                if done:
                    break
                pass
            if done:
                #(d,p) = self.guess_better_projection(point_mappings, base_projection, use_references, self.scale_deltas, verbose=verbose)
                #base_projection = p
                #if len(d)!=0: done=False
                pass
            if done:
                break
            pass
        (d,p) = self.guess_better_projection(point_mappings, base_projection, use_references, verbose=verbose)
        self.set_projection(base_projection)
        return base_projection
    #f guess_better_projection
    def guess_better_projection(self, point_mappings, base_projection, use_references=True, deltas_list=[{}], delta_scale=1.0, scale_error_weight=0.1, verbose=False):
        smallest_error = ({},10000,base_projection,1.0,1.0)
        for deltas in deltas_list:
            r = {}
            self.set_projection( projection=base_projection, deltas=deltas, delta_scale=0.25, resultant_projection=r )
            if verbose:
                print "\ngbp :", deltas, delta_scale, r
                pass
            e = 0
            corr = [statistics.c_correlation(), statistics.c_correlation(),1.0,1.0]
            corr[0].add_entry(0.0,0.0)
            corr[1].add_entry(0.0,0.0)
            pts = 0
            for n in point_mappings.get_mapping_names():
                xyz = point_mappings.get_xyz( n, use_references )
                mapping_xy = point_mappings.get_xy(n,self.name)
                if (xyz is not None) and (mapping_xy is not None):
                    e += self.mapping_error(n,xyz,mapping_xy,corr,verbose=verbose)
                    pts += 1
                    pass
                pass
            if pts>0:
                full_e = e
                full_e += scale_error_weight*(1-corr[0].correlation_coefficient())
                full_e += scale_error_weight*(1-corr[1].correlation_coefficient())
                (xscale, yscale) = (1.0,1.0)
                if corr[2]>0 and corr[3]>0:
                    xscale = math.pow(corr[2],1.0/pts)
                    yscale = math.pow(corr[3],1.0/pts)
                    pass
                print "Total error",full_e,e,1-corr[0].correlation_coefficient(), 1-corr[1].correlation_coefficient(),xscale,yscale
                if full_e<smallest_error[1]:
                    smallest_error = (deltas,full_e,r,xscale/r["xscale"],yscale/r["yscale"])
                    pass
                pass
            pass
        if "scale_update" in smallest_error[0]:
            (scale_low, scale_high, scale_update_power) = deltas["scale_update"]
            (r,xsc,ysc) = smallest_error[2:5]
            done = True
            if (xsc<scale_low) or (xsc>scale_high): done = False
            if (ysc<scale_low) or (ysc>scale_high): done = False
            if done:
                smallest_error[0] = {}
                pass
            else:
                r["xscale"] *= math.pow(xsc,scale_update_power)
                r["yscale"] *= math.pow(ysc,scale_update_power)
                pass
            pass

        if verbose:
            print "Smallest error",smallest_error
            print
            pass
        return (smallest_error[0], smallest_error[2])
    #f All done
    pass
