#!/usr/bin/env python
from OpenGL.GLUT import *
from OpenGL.GLU import *
from OpenGL.GL import *

import re

#a c_obj
class c_obj(object):
    #f __init__
    def __init__(self):
        self.vertices = []
        self.uv_map = []
        self.normals = []
        self.faces = []
        self.opengl_surface = {}
        pass
    #f from_bitmap
    def from_bitmap(self, image, scale_factors, is_solid=None):
        """
        image must have getpixel(x,y) and size = tuple (width,height)
        scale_factors is tuple of (width, depth, height) for the object
        """
        if is_solid is None:
            is_solid = lambda x:(x!=0)
            pass
        self.vertices = []
        self.uv_map = []
        self.normals = []
        (width,height) = image.size
        pixel_array = []
        for y in range(height):
            pixel_array.append([])
            for x in range(width):
                pixel_array[-1].append(is_solid(image.getpixel((x,y))))
                pass
            pass
        self.from_pixel_array(pixel_array, scale_factors)
        pass
    #f from_pixel_array
    def from_pixel_array(self, pixel_array, scale_factors):
        self.vertices = []
        self.uv_map = []
        self.normals = []
        height = len(pixel_array)
        width  = len(pixel_array[0])
        faces_required = {}
        def add_required_face(x,y,face,flip):
            k = (x,y,face)
            if k in faces_required:
                del(faces_required[k])
                return
            faces_required[k] = flip
            pass
        for y in range(height):
            for x in range(width):
                if pixel_array[y][x]:
                    add_required_face(x,y,"top",False)
                    add_required_face(x,y,"bottom",True)
                    add_required_face(x,y,"left",True)
                    add_required_face(x,y,"back",True)
                    add_required_face(x+1,y,"left",False)
                    add_required_face(x,y+1,"back",False)
                    pass
                pass
            pass
        for k in faces_required:
            (x,y,face) = k
            self.add_pixel_face(x,y,face,width,height,scale_factors,faces_required[k])
            pass
        pass
    #f add_pixel_face
    def add_pixel_face(self, x,y,face,width,height,scale_factors,flip=False):
        vi = len(self.vertices)
        vni = len(self.normals)
        vti = len(self.uv_map)
        deltas = [(0,0), (0,1), (1,0), (1,1)]
        if flip:
            deltas = [(0,0), (1,0), (0,1), (1,1)]
            pass
        def uv(x,y,width=width,height=height):
            return ((x+0.0)/width, (y+0.0)/height)
        def xyz(x,y,dx,dy,face,scale_factors=scale_factors,width=width,height=height):
            if face in ["top"]:
                (x,y,z)  = (x+dx,y+dy,0.0)
            elif face in ["bottom"]:
                (x,y,z)  = (x+dx,y+dy,1.0)
                pass
            elif face in ["left"]:
                (x,y,z)  = (x,y+dx,1.0-float(dy))
                pass
            elif face in ["back"]:
                (x,y,z)  = (x+dy,y,1.0-float(dx))
                pass
            return (x*scale_factors[0]/width, z*scale_factors[1], (y*scale_factors[2])/height)
        if face in ["top"]:   n = (0.0,-1.0,0.0)
        if face in ["bottom"]:n = (0.0,1.0,0.0)
        if face in ["left"]:  n = (1.0,0.0,0.0)
        if face in ["back"]:  n = (0.0,0.0,1.0)
        for (dx,dy) in deltas:
            self.vertices.append( xyz(x,y,dx,dy,face) )
            self.normals.append( n )
            self.uv_map.append( uv(x+dx,y+dy) )
            pass
        face = []
        face.append(self.face_of_triple(vi,vti,vni,0))
        face.append(self.face_of_triple(vi,vti,vni,1))
        face.append(self.face_of_triple(vi,vti,vni,2))
        self.faces.append( face )
        face = []
        face.append(self.face_of_triple(vi,vti,vni,1))
        face.append(self.face_of_triple(vi,vti,vni,3))
        face.append(self.face_of_triple(vi,vti,vni,2))
        self.faces.append( face )
        pass
    #f face_of_triple
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
    #f add_rectangle
    def add_rectangle(self,xyz,dxyz0,dxyz1,uv=(0.0,0.0),duv0=(1.0,0.0),duv1=(0.0,1.0)):
        nv = len(self.vertices)
        self.vertices.append(xyz)
        self.vertices.append( (xyz[0]+dxyz0[0], xyz[1]+dxyz0[1], xyz[2]+dxyz0[2]))
        self.vertices.append( (xyz[0]+dxyz0[0]+dxyz1[0], xyz[1]+dxyz0[1]+dxyz1[1], xyz[2]+dxyz0[2]+dxyz1[2]))
        self.vertices.append( (xyz[0]+dxyz1[0], xyz[1]+dxyz1[1], xyz[2]+dxyz1[2]))
        self.uv_map.append( uv )
        self.uv_map.append( (uv[0]+duv0[0], uv[1]+duv0[1]) )
        self.uv_map.append( (uv[0]+duv0[0]+duv1[0], uv[1]+duv0[1]+duv1[1]) )
        self.uv_map.append( (uv[0]+duv1[0], uv[1]+duv1[1]) )
        self.normals.extend(self.vertices[nv:])
        self.faces.append( (self.face_of_triple(0,0,0,nv), self.face_of_triple(1,1,1,nv), self.face_of_triple(2,2,2,nv)) )
        self.faces.append( (self.face_of_triple(0,0,0,nv), self.face_of_triple(2,2,2,nv), self.face_of_triple(3,3,3,nv)) )
        pass
    #f create_icosahedron
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
    #f create_icosphere
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
    #f load_from_file
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
    #f save_to_file
    def save_to_file(self, f):
        for v in self.vertices:
            print >> f, "v %f %f %f"%v
            pass
        for n in self.normals:
            print >> f, "vn %f %f %f"%n
            pass
        for uv in self.uv_map:
            print >> f, "vt %f %f"%uv
            pass
        for fa in self.faces:
            face = "f "
            for (vi, vni,vti) in fa:
                face += " %d/%d/%d"%(vi+1,vti+1,vni+1)
                pass
            print >> f, face
            pass
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
                            GL_UNSIGNED_SHORT,
                            self.opengl_surface["indices"] )
            pass
        self.opengl_surface["vectors"].unbind()
        self.opengl_surface["indices"].unbind()
        pass

#a c_text_page
class c_text_page(c_obj):
    def __init__(self):
        c_obj.__init__(self)
        pass
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
