#!/usr/bin/env python
# PYTHONPATH=`pwd`/../python:$PYTHONPATH ./mapping.py

#a Documentation
"""
An image should have a 'viewed from' 3D point, a unit view direction, a unit 'up' vector
and two scale factors (one for x, one for y).
The unit view direction has 2 DOF; the up vector must be perpendicular to the view direction and so has 1 DOF
This is a total of 5 DOF plus the 3D view point.

Note that a glutPerspective has FOV, aspect, zNear, zFar, plus a translation. The zNear/zFar provide a scaling factor, hence 1DOF.
In fact, these four probably supply 2 DOF for the view.

We can treat the image as a projection of the model onto a clip plain, and this clip plane as having 3 axes with an origin at the center of the image:
1. the axis perpendicular to the image (Z), which has (at distance 1 on the axis) the 'center of the clip'
2. the axis for the 'left-right' of the clip plane (X) which at distance 1 is the right-hand center of the image
3. the axis for the 'up-down' of the clip plane (Y) which at distance 1 is the top center of the image

If we have a matrix and translation that converts from model to projection we have
Clip(obj) = P . (obj - T)
OR, inverting:
obj(Clip) = T + P'.Clip

Now we have defined:
Clip(viewed from)     = (0,0,0) -> T = viewed_from
Clip(center of image) = (0,0,1)
Clip(center-right-of-image) = (1,0,1)
Clip(center-top-of-image)   = (0,1,1)

For the "Main" image we can have a view_from as Obj(0,0,0) and image center as Obj(0,0,1), image right as Obj(1,0,1), etc
This means that Clip() = Obj() for "Main" image - i.e. P is the identity (perspective) matrix

From the "Main" image we can cast rays for each known image point in model space; if the point as at (x,y) in the image, then
it must be at (x,y,1) in clip space (since that is where the image lies), and hence the model point is in model space at
(kx,ky,k) for some unknown k

For non-Main image we can cast rays, and each model point will be on the line ViewFrom(img)+k*ViewVector(img,x,y)

Now for another image we will need to determine its model space view from point, its model space unit view direction, its model space view 'up' unit vector, and its two scaling factors (X and Y)

If we fully know a model space point (Mx,My,Mz) and we know its image (Ix,Iy) we have:
Clip(Mx,My,Mz) = (Ix.Iw,Iy.Iw,Iz.Iw,Iw) = [Pimg,Timg] . (Mx,My,Mz,1)


We could assume the image projections are all perfect, and then find model positions for each image point.
This would be done by creating a set of lines that each image point must lie on in model space.

We then want to find the model space point that has the least distance from all the lines.

Line_set(p) = For all image that have pt p [ ImgToModel(image,image_coords[image,p]) ]

One approach is to find the O(N^2) set of midpoints of 'closest points between 2 lines'
and do a reasonable average


We can also assume the model positions are all perfect, and adjust Pimg and Timg for an image such that the error in the image points is smallest


"""

#a Imports
import gjslib.graphics.obj
from gjslib.graphics import opengl_app, opengl_utils, opengl_mesh
import math
from OpenGL.GLUT import *
from OpenGL.GLU import *
from OpenGL.GL import *

from gjslib.math.quaternion import c_quaternion
from gjslib.math import matrix, vectors, statistics
from image_point_mapping import c_point_mapping
from image_projection import c_image_projection
from gjslib.graphics import opengl_obj

