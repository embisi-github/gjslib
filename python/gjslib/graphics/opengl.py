#!/usr/bin/env python
from OpenGL.GLUT import *
from OpenGL.GLU import *
from OpenGL.GL import *
import sys
import math
from gjslib.math.quaternion import c_quaternion

name = 'ball_glut'

camera = {"position":[0,0,-10],
          "facing":c_quaternion.identity(),
          "rpy":[0,0,0],
          "speed":0,
          }
angle_speed = 0.0
delay = 40
delay = 100
use_primitive_restart = False
from gjslib.math import bezier
#import bezier
import array
opengl_surface = {}

def texture_from_png(png_filename):
    from PIL import Image
    import numpy

    png = Image.open(png_filename)
    png_data = numpy.array(list(png.getdata()), numpy.uint8)

    texture = glGenTextures(1)
    glPixelStorei(GL_UNPACK_ALIGNMENT,1)
    glBindTexture(GL_TEXTURE_2D, texture)

    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_MIRRORED_REPEAT)
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_MIRRORED_REPEAT)
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, png.size[0], png.size[1], 0, GL_RGB, GL_UNSIGNED_BYTE, png_data)
    return texture

def init_stuff():
    patches = { "flat_xy_square": ( (0,0,0),     (1/3.0,0,0),     (2/3.0,0,0),   (1,0,0),
                                    (0,1/3.0,0), (1/3.0,1/3.0,0), (2/3.0,1/3.0,0), (1,1/3.0,0),
                                    (0,2/3.0,0), (1/3.0,2/3.0,0), (2/3.0,2/3.0,0), (1,2/3.0,0),
                                    (0,1,0),     (1/3.0,1,0),     (2/3.0,1,0),     (1,1,0),
                                    ),
                "bump_one": ( (0,0,0),   (0.1,0,0.1),   (0.9,0,0.1),   (1,0,0),
                              (0,0.1,0.1), (0.1,0.1,0.1), (0.9,0.1,0.1), (1,0.1,0.1),
                              (0,0.9,0.1), (0.1,0.9,0.1), (0.9,0.9,0.1), (1,0.9,0.1),
                              (0,1,0),   (0.1,1,0.1),   (0.9,1,0.1),   (1,1,0),
                                    ),
                "bump_two": ( (0,0,0),        (0.2,-0.2,0.2),   (0.8,-0.2,0.2),   (1,0,0),
                              (-0.2,0.2,0.2), (0.2,0.2,-0.1),    (0.8,0.2,-0.1), (1.2,0.2,0.2),
                              (-0.2,0.8,0.2), (0.2,0.8,-0.1),    (0.8,0.8,-0.1), (1.2,0.8,0.2),
                              (0,1,0),        (0.2,1.2,0.2),    (0.8,1.2,0.2),   (1,1,0),
                                    ),
                }
    patch = patches["flat_xy_square"]
    patch = patches["bump_two"]
    patch = patches["bump_two"]
    patch = patches["bump_one"]
    #patch = patches["flat_xy_square"]
    global opengl_surface
    import OpenGL.arrays.vbo as vbo
    import numpy
    from ctypes import sizeof, c_float, c_void_p, c_uint
    pts = []
    for coords in patch: pts.append( bezier.c_point(coords=coords) )
    bp = bezier.c_bezier_patch( pts=pts )

    # data_array is an array of records, each of floats
    # Each record is:
    # 3 floats as a vertex
    # 3 floats as a normal
    float_size = sizeof(c_float)
    vertex_offset    = c_void_p(0 * float_size)
    normal_offset    = c_void_p(3 * float_size)
    record_len       = 6 * float_size
    data_array = []
    n = 14
    for i in range(n+1):
        for j in range(n+1):
            data_array.append( bp.coord(i/(n+0.0),j/(n+0.0)).get_coords(scale=(2.0,2.0,2.0),offset=(-1.,-1.0,.0)) )
            data_array.append( bp.normal(i/(n+0.0),j/(n+0.0)).get_coords() )
            pass
        pass

    # VBO is a vertex-buffer-object - really this is a VAO I believe
    vertices = vbo.VBO( data=numpy.array(data_array, dtype=numpy.float32) )

    # target=GL_ELEMENT_ARRAY_BUFFER makes the VBO 

    index_list = []
    if use_primitive_restart:
        glEnable(GL_PRIMITIVE_RESTART) 
        pass
    for j in range(n):
        for i in range(n+1):
            index_list.append( i+j*(n+1) )
            index_list.append( i+(j+1)*(n+1) )
            pass
        if j<(n-1):
            if use_primitive_restart:
                index_list.append( 255 )
                pass
            else:
                index_list.append( (n)+(j+1)*(n+1) )
                index_list.append( (n)+(j+1)*(n+1) )
                index_list.append( (j+1)*(n+1) )
                index_list.append( (j+1)*(n+1) )
                pass
        pass

    print index_list
    indices = vbo.VBO( data=numpy.array( index_list, dtype=numpy.uint8),
                       target=GL_ELEMENT_ARRAY_BUFFER )
    vertices.bind()
    indices.bind()
    opengl_surface["vertices"] = vertices
    opengl_surface["indices"] = indices
    opengl_surface["vertex_offset"] = vertex_offset
    opengl_surface["normal_offset"] = normal_offset
    opengl_surface["record_len"] = record_len

    # glTexCoordPointer(2, GL_FLOAT, sizeof(TVertex_VNTWI), info->texOffset);
    # glEnableClientState(GL_TEXTURE_COORD_ARRAY);
    # glNormalPointer(GL_FLOAT, sizeof(TVertex_VNTWI), info->nmlOffset);
    # glEnableClientState(GL_NORMAL_ARRAY);
    # uint_size  = sizeof(c_uint)
    # float_size = sizeof(c_float)
    # vertex_offset    = c_void_p(0 * float_size)
    # tex_coord_offset = c_void_p(3 * float_size)
    # normal_offset    = c_void_p(6 * float_size)
    # color_offset     = c_void_p(9 * float_size)
    # record_len       =         12 * float_size
    # def draw_object():
    #  glVertexPointer(3, GL_FLOAT, record_len, vertex_offset)
    #  glTexCoordPointer(3, GL_FLOAT, record_len, tex_coord_offset)
    #  glNormalPointer(GL_FLOAT, record_len, normal_offset)
    #  glColorPointer(3, GL_FLOAT, record_len, color_offset)

