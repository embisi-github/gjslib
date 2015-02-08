#!/usr/bin/env python
#a Documentation
r"""
Bezier curve and patch classes
----------------------------------------

Consider the equation

:math:`p(t,A,B) = (1-t)*A + t*B`

This provides for a linear interpolation as t varies from 0 to 1 of
the values A and B. In particular :math:`p(0,A,B)=A`, :math:`p(1,A,B)=B`,
:math:`p(\frac{1}{2},A,B)=\frac{A+B}{2}`

This equation is wonderful for providing, for example, the points on a
straight line between two *vectors* A and B:
:math:`\mathbf{p} (t,\mathbf{A},\mathbf{B}) = (1-t) * \mathbf{A} + t * \mathbf{B}`

Now consider the equation

:math:`q(t,A,B,C) = (1-t)*p(t,A,B) + t*p(t,B,C)`

This is effectively interpolating between a first 'value' between A and
B, and a second 'value' betwen B and C. Here, similar to p,
:math:`Q(0,A,B,C)=A` and :math:`Q(1,A,B,C)=C` - which means that the
interpolation starts at the 'left' (or A) and ends at the 'right' (or
B) as t goes from 0 to 1.

If we expand out the equation for 'p' in 'q', we get:

.. math::
 \begin{align}
 q(t,A,B,C) &= (1-t)*p(t,A,B) + t*p(t,B,C) \\
 &= (1-t)(1-t)A + t(1-t)tB + t(1-t)B + t*t*C \\
 &= (1-t)^2A + 2t(1-t)B + t^2C
 \end{align}
"""
__docformat__ = "restructuredtext"

#a Imports
import math


#a Variable
verbose = True
verbose = False

#a Point class
#c c_point
class c_point( object ):
    #f __init__
    def __init__( self, coords ):
        self.set_coords(coords)
        #print "Creating point at",self.coords,self
        pass
    #f set_coords
    def set_coords( self, coords ):
        cs = []
        for c in coords:
            cs.append(c+0.0)
            pass
        self.coords = tuple(cs)
        pass
    #f perturb
    def perturb( self, quantum ):
        cs = []
        for c in self.coords:
            cs.append(c)
            pass
        cs[0] += quantum+cs[1]*quantum
        cs[1] += quantum-cs[0]*quantum
        self.coords = tuple(cs)
        pass
    #f get_coords
    def get_coords( self, scale=(1.0,), offset=(0.0,) ):
        cs = []
        i = 0
        ls = len(scale)
        lo = len(offset)
        for c in self.coords:
            cs.append(c*scale[i%ls]+offset[i%lo])  
            i += 1
            pass
        return cs
    #f length
    def length( self ):
        c = 0
        for i in range(len(self.coords)):
            d = self.coords[i]
            c += d*d
            pass
        return math.sqrt(c)
    #f scale
    def scale( self, factor ):
        c = []
        for i in range(len(self.coords)):
            c.append( self.coords[i] * factor )
            pass
        return c_point( c )
    #f is_parallel_to
    def is_parallel_to( self, other ):
        return (self.coords[1]*other.coords[0]-self.coords[0]*other.coords[1])==0
    #f add
    def add( self, other, factor=1 ):
        c = []
        for i in range(len(self.coords)):
            c.append( self.coords[i]+factor*other.coords[i] )
            pass
        return c_point( c )
    #f distance
    def distance( self, other ):
        c = 0
        for i in range(len(self.coords)):
            d = self.coords[i]-other.coords[i]
            c += d*d
            pass
        return math.sqrt(c)
    #f normal
    def normal( self ):
        return c_point( coords=(-self.coords[1], self.coords[0]) )
    #f scalar_product
    def scalar_product( self, other ):
        c = 0
        for i in range(len(self.coords)):
            c += self.coords[i]*other.coords[i]
            pass
        return c
    #f cross_product
    def cross_product( self, other ):
        c = []
        for i in range(3):
            c.append( self.coords[(i+1)%3]*other.coords[(i+2)%3] -
                      other.coords[(i+1)%3]*self.coords[(i+2)%3] )
            pass
        if verbose:
            print "result",c
        return c_point(c)
    #f __repr__
    def __repr__( self ):
        result = "("
        for c in self.coords:
            result += "%6.4f "%c
        result += ")"
        return result

