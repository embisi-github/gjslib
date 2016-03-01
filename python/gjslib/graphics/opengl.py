#!/usr/bin/env python

#a Imports
from OpenGL.GLUT import *
from OpenGL.GLU import *
from OpenGL.GL import *
import sys
import math
from gjslib.math.quaternion import c_quaternion
from gjslib.math import matrix
from gjslib.graphics.font import c_bitmap_font

#a Useful functions
#f texture_from_png
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
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP)
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP)
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, png.size[0], png.size[1], 0, GL_RGB, GL_UNSIGNED_BYTE, png_data)
    glFlush()
    return texture

#f transformation
def transformation(translation=None, scale=None, rotation=None, map_xywh=None, inv_map_xywh=None):
    """
    First, map xywh to another xywh
    For this, use ( (ix,iy,iw,ih) -> (ox,oy,ow,oh) ) (input -> output)

    Then apply roll, pitch, yaw

    Then scale by scale (float or 2/3-tuple of floats)

    Then translate by 2/3-tuple

    Return column-major matrix for OpenGL operations; can use glMultMatrixf(m)...

    Note that the operations are applied to the object in bottom-up order
    """
    m = matrix.c_matrix4x4()
    if map_xywh is not None:
        if len(map_xywh)==2:
            (inv_map_xywh, map_xywh) = map_xywh
            pass
        pass
    if map_xywh is not None:
        (x,y,w,h) = map_xywh
        # Map (-1,-1) to (x,y); map (1,1) to (x+w, y+h)
        # So translate by +1,+1; then scale by w/2, h/2; then translate by x,y
        # Operations are reversed (as last is applied first to our object)
        m.translate(xyz=(x,y,0.0))
        m.scale(scale=(w/2.0,h/2.0,1.0))
        m.translate(xyz=(1.0,1.0,0.0))
        pass
    if inv_map_xywh is not None:
        (x,y,w,h) = inv_map_xywh
        # Map (x,y) to (-1,-1); map (x+w, y+h) to (1,1)
        # So translate by -x,-y; then scale by 2/w, 2/h; then translate by -1,-1
        # Operations are reversed (as last is applied first to our object)
        m.translate(xyz=(-1.0,-1.0,0.0))
        m.scale(scale=(2.0/w,2.0/h,1.0))
        m.translate(xyz=(-x,-y,0.0))
        pass
    q = c_quaternion.identity()
    if rotation is not None:
        for (k,f) in [("roll", c_quaternion.roll),
                      ("pitch", c_quaternion.pitch),
                      ("yaw", c_quaternion.yaw)]:
            if k in rotation: q = f(rotation["k"]).multiply(q)
            pass
        pass
    m.mult4x4(q.get_matrix4())
    if scale is not None:
        scale_matrix = matrix.c_matrix4x4()
        scale_matrix.scale(scale)
        m.mult4x4(scale_matrix)
        pass
    if translation is not None:
        if len(translation)==2: translation=(translation[0], translation[1], 0.0)
        m.translate(xyz=translation)
        pass
    return m.get_matrix(row_major=False)
    
#a Base useful classes
#c c_depth_contents_iter
class c_depth_contents_iter(object):
    def __init__(self, dc):
        self.dc = dc
        self.depths = dc.contents.keys()
        self.content_index = 0
        pass
    def next(self):
        if len(self.depths)==0:
            raise StopIteration()
        d = self.depths[0]
        if d not in self.dc.contents:
            raise StopIteration()
        if self.content_index<len(self.dc.contents[d]):
            self.content_index += 1
            return self.dc.contents[d][self.content_index-1]
        self.content_index = 0
        self.depths.pop(0)
        return self.next()
        
#c c_depth_contents
class c_depth_contents(object):
    #f __init__
    def __init__(self):
        self.contents = {}
        pass
    pass
    #f clear_contents
    def clear_contents(self, depth=None):
        if depth is None:
            self.contents = {}
            return
        if depth in self.contents:
            self.contents[depth] = []
            pass
        pass
    #f add_contents
    def add_contents(self, content, depth=0):
        if depth not in self.contents:
            self.contents[depth] = []
            pass
        self.contents[depth].append(content)
        pass
    #f remove_contents
    def remove_contents(self, content, depth=None):
        for d in self.contents:
            if (depth is not None) and (d!=depth):
                continue
            self.contents[d].remove(content)
            return
        raise Exception("Failed to find content to remove (at specified depth)")
    #f __iter__
    def __iter__(self):
        return c_depth_contents_iter(self)
    #f All done
    pass

