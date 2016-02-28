#!/usr/bin/env python
# PYTHONPATH=`pwd`/../python:$PYTHONPATH ./mapping.py

#a Imports
import gjslib.graphics.obj
import gjslib.graphics.opengl
from gjslib.graphics import opengl_layer, opengl_widget

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
    def __init__(self, filename=None, epm=None):
        self.filename = filename
        self.texture = None
        self.object = None
        self.epm = epm
        pass
    #f load_texture
    def load_texture(self):
        if (self.texture is None):
            self.texture = gjslib.graphics.opengl.texture_from_png(self.filename)
            pass
        if self.object is None:
            self.object = gjslib.graphics.obj.c_obj()
            self.object.add_rectangle( (-1.0,1.0,0.0), (2.0,0.0,0.0), (0.0,-2.0,0.0) )
            self.object.create_opengl_surface()
            pass
        pass
    #f display
    def display(self):
        self.load_texture()
        if self.texture is None:
            return
        m = self.camera["facing"].get_matrix()
        glPushMatrix()
        glMultMatrixf(m)
        glBindTexture(GL_TEXTURE_2D, self.texture)
        self.object.draw_opengl_surface()
        glPopMatrix()
        pass
    #f All done
    pass

#a c_edit_point_map_info
class c_edit_point_map_info(object):
    #f __init__
    def __init__(self, epm=None):
        self.epm = epm
        pass
    #f set_image_list
    def set_image_list(self, image_list):
        self.image_list = image_list
        self.image_list_obj = gjslib.graphics.obj.c_text_page()
        self.image_list_obj.add_text(str(image_list), self.epm.og.fonts["font"][0], (-1.0+0.02,-0.1),(0.001/3,-0.001/3))
        self.image_list_obj.create_opengl_surface()
        pass
    #f display
    def display(self):
        glBindTexture(GL_TEXTURE_2D, self.epm.og.fonts["font"][1])
        self.image_list_obj.draw_opengl_surface(draw=True)
        pass
    #f All done
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
        self.epm_info = c_edit_point_map_info(epm=self)
        self.load_images()
        pass
    #f main_loop
    def main_loop(self):
        self.og.main_loop( display_callback=self.display,
                           mouse_callback = self.mouse,
                           menu_callback = self.menu_callback)
        pass
    #f menu_callback
    def menu_callback(self, menu, value):
        if type(value)==tuple:
            if value[0]=="image":
                self.image_layers[0].clear_contents()
                self.image_layers[0].add_contents(self.images[value[1]])
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
            self.images[k] = c_edit_point_map_image(epm=self, filename=image_data["filename"])
            pass
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

        self.epm_info.set_image_list(self.images.keys())
        for i in self.images:
            self.images[i].camera = self.og.camera
            pass

        self.layers = opengl_layer.c_opengl_layer_set()
        self.image_layers = (self.layers.new_layer( (0,500,500,500), depth=10),
                             self.layers.new_layer( (500,500,500,500), depth=10 ))
        self.info_layer = self.layers.new_layer( (0,0,1000,500), depth=1 )
        self.image_layers[0].add_contents(self.images["img_1"])
        self.image_layers[1].add_contents(self.images["img_2"])
        self.info_layer.add_contents(self.epm_info)
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
    #f display
    def display(self):
        glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)
        self.og.camera["facing"] = c_quaternion.roll(self.og.camera["rpy"][0]).multiply(self.og.camera["facing"])
        self.og.camera["facing"] = c_quaternion.pitch(self.og.camera["rpy"][1]).multiply(self.og.camera["facing"])
        self.og.camera["facing"] = c_quaternion.yaw(self.og.camera["rpy"][2]).multiply(self.og.camera["facing"])
        self.layers.display()
        glutSwapBuffers()
        pass
    #f mouse
    def mouse(self,b,s,x,y):
        print "button, state, window x/y",b,s,x,y
        pass
    pass

#a Main
def main():
    og = gjslib.graphics.opengl.c_opengl(window_size = (1000,1000))
    font_dir = "../../fonts/"
    m = c_edit_point_map(og)
    og.load_font(font_dir+"cabin-bold")
    m.reset()
    m.main_loop()

if __name__ == '__main__':
    main()