#a Bezier classes
#c c_bezier2
class c_bezier2( object ):
    """
    A quadratic bezier curve class

    Here a point is defined by p(t) = (1-t)^2 * p0 + 2t(1-t) * c0 + t^2 * p1
    If we subdivide, we need p(0)=p0, p(1/2)=p0/4 + c0/2 + p1/4, and p(1)=p1
    And we need new control points

    We will end up with a q(u) (0<=u<=1) where q(u)=p(u/2) - this is the first half of the subdivide
    Now if we express q(u) as (1-u)^2 * p0 + 2u(1-u) * C0 + u^2 * (p0/4 + c0/2 + p1/4)
    q(0) = p0; q(1) = p0/4 + c0/2 + p1/4 ; q(1/2) = p0/4 + C0/2 + p0/16 + c0/8 + p1/16
    Note that p(1/4) should be the same as q(1/2), and p(1/4) = 9/16*p0 + 6/16*c0 + 1/16*p1
    So we can deduce that C0 = 8/16*p0 + 8/16*c0 = p0/2 + c0/2

    For the second half of the subdivide we have r(u)
    Now if we express r(u) as (1-u)^2 * (p0/4 + c0/2 + p1/4) + 2u(1-u) * C1 + u^2 * p1
    r(0) = p0/4 + c0/2 + p1/4 ; r(1) = p1; r(1/2) = p0/16 + c0/8 + p1/16 + C1/2 + p1/4
    Note that p(3/4) should be the same as q(1/2), and p(3/4) = 1/16*p0 + 6/16*c0 + 9/16*p1
    So we can deduce that C1 = 8/16*c0 + 8/16*p1 = c0/2 + p1/2
    """
    n = 100
    fmt = "%6.2f"
    def __init__( self, pts=None, color=(255,255,255,255), s=0, split_parent=None, first_split=True ):
        self.s = s
        self.color = color
        if split_parent is None:
            self.pts = pts
            return
        (p0, c0, p1) = split_parent.pts
        if first_split:
            self.s = split_parent.s+1
            self.pts = (p0,
                        p0.scale(0.5).add( c0, factor=0.5 ),
                        p0.scale(0.25).add(c0,factor=0.5).add(p1,factor=0.25) )
        else:
            self.s = split_parent.s+1
            self.pts = (p1.scale(0.25).add(c0,factor=0.5).add(p0,factor=0.25),
                        p1.scale(0.5).add( c0, factor=0.5 ),
                        p1 )
        pass
    def straight_enough( self, v ):
        p10n = self.pts[-1].add(self.pts[0],factor=-1).normal()
        len_p10n = p10n.length()
        v_len_p10n = v*len_p10n
        c0p10n = p10n.scalar_product(self.pts[1].add(self.pts[0],factor=-1))
        #print c0p10n, v_len_p10n, p10n
        if c0p10n*c0p10n>v_len_p10n: return False
        return True
    def break_into_segments( self, straightness ):
        lines = [self]
        i = 0
        while i<len(lines):
            if not lines[i].straight_enough(straightness):
                l = lines.pop(i)
                lines.insert(i,c_bezier2(color=self.color,split_parent=l,first_split=False))
                lines.insert(i,c_bezier2(color=self.color,split_parent=l,first_split=True))
                pass
            else:
                i+=1
                pass
            pass
        return lines
    def __repr__(self ):
        return "bezier2(%s %s %s)"%(str(self.pts[0]),str(self.pts[1]),str(self.pts[2]),)
    pass

