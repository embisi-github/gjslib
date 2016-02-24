import math

class c_spherical_coord(object):
    tenth_pi = math.pi*0.1
    golden_ratio = (1.0 + math.sqrt(5))/2.0
    top_theta    =  math.atan2(1.0,golden_ratio)
    bottom_theta = -math.atan2(1.0,golden_ratio)
    theta_range  = top_theta-bottom_theta

    triangle_map = {}
    triangle_map[10] = (0,0,"lower",(0,0),(1,0),(0,1))
    triangle_map[11] = (0,0,"upper",(1,0),(1,1),(0,1))
    triangle_map[12] = (1,0,"lower",(0,0),(1,0),(0,1))
    triangle_map[13] = (1,0,"upper",(1,0),(1,1),(0,1))
    triangle_map[14] = (0,1,"lower",(1,0),(0,1),(0,0))
    triangle_map[ 9] = (0,1,"upper",(1,0),(0,1),(1,1))
    triangle_map[ 0] = (1,1,"lower",(0,0),(1,0),(0,1))
    triangle_map[ 1] = (1,1,"upper",(0,1),(1,1),(1,0))
    triangle_map[ 2] = (0,2,"lower",(0,0),(1,0),(0,1))
    triangle_map[ 3] = (0,2,"upper",(0,1),(1,1),(1,0))
    triangle_map[ 4] = (1,2,"lower",(1,0),(0,1),(0,0))
    triangle_map[17] = (1,2,"upper",(1,0),(0,1),(1,1))
    triangle_map[18] = (0,3,"lower",(0,0),(0,1),(1,0))
    triangle_map[19] = (0,3,"upper",(0,1),(1,1),(1,0))
    triangle_map[15] = (1,3,"lower",(0,0),(0,1),(1,0))
    triangle_map[16] = (1,3,"upper",(0,1),(1,1),(1,0))
    triangle_map[ 5] = (0,4,"lower",(0,0),(1,0),(0,1))
    triangle_map[ 6] = (0,4,"upper",(0,1),(1,1),(1,0))
    triangle_map[ 7] = (1,4,"lower",(0,0),(1,0),(0,1))
    triangle_map[ 8] = (1,4,"upper",(0,1),(1,1),(1,0))

    def __init__(self):
        self.theta   = 0.0
        self.phi = 0.0
        self.tuv = None
        pass
    def spherical(self):
        return (self.phi, self.theta)
    def icos_tuv(self):
        """
        """
        if self.tuv is not None:
            return self.tuv
        v = (self.theta - self.bottom_theta) / (self.theta_range)
        if (v>=1.0):
            u = self.phi/self.tenth_pi/4.0
            t = math.floor(u)
            u -= t
            t = int(t) % 5
            v = (self.theta - self.top_theta) / (math.pi/2 - self.top_theta)
            if (v>1.0): v=1.0
            return (t+10,u,v)
        if (v<0.0):
            u = self.phi/self.tenth_pi/4.0
            t = math.floor(u)
            u -= t
            t = int(t) % 5
            v = (self.bottom_theta - self.theta) / (math.pi/2 - self.top_theta)
            if (v>1.0): v=1.0
            return (t+15,u,v)
        u = ((self.phi/self.tenth_pi)-v)/4
        t = 0
        while (u<0):
            u += 5
            t += 5
            pass
        while (u>1):
            u -= 1
            t += 1
            pass
        if (t<0):
            u -= 1
            t += 1
        if (u<0): u=0.0
        if (u>1): u=1.0
        t = (2*t) % 10
        if (u+v)>1.0:
            return (t+1, u-(1.0-v), 1.0-v)
        return (t,u,v)
    def from_icos_tuv(self,tuv):
        """
        """
        self.tuv = tuv
        (t,u,v) = tuv
        if (t<10):
            if (t&1):
                u = u + v
                v = 1.0-v
                t -= 1
                pass
            self.phi = ((t+2*u)*2+v)*self.tenth_pi
            self.theta = self.bottom_theta + v*self.theta_range
            return
        if v==1.0:
            self.phi = 0
        else:
            self.phi = ((t%5)+u/(1.0-v))*4*self.tenth_pi
        if (t<15):
            self.phi = self.phi + self.tenth_pi
            if (self.phi>2*math.pi):
                self.phi -= 2*math.pi
                pass
            self.theta = self.top_theta + v*(math.pi/2 - self.top_theta)
            return
        self.theta = self.bottom_theta - v*(math.pi/2 - self.top_theta)
        return
    def from_spherical(self, phi_theta):
        self.phi = phi_theta[0]
        self.theta = phi_theta[1]
        self.tuv = None
        pass
    def xyz(self):
        z = math.sin(self.theta)
        y = math.cos(self.theta)
        x = y * math.cos(self.phi)
        y = y * math.sin(self.phi)
        return (x,y,z)
    def from_xyz(self, xyz):
        self.tuv = None
        (x,y,z) = xyz;
        r = math.sqrt(x*x + y*y + z*z)
        if (r<0.0000001):
            self.theta=0.0
            self.phi  =0.0
            return
        self.phi   = math.atan2(y,x)
        self.theta = math.asin(z/r)
        pass
    def tex_uv(self,scalex=1.0,scaley=1.0):
        """
        u,v in range 0<=u<1
        """
        (t,u,v) = self.icos_tuv()
        m = self.triangle_map[t]
        (tx,ty,half,uv00,uv10,uv01) = m
        tx += (uv10[0]-uv00[0])*u + (uv01[0]-uv00[0])*v + uv00[0]
        ty += (uv10[1]-uv00[1])*u + (uv01[1]-uv00[1])*v + uv00[1]
        return (tx*scalex,ty*scaley)
    def project_to_xy_patterson(self):
        """The last step involved developing polynomial equations approximating the Flex Projector template for the Patterson projection.
        The process was similar to that used for the Natural Earth projection.
        Between 55 degrees north and south latitude, the polynomial equation does not exactly match the Miller 1,
        but the differences are only noticeable at high magnification near 15 degrees latitude.
        Equation 1 transforms spherical longitude and latitude coordinates to projected coordinates.
        x = lambda 
        y = c1.phi + c2.phi^5 + c3.phi^7 + c4.phi^9
        (Equation 1)
        """
        c1 = 1.0148
        c2 = 0.23185
        c3 = -0.14499
        c4 = 0.02406
        x = self.phi
        y = c1*self.theta + c2*math.pow(self.theta,5.0) + c3*math.pow(self.theta,7.0) + c4*math.pow(self.theta,9.0)
        x = x / math.pi / 2
        #y = y / 1.728 # seems to be a magic number - basically y(pi/2)...math.pi
        y = y / 1.79086 # seems to be a magic number - basically y(pi/2)...math.pi
        return (x,y)

    def __repr__(self):
        r = "(%8.5f, %8.5f)"%(self.phi, self.theta)
        r +=  ": (%7.5f, %7.5f, %7.5f)" % self.xyz()
        r +=  ": (%d, %7.5f, %7.5f)" % self.icos_tuv()
        return r
