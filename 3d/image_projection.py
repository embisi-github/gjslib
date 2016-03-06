#!/usr/bin/env python

#a Imports
import math
from gjslib.math import matrix, vectors, statistics, quaternion

#a c_image_projection
class c_image_projection(object):
    delta_angle = 0.005  # radians - 0.1 is 6 degrees
    camera_step = 0.01 
    fov_step = 0.01    
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
    fov_deltas = [{"fov":-fov_step},
                  {"fov":+fov_step},
                  {}]
    #f __init__
    def __init__(self,name,image_filename,size=(1.0,1.0)):
        self.name = name
        self.image_filename = image_filename
        self.mvp = None
        self.ip = None
        self.size = size
        self.projection = None
        pass
    #f save_projection_string
    def save_projection_string(self):
        """
        Save string - should be a set of 'n' comma separated items
        """
        repr = "%f,%f,%f "%(self.projection["camera"][0],
                            self.projection["camera"][1],
                            self.projection["camera"][2])
        rpy = self.projection["orientation"].to_euler(degrees=True)
        repr += ", %f,%f,%f "%(rpy[0], rpy[1], rpy[2])
        repr += ", %f, %f, %f "%(self.projection["fov"],
                                 self.projection["aspect"],
                                 self.projection["zFar"])
        return repr
    #f load_projection_strings
    def load_projection_strings(self, data):
        """
        Load a list of strings (undo the save)
        """
        camera = (float(data[0]), float(data[1]), float(data[2]))
        rpy    = (float(data[3]), float(data[4]), float(data[5]))
        fov    = float(data[6])
        aspect = float(data[7])
        zFar   = float(data[8])
        projection = {"camera":camera,
                      "orientation":quaternion.c_quaternion.of_euler(rpy=rpy, degrees=True),
                      "fov":fov,
                      "aspect":aspect,
                      "zFar":zFar}
        self.set_projection(projection)
        pass
    #f get_projection
    def get_projection(self):
        return self.projection
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
        z_of_w_1 = self.mvp.apply((0.0,0.0,-1.0,0.0))
        self.mvp.mult3x3(m=orientation.get_matrix3())
        self.mvp.translate(camera, scale=-1)

        self.ip = self.mvp.projection()
        self.ip.invert()

        self.projection = { "camera":      camera[:],
                            "orientation": orientation,
                            "fov": fov,
                            "zFar": zFar,
                            "aspect": aspect,
                            "z_of_w_1":z_of_w_1[2]
                            }

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
            print "c, ip"
            print c
            print self.ip
            c.postmult(matrix.c_matrixNxN(data=persp.get_matrix(linear=True)))
            print c

        pass
    #f image_of_model
    def image_of_model(self,xyz):
        if self.mvp is None:
            return None
        xy = self.mvp.apply(xyz,perspective=True)
        img_xy = ((1.0+xy[0])/2.0*self.size[0], (1.0-xy[1])/2.0*self.size[1])
        return (xy,img_xy)
    #f model_line_for_image
    def model_line_for_image(self,xy):
        if self.ip is None:
            return None
        dirn = self.ip.apply((xy[0],xy[1],self.projection["z_of_w_1"],1))
        return (self.projection["camera"], dirn[0:3])
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
    #f select_best_z_set
    def select_best_z_set(self, O, Pe, uv, guess_Z, max_results=20, verbose=False):
        """
        O = Object matrix (must be c_matrixNxN of order 4)
        Pe = perspective matrix (from projection aspect, FOV, zFar, zNear)
        image_locations = list of four (u,v) locations for the 4 columns of O
        guess_Z = dictionary of key -> four Z values to use (should all be -ve since they must be in front of the camera)

        Take an Object matrix with columns being 4 object reference points X, Y, Z, 1
        For each column have an image location (u,v) and a guess of distance from camera (Z), such that
        the image space vector would be u,v,z,w where w=-Z and z=((zF+zN).Z + 2*zF*zN)/(zF-zN).
        We can build an image matrix U with each column being (u,v,z,w)

        Now for a valid projection P we have P.O = U
        Hence P = U.O' (O' == O inverse)
        Further, P = Persp.Orient.Camera (Pe.Or.Ca)
        If we know the aspect ratio and FOV for the camera and zF and zN, we know Pe
        So Pe.Or.Ca = U.O', Or.Ca = Pe'.U.O'
        Inverting both sides yields Ca'.Or' = O.U'.Pe

        Ca'.Or' is a translation of a rotation; the translation can be determined by the fourth column
        of the matrix. The bottom row of the matrix should be (0,0,0,1).
        The top 3x3 should be the orientation matrix - a rotation.
        A rotation is supposed to be a unit orthogonal matrix.
        To test for orthogonality find the volume of the unit cube post-rotation; this is V0.V1xV2
        where Vi are the column vectors of the rotation matrix (also this is the determinant...)
        Also, the lengths of each column vector should be 1.
        So a measure of non-orthogonality is:
        NO(Vol) * NO(|V0|) * NO(|V1|) * NO(|V2|)
        where NO(x)=x if x>1, NO(x)=1/x if 0<x<1, NO(x)=1E9 if x<=0
        """
        smallest_error = None
        result_list = []
        U = matrix.c_matrixNxN(order=4)
        for Zk in guess_Z:
            Z_list    = guess_Z[Zk]
            for c in range(4):
                (_, _, z, w) = Pe.apply( (0.0,0.0,Z_list[c],1.0) )
                U[0,c] = w * uv[c][0]
                U[1,c] = w * uv[c][1]
                U[2,c] = z
                U[3,c] = w
                pass

            U_i = U.inverse()
            if U_i is None:
                continue

            Ca_i_Or_i = O.copy()
            Ca_i_Or_i.postmult(U_i)
            Ca_i_Or_i.postmult(Pe)

            # Rotation is top-left 3x3 of Or_i
            R = matrix.c_matrixNxN(order=3)
            for r in range(3):
                for c in range(3):
                    R[r,c] = Ca_i_Or_i[r,c]
                    pass
                pass

            camera = Ca_i_Or_i.get_column(3)[0:3]
            zs_okay = True
            for c in range(4):
                if vectors.vector_separation(O.get_column(c)[:3],camera)*1.1 < -Z_list[c]:
                    zs_okay = False
                    break
                pass
            if not zs_okay:
                continue

            v = (R.get_column(0),R.get_column(1),R.get_column(2))
            volume_r  = vectors.dot_product(vectors.vector_prod3(v[0],v[1]),v[2])
            lengths_r = (vectors.dot_product(v[0],v[0]), vectors.dot_product(v[1],v[1]), vectors.dot_product(v[2],v[2]))
            def NO(x, epsilon=1E-9):
                if (x>1): return x
                if (x>1E-9): return 1/x
                return 1E9
            error = NO(volume_r) * NO(lengths_r[0]) * NO(lengths_r[1]) * NO(lengths_r[2])
            if (volume_r<0): volume_r=1E9
            error = NO(volume_r/lengths_r[0]/lengths_r[1]/lengths_r[2])
            def sum_sq(xs):
                v = 0
                for x in xs:
                    v += x*x
                    pass
                return v
            error = sum_sq((NO(volume_r)-1, NO(lengths_r[0])-1, NO(lengths_r[1])-1, NO(lengths_r[2])-1))
            if (error<1E9):
                if (len(result_list)<max_results) or (error<result_list[-1][0]):
                    orientation = quaternion.c_quaternion().from_matrix(R.transpose())
                    r = (Zk, camera, orientation)
                    print "%s:Error %6f Volume %6f == +1, lengths %s, cam [%5f,%5f,%5f]"%(str(Zk),error, volume_r, str(lengths_r), camera[0],camera[1],camera[2])
                    index = 0
                    for i in range(len(result_list)):
                        if error<result_list[i][0]:
                            index = i
                            break
                        pass
                    result_list.insert(index,(error,r))
                    if len(result_list)>max_results:
                        result_list = result_list[:max_results]
                        pass
                    pass
                pass
            pass
        return result_list
    #f improve_projection_old
    def improve_projection_old(self, object_guess_locations, image_locations, projection, guess_z, coarseness, initial_max_error=1E9, sq_dist_divide=20.0, verbose=False):
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

        #camera = projection["camera"]
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
        if verbose:
            print "O"
            print O
            pass

        persp = matrix.c_matrix4x4()
        yfov = math.atan(math.tan(fov/2.0/180.0*3.1415926)/aspect)*2.0*180.0/3.14159256
        persp.perspective(fov=yfov, aspect=aspect, zFar=2.0, zNear=1.0) # do not use zFar, zNear here
        Pe = matrix.c_matrixNxN(data=persp.get_matrix(linear=True))

        if verbose:
            print "Pe"
            print Pe
            pass

        best_projection = None
        smallest_error = (initial_max_error,None)
        for gi in range(7*7*7*7*5):
            if verbose:
                print "-"*80
                print "Iteration",gi
                print "-"*80
                pass

            gi2 = gi
            ci = (gi2/(7*7*7*7)) % 15
            zNear = 1.0
            #zFar = 1.5*math.pow(1.0,ci+1)
            zFar = 20.0*math.pow(1.3,1+5-ci)
            Pe[2,2] = (zNear+zFar)/(zFar-zNear)
            Pe[2,3] = 2*zNear*zFar/(zFar-zNear)
            def dist(x, camera):
                (x,y,z) = object_guess_locations[x]
                x -= camera[0]
                y -= camera[1]
                z -= camera[2]
                return math.sqrt(x*x+y*y+z*z)

            U = matrix.c_matrixNxN(order=4)
            for c in range(4):
                pt = pts[c]
                ci = (gi2 % 7)
                gi2 = gi2 / 7
                z = -guess_z[pt]*math.pow(coarseness,(ci-3))
                #z = -guess_z[pt]*math.pow(1.013,((ci-3)*coarseness))
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
            volume_r  = vectors.dot_product(vectors.vector_prod3(v[0],v[1]),v[2])
            lengths_r = (vectors.dot_product(v[0],v[0]), vectors.dot_product(v[1],v[1]), vectors.dot_product(v[2],v[2]))
            def NO(x, epsilon=1E-9):
                if (x>1): return x
                if (x>1E-9): return 1/x
                return 1E9
            error = NO(volume_r) * NO(lengths_r[0]) * NO(lengths_r[1]) * NO(lengths_r[2])
            if (volume_r<0): volume_r=1E9
            error = NO(volume_r/lengths_r[0]/lengths_r[1]/lengths_r[2])
            def sum_sq(xs):
                v = 0
                for x in xs:
                    v += x*x
                    pass
                return v
            error = sum_sq((NO(volume_r)-1, NO(lengths_r[0])-1, NO(lengths_r[1])-1, NO(lengths_r[2])-1, NO(volume_r/lengths_r[0]/lengths_r[1]/lengths_r[2])-1))
            sum_sq_dist = 0.0
            if error<smallest_error[0]:#*1.01:
                print "%d:Error %6f Volume %6f == +1, sq_dist %6f == 0.0, lens %s"%(gi,error, volume_r, sum_sq_dist, str(lengths_r))
                #print angles_r
                #print angles_c
                #print lens_r
                #print lens_c
                #print volume_r
                #print volume_c
                #sum_sq_dist = 0
                #for i in range(len(pts)):
                #    k = pts[i]
                #    sum_sq_dist += (U[2,i] - dist(k, C)) * (U[2,i] - dist(k, C))
                #    #print k, U[2,i], dist(k, C), dist(k,camera)
                #    pass
                #print sum_sq_dist

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
                #print "ERROR",gi, error, e0+e1, math.sqrt((e0-e1)*(e0-e1)), (e0, e1), C, q, zNear, zFar
                orientation = quaternion.c_quaternion().from_matrix(R_t)
                best_projection = {"camera":C, "orientation":orientation, "fov":fov, "aspect":aspect, "zNear":zNear, "zFar":zFar}
                best_z = {}
                for c in range(4):
                    best_z[pts[c]] = -U[2,c]
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
        if best_projection is None:
            return None
        if True:
            self.set_projection( best_projection )
            for k in pts:
                print k, self.image_of_model(object_guess_locations[k])
                pass
            pass
        return (best_projection, best_z, smallest_error[0])
    #f improve_projection
    def improve_projection(self, O, Pe, uv, guess_Z, coarseness, initial_max_error=1E9, verbose=False):
        base_guess_Z = guess_Z

        guess_Z = {}
        for gi in range(7*7*7*7):

            gi2 = gi
            if False:
                ci = (gi2/(7*7*7*7)) % 15
                zNear = 1.0
                zFar = 20.0*math.pow(1.3,1+5-ci)
                Pe[2,2] = (zNear+zFar)/(zFar-zNear)
                Pe[2,3] = 2*zNear*zFar/(zFar-zNear)
                pass

            gZ = []
            for c in range(4):
                ci = (gi2 % 7)
                gi2 = gi2 / 7
                gZ.append(base_guess_Z[c]*math.pow(coarseness,(ci-3)))
                pass
            guess_Z[gi] = gZ
            pass
        r = self.select_best_z_set(O=O, Pe=Pe, uv=uv, guess_Z=guess_Z, max_results=1, verbose=False)
        if r is None:
            return None
        (error, (gi, camera, orientation)) = r[0]
        return ({"camera":camera, "orientation":orientation}, guess_Z[gi], error)

    #f get_best_projection_for_guess_Z
    def get_best_projection_for_guess_Z(self, O, Pe, uv, guess_Z, spread=1.15, iterations=5):
        max_error = 1E9
        for c in range(iterations):
            # Each run uses coarseness^-3 ... 1.0 ... coarseness^3
            # So an overlap of coarseness^1.5 seems sensible
            coarseness = math.pow(spread,(1.5/(1.5*(c+1))))
            print "Run with coarseness",c,coarseness
            r = self.improve_projection( O=O, Pe=Pe, uv=uv,
                                         guess_Z = guess_Z,
                                         initial_max_error = max_error*1.01,
                                         coarseness = coarseness )
            if r is None:
                return None
            (improved_projection, improved_z, max_error) = r
            guess_Z = improved_z
            pass
        return (improved_projection, improved_z, max_error)

    #f guess_initial_projection_matrix
    def guess_initial_projection_matrix(self, point_mappings ):
        # iphone 6s has XFOV of about 55, YFOV is therefore about 47
        projection = {"aspect":self.size[0]/float(self.size[1]),
                      "fov":55.0,
                      "zFar":40.0
                      }
        zNear = 1.0
        zFar  = projection["zFar"]
        aspect = projection["aspect"]
        fov = projection["fov"]

        object_guess_locations = {}
        for pt in point_mappings.object_guess_locations:
            if pt in point_mappings.image_mappings:
                object_guess_locations[pt] = point_mappings.object_guess_locations[pt]
                pass
            pass

        image_locations = {}
        for pt in object_guess_locations:
            if self.name in point_mappings.image_mappings[pt]:
                image_locations[pt] = point_mappings.image_mappings[pt][self.name]
                pass
            else:
                del(object_guess_locations[pt])
                pass
            pass

        if len(image_locations)!=4:
            print "Require 4 object guess locations with image locations for initial projection matrix"
            return None

        pt_names = image_locations.keys()
        pt_names.sort()

        O = matrix.c_matrixNxN(order=4)
        objs = []
        uv = []
        Oc = (0.0,0.0,0.0)
        for c in range(4):
            pt = pt_names[c]
            obj = object_guess_locations[pt]
            O[0,c] = obj[0]
            O[1,c] = obj[1]
            O[2,c] = obj[2]
            O[3,c] = 1.0
            u = -1.0 + (image_locations[pt][0]/self.size[0])*2.0
            v =  1.0 - (image_locations[pt][1]/self.size[1])*2.0
            uv.append((u,v))
            Oc = vectors.vector_add(Oc,obj,scale=0.25)
            objs.append(obj)
            pass

        Pe = matrix.c_matrixNxN(data=[0.0]*16)
        f = 1.0/math.tan(fov*3.14159265/180.0/2)
        Pe[0,0] = f
        Pe[1,1] = f*aspect
        Pe[2,2] = -(zNear+zFar)/(zFar-zNear)
        Pe[2,3] = -2*zNear*zFar/(zFar-zNear)
        Pe[3,2] = -1.0

        guess_Z = {}
        n = 11
        for i in range(n*n*n*n):
            # vi in range 0 to n-1
            # zs in range 0 to 1.7*(n-1) in steps of 1.7
            v = (i%n, (i/n)%n, (i/n/n%n), (i/n/n/n%n))
            zs = []
            for c in range(4):
                #zs.append( -1.0*(v[c]*1.7) ) # was 1.7 for 'img_1'
                #zs.append( -1.0*(v[c]*2.5)-10 ) # was 1.7 for 'img_1'
                zs.append( -1.0*(v[c]*1.7)-5 ) # was 1.7 for 'img_1'
                pass
            guess_Z[v] = zs
            pass
        results = self.select_best_z_set(O, Pe, uv, guess_Z, max_results=5)

        best_zs_guesses = []
        for r in results:
            (error, (ijkl, camera, orientation)) = r
            print "error, ijkl, camera, zs",error, ijkl, camera, guess_Z[ijkl]
            best_zs_guesses.append(guess_Z[ijkl])
            pass

        best_zs_results = []
        for gZ in best_zs_guesses:
            print "-"*80
            print "Looking for best of",gZ
            r = self.get_best_projection_for_guess_Z(O, Pe, uv, gZ, spread=1.05, iterations=5)
            if r is None:
                print "FAILED"
                pass
            else:
                (improved_projection, improved_z, max_error) = r
                print improved_projection, improved_z, max_error
                best_zs_results.append(r)
                pass
            pass

        def cmp_results(a,b):
            if a[2]<b[2]: return True
            return False

        best_zs_results.sort(cmp=cmp_results)
        print best_zs_results
        for (proj,gZ,error) in best_zs_results:
            r = self.get_best_projection_for_guess_Z(O, Pe, uv, gZ, spread=math.pow(1.05,1/(1.5*(5-1))), iterations=15)
            if r is None:
                continue
            print r
            (improved_projection, improved_z, max_error) = r
            improved_projection = {"camera":improved_projection["camera"],
                                   "orientation":improved_projection["orientation"],
                                   "fov":projection["fov"],
                                   "aspect":projection["aspect"],
                                   "zFar":projection["zFar"],
                                   }
            break
            
        opt_projection = improved_projection
        if True:
            print "Optimizing orientation (which is not refined yet)... delta scale 1"
            self.set_projection(opt_projection)
            opt_projection = self.optimize_projection(point_mappings = point_mappings,
                                                  fov_iterations=1, orientation_iterations=1000, camera_iterations=10, delta_scale=1 )
            print "Optimizing orientation (which is not refined yet)... delta scale 0."
            self.set_projection(opt_projection)
            opt_projection = self.optimize_projection(point_mappings = point_mappings,
                                                  fov_iterations=1, orientation_iterations=1000, camera_iterations=10, delta_scale=0.1 )
            print "Optimizing orientation (which is not refined yet)... delta scale 0.01"
            self.set_projection(opt_projection)
            opt_projection = self.optimize_projection(point_mappings = point_mappings,
                                                  fov_iterations=1, orientation_iterations=1000, camera_iterations=10, delta_scale=0.01 )
            print "Optimizing orientation (which is not refined yet)... delta scale 0.001"
            self.set_projection(opt_projection)
            opt_projection = self.optimize_projection(point_mappings = point_mappings,
                                                  fov_iterations=1, orientation_iterations=1000, camera_iterations=10, delta_scale=0.001 )
            pass

        print "Optimized:\nself.images['%s']['projection'] = %s"%(self.name,str(opt_projection))
        pts = object_guess_locations.keys()
        pts.sort()
        sum_d = 0
        for k in pts:
            (xyzw,uv) = self.image_of_model(object_guess_locations[k])
            d = vectors.vector_separation(uv,image_locations[k])
            sum_d += d
            print k, d, uv, image_locations[k]
            pass
        print "Total error",sum_d
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
                    q.from_euler(roll=i*angle,pitch=j*angle,yaw=k*angle,degrees=True)
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
            q.from_euler(rpy=ijk, degrees=True)
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
    #f run_optimization
    def run_optimization(self, point_mappings, coarse=True):
        opt_projection = self.optimize_projection(point_mappings = point_mappings,
                                                  fov_iterations=500, orientation_iterations=100, camera_iterations=10, delta_scale=1 )
        self.set_projection(opt_projection)
        opt_projection = self.optimize_projection(point_mappings = point_mappings,
                                                  fov_iterations=500, orientation_iterations=100, camera_iterations=10, delta_scale=0.1 )

        self.set_projection(opt_projection)
        opt_projection = self.optimize_projection(point_mappings = point_mappings,
                                                  fov_iterations=2000, orientation_iterations=1, camera_iterations=1, delta_scale=0.01, do_fov=True, do_camera=False )

        self.set_projection(opt_projection)

        if coarse:
            print "Optimized:\nself.images['%s']['projection'] = %s"%(self.name,str(opt_projection))
            return

        opt_projection = self.optimize_projection(point_mappings = point_mappings,
                                                  fov_iterations=100, orientation_iterations=100, camera_iterations=10, delta_scale=0.05 )
        self.set_projection(opt_projection)
        opt_projection = self.optimize_projection(point_mappings = point_mappings,
                                                  fov_iterations=200, orientation_iterations=100, camera_iterations=10, delta_scale=0.03 )
        #opt_projection = {'fov': 55, 'camera': [18.946400287962323, -22.74361538580119, 26.758691580937942], 'orientation': quaternion.c_quaternion(euler=(10.6165, 2.6457,50.3051),degrees=True), 'aspect': 1.3333333333333333, 'zFar': 33.800000000000004}
        self.set_projection(opt_projection)
        opt_projection = self.optimize_projection(point_mappings = point_mappings,
                                                  fov_iterations=200, orientation_iterations=100, camera_iterations=10, delta_scale=0.03 )
        #opt_projection = {'fov': 55, 'camera': [18.718700287962854, -22.75111538580117, 26.84179158093775], 'orientation': quaternion.c_quaternion(euler=(10.4051, 2.3963,50.1888),degrees=True), 'aspect': 1.3333333333333333, 'zFar': 33.800000000000004}
        self.set_projection(opt_projection)
        opt_projection = self.optimize_projection(point_mappings = point_mappings,
                                                  fov_iterations=2000, orientation_iterations=1, camera_iterations=1, delta_scale=0.001, do_fov=True, do_camera=False )
        self.set_projection(opt_projection)
        opt_projection = self.optimize_projection(point_mappings = point_mappings,
                                                  fov_iterations=1, orientation_iterations=100, camera_iterations=100, delta_scale=0.01 )
        self.set_projection(opt_projection)
        opt_projection = self.optimize_projection(point_mappings = point_mappings,
                                                  fov_iterations=1, orientation_iterations=100, camera_iterations=100, delta_scale=0.003 )
        self.set_projection(opt_projection)
        opt_projection = self.optimize_projection(point_mappings = point_mappings,
                                                  fov_iterations=1, orientation_iterations=100, camera_iterations=100, delta_scale=0.001 )

        self.set_projection(opt_projection)
        print "Optimized:\nself.images['%s']['projection'] = %s"%(self.name,str(opt_projection))
        pass
    #f optimize_projection
    def optimize_projection(self,
                            point_mappings,
                             use_references = True,
                             fov_iterations=10,
                             orientation_iterations=10,
                             camera_iterations=10,
                             delta_scale=0.05,
                            do_fov=False,
                            do_camera=True,
                             verbose=False):
        base_projection = self.projection
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
    import image_point_mapping
    pm = image_point_mapping.c_point_mapping()
    image_name = "left"
    image_name = "middle"
    pm.load_data("pencils.map")
    pm.add_image(image_name,size=(3264.0,2448.0))
    proj = c_image_projection(image_name,"img_filename", size=(3264.0,2448.0))
    pm.set_projection(image_name,proj)
    proj.guess_initial_projection_matrix(point_mappings = pm)
    pass