#c c_bezier
class c_bezier( object ):
    n = 100
    fmt = "%6.2f"
    def __init__( self, p0, p1, c0, c1, color=(255,255,255,255), s=0, split_parent=None, first_split=True ):
        self.s = s
        self.color = color
        if split_parent is None:
            self.pts = (p0, c0, c1, p1)
            self.pts = ( (p0[0],p0[1]),
                         (p0[0]+c0[0],p0[1]+c0[1]),
                         (p1[0]-c1[0],p1[1]-c1[1]),
                         (p1[0],p1[1]),
                         )
            return
        (p0, c0, c1, p1) = split_parent.pts
        if first_split:
            self.s = split_parent.s+1
            self.pts = ( (p0[0],p0[1]),
                         ( 1/2.0*( p0[0]+c0[0] ),
                           1/2.0*( p0[1]+c0[1] ) ),
                         ( 1/4.0*( p0[0]+2*c0[0]+c1[0] ),
                           1/4.0*( p0[1]+2*c0[1]+c1[1] ) ),
                         ( 1/8.0*( p0[0]+3*c0[0]+3*c1[0]+p1[0] ),
                           1/8.0*( p0[1]+3*c0[1]+3*c1[1]+p1[1] ) ),
                         )
        else:
            self.s = split_parent.s+1
            self.pts = ( ( 1/8.0*( p0[0]+3*c0[0]+3*c1[0]+p1[0] ),
                           1/8.0*( p0[1]+3*c0[1]+3*c1[1]+p1[1] ) ),
                         ( 1/4.0*( p1[0]+2*c1[0]+c0[0] ),
                           1/4.0*( p1[1]+2*c1[1]+c0[1] ) ),
                         ( 1/2.0*( p1[0]+c1[0] ),
                           1/2.0*( p1[1]+c1[1] ) ),
                         (p1[0],p1[1]),
                         )
        pass
    def coord( self, t ):
        u = 1-t
        x = ( self.pts[0][0]*u*u*u   + 3*self.pts[1][0]*t*u*u +
              3*self.pts[2][0]*t*t*u + self.pts[3][0]*t*t*t )
        y = ( self.pts[0][1]*u*u*u   + 3*self.pts[1][1]*t*u*u +
              3*self.pts[2][1]*t*t*u + self.pts[3][1]*t*t*t )
        return (x,y)
    def draw( self, screen ):
        for t in range(self.n):
            (x,y) = self.coord( t/(self.n+0.0) )
            screen.draw_dot( int(x), int(y), self.color )
            pass
        pass
    def draw( self, screen ):
        screen.draw_line( self.pts[0][0], self.pts[0][1], self.pts[3][0], self.pts[3][1], self.color )
        pass
    def straightness( self ):
        p10n = (self.pts[3][1]-self.pts[0][1], self.pts[0][0]-self.pts[3][0])
        c0p10n = (self.pts[1][0]-self.pts[0][0])*p10n[0] + (self.pts[1][1]-self.pts[0][1])*p10n[1]
        c1p10n = (self.pts[2][0]-self.pts[3][0])*p10n[0] + (self.pts[2][1]-self.pts[3][1])*p10n[1]
        max = c0p10n
        if (max<0): max=-max
        if (c1p10n<0) and (-c1p10n>max): max=c1p10n
        if (c1p10n>max): max=c1p10n
        len_p10n = p10n[0]*p10n[0] + p10n[1]*p10n[1]
        print c0p10n, c1p10n, len_p10n, max*max, (max*max)*10/len_p10n
        return (max*max)/len_p10n
    def straight_enough( self, v ):
        p10n = (self.pts[3][1]-self.pts[0][1], self.pts[0][0]-self.pts[3][0])
        len_p10n = p10n[0]*p10n[0] + p10n[1]*p10n[1]
        v_len_p10n = v*len_p10n
        c0p10n = (self.pts[1][0]-self.pts[0][0])*p10n[0] + (self.pts[1][1]-self.pts[0][1])*p10n[1]
        if c0p10n*c0p10n>v_len_p10n: return False
        c1p10n = (self.pts[2][0]-self.pts[3][0])*p10n[0] + (self.pts[2][1]-self.pts[3][1])*p10n[1]
        if c1p10n*c1p10n>v_len_p10n: return False
        return True
    def split( self ):
        return ( c_bezier( 0,0,0,0, color=(255,255,0,255), split_parent=self, first_split=True ),
                 c_bezier( 0,0,0,0, color=(255,0,255,255), split_parent=self, first_split=False ) )
    pass

