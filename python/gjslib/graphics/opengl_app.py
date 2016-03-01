#!/usr/bin/env python

#a Imports
from OpenGL.GLUT import *
from OpenGL.GLU import *
from OpenGL.GL import *
import sys
import math
from gjslib.math import quaternion

#a Class for c_opengl
#c c_opengl_app
class c_opengl_app(object):
    window_title = "opengl_main"
    #f __init__
    def __init__(self, window_size):
        self.window_size = window_size
        self.display_has_errored = False
        pass
    #f window_xy
    def window_xy(self, xy):
        return ((xy[0]+1.0)*self.window_size[0]/2, (xy[1]+1.0)*self.window_size[1]/2)
    #f attach_menu
    def attach_menu(self, menu, name):
        glutSetMenu(menu.glut_id(name))
        glutAttachMenu(GLUT_RIGHT_BUTTON)
        pass
    #f init_opengl
    def init_opengl(self):
        glutInit(sys.argv)
        glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
        glutInitWindowSize(self.window_size[0],self.window_size[1])
        glutCreateWindow(self.window_title)

        glClearColor(0.,0.,0.,1.)
        glShadeModel(GL_SMOOTH)
        #glEnable(GL_CULL_FACE)
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_LIGHTING)

        lightZeroPosition = [10.,4.,10.,1.]
        glLightfv(GL_LIGHT0, GL_POSITION, lightZeroPosition)
        glLightfv(GL_LIGHT0, GL_DIFFUSE, [1.0,1.0,1.0,1.0] )
        glLightf(GL_LIGHT0, GL_CONSTANT_ATTENUATION, 0.1)
        glLightf(GL_LIGHT0, GL_LINEAR_ATTENUATION, 0.05)
        glEnable(GL_LIGHT0)
        self.opengl_post_init()
        pass
    #f main_loop
    def main_loop(self):
        glutKeyboardFunc(self.keypress_callback)
        glutMouseFunc(self.mouse_callback)
        glutDisplayFunc(self.display_callback)
        glutIdleFunc(self.idle_callback)
        glutMainLoop()
        return
    #f display_callback
    def display_callback(self):
        if (not self.display_has_errored):
            try:
                self.display()
            except:
                traceback.print_exc()
                self.display_has_errored = True
                pass
            pass
        pass
    #f keypress_callback
    def keypress_callback(self, key,x,y):
        m = glutGetModifiers()
        if self.keypress(key,m,x,y):
            return
        if ord(key)==17: # ctrl-Q
            sys.exit()
        pass
    #f mouse_callback
    def mouse_callback(self, button,state,x,y):
        m = glutGetModifiers()
        b = "left"
        s = "up"
        if state == GLUT_UP:   s="up"
        if state == GLUT_DOWN: s="down"
        if button == GLUT_LEFT_BUTTON:   b="left"
        if button == GLUT_MIDDLE_BUTTON: b="middle"
        if button == GLUT_RIGHT_BUTTON:  b="right"
        x = (2.0*x)/self.window_size[0]-1.0
        y = 1.0-(2.0*y)/self.window_size[1]
        self.mouse(b,s,m,x,y)
        pass
    #f idle_callback
    def idle_callback(self):
        self.idle()
        glutPostRedisplay()
        pass
    #f display
    def display(self):
        """
        Should be provided by the subclass
        """
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(40.,1.,1.,40.)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()

        glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)

        glutSwapBuffers()
        pass
    #f keypress
    def keypress(self, k, m, x, y):
        """
        Should be provided by the subclass
        """
        pass
    #f mouse
    def mouse(self, b, s, m, x, y):
        """
        Should be provided by the subclass
        """
        pass
    #f idle
    def idle(self):
        """
        Should be provided by the subclass
        """
        pass
    #f get_font
    def get_font(self, fontname):
        if fontname not in self.fonts:
            fontname = self.fonts.keys()[0]
            pass
        return self.fonts[fontname]
    #f load_font
    def load_font(self, bitmap_filename):
        import numpy
        bf = c_bitmap_font()
        bf.load(bitmap_filename)

        png_data = numpy.array(list(bf.image.getdata()), numpy.uint8)
        texture = glGenTextures(1)
        glPixelStorei(GL_UNPACK_ALIGNMENT,1)
        glBindTexture(GL_TEXTURE_2D, texture)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_MIRRORED_REPEAT)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_MIRRORED_REPEAT)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_R8, bf.image_size[0], bf.image_size[1], 0, GL_RED, GL_UNSIGNED_BYTE, png_data)
        glFlush()
        self.fonts[bf.fontname] = (bf, texture)
        return bf
    #f All done
    pass