def stuff():
    global opengl_surface
    opengl_surface["vertices"].bind()
    glEnableClientState(GL_VERTEX_ARRAY)
    glEnableClientState(GL_VERTEX_ARRAY)
    glEnableClientState(GL_NORMAL_ARRAY)
    #glEnableClientState(GL_COLOR_ARRAY)
    #glEnableClientState(GL_TEXTURE_COORD_ARRAY)
    #glRotate(180,1,0,0)
    glVertexPointer( 3, GL_FLOAT, opengl_surface["record_len"], opengl_surface["vertex_offset"] )
    glNormalPointer( GL_FLOAT, opengl_surface["record_len"], opengl_surface["normal_offset"])
    opengl_surface["indices"].bind()
    if True:
        glDrawElements( GL_TRIANGLE_STRIP,
                        len(opengl_surface["indices"]),
                        GL_UNSIGNED_BYTE,
                        opengl_surface["indices"] )

def main(init_stuff,display):
    glutInit(sys.argv)
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(1000,1000)
    glutCreateWindow(name)


    print "OpenGL Version",OpenGL.GL.glGetString(OpenGL.GL.GL_VERSION)

    def menu_callback( x ):
        print x
        sys.exit()
    glutCreateMenu(menu_callback)
    glutAddMenuEntry("Blah",1)
    glutAddMenuEntry("Blib",2)
    glutAttachMenu(GLUT_RIGHT_BUTTON)

    glClearColor(0.,0.,0.,1.)
    glShadeModel(GL_SMOOTH)
    #glEnable(GL_CULL_FACE)
    glEnable(GL_DEPTH_TEST)
    glEnable(GL_LIGHTING)

    lightZeroPosition = [10.,4.,10.,1.]
    lightZeroColor = [0.8,1.0,0.8,1.0] #green tinged
    glLightfv(GL_LIGHT0, GL_POSITION, lightZeroPosition)
    glLightfv(GL_LIGHT0, GL_DIFFUSE, lightZeroColor)
    glLightf(GL_LIGHT0, GL_CONSTANT_ATTENUATION, 0.1)
    glLightf(GL_LIGHT0, GL_LINEAR_ATTENUATION, 0.05)
    glEnable(GL_LIGHT0)

    init_stuff()

    def keypress_callback(key,x,y):
        global camera, angle
        def change_angle( angle, dirn, camera=camera,
                          angle_delta=0.01 ):
            if (camera["rpy"][angle]*dirn)<0:
                camera["rpy"][angle]=0
            else:
                camera["rpy"][angle] += dirn*angle_delta            
            pass
        acceleration = 0.02
        if key=='i': change_angle(0,+3.1415/4,angle_delta=1)
        if key=='o': change_angle(1,+3.1415/4,angle_delta=1)
        if key=='p': change_angle(1,+3.1415/4,angle_delta=1)
        if key=='w': change_angle(1,-1)
        if key=='s': change_angle(1, 1)
        if key=='z': change_angle(0,-1)
        if key=='c': change_angle(0,+1)
        if key=='a': change_angle(2,-1)
        if key=='d': change_angle(2,+1)
        if key==' ': camera["speed"] = 0
        if key==';': camera["speed"] += acceleration
        if key=='.': camera["speed"] -= acceleration
        if key=='e': camera["rpy"] = [0,0,0]
        if key=='r': camera["position"] = [0,0,-10]
        if key=='r': camera["facing"] = c_quaternion.identity()
        if key=='q':sys.exit()
    glutKeyboardFunc(keypress_callback)
    def display_func():
        display()
        #camera["rpy"] = [0,0,0]
        pass
    glutDisplayFunc(display_func)
    def callback():
        global angle, angle_speed
        #angle = angle + angle_speed
        #glutTimerFunc(delay,callback,handle+1)
        glutPostRedisplay()
        pass
    glutIdleFunc(callback)
    glutMainLoop()
    return

