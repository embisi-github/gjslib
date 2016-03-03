#!/usr/bin/env python
import math
import vectors
        
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
        forward = vectors.vector_add(target, eye, scale=-1.0)
        forward = vectors.vector_normalize(forward)
        side    = vectors.vector_prod3(forward,up)
        side    = vectors.vector_normalize(side)
        up      = vectors.vector_prod3(side,forward)
        up      = vectors.vector_normalize(up)
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
    #f transpose
    def transpose(self):
        m = self.matrix
        self.matrix = [m[0], m[4], m[8], m[12],
                       m[1], m[5], m[9], m[13],
                       m[2], m[6], m[10], m[14],
                       m[3], m[7], m[11], m[15]]
        pass
    #f scale
    def scale(self, scale):
        if type(scale)==int:
            scale = float(scale)
            pass
        if type(scale)==float:
            scale = (scale, scale, scale)
            pass
        if len(scale)==2:
            scale = (scale[0], scale[1], 1.0)
            pass
        m = c_matrix4x4( r0=(scale[0],0.0,0.0,0.0),
                         r1=(0.0,scale[1],0.0,0.0),
                         r2=(0.0,0.0,scale[2],0.0),
                         r3=(0.0,0.0,0.0,1.0) )
        self.mult4x4(m)
        pass
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
    def mult4x4(self,m, premult=False):
        """
        Multiply by a 4x4 matrix as row-major 16-element m
        """
        if premult:
            return self.premult4x4(m)
        if type(m)==c_matrix4x4:
            m=m.matrix
            pass
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
    #f premult4x4
    def premult4x4(self,m):
        """
        Premultiply by a 4x4 matrix as row-major 16-element m
        """
        if type(m)==c_matrix4x4:
            m=m.matrix
            pass
        r = []
        for i in range(4):
            for j in range(4):
                v = 0
                for k in range(4):
                    v += m[4*i+k]*self.matrix[4*k+j]
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
    #f get_matrix
    def get_matrix(self, linear=True, row_major=True):
        m = self.matrix
        if not row_major:
            m = self.copy()
            m.transpose()
            m = m.matrix
            pass
        if linear:
            return m
        return [ [m[0],  m[1],   m[2],  m[3]],
                 [m[4],  m[5],   m[6],  m[7]],
                 [m[8],  m[9],  m[10], m[11]],
                 [m[12], m[13], m[14], m[15]] ]
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