#c c_opengl_camera_app
class c_opengl_camera_app(c_opengl_app):
    #f __init__
    def __init__(self, **kwargs):
        c_opengl_app.__init__(self, **kwargs)
        self.camera = {"position":[0,0,-10],
                       "facing":quaternion.c_quaternion.identity(),
                       "rpy":[0,0,0],
                       "speed":0,
                       "fov":90,
                       }
        pass
    #f change_angle
    def change_angle(self, angle, dirn, angle_delta=0.01 ):
        if (self.camera["rpy"][angle]*dirn)<0:
            self.camera["rpy"][angle]=0
            pass
        else:
            self.camera["rpy"][angle] += dirn*angle_delta            
            pass
        pass
    #f change_position
    def change_position(self, x,y,z ):
        scale = 0.1+self.camera["speed"]*5
        self.camera["position"] = [self.camera["position"][0]+x*scale,
                                   self.camera["position"][1]+y*scale,
                                   self.camera["position"][2]+z*scale
                                   ]
        pass
    #f keypress
    def keypress(self, key,m,x,y):
        acceleration = 0.02
        if key=='i': self.change_angle(0,+3.1415/4,angle_delta=1)
        if key=='o': self.change_angle(1,+3.1415/4,angle_delta=1)
        if key=='p': self.change_angle(1,+3.1415/4,angle_delta=1)
        if key=='w': self.change_angle(1,-1)
        if key=='s': self.change_angle(1, 1)
        if key=='z': self.change_angle(0,-1)
        if key=='c': self.change_angle(0,+1)
        if key=='a': self.change_angle(2,-1)
        if key=='d': self.change_angle(2,+1)

        if key=='W': self.change_position(0,0,-1)
        if key=='S': self.change_position(0,0,+1)
        if key=='Z': self.change_position(0,-1,0)
        if key=='C': self.change_position(0,+1,0)
        if key=='A': self.change_position(1,0,0)
        if key=='D': self.change_position(-1,0,0)

        if key==';': self.camera["speed"] += acceleration
        if key=='.': self.camera["speed"] -= acceleration

        if key=='[': self.change_fov(-1)
        if key==']': self.change_fov(+1)
        if key==' ': self.camera["speed"] = 0
        if key=='e': self.camera["rpy"] = [0,0,0]
        if key=='r': self.camera["position"] = [0,0,-10]
        if key=='r': self.camera["facing"] = quaternion.c_quaternion.identity()
        if key=='r': self.camera["fov"] = 90
        pass
    #f opengl_post_init
    def opengl_post_init(self):
        pass
    #f display
    def display(self):
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(40.,1.,1.,40.)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()

        self.camera["facing"] = quaternion.c_quaternion.roll(self.camera["rpy"][0]).multiply(self.camera["facing"])
        self.camera["facing"] = quaternion.c_quaternion.pitch(self.camera["rpy"][1]).multiply(self.camera["facing"])
        self.camera["facing"] = quaternion.c_quaternion.yaw(self.camera["rpy"][2]).multiply(self.camera["facing"])

        m = self.camera["facing"].get_matrix()
        self.camera["position"][0] += self.camera["speed"]*m[0][2]
        self.camera["position"][1] += self.camera["speed"]*m[1][2]
        self.camera["position"][2] += self.camera["speed"]*m[2][2]

        glMultMatrixf(m)
        glTranslate(self.camera["position"][0],self.camera["position"][1],self.camera["position"][2])

        glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)
        pass

    #f All done
    pass

