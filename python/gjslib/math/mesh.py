#!/usr/bin/env python
#a Documentation
r"""
A mesh class built from contours

A mesh is a set of 2D points that are connected by lines, and which is filled with non-overlapping triangles

A contour is an ordered set of lines between points in the mesh. A contour may be open or closed

A contoured mesh is a mesh and contours, where all the lines in every one of the contours is a line in the mesh, and where the lines are part of the triangles forming the mesh
    
"""
__docformat__ = "restructuredtext"

#a Imports
import gjslib.math.bezier as bezier
import math

#a Variable
verbose = True
verbose = False

#a Mesh classes
#c c_mesh_point
class c_mesh_point( object ):
    """
    A point within a (contoured) mesh

    A mesh point is a 2d-point (using an instance of a point class) that will be part of the mesh, and it will be part of lines and triangles in the mesh

    A mesh point will be in any number of line segments and triangles, but in a complete mesh every point should be part of at least two lines and one triangle

    The instance of the 'point class' which the mesh point uses must provide:
    * a 'coords' property that is either a tuple or list of two coordinates.
    """
    #f __init__
    def __init__( self, pt ):
        """
        Create a new mesh point from an instance of a 2d 'point class'.

        pt - an instance of a 2D point class, which must have a :attr:`coords` property
        """
        self.pt = pt
        self.triangles = []
        self.line_segments = []
        self.entry_number = -1
        pass
    #f check_consistent
    def check_consistent( self ):
        """
        Check the mesh point is consistent.

        Checks that every line segment that the mesh point believes it is part of has the mesh point as one of its two end-points.
        Checks that every triangle that the mesh point believes it is part of has the mesh point as one of its three points.
        Checks that there are no duplicate entries in the triangles and line segment lists
        """
        for l in self.line_segments:
            if self not in l[0].get_points():
                raise Exception("Failed to find point %s in line %s"%(str(self),str(l)))
            if self.line_segments.count(l)>1:
                raise Exception("Duplicate line in point %s: line %s"%(str(self),str(l)))
            pass
        for t in self.triangles:
            if t is not None:
                if self not in t.get_points():
                    raise Exception("Failed to find point %s in triangle %s"%(str(self),str(t)))
                pass
            if self.triangles.count(t)>1:
                raise Exception("Duplicate triangle in point %s: triangle %s"%(str(self),str(t)))
            pass
        pass
    #f coords
    def coords( self ):
        """Return the 2D coordinates of the mesh point using the 'point class' instance that it was created with."""
        return self.pt.coords
    #f set_coords
    def set_coords( self, coords ):
        """Set the coordinates of a point (for fine adjustment only)."""
        self.pt.set_coords( coords )
        pass
    #f add_to_line
    def add_to_line( self, line, other, line_pt_num ):
        """Add the mesh point to a line segment by updating the mesh point data *only*."""
        self.line_segments.append( (line, other, line_pt_num) )
        return
    #f remove_from_line
    def remove_from_line( self, line ):
        """Remove the mesh point from a line segment by updating the mesh point data *only*."""
        for i in range(len(self.line_segments)):
            if self.line_segments[i][0]==line:
                self.line_segments.pop(i)
                return
            pass
        raise Exception("Failed to find %s in attempting to remove %s from that line"%(line,self))
    #f is_on_line
    def is_on_line( self, line ):
        """Return True if the mesh point is one of the end-points of the line, else return False."""
        for (l,pt,x) in self.line_segments:
            if l == line: return True
            pass
        return False
    #f find_line_segment_to
    def find_line_segment_to( self, other, mesh_only=False ):
        """
        Find the line segment which goes from this mesh point to the :data:`other` mesh point.

        other - the other mesh point in the line segment to find
        mesh_only - True if only points that are in the mesh (i.e. those that are part of triangles) should be searched
        """
        for (l,pt,x) in self.line_segments:
            if mesh_only and (l.triangles[0] is None): continue
            if pt==other: return l
            pass
        return None
    #f find_line_segment_toward
    def find_line_segment_toward( self, other, verbose=False ):
        """
        Find the line segment which goes from this mesh point toward the other data point, if there is one
        """
        epsilon = 1E-10
        (x0,y0) = self.pt.coords
        (x1,y1) = other.pt.coords
        (dx,dy) = (x1-x0,y1-y0)
        for (l,pt,x) in self.line_segments:
            (x2,y2) = pt.pt.coords
            (dx2,dy2) = (x2-x0,y2-y0)
            a = dx*dy2 - dy*dx2
            b = dx*dx2 + dy*dy2
            #if verbose: print a,b,l,pt,x, x0,y0,x1,y1,x2,y2,dx,dy,dx2,dy2
            if (b>0) and (-epsilon<a<epsilon): # If parallel and in the +ve direction
                return l
            pass
        return None
    #f used_in_lines
    def used_in_lines( self ):
        """Return True if the mesh point is used in any lines."""
        return len(self.line_segments)>0
    #f all_lines
    def all_lines( self ):
        result = []
        for (l,pt,x) in self.line_segments:
            result.append(l)
            pass
        return result
    #f add_to_triangle
    def add_to_triangle( self, triangle ):
        """Add the mesh point to a triangle by updating the mesh point data *only*."""
        self.triangles.append(triangle)
        pass
    #f remove_from_triangle
    def remove_from_triangle( self, triangle ):
        """Remove the mesh point from a triangle by updating the mesh point data *only*."""
        self.triangles.remove(triangle)
        pass
    #f compare_with
    def compare_with( self, other ):
        """
        Compare a mesh point with another mesh point in terms of coordinates.

        Compare the first coordinate - return -1 if this mesh point is less than the other, 1 if greater than, else contine.
        Compare the second coordinate - return -1 if this mesh point is less than the other, 1 if greater than, else contine.
        Return 0 then if the points are equal.
        """
        for i in range(len(self.pt.coords)):
            if self.pt.coords[i]<other.coords[i]: return -1
            if self.pt.coords[i]>other.coords[i]: return 1
        return 0
    #f __repr__
    def __repr__( self ):
        """Provide a string representation of a mesh point including lines and triangles that it is part of."""
        lines = ""
        for l in self.line_segments: lines += "%d,"%l[0].line_num
        tris = ""
        for t in self.triangles: tris += "%d,"%t.triangle_num
        return "mesh_pt(%d:%s:(%s):(%s))"%(self.entry_number,str(self.pt),lines,tris)