#c c_bezier_patch
class c_bezier_patch( object ):
    factors = [ 1.0, 3.0, 3.0, 1.0,
                3.0, 9.0, 9.0, 3.0,
                3.0, 9.0, 9.0, 3.0,
                1.0, 3.0, 3.0, 1.0 ]
    def __init__( self, pts ):
        self.pts = pts
        pass
    def bezier_gradient( self, ofs=0, stride=1, t=0 ):
        tis = [ -3*(1-t)*(1-t), 3*(1-t)*(1-3*t), 3*(2-3*t)*t, 3*t*t ]
        pt = self.pts[0].add( -1.0, self.pts[0] )
        for i in range(4):
            pt = pt.add( tis[i], self.pts[ofs+i*stride] )
            #print i, t, tis[i], pt, ofs+i*stride, self.pts[ofs+i*stride]
            pass
        return pt
    def normal( self, t, u ):
        tis = [ (1-t)*(1-t)*(1-t), 3*(1-t)*(1-t)*t, 3*(1-t)*t*t, t*t*t ]
        uis = [ (1-u)*(1-u)*(1-u), 3*(1-u)*(1-u)*u, 3*(1-u)*u*u, u*u*u ]
        dt_vec = self.pts[0].add(-1.0,self.pts[0])
        du_vec = self.pts[0].add(-1.0,self.pts[0])
        for i in range(4):
            dt_vec = dt_vec.add( uis[i], self.bezier_gradient( ofs=4*i, stride=1, t=t ) )
            du_vec = du_vec.add( tis[i], self.bezier_gradient( ofs=i,   stride=4, t=u ) )
            pass
        #print t, u, dt_vec, du_vec
        return dt_vec.cross_product( du_vec )
    def coord( self, t, u ):
        pt = self.pts[0]
        pt = pt.add( -1.0, pt )
        tis = [ (1-t)*(1-t)*(1-t), (1-t)*(1-t)*t, (1-t)*t*t, t*t*t ]
        uis = [ (1-u)*(1-u)*(1-u), (1-u)*(1-u)*u, (1-u)*u*u, u*u*u ]
        for i in range(4):
            for j in range(4):
                pt = pt.add( self.factors[i+4*j]*tis[i]*uis[j], self.pts[i+4*j] )
                pass
            pass
        return pt

#a Tests
#f test_bezier
def test_bezier():
    epsilon = 0.001
    patches = { "flat_xy_square": ( (0,0,0),     (1/3.0,0,0),     (2/3.0,0,0),   (1,0,0),
                                    (0,1/3.0,0), (1/3.0,1/3.0,0), (2/3.0,1/3.0,0), (1,1/3.0,0),
                                    (0,2/3.0,0), (1/3.0,2/3.0,0), (2/3.0,2/3.0,0), (1,2/3.0,0),
                                    (0,1,0),     (1/3.0,1,0),     (2/3.0,1,0),     (1,1,0),
                                    ),
                "bump_one": ( (0,0,0),   (0.1,0,1),   (0.9,0,1),   (1,0,0),
                              (0,0.1,1), (0.1,0.1,1), (0.9,0.1,1), (1,0.1,1),
                              (0,0.9,1), (0.1,0.9,1), (0.9,0.9,1), (1,0.9,1),
                              (0,1,0),   (0.1,1,1),   (0.9,1,1),   (1,1,0),
                                    )
                }
    test_pts = {"flat_xy_square": ( (0.0,0.0,(0,0,0)),
                                    (1.0,0.0,(1,0,0)),
                                    (1.0,1.0,(1,1,0)),
                                    (0.0,1.0,(0,1,0)),
                                    (0.5,0.5,(0.5,0.5,0)),
                                    (0.1,0,(0.1,0,0)),
                                    (0.2,0,(0.2,0,0)),
                                    (0.1,1.0,(0.1,1.0,0)),
                                    (0.2,1.0,(0.2,1.0,0)),
                                    (0.5,0,(0.5,0.0,0)),
                                    (0.5,0.1,(0.5,0.1,0)),
                                    (0.3,0.4,(0.3,0.4,0)),
                                     ),
                "bump_one": ( (0.0,0.0,(0,0,0)),
                              (0.01,0.0,(0.0032,0,0.0297)),
                              (1.0,1.0,(1,1,0)),
                              )
                 }
    test_normals = {"flat_xy_square": ( (0.0,0.0,(0,0,1.0)),
                                        (0.3,0.2,(0,0,1.0)),
                                        (1.0,1.0,(0,0,1.0)),
                                     ),
                    "bump_one": ( (0.0,0.0,(-1,-1,0.1),),
                                  (0.5,0.5,(0,0,1),),
                                  ),
                 }

    for p in patches.keys():
        patch = patches[p]
        pts = []
        for coords in patch: pts.append( c_point(coords=coords) )
        bp = c_bezier_patch( pts=pts )
        for (t,u,tp) in test_pts[p]:
            dut = bp.coord(t=t,u=u)
            r = c_point(coords=tp)
            d = dut.distance(r)
            if (d>epsilon):
                print "Bezier fail",p,t,u,dut,r,d
            pass
        for (t,u,tp) in test_normals[p]:
            dut = bp.normal(t=t,u=u)
            r = c_point(coords=tp)
            cp = r.cross_product(dut)
            d = cp.length()
            if (d>epsilon):
                print "Bezier normal fail",p,t,u,dut,r,d
            pass
        pass
    pass

