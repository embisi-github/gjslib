#a Imports
from gjslib.math import matrix, vectors, statistics

#a c_image_projection
class c_image_projection(object):
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
            if "camera" in deltas: camera = vectors.vector_add(camera,deltas["camera"],scale=delta_scale)
            if "target" in deltas: target = vectors.vector_add(target,deltas["target"],scale=delta_scale)
            if "up" in deltas:     up     = vectors.vector_add(target,deltas["up"],scale=delta_scale)
            if "xscale" in deltas: xscale = xscale * deltas["xscale"]
            if "yscale" in deltas: yscale = yscale * deltas["yscale"]
            pass
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
    def mapping_error(self, name, xy, corr=None, object_guess_locations=None):
        abs_error = 0
        if name in object_guess_locations:
            (img_uvzw, img_xy) = self.image_of_model(object_guess_locations[name])
            error = ( (xy[0]-img_uvzw[0])*(xy[0]-img_uvzw[0]) +
                      (xy[1]-img_uvzw[1])*(xy[1]-img_uvzw[1]))
            abs_error += error
            xscale = xy[0] / img_uvzw[0] * self.scales[0]
            yscale = xy[1] / img_uvzw[1] * self.scales[1]
            if corr is not None:
                corr[0].add_entry(xy[0], img_uvzw[0])
                corr[1].add_entry(xy[1], img_uvzw[1])
                pass
            print name, error, xscale,yscale, "xy %s:%s"%(str(xy), str(img_uvzw[0:2]))
            pass
        return abs_error