#c c_mesh_line
class c_mesh_line( object ):
    """
    A line in a mesh, constructed from two mesh points

    A line in a mesh has the following properties:

    :data:`pts`
        Two points as a tuple that are the end-points of the mesh line, in any order.

    :data:`direction`
        Two coordinates containing the vector from pts[0] to pts[1].

    :data:`triangles`
        A 2-tuple of mesh triangles that the line is part of. If the line is part of no triangles, this will be
        (None, None). If the line is part of only one triangle, triangles[1] will be None.

    :data:`line_num`
        An integer for debug during printing, unique to each mesh_line
    """
    line_log = []
    #f __init__
    def __init__( self, pt0, pt1 ):
        """
        Create a mesh line from two mesh points

        Ensure the mesh is consistent by adding the new line to the two mesh points
        """
        self.line_num = len(self.line_log)
        self.line_log.append(self)
        self.pts = (pt0, pt1)
        self.triangles = (None, None)
        self.winding_order = None
        self.calculate_direction()
        pt0.add_to_line( self, pt1, 0 )
        pt1.add_to_line( self, pt0, 1 )
        pass
    #f calculate_direction
    def calculate_direction( self ):
        (pt0, pt1) = self.pts
        self.direction = (pt1.coords()[0]-pt0.coords()[0], pt1.coords()[1]-pt0.coords()[1])
        return
    #f check_consistent
    def check_consistent( self ):
        """
        Check that the mesh line is consistent with the rest of the mesh.

        Check that the two mesh points at the ends of the line believe that they are part of this mesh line.
        Check that the triangle 2-tuple is not malformed.
        Check that each triangle which the line is part of both the mesh points that the mesh line has as end-points.
        Check that each triangle finds this line in the mesh when the triangle is asked.
        """
        for pt in self.pts:
            if not pt.is_on_line(self):
                raise Exception("Failed to find %s in %s"%(str(self),str(pt)))
            if self.pts.count(pt)>1:
                raise Exception("Duplicate point in %s: %s"%(str(self),str(pt)))
            pass
        if (self.triangles[0] is None) and (self.triangles[1] is not None):
            raise Exception("Badly formed triangle tuple in line %s"%(str(self)))
        for t in self.triangles:
            if t is None: continue
            t_pts = t.get_points()
            for pt in self.pts:
                if pt not in t_pts:
                    raise Exception("Point %s in %s not in line's triangle %s"%(str(pt),str(self),str(t)))
                pass
            if self not in t.find_lines(mesh_only=True):
                raise Exception("%s not found in %s"%(str(self),str(t)))
            pass
        direction = (self.pts[1].coords()[0]-self.pts[0].coords()[0], self.pts[1].coords()[1]-self.pts[0].coords()[1])
        errs = [direction[0]-self.direction[0], direction[1]-self.direction[1]]
        if errs[0]<0: errs[0]=-errs[0]
        if errs[1]<0: errs[1]=-errs[1]
        err = errs[0]+errs[1]
        if err>1E-10:
            raise Exception("%s has bad direction (got %s wanted %s)"%(str(self),str(self.direction),str(direction)))
        pass
    #f change_vertex
    def change_vertex( self, pt_from, pt_to ):
        if pt_from not in self.pts:
            raise Exception("Cannot move %s to %s in %s as it is not part of the line"%(str(pt_from), str(pt_to), str(self)))
        if pt_from==self.pts[1]:
            self.pts = (self.pts[0], pt_to)
            i=1
            pass
        else:
            self.pts = (pt_to,self.pts[1])
            i=0
            pass
        pt_other = self.pts[1-i]
        pt_from.remove_from_line( self )
        pt_other.remove_from_line( self )
        pt_to.add_to_line( self, pt_other, i )
        pt_other.add_to_line( self, pt_to, 1-i )
        pass
    #f get_points
    def get_points( self ):
        """Get a 2-tuple of the two mesh points at the ends of the line."""
        return self.pts
    #f get_length
    def get_length( self ):
        l = math.sqrt( self.direction[0]*self.direction[0]+self.direction[1]*self.direction[1] )
        return l
    #f other_end
    def other_end( self, pt ):
        """Return the other end of the line segment to pt"""
        if self.pts[0]==pt: return self.pts[1]
        if self.pts[1]==pt: return self.pts[0]
        raise Exception("Failed to return other end of %s as %s is not either end"%(str(self),str(pt)))
    #f is_parallel_to
    def is_parallel_to( self, other ):
        """Return true if the mesh lines 'self' and 'other' are parallel."""
        return (self.direction[1]*other.direction[0] - self.direction[0]*other.direction[1])==0
    #f add_to_triangle
    def add_to_triangle( self, tri ):
        """Add the mesh line to a mesh triangle by updating the mesh line data *only*."""
        if self.triangles[0] is None:
            self.triangles=(tri,None)
            pass
        elif self.triangles[1] is None:
            self.triangles=(self.triangles[0],tri)
            pass
        else:
            raise Exception("Cannot add a third triangle %s to %s as a line only has two sides"%(str(tri),str(self)))
        return tri
    #f remove_from_triangle
    def remove_from_triangle( self, tri ):
        """Remove the mesh line from a mesh triangle by updating the mesh line data *only*."""
        if self.triangles[1]==tri:
            self.triangles = (self.triangles[0], None )
            return
        elif self.triangles[0]==tri:
            self.triangles=(self.triangles[1], None)
            return
        raise Exception("Cannot remove %s from %s as it was not present"%(str(tri),str(self)))
    #f num_triangles
    def num_triangles( self ):
        if self.triangles[0] is None: return 0
        if self.triangles[1] is None: return 1
        return 2
    #f find_other_triangle
    def find_other_triangle( self, t ):
        if self.triangles[0]==t: return self.triangles[1]
        return self.triangles[0]
    #f swap_triangle
    def swap_triangle( self, tri_from, tri_to ):
        """Move the mesh line from tri_from to tri_to, but updating the triangles tuple."""
        if self.triangles[0]==tri_from:
            self.triangles = (tri_to,self.triangles[1])
            return
        elif self.triangles[1]==tri_from:
            self.triangles = (self.triangles[0],tri_to)
            return
        raise Exception("Failed to find %s in %s to swap over to another triangle"%(str(tri_from),str(self)))
    #f merge
    def merge( self, other ):
        """
        Merge one mesh line segment with another.

        For two mesh lines with a shared point, remove the two lines and return a new line with the non-shared points
        Cannot be performed it the lines are part of triangles.

        Note that either self.pts[1]==other.pts[0] or self.pts[0]==other.pts[1]

        After this call the mesh point in the middle may require garbage-collecting from the mesh.
        """
        if self.triangles[0] is not None: raise Exception("Attempt to merge mesh lines which are part of triangles")
        if other.triangles[0] is not None: raise Exception("Attempt to merge mesh lines which are part of triangles")
        self_index = 0
        if self.pts[1]==other.pts[0]:
            self_index = 1
            pass
        self.pts[0].remove_from_line( self )
        self.pts[1].remove_from_line( self )
        other.pts[0].remove_from_line( other )
        other.pts[1].remove_from_line( other )
        return c_mesh_line( self.pts[1-self_index], other.pts[self_index] )
    #f can_shorten_diagonal
    def can_shorten_diagonal( self ):
        """
        Determine if this line, being part of two triangles hence forming the diagonal a quadrilateral, would be shorter if it were the other diagonal of the quadrilateral.

        If the mesh line is not part of two triangles, then clearly it cannot be a shorter diagonal.
        If the quadrilateral is concave then the 'other diagonal' will not work (even if shorter) as it would be outside the quadrilateral

        To check for concavity, we know that the quad (ABCD, for quad[0..3]) has a good diagonal AC (this mesh line).
        Now, looking at BD (the other diagonal), we can see that the quadrilateral is concave if both A and C are on the same side of BD.
        We calculate the vector BD as dx1,dy1; the normal (it does not matter which way) is dy1,-dx1.
        The scalar product of AB with the normal to BD is |AB|.|BD_normal|.cos(ABD); the sign of this indicates which side of BD point A is.
        The scalar product of CB with the normal to BD is |CB|.|BD_normal|.cos(CBD); the sign of this indicates which side of BD point C is.
        So if these are multiplied, the result is positive if both points are on the same side, negative if they are on opposite sides, and zero if at least one point is on the line.

        Here 'on the line' is not yet clear - it is best to avoid such circumstances.
        """
        #b Check that there are two triangles
        if self.triangles[1] is None: return False

        #b Get the coordinates (and for humans, the quadrilateral...)
        quad = [self.pts[0].coords(), None, self.pts[1].coords(), None]
        quad[1] = self.triangles[0].get_other_point( self.pts ).coords()
        quad[3] = self.triangles[1].get_other_point( self.pts ).coords()

        #b Check to see if diagonal is shorter - if not, then return False
        (dx0, dy0) = ( quad[2][0]-quad[0][0], quad[2][1]-quad[0][1] )
        (dx1, dy1) = ( quad[3][0]-quad[1][0], quad[3][1]-quad[1][1] )
        if (dx0*dx0+dy0*dy0 <= dx1*dx1+dy1*dy1): return False

        #b Are both quad[0] and quad[2] on the same side of the line quad[3]-quad[1]? If so, concave :-(
        if ( ( dy1*(quad[0][0]-quad[1][0])-dx1*(quad[0][1]-quad[1][1]) ) *
             ( dy1*(quad[2][0]-quad[1][0])-dx1*(quad[2][1]-quad[1][1]) ) ) >= 0: return False
        return True
    #f swap_diagonal
    def swap_diagonal( self, mesh, verbose=False ):
        """
        Trusting that the line has two triangles (ABX and ABY) move it to be XY and the triangles to be AYX and XBY

        For consistency, the line has to be removed from points A and B
        Point B has to be removed from the first triangle
        Point A has to be removed from the second triangle
        Point Y has to be added to the first triangle
        Point X has to be added to the second triangle
        The line is added to points X and Y (line 'XY')
        The line is changed to be X and Y
        The first triangle changes its points from ABX to AXY
        The second triangle changes its points from ABY to XBY
        """
        if self.triangles[1] is None: die_horribly
        A = self.pts[0]
        B = self.pts[1]
        X = self.triangles[0].get_other_point( self.pts )
        Y = self.triangles[1].get_other_point( self.pts )
        if verbose:
            mesh.check_consistent()
            print "********************************************************************************"
            print mesh.__repr__(verbose=True)
            print "********************************************************************************"
            print "Swapping diagonal (A,B) with (X,Y) for line",A,B,X,Y,self
            print "Triangles ",self.triangles[0], self.triangles[1]
        self.pts = ( X, Y )
        self.calculate_direction()
        self.triangles[0].change_point_on_diagonal( B, Y, self.triangles[1] )
        self.triangles[1].change_point_on_diagonal( A, X, self.triangles[0] )
        if verbose:
            print "Now", A,B,X,Y,self
            print "Triangles ",self.triangles[0], self.triangles[1]
            pass
        A.remove_from_line( self )
        B.remove_from_line( self )
        X.add_to_line( self, Y, 0 )
        Y.add_to_line( self, X, 1 )
        if verbose:
            print "********************************************************************************"
            print mesh.__repr__(verbose=True)
            print "********************************************************************************"
            mesh.check_consistent()
            pass
        pass
    #f find_intersection
    def find_intersection( self, pt, dxy ):
        """
        Find intersection of the line segment with a line from pt=(x,y) with vector dxy=(dx,dy)

        Intersection is point Z, and this line segment is A to B
        Z = pt + k.dxy = l.B + (1-l).A = l.(B-A) + A
        k.dxy + l.(A-B) = A-pt

        This can be solved by inverting the matrix
        (A = x0,y0 and B=x1,y1)
        (dxy[0] x0-x1) (k) = ( x0-x )
        (dxy[1] y0-y1) (l)   ( y0-y )

       (k) = (y0-y1   x1-x0 ) (x0-x)    / determinant
       (l)   (-dxy[1] dxy[0]) (y0-y)
        """
        epsilon = 1E-9
        (x0,y0) = self.pts[0].coords()
        (x1,y1) = self.pts[1].coords()
        if True:
            if (dxy[0]>0):
                if (x0<pt[0])        and (x1<pt[0]):        return None
                if (x0>pt[0]+dxy[0]) and (x1>pt[0]+dxy[0]): return None
                pass
            else:
                if (x0>pt[0])        and (x1>pt[0]):        return None
                if (x0<pt[0]+dxy[0]) and (x1<pt[0]+dxy[0]): return None
                pass
            if (dxy[1]>0):
                if (y0<pt[1])        and (y1<pt[1]):        return None
                if (y0>pt[1]+dxy[1]) and (y1>pt[1]+dxy[1]): return None
                pass
            else:
                if (y0>pt[1])        and (y1>pt[1]):        return None
                if (y0<pt[1]+dxy[1]) and (y1<pt[1]+dxy[1]): return None
                pass

        det = dxy[0]*(y0-y1) - dxy[1]*(x0-x1)
        if -epsilon<det<epsilon: return None # Parallel lines
        k =  ((y0-y1)*(x0-pt[0]) + (x1-x0)*(y0-pt[1]))/det
        l =  (-dxy[1]*(x0-pt[0]) +  dxy[0]*(y0-pt[1]))/det
        #print k,l
        #print pt[0]+k*dxy[0] - l*x1 - (1-l)*x0
        if k<0 or k>1 or l<0 or l>1: return None
        return (k, l, pt[0]+k*dxy[0], pt[1]+k*dxy[1])

    #f side_of_line
    def side_of_line( self, pt, verbose=False ):
        """Return <0 if pt is to left of line, >0 if pt is to right of line."""
        (px,py) = pt.coords()
        p0 = self.pts[0].coords()
        if verbose:
            print (px,py), p0
            print self.direction
            print (px-p0[0])*self.direction[1],(py-p0[1])*self.direction[0]
        return (px-p0[0])*self.direction[1] - (py-p0[1])*self.direction[0]
    #f set_winding_order
    def set_winding_order( self, p0=None, p1=None ):
        """Set the winding order for the line to be from p0 to p1"""
        if p0 is None:
            self.winding_order=None
            return
        if p0 not in self.pts or p1 not in self.pts:
            raise Exception("Unable to set winding order of %s as it does not have both points %s and %s"%(str(self),str(p0),str(p1)))
        self.winding_order = (self.pts[0]==p0)
    #f __repr__
    def __repr__( self ):
        winding = "X"
        if self.winding_order is not None: winding="%d"%self.winding_order
        tris = "(X,X)"
        if self.triangles[1] is not None: tris="(%d,%d)"%(self.triangles[0].triangle_num,self.triangles[1].triangle_num)
        elif self.triangles[0] is not None: tris="(%d,X)"%(self.triangles[0].triangle_num)
        return "line(%d:%s:%d:%d:%s)"%(self.line_num,winding,self.pts[0].entry_number,self.pts[1].entry_number,tris)

