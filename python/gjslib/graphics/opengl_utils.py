#!/usr/bin/env python

#a Imports
from OpenGL.GLUT import *
from OpenGL.GLU import *
from OpenGL.GL import *
from gjslib.math import matrix, quaternion, vectors
from gjslib.graphics.font import c_bitmap_font

#a Useful functions
#f min
def min(a,b,c=None):
    if a is None: a=b
    if a>b:a=b
    if c is not None and a>c: a=c
    return a

#f max
def max(a,b,c=None):
    if a is None: a=b
    if a<b:a=b
    if c is not None and a<c: a=c
    return a

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
    m = matrix.c_matrixNxN(order=4).identity()
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
        m.scale(scale=(w/2.0,h/2.0,1.0,1.0))
        m.translate(xyz=(1.0,1.0,0.0))
        pass
    if inv_map_xywh is not None:
        (x,y,w,h) = inv_map_xywh
        # Map (x,y) to (-1,-1); map (x+w, y+h) to (1,1)
        # So translate by -x,-y; then scale by 2/w, 2/h; then translate by -1,-1
        # Operations are reversed (as last is applied first to our object)
        m.translate(xyz=(-1.0,-1.0,0.0))
        m.scale(scale=(2.0/w,2.0/h,1.0,1.0))
        m.translate(xyz=(-x,-y,0.0))
        pass
    q = quaternion.c_quaternion.identity()
    if rotation is not None:
        for (k,f) in [("roll",  quaternion.c_quaternion.roll),
                      ("pitch", quaternion.c_quaternion.pitch),
                      ("yaw",   quaternion.c_quaternion.yaw)]:
            if k in rotation: q = f(rotation["k"]).multiply(q)
            pass
        pass
    m.postmult(q.get_matrixn(order=4))
    if scale is not None:
        scale_matrix = matrix.c_matrixNxN().identity().scale(scale)
        m.postmult(scale_matrix)
        pass
    if translation is not None:
        if len(translation)==2: translation=(translation[0], translation[1], 0.0)
        m.translate(xyz=translation)
        pass
    return m
    
#f xxyyzz_from_xyz_pair
def xxyyzz_from_xyz_pair(xyz0, xyz1):
    return (xyz0[0], xyz1[0], xyz0[1], xyz1[1], xyz0[2], xyz1[2])
            
#f xxyyzz_from_xyz_whd
def xxyyzz_from_xyz_whd(xyz, whd):
    return (xyz[0], xyz[0]+whd[0], xyz[1], xyz[1]+whd[1], xyz[2], xyz[2]+whd[2])
            
#f xxyyzz_add_border
def xxyyzz_add_border(xxyyzz, b, scale=1.0):
    return (xxyyzz[0]+b[0]*scale, xxyyzz[1]-b[1]*scale,
            xxyyzz[2]+b[2]*scale, xxyyzz[3]-b[3]*scale,
            xxyyzz[4]+b[4]*scale, xxyyzz[5]-b[5]*scale)
            
#f xxyyzz_minmax
def xxyyzz_minmax(xxyyzz0, xxyyzz1):
    return (min(xxyyzz0[0], xxyyzz1[0]), max(xxyyzz0[1], xxyyzz1[1]),
            min(xxyyzz0[2], xxyyzz1[2]), max(xxyyzz0[3], xxyyzz1[3]),
            min(xxyyzz0[4], xxyyzz1[4]), max(xxyyzz0[5], xxyyzz1[5]))
            
#f xyz_pair_from_xxyyzz
def xyz_pair_from_xxyyzz(xxyyzz):
    return (xxyyzz[0], xxyyzz[2], xxyyzz[4]), (xxyyzz[1], xxyyzz[3], xxyyzz[5])
            
#f whd_from_xxyyzz
def whd_from_xxyyzz(xxyyzz):
    return (xxyyzz[1]-xxyyzz[0], xxyyzz[3]-xxyyzz[2], xxyyzz[5]-xxyyzz[4])
#f xyz_whd_from_xxyyzz
def xyz_whd_from_xxyyzz(xxyyzz):
    return (xxyyzz[0],xxyyzz[2],xxyyzz[4]), (xxyyzz[1]-xxyyzz[0], xxyyzz[3]-xxyyzz[2], xxyyzz[5]-xxyyzz[4])
            
#f xxyyzz_ray_intersects_face
def xxyyzz_ray_intersects_face(xxyyzz, bbox, n, normal, epsilon=1E-6):
    """
    xxyyzz is xyz, dxyz
    bbox is xxyyzz - a cuboid
    n is the face to test for intersection
    normal is the normal to the face (0,0,1), (0,1,0) or (1,0,0)
    """
    dxyz = (xxyyzz[1], xxyyzz[3], xxyyzz[5])
    xyz = (xxyyzz[0], xxyyzz[2], xxyyzz[4])
    dn = vectors.dot_product(dxyz,normal)
    if dn>-epsilon and dn<epsilon: return False
    k = (bbox[n]-vectors.dot_product(xyz,normal)) / dn
    if k<=0: return False
    p = vectors.vector_add(xyz,dxyz,scale=k)
    if n not in [0,1]:
        if p[0]<bbox[0] or p[0]>bbox[1]: return False
    if n not in [2,3]:
        if p[1]<bbox[2] or p[1]>bbox[3]: return False
    if n not in [4,5]:
        if p[2]<bbox[4] or p[2]>bbox[5]: return False
    return True
