#!/usr/bin/arch -32 /System/Library/Frameworks/Python.framework/Versions/2.7/bin/python
#!/usr/bin/env python
#a Imports
import pygame
import sys, os

sys.path.insert(0, os.path.abspath('../python'))
import gjslib.math.bezier as bezier
import gjslib.graphics.font as font
import gjslib.math.mesh as mesh

#a Polygon classes
#c c_polygon_point
class c_polygon_point( object ):
    #f __init__
    def __init__( self, pt ):
        self.pt = pt
        self.triangles = []
        self.line_segments = []
        self.entry_number = -1
        pass
    #f check_consistent
    def check_consistent( self ):
        for l in self.line_segments:
            if self not in l[0].get_points():
                raise Exception("Failed to find point %s in line %s"%(str(self),str(l)))
            if self.line_segments.count(l)>1:
                raise Exception("Duplicate line in point %s: line %s"%(str(self),str(l)))
            pass
        for t in self.triangles:
            if t is not None:
                if self not in t.pts:
                    raise Exception("Failed to find point %s in triangle %s"%(str(self),str(t)))
                pass
            if self.triangles.count(t)>1:
                raise Exception("Duplicate triangle in point %s: triangle %s"%(str(self),str(t)))
            pass
        pass
    #f coords
    def coords( self ):
        return self.pt.coords
    #f add_to_line
    def add_to_line( self, line, other, line_pt_num ):
        #print "adding point to line as point",self, line, line_pt_num
        self.line_segments.append( (line, other, line_pt_num) )
        #print self.line_segments
        pass
    #f remove_from_line
    def remove_from_line( self, line ):
        #print "removing point from line",self, line, self.line_segments
        for i in range(len(self.line_segments)):
            if self.line_segments[i][0]==line:
                self.line_segments.pop(i)
                return
            pass
        die_horribly
        return
    #f is_on_line
    def is_on_line( self, line ):
        for (l,pt,x) in self.line_segments:
            if l == line: return True
            pass
        return False
    #f find_line_segment_to
    def find_line_segment_to( self, other, mesh_only=False ):
        for (l,pt,x) in self.line_segments:
            if mesh_only and (l.triangles[0] is None): continue
            if pt==other: return l
            pass
        return None
    #f used_in_lines
    def used_in_lines( self ):
        return len(self.line_segments)>0
    #f add_to_triangle
    def add_to_triangle( self, triangle ):
        self.triangles.append(triangle)
        pass
    #f remove_from_triangle
    def remove_from_triangle( self, triangle ):
        self.triangles.remove(triangle)
        pass
    #f compare_with
    def compare_with( self, other ):
        for i in range(len(self.pt.coords)):
            if self.pt.coords[i]<other.coords[i]: return -1
            if self.pt.coords[i]>other.coords[i]: return 1
        return 0
    #f __repr__
    def __repr__( self ):
        lines = ""
        for l in self.line_segments: lines += "%d,"%l[0].line_num
        tris = ""
        for t in self.triangles: tris += "%d,"%t.triangle_num
        return "pt(%d:%s:(%s):(%s))"%(self.entry_number,str(self.pt),lines,tris)

