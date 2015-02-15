#!/usr/bin/env python
class c_polynomial( object ):
    def __init__( self, coeffs=[0] ):
        self.coeffs=coeffs
        self.normalize()
        pass
    def __repr__( self ):
        return str(self.coeffs)
    def is_constant( self ):
        return len(self.coeffs)==1
    def is_linear( self ):
        return len(self.coeffs)==2
    def get_coeff( self, n ):
        return self.coeffs[n]
    def pretty( self, var ):
        fmt = ""
        if len(self.coeffs)==0: return "0"
        result = ""
        needs_plus = False
        for i in range(len(self.coeffs)):
            if self.coeffs[i]==0:
                pass
            elif self.coeffs[i]==1:
                if needs_plus: result+=" + "
                if i==0: fmt="1"
                result+=fmt
                needs_plus = True
                pass
            elif (self.coeffs[i]>0):
                if needs_plus: result+=" + "
                result += str(self.coeffs[i])+fmt
                needs_plus = True
                pass
            else:
                if needs_plus: result+=" - "
                else: result+="-"
                if self.coeffs[i]==-1:
                    if i==0: fmt="1"
                    result += fmt
                else:
                    result += str(-self.coeffs[i])+fmt
                needs_plus = True
                pass
            if i==0:
                fmt = var
                pass
            else:
                fmt = var+("^%d"%(i+1))
                pass
            pass
        return result
    def pretty_factors( self, var ):
        result = ""
        factors = self.factorize()
        needs_mult = False
        for f in factors:
            if needs_mult:
                result += " * "
                pass
            result += "("+f.pretty(var)+")"
            needs_mult = True
            pass
        return result
                
    def factorize( self ):
        import fractions
        factors = []
        poly = self
        while len(poly.coeffs)>1:
            for attempt in (0.01, -1.0, -5.0, -10.0, 1.0, 5.0, 10.0):
                x = poly.find_root(attempt)
                if x is not None:
                    x=x[0]
                    break
                pass
            if x is None:
                factors.append(poly)
                return factors
            f = fractions.Fraction(x).limit_denominator(1000)
            xx = float(f)
            p = c_polynomial([-f,1])
            p = c_polynomial([-x,1])
            factors.append(p)
            poly = poly.divide(p)[0]
            pass
        if len(poly.coeffs)==1:
            f = fractions.Fraction(poly.evaluate(0)).limit_denominator(1000)
            factors.append(c_polynomial([f]))
            pass
        return factors

    def normalize( self ):
        while (len(self.coeffs)>0) and (self.coeffs[-1]==0): self.coeffs.pop()
        return
    def add( self, other, scale=1 ):
        r = []
        sl = len(self.coeffs)
        ol = len(other.coeffs)
        for i in range(sl):
            if i>=ol:
                r.append(self.coeffs[i])
                pass
            else:
                r.append(self.coeffs[i]+scale*other.coeffs[i])
                pass
            pass
        for i in range(ol-sl):
            r.append(scale*other.coeffs[i+sl])
            pass
        return c_polynomial(coeffs=r)
    def multiply( self, other ):
        r = []
        sl = len(self.coeffs)
        ol = len(other.coeffs)
        for i in range(sl):
            v = self.coeffs[i]
            n = i
            for j in range(ol):
                while n>=len(r): r.append(0)
                r[n] += v*other.coeffs[j]
                n+=1
                pass
            pass
        return c_polynomial(coeffs=r)
    def differentiate( self ):
        r = []
        sl = len(self.coeffs)
        for i in range(sl-1):
            r.append(self.coeffs[i+1]*(i+1))
            pass
        return c_polynomial(coeffs=r)
    def evaluate( self, x ):
        v = 0
        xn = 1
        sl = len(self.coeffs)
        for i in range(sl):
            v += xn*self.coeffs[i]
            xn = xn*x
            pass
        return v
    def evaluate_poly( self, poly ):
        """
        self(n) = Sum( coeff[i].n^i )
        Apply to a polynomial 'poly'
        i.e. return self(poly)
        """
        result = c_polynomial()
        pn = c_polynomial(coeffs=[1])
        sl = len(self.coeffs)
        for i in range(sl):
            result = result.add( pn, scale=self.coeffs[i] )
            pn = pn.multiply(poly)
            pass
        return result
    def find_root( self, attempt ):
        """
        Use newton-raphson...
        """
        epsilon = 0.000001
        df = self.differentiate()
        x1 = attempt
        for i in range(40):
            x0 = x1
            dx = df.evaluate(x0)
            #print x1, dx
            if dx==0:
                return None
            x1 = x0 - self.evaluate(x0)/dx
            pass
        if -epsilon<self.evaluate(x1)<epsilon:
            return (x1, x0)
        return None
    def divide( self, other ):
        sl = len(self.coeffs)
        remainder = self.coeffs[:]
        result = []
        ol = len(other.coeffs)
        for i in range(1+sl-ol):
            shift = sl-ol-i
            m = remainder[shift+ol-1]/other.coeffs[-1]
            result.append(m)
            for j in range(ol):
                remainder[shift+j] -= m * other.coeffs[j]
                pass
            #print remainder
            remainder.pop()
            pass
        result.reverse()
        return (c_polynomial(coeffs=result),c_polynomial(coeffs=remainder))
            
import math
import fractions