#c c_mesh_triangle
class c_mesh_triangle( object ):
    """
    A triangle in the mesh contains three points, and implicitly three line segments.

    It is created from the three points, assuming that the lines have already been made.
    The points are c_mesh_point instances
    """
    triangle_log = []
    #f __init__
    def __init__( self, pts ):
        """
        To create a triangle, the lines between the points must have already been created so that the points are connected
        """
        self.triangle_num = len(self.triangle_log)
        self.triangle_log.append(self)
        self.pts = list(pts)
        self.winding_order = None
        pts[0].add_to_triangle( self )
        pts[1].add_to_triangle( self )
        pts[2].add_to_triangle( self )
        pts[0].find_line_segment_to( pts[1] ).add_to_triangle( self )
        pts[1].find_line_segment_to( pts[2] ).add_to_triangle( self )
        pts[2].find_line_segment_to( pts[0] ).add_to_triangle( self )
        pass
    #f check_consistent
    def check_consistent( self ):
        """
        Check that the triangle is consistent within the mesh.

        The triangle is inconsistent if some of the lines in the mesh, derived from the points in the triangle, do not believe they are part of this triangle
        """
        for l in self.find_lines(mesh_only=True):
            if self not in l.triangles:
                raise Exception("Failed to find %s in %s"%(str(self),str(l)))
            pass
        pass
    #f find_lines
    def find_lines( self, mesh_only=False ):
        """
        Find the three lines that make up the triangle, using the triangles mesh points and finding the lines that they form.
        """
        lines = []
        for i in range(3):
            pt = self.pts[i]
            for j in range(1,3):
                l = pt.find_line_segment_to(self.pts[(i+j)%3], mesh_only)
                if l is None:
                    raise Exception("Line segment from %s to %s is None for triangle %s"%(str(pt),str(self.pts[(i+j)%3]),str(self)))
                if l not in lines:
                    lines.append(l)
                    pass
                pass
            pass
        if len(lines)!=3: raise Exception("Triangle %s seems to have more than three lines that make it up %s"%(str(self), str(lines)))
        return lines
    #f change_vertex
    def change_vertex( self, pt_from, pt_to ):
        """
        Change a vertex for a triangle and update the mesh point data - do not touch the line data
        """
        for i in range(3):
            if self.pts[i]==pt_from: self.pts[i]=pt_to
            pass
        pt_from.remove_from_triangle( self )
        pt_to.add_to_triangle( self )
        pass
    #f change_point_on_diagonal
    def change_point_on_diagonal( self, pt_from, pt_to, other_triangle ):
        """
        Change a point 'F' from this triangle to be point 'T' consistently.

        This triangle is 'ABF', the other triangle is 'AFT'; they are becoming 'ABT' and 'BFT'.
        The five lines to start with AB, BF, FT, AT, and the common line AF
        The five lines a full swap of the diagonal are AB, AT, BF, FT, and the common line BT
        The lines AB and FT remain in the triangles they were in.
        The line AT is in the other triangle to start and will move to this one
        The line BF is in this triangle to start and will move to the other one
        The common line AF becomes the new common line BT that is in both triangles
        This method takes charge of only changing line BF to believe it is no longer in this triangle, but in other

        Find the point 'pt_from' (F) in the triangle's list of points
        Find the lines 'AF' and 'BF', and if that is in this triangle but not the other (it is BF) then change the line to be part of the other triangle.
        This is done for consistency.
        Then remove F from this triangle and add T to this triangle
        """
        for i in range(3):
            if self.pts[i]==pt_from:
                for j in range(1,3):
                    l = pt_from.find_line_segment_to( self.pts[(i+j)%3], mesh_only=True )
                    if (self in l.triangles) and not (other_triangle in l.triangles):
                        l.swap_triangle( self, other_triangle)
                        pass
                    pass
                pt_from.remove_from_triangle( self )
                pt_to.add_to_triangle( self )
                self.pts[i] = pt_to
                return
            pass
        raise Exception("Cannot change %s as it is not in %s"%(str(pt_from),str(self)))
    #f get_other_point
    def get_other_point( self, pts ):
        """Get the point in the triangle that is not in the 2-tuple 'pts'."""
        for p in self.pts:
            if p not in pts: return p
            pass
        return None
    #f get_points
    def get_points( self ):
        """Get the points in the triangle."""
        return self.pts
    #f get_area
    def get_area( self ):
        """Return the area of the triangle"""
        (x0,y0) = self.pts[0].coords()
        (x1,y1) = self.pts[1].coords()
        (x2,y2) = self.pts[2].coords()
        area = (x1-x0)*(y2-y0) - (x2-x0)*(y1-y0)
        if (area<0): area=-area
        return area
    #f set_winding_order
    def set_winding_order( self, line=None, winding_order_base=0, verbose=False ):
        """
        Set the winding order for the triangle based on a line and a winding order for the other side of the line
        """
        if self.winding_order is not None: return[]
        #verbose = (self.triangle_num==41) or (self.triangle_num==25)
        if line is None:
            self.winding_order = None
            return []
        p = self.get_other_point( line.pts )
        if verbose:
            print line.pts
            print line
            print p
        if line.winding_order is None:
            self.winding_order = winding_order_base
        else:
            side_of_line = line.side_of_line( p, verbose=verbose )
            if (side_of_line<0) and (line.winding_order):
                self.winding_order = winding_order_base-1
                pass
            elif (side_of_line>0) and (not line.winding_order):
                self.winding_order = winding_order_base-1
                pass
            else:
                self.winding_order = winding_order_base+1
                pass
            pass
        l0 = line.pts[0].find_line_segment_to(p)
        l1 = line.pts[1].find_line_segment_to(p)
        return [l0, l1]
    #f __repr__
    def __repr__( self ):
        """Return a representation of the triangle."""
        winding = "X"
        if self.winding_order is not None: winding="%d"%self.winding_order
        return "tri(%d:%s,%d,%d,%d,%6.2f)"%(self.triangle_num,winding,self.pts[0].entry_number,self.pts[1].entry_number,self.pts[2].entry_number,self.get_area())

