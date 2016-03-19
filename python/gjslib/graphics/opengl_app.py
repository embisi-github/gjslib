#!/usr/bin/env python

#a Imports
from OpenGL.GLUT import *
from OpenGL.GLU import *
from OpenGL.GL import *
from OpenGL.GL import shaders
import sys
import math
from gjslib.math import quaternion, matrix, vectors
import OpenGL.arrays.vbo as vbo
import numpy

#a Default shaders
shader_code={}
shader_code["standard_vertex"] = """
#version 330 core
layout(location = 0) in vec3 V_m;
layout(location = 1) in vec2 V_UV;
layout(location = 2) in vec3 N_m;
out vec2 UV;
out vec3 V_w;
out vec3 V_c;
uniform mat4 M;
uniform mat4 V;
uniform mat4 P;
void main(){
    V_w = (M * vec4(V_m,1)).xyz + 0*N_m;// Use N_m or lose it...
    V_c = (V * M * vec4(V_m,1)).xyz;
    gl_Position =  P * V * M * vec4(V_m,1);
    UV = V_UV;
}
"""
shader_code["standard_fragment"] = """
#version 330 core
in vec3 V_m;
in vec2 V_UV;
in vec3 N_m;
out vec4 color;
uniform vec3 C;
void main(){
    color = vec4(C,1);
}
"""
shader_code["texture_fragment"] = """
#version 330 core
in vec3 V_w;
in vec2 UV;
in vec3 V_c;
out vec3 color;
uniform sampler2D sampler;
void main(){
    color = texture(sampler,UV).rgb*0.7;
}
"""
shader_code["font_fragment"] = """
#version 330 core
in vec3 V_w;
in vec2 UV;
in vec3 V_c;
out vec4 color;
uniform sampler2D sampler;
uniform vec3 C;
void main(){
    color = texture(sampler,UV).r * vec4(C,1.0);
    if (texture(sampler,UV).r<0.1) discard;
}
"""

#a Shader classes - move to opengl_shader
class c_opengl_shader(object):
    #f __init__
    def __init__(self):
        pass
    #f compile
    def compile(self):
        self.vao = glGenVertexArrays(1)
        glBindVertexArray(self.vao)
        self.vertex_shader   = shaders.compileShader(self.vertex_src, GL_VERTEX_SHADER)
        self.fragment_shader = shaders.compileShader(self.fragment_src, GL_FRAGMENT_SHADER)
        self.program          = shaders.compileProgram(self.vertex_shader, self.fragment_shader)
        self.attrib_ids = {}
        for k in self.attribs:
            self.attrib_ids[k] = glGetAttribLocation(self.program,k)
            pass
        self.uniform_ids = {}
        for k in self.uniforms:
            self.uniform_ids[k] = glGetUniformLocation(self.program,k)
            pass

        for k in self.attrib_ids:
            if self.attrib_ids[k]==-1:
                raise Exception("Failed to create attribute",k)
            pass
        for k in self.uniform_ids:
            if self.uniform_ids[k]==-1:
                raise Exception("Failed to create uniform",k)
            pass
        pass
    #f use
    def use(self):
        shaders.glUseProgram(self.program)
        pass
    #f bind_vbo
    def bind_vbo(self, t=None, v=None, n=None, uv=None, **kwargs):
        from ctypes import sizeof, c_float, c_void_p, c_uint
        for (d,k,s) in ( (v,"V_m",3), (n,"N_m",3),  (uv,"V_UV",2) ):
            if d is not None and k in self.attrib_ids:
                glEnableVertexAttribArray(self.attrib_ids[k])
                glVertexAttribPointer(self.attrib_ids[k], s, GL_FLOAT, GL_FALSE, t*sizeof(c_float), c_void_p(d*sizeof(c_float)) )
            pass
        for (k,v) in kwargs.iteritems():
            if k in self.uniform_ids:
                if type(v)==float:
                    glUniformMatrix1f(self.uniform_ids[k],v)
                    pass
                elif len(v)==3:
                    glUniform3f(self.uniform_ids[k],v[0],v[1],v[2])
                    pass
                elif len(v)==4:
                    glUniform4f(self.uniform_ids[k],v[0],v[1],v[2],v[3])
                    pass
                pass
            pass
        pass
    #f set_matrices
    def set_matrices(self, matrix_stacks):
        glUniformMatrix4fv(self.uniform_ids["M"],1,GL_TRUE,matrix_stacks["model"][-1].get_matrix())
        glUniformMatrix4fv(self.uniform_ids["V"],1,GL_TRUE,matrix_stacks["view"][-1].get_matrix())
        glUniformMatrix4fv(self.uniform_ids["P"],1,GL_TRUE,matrix_stacks["project"][-1].get_matrix())
        pass
    #f All done
    pass

