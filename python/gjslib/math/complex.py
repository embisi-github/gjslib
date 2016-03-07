#!/usr/bin/env python
import math
class c_complex(object):
    def __init__(self, real=None, imaginary=None, cartesian=None, polar=None):
        if real is not None:
            cartesian = (real, 0)
            pass
        if imaginary is not None:
            cartesian = (0,imaginary)
            pass
        if polar is not None:
            self.polar = (float(polar[0]), float(polar[1]))
            self.cartesian = None
            pass
        if cartesian is not None:
            self.cartesian = (float(cartesian[0]), float(cartesian[1]))
            self.polar = None
            pass
        pass
    def copy(self):
        return c_complex(cartesian=self.cartesian, polar=self.polar)
    def add(self, other, scale=1.0):
        self.to_cartesian()
        other.to_cartesian()
        self.cartesian = (self.cartesian[0]+scale*other.cartesian[0], self.cartesian[1]+scale*other.cartesian[1])
        return self
    def multiply(self, other):
        if self.cartesian is not None and other.cartesian is not None:
            (r0,i0) = self.cartesian
            (r1,i1) = other.cartesian
            r = r0*r1 - i0*i1
            i = r0*i1 + r1*i0
            self.cartesian = (r,i)
            return self
        self.to_polar()
        other.to_polar()
        self.polar = (self.polar[0]*other.polar[0], self.polar[1]+other.polar[1])
        return self
    def reciprocal(self):
        self.to_polar()
        self.polar = (1.0/self.polar[0], -self.polar[1])
        return self
    def magnitude(self):
        if self.polar is not None:
            return self.polar[0]
        (r,i) = self.cartesian
        return math.sqrt(r*r+i*i)
    def to_polar(self):
        if self.polar is None:
            (r,i) = self.cartesian
            self.polar = (self.magnitude(), math.atan2(i,r))
            self.cartesian = None
            pass
        return self
    def sqrt(self):
        a = self.copy().to_polar()
        a.polar = (math.sqrt(a.polar[0]), a.polar[1]/2)
        return a
    def pow(self,p):
        a = self.copy().to_polar()
        a.polar = (math.pow(a.polar[0],p), a.polar[1]*p)
        return a
    def to_cartesian(self):
        if self.cartesian is None:
            (r,theta) = self.polar
            self.cartesian = (r*math.cos(theta), r*math.sin(theta))
            self.polar = None
            pass
        return self
    def real(self, epsilon=1E-6):
        self.to_cartesian()
        (r,i) = self.cartesian
        if i<-epsilon or i>epsilon: return None
        return r
    def __repr__(self):
        if self.cartesian is not None:
            return "%6f + %6fi"%self.cartesian
        return "c(%6f, %6f)"%(self.polar[0], 180.0/3.14159265*self.polar[1])
