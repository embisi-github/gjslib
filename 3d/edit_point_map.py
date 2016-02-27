#!/usr/bin/env python
# PYTHONPATH=`pwd`/../python:$PYTHONPATH ./mapping.py

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

#a c_edit_point_map_image
class c_edit_point_map_image(object):
    #f __init__
    def __init__(self, filename):
        self.filename = filename
        self.texture = None
        self.object = None
        self.display_options = {"show":False}
        #self.display_options = {"show":True}
        pass
    #f load_texture
    def load_texture(self):
        if (self.texture is None) and self.display_options["show"]:
            self.texture = gjslib.graphics.opengl.texture_from_png(self.filename)
            pass
        if self.object is None:
            self.object = gjslib.graphics.obj.c_obj()
            self.object.add_rectangle( (-1.0,1.0,0.0), (1.0,0.0,0.0), (0.0,-1.0,0.0) )
            self.object.create_opengl_surface()
            pass
        pass
    #f display
    def display(self):
        if not self.display_options["show"]:
            return
        self.load_texture()
        if self.texture is None:
            return
        glPushMatrix()
        glBindTexture(GL_TEXTURE_2D, self.texture)
        self.object.draw_opengl_surface()
        glPopMatrix()
        pass

#a c_edit_point_map
class c_edit_point_map(object):
    #f __init__
    def __init__(self, og):
        self.og = og
        self.aspect = 1.0
        self.zNear=1.0
        self.zFar=40.0
        self.images = {}
        self.og.init_opengl()
        self.point_mappings = c_point_mapping()
        self.load_point_mapping("sidsussexbell.map")
        self.load_images()
        pass
    #f main_loop
    def main_loop(self):
        self.og.main_loop( display_callback=self.display,
                      mouse_callback = self.mouse,
                      menu_callback = self.menu_callback)
        pass
    #f enable_image
    def enable_image(self, image_name):
        if image_name not in self.images:
            return
        for i in self.images:
            self.images[i].display_options["show"] = False
            pass
        self.images[image_name].display_options["show"] = True
        pass
    #f menu_callback
    def menu_callback(self, menu, value):
        if type(value)==tuple:
            if value[0]=="image":
                self.enable_image(value[1])
                return True
            pass
        print menu, value
        return True
    #f load_point_mapping
    def load_point_mapping(self, point_map_filename):
        self.point_mappings.reset()
        self.point_mappings.load_data(point_map_filename)
        pass
    #f load_images
    def load_images(self):
        image_names = self.point_mappings.get_images()
        for k in image_names:
            image_data = self.point_mappings.get_image(k)
            self.images[k] = c_edit_point_map_image(filename=image_data["filename"])
            pass
        self.images[k].display_options["show"] = True
        pass
    #f reset
    def reset(self):
        glutSetCursor(GLUT_CURSOR_CROSSHAIR)
        menus = self.og.build_menu_init()
        #gjslib.graphics.opengl.attach_menu("main_menu")
        self.og.build_menu_add_menu(menus,"images")
        image_keys = self.images.keys()
        for i in range(len(image_keys)):
            k = image_keys[i]
            self.og.build_menu_add_menu_item(menus,k,("image",k))
            pass
        self.og.build_menu_add_menu(menus,"main_menu")
        self.og.build_menu_add_menu_submenu(menus,"Images","images")
        print menus
        self.og.create_menus(menus)
        self.og.attach_menu("main_menu")

        image_list = ""
        for i in self.images:
            image_list += i+"\n"
            pass
        self.image_list_obj = gjslib.graphics.obj.c_text_page()
        self.image_list_obj.add_text(image_list, self.og.fonts["font"][0], (-1.0+0.02,-0.1),(0.001/3,-0.001/3))
        self.image_list_obj.create_opengl_surface()

        for k in self.images:
            if k not in ["main"]:
                self.images[k].load_texture()
                pass
            pass
        pass
    #f display_set_projection
    def display_set_projection(self):
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()

        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        self.og.camera["facing"] = c_quaternion.roll(self.og.camera["rpy"][0]).multiply(self.og.camera["facing"])
        self.og.camera["facing"] = c_quaternion.pitch(self.og.camera["rpy"][1]).multiply(self.og.camera["facing"])
        self.og.camera["facing"] = c_quaternion.yaw(self.og.camera["rpy"][2]).multiply(self.og.camera["facing"])
        m = self.og.camera["facing"].get_matrix()
        glMultMatrixf(m)
        pass
    #f display_image_points
    def display_image_points(self):
        global faces
        for n in faces:
            f = faces[n]
            pts = []
            for pt in f:
                if pt in self.point_mappings.get_mapping_names():
                    pts.append(self.point_mappings.get_approx_position(pt))
                    pass
                pass
            if len(pts)>=3:
                i = 0
                j = len(pts)-1
                glBegin(GL_TRIANGLE_STRIP)
                while (j>=i):
                    glVertex3f(pts[i][0],pts[i][1],pts[i][2])
                    i += 1
                    if (i<=j):
                        glVertex3f(pts[j][0],pts[j][1],pts[j][2])
                        pass
                    j -= 1
                    pass
                glEnd()
                pass
            pass
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
    #f display_info
    def display_info(self):
        glPushMatrix()
        glMaterialfv(GL_FRONT,GL_DIFFUSE,[1.0,1.0,1.0,1.0])
        glMaterialfv(GL_FRONT,GL_AMBIENT,[1.0,1.0,1.0,1.0])
        glBindTexture(GL_TEXTURE_2D, self.og.fonts["font"][1])
        self.image_list_obj.draw_opengl_surface(draw=True)
        glPopMatrix()
        pass
    #f display_images
    def display_images(self):
        brightness = 1.0
        glMaterialfv(GL_FRONT,GL_DIFFUSE,[brightness*1.0,brightness*1.,brightness*1.0,1.])
        glMaterialfv(GL_FRONT,GL_AMBIENT,[1.0,1.0,1.0,1.0])
        for image in self.images:
            self.images[image].display()
            pass
        pass
    #f display
    def display(self):
        glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)

        self.display_set_projection()

        ambient_lightZeroColor = [1.0,1.0,1.0,1.0]
        glLightfv(GL_LIGHT1, GL_AMBIENT, ambient_lightZeroColor)
        glEnable(GL_LIGHT1)
        glEnable(GL_TEXTURE_2D)

        #self.display_grid(3)
        #self.display_image_points()
        self.display_info()
        self.display_images()
   
        glutSwapBuffers()
        pass
    #f mouse
    def mouse(self,b,s,x,y):
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
test_text  = "It is a period of civil war.\n"
test_text += "Rebel spaceships, striking\n"
test_text += "from a hidden base, have won\n"
test_text += "their first victory against\n"
test_text += "the evil Galactic Empire.\n"
test_text += "\n"
test_text += "During the battle, Rebel spies\n"
test_text += "managed to steal secret plans\n"
test_text += "to the Empire's ultimate weapon,\n"
test_text += "the DEATH STAR, an armored space\n"
test_text += "station with enough power to\n"
test_text += "destroy an entire planet.\n"
test_text += "\n"
test_text += "Pursued by the Empire's sinister\n"
test_text += "agents, Princess Leia races\n"
test_text += "home aboard her starship,\n"
test_text += "custodian of the stolen plans\n"
test_text += "that can save her people and\n"
test_text += "restore freedom to the galaxy...."
def main():
    og = gjslib.graphics.opengl.c_opengl(window_size = (1000,1000))
    font_dir = "../../fonts/"
    m = c_edit_point_map(og)
    og.load_font(font_dir+"cabin-bold")
    m.reset()
    m.main_loop()

if __name__ == '__main__':
    main()