#c c_polygon_line
class c_polygon_line( object ):
    """
    A line in a polygon

    It has two points leading in the 'direction' of the line
    It has two triangles (either of which may be None)
    """
    line_log = []
    #f __init__
    def __init__( self, pt0, pt1, on_contour=True ):
        self.line_num = len(self.line_log)
        self.line_log.append(self)
        self.pts = (pt0, pt1)
        self.direction = pt1.pt.add(pt0.pt,factor=-1)
        self.triangles = (None, None)
        self.on_contour = on_contour
        pt0.add_to_line( self, pt1, 0 )
        pt1.add_to_line( self, pt0, 1 )
        self.in_use = True
        pass
    #f check_consistent
    def check_consistent( self ):
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
        pass
    #f get_points
    def get_points( self ):
        return self.pts
    #f num_triangles
    def num_triangles( self ):
        """Return number of triangles the line is part of (0, 1, or 2)."""
        if self.triangles[0] is None: return 0
        if self.triangles[1] is None: return 1
        return 2
    #f is_parallel_to
    def is_parallel_to( self, other ):
        return self.direction.is_parallel_to(other.direction)
    #f add_triangle
    def add_triangle( self, tri ):
        if self.triangles[0] is None:
            self.triangles=(tri,None)
            pass
        elif self.triangles[1] is None:
            self.triangles=(self.triangles[0],tri)
            pass
        else:
            die_horribly
        return tri
    #f swap_triangle
    def swap_triangle( self, tri_from, tri_to ):
        if self.triangles[0]==tri_from:
            self.triangles = (tri_to,self.triangles[1])
            pass
        elif self.triangles[1]==tri_from:
            self.triangles = (self.triangles[0],tri_to)
            pass
        return
    #f merge
    def merge( self, other ):
        """
        Either self.pts[1]==other.pts[0] or self.pts[0]==other.pts[1]

        Either way we are basically removing the lines 'self' and 'other'
        """
        self_index = 0
        if self.pts[1]==other.pts[0]:
            self_index = 1
            pass
        self.pts[0].remove_from_line( self )
        self.pts[1].remove_from_line( self )
        other.pts[0].remove_from_line( other )
        other.pts[1].remove_from_line( other )
        return c_polygon_line( self.pts[1-self_index], other.pts[self_index] )
    #f can_shorten_diagonal
    def can_shorten_diagonal( self ):
        """
        If the line has two triangles (one on each side) then see if the quad formed is convex and the shorter diagonal could be taken
        """
        if self.triangles[1] is None: return False
        quad = [self.pts[0].coords(), None, self.pts[1].coords(), None]
        quad[1] = self.triangles[0].get_other_point( self.pts ).coords()
        quad[3] = self.triangles[1].get_other_point( self.pts ).coords()
        (dx0, dy0) = ( quad[2][0]-quad[0][0], quad[2][1]-quad[0][1] )
        (dx1, dy1) = ( quad[3][0]-quad[1][0], quad[3][1]-quad[1][1] )
        if (dx0*dx0+dy0*dy0 <= dx1*dx1+dy1*dy1): return False
        # Are both quad[0] and quad[2] on the same side of the line quad[3]-quad[1]? If so, concave :-(
        if ( ( dy1*(quad[0][0]-quad[1][0])-dx1*(quad[0][1]-quad[1][1]) ) *
             ( dy1*(quad[2][0]-quad[1][0])-dx1*(quad[2][1]-quad[1][1]) ) ) > 0: return False
        return True
    #f swap_diagonal
    def swap_diagonal( self, p, verbose=False ):
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
            p.check_consistent()
            print "********************************************************************************"
            print p.__repr__(verbose=True)
            print "********************************************************************************"
            print "Swapping diagonal (A,B) with (X,Y) for line",A,B,X,Y,self
            print "Triangles ",self.triangles[0], self.triangles[1]
        self.pts = ( X, Y )
        self.triangles[0].change_point( B, Y, self.triangles[1] )
        self.triangles[1].change_point( A, X, self.triangles[0] )
        #print "Now", A,B,X,Y,self
        #print "Triangles ",self.triangles[0], self.triangles[1]
        A.remove_from_line( self )
        B.remove_from_line( self )
        X.add_to_line( self, Y, 0 )
        Y.add_to_line( self, X, 1 )
        #print "********************************************************************************"
        #print p.__repr__(verbose=True)
        #print "********************************************************************************"
        #p.check_consistent()
        pass
    def __repr__( self ):
        tris = "(X,X)"
        if self.triangles[1] is not None: tris="(%d,%d)"%(self.triangles[0].triangle_num,self.triangles[1].triangle_num)
        elif self.triangles[0] is not None: tris="(%d,X)"%(self.triangles[0].triangle_num)
        return "line(%d:%d:%d:%d:%s)"%(self.line_num,self.on_contour,self.pts[0].entry_number,self.pts[1].entry_number,tris)

