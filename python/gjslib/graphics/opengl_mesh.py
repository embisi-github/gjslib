#!/usr/bin/env python

#a Imports
from OpenGL.GLUT import *
from OpenGL.GLU import *
from OpenGL.GL import *
from gjslib.graphics import opengl, opengl_obj
from gjslib.math import mesh
from gjslib.math.bezier import c_point

#a Classes for c_opengl_mesh
#c c_opengl_textured_mesh_point
class c_opengl_textured_mesh_point(c_point):
    """
    """
    #f __init__
    def __init__(self, uv, xyz, ref=None):
        c_point.__init__(self, coords=uv)
        self.otmp_xyz = xyz
        self.ref = ref
        pass
    #f __repr__
    def __repr__(self):
        r = "otmp:"+c_point.__repr__(self)
        return r
    #f All done
    pass

#c c_opengl_textured_mesh
class c_opengl_textured_mesh(object):
    """
    A textured mesh has a set of points
    (u,v) -> (xyz)

    Assuming the mesh xyz are coplanar, the mesh may be concave
    As such it may need to be broken into a set of convex faces for OpenGL to display

    A textured mesh may also have holes in it

    The specification of a textured mesh is then:
    a. Sets of contours of (uv,xyz) tuples (where 'holes' are ordered anti-clockwise in uv, outer perimeter clockwise)
    b. Sets of internal (uv,xyz) tuples (additional data points to help rendering)

    
    """
    #f __init__
    def __init__(self):
        self.mesh = mesh.c_mesh()
        self.object = None
        pass
    #f add_contour
    def add_contour(self, point_list):
        """
        Add a contour using a list of (uv, xyz, ref) tuples
        """
        if len(point_list)<3: return
        contour = []
        for (uv, xyz, ref) in point_list:
            contour.append( c_opengl_textured_mesh_point(uv, xyz, ref) )
            pass
        self.mesh.add_contour(contour)
        pass
    #f add_point
    def add_point(self, uv, xyz, ref=None):
        """
        Add a single point to aid rendering
        """
        pt = c_opengl_textured_mesh_point(uv, xyz, ref)
        self.mesh.add_point(pt)
        pass
    #f optimize
    def optimize(self, split_max_areas=3):
        min_length = 1E-6
        min_area = 1E-8
        self.mesh.map_contours_to_mesh()
        self.mesh.normalize()
        self.mesh.fill_convex_hull_with_triangles()
        self.mesh.remove_small_lines(min_length=min_length)
        self.mesh.remove_small_area_triangles( min_area=min_area)
        for i in range(10):
            if self.mesh.shorten_quad_diagonals()==0: break
            pass
        for i in range(10):
            self.mesh.ensure_contours_on_mesh()
            self.mesh.shorten_quad_diagonals()
            self.mesh.remove_small_lines(min_length=min_length)
            self.mesh.remove_small_area_triangles(min_area=min_area)
            pass
        self.mesh.ensure_contours_on_mesh()
        self.mesh.assign_winding_order_to_contours()
        self.mesh.assign_winding_order_to_mesh()
        if split_max_areas<=0:
            return
        large_areas = self.mesh.find_large_area_triangle_centroids(max_area=0)
        #print large_areas
        l = []
        for (a,x,y) in large_areas:
            l.append(a)
            pass
        l.sort()
        max_area = l[len(l)/2]/2.0 # find median area of l, and divide by 2
        for (a,x,y) in large_areas:
            if (a>max_area):
                self.mesh.add_point(c_point((x,y)))
                #print "Adding point",(x,y)
                pass
            pass
        self.mesh.reset_triangles()
        self.mesh.reset_lines()
        return self.optimize(split_max_areas=split_max_areas-1)
        pass
    #f create_opengl_surface
    def create_opengl_surface(self,projection_callback=None):
        self.object = opengl_obj.c_opengl_obj()
        for t in self.mesh.triangles:
            #print t.winding_order
            #if (t.winding_order%2)==0: continue
            xyz_list = []
            uv_list = []
            for p in t.pts:
                if type(p.pt) == c_opengl_textured_mesh_point:
                    xyz_list.append(p.pt.otmp_xyz)
                    uv_list.append(p.coords())
                    pass
                else:
                    xyz = None
                    uv = p.coords()
                    if projection_callback is not None:
                        xyz = projection_callback(uv)
                        pass
                    if xyz is not None:
                        xyz_list.append(xyz)
                        uv_list.append(uv)
                        pass
                    pass
                pass
            if len(xyz_list)==3:
                self.object.add_triangle(xyz_list,uv_list)
                pass
            pass
        self.object.create_opengl_surface()
        pass
    #f draw_opengl_surface
    def draw_opengl_surface(self, og):
        if self.object is None:
            return
        self.object.draw_opengl_surface(og)
        pass
    #f All done
    pass
