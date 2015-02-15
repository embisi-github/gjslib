#!/usr/bin/env python
"""
A recurrence relationship is something like:

Xn+2 = 2Xn+1 + 6Xn

The Fibonacci sequence is one of these:

Fn+2 = Fn+1 + Fn

Before looking at these in detail, investigate an equation like:

X(n) = (1+sqrt(x))^n + (1-sqrt(x))^n, for some fixed x and n an integer

First look at (1+a)^n + (1-a)^n...

Let S0 = (1+a)^n = 1  + n.a  + n(n-1)/2.a^2 + ... + n(n-1)/2.a^(n-2) + n.a^(n-1) + a^n
and S1 = (1-a)^n = 1  - n.a  + n(n-1)/2.a^2 + ... - n(n-1)/2.a^(n-2) + n.a^(n-1) - a^n (if n odd)
Adding S0+S1     =2(1 + 0    + n(n-1)/2.a^2 + ... + 0                  n.a^(n-1) + 0 ) (if n odd)
Which means that =2( 1 + k2.a^2 + k4.a^4 + ... ), i.e. a sum of even powers of a
Similarly if n is even, the same result holds - S0+S1 is the sum of even powers of a.

So X(n) = (1+sqrt(x))^n + (1-sqrt(x))^n is the sum of even powers of sqrt(x);
this means that X(n) is the sum of powers of x; so if x is a rational number, then X(n) is rational, despite the sqrts().

A simple example is to set x to be 7:
X(n) = (1+sqrt(7))^n + (1-sqrt(7))^n

Here is a table of values:
n   0    1    2    3    4    5
X   2    2   16   44  184  732

It is interesting to look at the differences between successive Xes:
n   0    1    2    3    4    5
X   2    2   16   44  184  732
dX     0   14   28  140  548
The dX values are X(n) - X(n-1); they seem to be very similar in scale to Xn.
So, what about X(n)-2.X(n-1)?
n   0    1    2    3    4    5
X   2    2   16   44  184  732
dX   -2    12   12   96  264

If we align the dXes differently:
n           0    1    2    3    4    5
X           2    2   16   44  184  732
dX   -2    12   12   96  264

On careful inspecfion we can see that the dX is 6 times the X.
This means that

X(n) - 2X(n-1) - 6X(n-2) = 0 (and we can define R to be X(n) - 2X(n-1) - 6X(n-2))
We can check this easily
n       0     1     2     3     4     5     6     7
Xn-2                2     2    16    44   184   732
Xn-1          2     2    16    44   184   732  2568
6Xn-2              12    12    96   264  1104  4392
2Xn-1         4     4    32    88   376  1464  5136
Xn      2     2    16    44   184   732  2568  9528

So, what happens if we insert the formula for X(n) into the recurrence relation R?
R = (1+sqrt(7))^n + (1-sqrt(7))^n - 2(1+sqrt(7))^(n-1) -2(1-sqrt(7))^(n-1) - 6(1+sqrt(7))^(n-2) -6(1-sqrt(7))^(n-2) 
  = (1+sqrt(7))^(n-2).((1+sqrt(7))^2-2(1+sqrt(7))-6) + (1-sqrt(7))^(n-2).((1-sqrt(7))^2-2(1-sqrt(7))-6)

Looking at ((1+sqrt(7))^2-2(1+sqrt(7))-6):
  ((1+sqrt(7))^2-2(1+sqrt(7))-6) = 1 + 2sqrt(7) + sqrt(7)^2 - 2.1. -2.sqrt(7) - 6
                                 = 1 +7 -2 -6 + (2-2).sqrt(7)
                                 = 0.

So if we knew the recurrence relationship R, may we be able to work out a formula for X(n)?
Let's try for the Fibonaci sequence Fn+2 = Fn+1 + Fn, or Fn+2 - Fn-1 - Fn = 0

Assume to start with that F(n) = A.B^(n); this is 'half' of what we have for X(n), so it is a start to see what we get.
F(n+2) - F(n+1) - F(n) = A.B^(n+2) - A.B^(n+1) - A.B^n
                       = A.B^n( B^2 - B - 1 )
                       = 0 for all n
If A or B are zero then it means F(n) is zero, and we know that is not the case. So, B^2-B-1 must be zero.
    B^2-B-1 = 0
    B = 1/2 +- sqrt(1+4)/2
    B = (1+sqrt(5))/2 or (1-sqrt(5))/2
We have two different values for B (call them B1 and B2)- this is good, as it means that we now have a 'full' version of X(n) above:
F(n) = A1.B1^n + A2.B2^n
     = A1.((1+sqrt(5))/2)^n + A2.((1-sqrt(5))/2)^n
We know that the regular Fibonaci sequence starts with 1, 1, 2, 3, 5, etc.
So we know that F(0)=1 and F(1)=1.
But F(0) = A1 + A2 = 1, and
    F(1) = A1.(1+sqrt(5))/2 + A2.(1-sqrt(5))/2
         = (A1+A2).1/2 + (A1-A2).sqrt(5)/2
         = 1
From this we get:
 1/2 + (A1-A2).sqrt(5)/2 = 1
       (A1-A2).sqrt(5)   = 1
       A1-A2             = sqrt(5)/5   (multiply both sides by sqrt(5)/5)
      2A1                = 1+sqrt(5)/5 (by adding F(0) to both sides)
Hence A1=1/2 + 1/(2sqrt(5)), and A2=1/2 - 1/(2sqrt(5)) (since A1+A2=1)

Hence we believe that the Fibonacci sequence is:
F(n) = (1/2+1/(2sqrt(5))).((1+sqrt(5))/2)^n + (1/2-1/(2sqrt(5))).((1-sqrt(5))/2)^n
     = 1/(2sqrt(5)) . ( (sqrt(5)+1).((1+sqrt(5))/2)^n + (sqrt(5)-1).((1-sqrt(5))/2)^n )
     = 1/sqrt(5) . ( (1+sqrt(5))/2.((1+sqrt(5))/2)^n - (1-sqrt(5))/2.((1-sqrt(5))/2)^n )
     = 1/sqrt(5) . ( ((1+sqrt(5))/2)^(n+1) - ((1-sqrt(5))/2)^(n+1) )

Trying this out:
F(0) = 1/sqrt(5) . ( ((1+sqrt(5))/2) - ((1-sqrt(5))/2) )
     = 1/sqrt(5) . ( 1/2 + sqrt(5)/2 -1/2 +sqrt(5)/2 )
     = 1/sqrt(5) . ( sqrt(5) )
     = 1
F(1) = 1/sqrt(5) . ( ((1+sqrt(5))/2)^2 - ((1-sqrt(5))/2)^2 )
     = 1/sqrt(5) . ( 1+2sqrt(5)+5 -1+2sqrt(5)-5 )/4
     = 1/sqrt(5) . ( 4sqrt(5) )/4
     = 1
So it seems to work...!

"""