#c c_mesh
class c_mesh( object ):
    """
    A mesh is a set of mesh points, which are connected by mesh line segments, which are then filled with non-overlapping mesh triangles.

    It can be created from a set of contours, from which a set of mesh points is generated.
    Mesh lines are then created for the points to enable it to be filled with triangles, and triangles are made to fill the convex hull of the mesh points.
    Then the contours can be applied to ensure that all of the contours are present as mesh line segments.

    After the mesh is fully built with contours winding rules and fill can be applied, or gradients applied to lines.

    The mesh always has a list of points (self.point_set), list of line segments, and a list of triangles
    This is a list of c_mesh_points
    Each mesh point has a list of lines it is part of
    The list of line_segments is a list of c_mesh_lines(pta,ptb)
    Each mesh line has a pts=(pta,ptb) tuple attribute and a (tria,trib) triangle tuple
    The triangle list is a list of c_mesh_triangle()
    Each triangle has a list of 3 points, triangle number (unique id), winding order (None, True or False, for whether it is in/out or unknown)

    To use a mesh with contours:
    x = c_mesh()
    x.add_contour( [c_point,...] )
    x.map_contours_to_mesh()
    x.normalize() - number the points, and remove empty triangles

    To create a mesh for a shape from a set of points
    x = c_mesh()
    x.from_points( [c_point,...] )

    """
    #f __init__
    def __init__( self ):
        """Create an empty mesh."""
        self.reset()
        pass
    #f reset
    def reset( self ):
        """Reset a mesh to be empty."""
        self.line_segments = []
        self.triangles = []
        self.point_set = []
        self.contours = []
        pass
    #f check_consistent
    def check_consistent( self ):
        """
        Check that the mesh is consistent.

        Perform checks for the points, lines and triangles that make up the mesh
        """
        for pt in self.point_set:
            pt.check_consistent()
            pass
        for l in self.line_segments:
            l.check_consistent()
            pass
        for t in self.triangles:
            t.check_consistent()
            pass
        pass
    #f find_insertion_index
    def find_insertion_index( self, set, element, compare_fn ):
        """
        Find where to insert an element in a set, using a specified compare_fn

        compare_fn takes (set_element, element) and returns -1 if set_element<element, 0 if set_element==element, 1 if set_element>element

        Return (index, match); if match is True then element compares to match (compare_fn returned 0)
        index is the index of the entry in 'set' to insert 'element' before to maintain an ordered list (i.e. set[index-1]<element<set[index])

        Use a binary search
        """
        l = len(set)
        if l==0: return (0, False)
        (i0, i1) = (-1,l)
        while i0<i1-1:
            im = (i0+i1)/2
            cmp = compare_fn( set[im], element )
            if cmp==0:
                return (im, True)
            if cmp<0: # i.e. im is 'less' than element
                i0 = im
                pass
            else:
                i1 = im
                pass
            pass
        return (i1, False)
    #f add_point
    def add_point( self, point, append_to_numbers=False ):
        """
        Add a point to the set of points in the mesh

        point is NOT a mesh point
        Add an external representation of a point to the set of points in the mesh, and return that object
        If the point is already in our set, return that object
        Keep the point set ordered by coords
        """
        (ins, match) = self.find_insertion_index( self.point_set, point, lambda s,e:s.compare_with(e) )
        if match: return self.point_set[ins]
        new_point = c_mesh_point( point )
        self.point_set.insert( ins, new_point )
        if append_to_numbers:
            new_point.entry_number = len(self.point_set)
            pass
        return new_point
    #f remove_point
    def remove_point( self, pt ):
        """
        Remove a point from the mesh - just from the mesh data
        """
        self.point_set.remove( pt )
        return
    #f add_line
    def add_line( self, pt0, pt1 ):
        """
        Add a line to the mesh using two mesh points.
        """
        line = c_mesh_line(pt0,pt1)
        self.line_segments.append( line )
        return line
    #f remove_line
    def remove_line( self, line ):
        """
        Remove a line to the mesh - just from the mesh data
        """
        self.line_segments.remove( line )
        return
    #f find_or_create_line
    def find_or_create_line( self, pt0, pt1 ):
        line = pt0.find_line_segment_to(pt1)
        if line is not None: return line
        return self.add_line( pt0, pt1 )
    #f add_triangle_from_points
    def add_triangle_from_points( self, pts ):
        """
        Must add a triangle from points to ensure that the winding order is passed in cleanly
        """
        self.find_or_create_line( pts[0], pts[1] )
        self.find_or_create_line( pts[1], pts[2] )
        self.find_or_create_line( pts[2], pts[0] )
        triangle = c_mesh_triangle( pts )
        self.triangles.append(triangle)
        return triangle
    #f remove_triangle
    def remove_triangle( self, tri ):
        """
        Remove a triangle from the mesh - just from the mesh data
        """
        self.triangles.remove( tri )
        return
    #f add_contour
    def add_contour( self, pts, closed=True, contour_data=None ):
        """
        Add a contour to the mesh

        The points must be a list of 'point class' instances which are joined by line segments that make the contour
        The contour may be closed (last point has a line segment to the first point) or open (effectively just a line)
        The contour_data is opaque to the mesh; it can include contour height, winding order, etc, depending on the mesh usage.

        The contour is just added to the mesh; later method invocations are required to create the mesh points and lines
        """
        self.contours.append( {"pts":pts, "mesh_pts":[], "closed":closed, "data":contour_data} )
        pass
    #f add_bezier_list_contour
    def add_bezier_list_contour( self, bezier_list, closed=False, contour_data=None, straightness=1000, perturbation=None ):
        points = []
        i = 0
        for b in bezier_list:
            subbeziers = b.break_into_segments(straightness)
            for s in subbeziers:
                if perturbation is not None:
                    s.pts[0].perturb(i*perturbation)
                    pass
                points.append(s.pts[0])
                i += 1
                pass
            pass
        self.add_contour( points, closed=closed, contour_data=contour_data )
        return self
    #f map_contours_to_mesh
    def map_contours_to_mesh( self ):
        """
        Map the contours of the mesh to mesh points

        Add all the points as mesh points, and update the contour.
        """
        for c in self.contours:
            mesh_pts = c["mesh_pts"]
            for p in c["pts"]:
                mesh_pts.append( self.add_point( p ) )
                pass
            pass
        pass
    #f from_points
    def from_points( self, points ):
        """
        points is a list of c_points

        Must create the set of c_mesh_point, and the line segments that use them
        The points list can then be sorted to start with the smallest X point (with smallest Y on ties)

        Once sorted, one can reorder the line segments to start at that smallest X point.
        This is a normalized mesh
        """
        self.line_segments = []
        p0 = points[-1]
        for i in range(len(points)):
            p1 = points[i]
            self.add_line( p0, p1 )
            p0 = p1
            pass
        pass
    #f from_bezier_list
    def from_bezier_list( self, bezier_list, straightness=1000 ):
        epsilon = 1e-9
        self.reset()
        points = []
        i = 0
        for b in bezier_list:
            subbeziers = b.break_into_segments(straightness)
            for s in subbeziers:
                s.pts[0].perturb(i*epsilon)
                points.append(self.add_point(s.pts[0]) )
                i += 1
                pass
            pass

        self.from_points( points )
        return self
    #f number_points
    def number_points( self ):
        for i in range(len(self.point_set)):
            self.point_set[i].entry_number = i
            pass
        pass
    #f find_first_segment
    def find_first_segment( self ):
        first_segment = None
        for i in range(len(self.line_segments)):
            if self.line_segments[i].pts[0].entry_number==0:
                return i
                break
            pass
        return None
    #f normalize
    def normalize( self ):
        self.number_points()
        self.remove_empty_triangles()
        pass
    #f split_line_segment_in_half
    def split_line_segment_in_half( self, line ):
        (p0,p1) = line.get_points()
        midpoint = bezier.c_point( coords=( 0.5*(p0.coords()[0]+p1.coords()[0]),
                                            0.5*(p0.coords()[1]+p1.coords()[1]) ) )
        pt = self.add_point(midpoint, append_to_numbers=True)
        self.split_line_segment( line, pt )
    #f split_line_segment
    def split_line_segment( self, line, pt, verbose=False ):
        """
        Split a mesh line segment by inserting a mesh point, which should be on the line

        Return the two mesh line segments that replace the original.

        Effectively replace the line with two line segments, plus up to two further line segments if splitting up to 2 triangles, and create up to 2 more triangles.

        For the line, remove the line from the two mesh points at its ends (P0, P1), and create two more line segments L0=(P0,pt) and L1=(pt,p1)

        For each triangle T (P0.P1.X) in the original line's triangles:
            Move T to be P0.Pt.X (change the point P1 on the triangle to Pt, remove T from P1's triangles, add to Pt's triangles)
            Remove triangle T from line P1.X's triangle list
            Add T to L0's triangles list
            Add line LX (Pt.X), and add T to that line
            Add (new) triangle Pt.P1.X to the mesh

        Return (L0, L1)
        """
        if verbose:
            self.check_consistent()
            pass
        (p0, p1) = line.get_points()
        if (pt is p0) or (pt is p1):
            raise Exception("Request to split a line %s at one of its endpoints %s"%(str(line),str(pt)))
        if (pt.find_line_segment_to(p0)):
            raise Exception("Request to split a line %s at %s when there is already a line from there to one end of the line %s from %s"%(str(line),str(pt),str(p0),str(p1)))
        if (pt.find_line_segment_to(p1)):
            raise Exception("Request to split a line %s at %s when there is already a line from there to one end of the line %s from %s"%(str(line),str(pt),str(p1),str(p0)))
        p0.remove_from_line( line )
        p1.remove_from_line( line )
        l0 = self.add_line( p0, pt )
        l1 = self.add_line( pt, p1 )

        if verbose:
            print "Split line",line,pt
            print "p0",p0
            print "p1",p1
            print "l0",l0
            print "l1",l1
        for t in line.triangles:
            if t is None: continue
            x = t.get_other_point( (p1, p0) )
            t.change_vertex( p1, pt )
            p1.find_line_segment_to( other=x, mesh_only=True ).remove_from_triangle( t )
            l0.add_to_triangle( t )
            lx = self.add_line( pt, x )
            lx.add_to_triangle( t )
            self.add_triangle_from_points( (pt, p1, x) )
            pass

        self.remove_line( line )
        if verbose:
            self.check_consistent()
            pass
        return (l0, l1)
    #f remove_empty_triangles
    def remove_empty_triangles( self ):
        """
        Find all pair of consecutive line segments make a 'zero area' triangle, and merge to a single line segment

        If the line segments are (a, b) and (b,c), and b-a and c-b are parallel, then change first line segment to be (a,c) and remove the second
        """
        l = len(self.line_segments)
        i = l-1
        while i>0:
            if self.line_segments[i].is_parallel_to(self.line_segments[(i+1)%l]):
                self.line_segments[i] = self.line_segments[i].merge(self.line_segments[(i+1)%l])
                old_point = self.line_segments.pop((i+1)%l)
                if not old_point.used_in_lines():
                    self.remove_unused_point( old_point )
                    pass
                if (i+1==l): i-= 2
                l -= 1
                pass
            else:
                i -= 1
                pass
            pass
        pass
    #f fill_convex_hull_with_triangles
    def fill_convex_hull_with_triangles( self, must_be_used_in_lines=False ):
        """
        Starting with a normalized mesh, we can generate filled triangles

        A normalized mesh has a sorted set of points and a list of line segments starting at any point without any consecutive parallel line segments
        Since we can guarantee that no consecutive line segments are parallel, two consecutive line segments must form a non-zero area triangle

        Sort all points after the 'first point (x0,y0) (left-most, top-most)' by angle to y=y0 (-90,+90).
        The sweep all points creating triangles from (x0,y0) to (xn,yn), (xn+1,yn+1) in the swept order
        """
        radial_order = []
        (x0,y0) = self.point_set[0].coords()
        for pt in self.point_set[1:]:
            if must_be_used_in_lines and not pt.used_in_lines(): continue
            (x,y) = pt.coords()
            (dx,dy) = (x-x0,y-y0)
            (ins, match) = self.find_insertion_index( radial_order, (dx,dy), lambda s,e:s[0]*e[1]-s[1]*e[0] )
            radial_order.insert( ins, (dx, dy, pt) )
            pass
        radial_order.insert(0,(0,0,self.point_set[0]))
        num_points_used = len(radial_order)
        if num_points_used<3:
            return
        # First fill from the 'starter point'
        for i in range(2,num_points_used):
            self.add_triangle_from_points( (radial_order[0][2],radial_order[i-1][2], radial_order[i][2]) )
            pass

        # Now fill in the perimeter (Graham Scan)
        hull_pts = [ radial_order[0][2], radial_order[1][2], radial_order[2][2] ]
        next_point = 3
        while next_point<num_points_used:
            # Check for concavity from (hull_pts[-2], hull_pts[-1]) and (hull_pts[-1],next_point)
            # If not, can add next_point to the hull
            # If there is, then:
            #      add a triangle to fill in the concavity
            #      pop hull_pts[-1] from the points on the hull
            is_concavity = True
            if (len(hull_pts)<2):
                is_concavity = False
                pass
            else:
                (x0,y0) = hull_pts[-2].coords()
                (x1,y1) = hull_pts[-1].coords()
                (x2,y2) = radial_order[next_point][2].coords()
                (dx1,dy1) = (x1-x0,y1-y0)
                (dx2,dy2) = (x2-x0,y2-y0)
                is_concavity = ((dx1*dy2-dy1*dx2)>0)
                pass
            if is_concavity:
                self.add_triangle_from_points( (hull_pts[-2], hull_pts[-1], radial_order[next_point][2] ) )
                hull_pts.pop()
                pass
            else:
                hull_pts.append( radial_order[next_point][2] )
                next_point = next_point+1
                pass
            pass
        # Remove any zero-area triangles which 
        #for l in self.line_segments:
        #    tris = l.get_triangles()
        #    for t in tris:
        #        if t.is_degenerate_with_longest_side(l):
        #            l.swap_as_diagonals()
        #            break
        #        pass
        #    pass

        # Now ensure that the actual lines forming the mesh are in the set of lines
        # tricky
        pass
    #f merge_two_line_ends
    def merge_two_line_ends( self, line, verbose=False ):
        """
        The line to remove (L=AB) can have up to two triangles (T=ABC)
        T has lines AB, BC, AC; the end result is to remove T and merge BC and AC (as A and B become one point)
          Change T in AC and BC to be the other triangle from the other line
          Remove BC from point C
          Remove BC from the mesh
          Remove T from point C
          Remove T from mesh
        Remove AB from the mesh
        For all triangles in the mesh which include B, make them use A instead
        For all lines in the mesh which include B, make them use A instead
        Remove B from the mesh
        """
        (A,B) = line.get_points()
        (xA,yA) = A.coords()
        (xB,yB) = B.coords()
        xA = (xA+xB)/2.0
        yA = (yA+yB)/2.0
        A.set_coords( coords=(xA,yA) )
        for t in line.triangles:
            if t is None: continue
            C = t.get_other_point( (A,B) )
            AC = A.find_line_segment_to( C )
            BC = B.find_line_segment_to( C )
            tac = AC.find_other_triangle(t)
            tbc = BC.find_other_triangle(t)
            AC.swap_triangle(t,tbc)
            A.remove_from_triangle(t)
            C.remove_from_triangle(t)
            C.remove_from_line(BC)
            self.remove_line(BC)
            self.remove_triangle( t )
            pass
        self.remove_line(line)
        A.remove_from_line(line)
        self.remove_point(B)
        for t in self.triangles:
            if B in t.get_points():
                t.change_vertex(B,A)
                pass
            pass
        for l in self.line_segments:
            if l is line: continue
            lpts = l.get_points()
            if B in lpts:
                print "Change vertex for %s from %s to %s"%(str(l),str(B),str(A))
                l.change_vertex(B,A)
                print "Changed vertex for %s from %s to %s"%(str(l),str(B),str(A))
                pass
            elif A in lpts:
                l.calculate_direction()
                pass
            pass
        for c in self.contours:
            mesh_pts = c["mesh_pts"]
            for i in range(len(mesh_pts)):
                if mesh_pts[i]==B: mesh_pts[i] = A
                pass
            i=0
            while i<len(mesh_pts):
                if (mesh_pts[i]==A) and (mesh_pts[(i+1)%len(mesh_pts)]==A):
                    mesh_pts.pop(i)
                    pass
                else:
                    i+=1
                    pass
                pass
            pass
        pass
    #f remove_small_lines
    def remove_small_lines( self, min_length, verbose=False ):
        """
        Find all lines below a smallest length and remove them by merging the two points

        Return number of lines removed
        Check all lines
        If the line length is not small, continue, else remove the line by merging its two ends
        """
        if verbose:
            print "%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%"
            print "Removing small lines"
            self.check_consistent()
            print self.__repr__(verbose=True)
            pass
        lines_removed = 0
        i = 0
        while i<len(self.line_segments):
            l = self.line_segments[i]
            if l.get_length()>min_length:
                i+=1
                continue
            if verbose:
                print "********************************************************************************"
                print "Length %f of %s, want to remove"%(l.get_length(),str(l))
                pass
            #self.check_consistent()
            self.merge_two_line_ends(l, verbose=verbose)
            #print self.__repr__(verbose=True)
            #self.check_consistent()
            lines_removed += 1
            pass
        if verbose:
            print "%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%"
            print "Lines removed",lines_removed
            print self.__repr__(verbose=True)
            self.check_consistent()
        return lines_removed
    #f remove_small_area_triangles
    def remove_small_area_triangles( self, min_area, verbose=False ):
        """
        Find all triangles below a smallest area and remove them by moving the mesh point not on the longest side to be in line with the longest side

        Return number of triangles removed
        Check all triangles
        If the triangle area is not small, continue, else remove the triangle
        The triangle to remove (T=ABC) must be 'nearly a straight line', i.e. the longest side of the triangle (AB)
        IF AB is the longest side then C = (qA + (1-q)B) + e.perp(BA) where 0<q<1
        (A-C).(B-C) = ((q-1)(A+B) . 
        Find the point of the triangle that is not on the longest side (C), and move it gently so it is on the longest side
          Note that C = k.AB + l.(normal to AB); find k, then make C=k.AB
          Find the triangle the other side of AB (T2=ABX)
          If T2 exists (i.e. AB borders 2 triangles)
            We want to have 2 triangles ACX and BCX
            Since C is between A and B on AB, ACBX must be convex
            So swap the diagonal (AB.swap_diagonal( mesh ) )
          Else (AB borders one triangle)
            Remove T from lines AC and BC
            Remove T from points A and B
            Remove AB from points A and B
            Remove T from the mesh
            Remove AB from the mesh
        """
        if verbose:
            print "%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%"
            print "Removing triangles"
            self.check_consistent()
            print self.__repr__(verbose=True)
            pass
        #verbose = True
        triangles_removed = 0
        i = 0
        while i<len(self.triangles):
            t = self.triangles[i]
            if t.get_area()>min_area:
                i+=1
                continue
            if verbose:
                print "********************************************************************************"
                print "Area %f of %s, want to remove"%(t.get_area(),str(t))
                pass
            (A,B,C) = t.get_points()

            (Ax,Ay) = A.coords()
            (Bx,By) = B.coords()
            (Cx,Cy) = C.coords()
            lAB2 = (Ax-Bx)*(Ax-Bx)+(Ay-By)*(Ay-By)
            lAC2 = (Ax-Cx)*(Ax-Cx)+(Ay-Cy)*(Ay-Cy)
            lBC2 = (Bx-Cx)*(Bx-Cx)+(By-Cy)*(By-Cy)
            while (lAB2<lAC2) or (lAB2<lBC2):
                (A,B,C) = (B,C,A)
                (lAB2, lAC2, lBC2) = (lBC2, lAB2, lAC2)
                pass
            (Ax,Ay) = A.coords()
            (Bx,By) = B.coords()
            (Cx,Cy) = C.coords()
            l = (By-Ay)*(By-Ay)+(Bx-Ax)*(Bx-Ax)
            k = ((Cx-Ax)*(Bx-Ax) + (Cy-Ay)*(By-Ay)) / l
            if verbose:
                print (Ax,Ay), (Bx,By), (Cx,Cy), k, l
                print "Will move C to",(Ax*(1-k)+k*Bx,Ay*(1-k)+k*By)
                pass
            C.set_coords( (Ax*(1-k)+k*Bx,Ay*(1-k)+k*By) )
            for cl in C.all_lines():
                cl.calculate_direction()
                pass
            AB = A.find_line_segment_to(B)
            AC = A.find_line_segment_to(C)
            BC = B.find_line_segment_to(C)
            if AB.num_triangles()==1:
                #self.check_consistent()
                A.remove_from_triangle( t )
                B.remove_from_triangle( t )
                AC.remove_from_triangle( t )
                BC.remove_from_triangle( t )
                A.remove_from_line( AB )
                B.remove_from_line( AB )
                self.remove_line( AB )
                self.remove_triangle( t )
                #self.check_consistent()
                pass
            else:
                #self.check_consistent()
                AB.swap_diagonal( self, verbose=verbose )
                #self.check_consistent()
                pass
            i+=1
            pass
        if verbose:
            print "%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%"
            print "Triangles removed",triangles_removed
            print self.__repr__(verbose=True)
            self.check_consistent()
        return triangles_removed
    #f shorten_quad_diagonals
    def shorten_quad_diagonals( self, verbose=False ):
        """
        Swap diagonals of quadrilaterals by picking the shortest of each one

        Return number of triangles changed
        """
        work_done = 0
        for i in range(len(self.line_segments)):
            l = self.line_segments[i]
            if l.can_shorten_diagonal():
                l.swap_diagonal( self, verbose=verbose  )
                work_done += 1
                #self.check_consistent()
                #return
                pass
            pass
        #self.split_line_segment_in_half( self.line_segments[0] )

        return work_done
    #f find_line_segments_on_line
    def find_line_segments_on_line( self, pt0, pt1 ):
        """
        Find all the line segments that intersect a line between two mesh points if the line is not between two mesh points already
        """
        intersections = []
        (x0,y0) = pt0.coords()
        (x1,y1) = pt1.coords()
        (dx,dy) = (x1-x0, y1-y0)
        for l in self.line_segments:
            l_pts = l.get_points()
            if pt0 in l_pts or pt1 in l_pts: continue
            intersect = l.find_intersection( (x0,y0), (dx,dy) )
            if intersect is not None:
                intersections.append( (l, intersect) )
                pass
            pass
        return intersections
    #f split_a_line_for_contour_segment
    def split_a_line_for_contour_segment( self, mesh_pts, pt_num, intersections, max_breaks=1 ):
        """
        Split a line between mesh_pts[pt_num-1] and mesh_pts[pt_num] using one or more of the list of intersections.

        intersections is returned by find_line_segments_on_line, and so is a list of (line segment, intersection info) tuples
        intersection info is (k, l, x, y) where k is how far along the line segment to split and l is how far between the two mesh points the split would be.
        (k and l are in the range 0 to 1).

        First cut is to split at lowest l...
        """
        min_l = 2
        min_i = None
        for i in range(len(intersections)):
            if intersections[i][1][1]<min_l:
                min_l=intersections[i][1][1]
                min_i=i
                pass
            pass
        (x,y) = (intersections[min_i][1][2],intersections[min_i][1][3])
        pt = self.add_point(bezier.c_point( coords=(x,y) ), append_to_numbers=True)
        mesh_pts.insert( pt_num, pt )
        self.split_line_segment( intersections[min_i][0], pt )
        return
    #f ensure_contours_on_mesh
    def ensure_contours_on_mesh( self, verbose=False ):
        """
        For every line segment in every contour, if the line segment is not present in the mesh, split

        Check every pair of mesh points on every contour.
        If the line between the points is not a line segment, then chose one from the set of line segments that lies between the two points and split that at the correct point, adding this new point to the contour
        Return the total number of lines split.

        At each call the situation is improved; however, the method should be invoked repeatedly until it returns zero if all contours are required to be on the mesh.
        Between calls of this method the mesh can be optimized with, for example, calls of the shorten_quad_diagonals() method.
        """
        lines_changed = 0
        for c in self.contours:
            mesh_pts = c["mesh_pts"]
            p0 = mesh_pts[-1]
            if not c["closed"]: p0=None
            i = 0
            while i<len(mesh_pts):
                p = mesh_pts[i]
                if (p0 is not None) and (p0.find_line_segment_to(p) is None):
                    #verbose = (p0.entry_number==7) and (p.entry_number==11)
                    l0 = p0.find_line_segment_toward( p, verbose=verbose )
                    l1 = p.find_line_segment_toward( p0, verbose=verbose )
                    if verbose:
                        print i, mesh_pts, p0, p, l0, l1
                    if l0 is not None:
                        mesh_pts.insert( i, l0.other_end(p0) )
                        lines_changed+=1
                        pass
                    elif l1 is not None:
                        mesh_pts.insert( i, l1.other_end(p) )
                        lines_changed+=1
                        p=p0
                        i-=1
                        pass
                    else:
                        ls = self.find_line_segments_on_line( p0, p )
                        if len(ls)>0:
                            self.split_a_line_for_contour_segment( mesh_pts, i, ls )
                            lines_changed+=1
                            pass
                        pass
                    pass
                p0 = p
                i+=1
                pass
            pass
        return lines_changed

    #f assign_winding_order_to_contours
    def assign_winding_order_to_contours( self ):
        """
        Assign a winding order to mesh line segments which make up lines

        For every line segment making a contour set the winding order to be that of the contour
        """
        for l in self.line_segments:
            l.set_winding_order()
            pass

        for c in self.contours:
            mesh_pts = c["mesh_pts"]
            p0 = mesh_pts[-1]
            if not c["closed"]: p0=None
            i = 0
            while i<len(mesh_pts):
                p = mesh_pts[i]
                if p0 is not None:
                    l = p0.find_line_segment_to(p)
                    if l is not None: # Should be none if ensure_contours_on_mesh process is complete, but do not require it
                        l.set_winding_order(p0,p)
                        pass
                    pass
                p0 = p
                i+=1
                pass
            pass
        pass
    #f assign_winding_order_to_mesh
    def assign_winding_order_to_mesh( self ):
        """
        Assign a winding order to the whole mesh given that some lines have a winding order

        Clear the winding order for each triangle
        Work from the 'outside' in of the mesh.
           Create a list of lines segments that border exactly one triangle
           Pop the first line in the list
             If there are two triangles for the line and both already have a winding order, move on
             If there is one triangle for the line, set its winding order based on the winding order of the line
             If there are two triangles for the line then at least one has a winding order, and set the winding order of the other triangle
             For each triangle whose winding order is set, and the other lines in the triangle to the list of line segments to work on
           Repeat until the work list is empty

        If a line has 'None' as its winding order, then the triangles on both sides have the same winding order
        If a line has 'False' as its winding order, then the triangle on the 'left' of the line (that whose third point is left of line.pts[0] -> line.pts[1]) has -1 of the other triangle
        If a line has 'True' as its winding order, then the triangle on the 'left' of the line (that whose third point is left of line.pts[0] -> line.pts[1]) has +1 of the other triangle
        """
        for t in self.triangles:
            t.set_winding_order()
            pass

        work_list = []
        for l in self.line_segments:
            if l.num_triangles()==1:
                work_list.append(l)
                pass
            pass

        while len(work_list)>0:
            l = work_list.pop(0)
            (t0, t1) = l.triangles
            if (t1 is not None) and (t0.winding_order is not None) and (t1.winding_order is not None): continue
            if t1 is None:
                work_list.extend( t0.set_winding_order(l) )
                pass
            elif (t1 is not None) and (t1.winding_order is not None):
                work_list.extend( t0.set_winding_order(l,t1.winding_order) )
                pass
            elif (t0 is not None) and (t0.winding_order is not None):
                work_list.extend( t1.set_winding_order(l,t0.winding_order) )
                pass
            pass
        pass
    #f get_vertices_and_triangles
    def get_vertices_and_triangles( self ):
        """
        Generate lists of all vertices

        Generate triangle strips (list of triangle strips) for all triangles
          triangle strip = [ vertex index, vertex index, ...]
        Generate list of edges in counter-clockwise order
          an edge is a line that does not have two triangles
          may need to have a 'other-handedness flag' so the mesh can be 'inverted'
        """
        pass
    #f __repr__
    def __repr__( self, verbose=False ):
        result =  "mesh\n"
        result += "  pts: %s\n"%(str(self.point_set))
        result += "  lns: %s\n"%(str(self.line_segments))
        result += "  tris: %s\n"%(str(self.triangles))
        if verbose:
            result = result.replace(", ",",\n        ")
        return result