def find_eqn( x ):
    epsilon = 0.00001
    tests = {}
    for i in range(30):
        tests["sqrt(%d)"%(i+2)]=math.sqrt(i+2)
        pass
    #tests = {"sqrt(21)":math.sqrt(21)}
    tests = {"sqrt(2)":math.sqrt(2)}
    def fred(x,a,b,n=100,approx=4):
        print x,a,b,n
        for i in range(n):
            if ((x-i*a)%b) < approx: return i,(x-i*a)/b
            pass
        (a,b)=(b,a)
        for i in range(n):
            if ((x-i*a)%b) < approx: return (x-i*a)/b,i
            pass
        return None
    def check( t, x, f, num, denom, mult=720 ):
        y = int(round(denom*x))
        r = fred(y*mult,num,denom,n=1000)
        #print r
        if r is not None:
            # int(x*denom)*mult = r[0]*num + r[1]*denom
            # So x*mult approx= r[0]*num/denom + r[1]
            # Or x = r[0]*num/denom/mult + r[1]/mult
            gr0 = fractions.gcd(r[0],mult)
            gr1 = fractions.gcd(r[1],mult)
            rr = ( (r[0]/gr0, mult/gr0), (r[1]/gr1,mult/gr1) )
            v = f*(0.+rr[0][0])/rr[0][1] + (0.+rr[1][0])/rr[1][1]
            if -epsilon<(x-v)<epsilon:
                print "%d/%d %s + %d/%d = %f (should be %f, diff %f)"%(rr[0][0],rr[0][1],t,rr[1][0],rr[1][1],v,x,x-v)
                pass
            pass
        pass
    for t,v in tests.iteritems():
        f = fractions.Fraction(v).limit_denominator(1000)
        check( t, x, f, num=f.numerator, denom=f.denominator )
        pass
    pass

def main():

    a = c_polynomial( [1] )
    b = a.multiply( c_polynomial([0, 1]) )
    c = b.multiply( c_polynomial([1, 1]) )
    d = c.multiply( c_polynomial([2, 1]) )
    e = d.multiply( c_polynomial([3, 1]) )
    f = e.multiply( c_polynomial([4, 1]) )
    g = f.multiply( c_polynomial([5, 1]) )
    h = g.multiply( c_polynomial([6, 1]) )

    print a
    print b
    print c
    print d
    print e
    print f
    print g
    print h

    print a.differentiate(), b.differentiate(), c.differentiate()

    print d.divide(b)
    print f.divide(d)

    print f.pretty_factors('n')

    for i in range(10):
        print i, d.evaluate(i)

    x = c_polynomial([0,1])
    x_p_1 = c_polynomial([1,1])
    x_m_1 = c_polynomial([-1,1])
    print c.evaluate_poly(x_p_1).pretty("x")
    print c.evaluate_poly(x_m_1).pretty("x")

    d_i     = d.evaluate_poly(x)
    d_i_m_1 = d.evaluate_poly(x_m_1)
    d_diff = d_i.add(d_i_m_1,scale=-1)
    print "d_diff",d_diff.pretty("i"),"   OR   ",d_diff.pretty_factors("i")

    e_i     = e.evaluate_poly(x)
    e_i_m_1 = e.evaluate_poly(x_m_1)
    e_diff = e_i.add(e_i_m_1,scale=-1)
    print "e_diff",e_diff.pretty("i"),"   OR   ",e_diff.pretty_factors("i")


    sum_i_0 = c_polynomial([0,1])
    sum_i_1 = c_polynomial([0,1/2.0]).multiply(c_polynomial([1,1]))
    sum_i_2 = d.add(sum_i_1,scale=-3)
    #
    # sum_i_2 = polynomial d MINUS d_diff.coeff[1]*sum_i_1
    # and divide by d_diff.coeff[2]
    # sum_i_3 = polynomial e MINUS e_diff.coeff[1]*sum_i_1
    #                        MINUS e_diff.coeff[2]*sum_i_2
    # and divide by e_diff.coeff[3]
    # etc
    # Actually we can keep the sums as (divisor, sum_poly)

    print sum_i_0.pretty_factors('n')
    print sum_i_1.pretty_factors('n')
    print sum_i_2.pretty_factors('n')

    print sum_i_0.pretty('n')
    print sum_i_1.pretty('n')
    print sum_i_2.pretty('n')

    x = c_polynomial([-3,3,1])
    print x.pretty('n') ,"=", x.pretty_factors('n')

    x = c_polynomial([165.0,-55.0,18.0,-6.0,-3.0,1.0])
    print x.pretty('n') ,"=", x.pretty_factors('n')

    print "\nLooking for ",610/987.0
    find_eqn( 610/987.0 )
    print "\nLooking for ",1597/987.0
    find_eqn( 1597/987.0 )
    print "\nLooking for ",math.sqrt(2)+3
    find_eqn( math.sqrt(2)+3 )
    print "\nLooking for ",154/949.0
    find_eqn( 154/949.0 )
    print "\nLooking for ",91/919.0
    find_eqn( 91/919.0 )
    print "\nLooking for ",251/829.0
    find_eqn( 251/829.0 )
    print "\nLooking for ",436/551.0
    find_eqn( 436/551.0 )
    print "\nLooking for ",-1.5+math.sqrt(21)/2
    find_eqn( 0*-1.5+math.sqrt(21) )
    print "\nLooking for ",-2378/985.0
    find_eqn( -2378/985.0 )

if __name__=="__main__": main()