#a Class for c_opengl
#c c_opengl
class c_opengl(object):
    #f __init__
    def __init__(self, window_size):
        global camera
        self.menu_dict = {"menus":{}, "ids":[]}
        self.window_size = window_size
        self.display_has_errored = False
        self.callbacks = {}
        self.camera = {"position":[0,0,-10],
                       "facing":c_quaternion.identity(),
                       "rpy":[0,0,0],
                       "speed":0,
                       "fov":90,
                       }
        camera = self.camera
        self.fonts = {}
        pass
    #f window_xy
    def window_xy(self, xy):
        return ((xy[0]+1.0)*self.window_size[0]/2, (xy[1]+1.0)*self.window_size[1]/2)
    #f destroy_menus
    def destroy_menus(self):
        if len(self.menu_dict["menus"])==0:
            return
        glutDetachMenu()
        for m in self.menu_dict["menus"]:
            glutDeleteMenu(self.menu_dict["menus"][m]["glut"])
            pass
        self.menu_dict = {"menus":{}, "ids":[]}
        pass
    #f create_menus
    def create_menus(self, menus):
        self.destroy_menus()
        if menus is not None:
            self.menu_dict["ids"] = menus["ids"]
            for (name, items) in menus["menus"]:
                m = glutCreateMenu(lambda x:self.menu_callback(name,x))
                self.menu_dict["menus"][name] = {"glut":m}
                for (text,item) in items:
                    if type(item)==int:
                        glutAddMenuEntry(text,item)
                        pass
                    else:
                        glutAddSubMenu(text,self.menu_dict["menus"][item]["glut"])
                        pass
                    pass
                pass
            pass
        pass
    #f build_menu_init
    def build_menu_init(self):
        return {"ids":[], "menus":[]}
    #f build_menu_add_menu
    def build_menu_add_menu(self,menus,menu_name):
        menus["menus"].append( (menu_name,[]) )
        pass
    #f build_menu_add_menu_item
    def build_menu_add_menu_item(self,menus,text,item_id):
        menus["menus"][-1][1].append( (text,len(menus["ids"])) )
        menus["ids"].append(item_id)
        pass
    #f build_menu_add_menu_submenu
    def build_menu_add_menu_submenu(self,menus,text,menu_name):
        menus["menus"][-1][1].append( (text,menu_name) )
        return
    #f mouse_callback
    def mouse_callback(self, button,state,x,y):
        m = glutGetModifiers()
        b = "left"
        s = "up"
        if state == GLUT_UP: s="up"
        if state == GLUT_DOWN: s="down"
        if button == GLUT_LEFT_BUTTON: b="left"
        if button == GLUT_MIDDLE_BUTTON: b="middle"
        if button == GLUT_RIGHT_BUTTON: b="right"
        x = (2.0*x)/self.window_size[0]-1.0
        y = 1.0-(2.0*y)/self.window_size[1]
        if ("mouse" in self.callbacks) and (self.callbacks["mouse"] is not None):
            self.callbacks["mouse"](b,s,m,x,y)
            pass
        pass
    #f change_fov
    def change_fov(self, fov):
        self.camera["fov"] += fov
        if self.camera["fov"]<10:  self.camera["fov"]=10
        if self.camera["fov"]>140: self.camera["fov"]=140
        pass
    #f attach_menu
    def attach_menu(self,menu_name):
        glutSetMenu(self.menu_dict["menus"][menu_name]["glut"])
        glutAttachMenu(GLUT_RIGHT_BUTTON)
    pass
    #f menu_callback
    def menu_callback(self, name, x):
        if (x>=0) and (x<=len(self.menu_dict["ids"])):
            x = self.menu_dict["ids"][x]
            pass
        if ("menu" in self.callbacks) and (self.callbacks["menu"] is not None):
            if self.callbacks["menu"](name,x):
                return 0
            pass
        print x
        sys.exit()
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
    #f keypress_callback
    def keypress_callback(self, key,x,y):
        m = glutGetModifiers()
        if ("keyboard" in self.callbacks) and (self.callbacks["keyboard"] is not None):
            if self.callbacks["keyboard"](key,m,x,y):
                return
            pass
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
        if key=='r': self.camera["facing"] = c_quaternion.identity()
        if key=='r': self.camera["fov"] = 90
        if key=='q':sys.exit()
        pass
    #f display_callback
    def display_callback(self):
        display = None
        if ("display" in self.callbacks):
            display = self.callbacks["display"]
            pass
        if (display is not None) and (not self.display_has_errored):
            try:
                display()
            except:
                traceback.print_exc()
                self.display_has_errored = True
                pass
            pass
        pass
    #f init_opengl
    def init_opengl(self):
        glutInit(sys.argv)
        glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
        glutInitWindowSize(self.window_size[0],self.window_size[1])
        glutCreateWindow("opengl_main")

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
        pass
    #f idle_callback
    def idle_callback(self):
        if ("idle" in self.callbacks) and (self.callbacks["idle"] is not None):
            if self.callbacks["idle"]():
                return
            pass
        #global angle, angle_speed
        #angle = angle + angle_speed
        #glutTimerFunc(delay,callback,handle+1)
        glutPostRedisplay()
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
    #f main_loop
    def main_loop(self, idle_callback=None, display_callback=None, mouse_callback=None, keyboard_callback=None, menu_callback=None):
        self.callbacks["idle"] = idle_callback
        self.callbacks["display"] = display_callback
        self.callbacks["mouse"] = mouse_callback
        self.callbacks["keyboard"] = keyboard_callback
        self.callbacks["menu"] = menu_callback

        glutKeyboardFunc(self.keypress_callback)
        glutMouseFunc(self.mouse_callback)
        glutDisplayFunc(self.display_callback)
        glutIdleFunc(self.idle_callback)
        glutMainLoop()
        
        return
    pass


