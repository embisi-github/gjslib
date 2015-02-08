#!/usr/bin/env python
import math

class c_quad_complex( object ):
    d_fmt = "%7.5f"
    epsilon = 1E-10
    fmt = "e^(%s+%si+%sj+%sk)"%(d_fmt,d_fmt,d_fmt,d_fmt)
    def __init__( self, r=1.0, i=0, j=0, k=0, rijk=None ):
        if rijk is not None: (r,i,j,k)=rijk
        self.r = r+0.0
        self.i = i+0.0
        self.j = j+0.0
        self.k = k+0.0
        pass
    def copy( self ):
        return self.__class__( r=self.r, i=self.i, j=self.j, k=self.k )
    def to_abcd( self ):
        l = math.sqrt( self.i**2 + self.j**2 + self.k**2 )
        if l<self.epsilon: return (self.r,0.0,0.0,0.0)
        cl = math.cos(l)
        ersldl = math.exp(self.r)*math.sin(l)/l
        return ( math.exp(self.r)*cl, self.i*ersldl, self.j*ersldl, self.k*ersldl )
    def from_abcd( self, a=0.0, b=0.0, c=0.0, d=0.0, abcd=None ):
        """
        a = e^r.cos(L)
        b = i/L.e^r.sin(L)
        c = j/L.e^r.sin(L)
        d = k/L.e^r.sin(L)
        (L = sqrt(i^2+j^2+k^2))
        b^2+c^2+d^2 = (e^r.sin(L)/L)^2 . (i^2+j^2+k^2) = (e^r.sin(L))^2 . L^2/L^2
        => e^r.sin(L) = sqrt(b^2+c^2+d^2)
        e^2r = e^2r.sin(L)^2 + e^2r.cos(L)^2
        L = math.atan2( rsl, a )
        
        """
        if abcd is not None: (a,b,c,d) = abcd
        ersl = math.sqrt( b**2 + c**2 + d**2 )
        L = math.atan2( ersl, a )
        if ersl<self.epsilon:
            (self.r, self.i, self.j, self.k) = (0.0,0.0,0.0,0.0)
            return self
        self.r = math.log(ersl**2 + a**2)/2.0
        ersldl = ersl / L
        (self.i, self.j, self.k) = (b/ersldl, c/ersldl, d/ersldl )
        return self
    def mult( self, other ):
        self.r += other.r
        self.i += other.i
        self.j += other.j
        self.k += other.k
        return self
    def complement( self ):
        self.r = self.r
        self.i = -self.i
        self.j = -self.j
        self.k = -self.k
        return self
    def power( self, other ):
        r = self.r*other.r - self.i*other.i - self.j*other.j - self.k*other.k
        i = self.r*other.i + self.i*other.r + self.j*other.k - self.k*other.j
        j = self.r*other.j + self.j*other.r + self.k*other.i - self.i*other.k
        k = self.r*other.k + self.k*other.r + self.i*other.j - self.j*other.i
        (self.r, self.i, self.j, self.k) = (r,i,j,k)
        return self
    def normalize( self ):
        L = math.sqrt( self.i**2 + self.j**2 + self.k**2 )
        if L<self.epsilon: return self
        scale = 3.141592653/2.0/L
        self.i *= scale
        self.j *= scale
        self.k *= scale
        return self
    def __repr__( self ):
        return self.fmt % (self.r, self.i, self.j, self.k )

for rijk in [ (0,0,0,0),
              (0,1,0,0),
              (0,0,1,0),
              (0,0,0,1),
              (0,1,1,1),
              (0,1,1,0),
              ]:
    print "\n",rijk
    a = c_quad_complex( rijk=rijk).normalize()
    print a, a.to_abcd()
    b = c_quad_complex()
    b.from_abcd( abcd=a.to_abcd() )
    print b, b.to_abcd()
    c = b.copy().mult(a)
    print c, c.to_abcd()
    d = b.copy().complement()
    print d, d.to_abcd()
    d.mult(b)
    print d, d.to_abcd()
