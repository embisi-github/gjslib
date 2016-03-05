#!/usr/bin/env python

#a Imports
import math
from gjslib.math import matrix, vectors, statistics, quaternion

#a c_image_projection
class c_image_projection(object):
    delta_angle = 0.005  # radians - 0.1 is 6 degrees
    camera_step = 0.01 
    camera_deltas = [{"camera":(-camera_step,0.0,0.0)},
                     {"camera":(+camera_step,0.0,0.0)},
                     {"camera":(0.0,-camera_step,0.0)},
                     {"camera":(0.0,+camera_step,0.0)},
                     {"camera":(0.0,0.0,-camera_step)},
                     {"camera":(0.0,0.0,+camera_step)},
                     {"camera":(-camera_step,-camera_step,0.0)},
                     {"camera":(+camera_step,-camera_step,0.0)},
                     {"camera":(-camera_step,+camera_step,0.0)},
                     {"camera":(+camera_step,+camera_step,0.0)},
                     {}]
    orientation_deltas = [{"roll":-delta_angle},
                          {"roll":+delta_angle},
                          {"pitch":+delta_angle},
                          {"pitch":-delta_angle},
                          {"yaw":+delta_angle},
                          {"yaw":-delta_angle},
                          {"roll":+delta_angle, "yaw":+delta_angle},
                          {"roll":+delta_angle, "yaw":-delta_angle},
                          {"roll":-delta_angle, "yaw":+delta_angle},
                          {"roll":-delta_angle, "yaw":-delta_angle},
                          {"roll":+delta_angle, "pitch":+delta_angle},
                          {"roll":+delta_angle, "pitch":-delta_angle},
                          {"roll":-delta_angle, "pitch":+delta_angle},
                          {"roll":-delta_angle, "pitch":-delta_angle},
                          {"yaw":+delta_angle, "pitch":+delta_angle},
                          {"yaw":+delta_angle, "pitch":-delta_angle},
                          {"yaw":-delta_angle, "pitch":+delta_angle},
                          {"yaw":-delta_angle, "pitch":-delta_angle},
                     {}]
    fov_deltas = [{"fov":-0.01},
                  {"fov":+0.01},
                  {}]
    #f __init__
    def __init__(self,name,image_filename,size=(1.0,1.0)):
        self.name = name
        self.image_filename = image_filename
        self.mvp = None
        self.ip = None
        self.size = size
        pass
    #f set_projection
    def set_projection(self, projection=None, deltas=None, delta_scale=1.0, resultant_projection=None, verbose=False ):
        if projection is None:
            projection = {"camera":(0.0,0.0,-20.0), "orientation":quaternion.c_quaternion(), "fov":90, "aspect":1.0}
            pass
        fov         = projection["fov"]          # Scalar
        aspect      = projection["aspect"]       # Scalar (x / y)
        camera      = projection["camera"]       # 3D vector
        orientation = projection["orientation"]  # unit quaternion
        orientation = orientation.copy()
        if deltas is not None:
            if "camera"      in deltas: camera = vectors.vector_add(camera, deltas["camera"], scale=delta_scale)
            if "roll"        in deltas: orientation = quaternion.c_quaternion.roll (deltas["roll"] *delta_scale).multiply(orientation)
            if "pitch"       in deltas: orientation = quaternion.c_quaternion.pitch(deltas["pitch"]*delta_scale).multiply(orientation)
            if "yaw"         in deltas: orientation = quaternion.c_quaternion.yaw  (deltas["yaw"]  *delta_scale).multiply(orientation)
            if "aspect"      in deltas: aspect = aspect* (1+delta_scale*deltas["aspect"])
            if "fov"         in deltas: fov    = fov   * (1+delta_scale*deltas["fov"])
            pass
        self.mvp = matrix.c_matrix4x4()
        #self.mvp.perspective(fov=fov, aspect=aspect, zFar=1.0, zNear=0.0)
        # Use 360 as we use 'half FOV' i.e. fov/2
        yfov = math.atan(math.tan(fov/360.0*3.1415926)/aspect)*360.0/3.14159256
        # zFar and zNear do not seem to effect mapping to image (correctly!)
        # However, zNear must not be 0 or the projection matrix will be singular
        zFar = 40.0
        if "zFar" in projection:zFar=projection["zFar"]
        self.mvp.perspective(fov=yfov, aspect=aspect, zFar=zFar, zNear=1.0)
        persp = self.mvp.copy()
        self.mvp.mult3x3(m=orientation.get_matrix3())
        self.mvp.translate(camera, scale=-1)

        self.ip = self.mvp.projection()
        self.ip.invert()

        self.projection = { "camera":      camera[:],
                            "orientation": orientation,
                            "fov": fov,
                            "zFar": zFar,
                            "aspect": aspect}

        if resultant_projection is not None:
            resultant_projection["camera"]      = camera[:]
            resultant_projection["orientation"] = orientation.copy()
            resultant_projection["fov"]         = fov
            resultant_projection["aspect"]      = aspect
            resultant_projection["zFar"]        = zFar
            pass

        if verbose:
            print "Projection..."
            print self.projection
            print persp
            print self.mvp
            c = matrix.c_matrixNxN(data=self.mvp.get_matrix(linear=True))
            print c
            c.invert()
            print c
            c.postmult(matrix.c_matrixNxN(data=persp.get_matrix(linear=True)))
            print c

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
        return (self.projection["camera"], dirn)
    #f mapping_error
    def mapping_error(self, name, xyz, xy, corr=None, epsilon=1E-6, verbose=False ):
        abs_error = 0
        (img_uvzw, img_xy) = self.image_of_model(xyz)
        error = ( (xy[0]-img_uvzw[0])*(xy[0]-img_uvzw[0]) +
                  (xy[1]-img_uvzw[1])*(xy[1]-img_uvzw[1]))
        if corr is not None:
            corr[0].add_entry(xy[0], img_uvzw[0])
            corr[1].add_entry(xy[1], img_uvzw[1])
            pass
        if verbose:
            print "%16s"%name, error, "xy %s:%s"%(str(xy), str(img_uvzw[0:2]))
            pass
        return error
    #f calc_point_errors
    def calc_point_errors(self, point_mappings, pt_names, use_references=False, verbose=False):
        err = 0
        corr = [statistics.c_correlation(), statistics.c_correlation()]
        pts = 0
        for n in pt_names:
            xyz = point_mappings.get_xyz( n, use_references )
            mapping_xy = point_mappings.get_xy(n,self.name)
            if (xyz is not None) and (mapping_xy is not None):
                err += self.mapping_error(n,xyz,mapping_xy,corr,verbose=verbose)
                pts += 1
                pass
            pass
        return (pts,err,corr)
    #f improve_projection
    def improve_projection(self, object_guess_locations, image_locations, projection, coarseness, verbose=False):
        """
        Take 4 object reference points with u,v and X, Y, Z
        In object space make a matrix O that is column vectors XYZ1
        Note that P.(XYZ1) = (uw, vw, z, w)
        and note that w=k.z+l for some constant k and l for the projection
        So if we choose values for the object z's, we can get a 
        matrix U of the 4 columns in image space - where we choose four z's
        in the range 1.0 to 40.0 for example (since the objects are not clipped)

        Now, if P.O = U for some P, then P = U.O' (O' == O inverse)
        Further, P = Persp.Orient.Camera (Pe.Or.Ca)
        If we know the aspect ratio and FOV for the camera, and we have a known
        mapping from z to w, then we know Pe, hence also Pe'
        So Pe.Or.Ca = U.O', Or.Ca = Pe'.U.O'
        Now, the rotation of a translation can be inverted - it becomes a translation of a rotation
        So (Or.Ca)' = Ca'.Or'.
        Since the translation can be determined by the fourth column of the matrix, we can find the camera
        position by just reading this off.
        The bottom row of the matrix should be zeros (except in the fourth column, which should be 1)
        The top 3x3 should be the rotation - which should be an orthogonal matrix
        To test how close to an orthogonal matrix the 3x3 is one can multiply it by its transpose,
        and should get the identity
        So if we find a candidate for Ca'.Or' we can tell how good it is as a candidate.

        Now (Or.Ca)' = Ca'.Or' = (Pe'.U.O')' = O.U'.Pe

        Hence for a candidate U guess (4 degrees of freedom) we can get a measure of goodness of fit
        from examining the bottom row and the 3x3 'rotation' section of O.U'.Pe
        
        Now, if we assume a zNear of 1.0 and a zFar of 40.0, we have the bottom 2x2 of Pe as 
        1.051282051  2.051282051
        -1.000000000  0.000000000

        This is applied to (Z,1) to get (z,w): hence z = 2.0513 + 1.0513Z, w=-Z (where Z is post-orientation, post camera translation)
        In particular we can state that z=2.0513-1.0513w, of w=(2.0513-z)/1.0513
        So this gives a mechanism for determining uvzw from a given u,v and a guess at z (distance from camera)

        But what should the values of zNear and zFar be?

        Pre-perspective, the transformed coordinates are in 'world units'. This is scaled by 1/w, so w must be in world units (which it clearly is)
        zFar is effectively our 'we can ignore it as that is infinity' clipping - so we should let that tend to infinity
        Then we have the bottom of 2x2 of Pe as 1.0, 2*zNear, -1.0, 0.0; with w=(2*zNear-z) / 1
        The matrix is degenerate if zNear is 0

        We want to find the zNear and zFar... let's try...

        (note... object measurements here are in 0.8cm)
        """

        pts = object_guess_locations.keys()
        pts.sort()
        print pts

        camera = projection["camera"]
        aspect = projection["aspect"]
        fov    = projection["fov"] # xFOV
        # Do not use orientation

        obj_data = []
        for i in range(3):
            for k in pts:
                obj_data.append( object_guess_locations[k][i] )
                pass
            pass
        obj_data.extend([1.0,1.0,1.0,1.0])
        O=matrix.c_matrixNxN(data=obj_data)
        print "O"
        print O

        persp = matrix.c_matrix4x4()
        yfov = math.atan(math.tan(fov/2.0/180.0*3.1415926)/aspect)*2.0*180.0/3.14159256
        persp.perspective(fov=yfov, aspect=aspect, zFar=2.0, zNear=1.0) # do not use zFar, zNear here
        Pe = matrix.c_matrixNxN(data=persp.get_matrix(linear=True))

        print "Pe"
        print Pe

        smallest_error = (1E9,None)
        for gi in range(7*7*7*7*15):
            if verbose:
                print "-"*80
                print "Iteration",gi,camera
                print "-"*80
                pass

            gi2 = gi
            ci = (gi2/(7*7*7*7)) % 15
            zNear = 1.0
            #zFar = 1.5*math.pow(1.0,ci+1)
            zFar = 20.0*math.pow(1.0,ci+1)
            Pe[2,2] = (zNear+zFar)/(zFar-zNear)
            Pe[2,3] = 2*zNear*zFar/(zFar-zNear)
            def dist(x, camera):
                (x,y,z) = object_guess_locations[x]
                x -= camera[0]
                y -= camera[1]
                z -= camera[2]
                return math.sqrt(x*x+y*y+z*z)
            guess_z = {}
            for k in pts:
                guess_z[k] = dist(k, camera)
                pass

            U = matrix.c_matrixNxN(order=4)
            for c in range(4):
                pt = pts[c]
                ci = (gi2 % 7)
                gi2 = gi2 / 7
                z = -guess_z[pt]*math.pow(1.013,((ci-3)*coarseness))
                w = (Pe[2,3]-z)/Pe[2,2]
                U[2,c] = z
                U[3,c] = w
                U[0,c] = w * ( (image_locations[pt][0] / float(self.size[0]))*2.0-1.0)
                U[1,c] = w * (-(image_locations[pt][1] / float(self.size[1]))*2.0+1.0)
                pass

            U_i = U.inverse()
            if U_i is None:
                continue

            Ca_i_Or_i = O.copy()
            Ca_i_Or_i.postmult(U_i)
            Ca_i_Or_i.postmult(Pe)

            # Deduced camera location is Ca_i
            C = Ca_i_Or_i.get_column(3)[0:3]

            # Rotation is top-left 3x3 of Or_i
            R = matrix.c_matrixNxN(order=3)
            for r in range(3):
                for c in range(3):
                    R[r,c] = Ca_i_Or_i[r,c]
                    pass
                pass

            # Note that bottom row of Ca_i_Or_i is going to be 0.0,0.0,0.0,-1.0
            # It always is
            if verbose:
                br = Ca_i_Or_i.get_row(3)
                br = vectors.vector_add(br,(0.0,0.0,0.0,-1.0))
                print "br check",vectors.dot_product(br,br)
                print "C"
                print C
                print "R"
                print R
                pass

            if verbose:
                print "Check of perp vectors"
                pass

            v = (R.get_column(0),R.get_column(1),R.get_column(2))
            volume_r = vectors.dot_product(vectors.vector_prod3(v[0],v[1]),v[2])
            angles_r = (vectors.cos_angle_between(v[0],v[1]), vectors.cos_angle_between(v[1],v[2]), vectors.cos_angle_between(v[2],v[0]))
            lens_r = (vectors.dot_product(v[0],v[0]), vectors.dot_product(v[1],v[1]), vectors.dot_product(v[2],v[2]))
            e0 = angles_r[0]*angles_r[0] + angles_r[1]*angles_r[1] + angles_r[2]*angles_r[2]
            v = (R.get_row(0),R.get_row(1),R.get_row(2))
            volume_c = vectors.dot_product(vectors.vector_prod3(v[0],v[1]),v[2])
            angles_c = (vectors.cos_angle_between(v[0],v[1]), vectors.cos_angle_between(v[1],v[2]), vectors.cos_angle_between(v[2],v[0]))
            lens_c = (vectors.dot_product(v[0],v[0]), vectors.dot_product(v[1],v[1]), vectors.dot_product(v[2],v[2]))
            e1 = angles_c[0]*angles_c[0] + angles_c[1]*angles_c[1] + angles_c[2]*angles_c[2]

            if volume_c>0:
                pass
            else:
                volume_c = 100-volume_c
                #error=1E19
                pass

            sum_sq_dist = 0
            for i in range(len(pts)):
                k = pts[i]
                sum_sq_dist += (-U[2,i] - dist(k, C)) * (-U[2,i] - dist(k, C))
                pass
            e2 = volume_r
            if (e2<=0): e2=1E9
            if (e2<1):e2=1/e2
            error = e2 + sum_sq_dist/20.0
            if error<smallest_error[0]:#*1.01:
                print "Error %6f Volume %6f == +1, sq_dist %6f == 0.0, det^2 (or/det^-2) %6f == 1.0"%(error, volume_r, sum_sq_dist, R.determinant())
                #print angles_r
                #print angles_c
                #print lens_r
                #print lens_c
                #print volume_r
                #print volume_c
                sum_sq_dist = 0
                for i in range(len(pts)):
                    k = pts[i]
                    sum_sq_dist += (U[2,i] - dist(k, C)) * (U[2,i] - dist(k, C))
                    print k, U[2,i], dist(k, C), dist(k,camera)
                    pass
                print sum_sq_dist

                R_t = R.copy().transpose()
                #R_R_t = R.copy().postmult(R_t)
                #print "R.R_t"
                #print R_R_t.determinant(), R_R_t

                q = quaternion.c_quaternion().from_matrix(R)
                #print "R and q - should be the same..."
                #print R
                #print q.get_matrix3()
                #print

                smallest_error = (error, None)
                print "ERROR",gi, error, e0+e1, math.sqrt((e0-e1)*(e0-e1)), (e0, e1), C, q, zNear, zFar
                orientation = quaternion.c_quaternion().from_matrix(R_t)
                best_projection = {"camera":C, "orientation":orientation, "fov":fov, "aspect":aspect, "zNear":zNear, "zFar":zFar}
                if True:
                    self.set_projection( best_projection )
                    for k in pts:
                        print k, self.image_of_model(object_guess_locations[k])
                        pass
                    #print U
                    pass
                pass

            if verbose:
                OrCa = Ca_i_Or_i.inverse()
                print "OrCa"
                print OrCa
                mvp = OrCa.copy()
                mvp.premult(Pe)
                print mvp
                pass

            pass
        return best_projection
    #f guess_initial_projection_matrix
    def guess_initial_projection_matrix(self):
        object_guess_locations = {}
        object_guess_locations["calc.b.fr"]   = ( 24.0,  0.0, 0.0)
        object_guess_locations["calc.t.bl"]   = ( 10.2, 19.0, 2.0)
        object_guess_locations["clips.b.fr"]  = ( 0.0,   0.0, 0.0)
        object_guess_locations["clips.t.fr"]  = ( 0.0,   0.0, 7.5)

        image_locations = {}
        image_locations["calc.b.fr"]   = ( 2691.936508,1205.542857 )
        image_locations["calc.t.bl"]   = ( 1161.396825,697.485714 )
        image_locations["clips.b.fr"]  = ( 927.740759,1937.970392 )
        image_locations["clips.t.fr"]  = ( 811.250794,1313.371429 )
        camera = [10, -10, 20]

        image_locations["calc.b.fr"]   = ( 2616.035556,1841.569524 )
        image_locations["calc.t.bl"]   = ( 1644.606984,697.550476 )
        image_locations["clips.b.fr"]  = ( 513.173333,1598.000000 )
        image_locations["clips.t.fr"]  = ( 328.213333,1081.200000 )
        camera = [30, 0, 20]

        # iphone 6s has XFOV of about 55, YFOV is therefore about 47
        projection = {"camera":camera,
                      "aspect":self.size[0]/float(self.size[1]),
                      "fov":55,
                      }
        #for c in [5.0,3.0,1.5]:
        for c in [5.0,4.0,3.0,2.0,1.4,1.0,0.8,0.6,0.5,0.4,0.3,0.25]:#,0.4,0.3,0.15]:
            improved_projection = self.improve_projection( object_guess_locations=object_guess_locations,
                                                           image_locations = image_locations,
                                                           projection = projection,
                                                           coarseness = c )
            print improved_projection
            projection["camera"] = improved_projection["camera"]
        return
    #f guess_initial_orientation
    def guess_initial_orientation(self, point_mappings, use_references=False, steps=20, verbose=False):
        """
        This may end up facing the wrong direction
        """
        angle = 360.0/steps
        q = quaternion.c_quaternion()
        base_projection = self.projection
        base_projection["orientation"] = q
        smallest_error = (1, 100000, None)
        pt_names = point_mappings.get_mapping_names()
        for i in range(steps):
            for j in range(steps):
                for k in range(steps/2): # don't need to look behind - we get the same 'error'
                    q.from_euler(i*angle,j*angle,k*angle,degrees=True)
                    self.set_projection(projection=base_projection)
                    (pts,e,corr) = self.calc_point_errors(point_mappings, pt_names,
                                                          use_references=use_references,
                                                          verbose=verbose)
                    if (pts>=smallest_error[0]):
                        if (e<smallest_error[1]):
                            smallest_error = (pts, e, (i*angle,j*angle,k*angle))
                            pass
                        pass
                    pass
                pass
            pass
        (pts,e,ijk) = smallest_error
        if ijk is not None:
            print "Best initial orientation has error ",e,"from",pts,"pts",ijk
            q.from_euler(ijk[0],ijk[1],ijk[2],degrees=True)
            self.set_projection(projection=base_projection)
            if True:
                self.calc_point_errors(point_mappings, pt_names,
                                       use_references=use_references,
                                       verbose=True)
            pass
        return base_projection
    #f guess_better_projection
    def guess_better_projection(self, point_mappings, base_projection, use_references=True, deltas_list=[{}], delta_scale=1.0, scale_error_weight=0.1, verbose=False):
        smallest_error = ({},10000,base_projection,1.0,1.0)
        for deltas in deltas_list:
            r = {}
            self.set_projection( projection=base_projection, deltas=deltas, delta_scale=delta_scale, resultant_projection=r )
            if verbose:
                print "\ngbp :", deltas, delta_scale, r
                pass
            (pts,e,corr) = self.calc_point_errors(point_mappings, point_mappings.get_mapping_names(),
                                                  use_references=use_references,
                                                  verbose=verbose)
            if pts>0:
                corr[0].add_entry(0.0,0.0)
                corr[1].add_entry(0.0,0.0)
                full_e = e
                #full_e += scale_error_weight*(1-corr[0].correlation_coefficient())
                #full_e += scale_error_weight*(1-corr[1].correlation_coefficient())
                #print "Total error",full_e,e,1-corr[0].correlation_coefficient(), 1-corr[1].correlation_coefficient()
                if full_e<smallest_error[1]:
                    smallest_error = (deltas,full_e,r)
                    pass
                pass
            pass
        if verbose:
            print "Smallest error",smallest_error
            print
            pass
        return (smallest_error[0], smallest_error[2])
    #f optimize_projection
    def optimize_projection(self,
                            point_mappings,
                             use_references = False,
                             fov_iterations=10,
                             orientation_iterations=10,
                             camera_iterations=10,
                             delta_scale=0.05,
                             verbose=False):
        base_projection = self.projection
        do_fov = True
        do_camera = True
        for k in range(fov_iterations):
            (xsc,ysc)=(1.0,1.0)
            for i in range(camera_iterations):
                done = False
                for j in range(orientation_iterations):
                    (d,p) = self.guess_better_projection(point_mappings, base_projection, use_references, self.orientation_deltas, delta_scale=delta_scale, verbose=verbose)
                    base_projection = p
                    if len(d)==0:
                        #print "Oriented complete at",j,i
                        done = True
                        break
                    pass
                if done and do_camera:
                    (d,p) = self.guess_better_projection(point_mappings, base_projection, use_references, self.camera_deltas, delta_scale=delta_scale, scale_error_weight=0.1, verbose=verbose)
                    base_projection = p
                    if len(d)!=0: done=False
                    pass
                if done:
                    break
                pass
            if done and do_fov:
                (d,p) = self.guess_better_projection(point_mappings, base_projection, use_references, self.fov_deltas, delta_scale=delta_scale, verbose=verbose)
                base_projection = p
                if len(d)!=0: done=False
                pass
            if done:
                break
            pass
        (d,p) = self.guess_better_projection(point_mappings, base_projection, use_references, verbose=verbose)
        self.set_projection(base_projection)
        return base_projection
    #f All done
    pass

#a Toplevel
if __name__=="__main__":
    a = c_image_projection("name","img_filename", size=(3264.0,2448.0))
    a.guess_initial_projection_matrix()
    pass