def test_cross_product():
    vectors = { "zero":(0,0,0),
                "x":(1,0,0),    "y":(0,1,0), "z":(0,0,1),
                "-x":(-1,0,0), "-y":(0,-1,0), "-z":(0,0,-1),
                "xyz":(1,1,1),
                "-yz":(0,-1,1),
                "-y-z":(0,-1,-1),
                "x-z":(1,0,-1),
                "-xy":(-1,1,0),
                }
    tests = ( ("zero","x","zero"),("zero","y","zero"),("zero","z","zero"),
              ("zero","-x","zero"),("zero","-y","zero"),("zero","-z","zero"),
              ("x","y","z"), ("y","z","x"), ("z","x","y"),
              ("y","x","-z"), ("z","y","-x"), ("x","z","-y"),
              ("x","xyz","-yz"), ("x","-yz","-y-z"),
              ("y","xyz","x-z"), ("z","xyz","-xy"),
              )
    epsilon = 0.000001
    pts = {}
    for (k,v) in vectors.iteritems():
        pts[k] = c_point( coords=v )
        pass
    for (a,b,r) in tests:
        dut = pts[a].cross_product(pts[b])
        d = dut.distance(pts[r])
        if (d>epsilon):
            print "Test failed (a x b)",a,b,r
            print pts[a], pts[b], dut, pts[r], d
            pass
        pass
    # Try b x 2a = -2r
    for (a,b,r) in tests:
        p = pts[a].add(1.0,pts[a])
        dut = pts[b].cross_product(p)
        minus_r = pts[b].add(-1.0,pts[b]).add(-2.0,pts[r])
        d = dut.distance(minus_r)
        if (d>epsilon):
            print "Test failed (b x 2a)",b,a,minus_r
            print pts[a], pts[b], dut, minus_r, d
            pass
        pass
    # Note that if a x b1 = r1
    # And a x b2 = r2
    # Then a x (b1+b2) = (r1+r2)
    for (a,b1,r1) in tests:
        for (ap, b2, r2) in tests:
            if (a==ap):
                b1b2 = pts[b1].add(1.0,pts[b2])
                dut = pts[a].cross_product(b1b2)
                r1r2 = pts[r1].add(1.0,pts[r2])
                d = dut.distance(r1r2)
                if (d>epsilon):
                    print "Test failed (a x (b1+b2))",a,b1,b2,r1,r2
                    print pts[a], b1b2, dut, r1r2, d
                    pass
                pass
            pass
        pass

def main():
    test_bezier()
    #test_cross_product()

if __name__ == '__main__': main()
