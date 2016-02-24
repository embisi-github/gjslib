#!/usr/bin/env python
import math

#a Useful functions
def normalize(xyz):
    d = 0
    for v in xyz:
        d += v*v
        pass
    if d<0.000001:
        pass
    d = math.sqrt(d)
    for i in range(len(xyz)):
        xyz[i] = xyz[i] / d
        pass
    pass
def vector_prod(a,b):
    r = [ a[1]*b[2] - a[2]*b[1],
          a[2]*b[0] - a[0]*b[2],
          a[0]*b[1] - a[1]*b[0] ]
    return r
        
#a c_matrix2x2
class c_matrix2x2(object):
    #f __init__
    def __init__(self,m):
        self.matrix = m
        pass
    #f invert
    def invert(self):
        det = self.matrix[0]*self.matrix[3] - self.matrix[1]*self.matrix[2]
        if (det>-0.00000001) and (det<0.00000001):
            self.matrix = (0.0,0.0,0.0,0.0)
            return
        self.matrix = (self.matrix[3]/det, -self.matrix[1]/det, -self.matrix[2]/det, self.matrix[0]/det)
        return
    #f apply
    def apply(self,m):
        return (self.matrix[0]*m[0] + self.matrix[1]*m[1],
                self.matrix[2]*m[0] + self.matrix[3]*m[1])

#a c_matrix3x3
class c_matrix3x3(object):
    """
    A 3x3 matrix stored as row-major 9-element self.matrix
    """
    #f __init__
    def __init__(self, m9=[0.0]*9):
        self.matrix = m9[:]
        pass
    #f invert
    def invert(self):
        (a,b,c, d,e,f, g,h,i) = self.matrix
        A =   e*i-f*h
        B = -(d*i-f*g)
        C =   d*h-e*g
        D = -(b*i-c*h)
        E =   a*i-c*g
        F = -(a*h-b*g)
        G =   b*f-c*e
        H = -(a*f-c*d)
        I =   a*e-b*d
        det = a*A + b*B + c*C
        if (det>-0.0000001) and (det<0.0000001):
            self.matrix = [0.0]*9
            return
        self.matrix = [A/det, D/det, G/det,
                       B/det, E/det, H/det,
                       C/det, F/det, I/det]
        pass
    #f mult3x3
    def mult3x3(self,m9):
        """
        """
        r = []
        for i in range(3):
            for j in range(3):
                v = 0
                for k in range(3):
                    v += self.matrix[3*i+k]*m9[3*k+j]
                    pass
                r.append(v)
                pass
            pass
        self.matrix = r
        pass
    #f lookat
    def lookat(self, eye, target, up):
        forward = [target[0]-eye[0],
                   target[1]-eye[1],
                   target[2]-eye[2]]
        normalize(forward)
        side = vector_prod(forward,up)
        normalize(side)
        up = vector_prod(side,forward)
        normalize(up)
        self.matrix = (side[0], side[1], side[2],
                       up[0], up[1], up[2],
                       -forward[0], -forward[1], -forward[2])
        pass
    #f apply
    def apply(self,xyz):
        """
        """
        r = []
        for i in range(3):
            v = 0
            for k in range(3):
                v += self.matrix[3*i+k]*xyz[k]
                pass
            r.append(v)
            pass
        return r
    #f __repr__
    def __repr__(self):
        return str(self.matrix)
    pass