#a Class
#c c_plane
class c_plane(object):
    """
    A plane can be described as the set of points p satisfying
    p.n = k (p, n vectors, k scalar)

    This plane class provides for being given a set of (x,y,z) points
    that are approximately on a plane, which can then be coplanarized
    
    This process requires estimating some 'n' for the plane, and
    then averaging the normals, and generating a unit normal

    Then the value 'k' can be determined, again by averaging

    Then the points may be 'coplanarized'

    Also, an intersection between a line a + l.d (a, r vectors, l variable scalar)
    can be found with the plane.
    """
    normal_indices = {}
    normal_indices[3] = ( (0,1,2), )
    normal_indices[4] = ( (0,1,2), (0,1,3), (0,2,3), (1,2,3), )
    normal_indices[5] = ( (0,2,4), (1,3,0), (2,4,1), (3,0,2), (4,1,3) )
    normal_indices[6] = ( (0,2,4), (1,3,5), (0,1,2), (1,2,3), (2,3,4), (3,4,5), (4,5,0), (5,0,1) )
    normal_indices[6] = ( (0,2,4), (1,3,5) )
    #f __init__
    def __init__(self):
        self.xyz_list = []
        self.normal = None
        self.k = None
        pass
    #f invalid
    def invalid(self):
        if self.normal is None:
            return True
        if self.k is None:
            return True
        return False
    #f add_xyz
    def add_xyz(self, xyz, name=None):
        self.xyz_list.append((xyz,name))
        pass
    #f estimate_normals
    def estimate_normals(self, epsilon=1E-6):
        l = len(self.xyz_list)
        if l<3:
            return None
        n = []
        if l in self.normal_indices:
            n = self.normal_indices[l]
            pass
        else:
            # Choose k=(l/3)+1
            # l=7 -> k=3
            # Then 0,k,2k; 1,k+1,2k+1, etc up to k-1,...
            # for l=7 it is 0,3,6; 1,4,0; 2,5,1
            k = (l/3)+1
            for i in range(k):
                n.append( (i,(i+k)%l,(i+2*k)%l) )
                pass
            pass
        normals = []
        for (i,j,k) in n:
            vi = self.xyz_list[i][0]
            vj = self.xyz_list[j][0]
            vk = self.xyz_list[k][0]
            vij = (vj[0]-vi[0], vj[1]-vi[1], vj[2]-vi[2])
            vik = (vk[0]-vi[0], vk[1]-vi[1], vk[2]-vi[2])
            vij = vectors.vector_normalize(vij)
            vjk = vectors.vector_normalize(vik)
            n = (vij[1]*vik[2] - vij[2]*vik[1],
                 vij[2]*vik[0] - vij[0]*vik[2],
                 vij[0]*vik[1] - vij[1]*vik[0])
            ln = math.sqrt(n[0]*n[0] + n[1]*n[1] + n[2]*n[2])
            if (ln<0.7):
                print "Dont like normal",(i,j,k)
                continue
            if (ln<epsilon):
                n = (0.0,0.0,0.0)
                pass
            else:
                n = (n[0]/ln, n[1]/ln, n[2]/ln)
                pass
            if len(normals)>0:
                nn0 = (normals[0][1][0]*n[0] + 
                       normals[0][1][1]*n[1] + 
                       normals[0][1][2]*n[2])
                if nn0<0:
                    n = (-n[0], -n[1], -n[2])
                    pass
                pass
            normals.append(((i,j,k),n))
            pass
        return normals
    #f average_normal
    def average_normal(self, normals, epsilon=1E-6):
        if len(normals)==0:
            return None
        normal = (0.0,0.0,0.0)
        for (ijk,n) in normals:
            normal = (normal[0]+n[0], normal[1]+n[1], normal[2]+n[2])
            pass
        normal = (normal[0]/len(normals), normal[1]/len(normals), normal[2]/len(normals))
        ln = math.sqrt(normal[0]*normal[0] + normal[1]*normal[1] + normal[2]*normal[2])
        if (ln<epsilon):
            normal = None
            pass
        else:
            normal = (normal[0]/ln, normal[1]/ln, normal[2]/ln)
            pass
        return normal
    #f average_k
    def average_k(self, normal, epsilon=1E-6):
        if normal is None:
            return None
        k = 0.0
        n = 0
        for xyz in self.xyz_list:
            xyz = xyz[0]
            kdn = (xyz[0]*normal[0] + 
                   xyz[1]*normal[1] + 
                   xyz[2]*normal[2])
            if (kdn<-epsilon) or (kdn>epsilon): # xyz may be unknown (0.0,0.0,0.0)
                n+=1
                k += kdn
                pass
            pass
        if n==0: return None
        k = k / n
        return k
    #f verify_normals
    def verify_normals(self, normal, normals, error_margin=0.1):
        for (ijk,n) in normals:
            nn = ( n[0]*normal[0] +
                   n[1]*normal[1] +
                   n[2]*normal[2])
            if nn<1.0-error_margin:
                pts = (self.xyz_list[ijk[0]][1],
                       self.xyz_list[ijk[1]][1],
                       self.xyz_list[ijk[2]][1])
                       
                print "Large error in normal",nn,pts
                pass
            pass
        pass
    #f generate_plane
    def generate_plane(self, epsilon=1E-6):
        self.normal = None
        self.k = None
        normals = self.estimate_normals(epsilon=epsilon)
        if normals is None:
            return
        normal = self.average_normal(normals,epsilon=epsilon)
        self.verify_normals(normal, normals)
        k = self.average_k(normal, epsilon=epsilon)
        self.normal = normal
        self.k = k
        pass
    #f coplanarize_xyz
    def coplanarize_xyz(self, xyz, name=None, errors=None ):
        """
        Every point in the plane is p.n=k
        If a point is p'=(p+l*n), as it has a perpendicular error of 'l', then
        p'.n = (p+l*n).n = p.n+l*n.n = k + l => l = p'.n - k,
        and a 'coplanarized point' is p' - l*n
        (Note n is a unit vector)
        """
        l = ( xyz[0]*self.normal[0] + 
              xyz[1]*self.normal[1] + 
              xyz[2]*self.normal[2]) - self.k
        xyz = (xyz[0] - l*self.normal[0],
               xyz[1] - l*self.normal[1],                   
               xyz[2] - l*self.normal[2])
        if errors is not None:
            if "total_sq" not in errors:
                errors["total_sq"] = 0
                errors["num_pts"] = 1
                errors["pts"] = {}
                pass
            if name is None: name=str(xyz)
            errors["pts"][name] = l
            errors["total_sq"] += l*l
            errors["num_pts"] += 1
            pass
        return xyz
    #f coplanarize
    def coplanarize(self, errors=None):
        if self.normal is None:
            return
        if self.k is None:
            return
        for i in range(len(self.xyz_list)):
            self.xyz_list[i][0] = self.coplanarize_xyz(self.xyz_list[i][0],errors)
            pass
        pass
    #f line_intersect
    def line_intersect(self, p, d, epsilon=1E-6):
        """
        Find intersection of plane with line p + l*d

        Since all points p' on the plane have p'.n = k:
        (p + l*d).n = k => p.n + l*d.n = k => p.n + l(d.n) = k
        Hence l(d.n) = k - p.n => l = (k-p.n)/(d.n)
        """
        if self.normal is None:
            return None
        if self.k is None:
            return None
        kpn = self.k - ( p[0]*self.normal[0] + 
                         p[1]*self.normal[1] + 
                         p[2]*self.normal[2] )
        dn = (d[0]*self.normal[0] + 
              d[1]*self.normal[1] + 
              d[2]*self.normal[2])
        if (dn<-epsilon) or (dn>epsilon):
            l = kpn/dn
            p = (p[0] + l*d[0],
                 p[1] + l*d[1],
                 p[2] + l*d[2])
            pass
        return p
    #f All done
    pass

