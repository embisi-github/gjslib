#!/usr/bin/env python
# PYTHONPATH=`pwd`/../python:$PYTHONPATH ./view_obj.py
import gjslib.graphics.obj
import gjslib.graphics.opengl

import math
from OpenGL.GLUT import *
from OpenGL.GLU import *
from OpenGL.GL import *
from gjslib.math.quaternion import c_quaternion

camera = gjslib.graphics.opengl.camera
icosahedron = gjslib.graphics.obj.c_obj()
f = open("icosahedron.obj")
icosahedron.load_from_file(f)

xxx = 0
yyy = 0
first = True
def display():
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(40.,1.,1.,40.)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    #gluLookAt(10*math.sin(angle),0,10*math.cos(angle),
    #          0,0,0,
    #          0,1,0)
    #print angle*180.0/3.14159

    camera["facing"] = c_quaternion.roll(camera["rpy"][0]).multiply(camera["facing"])
    camera["facing"] = c_quaternion.pitch(camera["rpy"][1]).multiply(camera["facing"])
    camera["facing"] = c_quaternion.yaw(camera["rpy"][2]).multiply(camera["facing"])
    m = camera["facing"].get_matrix()
    glMultMatrixf(m)
    camera["position"][0] += camera["speed"]*m[0][2]
    camera["position"][1] += camera["speed"]*m[1][2]
    camera["position"][2] += camera["speed"]*m[2][2]
    #glRotate(angle*180.0/3.14159,0,1,0)
    glTranslate(camera["position"][0],camera["position"][1],camera["position"][2])

    glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)
    global yyy
    yyy += 0.03
    lightZeroPosition = [4.+3*math.sin(yyy),4.,4.-3*math.cos(yyy),1.]
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

    glMaterialfv(GL_FRONT,GL_AMBIENT,[0.1,0.1,0.1,1.0])
    glPushMatrix()
    #glTranslate(0.0 ,2.75, 0.0)
    color = [0.5,0,0.,0.,1.]
    glMaterialfv(GL_FRONT,GL_DIFFUSE,color)
    #glutSolidSphere(2,40,40)
    glutSolidOctahedron()
    glPopMatrix()

    glPushMatrix()
    global xxx, first
    xxx += 2#0.1
    brightness = 0.4
    glRotate(xxx,1,0,1)
    glTranslate(0.0 ,-0.75, 0.0)

    import traceback
    if True:
        glEnable(GL_TEXTURE_2D)
        glBindTexture(GL_TEXTURE_2D, texture)
        glMaterialfv(GL_FRONT,GL_DIFFUSE,[brightness*1.0,brightness*1.,brightness*1.0,1.])
        glPushMatrix()
        glTranslate(0,0,1)
        try:
            icosahedron.draw_opengl_surface()
        except:
            traceback.print_exc()
            pass
        glDisable(GL_TEXTURE_2D)
        glPopMatrix()

        pass

    glPopMatrix()

    glutSwapBuffers()
    first = False
    return

def init():
    global texture
    texture = gjslib.graphics.opengl.texture_from_png("test2.png")#../../1_earth_16k_div10.png")#icosahedron.png")
    icosahedron.create_opengl_surface()
    pass

if __name__ == '__main__': gjslib.graphics.opengl.main(init, display)