#a Toplevel

name = 'ball_glut'

camera = {"position":[0,0,-10],
          "facing":c_quaternion.identity(),
          "rpy":[0,0,0],
          "speed":0,
          "fov":90,
          }
angle_speed = 0.0
delay = 40
delay = 100
use_primitive_restart = False
from gjslib.math import bezier
#import bezier
import array
opengl_surface = {}


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

display_has_errored = False
window_size = (1000,1000)
def attach_menu(menu_name):
    global menu_dict
    glutSetMenu(menu_dict[menu_name]["glut"])
    glutAttachMenu(GLUT_RIGHT_BUTTON)
    pass

def main(init_stuff,display,mouse=None,keyboard=None,menus=None):
    global window_size, menu_dict
    glutInit(sys.argv)
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(window_size[0],window_size[1])
    glutCreateWindow("opengl_main")


    print "OpenGL Version",OpenGL.GL.glGetString(OpenGL.GL.GL_VERSION)

    def menu_callback(name, x ):
        print x
        sys.exit()
        pass
    if menus is not None:
        menu_dict = {}
        for (name, items) in menus:
            m = glutCreateMenu(lambda x:menu_callback(name,x))
            menu_dict[name] = {"glut":m}
            for (text,item) in items:
                if type(item)==int:
                    glutAddMenuEntry(text,item)
                    pass
                else:
                    glutAddSubMenu(text,menu_dict[item]["glut"])
                pass
            pass
        pass

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

    def mouse_callback(button,state,x,y,mouse=mouse):
        #glutGetModifiers()
        global window_size
        b = "left"
        s = "up"
        if state == GLUT_UP: s="up"
        if state == GLUT_DOWN: s="down"
        if button == GLUT_LEFT_BUTTON: b="left"
        if button == GLUT_MIDDLE_BUTTON: b="middle"
        if button == GLUT_RIGHT_BUTTON: b="right"
        x = (2.0*x)/window_size[0]-1.0
        y = 1.0-(2.0*y)/window_size[1]
        if mouse:
            mouse(b,s,x,y)
            pass
        pass
    def keypress_callback(key,x,y):
        global camera, angle
        def change_fov(fov):
            camera["fov"] += fov
            if camera["fov"]<10: camera["fov"]=10
            if camera["fov"]>140: camera["fov"]=140
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
        if key=='[': change_fov(-1)
        if key==']': change_fov(+1)
        if key==' ': camera["speed"] = 0
        if key==';': camera["speed"] += acceleration
        if key=='.': camera["speed"] -= acceleration
        if key=='e': camera["rpy"] = [0,0,0]
        if key=='r': camera["position"] = [0,0,-10]
        if key=='r': camera["facing"] = c_quaternion.identity()
        if key=='r': camera["fov"] = 90
        if key=='q':sys.exit()
        pass
    glutKeyboardFunc(keypress_callback)
    glutMouseFunc(mouse_callback)
    def display_func():
        global display_has_errored
        if not display_has_errored:
            try:
                display()
            except:
                traceback.print_exc()
                display_has_errored = True
                pass
            pass
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

if __name__ == '__main__':
    a = c_opengl(window_size = (1000,1000))
    a.init_opengl()
    init_stuff()
    a.main_loop(display_callback=display)
    #main(init_stuff,display)