#c c_polygon_triangle
class c_polygon_triangle( object ):
    triangle_log = []
    #f __init__
    def __init__( self, pts ):
        """
        To create a triangle, the lines between the points must have already been created so that the points are connected
        """
        self.triangle_num = len(self.triangle_log)
        self.triangle_log.append(self)
        self.pts = list(pts)
        pts[0].add_to_triangle( self )
        pts[1].add_to_triangle( self )
        pts[2].add_to_triangle( self )
        pts[0].find_line_segment_to( pts[1] ).add_triangle( self )
        pts[1].find_line_segment_to( pts[2] ).add_triangle( self )
        pts[2].find_line_segment_to( pts[0] ).add_triangle( self )
        pass
    #f check_consistent
    def check_consistent( self ):
        for l in self.find_lines(mesh_only=True):
            if self not in l.triangles:
                raise Exception("Failed to find %s in %s"%(str(self),str(l)))
            pass
        pass
    #f find_lines
    def find_lines( self, mesh_only=False ):
        lines = []
        for i in range(3):
            pt = self.pts[i]
            for j in range(1,3):
                l = pt.find_line_segment_to(self.pts[(i+j)%3], mesh_only)
                if l not in lines:
                    lines.append(l)
                    pass
                pass
            pass
        return lines
    #f change_point
    def change_point( self, pt_from, pt_to, other_triangle ):
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
        die_horribly
        pass
    #f get_other_point
    def get_other_point( self, pts ):
        for p in self.pts:
            if p not in pts: return p
            pass
        return None
    #f get_points
    def get_points( self ):
        return self.pts
    #f __repr__
    def __repr__( self ):
        return "tri(%d:%d,%d,%d)"%(self.triangle_num,self.pts[0].entry_number,self.pts[1].entry_number,self.pts[2].entry_number)