#a Test app
class c_opengl_test_app(c_opengl_camera_app):
    use_primitive_restart = False
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
    #f __init__
    def __init__(self, patch_name, **kwargs):
        c_opengl_camera_app.__init__(self, **kwargs)
        self.patch = self.patches[patch_name]
        self.opengl_surface = {}
        self.xxx = 0.0
        self.yyy = 0.0
        self.window_title = "OpenGL Test app '%s'"%patch_name
        pass
    #f opengl_post_init
    def opengl_post_init(self):
        import OpenGL.arrays.vbo as vbo
        import numpy
        from gjslib.math import bezier
        from ctypes import sizeof, c_float, c_void_p, c_uint

        pts = []
        for coords in self.patch:
            pts.append( bezier.c_point(coords=coords) )
            pass
        bp = bezier.c_bezier_patch( pts=pts )

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

        vertices = vbo.VBO( data=numpy.array(data_array, dtype=numpy.float32) )
        index_list = []
        if self.use_primitive_restart:
            glEnable(GL_PRIMITIVE_RESTART) 
            pass
        for j in range(n):
            for i in range(n+1):
                index_list.append( i+j*(n+1) )
                index_list.append( i+(j+1)*(n+1) )
                pass
            if j<(n-1):
                if self.use_primitive_restart:
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
        self.opengl_surface["vertices"] = vertices
        self.opengl_surface["indices"] = indices
        self.opengl_surface["vertex_offset"] = vertex_offset
        self.opengl_surface["normal_offset"] = normal_offset
        self.opengl_surface["record_len"] = record_len
        pass
    #f display
    def display(self):
        c_opengl_camera_app.display(self)
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

        glMaterialfv(GL_FRONT,GL_AMBIENT,[0.1,0.1,0.1,1.0])
        glPushMatrix()
        #glTranslate(0.0 ,2.75, 0.0)
        color = [0.5,0,0.,0.,1.]
        glMaterialfv(GL_FRONT,GL_DIFFUSE,color)
        #glutSolidSphere(2,40,40)
        glutSolidOctahedron()
        glPopMatrix()

        glPushMatrix()
        self.xxx += 0.3
        brightness = 0.4
        glRotate(self.xxx,1,1,0)
        glTranslate(0.0 ,-0.75, 0.0)

        glMaterialfv(GL_FRONT,GL_DIFFUSE,[brightness*1.0,brightness*1.,brightness*0.,1.])
        glPushMatrix()
        glTranslate(0,0,1)
        self.draw_object()
        glPopMatrix()
        glPushMatrix()
        glRotate(180,0,1,0)
        glTranslate(0,0,1)
        self.draw_object()
        glPopMatrix()

        glMaterialfv(GL_FRONT,GL_DIFFUSE,[brightness*0.5,brightness*1.,brightness*0.,1.])
        glPushMatrix()
        glRotate(-90,0,1,0)
        glTranslate(0,0,1)
        self.draw_object()
        glPopMatrix()
        glPushMatrix()
        glRotate(90,0,1,0)
        glTranslate(0,0,1)
        self.draw_object()
        glPopMatrix()

        glMaterialfv(GL_FRONT,GL_DIFFUSE,[brightness*0,brightness*0.5,brightness*0.5,1.])
        glPushMatrix()
        glRotate(-90,1,0,0)
        glTranslate(0,0,1)
        self.draw_object()
        glPopMatrix()
        glPushMatrix()
        glRotate(90,1,0,0)
        glTranslate(0,0,1)
        self.draw_object()
        glPopMatrix()

        glPopMatrix()
        glutSwapBuffers()
        pass
    #f draw_object
    def draw_object(self):
        self.opengl_surface["vertices"].bind()
        glEnableClientState(GL_VERTEX_ARRAY)
        glEnableClientState(GL_VERTEX_ARRAY)
        glEnableClientState(GL_NORMAL_ARRAY)
        glVertexPointer( 3, GL_FLOAT, self.opengl_surface["record_len"], self.opengl_surface["vertex_offset"] )
        glNormalPointer( GL_FLOAT,    self.opengl_surface["record_len"], self.opengl_surface["normal_offset"])
        self.opengl_surface["indices"].bind()
        glDrawElements( GL_TRIANGLE_STRIP,
                        len(self.opengl_surface["indices"]),
                        GL_UNSIGNED_BYTE,
                        self.opengl_surface["indices"] )

        pass
    #f All done
    pass
        
#a Toplevel
if __name__ == '__main__':
    a = c_opengl_test_app(patch_name="bump_one", window_size=(1000,1000))
    a.init_opengl()
    a.main_loop()
    pass

