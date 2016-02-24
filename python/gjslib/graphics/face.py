#!/usr/bin/env python
from OpenGL.GLUT import *
from OpenGL.GLU import *
from OpenGL.GL import *

import re
class c_obj(object):
    def __init__(self):
        self.vertices = []
        self.uv_map = []
        self.normals = []
        self.faces = []
        pass
    def face_of_triple(self, vi,vti,vni,delta=0):
        vi = int(vi)
        vni = int(vni)
        try:
            vti = int(vti)
            pass
        except:
            vti = None
            pass
        return (vi+delta,vti+delta,vni+delta)
    def create_icosahedron(self):
        from gjslib.math.spherical_coords import c_spherical_coord
        self.vertices = []
        self.uv_map = []
        self.normals = []
        self.faces = []
        sc = c_spherical_coord()
        for i in range(10):
            sc.from_icos_tuv((i,0,0))
            xyz = sc.xyz()
            xyz = (xyz[0],-xyz[1],xyz[2])
            self.vertices.append(xyz)
            pass
        self.vertices.append((0.0,0.0,1.0))
        self.vertices.append((0.0,0.0,-1.0))
        self.normals = self.vertices[:]
        zero=0.00001
        one=1.0-3*zero
        for i in range(20):
            sc.from_icos_tuv((i,zero,zero))
            self.uv_map.append( sc.tex_uv(scalex=0.5,scaley=0.2) )
            sc.from_icos_tuv((i,one,zero))
            self.uv_map.append( sc.tex_uv(scalex=0.5,scaley=0.2) )
            sc.from_icos_tuv((i,zero,one))
            self.uv_map.append( sc.tex_uv(scalex=0.5,scaley=0.2) )
            print self.uv_map[-3:]
            pass
        for i in range(5):
            t = 2*i
            t2 = (2*i+2)%10
            self.faces.append( [self.face_of_triple(t,  6*i,    t), self.face_of_triple(t+1, 6*i+2, t+1), self.face_of_triple(t2,6*i+1,t2)] )
            self.faces.append( [self.face_of_triple(t+1,6*i+3,t+1), self.face_of_triple(t2+1,6*i+4,t2+1), self.face_of_triple(t2,6*i+5,t2)] )
            pass
        for i in range(5):
            t  = 2*i
            t2 = (2*i+2)%10
            t_top = 30+3*i
            t_bottom = 45+3*i
            self.faces.append( [self.face_of_triple(t+1,t_top+0,t+1), self.face_of_triple(t2+1,t_top+1,t2+1), self.face_of_triple(10,t_top+2,10)] )
            self.faces.append( [self.face_of_triple(t,  t_bottom,t), self.face_of_triple(t2,t_bottom+1,t2), self.face_of_triple(11,t_bottom+2,11)] )
            pass
        pass
    def create_icosphere(self,subdivide=1):
        from gjslib.math.spherical_coords import c_spherical_coord
        self.vertices = []
        self.uv_map = []
        self.normals = []
        self.faces = []
        sc = c_spherical_coord()
        n = 0
        for i in range(20):
            num_sub = 1<<subdivide
            for um in range(num_sub):
                for vm in range(num_sub):
                    if (um+vm)>=num_sub: continue
                    for (u,v) in ( (0,0), (1,0), (0,1) ):
                        sc.from_icos_tuv((i,(um+u)/(num_sub+0.0),(vm+v)/(num_sub+0.0)))
                        xyz = sc.xyz()
                        xyz = (xyz[0],-xyz[1],xyz[2])
                        self.vertices.append(xyz)
                        self.normals.append(xyz)
                        self.uv_map.append( sc.tex_uv(scalex=0.5,scaley=0.2) )
                        pass
                    self.faces.append( [self.face_of_triple(n,n,n), self.face_of_triple(n+1,n+1,n+1), self.face_of_triple(n+2,n+2,n+2)] )
                    n = n + 3
                    if (um+vm)>=num_sub-1: continue
                    for (u,v) in ( (1,0), (1,1), (0,1) ):
                        sc.from_icos_tuv((i,(um+u)/(num_sub+0.0),(vm+v)/(num_sub+0.0)))
                        xyz = sc.xyz()
                        xyz = (xyz[0],-xyz[1],xyz[2])
                        self.vertices.append(xyz)
                        self.normals.append(xyz)
                        self.uv_map.append( sc.tex_uv(scalex=0.5,scaley=0.2) )
                        pass
                    self.faces.append( [self.face_of_triple(n,n,n), self.face_of_triple(n+1,n+1,n+1), self.face_of_triple(n+2,n+2,n+2)] )
                    n = n + 3
                    pass
                pass
            pass
        pass
    def load_from_file(self, f, transform=None, translation=None):
        float_re = r"(-*\d+(?:(?:\.\d*)|))"
        triple_re = r"(\d+)/((?:\d+)|)/(\d+)"
        uv_map_re      = re.compile("vt "+float_re+" "+float_re)
        normal_map_re  = re.compile("vn "+float_re+" "+float_re+" "+float_re)
        vertex_map_re  = re.compile("v "+float_re+" "+float_re+" "+float_re)
        face_re        = re.compile("f "+triple_re+"(.*)")
        face_triple_re = re.compile(" "+triple_re+"(.*)")
        self.uv_map = []
        self.normals = []
        self.vertices = []
        self.faces = []
        for l in f:
            m = uv_map_re.match(l)
            if m is not None:
                self.uv_map.append( (float(m.group(1)),1.0-float(m.group(2))) )
                pass
            m = normal_map_re.match(l)
            if m is not None:
                self.normals.append( (float(m.group(1)),float(m.group(2)),float(m.group(3))) )
                pass
            m = vertex_map_re.match(l)
            if m is not None:
                self.vertices.append( (float(m.group(1)),float(m.group(2)),float(m.group(3))) )
                pass
            m = face_re.match(l)
            if m is not None:
                face = []
                face.append(self.face_of_triple(m.group(1),m.group(2),m.group(3),-1))
                l = m.group(4)
                l.strip()
                while len(l)>0:
                    m = face_triple_re.match(l)
                    if m is None: break
                    face.append(self.face_of_triple(m.group(1),m.group(2),m.group(3),-1))
                    l = m.group(4)
                    l.strip()
                    pass
                self.faces.append(face)
                pass
            pass
        pass
    def create_opengl_surface(self):
        import OpenGL.arrays.vbo as vbo
        import numpy
        from ctypes import sizeof, c_float, c_void_p, c_uint

        self.opengl_surface = {}

        index_list = []
        vector_list = []
        for f in self.faces:
            for (vi,vti,vni) in f:
                vertex = self.vertices[vi]
                normal = self.normals[vni]
                uv_map = (0.0,0.0)
                if vti is not None: uv_map = self.uv_map[vti]
                vector_list.extend( [vertex[0], vertex[1], vertex[2],
                                     normal[0], normal[1], normal[2],
                                     uv_map[0], uv_map[1]] )
                index_list.append(len(index_list))
                pass
            pass

        vectors = vbo.VBO( data=numpy.array(vector_list, dtype=numpy.float32), target=GL_ARRAY_BUFFER )
        indices = vbo.VBO( data=numpy.array(index_list, dtype=numpy.uint16), target=GL_ELEMENT_ARRAY_BUFFER )

        self.opengl_surface["vectors"] = vectors
        self.opengl_surface["indices"] = indices

        self.opengl_surface["vectors"].bind()
        self.opengl_surface["indices"].bind()

        pass
    def draw_opengl_surface(self):
        from ctypes import sizeof, c_float, c_void_p, c_uint
        glEnableClientState(GL_VERTEX_ARRAY)
        glEnableClientState(GL_NORMAL_ARRAY)
        glEnableClientState(GL_TEXTURE_COORD_ARRAY)

        glVertexPointer( 3, GL_FLOAT,   8*sizeof(c_float), c_void_p(0) )
        glNormalPointer( GL_FLOAT,      8*sizeof(c_float), c_void_p(3*sizeof(c_float)) )
        glTexCoordPointer( 2, GL_FLOAT, 8*sizeof(c_float), c_void_p(6*sizeof(c_float)) )

        self.opengl_surface["vectors"].bind()
        self.opengl_surface["indices"].bind()

        if True:
            glDrawElements( GL_TRIANGLES,
                            len(self.opengl_surface["indices"]),
                            GL_UNSIGNED_SHORT,
                            self.opengl_surface["indices"] )
            pass
