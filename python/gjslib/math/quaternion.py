#!/usr/bin/env python
import math
from matrix import c_matrix3x3, c_matrix4x4

class c_quaternion( object ):
    fmt = "%7.4f"
    default_fmt = "euler"
    @classmethod
    def identity( cls ):
        return cls()
    @classmethod
    def pitch( cls, angle, degrees=False ):
        return cls().from_euler( pitch=angle, degrees=degrees )
    @classmethod
    def yaw( cls, angle, degrees=False ):
        return cls().from_euler( yaw=angle, degrees=degrees )
    @classmethod
    def roll( cls, angle, degrees=False ):
        return cls().from_euler( roll=angle, degrees=degrees )
    @classmethod
    def from_sequence( cls, rotations, degrees=False ):
        q = cls()
        for (t,n) in rotations:
            r = {"roll":cls.roll, "pitch":cls.pitch, "yaw":cls.yaw}[t](n,degrees=degrees)
            print t,n,r, q
            q = r.multiply(q)
            pass
        return q
    @classmethod
    def of_euler( cls, roll, pitch, yaw, degrees=False ):
        return cls().from_euler( roll, pitch, yaw, degrees=degrees )
    def __init__( self, quat=None, euler=None, degrees=False, repr_fmt=None ):
        self.quat = {"r":1, "i":0, "j":0, "k":0}
        self.matrix = None
        if repr_fmt is None:
            repr_fmt = self.default_fmt
        self.repr_fmt = repr_fmt
        if quat is not None:
            self.quat["r"] = quat["r"]
            self.quat["i"] = quat["i"]
            self.quat["j"] = quat["j"]
            self.quat["k"] = quat["k"]
            pass
        if euler is not None:
            self.from_euler(roll=euler[0], pitch=euler[1], yaw=euler[2], degrees=degrees)
            pass
        pass
    def copy(self):
        return c_quaternion(quat=self.quat)
    def __repr__( self ):
        if self.repr_fmt=="euler":
            result = ("c_quaternion(euler=("+self.fmt+","+self.fmt+","+self.fmt+"),degrees=True)") % self.to_euler(degrees=True)
            return result
        result = ("c_quaternion({'r':"+self.fmt+", 'i':"+self.fmt+", 'j':"+self.fmt+", 'k':"+self.fmt+"})") % (self.quat["r"],
                                                                                       self.quat["i"],
                                                                                       self.quat["j"],
                                                                                       self.quat["k"] )
        return result
    def get_matrix( self ):
        if self.matrix is None: self.create_matrix()
        return self.matrix
    def get_matrix3( self ):
        m = self.get_matrix()
        return c_matrix3x3((m[0][0], m[0][1], m[0][2],
                            m[1][0], m[1][1], m[1][2],
                            m[2][0], m[2][1], m[2][2],))
    def get_matrix4( self ):
        m = self.get_matrix()
        m4 = c_matrix4x4( r0=(m[0][0], m[0][1], m[0][2], 0.0),
                                 r1=(m[1][0], m[1][1], m[1][2], 0.0),
                                 r2=(m[2][0], m[2][1], m[2][2], 0.0),
                                 r3=(0.0, 0.0, 0.0, 1.0) )
        return m4
    def create_matrix( self ):
        # From http://www.gamasutra.com/view/feature/131686/rotating_objects_using_quaternions.php?page=2
        # calculate coefficients
        x2 = self.quat["i"] + self.quat["i"]
        y2 = self.quat["j"] + self.quat["j"] 
        z2 = self.quat["k"] + self.quat["k"]
        xx = self.quat["i"] * x2
        xy = self.quat["i"] * y2
        xz = self.quat["i"] * z2
        yy = self.quat["j"] * y2
        yz = self.quat["j"] * z2
        zz = self.quat["k"] * z2
        wx = self.quat["r"] * x2
        wy = self.quat["r"] * y2
        wz = self.quat["r"] * z2
        m = [[0,0,0,0.],[0,0,0,0.],[0,0,0,0.],[0.,0.,0.,1.]]

        m[0][0] = 1.0 - (yy + zz)
        m[1][0] = xy - wz
        m[2][0] = xz + wy

        m[0][1] = xy + wz
        m[1][1] = 1.0 - (xx + zz)
        m[2][1] = yz - wx

        m[0][2] = xz - wy
        m[1][2] = yz + wx;
        m[2][2] = 1.0 - (xx + yy)

        self.matrix = m
        pass
    def from_euler( self, pitch=0, yaw=0, roll=0, degrees=False ):
        """
        Euler angles are roll, pitch and yaw. (Z, Y then X axis rotations)

        The yaw is done in the middle

        Roll is around Z
        Pitch is around Y
        Yaw is around X
        """
        if degrees:
            roll  = 3.14159265/180.0 * roll
            pitch = 3.14159265/180.0 * pitch
            yaw   = 3.14159265/180.0 * yaw
            pass

        (pitch,yaw)=(yaw,pitch)
        cr = math.cos(roll/2)
        cp = math.cos(pitch/2)
        cy = math.cos(yaw/2)
        sr = math.sin(roll/2)
        sp = math.sin(pitch/2)
        sy = math.sin(yaw/2)

        crcy = cr * cy
        srsy = sr * sy
        self.quat["r"] = cp * crcy + sp * srsy
        self.quat["i"] = sp * crcy - cp * srsy
        self.quat["j"] = cp * cr * sy + sp * sr * cy
        self.quat["k"] = cp * sr * cy - sp * cr * sy
        self.matrix = None
        return self
    def to_euler( self, degrees=False ):
        """
        Euler angles are roll, pitch and yaw.
        The rotations are performed in the order 
        """
        r = self.quat["r"]
        i = self.quat["i"]
        j = self.quat["j"]
        k = self.quat["k"]
        yaw   = math.atan2(2*(r*i+j*k), 1-2*(i*i+j*j))
        pitch = math.asin( 2*(r*j-i*k))
        roll  = math.atan2(2*(r*k+i*j), 1-2*(j*j+k*k))
        if degrees:
            roll  = 180.0/3.14159265 * roll
            pitch = 180.0/3.14159265 * pitch
            yaw   = 180.0/3.14159265 * yaw
            pass
        return (roll, pitch, yaw)
    def multiply( self, other ):
        A = (self.quat["r"] + self.quat["i"])*(other.quat["r"] + other.quat["i"])
        B = (self.quat["k"] - self.quat["j"])*(other.quat["j"] - other.quat["k"])
        C = (self.quat["r"] - self.quat["i"])*(other.quat["j"] + other.quat["k"]) 
        D = (self.quat["j"] + self.quat["k"])*(other.quat["r"] - other.quat["i"])
        E = (self.quat["i"] + self.quat["k"])*(other.quat["i"] + other.quat["j"])
        F = (self.quat["i"] - self.quat["k"])*(other.quat["i"] - other.quat["j"])
        G = (self.quat["r"] + self.quat["j"])*(other.quat["r"] - other.quat["k"])
        H = (self.quat["r"] - self.quat["j"])*(other.quat["r"] + other.quat["k"])
        r = B + (-E - F + G + H) /2
        i = A - (E + F + G + H)/2 
        j = C + (E - F + G - H)/2 
        k = D + (E - F - G + H)/2
        return c_quaternion( quat={"r":r, "i":i, "j":j, "k":k } )
    def interpolate( self, other, t ):
        cosom = ( self.quat["i"] * other.quat["i"] +
                  self.quat["j"] * other.quat["j"] +
                  self.quat["k"] * other.quat["k"] +
                  self.quat["r"] * other.quat["r"] )
        abs_cosom = cosom
        sgn_cosom = 1
        if (cosom <0.0): 
            abs_cosom = -cosom
            sgn_cosom = -1
            pass

        # calculate coefficients
        if ( (1.0-abs_cosom) > epsilon ):
            #  standard case (slerp)
            omega = math.acos(abs_cosom);
            sinom = math.sin(omega);
            scale0 = math.sin((1.0 - t) * omega) / sinom;
            scale1 = math.sin(t * omega) / sinom;
            pass
        else:
            # "from" and "to" quaternions are very close 
            #  ... so we can do a linear interpolation
            scale0 = 1.0 - t;
            scale1 = t;
            pass

        # calculate final values
        i = scale0 * self.quat["i"] + scale1 * sgn_cosom * other.quat["i"]
        j = scale0 * self.quat["j"] + scale1 * sgn_cosom * other.quat["j"]
        k = scale0 * self.quat["k"] + scale1 * sgn_cosom * other.quat["k"]
        r = scale0 * self.quat["r"] + scale1 * sgn_cosom * other.quat["r"]
        return c_quaternion( quat={"r":r, "i":i, "j":j, "k":k } )

