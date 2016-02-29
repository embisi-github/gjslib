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
import gjslib.graphics.opengl
import math
from OpenGL.GLUT import *
from OpenGL.GLU import *
from OpenGL.GL import *

from gjslib.math.quaternion import c_quaternion
from gjslib.math import matrix, vectors, statistics
from image_point_mapping import c_point_mapping
from image_projection import c_image_projection

#a Mapping data
object_guess_locations = {}
object_guess_locations["clk.center"] = (0.0,0.0,6.5)
object_guess_locations["lspike.t"] = (-3.0,0.0,8.5)
object_guess_locations["rspike.t"] = ( 3.0,0.0,8.5)
faces = {}
faces["frontleft"]  = ["tl", "fl.cr", "fl.br", "bl"]
faces["frontright"] = ["tr", "br", "fr.bl", "fr.cl"]
faces["clock"]      = ["clk.tl", "clk.mtr", "clk.mtl", "clk.tr", "clk.br", "clk.bl"]
faces["lspike.fl"]  = ["lspike.l", "lspike.t", "lspike.f"]
faces["lspike.fr"]  = ["lspike.f", "lspike.t", "lspike.r"]
faces["rspike.fl"]  = ["rspike.l", "rspike.t", "rspike.f"]
faces["rspike.fr"]  = ["rspike.f", "rspike.t", "rspike.r"]

image_mapping_data = {}
image_mapping_data["main"] = {}
image_mapping_data["main"]["filename"] = "sidsussexbell.jpg"
image_mapping_data["main"]["size"] = (4272,2848)
image_mapping_data["main"]["projection"] = {"camera":(-6.0,-12.0,2.0), "target":(5.0,0.0,4.0), "up":(0.0,0.0,1.0), "xscale":1.3, "yscale":1.75}
image_mapping_data["main"]["projection"] = {'xscale': 1.052, 'camera': [-3.319999999999946, -13.375000000000016, 1.5700000000000052], 'yscale': 1.90, 'target': [5.574999999999997, 0.15, 4.280000000000003], 'up': (0.0, 0.0, 1.0)}


image_mapping_data["img_1"] = {}
image_mapping_data["img_1"]["filename"] = "sidsussexbell_1.jpg"
image_mapping_data["img_1"]["size"] = (640,480)
image_mapping_data["img_1"]["projection"] = {"camera":(+7.0,-6.0,6.7), "target":(-1.0,0.0,5.5), "up":(0.0,0.0,1.0), "xscale":2.2, "yscale":2.1}
image_mapping_data["img_1"]["projection"] = {'xscale': 1.78, 'camera': [5.7249999999999766, -8.050000000000045, 6.349999999999991], 'yscale': 2.495, 'target': [-1.0999999999999996, -0.025, 5.650000000000002], 'up': (0.0, 0.0, 1.0)}



image_mapping_data["img_2"] = {}
image_mapping_data["img_2"]["filename"] = "sidsussexbell_2.jpg"
image_mapping_data["img_2"]["size"] = (1024,772)
image_mapping_data["img_2"]["projection"] = {"camera":(0.0,-6.0,2.0), "target":( 0.0,0.0,7.2), "up":(0.01,0.0,1.0), "xscale":2.45, "yscale":3.8}
image_mapping_data["img_2"]["projection"] = {'xscale': 2.445, 'camera': (-0.2, -6.2, 2.225), 'yscale': 3.77, 'target': (0.025, 0.025, 7.2), 'up': (0.01, 0.0, 1.0)}


image_mapping_data["img_3"] = {}
image_mapping_data["img_3"]["filename"] = "sidsussexbell_3.jpg"
image_mapping_data["img_3"]["size"] = (320,370)
image_mapping_data["img_3"]["projection"] = {'xscale': 3.0, 'camera': [0.05, -9.999999999999986, -0.6500000000000005], 'yscale': 2.93, 'target': [0.25, 0.2, 4.999999999999997], 'up': (0.0, 0.0, 1.0)}