#a Mapping data
"""
lspike 0,1810
clk center 0,1275
rspkie 0,1502

clk cetner = 1275/1650 * spike height

450 on spkie approx 2.7m

Spikes at 10.86m off the ground
clock center at 8.4m off the groun
LDBL at about 4.5m left of center

spkies at 620.0/936*4.5
"""
faces = {}
faces["frontleft"]  = ("img_1",
                       ( ["tl",
                          "fl.cr1.bl", "fl.cr1.tl", "fl.cr1.tr", "fl.cr1.br",
                          "fl.cr2.bl", "fl.cr2.tl", "fl.cr2.tr", "fl.cr2.br",
                          "fl.cr3.bl", "fl.cr3.tl", "fl.cr3.tr", "fl.cr3.br",
                          "fl.cr4.bl", "fl.cr4.tl", "fl.cr4.tr", "fl.cr4.br",
                          "fl.cr5.bl", "fl.cr5.tl", "fl.cr5.tr", "fl.cr5.br",
                          "fl.cr6.bl", "fl.cr6.br", 
                          "fl.cr", "fl.crt","fl.crtr",
                          "fl.br", "bl",
                          ],
                         ["fl.win1.bl","fl.win1.br","fl.win1.tr","fl.win1.tl"],
                         ["fl.win2.bl","fl.win2.br","fl.win2.tr","fl.win2.tl"],
                         ["fl.win3.bl","fl.win3.br","fl.win3.tr","fl.win3.tl"],
                         ["fl.win4.bl","fl.win4.br","fl.win4.tr","fl.win4.tl"],
                         ["fl.win5.bl","fl.win5.br","fl.win5.tr","fl.win5.tl"],
                         ),
                       (
                         #"fl.win1.bl","fl.win1.br","fl.win1.tr","fl.win1.tl",
                         #"fl.win2.bl","fl.win2.br","fl.win2.tr","fl.win2.tl",
                         #"fl.win3.bl","fl.win3.br","fl.win3.tr","fl.win3.tl",
                         #"fl.win4.bl","fl.win4.br","fl.win4.tr","fl.win4.tl",
                         #"fl.win5.bl","fl.win5.br","fl.win5.tr","fl.win5.tl",
                         ), )
