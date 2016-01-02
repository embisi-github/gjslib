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
            self.vertices.append(sc.xyz())
            pass
        self.vertices.append((0.0,0.0,1.0))
        self.vertices.append((0.0,0.0,-1.0))
        self.normals = self.vertices[:]
        self.uv_map.append( (0.0,0.0) )
        self.uv_map.append( (1.0,0.0) )
        self.uv_map.append( (0.0,1.0) )
        for i in range(5):
            t = 2*i
            t2 = (2*i+2)%10
            self.faces.append( [self.face_of_triple(t,0,t), self.face_of_triple(t+1,2,t+1), self.face_of_triple(t2,1,t2)] )
            self.faces.append( [self.face_of_triple(t+1,0,t+1), self.face_of_triple(t2+1,1,t2+1), self.face_of_triple(t2,2,t2)] )
            pass
        for i in range(5):
            t  = 2*i
            t2 = (2*i+2)%10
            self.faces.append( [self.face_of_triple(t,0,t), self.face_of_triple(t2,1,t2), self.face_of_triple(11,2,11)] )
            self.faces.append( [self.face_of_triple(t+1,0,t+1), self.face_of_triple(t2+1,1,t2+1), self.face_of_triple(10,2,10)] )
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
        indices = vbo.VBO( data=numpy.array(index_list, dtype=numpy.uint8), target=GL_ELEMENT_ARRAY_BUFFER )

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
                            GL_UNSIGNED_BYTE,
                            self.opengl_surface["indices"] )
            pass
