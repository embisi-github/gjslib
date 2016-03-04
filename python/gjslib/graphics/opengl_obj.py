#!/usr/bin/env python
from OpenGL.GLUT import *
from OpenGL.GLU import *
from OpenGL.GL import *

from gjslib.graphics.obj import c_obj

#a c_opengl_obj
class c_opengl_obj(c_obj):
    #f __init__
    def __init__(self):
        c_obj.__init__(self)
        self.opengl_surface = {}
        pass
    #f reset
    def reset(self):
        self.destroy_opengl_surface()
        c_obj.reset(self)
        pass
    #f destroy_opengl_surface
    def destroy_opengl_surface(self):
        # Be explicit about deleting the vectors and indices - OpenGL.arrays.vbo should do glDeleteBuffers
        if "vectors" in self.opengl_surface:
            del(self.opengl_surface["vectors"])
            pass
        if "indices" in self.opengl_surface:
            del(self.opengl_surface["indices"])
            pass
        pass
    #f create_opengl_surface
    def create_opengl_surface(self):
        import OpenGL.arrays.vbo as vbo
        import numpy
        from ctypes import sizeof, c_float, c_void_p, c_uint

        self.opengl_surface = {}

        index_list = []
        vector_list = []
        num_vectors = 0
        for f in self.faces:
            for (vi,vti,vni) in f:
                vertex = self.vertices[vi]
                normal = self.normals[vni]
                uv_map = (0.0,0.0)
                if vti is not None: uv_map = self.uv_map[vti]
                vector_list.extend( [vertex[0], vertex[1], vertex[2],
                                     normal[0], normal[1], normal[2],
                                     uv_map[0], uv_map[1]] )
                num_vectors += 1
                index_list.append(len(index_list))
                pass
            pass

        if num_vectors > 65530:
            raise Exception("Object has too many vectors to index - opengl is limited to 64k vectors")
        vectors = vbo.VBO( data=numpy.array(vector_list, dtype=numpy.float32), target=GL_ARRAY_BUFFER )
        indices = vbo.VBO( data=numpy.array(index_list, dtype=numpy.uint16), target=GL_ELEMENT_ARRAY_BUFFER )

        self.opengl_surface["vectors"] = vectors
        self.opengl_surface["indices"] = indices

        pass
    #f draw_opengl_surface
    def draw_opengl_surface(self, draw=True):
        from ctypes import sizeof, c_float, c_void_p, c_uint
        glEnableClientState(GL_VERTEX_ARRAY)
        glEnableClientState(GL_NORMAL_ARRAY)
        glEnableClientState(GL_TEXTURE_COORD_ARRAY)

        self.opengl_surface["vectors"].bind()
        self.opengl_surface["indices"].bind()

        glVertexPointer( 3, GL_FLOAT,   8*sizeof(c_float), c_void_p(0) )
        glNormalPointer( GL_FLOAT,      8*sizeof(c_float), c_void_p(3*sizeof(c_float)) )
        glTexCoordPointer( 2, GL_FLOAT, 8*sizeof(c_float), c_void_p(6*sizeof(c_float)) )

        if draw:
            glDrawElements( GL_TRIANGLES,
                            len(self.opengl_surface["indices"]),
                            GL_UNSIGNED_SHORT, None) 
            pass
        self.opengl_surface["vectors"].unbind()
        self.opengl_surface["indices"].unbind()
        pass
    #f All done
    pass

#a c_outline_text_obj
class c_outline_text_obj(c_opengl_obj):
    #f add_text
    def add_text(self, text, outline_font, baseline_xy, thickness=None ):
        nv = len(self.vertices)
        nn = len(self.normals)
        nu = len(self.uv_map)

        self.normals.append( (0.0,0.0,1.0) )
        if thickness is not None:
            self.normals.append( (0.0,0.0,-1.0) )
            pass
        ln_baseline_xy = baseline_xy
        for l in text.split("\n"):
            (baseline_x, baseline_y) = ln_baseline_xy
            ln_baseline_xy = (baseline_x, baseline_y-outline_font.get_line_spacing())
            for g in l:
                ofg = outline_font.get_glyph(g, baseline_x)
                if ofg is not None:
                    (baseline_x, pts, tris) = ofg
                    for t in tris:
                        for p in t:
                            self.vertices.append( (pts[p][0],pts[p][1]+baseline_y,0.0) )
                            pass
                        face = ( (nv,None,nn), (nv+1,None,nn), (nv+2,None,nn) )
                        nv += 3
                        self.faces.append(face)
                        if thickness is not None:
                            for p in t:
                                self.vertices.append( (pts[p][0],pts[p][1]+baseline_y,thickness) )
                                pass
                            face = ( (nv,None,nn), (nv+1,None,nn), (nv+2,None,nn) )
                            nv += 3
                            self.faces.append(face)
                        pass
                    pass
                pass
            pass
        return ln_baseline_xy
    #f All done
    pass
#a c_text_page - move to opengl_font/opengl_text
class c_text_page(c_opengl_obj):
    def add_glyph(self, unichar, bitmap_font, baseline_xy, scale=(1.0,1.0) ):
        r = bitmap_font.map_char(unichar, baseline_xy, scale)
        #r["src_uv"] = (x,y,w,h)
        #r["tgt_xy"] = (x,y,w,h)
        #r["adv"] = tgt x+
        if r["tgt_xy"] is None:
            return (baseline_xy[0]+r["adv"], baseline_xy[1])
        tgt_xyz = (r["tgt_xy"][0],
                   r["tgt_xy"][1],
                   0.0)
        tgt_dxyz0 = (r["tgt_xy"][2], 0.0, 0.0)
        tgt_dxyz1 = (0.0, r["tgt_xy"][3], 0.0)
        src_uv = (r["src_uv"][0], r["src_uv"][1])
        src_duv0 = (r["src_uv"][2],0.0)
        src_duv1 = (0.0,r["src_uv"][3])
        self.add_rectangle( xyz=tgt_xyz, dxyz0=tgt_dxyz0, dxyz1=tgt_dxyz1,
                            uv=src_uv, duv0=src_duv0, duv1=src_duv1 )
        return (baseline_xy[0]+r["adv"], baseline_xy[1])
        pass
    def add_text(self, text, bitmap_font, baseline_xy, scale=(1.0,1.0) ):
        ln_baseline_xy = baseline_xy
        for l in text.split("\n"):
            baseline_xy = ln_baseline_xy
            ln_baseline_xy = (baseline_xy[0], baseline_xy[1]+scale[1]*bitmap_font.line_spacing)
            for u in l:
                baseline_xy = self.add_glyph(u, bitmap_font, baseline_xy, scale=scale)
                pass
            pass
        return baseline_xy