xxx = 0
yyy = 0
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
    global xxx
    xxx += 0.3
    brightness = 0.4
    glRotate(xxx,1,1,0)
    glTranslate(0.0 ,-0.75, 0.0)

    glMaterialfv(GL_FRONT,GL_DIFFUSE,[brightness*1.0,brightness*1.,brightness*0.,1.])
    glPushMatrix()
    glTranslate(0,0,1)
    stuff()
    glPopMatrix()
    glPushMatrix()
    glRotate(180,0,1,0)
    glTranslate(0,0,1)
    stuff()
    glPopMatrix()

    glMaterialfv(GL_FRONT,GL_DIFFUSE,[brightness*0.5,brightness*1.,brightness*0.,1.])
    glPushMatrix()
    glRotate(-90,0,1,0)
    glTranslate(0,0,1)
    stuff()
    glPopMatrix()
    glPushMatrix()
    glRotate(90,0,1,0)
    glTranslate(0,0,1)
    stuff()
    glPopMatrix()

    glMaterialfv(GL_FRONT,GL_DIFFUSE,[brightness*0,brightness*0.5,brightness*0.5,1.])
    glPushMatrix()
    glRotate(-90,1,0,0)
    glTranslate(0,0,1)
    stuff()
    glPopMatrix()
    glPushMatrix()
    glRotate(90,1,0,0)
    glTranslate(0,0,1)
    stuff()
    glPopMatrix()

    glPopMatrix()



    glutSwapBuffers()
    return

if __name__ == '__main__': main(init_stuff,display)

