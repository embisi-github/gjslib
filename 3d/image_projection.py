#!/usr/bin/env python
"""
Note guess_Zs that are good (error 0.01...)

0.0122213866214 (15, 17, 11, 9) [-0.6717595748421669, -0.4767217795729873, 0.5669880232320921] [-39.5, -44.5, -29.5, -24.5]
"""

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
        if self.projection is None:
            return None
        if "camera" not in self.projection:
            return None
        if "orientation" not in self.projection:
            return None
        if "xfov" not in self.projection:
            return None
        if "yfov" not in self.projection:
            return None
        repr = "%f,%f,%f "%(self.projection["camera"][0],
                            self.projection["camera"][1],
                            self.projection["camera"][2])
        rpy = self.projection["orientation"].to_euler(degrees=True)
        repr += ", %f,%f,%f "%(rpy[0], rpy[1], rpy[2])
        repr += ", %f, %f,"%(self.projection["xfov"],
                             self.projection["yfov"])
        return repr
    #f load_projection_strings
    def load_projection_strings(self, data):
        """
        Load a list of strings (undo the save)
        """
        camera = (float(data[0]), float(data[1]), float(data[2]))
        rpy    = (float(data[3]), float(data[4]), float(data[5]))
        xfov    = float(data[6])
        yfov    = float(data[7])
        projection = {"camera":camera,
                      "orientation":quaternion.c_quaternion.of_euler(rpy=rpy, degrees=True),
                      "xfov":xfov,
                      "yfov":yfov,
                      }
        self.set_projection(projection)
        pass
    #f get_projection
    def get_projection(self):
        return self.projection
    #f set_projection
    def set_projection(self, projection=None, deltas=None, delta_scale=1.0, resultant_projection=None, verbose=False ):
        if projection is None:
            projection = {"camera":(0.0,0.0,-20.0), "orientation":quaternion.c_quaternion(), "xfov":65, "yfov":65}
            pass
        xfov        = projection["xfov"]         # Scalar
        yfov        = projection["yfov"]         # Scalar
        camera      = projection["camera"]       # 3D vector
        orientation = projection["orientation"]  # unit quaternion
        orientation = orientation.copy()
        if deltas is not None:
            if "camera"      in deltas: camera = vectors.vector_add(camera, deltas["camera"], scale=delta_scale)
            if "roll"        in deltas: orientation = quaternion.c_quaternion.roll (deltas["roll"] *delta_scale).multiply(orientation)
            if "pitch"       in deltas: orientation = quaternion.c_quaternion.pitch(deltas["pitch"]*delta_scale).multiply(orientation)
            if "yaw"         in deltas: orientation = quaternion.c_quaternion.yaw  (deltas["yaw"]  *delta_scale).multiply(orientation)
            pass
        self.mvp = matrix.c_matrix4x4()
        #self.mvp.perspective(fov=fov, aspect=aspect, zFar=1.0, zNear=0.0)
        # Use 360 as we use 'half FOV' i.e. fov/2
        #yfov = math.atan(math.tan(fov/360.0*3.1415926)/aspect)*360.0/3.14159256
        # zFar and zNear do not seem to effect mapping to image (correctly!)
        # However, zNear must not be 0 or the projection matrix will be singular
        zFar = 40.0
        aspect = math.tan(xfov/360.0*3.14159256) / math.tan(yfov/360.0*3.14159256)
        self.mvp.perspective(fov=yfov, aspect=aspect, zFar=zFar, zNear=1.0)
        persp = self.mvp.copy()
        z_of_w_1 = self.mvp.apply((0.0,0.0,-1.0,0.0))
        self.mvp.mult3x3(m=orientation.get_matrix3())
        self.mvp.translate(camera, scale=-1)

        self.ip = self.mvp.projection()
        self.ip.invert()

        self.projection = { "camera":      camera[:],
                            "orientation": orientation,
                            "xfov": xfov,
                            "yfov": yfov,
                            "z_of_w_1":z_of_w_1[2]
                            }

        if resultant_projection is not None:
            resultant_projection["camera"]      = camera[:]
            resultant_projection["orientation"] = orientation.copy()
            resultant_projection["xfov"]        = xfov
            resultant_projection["yfov"]        = yfov
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
    def image_of_model(self,xyz, perspective=True):
        if self.mvp is None:
            return None
        xyzw = self.mvp.apply(xyz, perspective=perspective)
        img_xy = ((1.0+xyzw[0])/2.0*self.size[0], (1.0-xyzw[1])/2.0*self.size[1])
        return (xyzw,img_xy)
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
    #f error_of_rotation
    def error_of_rotation(self, R, verbose=False):
        # Rotations have a single eigenvalue - it should be 1, but that is less critical than the volume and lengths of R
        # Prune out any clearly non-rotations with number of eigenvalues though
        eigenvalues = R.eigenvalues()
        if len(eigenvalues)>1:
            if verbose:
                print "R has three eigenvalues"
                pass
            return None

        # The rotation MUST be a right-handed set of vectors, else we are in some wonky space
        # Also the volume of the unit cube should remain 1 for a pure rotation
        v = (R.get_column(0),R.get_column(1),R.get_column(2))
        volume_r  = vectors.dot_product(vectors.vector_prod3(v[0],v[1]),v[2])
        if (volume_r<0):
            if verbose:
                print "Volume of rotated cube negative"
                pass
            return None

        # If the volume is 1 then the unit cube could have been stretched in X and squashed in Y, for example
        # Make sure the scalings along each vector approach 1.0
        lengths_r = (vectors.dot_product(v[0],v[0]), vectors.dot_product(v[1],v[1]), vectors.dot_product(v[2],v[2]))
        def NO(x, epsilon=1E-9):
            #return math.pow(x,5.0)-1
            if (x>1): return x-1
            if (x>1E-9): return 1/x-1
            return 1E9
        def sum_sq(xs):
            v = 0
            for x in xs:
                v += x*x
                pass
            return v
        v = (R.get_row(0),R.get_row(1),R.get_row(2))
        lengths_c = (vectors.dot_product(v[0],v[0]), vectors.dot_product(v[1],v[1]), vectors.dot_product(v[2],v[2]))

        # Error term is sum of squares of x-1 (or 1/x-1 if x<1) so each counts the same
        # Note that the eigenvalue should also approach 1, but adding it in does not really change things much
        error = sum_sq((NO(volume_r), NO(lengths_r[0]), NO(lengths_r[1]), NO(lengths_r[2]), NO(lengths_c[0]), NO(lengths_c[1]), NO(lengths_c[2])))
        if verbose:
            print "Error %6f Volume %6f == +1, lengths %s, eigen %6f"%(error, volume_r, str(lengths_c), eigenvalues[0])
        return (error, volume_r, lengths_r, lengths_c, eigenvalues[0])
    #f error_of_Z
    def error_of_Z(self, O, Pe, U, uv, Zs, verbose=False):
        for c in range(4):
            (_, _, z, w) = Pe.apply( (0.0,0.0,Zs[c],1.0) )
            U[0,c] = w * uv[c][0]
            U[1,c] = w * uv[c][1]
            U[2,c] = z
            U[3,c] = w
            pass

        U_i = U.inverse()
        if U_i is None:
            if verbose:
                print "U was singular"
                pass
            return None

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
        for c in range(4):
            if vectors.vector_separation(O.get_column(c)[:3],camera)*1.1 < -Zs[c]:
                if verbose:
                    print "Camera did not meet Zs"
                    pass
                return None
            pass

        # Rotations have a single eigenvalue - it should be 1, but that is less critical than the volume and lengths of R
        # Prune out any clearly non-rotations with number of eigenvalues though
        eigenvalues = R.eigenvalues()
        if len(eigenvalues)>1:
            if verbose:
                print "R has three eigenvalues"
                pass
            return None

        # The rotation MUST be a right-handed set of vectors, else we are in some wonky space
        # Also the volume of the unit cube should remain 1 for a pure rotation
        v = (R.get_column(0),R.get_column(1),R.get_column(2))
        volume_r  = vectors.dot_product(vectors.vector_prod3(v[0],v[1]),v[2])
        if (volume_r<0):
            if verbose:
                print "Volume of rotated cube negative"
                pass
            return None

        # If the volume is 1 then the unit cube could have been stretched in X and squashed in Y, for example
        # Make sure the scalings along each vector approach 1.0
        lengths_r = (vectors.dot_product(v[0],v[0]), vectors.dot_product(v[1],v[1]), vectors.dot_product(v[2],v[2]))
        def NO(x, epsilon=1E-9):
            #return math.pow(x,5.0)-1
            if (x>1): return x-1
            if (x>1E-9): return 1/x-1
            return 1E9
        def sum_sq(xs):
            v = 0
            for x in xs:
                v += x*x
                pass
            return v
        v = (R.get_row(0),R.get_row(1),R.get_row(2))
        lengths_c = (vectors.dot_product(v[0],v[0]), vectors.dot_product(v[1],v[1]), vectors.dot_product(v[2],v[2]))

        # Error term is sum of squares of x-1 (or 1/x-1 if x<1) so each counts the same
        # Note that the eigenvalue should also approach 1, but adding it in does not really change things much
        error = sum_sq((NO(volume_r), NO(lengths_r[0]), NO(lengths_r[1]), NO(lengths_r[2]), NO(lengths_c[0]), NO(lengths_c[1]), NO(lengths_c[2])))
        if verbose:
            print "Error %6f Volume %6f == +1, lengths %s, eigen %6f, cam [%5f,%5f,%5f]"%(error, volume_r, str(lengths_c), eigenvalues[0], camera[0],camera[1],camera[2])

        return (error, camera, R, volume_r, lengths_r, lengths_c, eigenvalues)
    #f select_best_Z_set
    def select_best_Z_set(self, O, Pe, uv, guess_Z, max_results=20, verbose=False):
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
        last_report = "No results found"
        U = matrix.c_matrixNxN(order=4)
        for Zk in guess_Z:
            Z_list    = guess_Z[Zk]
            error = self.error_of_Z(O=O, Pe=Pe, U=U, uv=uv, Zs=Z_list)
            if error is None:
                continue

            (error, camera, R, volume_r, lengths_r, lengths_c, eigenvalues) = error
            if (error<1E9):
                if (len(result_list)<max_results) or (error<result_list[-1][0]):
                    orientation = quaternion.c_quaternion().from_matrix(R.transpose())
                    r = (Zk, camera, orientation)
                    last_report = "%s:Error %6f Volume %6f == +1, lengths %s, eigen %6f, cam [%5f,%5f,%5f]"%(str(Zk),error, volume_r, str(lengths_c), eigenvalues[0], camera[0],camera[1],camera[2])
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
        print last_report
        return result_list
    #f calculate_det_Zs
    def calculate_det_Zs(self, projection, pt_names, object_guess_locations, image_locations):
        """
        Calculate det|U.Z.O-1| = |U|.|Z|.|O-1|
        and a projection camera, aspect, FOV

        We know that R.O = U.Z (where Z = (za,0,0, 0,zb,0, 0,0,zc))
        We also know that R has a determinant of 1
        We can also deduce that R.O.U' = Z, hence |R|.|O|.|U'| = |Z|
        But |Z| is za.zb.zc, which is useful (?)
        """
        #b Create O and U matrices
        camera = projection["camera"]
        fovx = projection["xfov"]
        fovy = projection["yfov"]

        xscale = math.tan(fovx/360.0*3.14159256)
        yscale = math.tan(fovy/360.0*3.14159256)

        O = matrix.c_matrixNxN(order=3)
        U = matrix.c_matrixNxN(order=3)
        for c in range(3):
            pt = pt_names[c]
            obj = vectors.vector_add(object_guess_locations[pt], camera, scale=-1.0)
            O[0,c] = obj[0]
            O[1,c] = obj[1]
            O[2,c] = obj[2]
            u = -1.0 + (image_locations[pt][0]/self.size[0])*2.0
            v =  1.0 - (image_locations[pt][1]/self.size[1])*2.0
            U[0,c] = u*xscale
            U[1,c] = v*yscale
            U[2,c] = -1.0
            pass
        det_Z = O.determinant() / U.determinant()
        return det_Z
    #f calculate_R
    def calculate_R(self, projection, pt_names, object_guess_locations, image_locations, Zs):
        """
        Calculate R from object and image locations and Zs
        and a projection camera, aspect, FOV

        We know that R.O = U.Z (where Z = (za,0,0, 0,zb,0, 0,0,zc))
        Hence R = U.Z.O'
        """
        #b Create O and U.Z matrices
        camera = projection["camera"]
        fovx = projection["xfov"]
        fovy = projection["yfov"]

        xscale = math.tan(fovx/360.0*3.14159256)
        yscale = math.tan(fovy/360.0*3.14159256)

        O = matrix.c_matrixNxN(order=3)
        U = matrix.c_matrixNxN(order=3)
        for c in range(3):
            pt = pt_names[c]
            obj = vectors.vector_add(object_guess_locations[pt], camera, scale=-1.0)
            O[0,c] = obj[0]
            O[1,c] = obj[1]
            O[2,c] = obj[2]
            u = -1.0 + (image_locations[pt][0]/self.size[0])*2.0
            v =  1.0 - (image_locations[pt][1]/self.size[1])*2.0
            U[0,c] = u*xscale*Zs[c]
            U[1,c] = v*yscale*Zs[c]
            U[2,c] = -1.0*Zs[c]
            pass

        O_i = O.inverse()
        return U.postmult(O_i)
    #f improve_projection
    def improve_projection(self, O, Pe, uv, guess_Z, coarseness, initial_max_error=1E9, verbose=False):
        """
        O = object matrix (4x4, columns are object x,y,z,1)
        Pe = perspective matrix (1/f, 1/f.aspect, zfar/znear, -1...)
        uv = [(u,v)] * 4
        guess_Z = base four MVP.xyz Z values to spread around
        """
        base_guess_Z = guess_Z

        guess_Z = {}
        for gi in range(7*7*7*7):

            gi2 = gi

            gZ = []
            for c in range(4):
                ci = (gi2 % 7)
                gi2 = gi2 / 7
                gZ.append(base_guess_Z[c]*math.pow(coarseness,(ci-3)))
                pass
            guess_Z[gi] = gZ
            pass
        r = self.select_best_Z_set(O=O, Pe=Pe, uv=uv, guess_Z=guess_Z, max_results=1, verbose=False)
        if r is None:
            return None
        (error, (gi, camera, orientation)) = r[0]
        return ({"camera":camera, "orientation":orientation}, guess_Z[gi], error)
    #f improve_projection_differentially
    def improve_projection_differentially(self, O, Pe, uv, guess_Z, delta=1E-3, verbose=False):
        """
        O = object matrix (4x4, columns are object x,y,z,1)
        Pe = perspective matrix (1/f, 1/f.aspect, zfar/znear, -1...)
        uv = [(u,v)] * 4
        guess_Z = base four MVP.xyz Z values to spread around

        If one does dE/dZc for each of the four c then this is not representative - i.e.
        you cannot change one Zc without impacting more than one
        Hence 
        """
        errors = {}
        U = matrix.c_matrixNxN(order=4)
        errors[0] = self.error_of_Z(O=O, Pe=Pe, U=U, uv=uv, Zs=guess_Z, verbose=False)
        if errors[0] is None:
            print "Error for base Zs is None",guess_Z
            return None

        #print "-"*80
        #print errors[0]
        for c in range(4):
            for dirn in (-1,1):
                Zs = guess_Z[:]
                Zs[c] = Zs[c] + delta*dirn
                #print (c,dirn), Zs
                error = self.error_of_Z(O=O, Pe=Pe, U=U, uv=uv, Zs=Zs, verbose=False)
                #print error
                if error is None:
                    error = 10000
                    pass
                errors[(c,dirn)] = error
                pass
            pass

        # error_of_Z yields (error, camera, R, volume_r, lengths_r, lengths_c, eigenvalues)
        chosen_errors = []
        total_delta_error = 0
        for c in range(4):
            e_m = errors[0][0] - errors[(c,-1)][0]
            e_p = errors[0][0] - errors[(c, 1)][0]
            if verbose:
                print c, e_m, e_p
                pass
            if e_m<0 and e_p<0: continue
            if e_m>0 and e_p>0: continue
            if e_p>0:
                chosen_errors.append( (c,1,e_p) )
                total_delta_error += e_p
                pass
            else:
                chosen_errors.append( (c,-1,e_m) )
                total_delta_error += e_m
                pass
            pass

        if verbose:
            print "Total delta error", total_delta_error
            pass
        if total_delta_error==0:
            return None

        # delta (1E-4 ) yields an error change of e for a direction
        # out of a total error change of total_delta_error
        # So to achieve a total error change of total_delta_error one can _assume_
        # that one must move by delta in that direction
        # To achieve a total error change of errors[0][0] then one might _assume_
        # that one needs to move by delta*errors[0][0]/total_delta_error
        # However, this would mean having to move by a fixed direction
        step_size = 1.5 * delta * errors[0][0] / total_delta_error
        print errors[0][0], total_delta_error, delta, step_size, guess_Z
        while True:
            step_size = step_size/2.0
            if step_size<1E-15:
                if verbose:
                    print "Had no benefit"
                    pass
                return None
            Zs = guess_Z[:]
            for (c,d,e) in chosen_errors:
                Zs[c] = guess_Z[c] + d*step_size * e/total_delta_error
                pass

            if verbose:
                print "Error",errors[0]
                print "Using step size of",step_size
                print "Chosen errors",chosen_errors
                print "Zs",Zs
                print "guess_Z",guess_Z
                pass

            r = self.error_of_Z(O=O, Pe=Pe, U=U, uv=uv, Zs=Zs, verbose=True)
            if r is None:
                print "Got error of none for Zs",Zs
                continue
            (error, camera, R, volume_r, lengths_r, lengths_c, eigenvalues) = r
            if verbose:
                print "Differential to",r
                pass
            if error<errors[0][0]:
                break
            pass
        print error, step_size
        orientation   = quaternion.c_quaternion().from_matrix(R.transpose())
        return ({"camera":camera, "orientation":orientation}, Zs, error)
    #f get_best_projection_for_guess_Z
    def get_best_projection_for_guess_Z(self, O, Pe, uv, guess_Z, spread=1.15, iterations=5):
        """
        O = object matrix (4x4, columns are object x,y,z,1)
        Pe = perspective matrix (1/f, 1/f.aspect, zfar/znear, -1...)
        uv = [(u,v)] * 4
        guess_Z = base four MVP.xyz Z values to spread around
        """
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
    #f generate_uniform_Z_set_ijkl
    def generate_uniform_Z_set_ijkl(self, n=10, base=1.0, step=1.7):
        """
        Generate a uniform set of Z values for i,j,k,l in 0..n-1
        where Z = -(base + step*i)
        """
        print "Generating uniform Z set",n,base,step
        guess_Z = {}
        # The range we need has got to cover the camera position
        # For img_1 we used 0, -1.7, ... -17
        # For left  we used -10, -12.5, -15.0, ... -35
        #Since this is early doors we can use a big range.
        # However, an exponential range may be too much - is linear too small?
        # Change from 11 n to 20 n
        # That means range is now -10 to -60, which is not enough for the pencil image right
        # So going to scale it up
        # Using n=7 for speed for selecting best camera line
        for i in range(n*n*n*n):
            ijkl = (i%n, (i/n)%n, (i/n/n%n), (i/n/n/n%n))
            zs = []
            for c in range(4):
                zs.append( -(base + ijkl[c]*step) )
                pass
            guess_Z[ijkl] = zs
            pass
        return guess_Z
    #f find_best_camera_choices
    def find_best_camera_choices(self, z_set_results, cos_angle=0.90):
        """
        Find the n*(n-1)/2 set of normalized camera vectors
        (directions between every pair of cameras for z_set_results)
        Dot product each pair of these and discard the second of any
        whose dot product indicates a cos angle between them > cos_angle
        Sort 
        """
        #b camera_deltas = list of (vector, [(ijkl,ijkl)*); camera_deltas_per_ijkl[ijkl]=r
        camera_deltas = []
        camera_deltas_per_ijkl = {}
        for r in z_set_results:
            (_, (ijkl, camera, _)) = r
            camera_deltas_per_ijkl[ijkl] = r
            for r2 in z_set_results:
                (_, (ijkl2, camera2, _)) = r2
                if ijkl != ijkl2:
                    dc = vectors.vector_add(camera, camera2, scale=-1.0)
                    l = vectors.vector_length(dc)
                    if l>0.01:
                        camera_deltas.append( (vectors.vector_scale(dc,1/l),[(ijkl,ijkl2)] ) )
                        pass
                    pass
                pass
            pass

        #b Merge camera_delta entries where two vectors dot product to > cos_angle
        i = 0
        while i<len(camera_deltas):
            dc_i = camera_deltas[i]
            j = i+1
            while j<len(camera_deltas):
                dc_j = camera_deltas[j]
                d = vectors.dot_product(dc_i[0], dc_j[0])
                if d<0: d=-d
                if (d>cos_angle):
                    j = j+1
                    continue
                dc_i[1].extend(dc_j[1])
                camera_deltas.pop(j)
                pass
            i = i+1
            pass

        #b best_camera_deltas = For each camera_delta select the ijkl in its list with lowest error
        best_camera_deltas = {}
        for dc in camera_deltas:
            (vector,pairs) = dc
            smallest_error = (None,None)
            for ijkl_pair in pairs:
                for ijkl in ijkl_pair:
                    (error, _) = camera_deltas_per_ijkl[ijkl]
                    if smallest_error is None or error<smallest_error:
                        smallest_error = (error, ijkl)
                        pass
                    pass
                pass
            best_camera_deltas[ijkl] = (error, vector)
            pass

        #b Sort best_camera_deltas by error into best_camera_choices
        best_camera_choices = []
        for ijkl in best_camera_deltas:
            (e,v) = best_camera_deltas[ijkl]
            best_camera_choices.append((e,ijkl,v))
            pass
        def cmp_camera_choices(x,y):
            if x[0]<y[0]: return -1
            return 1
        best_camera_choices.sort(cmp=cmp_camera_choices)
        return best_camera_choices
    #f find_R_Zs_from_camera
    def find_R_Zs_from_camera(self, projection, pt_names, object_guess_locations, image_locations):
        a = self.calculate_det_Zs(projection, (pt_names[0], pt_names[1], pt_names[2]), object_guess_locations, image_locations)
        b = self.calculate_det_Zs(projection, (pt_names[0], pt_names[1], pt_names[3]), object_guess_locations, image_locations)
        c = self.calculate_det_Zs(projection, (pt_names[0], pt_names[2], pt_names[3]), object_guess_locations, image_locations)
        d = self.calculate_det_Zs(projection, (pt_names[1], pt_names[2], pt_names[3]), object_guess_locations, image_locations)
        p = a*b*c*d
        if p<0: p=-p
        p = math.pow(p,1/3.0)
        w = p/d
        x = p/c
        y = p/b
        z = p/a
        Zs = (w,x,y,z)
        #print Zs
        R = self.calculate_R(projection, pt_names, object_guess_locations, image_locations, Zs)
        return (R, Zs)
    #f report_point_errors
    def report_point_errors(self, points, image_locations):
        pts = points.keys()
        pts.sort()
        sum_d = 0
        for k in pts:
            (xyzw,uv) = self.image_of_model(points[k])
            d = vectors.vector_separation(uv,image_locations[k])
            sum_d += d
            print k, d, uv, image_locations[k]
            pass
        print "Total error",sum_d
        pass
    #f optimize_camera
    def optimize_camera(self, point_mappings, verbose=True):
        print "Camera before optimization"
        print self.projection["camera"]
        projection = {"xfov":self.projection["xfov"],
                      "yfov":self.projection["yfov"],
                      }
        (object_guess_locations, image_locations) = self.get_object_and_image_locations(point_mappings)
        pt_names = object_guess_locations.keys()
        dirns = []
        for i in (-1,0,1):
            for j in (-1,0,1):
                for k in (-1,0,1):
                    if (i==0) and (j==0) and (k==0): continue
                    dirns.append(vectors.vector_normalize((i,j,k)))
                    pass
                pass
            pass
        print object_guess_locations
        print image_locations
        print projection
        base_camera = self.projection["camera"]
        for i in range(50):
            print "-"*80
            print "Iteration",i,math.pow(0.8,i)
            for j in range(100):
                smallest_error = (1E9,None)
                first_v = True
                for v in dirns:
                    for scale in [0, 1, 2]:
                        if not first_v and (scale==0): continue
                        first_v = False
                        camera = vectors.vector_add(base_camera,v,scale=scale*math.pow(0.8,i))
                        projection["camera"] = camera
                        R,Zs = self.find_R_Zs_from_camera(projection, pt_names, object_guess_locations, image_locations)
                        error = self.error_of_rotation(R, verbose=False)
                        if error is not None and error[0]<smallest_error[0]:
                            #(error, volume_r, lengths_r, lengths_c, eigenvalues[0]) = error
                            smallest_error = (error[0], R, Zs, v, scale, camera)
                            print error[0], camera, v, scale
                            pass
                        pass
                    pass
                (error,R,Zs,v,scale,camera) = smallest_error
                if scale==0:
                    break
                base_camera = camera
                pass
            pass
        orientation = quaternion.c_quaternion().from_matrix(R)
        projection["camera"] = base_camera
        projection["orientation"] = orientation
        self.set_projection(projection)
        print "Cameras after blah"
        print base_camera
        print self.projection["camera"]
        self.report_point_errors(object_guess_locations, image_locations)
        pass
    #f get_object_and_image_locations
    def get_object_and_image_locations(self, point_mappings):
        """
        Find a tuple of object_guess_locations and image_locations from point_mappings
        for this image

        object_guess_locations and image_locations are dictionaries of point_name->tuple

        The dictionaries will have the same set of point_name keys
        """
        object_guess_locations = {}
        for pt in point_mappings.object_guess_locations:
            if pt in point_mappings.image_mappings:
                object_guess_locations[pt] = point_mappings.object_guess_locations[pt]
                pass
            pass

        image_locations = {}
        pt_names = object_guess_locations.keys()
        for pt in pt_names:
            if self.name in point_mappings.image_mappings[pt]:
                image_locations[pt] = point_mappings.image_mappings[pt][self.name]
                pass
            else:
                del(object_guess_locations[pt])
                pass
            pass

        return (object_guess_locations, image_locations)
    #f guess_initial_projection_matrix
    def guess_initial_projection_matrix(self, point_mappings ):
        #b Find object_guess_locations and image_locations to use
        # iphone 6s has XFOV of about 55, YFOV is therefore about 47
        # FOV is currently not critical though - 55-63 is a good range...
        # Wired says iphone6 has xFOV of 63.54
        # That makes yFOV of 49.83
        projection = {"xfov":63.54,
                      "yfov":49.83,
                      }
        (object_guess_locations, image_locations) = self.get_object_and_image_locations(point_mappings)

        if len(image_locations)!=4:
            print "Require 4 object guess locations with image locations for initial projection matrix"
            return None

        #b Create O and Pe matrices and uv list
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

        Pe = self.pe_matrix_of_projection(projection)

        #b Generate initial guesses for Z and run them
        #guess_Z = self.generate_uniform_Z_set_ijkl(n=20, base=2.0, step=2.5)
        guess_Z = self.generate_uniform_Z_set_ijkl(n=7, base=0.0, step=5.0)
        z_set_results = self.select_best_Z_set(O, Pe, uv, guess_Z, max_results=125)

        #b Find best camera choices from results and hence best Z guesses to optimize
        cos_angle = 0.99 # This means the cameras are in line by arccos(0.99), or 8 degrees
        cos_angle = 0.95 # This means the cameras are in line by arccos(0.95), or 18 degrees
        cos_angle = 0.90  # This means the cameras are in line by arccos(0.9), or 25 degrees
        best_camera_choices = self.find_best_camera_choices(z_set_results, cos_angle=cos_angle)

        print "Best Z guesses"
        best_zs_guesses = []
        for (e,ijkl,v) in best_camera_choices:
            print e,ijkl,v,guess_Z[ijkl]
            best_zs_guesses.append(guess_Z[ijkl])
            if len(best_zs_guesses)>15:
                break
            pass

        #b Optimize the first 5 best Z guesses to get the best of them
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
                if len(best_zs_results)>5:
                    break
                pass
            pass

        def cmp_results(a,b):
            if a[2]<b[2]: return -1
            return 1

        best_zs_results.sort(cmp=cmp_results)

        #b Optimize the best optimized Zs results
        for (proj,gZ,error) in best_zs_results:
            print "-"*80
            print "Final optimizing",gZ
            r = self.get_best_projection_for_guess_Z(O, Pe, uv, gZ, spread=math.pow(1.05,1/(1.5*(5-1))), iterations=35)
            if r is None:
                continue
            print r
            (improved_projection, improved_z, max_error) = r
            improved_projection = {"camera":improved_projection["camera"],
                                   "orientation":improved_projection["orientation"],
                                   "xfov":projection["xfov"],
                                   "yfov":projection["yfov"],
                                   }
            break

        #b Set projection and report on the net error
        projection = improved_projection
        print "-"*80
        print "Optimized:\nself.images['%s']['projection'] = %s"%(self.name,str(projection))
        self.set_projection(projection)

        self.report_point_errors(object_guess_locations, image_locations)

        #b Done
        return
    #f pe_matrix_of_projection
    def pe_matrix_of_projection(self, projection=None):
        if projection is None:
            projection = self.projection
            pass

        xfov   = projection["xfov"]
        yfov   = projection["yfov"]
        zFar   = 40.0
        zNear  = 1.0
        Pe = matrix.c_matrixNxN(data=[0.0]*16)
        fx = 1.0/math.tan(xfov*3.14159265/180.0/2)
        fy = 1.0/math.tan(yfov*3.14159265/180.0/2)
        Pe[0,0] = fx
        Pe[1,1] = fy
        Pe[2,2] = -(zNear+zFar)/(zFar-zNear)
        Pe[2,3] = -2*zNear*zFar/(zFar-zNear)
        Pe[3,2] = -1.0
        return Pe
    #f calculate_map_and_errors
    def calculate_map_and_errors(self, point_mappings, display=False):
        result = []
        pt_names = point_mappings.get_mapping_names()
        pt_names.sort()
        for pt in pt_names:
            xyz = point_mappings.get_xyz(pt)
            if xyz is None:
                continue
            (xyzw, img_xy) = self.image_of_model(xyz, perspective=False)
            uv = (xyzw[0]/xyzw[3], xyzw[1]/xyzw[3])
            mapping_uv = point_mappings.get_xy(pt,self.name)
            dist = None
            if mapping_uv is not None:
                dist = vectors.vector_separation(mapping_uv, uv)
                pass
            result.append((pt, {"uv":uv, "xyz":xyz, "xyzw":xyzw, "map_uv":mapping_uv, "error":dist}))
            pass

        if display:
            print "Results from calculate_map_and_errors for",self.name
            total_error = 0
            total_pts = 0
            for d in result:
                print d
                if d[1] is not None and d[1]["error"] is not None:
                    total_error += d[1]["error"]
                    total_pts += 1
                    pass
                pass
            if total_pts>0:
                print "Total error %6f for %d points average %6f"%(total_error,total_pts,total_error/total_pts)
                pass
            pass

        return result
    #f improve_projection_from_point_data
    def improve_projection_from_point_data(self, pt_data, spread=1.15, iterations=5):
        """
        pt_data is list (pt_name, data_dict)
        data_dict has keys 'uv', 'xyz'
        """
        Pe = self.pe_matrix_of_projection()
        O  = matrix.c_matrixNxN(order=4)
        uv = []
        guess_Z = []
        for c in range(4):
            d = pt_data[c][1]
            O[0,c] = d["xyz"][0]
            O[1,c] = d["xyz"][1]
            O[2,c] = d["xyz"][2]
            O[3,c] = 1.0
            uv.append(d["map_uv"])
            #guess_Z.append(d["xyzw"][2])
            guess_Z.append(-d["xyzw"][3]) # Should this be 2 or 3
            pass
        r = self.get_best_projection_for_guess_Z(O=O, Pe=Pe, uv=uv, guess_Z=guess_Z, spread=spread, iterations=iterations)
        if r is None:
            print "FAILED"
            return
        (improved_projection, improved_z, max_error) = r
        print improved_projection, improved_z, max_error
        improved_projection = {"camera":improved_projection["camera"],
                               "orientation":improved_projection["orientation"],
                               "xfov":self.projection["xfov"],
                               "yfov":self.projection["yfov"],
                               }
        print "Setting projection to",improved_projection
        self.set_projection(improved_projection)
        return
    #f improve_projection_from_point_data_differentially
    def improve_projection_from_point_data_differentially(self, pt_data):
        """
        pt_data is list (pt_name, data_dict), from 'calculate_map_and_errors'
        data_dict has keys 'uv', 'xyz'
        """
        Pe = self.pe_matrix_of_projection()
        O  = matrix.c_matrixNxN(order=4)
        uv = []
        guess_Z = []
        for c in range(4):
            d = pt_data[c][1]
            O[0,c] = d["xyz"][0]
            O[1,c] = d["xyz"][1]
            O[2,c] = d["xyz"][2]
            O[3,c] = 1.0
            uv.append(d["map_uv"])
            guess_Z.append(-d["xyzw"][3]) # Should this be d["xyzw"][2] or -d["xyzw"][3]?
            #guess_Z.append(d["xyzw"][2]) # Should this be d["xyzw"][2] or -d["xyzw"][3]?
            pass

        print "Pt_data"
        print pt_data
        improved_projection = None
        for i in range(500):
            print "Iteration",i
            r = self.improve_projection_differentially(O=O, Pe=Pe, uv=uv, guess_Z=guess_Z, verbose=False)
            if r is None:
                break
            (improved_projection, improved_z, max_error) = r
            #print improved_projection, improved_z, max_error
            guess_Z = improved_z
            pass
        if improved_projection is None:
            print "FAILED"            
            return
        improved_projection = {"camera":improved_projection["camera"],
                               "orientation":improved_projection["orientation"],
                               "xfov":self.projection["xfov"],
                               "yfov":self.projection["yfov"],
                               }
        print "Setting projection to",improved_projection
        self.set_projection(improved_projection)
        return
    #f optimize_projection_from_select_points
    def optimize_projection_from_select_points(self, point_mappings, use_corners=True, differentially=True):
        best_pts = [None, None, None, None]
        mae = self.calculate_map_and_errors(point_mappings, display=True)
        if use_corners:
            for d in mae:
                xy = (d[1]["uv"][0], d[1]["uv"][1]) # Use 'uv' or 'map_uv'?
                dbl = vectors.vector_separation((-1.0,-1.0),xy)
                dtl = vectors.vector_separation((-1.0, 1.0),xy)
                dbr = vectors.vector_separation(( 1.0,-1.0),xy)
                dtr = vectors.vector_separation(( 1.0, 1.0),xy)
                for (p, v) in ( (0,dbl), (1,dtl), (2,dbr), (3,dtr) ):
                    if best_pts[p] is None or v<best_pts[p][0]:
                        best_pts[p] = (v, d)
                    pass
                pass

            mae = []
            for (d,p) in best_pts:
                mae.append(p)
                print "Using corner point",p
                pass
            pass
        else:
            best_pts = []
            for d in mae:
                if d[0] in point_mappings.object_guess_locations:
                    best_pts.append(d)
                    pass
                pass
            mae = best_pts
            pass

        if differentially:
            self.improve_projection_from_point_data_differentially(mae)
            pass
        else:
            self.improve_projection_from_point_data(mae,spread=1.03, iterations=50)
            pass
        self.calculate_map_and_errors(point_mappings, display=True)
        return
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

        self.set_projection(opt_projection)
        opt_projection = self.optimize_projection(point_mappings = point_mappings,
                                                  fov_iterations=200, orientation_iterations=100, camera_iterations=10, delta_scale=0.03 )

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
