#!/usr/bin/env python
# PYTHONPATH=`pwd`/../python:$PYTHONPATH ./view_obj.py

#a Imports
import gjslib.graphics.obj
import gjslib.graphics.opengl

import math
from OpenGL.GLUT import *
from OpenGL.GLU import *
from OpenGL.GL import *
from gjslib.math.quaternion import c_quaternion

#a Classes
#c c_view_obj
class c_view_obj(object):
    #f __init__
    def __init__(self, obj):
        self.camera = None
        self.obj = obj
        self.xxx = 0
        self.yyy = 0
        pass
    #f display
    def display(self):
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(40.,1.,1.,40.)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()

        
        self.camera["facing"] = c_quaternion.roll(self.camera["rpy"][0]).multiply(self.camera["facing"])
        self.camera["facing"] = c_quaternion.pitch(self.camera["rpy"][1]).multiply(self.camera["facing"])
        self.camera["facing"] = c_quaternion.yaw(self.camera["rpy"][2]).multiply(self.camera["facing"])
        m = self.camera["facing"].get_matrix()
        glMultMatrixf(m)
        self.camera["position"][0] += self.camera["speed"]*m[0][2]
        self.camera["position"][1] += self.camera["speed"]*m[1][2]
        self.camera["position"][2] += self.camera["speed"]*m[2][2]
        #glRotate(angle*180.0/3.14159,0,1,0)
        glTranslate(self.camera["position"][0],self.camera["position"][1],self.camera["position"][2])

        glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)
        self.yyy += 0.03
        lightZeroPosition = [4.+3*math.sin(self.yyy),4.,4.-3*math.cos(self.yyy),1.]
        lightZeroColor = [0.7,1.0,0.7,1.0] #white
        ambient_lightZeroColor = [1.0,1.0,1.0,1.0] #green tinged
        glLightfv(GL_LIGHT0, GL_POSITION, lightZeroPosition)
        glLightfv(GL_LIGHT0, GL_DIFFUSE, lightZeroColor)
        glLightf(GL_LIGHT0, GL_CONSTANT_ATTENUATION, 0.1)
        glLightf(GL_LIGHT0, GL_LINEAR_ATTENUATION, 0.05)
        glEnable(GL_LIGHT0)
        glLightfv(GL_LIGHT1, GL_AMBIENT, ambient_lightZeroColor)
        glEnable(GL_LIGHT1)

        glPushMatrix()
        color = [1.0,0.,0.,1.]
        glMaterialfv(GL_FRONT,GL_DIFFUSE,[1.0,1.0,1.0,1.0])
        glMaterialfv(GL_FRONT,GL_AMBIENT,[1.0,1.0,1.0,1.0])
        glTranslate(lightZeroPosition[0],lightZeroPosition[1],lightZeroPosition[2])
        glScale(0.3,0.3,0.3)
        glutSolidSphere(2,40,40)
        glPopMatrix()

        color = [0.5,0,0.,0.,1.]
        glMaterialfv(GL_FRONT,GL_AMBIENT,[0.1,0.1,0.1,1.0])
        glMaterialfv(GL_FRONT,GL_DIFFUSE,color)

        glPushMatrix()
        glRotate(95,1,0,0)
        self.xxx += 0.2#0.1
        brightness = 0.4
        glRotate(self.xxx,0,0,1)

        glEnable(GL_TEXTURE_2D)
        glBindTexture(GL_TEXTURE_2D, self.texture)
        glMaterialfv(GL_FRONT,GL_DIFFUSE,[brightness*1.0,brightness*1.,brightness*1.0,1.])
        glMaterialfv(GL_FRONT,GL_AMBIENT,[0.6,0.6,0.6,1.0])
        glPushMatrix()
        glTranslate(0,0,1)
        glScale(4,4,4)
        self.obj.draw_opengl_surface()
        glDisable(GL_TEXTURE_2D)
        glPopMatrix()

        glPopMatrix()

        glutSwapBuffers()
        return
    #f init
    def init(self, texture_filename):
        self.texture = gjslib.graphics.opengl.texture_from_png(texture_filename)
        self.obj.create_opengl_surface()
        pass
    #f All done
    pass

#a Top level
#f test_object
def test_object():
    obj = gjslib.graphics.obj.c_obj()
    #f = open("icosahedron.obj")
    #obj.load_from_file(f)
    #obj.create_icosahedron()
    obj.create_icosphere(subdivide=4)

    m = c_view_obj(obj)
    og = gjslib.graphics.opengl.c_opengl(window_size = (1000,1000))
    og.init_opengl()
    #og.create_menus(menus)
    #og.attach_menu("main_menu")
    #texture_filename = "earth_ico.png"
    #texture_filename = "../../1_earth_16k_div10.png"
    #texture_filename = "icosahedron.png"
    #texture_filename = "test2.png"
    texture_filename = "brick.png"
    m.init(texture_filename=texture_filename)
    m.camera = og.camera
    og.main_loop( display_callback = m.display,
                  #mouse_callback   = m.mouse,
                  #menu_callback = menu_callback,
                  )
#f Main
if __name__ == '__main__':
    test_object()