#a Mesh pygame test
def mesh_test_get_draw_fn():
    import gjslib.graphics.font as font
    x = c_mesh()
    bezier_list = []
    for (p0,c0,p1) in [ ( (100,100), (110,90), (150, 50) ),
                        ( (150, 50), (150,150), (200,100) ),
                        ( (200,100), (150,150), (200,200) ),
                        ( (200,200), (175,175), (150,150) ),
                        ( (150,150), (125,125), (100,100) ),
                    ]:
        p0 = bezier.c_point(coords=p0)
        c0 = bezier.c_point(coords=c0)
        p1 = bezier.c_point(coords=p1)
        bezier_list.append(bezier.c_bezier2(pts=(p0,c0,p1)))
        pass
    f = font.c_font("benegraphic").load_from_ttx("/Users/gstark_old/a.ttx")
    bezier_list = f.create_bezier_lists( "ampersand" )[0]
    print bezier_list
    x.from_bezier_list( bezier_list=bezier_list, straightness=10 )
    #print x
    print "Normalizing"
    x.normalize()
    print x.__repr__(verbose=True)
    print "Filling"
    x.fill_convex_hull_with_triangles()
    print x.__repr__(verbose=True)
    x.check_consistent()
    print "Shorten"
    i=0
    while x.shorten_quad_diagonals(i>100)>0:
        i+=1
        if i>101:break
        pass
    print "broken out after",i
    x.check_consistent()
    def draw_fn( screen ):
        draw_triangles( screen, x.triangles )
        draw_contour( screen, x )
    return draw_fn