#c c_opengl_shader_color_standard
class c_opengl_shader_color_standard(c_opengl_shader):
    vertex_src   = shader_code["standard_vertex"]
    fragment_src = shader_code["standard_fragment"]
    attribs      = ("V_m", "V_UV", "N_m")
    uniforms     = ("M", "V", "P", "C")
    pass

#c c_opengl_shader_texture_standard
class c_opengl_shader_texture_standard(c_opengl_shader):
    vertex_src   = shader_code["standard_vertex"]
    fragment_src = shader_code["texture_fragment"]
    attribs      = ("V_m", "V_UV", "N_m")
    uniforms     = ("M", "V", "P")
    pass

#c c_opengl_shader_font_standard
class c_opengl_shader_font_standard(c_opengl_shader):
    vertex_src   = shader_code["standard_vertex"]
    fragment_src = shader_code["font_fragment"]
    attribs      = ("V_m", "V_UV", "N_m")
    uniforms     = ("M", "V", "P", "C")
    pass

#a Class for c_opengl
#c c_opengl_app
class c_opengl_app(object):
    window_title = "opengl_main"
    #f __init__
    def __init__(self, window_size):
        self.window_size = window_size
        self.display_has_errored = False
        self.fonts = {}
        self.display_matrices = {"model":  [matrix.c_matrixNxN(order=4).identity()],
                                 "view":   [matrix.c_matrixNxN(order=4).identity()],
                                 "project":[matrix.c_matrixNxN(order=4).identity()],
                                 }
        self.clips = []
        self.selected_shader = None
        self.simple_object = {}
        self.simple_object["cross"] = {"vectors":vbo.VBO(data=numpy.array([1.0,0.2,0, -1.0,0.2,0, 1.0,-0.2,0, -1.0,-0.2,0, 
                                                                           0.2,1.0,0, 0.2,-1.0,0, -0.2,1.0,0, -0.2,-1.0,0, ],
                                                                          dtype=numpy.float32), target=GL_ARRAY_BUFFER ),
                                       "indices":vbo.VBO(data=numpy.array([0,1,2,1,2,3,4,5,6,5,6,7],
                                                                          dtype=numpy.uint8), target=GL_ELEMENT_ARRAY_BUFFER ),
                                       }
        self.simple_object["diamond"] = {"vectors":vbo.VBO(data=numpy.array([1,0,0, -1,0,0, 0,1,0, 0,-1,0, 0,0,1, 0,0,-1],
                                                                            dtype=numpy.float32), target=GL_ARRAY_BUFFER ),
                                         "indices":vbo.VBO(data=numpy.array([0,2,4, 0,2,5, 0,3,4, 0,3,5,
                                                                             1,2,4, 1,2,5, 1,3,4, 1,3,5],
                                                                            dtype=numpy.uint8), target=GL_ELEMENT_ARRAY_BUFFER ),
                                         }
        pass
    #f window_xy
    def window_xy(self, xy):
        return ((xy[0]+1.0)*self.window_size[0]/2, (xy[1]+1.0)*self.window_size[1]/2)
    #f uniform_xy
    def uniform_xy(self, xy):
        return (-1.0+2*float(xy[0])/self.window_size[0], -1.0+2*float(xy[1])/self.window_size[1])
    #f attach_menu
    def attach_menu(self, menu, name):
        glutSetMenu(menu.glut_id(name))
        glutAttachMenu(GLUT_RIGHT_BUTTON)
        pass
    #f clip_push
    def clip_push(self, x,y,w,h):
        x,y,w,h = int(x),int(y),int(w),int(h)
        self.clips.append((x,y,w,h))
        glViewport(x,y,w,h)
        glScissor(x,y,w,h)
        glEnable(GL_SCISSOR_TEST)
        pass
    #f clip_pop
    def clip_pop(self, matrix="model"):
        self.clips.pop()
        if len(self.clips)==0:
            (x,y,w,h) = (0,0,self.window_size[0],self.window_size[1])
            glDisable(GL_SCISSOR_TEST)
            pass
        else:
            (x,y,w,h) = self.clips[-1]
            pass
        glViewport(x,y,w,h)
        glScissor(x,y,w,h)
        pass
    #f matrix_push
    def matrix_push(self, matrix="model"):
        m = self.display_matrices[matrix][-1].copy()
        self.display_matrices[matrix].append(m)
        if len(self.display_matrices[matrix])>100:
            raise Exception("Too many matrices pushed")
        pass
    #f matrix_pop
    def matrix_pop(self, matrix="model"):
        m = self.display_matrices[matrix].pop()
        pass
    #f matrix_mult
    def matrix_mult(self, by, matrix="model"):
        self.display_matrices[matrix][-1].postmult(by)
        pass
    #f matrix_scale
    def matrix_scale(self, scale=1.0, matrix="model"):
        if type(scale)==float:
            scale = (scale,scale,scale,1.0)
            pass
        self.display_matrices[matrix][-1].scale(scale)
        pass
    #f matrix_rotate
    def matrix_rotate(self, angle, axis, matrix="model"):
        q = quaternion.c_quaternion.of_rotation(angle=angle, axis=axis, degrees=True)
        self.display_matrices[matrix][-1].postmult(q.get_matrixn(order=4))
        pass
    #f matrix_translate
    def matrix_translate(self, translate, matrix="model"):
        self.display_matrices[matrix][-1].translate(translate)
        pass
    #f matrix_set
    def matrix_set(self, m, matrix="project"):
        self.display_matrices[matrix][-1] = m
        pass
    #f matrix_identity
    def matrix_identity(self, matrix="model"):
        self.display_matrices[matrix][-1].identity()
        pass
    #f matrix_perspective
    def matrix_perspective(self, fovx=None, fovy=None, aspect=1.0, zNear=None, zFar=None, matrix="project"):
        m = self.display_matrices[matrix][-1]
        for r in range(4):
            for c in range(4):
                m[r,c] = 0.0
                pass
            pass
        if fovx is None:
            fy = 1/math.tan(math.radians(fovy)/2)
            fx = fy/aspect
            pass
        else:
            fx = 1/math.tan(math.radians(fovx)/2)
            if fovy is None:
                fy = fx*aspect
                pass
            else:
                fy = 1/math.tan(math.radians(fovy)/2)
                pass
            pass
        m[0,0] = fx
        m[1,1] = fy
        m[2,2] = (zNear+zFar)/(zNear-zFar)
        m[2,3] = 2*zNear*zFar/(zNear-zFar)
        m[3,2] = -1.0
        pass
    #f matrix_use
    def matrix_use(self):
        self.selected_shader.set_matrices(self.display_matrices)
        pass
    #f shaders_compile
    def shaders_compile(self):
        self.shaders = {}
        self.shaders["color_standard"]   = c_opengl_shader_color_standard()
        self.shaders["texture_standard"] = c_opengl_shader_texture_standard()
        self.shaders["font_standard"]    = c_opengl_shader_font_standard()
        for k in self.shaders:
            self.shaders[k].compile()
        pass
    #f shader_set_attributes
    def shader_set_attributes(self, **kwargs):
        self.selected_shader.bind_vbo(**kwargs)
        pass
    #f shader_use
    def shader_use(self,shader_name="color_standard"):
        self.selected_shader = self.shaders[shader_name]
        self.selected_shader.use()
        pass
    #f draw_simple_object
    def draw_simple_object(self, obj, c, xyz, sc, angle=0, axis=(0,0,1)):
        self.matrix_push()
        self.matrix_translate(xyz)
        self.matrix_rotate(angle, axis)
        self.matrix_scale(sc)
        self.matrix_use()
        self.simple_object[obj]["vectors"].bind()
        self.simple_object[obj]["indices"].bind()
        self.shader_set_attributes( t=3, v=0, C=c )
        glDrawElements(GL_TRIANGLES,len(self.simple_object[obj]["indices"]),GL_UNSIGNED_BYTE, None) 
        self.simple_object[obj]["vectors"].unbind()
        self.simple_object[obj]["indices"].unbind()
        self.matrix_pop()
        pass
    #f draw_lines
    def draw_lines(self, line_data):
        vectors = vbo.VBO(data=numpy.array(line_data, dtype=numpy.float32), target=GL_ARRAY_BUFFER )
        vectors.bind()
        self.shader_set_attributes(t=3, v=0)
        glDrawArrays(GL_LINES,0,len(line_data))
        vectors.unbind()
        pass
    #f init_opengl
    def init_opengl(self):
        glutInit(sys.argv)
        glutInitDisplayMode(GLUT_3_2_CORE_PROFILE |GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
        glutInitWindowSize(self.window_size[0],self.window_size[1])
        glutCreateWindow(self.window_title)

        #print glGetString(GL_VERSION)

        self.shaders_compile()
        self.shader_use()

        glClearColor(0.,0.,0.,1.)
        #glShadeModel(GL_SMOOTH)
        #glEnable(GL_CULL_FACE)
        glEnable(GL_DEPTH_TEST)
        self.opengl_post_init()
        pass
    #f opengl_post_init
    def opengl_post_init(self):
        """Subclass should provide this"""
        pass
    #f main_loop
    def main_loop(self):
        glutKeyboardFunc(self.keypress_callback)
        glutKeyboardUpFunc(self.keyrelease_callback)
        glutMouseFunc(self.mouse_callback)
        glutMotionFunc(self.motion_callback)
        glutDisplayFunc(self.display_callback)
        glutIdleFunc(self.idle_callback)
        glutIgnoreKeyRepeat(True)
        glutMainLoop()
        return
    #f display_callback
    def display_callback(self):
        if (not self.display_has_errored):
            try:
                self.display()
            except SystemExit as e:
                raise
            except:
                traceback.print_exc()
                self.display_has_errored = True
                pass
            pass
        pass
    #f keypress_callback
    def keypress_callback(self, key,x,y):
        w = glutGet(GLUT_WINDOW_WIDTH)
        h = glutGet(GLUT_WINDOW_HEIGHT)
        y = h-y # Invert y as OpenGL want it from BL
        m = glutGetModifiers()
        if self.keypress(key,m,x,y):
            return
        if ord(key)==17: # ctrl-Q
            sys.exit()
        pass
    #f keyrelease_callback
    def keyrelease_callback(self, key,x,y):
        w = glutGet(GLUT_WINDOW_WIDTH)
        h = glutGet(GLUT_WINDOW_HEIGHT)
        y = h-y # Invert y as OpenGL want it from BL
        m = glutGetModifiers()
        if self.keyrelease(key,m,x,y):
            return
        if ord(key)==17: # ctrl-Q
            sys.exit()
        pass
    #f mouse_callback
    def mouse_callback(self, button,state,x,y):
        w = glutGet(GLUT_WINDOW_WIDTH)
        h = glutGet(GLUT_WINDOW_HEIGHT)
        y = h-y # Invert y as OpenGL want it from BL
        m = glutGetModifiers()
        b = "left"
        s = "up"
        if state == GLUT_UP:   s="up"
        if state == GLUT_DOWN: s="down"
        if button == GLUT_LEFT_BUTTON:   b="left"
        if button == GLUT_MIDDLE_BUTTON: b="middle"
        if button == GLUT_RIGHT_BUTTON:  b="right"
        self.mouse(b,s,m,x,y)
        pass
    #f motion_callback
    def motion_callback(self, x,y):
        w = glutGet(GLUT_WINDOW_WIDTH)
        h = glutGet(GLUT_WINDOW_HEIGHT)
        y = h-y # Invert y as OpenGL want it from BL
        self.motion(x,y)
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
        glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)

        glutSwapBuffers()
        pass
    #f keypress
    def keypress(self, k, m, x, y):
        """
        Should be provided by the subclass
        """
        pass
    #f keyrelease
    def keyrelease(self, k, m, x, y):
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
    #f motion
    def motion(self, x, y):
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
        from gjslib.graphics.font import c_bitmap_font
        bf = c_bitmap_font()
        bf.load(bitmap_filename)

        png_data = numpy.array(list(bf.image.getdata()), numpy.uint8)
        texture = glGenTextures(1)
        glPixelStorei(GL_UNPACK_ALIGNMENT,1)
        glBindTexture(GL_TEXTURE_2D, texture)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_MIRRORED_REPEAT)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_MIRRORED_REPEAT)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_R8, bf.image_size[0], bf.image_size[1], 0, GL_RED, GL_UNSIGNED_BYTE, png_data)
        glFlush()
        self.fonts[bf.fontname] = (bf, texture)
        return bf
    #f debug
    def debug(self, reason, options=None):
        print "*"*80
        print "opengl_app.debug",reason
        print "*"*80
        print self.clips
        print self.display_matrices["project"][-1]
        print self.display_matrices["view"][-1]
        print self.display_matrices["model"][-1]
        pass
    #f All done
    pass