def test():
    c_quaternion.default_fmt = "quat"

    print "Identity, roll30, yaw30, pitch30..."
    i = c_quaternion.identity()
    print i, i.get_matrix(), i.to_euler(degrees=True)

    roll30 = c_quaternion.roll(math.radians(30))
    print roll30, roll30.get_matrix(), roll30.to_euler(degrees=True)

    yaw30 = c_quaternion.yaw(math.radians(30))
    print yaw30, yaw30.get_matrix(), yaw30.to_euler(degrees=True)

    pitch30 = c_quaternion.pitch(math.radians(30))
    print pitch30, pitch30.get_matrix(), pitch30.to_euler(degrees=True)


    print
    print "90 degrees roll, pitch, yaw from 3*roll30 etc"
    roll90 = roll30.multiply(roll30.multiply(roll30))
    print roll90, roll90.get_matrix(), roll90.to_euler(degrees=True)

    yaw90 = yaw30.multiply(yaw30.multiply(yaw30))
    print yaw90, yaw90.get_matrix(), yaw90.to_euler(degrees=True)

    pitch90 = pitch30.multiply(pitch30.multiply(pitch30))
    print pitch90, pitch90.get_matrix(), pitch90.to_euler(degrees=True)

    print
    print "roll 180, 360..."
    roll180 = roll90.multiply(roll90)
    print roll180, roll180.get_matrix(), roll180.to_euler(degrees=True)
    roll360 = roll180.multiply(roll180)
    print roll360, roll360.get_matrix(), roll360.to_euler(degrees=True)

    print
    print "yaw90 of pitch90"
    k = yaw90.multiply(pitch90)
    print k, k.get_matrix(), k.to_euler(degrees=True)

    print
    print "roll90 of yaw90 of pitch90, and then repeated, and then repeated; second should be 180,0,180, last should be 0,0,0"
    k = roll90.multiply(yaw90.multiply(pitch90))
    print k, k.get_matrix(), k.to_euler(degrees=True)
    k = k.multiply(k)
    print k, k.get_matrix(), k.to_euler(degrees=True)
    k = k.multiply(k)
    print k, k.get_matrix(), k.to_euler(degrees=True)

    print
    print "roll30 OF a yaw30..."
    k = roll30.multiply(yaw30)
    print k, k.get_matrix(), k.to_euler(degrees=True)

    print
    print "roll -90 of yaw -90 of pitch 90 of yaw 90, should be the identity"
    x = roll90.multiply(roll90.multiply(roll90.multiply(yaw90.multiply(yaw90.multiply(yaw90.multiply(pitch90.multiply(yaw90)))))))
    print x, x.get_matrix(), x.to_euler(degrees=True)

    print
    print "roll90, pitch90, yaw90, to/from euler"
    k = c_quaternion(euler=roll90.to_euler(degrees=True), degrees=True)
    print k, k.get_matrix(), k.to_euler(degrees=True)
    k = c_quaternion(euler=pitch90.to_euler(degrees=True), degrees=True)
    print k, k.get_matrix(), k.to_euler(degrees=True)
    k = c_quaternion(euler=yaw90.to_euler(degrees=True), degrees=True)
    print k, k.get_matrix(), k.to_euler(degrees=True)

    print
    print "from euler of rpy 90,90,0 in all the possible orders"
    k = c_quaternion(euler=(0,90,90), degrees=True)
    print k, k.get_matrix(), k.to_euler(degrees=True)
    k = c_quaternion(euler=(90,0,90), degrees=True)
    print k, k.get_matrix(), k.to_euler(degrees=True)
    k = c_quaternion(euler=(90,90,0), degrees=True)
    print k, k.get_matrix(), k.to_euler(degrees=True)

    print
    print "from euler of rpy 10,20,30 in all the possible orders"
    k = c_quaternion(euler=(10,20,30), degrees=True)
    print k, k.get_matrix(), k.to_euler(degrees=True)
    k = c_quaternion(euler=(20,30,10), degrees=True)
    print k, k.get_matrix(), k.to_euler(degrees=True)
    k = c_quaternion(euler=(30,10,20), degrees=True)
    print k, k.get_matrix(), k.to_euler(degrees=True)

    k = c_quaternion(euler=(10,30,20), degrees=True)
    print k, k.get_matrix(), k.to_euler(degrees=True)
    k = c_quaternion(euler=(30,20,10), degrees=True)
    print k, k.get_matrix(), k.to_euler(degrees=True)
    k = c_quaternion(euler=(20,10,30), degrees=True)
    print k, k.get_matrix(), k.to_euler(degrees=True)

    print
    print "Roll 30 of yaw 20 of pitch 10"
    k = ( c_quaternion.roll(math.radians(30)).multiply( 
            c_quaternion.yaw(math.radians(20)).multiply( 
                c_quaternion.pitch(math.radians(10)))) )
    print k, k.get_matrix(), k.to_euler(degrees=True)

    print
    print "Pitch 30 of yaw 20 of roll 10"
    k = ( c_quaternion.pitch(math.radians(30)).multiply( 
            c_quaternion.yaw(math.radians(20)).multiply( 
                c_quaternion.roll(math.radians(10)))) )
    print k, k.get_matrix(), k.to_euler(degrees=True)

def main():
    test()

if __name__ == '__main__': main()