#a c_matrix
class c_matrixNxN(object):
    """
    N x N matrix, held in a linear list in row-major order

    i.e. matrxi[1] is the second column, first row
    """
    order = 2
    #f multiply_matrix_data
    @classmethod
    def multiply_matrix_data( cls, n, m0, m1 ):
        m = []
        for r in range(n): # Row of result
            for c in range(n): # Col of result
                d = 0
                for k in range(n):
                    d += m0[r*n+k] * m1[k*n+c]
                    pass
                m.append(d)
                pass
            pass
        return m
    #f multiply_matrices
    @classmethod
    def multiply_matrices( cls, matrix_0, matrix_1 ):
        m = cls.multiply_matrix_data(matrix_0.order, matrix_0.matrix, matrix_1.matrix)
        return cls(data=m)
    #f combine_lu
    @classmethod
    def combine_lu( cls, L, U):
        m = U.copy()
        for c in range(U.order):
            for r in range(U.order):
                if (c>r):
                    m[c,r] = L[c,r]
                    pass
                pass
            pass
        return m
    #f __init__
    def __init__(self, order=None, data=None):
        if order is None:
            if data is None:
                order=self.order
                pass
            else:
                order = [1,4,9,16,25,36].index(len(data))+1
                pass
            pass
        self.order = order
        if data is None:
            self.matrix = [0.]*(order*order)
            pass
        else:
            if len(data) != order*order:
                raise Exception("Bad data for order %d matrix"%order)
            self.matrix = data[:]
            pass
        pass
    #f get_matrix
    def get_matrix(self, row_major=True):
        if row_major:
            return self.matrix
        m = self.copy()
        m.transpose()
        return m.matrix
    #f copy
    def copy(self):
        return c_matrixNxN(data=self.matrix)
    #f apply
    def apply(self, v):
        n = self.order
        r = []
        for i in range(n):
            d = 0
            for j in range(n):
                d += self.matrix[i*n+j]*v[j]
                pass
            r.append(d)
            pass
        return r
    #f transpose
    def transpose(self):
        n = self.order
        r = []
        for i in range(n):
            d = 0
            for j in range(n):
                r.append(self.matrix[j*n+i])
                pass
            pass
        self.matrix = r
        return self
    #f premult
    def premult(self, matrix=None, data=None):
        if matrix is not None: data=matrix.matrix
        self.matrix = c_matrixNxN.multiply_matrix_data(self.order, data, self.matrix)
        return self
    #f postmult
    def postmult(self, matrix=None, data=None):
        if matrix is not None: data=matrix.matrix
        self.matrix = c_matrixNxN.multiply_matrix_data(self.order, self.matrix, data)
        return self

    #f __getitem__
    def __getitem__(self,key):
        if type(key)==tuple:
            key = self.order*key[0]+key[1]
        return self.matrix[key]
    #f __setitem__
    def __setitem__(self,key, value):
        if type(key)==tuple:
            key = self.order*key[0]+key[1]
        self.matrix[key] = value
    #f lup_decompose
    def lup_decompose(self):
        """
        Decompose into L and U matrices with a pivot P
        """
        n =  self.order
        P = []
        for i in range(n): P.append(i)

        LU = self.copy()
        # Run through the diagonal
        for d in range(n-1):
            # Find row with maximum (abs) value in c,r
            p = 0.
            r_max = None
            for r in range(d,n):
                t = LU[r, d]
                if t<0: t=-t
                if t>p:
                    p     = t
                    r_max = r
                    pass
                pass
            #print "Diagonal",d,"has max in row",p,r_max
            if p==0:
                return None
                raise Exception("Noninvertible matrix")

            # Swap row i with r_max and update the pivot list
            if r_max != d:
                (P[d], P[r_max]) = (P[r_max], P[d])
                for c in range(d,n):
                    (LU[d,c], LU[r_max,c]) = (LU[r_max,c], LU[d,c])
                    pass
                pass

            # Subtract out from rows below scaling down by LU[d][d] (in p) and up by LU[r][r]
            for r in range(d+1,n):
                scale = LU[r,d]/LU[d,d]
                LU[r,d] = scale
                for c in range(d+1,n):
                    LU[r,c] -= scale*LU[d,c]
                    pass
                pass

            # Next element on the diagonal...
            #print "After diagonal",d,LU
            pass
        return (LU, P)
    #f lup_invert
    def lup_invert(self, P):
        """
        self should be an LU matrix
        Note that LUP matrix is actually a matrix P.L.U
        If we find vectors 'x' such that L.U.x = P-1.Ic for the c'th column of the identity matrix
        we will find (with all 'n' x) the inverse
        """
        n = self.order
        R = c_matrixNxN(order=n)

        # For each column in the identity matrix...
        for c in range(n):
            # We want to find vector x such that LU.x = Ic
            # First find a such that L.a = Ic
            # Note that as L is a lower, we can find the elements top down
            a = [0]*n
            a[c] = 1
            for r in range(n):
                # Would divide a[r] by Lrr, but that is 1 for L
                # a[r] = a[r]/1
                # For the rest of the column remove multiples of a[r] (Lir, n>i>r)
                for i in range(r+1,n):
                    a[i] -= self[i,r]*a[r]
                    pass
                pass

            # Now we have L.a = Ic
            # Hence a = U.x
            # Here we can work up from the bottom of x - we have to start with a...
            x = a
            for r in range(n-1,-1,-1):
                # Now divide a[r] by Urr, which is not 1
                x[r] = x[r]/self[r,r]
                # For the rest of the column remove multiples of x[r] (Uir, r>i>=0)
                for i in range(0,r):
                    x[i] -= self[i,r]*x[r]
                    pass
                pass

            # So we know that LU.x = Ic
            # Insert into R at the permuted column
            for r in range(n):
                R[P[c],r] = x[r]
                pass
   
            pass
        R.transpose()
        return R
    #f lu_split
    def lu_split(self):
        """
        Split an LU where L has diagonal of 1s and is stored in lower half, U is upper half
        """
        L = self.copy()
        U = self.copy()
        n = self.order

        for r in range(n):
            for c in range(n):
                if (r==c):
                    L[r,c] = 1.
                    pass
                elif (r<c):
                    L[r,c] = 0.
                    pass
                else:
                    U[r,c] = 0.
                    pass
                pass
            pass
        return (L, U)
    #f inverse
    def inverse(self):
        lup = self.lup_decompose()
        if lup is None:
            return None
        return lup[0].lup_invert(lup[1])
    #f invert
    def invert(self):
        m = self.inverse()
        self.matrix = m.matrix
        return self
    #f __repr__
    def __repr__(self):
        return str(self.matrix)

#a Main
def main():
    print "LU decompose of 1,2 4,3 should be U=4,3 0,1.25  L= 1,0 0.25,1, P = 2,1; as one matrix this is 4,3, 0.25,1.25"
    a = c_matrixNxN(data=[1.,2.,4.,3.])
    print "A", a
    lup = a.lup_decompose()
    print "LUP", lup
    a_i = lup[0].lup_invert(lup[1])
    print "A inverse", a_i
    print c_matrixNxN.multiply_matrices(a,a_i)

    print
    print "More matrices"
    #a = c_matrixNxN(data=[1.,0.,0.,1.])
    a = c_matrixNxN(data=[1.,2.,3,4.,5.,4.,6.,3,2.])
    #L = c_matrixNxN(data=[1.,0.,0.,2.,1.,0.,3.,4.,1.])
    #U = c_matrixNxN(data=[3.,4.,6.,0.,2.,9.,0.,0.,1.])
    #LU = c_matrixNxN.combine_lu(L,U)
    #print "LU", LU
    #lup = (LU, lup[1])
    print "A", a
    lup = a.lup_decompose()
    print "LUP", lup
    a_i = lup[0].lup_invert(lup[1])
    print "A inverse", a_i
    print c_matrixNxN.multiply_matrices(a,a_i)

    print
    print "4 by 4..."
    a = c_matrixNxN(data=[-1.,3.,4.,5.,  0.,4.,2.,1., -5.,5.,2.,-3., -4.,3.,2.,1.])
    print "A",a
    lup = a.lup_decompose()
    print "LUP", lup
    L,U = lup[0].lu_split()
    print "U",U
    print "L",L
    print "L.U", c_matrixNxN.multiply_matrices(L,U)

    print "A inverse",a.inverse()
    b = a.copy()
    print "B",b
    b.invert()
    print "B inverted",b
    b.postmult(a)
    print "Identity?",b
    return
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