#a c_opengl_image_projection
class c_opengl_image_projection(c_image_projection):
    #f __init__
    def __init__(self, **kwargs):
        self.texture = None
        self.object = None
        c_image_projection.__init__(self, **kwargs)
        pass
    #f load_texture
    def load_texture(self):
        self.texture = gjslib.graphics.opengl.texture_from_png(self.image_filename)
        self.object = gjslib.graphics.obj.c_obj()
        self.object.add_rectangle( (-10.0,10.0,0.0), (20.0,0.0,0.0), (0.0,-20.0,0.0) )
        self.object.create_opengl_surface()
        pass
    #f display
    def display(self):
        glPushMatrix()
        if self.texture is not None:
            glBindTexture(GL_TEXTURE_2D, self.texture)
            self.object.draw_opengl_surface()
            glPopMatrix()
            return
        glPushMatrix()
        glTranslate(self.camera[0],self.camera[1],self.camera[2])
        glutSolidCube(0.1)
        glPopMatrix()
        glColor3f(1.0, 1.0, 1.0)
        glLineWidth(1.0)
        glBegin(GL_LINES);
        glVertex3f(self.camera[0],self.camera[1],self.camera[2])
        glVertex3f(self.target[0],self.target[1],self.target[2])
        glEnd()
        glPopMatrix()
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
class c_mapping(object):
    camera_deltas = [{"camera":(-0.1,0.0,0.0)},
                     {"camera":(+0.1,0.0,0.0)},
                     {"camera":(0.0,-0.1,0.0)},
                     {"camera":(0.0,+0.1,0.0)},
                     {"camera":(0.0,0.0,-0.1)},
                     {"camera":(0.0,0.0,+0.1)},
                     {}]
    target_deltas = [{"target":(-0.1,0.0,0.0)},
                     {"target":(+0.1,0.0,0.0)},
                     {"target":(0.0,-0.1,0.0)},
                     {"target":(0.0,+0.1,0.0)},
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
    def __init__(self):
        self.first_pass = True
        self.mvp =  matrix.c_matrix4x4()
        self.camera = gjslib.graphics.opengl.camera
        self.aspect = 1.0
        self.zNear=1.0
        self.zFar=40.0
        self.point_mappings = c_point_mapping()
        self.image_projections = {}
        self.load_point_mapping("sidsussexbell.map")
        global image_mapping_data
        self.load_images(image_mapping_data)
        print self.point_mappings.get_mapping_names()
        #self.calc_total_errors()
        pass
    #f load_point_mapping
    def load_point_mapping(self, point_map_filename):
        self.point_mappings.reset()
        self.point_mappings.load_data(point_map_filename)
        pass
    #f load_image
    def load_image(self, name, image_filename, projection, size):
        self.image_projections[name] = c_opengl_image_projection(name=name,
                                                                 image_filename=image_filename,
                                                                 size=size)
        self.image_projections[name].set_projection(projection=projection)
        self.point_mappings.add_image(name, size=size)
        self.point_mappings.set_projection(name, self.image_projections[name])
        pass
    #f find_better_projection
    def find_better_projection(self,mappings,image_projection,projection,deltas_list,delta_scale):
        smallest_error = (None,10000)
        for deltas in deltas_list:
            r = {}
            image_projection.set_projection( projection=projection, deltas=deltas, delta_scale=0.25, resultant_projection=r )
            print
            print deltas
            e = 0
            corr = (statistics.c_correlation(), statistics.c_correlation())
            corr[0].add_entry(0.0,0.0)
            corr[1].add_entry(0.0,0.0)
            for n in mappings:
                e += image_projection.mapping_error(n,mappings[n],corr)
                pass
            print "Total error",e,1-corr[0].correlation_coefficient(), 1-corr[1].correlation_coefficient()
            e += 50.0*(1-corr[0].correlation_coefficient())
            e += 50.0*(1-corr[1].correlation_coefficient())
            if e<smallest_error[1]:
                smallest_error = (deltas,e,r)
                pass
            pass
        print "Smallest error",smallest_error
        print
        return smallest_error
    #f blah
    def blah(self, image_mapping_name):
        global image_mapping_data
        image_data = image_mapping_data[image_mapping_name]
        p = self.image_projections[image_mapping_name].projection
        for i in range(1000):
            for j in range(5):
                (d,e,p) = self.find_better_projection(image_data["mappings"],self.image_projections[image_mapping_name],p,self.camera_deltas,delta_scale=0.05)
                if len(d)==0: break
                pass
            (d,e,p) = self.find_better_projection(image_data["mappings"],self.image_projections[image_mapping_name],p,self.target_deltas,delta_scale=0.0125)
            (d,e,p) = self.find_better_projection(image_data["mappings"],self.image_projections[image_mapping_name],p,self.up_deltas,delta_scale=0.0025)
            pass
        pass
    #f load_images
    def load_images(self, image_mapping_data):
        for k in image_mapping_data:
            image_data = image_mapping_data[k]
            self.load_image(k,
                            image_filename=image_data["filename"],
                            projection=image_data["projection"],
                            size=image_data["size"])
            pass
        pass
    #f calc_total_errors
    def calc_total_errors(self):
        global image_mapping_data
        # Should get data from point_mappings instead
        for k in image_mapping_data:
            #if k in ["img_1", "img_3"]: continue
            image_data = image_mapping_data[k]
            print
            print k
            e = 0
            corr = (statistics.c_correlation(), statistics.c_correlation())
            for n in image_data["mappings"]: # Should get data from point_mappings instead
                xy = image_data["mappings"][n]
                e += self.image_projections[k].mapping_error(n,xy,corr)
                pass
            print "Total error",e,1-corr[0].correlation_coefficient(), 1-corr[1].correlation_coefficient()
            pass
        pass
        #self.blah("img_3")
        pass
    #f reset
    def reset(self):
        global image_mapping_data
        #gjslib.graphics.opengl.attach_menu("main_menu")
        self.camera["position"] = [0.0,10.0,-2.0]
        self.camera["facing"] = c_quaternion.identity()
        self.camera["facing"] = c_quaternion.pitch(-1*3.1415/2).multiply(self.camera["facing"])
        self.camera["facing"] = c_quaternion.roll(0*3.1415).multiply(self.camera["facing"])
        for k in image_mapping_data:
            self.image_projections[k].load_texture()
            pass
        self.point_mappings.find_line_sets()
        self.point_mappings.approximate_positions()
        #die
        pass
    #f display_set_projection
    def display_set_projection(self):
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(self.camera["fov"],self.aspect,self.zNear,self.zFar)
        self.mvp.perspective(self.camera["fov"],self.aspect,self.zNear,self.zFar)

        self.camera["facing"] = c_quaternion.roll( self.camera["rpy"][0]).multiply(self.camera["facing"])
        self.camera["facing"] = c_quaternion.pitch(self.camera["rpy"][1]).multiply(self.camera["facing"])
        self.camera["facing"] = c_quaternion.yaw(  self.camera["rpy"][2]).multiply(self.camera["facing"])

        m = self.camera["facing"].get_matrix()
        self.camera["position"][0] += self.camera["speed"]*m[0][2]
        self.camera["position"][1] += self.camera["speed"]*m[1][2]
        self.camera["position"][2] += self.camera["speed"]*m[2][2]

        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        glMultMatrixf(m)
        glTranslate(self.camera["position"][0],self.camera["position"][1],self.camera["position"][2])

        self.mvp.mult3x3(m3=m)
        self.mvp.translate(self.camera["position"])
        pass
    #f display_image_faces
    def display_image_faces(self):
        global faces
        glPushMatrix()
        glEnable(GL_TEXTURE_2D)
        glMaterialfv(GL_FRONT,GL_AMBIENT,[1.0,1.0,1.0,1.0])
        proj = self.image_projections["main"]
        if proj.texture is not None:
            glBindTexture(GL_TEXTURE_2D, proj.texture)
            pass
        for n in faces:
            f = faces[n]
            pts = []
            tex_pts = []
            for pt in f:
                if pt in self.point_mappings.get_mapping_names():
                    pt_xyz = self.point_mappings.get_approx_position(pt)
                    pts.append(pt_xyz)
                    (xyzw,img_xy) = proj.image_of_model(pt_xyz)
                    tex_pts.append( (0.5+xyzw[0]*0.5, 0.5-xyzw[1]*0.5) )
                    pass
                pass
            if len(pts)>=3:
                i = 0
                j = len(pts)-1
                glBegin(GL_TRIANGLE_STRIP)
                while (j>=i):
                    glTexCoord2f(tex_pts[i][0],tex_pts[i][1])
                    glVertex3f(pts[i][0],pts[i][1],pts[i][2])
                    i += 1
                    if (i<=j):
                        glTexCoord2f(tex_pts[j][0],tex_pts[j][1])
                        glVertex3f(pts[j][0],pts[j][1],pts[j][2])
                        pass
                    j -= 1
                    pass
                glEnd()
                pass
            pass
        glDisable(GL_TEXTURE_2D)
        glPopMatrix()
        self.first_pass = False
        pass
    #f display_image_points
    def display_image_points(self):
        for n in self.point_mappings.get_mapping_names():
            (xyz) = self.point_mappings.get_approx_position(n)
            glPushMatrix()
            glMaterialfv(GL_FRONT,GL_AMBIENT,[1.0,0.3,0.3,1.0])
            glTranslate(xyz[0],xyz[1],xyz[2])
            glScale(0.03,0.03,0.03)
            glutSolidSphere(1,6,6)
            glPopMatrix()
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
                p = self.image_projections[k]
                xy = self.point_mappings.get_xy(pt, k)
                if xy is not None:
                    (p0,d0) = p.model_line_for_image(xy)
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
        glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)

        self.display_set_projection()

        ambient_lightZeroColor = [1.0,1.0,1.0,1.0]
        glLightfv(GL_LIGHT1, GL_AMBIENT, ambient_lightZeroColor)
        glEnable(GL_LIGHT1)

        self.display_grid(3)
        self.display_image_faces()
        self.display_image_points()
        self.display_images()
   
        glutSwapBuffers()
        pass
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
        print "button, state, window x/y",b,s,x,y
        ip = self.mvp.projection()
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
    m = c_mapping()
    menus = [ ("submenu",   (("a",1), ("b",2))),
              ("main_menu", (("sub", "submenu"), ("c", 3)))
              ]
    og = gjslib.graphics.opengl.c_opengl(window_size = (1000,1000))
    og.init_opengl()
    menus = og.build_menu_init()
    og.build_menu_add_menu(menus,"submenu")
    og.build_menu_add_menu_item(menus,"a",("a",1))
    og.build_menu_add_menu_item(menus,"b",("b",2))
    og.build_menu_add_menu(menus,"main_menu")
    og.build_menu_add_menu_submenu(menus,"Sub","submenu")
    og.build_menu_add_menu_item(menus,"c","Item c")
    og.create_menus(menus)
    og.attach_menu("main_menu")
    m.camera = og.camera
    m.reset()
    og.main_loop( display_callback=m.display,
                  mouse_callback = m.mouse)
                  #menu_callback = menu_callback)

if __name__ == '__main__':
    main()