#a c_matrix4x4
class c_matrix4x4(object):
    """
    A 4x4 matrix stored as row-major 16-element self.matrix
    """
    #f __init__
    def __init__(self,
                 r0=(1.0,0.0,0.0,0.0),
                 r1=(0.0,1.0,0.0,0.0),
                 r2=(0.0,0.0,1.0,0.0),
                 r3=(0.0,0.0,0.0,1.0)):
        self.matrix = [r0[0],r0[1],r0[2],r0[3],
                       r1[0],r1[1],r1[2],r1[3],
                       r2[0],r2[1],r2[2],r2[3],
                       r3[0],r3[1],r3[2],r3[3],]
        pass
    #f copy
    def copy(self):
        m = c_matrix4x4()
        m.matrix = self.matrix[:]
        return m
    #f perspective
    def perspective(self,fov,aspect,zFar,zNear):
        f = 1/math.tan(fov*3.14159265/180.0/2)
        self.matrix = [f/aspect, 0.0, 0.0, 0.0,
                       0.0, f, 0.0, 0.0,
                       0.0, 0.0, (zFar+zNear)/(zFar-zNear), 2.0*(zFar*zNear)/(zFar-zNear),
                       0.0, 0.0, -1.0, 0.0]
        pass
    #f translate
    def translate(self,xyz,scale=1.0):
        m = [1,0,0,xyz[0]*scale,
             0,1,0,xyz[1]*scale,
             0,0,1,xyz[2]*scale,
             0,0,0,1]
        self.mult4x4(m)
        pass
    #f mult3x3
    def mult3x3(self,m=None,m9=None,m3=None,column_major=True):
        """
        Multiply by a 3x3 matrix as either row-major 9 element m9
        or row or column major 3x3 m3.
        OpenGL is column major for 3x3 matrices
        """
        if m is not None:
            m9 = m.matrix
            pass
        if m3 is not None:
            if column_major:
                m9 = (m3[0][0], m3[1][0], m3[2][0],
                      m3[0][1], m3[1][1], m3[2][1],
                      m3[0][2], m3[1][2], m3[2][2])                  
                pass
            else:
                m9 = (m3[0][0], m3[0][1], m3[0][2],
                      m3[1][0], m3[1][1], m3[1][2],
                      m3[2][0], m3[2][1], m3[2][2])                  
                pass
        m = [m9[0], m9[1], m9[2], 0,
             m9[3], m9[4], m9[5], 0,
             m9[6], m9[7], m9[8], 0,
             0, 0, 0, 1]
        self.mult4x4(m)
        pass
    #f mult4x4
    def mult4x4(self,m):
        """
        Multiply by a 4x4 matrix as row-major 16-element m
        """
        r = []
        for i in range(4):
            for j in range(4):
                v = 0
                for k in range(4):
                    v += self.matrix[4*i+k]*m[4*k+j]
                    pass
                r.append(v)
                pass
            pass
        self.matrix = r
        pass
    #f projection
    def projection(self):
        """
        Return 3x3 top left matrix as new c_matrix3x3
        """
        return c_matrix3x3([self.matrix[0],self.matrix[1],self.matrix[2],
                            self.matrix[4],self.matrix[5],self.matrix[6],
                            self.matrix[8],self.matrix[9],self.matrix[10]])
    #f apply
    def apply(self,xyz,perspective=True):
        """
        """
        m = list(xyz)
        m.append(1.0)
        r = []
        for i in range(4):
            v = 0
            for k in range(4):
                v += self.matrix[4*i+k]*m[k]
                pass
            r.append(v)
            pass
        if perspective:
            try:
                r[0] /= r[3]
                r[1] /= r[3]
                r[2] /= r[3]
                pass
            except:
                pass
            pass
        return r
    #f __repr__
    def __repr__(self):
        r = ""
        for i in range(4):
            r+="["
            for j in range(4):
                r += " %12.9f"%self.matrix[i*4+j]
                pass
            r += "\n"
            pass
        return r

#a Main
def main():
    a = c_matrix4x4((1.0,0.0,0.0,0.0),
              (0.0,1.0,0.0,0.0),
              (0.0,0.0,1.0,0.0),
              (0.0,0.0,0.0,1.0))
    a.perspective(90.0,1.0,1.0,40.0)
    a.mult3x3( (1.0,0.0,0.0, 0.0,1.0,0.0, 0.0,0.0,1.0) )    
    a.translate( (-2.0,-3.0,-4.0) )
    a.mult3x3( (0.5,0.866,0.0, -0.866,0.5,0.0, 0.0,0.0,1.0) )    
    a.mult3x3( (0.5,-0.866,0.0, 0.866,0.5,0.0, 0.0,0.0,1.0) )    
    a.translate( (2.0,3.0,4.0) )
    print a

    a = c_matrix2x2( (0.0,2.0,-2.0,0.0) )
    print a.matrix
    a.invert()
    print a.matrix
    pass

if __name__ == '__main__':
    main()