#a Imports
import sys, os
import math
sys.path.insert(0, os.path.abspath('../python'))

from gjslib.math.polynomial import c_polynomial

#c Recurrence class
class c_recurrence( object ):
    def __init__( self, coeffs, initial_values ):
        """
        coeffs is a tuple of (a,b,c...)

        Recurrence relation is
        a + b.xn + c.xn+1 + ... = xn+p
        where p=len(tuple)-1

        Resolves to
        xn = ai.di^n + k (for a sum of ai/di pairs)
        """
        self.coeffs = coeffs
        self.initial_values = initial_values
        self.a_d = []
        self.k = 0
        self.order = len(self.coeffs)-1
        poly_coeffs = []
        for c in coeffs[1:]:
            poly_coeffs.append(-c)
            pass
        poly_coeffs.append(1)
        self.polynomial = c_polynomial( poly_coeffs )
        self.find_constant()
        self.find_ads()
        pass
    def find_constant( self ):
        if self.coeffs[0]==0:
            self.k = 0
            return
        n = 1.0
        for i in range(len(self.coeffs)-1):
            n -= self.coeffs[i+1]
            pass
        self.k = self.coeffs[0] / n
        pass
    def find_ads( self ):
        import numpy.matlib
        ds = []
        factors = self.polynomial.factorize()
        for f in factors:
            if f.is_linear():
                ds.append( -f.get_coeff(0) )
                pass
            elif not f.is_constant():
                raise Exception("Polynomial for recurrence relation must have all real roots but is %s"%(self.polynomial.pretty_factors("x")))
            pass

        r = numpy.matlib.zeros(self.order)
        m = numpy.matlib.zeros((self.order,self.order))
        for i in range(self.order):
            r[0,i] = self.initial_values[i]-self.k
            for j in range(self.order):
                m[i,j] = math.pow(ds[j],i)
                pass
            pass
        a = m.getI().dot(r.getT())
        self.a_d = []
        for i in range(self.order):
            self.a_d.append( (a[i,0],ds[i] ) )
            pass
        print self.a_d
        pass
    def evaluate( self, n ):
        r = self.k
        for ad in self.a_d:
            r += ad[0]*math.pow(ad[1],n)
            pass
        return r
    
x = c_recurrence( (1,1,2), (1,3) )
x = c_recurrence( (2,1,4), (1,6) )
x = c_recurrence( (2,1,4), (2,10) )
x = c_recurrence( (0,-4,4,1), (0,1,7) )
x = c_recurrence( (0,-4,-15,13,15,-2), (0,1,2,3,4,5) )
for i in range(10): print i, x.evaluate(i)