faces["frontright"] = ("img_1", (["tr", "br", "fr.bl", "fr.cl"],),() )
faces["clock"]      = ("img_1", (["clk.l1","clk.tl", "clk.mtr", "clk.mtl", "clk.tr", "clk.br", "clk.r1", "clk.bl"],),
                       ("clk.l2","clk.l3","clk.l4","clk.l5",
                        "clk.r2","clk.r3","clk.r4","clk.r5",
                        ))
faces["lspike.fl"]  = ("img_1", (["lspike.l", "lspike.t", "lspike.f"],), () )
faces["lspike.fr"]  = ("img_1", (["lspike.f", "lspike.t", "lspike.r"],), () )
faces["rspike.fl"]  = ("img_1", (["rspike.l", "rspike.t", "rspike.f"],), () )
faces["rspike.fr"]  = ("img_1", (["rspike.f", "rspike.t", "rspike.r"],), () )

faces["floor"]  = ("left", (["drflr.4", "drflr.3", "drflr.2", "drflr.1", "drflr.0",
                             #"flsq1.0", "flsq3.3", "flsq4.2", "flsq4.1", "flsq2.0",
                             "flsq5.0", "flsq5.1", "flsq6.0", "flsq6.1",
                             ],),
                   ("flsq1.0","flsq1.1","flsq1.2","flsq1.3",
                    "flsq2.0","flsq2.1","flsq2.2","flsq2.3",                    
                    "flsq3.0","flsq3.1","flsq3.2","flsq3.3",                    
                    "flsq4.0","flsq4.1","flsq4.2","flsq4.3",                    
                    #"flsq5.0","flsq5.1",
                    "flsq5.2","flsq5.3",                    
                    ))

#a c_opengl_image_projection
class c_opengl_image_projection(object):
    #f __init__
    def __init__(self, projection=None, **kwargs):
        self.texture = None
        self.object = None
        self.projection = projection
        pass
    #f load_texture
    def load_texture(self):
        if self.projection is None:
            return
        self.texture = opengl_utils.texture_from_png(self.projection.image_filename)
        self.object = opengl_obj.c_opengl_obj()
        self.object.add_rectangle( (-10.0,10.0,0.0), (20.0,0.0,0.0), (0.0,-20.0,0.0) )
        self.object.create_opengl_surface()
        pass
    #f display
    def display(self):
        if self.projection is None:
            return
        if self.projection.projection is None:
            return
        if False and self.texture is not None:
            glPushMatrix()
            glBindTexture(GL_TEXTURE_2D, self.texture)
            self.object.draw_opengl_surface()
            glPopMatrix()
            return

        glDisable(GL_TEXTURE_2D)
        glMaterialfv(GL_FRONT,GL_AMBIENT,[1.0,1.0,1.0,1.0])
        glColor3f(1.0, 1.0, 1.0)

        glPushMatrix()

        camera = self.projection.projection["camera"]
        glTranslate(camera[0],camera[1],camera[2])
        glutSolidCube(0.1)
        glLineWidth(1.0)
        glBegin(GL_LINES);
        m = self.projection.projection["orientation"].get_matrixn()
        v = vectors.vector_scale(m.get_row(2),40.0)
        glVertex3f(-v[0],-v[1],-v[2])
        glVertex3f(v[0],v[1],v[2])
        glEnd()

        glPopMatrix()
        glEnable(GL_TEXTURE_2D)
        pass
    pass

