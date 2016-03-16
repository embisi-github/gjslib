#!/usr/bin/env python
# PYTHONPATH=`pwd`/../python:$PYTHONPATH ./view_obj.py

#a Imports
from gjslib.graphics import opengl_app, opengl_utils, opengl_obj

import math
from OpenGL.GLUT import *
from OpenGL.GLU import *
from OpenGL.GL import *

#a Classes
#c c_view_obj
class c_view_obj(opengl_app.c_opengl_camera_app):
    #f __init__
    def __init__(self, obj, texture_filename, **kwargs):
        opengl_app.c_opengl_camera_app.__init__(self, **kwargs)
        self.obj = obj
        self.xxx = 0.0
        self.yyy = 0.0
        self.window_title = "Viewing object"
        self.texture_filename = texture_filename
        pass
    #f opengl_post_init
    def opengl_post_init(self):
        self.texture = opengl_utils.texture_from_png(self.texture_filename)
        self.obj.create_opengl_surface()
        pass
    #f display
    def display(self):
        opengl_app.c_opengl_camera_app.display(self)

        self.yyy += 0.03
        lightZeroPosition = [4.+3*math.sin(self.yyy),4.,4.-3*math.cos(self.yyy),1.]
        lightZeroColor = [0.7,1.0,0.7,1.0] #white
        ambient_lightZeroColor = [1.0,1.0,1.0,1.0] #green tinged

        #glPushMatrix()
        #color = [1.0,0.,0.,1.]
        #glTranslate(lightZeroPosition[0],lightZeroPosition[1],lightZeroPosition[2])
        #glScale(0.3,0.3,0.3)
        #glutSolidSphere(2,40,40)
        #glPopMatrix()

        color = [0.5,0,0.,0.,1.]

        self.matrix_push()
        self.matrix_rotate(95,(1,0,0))
        #self.xxx += 0.2#0.1
        brightness = 0.4
        self.matrix_rotate(self.xxx,(0,0,1))

        glBindTexture(GL_TEXTURE_2D, self.texture)
        self.matrix_push()
        self.matrix_translate((0,0,1))
        self.matrix_scale(4)
        self.shader_use("texture_standard")
        self.matrix_use()
        self.obj.draw_opengl_surface(self)
        self.matrix_pop()
        self.matrix_pop()

        glutSwapBuffers()
        return
    #f All done
    pass

#a Top level
#f test_object
def test_object():
    obj = opengl_obj.c_opengl_obj()

    texture_filename = "earth_ico.png"
    #texture_filename = "../../1_earth_16k_div10.png"
    #texture_filename = "icosahedron.png"
    #texture_filename = "test2.png"
    #texture_filename = "brick.png"

    #f = open("icosahedron.obj")
    #obj.load_from_file(f)
    #obj.create_icosahedron()
    obj.create_icosphere(subdivide=4)

    og = c_view_obj(obj=obj,
                    texture_filename=texture_filename,
                    window_size=(1000,1000))
    og.init_opengl()
    og.seal_hack = True
    og.camera["fov"] = 5

    og.zFar = 100.0
    #og.create_menus(menus)
    #og.attach_menu("main_menu")
    og.main_loop()

#f Main
if __name__ == '__main__':
    test_object()