#c c_polygon
class c_polygon( object ):
    """
    A polygon is a set of line segments, each of which has two points
    """
    #f __init__
    def __init__( self ):
        self.reset()
        pass
    #f reset
    def reset( self ):
        self.line_segments = []
        self.triangles = []
        self.point_set = []
        self.contour = []
        pass
    #f check_consistent
    def check_consistent( self ):
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
    def add_point( self, point ):
        """
        Add an external representation of a point to our set, and return that object
        If the point is already in our set, return that object
        Keep the point set ordered by coords
        """
        (ins, match) = self.find_insertion_index( self.point_set, point, lambda s,e:s.compare_with(e) )
        if match: return self.point_set[ins]
        new_point = c_polygon_point( point )
        self.point_set.insert( ins, new_point )
        return new_point
    #f add_line
    def add_line( self, pt0, pt1, on_contour=False ):
        line = c_polygon_line(pt0,pt1,on_contour)
        self.line_segments.append( line )
        return line
    #f find_or_create_line
    def find_or_create_line( self, pt0, pt1, on_contour=False ):
        line = pt0.find_line_segment_to(pt1)
        if line is not None: return line
        return self.add_line( pt0, pt1, on_contour )
    #f add_triangle_from_points
    def add_triangle_from_points( self, pts ):
        """
        Must add a triangle from points to ensure that the winding order is passed in cleanly
        """
        self.find_or_create_line( pts[0], pts[1] )
        self.find_or_create_line( pts[1], pts[2] )
        self.find_or_create_line( pts[2], pts[0] )
        triangle = c_polygon_triangle( pts )
        self.triangles.append(triangle)
        return triangle
    #f from_points
    def from_points( self, points ):
        """
        points is a list of c_points

        Must create the set of c_polygon_point, and the line segments that use them
        The points list can then be sorted to start with the smallest X point (with smallest Y on ties)

        Once sorted, one can reorder the line segments to start at that smallest X point.
        This is a normalized polygon
        """
        self.line_segments = []
        p0 = points[-1]
        for i in range(len(points)):
            p1 = points[i]
            self.add_line( p0, p1, True )
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
                self.line_segments.pop((i+1)%l)
                if (i+1==l): i-= 2
                l -= 1
                pass
            else:
                i -= 1
                pass
            pass
        pass
    #f fill_with_triangles
    def fill_with_triangles( self ):
        """
        Starting with a normalized polygon, we can generate filled triangles

        A normalized polygon has a sorted set of points and a list of line segments starting at any point without any consecutive parallel line segments
        Since we can guarantee that no consecutive line segments are parallel, two consecutive line segments must form a non-zero area triangle

        So, if we find the top-most of the left-most points, and the line segments starting there, we can guarantee that the triangle with those line segments is in the convex hull.
        Note that it _MAY_ overlap with another line segment (i.e. some other point in the point set may lie within this triangle)
        ... argh
        Find all points within the triangle

        """
        first_segment = self.find_first_segment()
        if first_segment is None:
            die_horribly
            pass

        lines_to_do = self.line_segments[first_segment:]
        lines_to_do.extend(self.line_segments[:first_segment])
        
        pass
    #f fill_convex_hull_with_triangles
    def fill_convex_hull_with_triangles( self ):
        """
        Starting with a normalized polygon, we can generate filled triangles

        A normalized polygon has a sorted set of points and a list of line segments starting at any point without any consecutive parallel line segments
        Since we can guarantee that no consecutive line segments are parallel, two consecutive line segments must form a non-zero area triangle

        Sort all points after the 'first point (x0,y0) (left-most, top-most)' by angle to y=y0 (-90,+90).
        The sweep all points creating triangles from (x0,y0) to (xn,yn), (xn+1,yn+1) in the swept order
        """
        radial_order = []
        (x0,y0) = self.point_set[0].coords()
        for pt in self.point_set[1:]:
            if not pt.used_in_lines(): continue
            (x,y) = pt.coords()
            (dx,dy) = (x-x0,y-y0)
            (ins, match) = self.find_insertion_index( radial_order, (dx,dy), lambda s,e:s[0]*e[1]-s[1]*e[0] )
            radial_order.insert( ins, (dx, dy, pt) )
            pass
        radial_order.insert(0,(0,0,self.point_set[0]))
        num_points_used = len(radial_order)
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

        # Now ensure that the actual lines forming the polygon are in the set of lines
        # tricky
        pass
    #f shorten_quad_diagonals
    def shorten_quad_diagonals( self, verbose=False ):
        """
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
        return work_done

    #f __repr__
    def __repr__( self, verbose=False ):
        result =  "polygon\n"
        result += "  pts: %s\n"%(str(self.point_set))
        result += "  lns: %s\n"%(str(self.line_segments))
        result += "  tris: %s\n"%(str(self.triangles))
        if verbose:
            result = result.replace(", ",",\n        ")
        return result
#c Polygon pygame test
def polygon_test_get_draw_fn():
    x = c_polygon()
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

#c mesh_test_get_draw_fn
def mesh_test_get_draw_fn():
    x = mesh.c_mesh()
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
    font_dir = "../../fonts/"
    fontname = "beneg___"
    #fontname = "SF Old Republic SC Bold"
    glyphname = "ampersand"
    glyphname = "dollar"
    glyphname = "A"
    glyphname = "C"
    glyphname = "m"
    #glyphname = "A"
    #glyphname = "N"
    #glyphname = "F"
    #glyphname = "P"
    font.c_font.convert_ttf_to_ttx( font_dir+fontname+".ttf", font_dir+"a.ttx" )
    f = font.c_font("benegraphic").load_from_ttx( font_dir+"a.ttx")
    contours = f.create_bezier_lists( glyphname )
    x = f.get_mesh( glyphname, straightness=50 )
    bbox = f.get_bbox(glyphname )
    pygame.font.init()
    pyfont = pygame.font.SysFont(u'palatino',10)
    #pyfont=None
    def draw_fn( screen ):
        size = 800.0
        scale = size/bbox[2]
        if 100.0/bbox[3]<scale: scale=size/bbox[3]
        scale = ( scale, -scale )
        offset=( 0, size)
        draw_triangles( screen, x.triangles, scale=scale, offset=offset, font=pyfont )
        draw_contour( screen, x, scale=scale, offset=offset )
    return draw_fn

#a Bezier test
def bezier_test_get_draw_fn():
    f = font.c_font("benegraphic").load_from_ttx("/Users/gstark_old/a.ttx")
    print f.glyphs

    beziers = []
    def create_bezier_lists( glyph ):
        bezier_lists = []
        for c in glyph.glyph["contours"]:
            beziers = []
            i = 0
            p0 = c0 = p1 = None
            while i<len(c):
                (p0,c0,p1) = (c0,p1,bezier.c_point(coords=c[i]))
                if ((i&1)==0) and p0 is not None:
                    beziers.append( bezier.c_bezier2( pts=(p0,c0,p1) ) )
                    pass
                i += 1
                pass
            bezier_lists.append(beziers)
            pass
        return bezier_lists

    def create_polygons( bezier_lists, straightness=10 ):
        polygons = []
        for bl in bezier_lists:
            line_segments = []
            for b in bl:
                subbeziers = b.break_into_segments(straightness)
                for s in subbeziers:
                    line_segments.append( s.pts[0] )
                    pass
                line_segments.append( s.pts[2] )
                pass
            polygons.append(line_segments)
            pass
        return polygons

    bezier_lists = create_bezier_lists( f.glyphs["ampersand"] )
    polygons = create_polygons( bezier_lists )

    split_beziers = []
    for bl in bezier_lists:
        for b in bl:
            split_beziers.extend(b.break_into_segments(100))
            pass
        pass
    pass
    def draw_fn( screen ):
        draw_world( screen, bezier_lists )
        #draw_world( screen, (split_beziers,) )
        draw_polygons( screen, polygons )
    return draw_fn

#a Drawing functions
#c c_screen
class c_screen( object ):
    def __init__( self, screen ):
        self.screen = screen
        pass
    def draw_line( self, x0, y0, x1, y1, color ):
        draw_line( self.screen, x0, y0, x1, y1, color )
        pass
    def draw_dot( self, x, y, color ):
        draw_dot( self.screen, x, y, color )
        pass
    def fill_polygon( self, points_list, color ):
        pygame.draw.polygon(self.screen, color, points_list )
        pass
    def blit( self, surface, coords ):
        self.screen.blit( surface, coords )
        pass

#f draw_dot
def draw_dot( screen, x, y, color ):
    screen.fill(color, rect=(x,y,1,1) )

#f draw_line
def draw_line( screen, x0, y0, x1, y1, color ):
    if (x0>x1): return draw_line( screen, x1, y1, x0, y0, color )
    dx = x1-x0
    dy = y1-y0
    if (dy>0) and (dx>=dy):  return draw_line_by_dx( screen, x0, y0, dx, dy, +1, color )
    if (dy<=0) and (dx>=-dy): return draw_line_by_dx( screen, x0, y0, dx, -dy, -1, color )
    if (dy<0): (x0,y0,x1,y1) = (x1,y1,x0,y0)
    dx = x1-x0
    dy = y1-y0
    if (dx>0):
        return draw_line_by_dy( screen, x0, y0, dx, dy, +1, color )
    return draw_line_by_dy( screen, x0, y0, -dx, dy, -1, color )

#f draw_line_by_dx
def draw_line_by_dx( screen, x, y, dx, dy, pdy, color ):
    """Called if dx>=dy"""
    px = int(x)
    py = int(y)
    error = -(dx/2)
    for i in range(int(dx)):
        draw_dot(screen,px,py,color)
        px = px+1
        error = error + dy
        if error>0:
            py=py+pdy
            error = error-dx
            pass
        pass
    pass

#f draw_line_by_dy
def draw_line_by_dy( screen, x, y, dx, dy, pdx, color ):
    """Called if dy>dx"""
    px = int(x)
    py = int(y)
    error = -(dy/2)
    for i in range(int(dy)):
        draw_dot(screen,px,py,color)
        py = py+1
        error = error + dx
        if error>0:
            px=px+pdx
            error = error-dy
            pass
        pass
    pass

#f draw_world
def draw_world(screen, object_lists):
    screen.draw_line( 0,0, 100,100, (128,128,128,255) )
    screen.draw_line( 200,150, 100,100, (128,128,128,255) )
    screen.draw_line( 200,150, 300,600, (128,128,128,255) )
    for ol in object_lists:
        for o in ol:
            screen.draw_line( o.pts[0].coords[0],1000-o.pts[0].coords[1],
                       o.pts[2].coords[0], 1000-o.pts[2].coords[1], (o.s*50,255,255,255) )
            pass
        pass
    pass

#f draw_polygons
def draw_polygons(screen, polygons):
    for poly in polygons[0],:
        last_pt = poly[-1]
        last_pt = None
        for pt in poly:
            if last_pt is not None:
                screen.draw_line( last_pt.coords[0],last_pt.coords[1],
                                  pt.coords[0], pt.coords[1], (255,128,128,255) )
            last_pt = pt
            pass
        points_list = []
        for pt in poly:
            points_list.append( (pt.coords[0], pt.coords[1]) )
            pass
        screen.fill_polygon( points_list, (128,255,128,255) )
        pass
    pass

#f draw_triangles
def draw_triangles(screen, triangles, scale=(1,1), offset=(0,0), font=None):
    i = 0
    num = len(triangles)
    text_list = []
    for t in triangles:
        points_list = []
        brightness = 100
        if t.winding_order is not None and t.winding_order>0: brightness=255
        centre = [0,0]
        for pt in t.get_points():
            c = pt.coords()
            (x,y) = (c[0]*scale[0]+offset[0], c[1]*scale[1]+offset[1])            
            centre[0] += x/3.0
            centre[1] += y/3.0
            points_list.append( (x,y) )
            pass
        screen.fill_polygon( points_list, (brightness*i/num,brightness-brightness*i/num,brightness,255) )
        if font is not None:
            text_list.append( (centre, str(t.triangle_num)) )
            pass
        i+=1
        pass
    for (centre, text) in text_list:
        p = font.render(text,False,(255,255,255))
        screen.blit(p,centre)
        pass
    pass

#f draw_contour
def draw_contour(screen, polygon, scale=(1,1), offset=(0,0)):
    i = 0
    for l in polygon.line_segments:
        #if not l.on_contour: continue
        coords = []
        for pt in l.get_points():
            c = pt.coords()
            coords.append( c[0]*scale[0]+offset[0] )
            coords.append( c[1]*scale[1]+offset[1] )
            pass
        screen.draw_line( coords[0], coords[1], coords[2], coords[3], (64,255,64,255) )
    pass

#a Toplevel
(w,h) = (1000,1000)
max_straightness = 2

screen = pygame.display.set_mode((w,h),pygame.DOUBLEBUF|pygame.HWSURFACE)
my_screen = c_screen(screen)

#draw_fn = bezier_test_get_draw_fn()
#draw_fn = polygon_test_get_draw_fn()
draw_fn = mesh_test_get_draw_fn()
def loop():
    alive = True
    while alive:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit();
                pass
            pass

        draw_fn( my_screen )

        pygame.display.flip()
        msElapsed = clock.tick(15)
        pass
    pass

clock = pygame.time.Clock()
loop()
a.ttLib