#a Useful functions
def point_on_plane(p0,p1,p2,k01,k02):
    # mp = p0 + k01.(p1-p0) + k02.(p2-p0)
    mp = vector.add(p0, p1, scale=k01 )
    mp = vector.add(mp, p2, scale=k02 )
    mp = vector.add(mp, p0, scale=(-k01-k02) )
    return mp

#a c_mapping
class c_mapping(opengl_app.c_opengl_camera_app):
    camera_deltas = [{"camera":(-0.1,0.0,0.0)},
                     {"camera":(+0.1,0.0,0.0)},
                     {"camera":(0.0,-0.1,0.0)},
                     {"camera":(0.0,+0.1,0.0)},
                     {"camera":(0.0,0.0,-0.1)},
                     {"camera":(0.0,0.0,+0.1)},
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
    #f __init__
    def __init__(self, point_map_filename, **kwargs):
        opengl_app.c_opengl_camera_app.__init__(self, **kwargs)
        self.first_pass = True
        self.mvp =  matrix.c_matrix4x4()
        self.point_mappings = c_point_mapping()
        self.image_projections = {}
        self.load_point_mapping(point_map_filename)
        self.image_names = self.point_mappings.get_images()
        self.image_names.sort()
        self.load_images()
        pass
    #f opengl_post_init
    def opengl_post_init(self):
        global image_mapping_data

        self.set_camera( camera=[0.0,10.0,-2.0],
                         orientation=c_quaternion.identity() )

        self.point_mappings.find_line_sets()
        self.point_mappings.approximate_positions()

        self.generate_faces()

        pass
    #f load_point_mapping
    def load_point_mapping(self, point_map_filename):
        self.point_mappings.reset()
        self.point_mappings.load_data(point_map_filename)
        pass
    #f load_images
    def load_images(self):
        for k in self.image_names:
            image_data = self.point_mappings.get_image_data(k)
            self.image_projections[k] = c_opengl_image_projection(name = k,
                                                                  image_filename = image_data["filename"],
                                                                  size           = image_data["size"],
                                                                  projection     = image_data["projection"])
            pass
        pass
    #f generate_faces
    def generate_faces(self, texture_image_name="left"): # was main for sidsussex
        global faces
        proj = self.image_projections[texture_image_name]
        proj.load_texture()
        self.meshes = []
        pts = {}
        def uv_from_image_xyz(xyz, proj=proj):
            (uvzw,img_xy) = proj.projection.image_of_model(xyz)
            uv = (0.5+uvzw[0]*0.5, 0.5-uvzw[1]*0.5)
            return uv
        for pt in self.point_mappings.get_mapping_names():
            xyz = self.point_mappings.get_approx_position(pt)
            if xyz is not None:
                uv = uv_from_image_xyz(xyz)
                if uv is not None:
                    pts[pt] = (uv, xyz)
                    pass
                pass
            pass
        for n in faces:
            plane = c_plane()
            errors = {}
            (img, contour_list, fill_points) = faces[n]
            ogm = opengl_mesh.c_opengl_textured_mesh()
            for c in contour_list:
                for pt in c:
                    if pt in pts:
                        plane.add_xyz(pts[pt][1], pt)
                        pass
                    pass
            for pt in fill_points:
                if pt in pts:
                    plane.add_xyz(pts[pt][1], pt)
                    pass
                pass
            plane.generate_plane()
            if plane.invalid():
                print "Abandon plane",n
                continue
            for c in contour_list:
                contour = []
                for pt in c:
                    if pt in pts:
                        xyz = plane.coplanarize_xyz(pts[pt][1],name=pt,errors=errors)
                        contour.append( (pts[pt][0], xyz, None) )
                        pass
                    pass
                ogm.add_contour(contour)
                pass
            for pt in fill_points:
                if pt in pts:
                    xyz = plane.coplanarize_xyz(pts[pt][1],name=pt,errors=errors)
                    ogm.add_point( pts[pt][0], xyz, None )
                    pass
                pass
            print "Plane",n,errors["total_sq"]/errors["num_pts"],errors["pts"]
            ogm.optimize()
            def xyz_from_image_uv(uv, proj=proj, plane=plane):
                (p,d) = proj.projection.model_line_for_image((-1.0+2.0*uv[0],1.0-2.0*uv[1]))
                xyz = plane.line_intersect(p,d)
                if xyz is None: return (0.0,0.0,0.0)
                return xyz
            ogm.create_opengl_surface(projection_callback=xyz_from_image_uv)
            self.meshes.append(ogm)
            pass
        pass
    #f display_image_faces
    def display_image_faces(self):
        global faces
        glPushMatrix()
        glEnable(GL_TEXTURE_2D)
        glMaterialfv(GL_FRONT,GL_AMBIENT,[1.0,1.0,1.0,1.0])
        #SIDSUSSEX proj = self.image_projections["img_1"]
        proj = self.image_projections["left"]
        if proj.texture is not None:
            glBindTexture(GL_TEXTURE_2D, proj.texture)
            pass
        for m in self.meshes:
            m.draw_opengl_surface()
            pass
        glDisable(GL_TEXTURE_2D)

        glMaterialfv(GL_FRONT,GL_AMBIENT,[1.0,1.0,1.0,1.0])
        glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)
        for m in self.meshes:
            m.draw_opengl_surface()
            pass
        glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)

        glPopMatrix()
        self.first_pass = False
        pass
    #f display_image_points
    def display_image_points(self):
        for n in self.point_mappings.get_mapping_names():
            xyz = self.point_mappings.get_approx_position(n)
            if xyz is not None:
                glPushMatrix()
                glMaterialfv(GL_FRONT,GL_AMBIENT,[1.0,0.3,0.3,1.0])
                glTranslate(xyz[0],xyz[1],xyz[2])
                glScale(0.03,0.03,0.03)
                glutSolidSphere(1,6,6)
                glPopMatrix()
                pass
            pass
        #for pt in ["clkcenter", "lspike", "rspike"]:
        for pt in ["rspike"]:
        #for pt in ["clkcenter", "lspike", "rspike", "belltl", "belltr"]:
            (r,g,b) = {"clkcenter":(1.0,0.3,1.0),
                   "rspike":(1.0,0.3,1.0),
                   "lspike":(1.0,0.3,1.0),
                   "belltl":(0.3,1.0,1.0),
                   "belltr":(0.3,1.0,1.0),}[pt]
            for k in self.image_projections:
                proj = self.image_projections[k]
                xy = self.point_mappings.get_xy(pt, k)
                if xy is not None:
                    (p0,d0) = proj.model_line_for_image(xy)
                    glMaterialfv(GL_FRONT,GL_AMBIENT,[r,g,b,1.0])
                    glLineWidth(2.0)
                    glBegin(GL_LINES);
                    glVertex3f(p0[0]+d0[0]*40.0,
                               p0[1]+d0[1]*40.0,
                               p0[2]+d0[2]*40.0)
                    glVertex3f(p0[0]-d0[0]*40.0,
                               p0[1]-d0[1]*40.0,
                               p0[2]-d0[2]*40.0)
                    glEnd()
                    pass
                pass
            pass
        pass
    #f display_grid
    def display_grid(self,n):
        glLineWidth(1.0)
        glMaterialfv(GL_FRONT,GL_AMBIENT,[1.0,0.3,0.3,1.0])
        glBegin(GL_LINES)
        for i in range(2*10+1):
            glVertex3f(-10.0,(i-10)*1.0,0.0)
            glVertex3f( 10.0,(i-10)*1.0,0.0)
            glVertex3f( (i-10)*1.0,-10.0,0.0)
            glVertex3f( (i-10)*1.0,10.0,0.0)
            pass
        glEnd()
        glMaterialfv(GL_FRONT,GL_AMBIENT,[0.3,1.0,0.3,1.0])
        glBegin(GL_LINES)
        for i in range(2*10+1):
            glVertex3f( -10.0,0.0,(i-10)*1.0)
            glVertex3f(  10.0,0.0,(i-10)*1.0)
            glVertex3f( (i-10)*1.0,0.0,-10.0)
            glVertex3f( (i-10)*1.0,0.0, 10.0)
        glEnd()
        glMaterialfv(GL_FRONT,GL_AMBIENT,[0.3,0.3,1.0,1.0])
        glBegin(GL_LINES)
        for i in range(2*10+1):
            glVertex3f( 0.0, -10.0,(i-10)*1.0)
            glVertex3f( 0.0,  10.0,(i-10)*1.0)
            glVertex3f( 0.0, (i-10)*1.0,-10.0)
            glVertex3f( 0.0, (i-10)*1.0, 10.0)
        glEnd()
        glMaterialfv(GL_FRONT,GL_AMBIENT,[1.0,1.0,1.0,1.0])
        glLineWidth(3.0)
        glBegin(GL_LINES)
        glVertex3f( -12.0, 0.0, 0.0 )
        glVertex3f(  12.0, 0.0, 0.0 )
        glVertex3f( 0.0, -12.0, 0.0 )
        glVertex3f( 0.0,  12.0, 0.0 )
        glVertex3f( 0.0, 0.0, -12.0 )
        glVertex3f( 0.0, 0.0,  12.0 )
        glEnd()
        pass
    #f display_images
    def display_images(self):
        brightness = 1.0
        glEnable(GL_TEXTURE_2D)
        glMaterialfv(GL_FRONT,GL_DIFFUSE,[brightness*1.0,brightness*1.,brightness*1.0,1.])
        glMaterialfv(GL_FRONT,GL_AMBIENT,[1.0,1.0,1.0,1.0])
        for image in self.image_projections:
            self.image_projections[image].display()
            pass
        glDisable(GL_TEXTURE_2D)
        pass
    #f display
    def display(self):
        opengl_app.c_opengl_camera_app.display(self, show_crosshairs=True)

        ambient_lightZeroColor = [1.0,1.0,1.0,1.0]
        glLightfv(GL_LIGHT1, GL_AMBIENT, ambient_lightZeroColor)
        glEnable(GL_LIGHT1)

        self.display_grid(3)
        self.display_image_faces()
        self.display_image_points()
        self.display_images()
   
        glutSwapBuffers()
        pass
    #f keypress
    def keypress(self, key,m,x,y):
        if key in ["1", "2", "3", "4"]:
            n = ["1","2","3","4"].index(key)
            image_data = self.point_mappings.get_image_data(self.image_names[n])
            proj = image_data["projection"]
            self.set_camera(camera=vectors.vector_scale(proj.projection["camera"],-1.0),
                            orientation=proj.projection["orientation"].copy().invert_rotation(),
                            fov=proj.projection["fov"])
            return True
        return opengl_app.c_opengl_camera_app.keypress(self, key,m,x,y)
    #f find_in_triangle
    def find_in_triangle(self, xy, p0, p1, p2):
        """
        Iterative approach to finding a point on a plane that maps by self.mvp to xy on the screen
        """
        k01 = 0.0
        k02 = 0.0
        sp0 = self.mvp.apply(p0)
        sp1 = self.mvp.apply(p1)
        sp2 = self.mvp.apply(p2)
        dxy01 = (sp1[0]-sp0[0], sp1[1]-sp0[1])
        dxy02 = (sp2[0]-sp0[0], sp2[1]-sp0[1])
        #m = matrix2x2((dxy01.dxy01, dxy02.dxy01, dxy01.dxy02, dxy02.dxy02))
        m = matrix.c_matrix2x2((dxy01[0]*dxy01[0]+dxy01[1]*dxy01[1],
                       dxy02[0]*dxy01[0]+dxy02[1]*dxy01[1],
                       dxy02[0]*dxy01[0]+dxy02[1]*dxy01[1],
                       dxy02[0]*dxy02[0]+dxy02[1]*dxy02[1],))
        m.invert()
        def find_better_point(k01, k02):
            mp = point_on_plane(p0,p1,p2, k01,k02)
            sp = self.mvp.apply(mp)
            #print "better_point ks, mp and screen point",k01,k02,mp,sp
            dxy = (xy[0]-sp[0], xy[1]-sp[1])
            #dk01*dxy01 + dk02*dxy02 = dxy
            #dk01*dxy01.dxy01 + dk02*dxy02.dxy01 = dxy.dxy01
            #dk01*dxy01.dxy02 + dk02*dxy02.dxy02 = dxy.dxy02
            #return m.apply( (dxy.dxy01, dxy,dxy02) )
            dk = m.apply( (dxy[0]*dxy01[0] + dxy[1]*dxy01[1],
                             dxy[0]*dxy02[0] + dxy[1]*dxy02[1]) )
            return (k01+dk[0], k02+dk[1])
        for i in range(30):
            (k01,k02) = find_better_point(k01, k02)
        return (k01,k02)
    #f mouse
    def mouse(self,b,s,m,x,y):
        if self.projection is None:
            return
        print "button, state, window x/y",b,s,x,y
        ip = self.projection.mvp.projection()
        ip.invert()

        p0 = [0,0,0]
        p1 = [x,y,(self.zFar+self.zNear)/(self.zFar-self.zNear)]
        p0 = ip.apply(p0)
        p1 = ip.apply(p1)
        for i in range(3):
            p0[i] += self.camera["position"][i]
            p1[i] += self.camera["position"][i]
            pass
        print p0, p1
        # The plane going through p with normal n has points p' such that (p'-p).n = 0
        # The line p0 -> p1 has points px = p0 + k(p1-p0)
        # this intersects a plane in model space that is -10,-10,0 with unit normal 0,0,1
        # We know that (p0 + k(p1-p0) - p).n = 0
        # i.e. k(p1-p0).n = (p-p0).n
        n = (0.0,0.0,1.0)
        p = (0.0,0.0,0.0)
        p10n = (p1[0]-p0[0])*n[0] + (p1[1]-p0[1])*n[1] + (p1[2]-p0[2])*n[2]
        pp0n = (p[0]-p0[0])*n[0]  + (p[1]-p0[1])*n[1]  + (p[2]-p0[2])*n[2]
        k = pp0n/p10n
        p = (p0[0] + k*(p1[0]-p0[0]),
             p0[1] + k*(p1[1]-p0[1]),
             p0[2] + k*(p1[2]-p0[2]))
        print p
        k01 = (10-p[0])/20.0
        k02 = (10-p[1])/20.0
        print "proj coord in image",k01,k02,k01*4272, (1-k02)*2848

        #(k01,k02) = self.find_in_triangle((x,y), (-10.0,-10.0,0.0), (10.0,-10.0,0.0), (-10.0,10.0,0.0) )
        #print "coord in image",k01,k02,k01*4272, (1-k02)*2848
        #self.floatywoaty = point_on_plane((-10.0,-10.0,0.0), (10.0,-10.0,0.0), (-10.0,10.0,0.0),k01,k02)
        pass
    pass

#a Main
def main():
    point_map_filename = "sidsussexbell.map"
    point_map_filename = "pencils.map"
    point_map_filename = "corridor.map"
    og = c_mapping(point_map_filename=point_map_filename, window_size = (1000,1000))
    og.init_opengl()
    og.main_loop()

if __name__ == '__main__':
    main()