#f xxyyzz_ray_intersects_bbox
def xxyyzz_ray_intersects_bbox(xxyyzz, bbox):
    """
    Ray is xyz[0] + k.xyz[1], k>0
    Or, a + k.d
    Bbox is cuboid with normals (0,0,1), (0,1,0), (0,0,1)
    BBox cuboid faces are (e.g.) x0,y0,z0, x1,y0,z0, x1,y1,z0, x1,y0,z0
    Such a face has a vector equation p.n = p.(0,0,1) = z0
    The intersection is then a.n+k.d.n = z0, i.e. k=(z0-a.n) / d.n
    The intersection point is a+k.d = x,y,z0
    To be a collision with the bbox k>0, x0<x<x1, y0<y<y1, for at least
    two faces
    """
    # Would rotate ray first by content_inverse_transformation?
    cnt = 0
    if xxyyzz_ray_intersects_face(xxyyzz,bbox,4,(0,0,1)):
        cnt += 1
        pass
    if xxyyzz_ray_intersects_face(xxyyzz,bbox,5,(0,0,1)):
        cnt += 1
        pass
    if cnt==2: return True
    if xxyyzz_ray_intersects_face(xxyyzz,bbox,2,(0,1,0)):
        cnt += 1
        pass
    if cnt==2: return True
    if xxyyzz_ray_intersects_face(xxyyzz,bbox,3,(0,1,0)):
        cnt += 1
        pass
    if cnt==2: return True
    if xxyyzz_ray_intersects_face(xxyyzz,bbox,0,(1,0,0)):
        cnt += 1
        pass
    if cnt==2: return True
    if xxyyzz_ray_intersects_face(xxyyzz,bbox,1,(1,0,0)):
        cnt += 1
        pass
    if cnt==2: return True
    return False

#a Base useful classes
#c c_depth_contents_iter
class c_depth_contents_iter(object):
    """
    Iteration class for the c_depth_contents

    Provides a 'next' method that iterates in a pre-defined order over the contents
    """
    #f __init__
    def __init__(self, dc, reverse_depth=False, selector=None):
        """
        Set up iterator to go up in depth (or down)
        """
        self.dc = dc
        self.selector = selector
        self.depths = dc.keys()
        if reverse_depth:
            self.depths.reverse()
            pass
        self.content_index = 0
        pass
    #f __iter__
    def __iter__(self):
        return self
    #f next
    def next(self):
        if len(self.depths)==0:
            raise StopIteration()
        d = self.depths[0]
        if d not in self.dc:
            raise StopIteration()
        if self.content_index<len(self.dc[d]):
            self.content_index += 1
            item = self.dc[d][self.content_index-1]
            if self.selector is None:
                return item
            return self.selector(item)
        self.content_index = 0
        self.depths.pop(0)
        return self.next()
    #f All done
    pass
        
#c c_depth_contents
class c_depth_contents(object):
    """
    A set of 'depth ordered' lists of contents
    Each item in the contents has a depth
    The iteration over the contents is done by all items at each depth, in either depth-order or reverse-depth-order
    """
    #f __init__
    def __init__(self, **kwargs):
        self.__dc__contents = {}
        pass
    pass
    #f clear_contents
    def clear_contents(self, depth=None):
        """
        Clear the contents, optionally for a particular depth
        """
        if depth is None:
            self.__dc__contents = {}
            return
        if depth in self.__dc__contents:
            self.__dc__contents[depth] = []
            pass
        pass
    #f add_contents
    def add_contents(self, content, depth=0):
        """
        Add content at a particular depth

        The content is appended to the depth list
        """
        if depth not in self.__dc__contents:
            self.__dc__contents[depth] = []
            pass
        self.__dc__contents[depth].append(content)
        pass
    #f remove_contents
    def remove_contents(self, content, depth=None):
        """
        Remove content (from a particular depth)
        """
        for d in self.__dc__contents:
            if (depth is not None) and (d!=depth):
                continue
            self.__dc__contents[d].remove(content)
            return
        raise Exception("Failed to find content to remove (at specified depth)")
    #f get_iter
    def get_iter(self, fwd=True, selector=None):
        return c_depth_contents_iter(self.__dc__contents, reverse_depth=not fwd, selector=selector)
    #f __iter__
    def __iter__(self):
        return c_depth_contents_iter(self.__dc__contents)
    #f reverse
    def reverse(self):
        """
        Return iterator running in reverse order of depth (largest depth first)
        """
        return c_depth_contents_iter(self.__dc__contents, reverse_depth=True)
    #f All done
    pass