#c c_opengl_camera_app
class c_opengl_camera_app(c_opengl_app):
    camera_control_keys = { "x":(("roll",1,0),),
                            "z":(("roll",2,0),),
                            "s":(("pitch",1,0),),
                            "a":(("pitch",2,0),),
                            ".":(("yaw",1,0),),
                            ";":(("yaw",2,0),),
                            "[":(("fov",1,0),),
                            "]":(("fov",2,0),),
                            "/":(("speed",1,0),),
                            "'":(("speed",2,0),),
                            " ":(("roll",0,-1),("yaw",0,-1),("pitch",0,-1),("speed",4,3),),
                            }
    #f __init__
    def __init__(self, **kwargs):
        c_opengl_app.__init__(self, **kwargs)
        self.camera = {"position":[0,0,-10],
                       "facing":quaternion.c_quaternion.identity(),
                       "rpy":[0,0,0],
                       "speed":0,
                       "fov":90,
                       }
        self.mvp = None
        self.aspect = 1.0
        self.zNear=1.0
        self.zFar=40.0
        self.camera_controls = set()
        self.camera_quats = {("roll",1):quaternion.c_quaternion.roll(+0.002),
                             ("roll",2):quaternion.c_quaternion.roll(-0.002),
                             ("yaw",1):quaternion.c_quaternion.yaw(+0.002),
                             ("yaw",2):quaternion.c_quaternion.yaw(-0.002),
                             ("pitch",1):quaternion.c_quaternion.pitch(+0.002),
                             ("pitch",2):quaternion.c_quaternion.pitch(-0.002),
                             }
        pass
    #f set_camera
    def set_camera(self, camera=None, orientation=None, yfov=None):
        if camera is not None:
            self.camera["position"] = list(camera)
            pass
        if orientation is not None:
            self.camera["facing"] = orientation
            pass
        if yfov is not None:
            self.camera["fov"] = yfov
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
    #f change_fov
    def change_fov(self, fov):
        self.camera["fov"] += fov
        if self.camera["fov"]<10:  self.camera["fov"]=10
        if self.camera["fov"]>140: self.camera["fov"]=140
        pass
    #f idle
    def idle(self):
        acceleration = 0.02
        self.camera["speed"] = self.camera["speed"]*0.9
        actions = {}
        for c in self.camera_controls:
            for action in self.camera_control_keys[c]:
                (a,s,c) = action
                if a in actions:
                    s = s | actions[a][0]
                    c = c | actions[a][1]
                    pass
                actions[a] = (s,c)
                pass
            pass
        for a in actions:
            (s,c) = actions[a]
            controls = s &~ c
            if controls!=0:
                if (a,controls) in self.camera_quats:
                    self.camera["facing"] = self.camera_quats[(a,controls)].copy().multiply(self.camera["facing"])
                elif a=="speed":
                    self.camera["speed"] += acceleration*(2*controls-3)
                    if controls&4: self.camera["speed"]=0
                elif a=="fov":
                    self.camera["fov"] *= 1+0.1*(2*controls-3)
                pass
            pass
        if self.camera["speed"]!=0:
            m = self.camera["facing"].get_matrix()
            self.camera["position"][0] += self.camera["speed"]*m[0][2]
            self.camera["position"][1] += self.camera["speed"]*m[1][2]
            self.camera["position"][2] += self.camera["speed"]*m[2][2]
            pass
        pass
    #f key_updown
    def key_updown(self, key,m,x,y,key_down):
        if key in self.camera_control_keys:
            if key_down:
                self.camera_controls.add(key)
                pass
            else:
                self.camera_controls.discard(key)
                pass
            return True
        pass
    #f keyrelease
    def keyrelease(self, key,m,x,y):
        if self.key_updown(key,m,x,y,False):
            return
        pass
    #f blah
    def blah():
        
        acceleration = 0.02
        if key=='i': self.change_angle(0,+3.1415/4,angle_delta=1)
        if key=='o': self.change_angle(1,+3.1415/4,angle_delta=1)
        if key=='p': self.change_angle(1,+3.1415/4,angle_delta=1)
        if key=='w': self.change_angle(2,-1)
        if key=='s': self.change_angle(2, 1)
        if key=='z': self.change_angle(0,-1)
        if key=='c': self.change_angle(0,+1)
        if key=='a': self.change_angle(1,-1)
        if key=='d': self.change_angle(1,+1)

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

    #f keypress
    def keypress(self, key,m,x,y):
        if self.key_updown(key,m,x,y,True):
            return
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
    def display(self, show_crosshairs=False):
        self.matrix_perspective(fovy=self.camera["fov"], aspect=self.aspect, zNear=self.zNear, zFar=self.zFar, matrix="project")
        if self.mvp is not None:
            self.mvp.perspective(self.camera["fov"],self.aspect,self.zNear,self.zFar)
            pass

        self.camera["facing"] = quaternion.c_quaternion.roll(self.camera["rpy"][0]).multiply(self.camera["facing"])
        self.camera["facing"] = quaternion.c_quaternion.pitch(self.camera["rpy"][1]).multiply(self.camera["facing"])
        self.camera["facing"] = quaternion.c_quaternion.yaw(self.camera["rpy"][2]).multiply(self.camera["facing"])

        m = self.camera["facing"].get_matrixn(order=4)
        self.camera["position"][0] += self.camera["speed"]*m[0,2]
        self.camera["position"][1] += self.camera["speed"]*m[1,2]
        self.camera["position"][2] += self.camera["speed"]*m[2,2]

        if self.seal_hack:
            m2 = m.copy()
            #m2.transpose()
            #self.camera["position"] = vectors.vector_add((0,-1,0),m2.apply((0,0,-10,1))[0:3])
            self.camera["position"] = vectors.vector_add((0,0,0),m2.apply((0,0,-10,1))[0:3])

        self.matrix_set(m.transpose(), matrix="view")
        self.matrix_translate(self.camera["position"], matrix="view")

        self.matrix_identity(matrix="model")

        if self.mvp is not None:
            m3 = self.camera["facing"].get_matrix3()
            self.mvp.mult3x3(m9=m3.matrix)
            self.mvp.translate(self.camera["position"])
            pass

        glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)

        if True: # Draw crosshairs

            self.matrix_push("project")
            self.matrix_push("view")
            self.matrix_push("model")
            self.matrix_identity("project")
            self.matrix_identity("view")
            self.matrix_identity("model")
            self.matrix_use()
            self.shader_use("color_standard")
            self.shader_set_attributes(C=(0.7,0.7,0.9))
            self.draw_lines((-1,0,0,1,0,0, 0,-1,0,0,1,0))
            self.matrix_pop("project")
            self.matrix_pop("view")
            self.matrix_pop("model")
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

