#!/usr/bin/env python

import math

class c_spherical_coord(object):
    tenth_pi = math.pi*0.1
    golden_ratio = (1.0 + math.sqrt(5))/2.0
    top_theta    =  math.atan2(1.0,golden_ratio)
    bottom_theta = -math.atan2(1.0,golden_ratio)
    theta_range  = top_theta-bottom_theta
    def __init__(self):
        self.theta   = 0.0
        self.phi = 0.0
        pass
    def spherical(self):
        return (self.phi, self.theta)
    def xyz(self):
        z = math.cos(self.theta)
        y = math.sin(self.theta)
        x = y * math.cos(self.phi)
        y = y * math.sin(self.phi)
        return (x,y,z)
    def icos_tuv(self):
        """
        """
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
            self.theta = self.top_theta + v*(math.pi/2 - self.top_theta)
            return
        self.theta = self.bottom_theta - v*(math.pi/2 - self.top_theta)
        return
    def from_spherical(self, phi_theta):
        self.phi = phi_theta[0]
        self.theta = phi_theta[1]
        pass
    def from_xyz(self, xyz):
        (x,y,z) = xyz;
        r = math.sqrt(x*x + y*y + z*z)
        if (r<0.0000001):
            self.theta=0.0
            self.phi  =0.0
            return
        self.phi   = math.atan2(y,x)
        self.theta = math.acos(z/r)
        pass
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
        y = y / math.pi
        return (x,y)

    def __repr__(self):
        r = "(%8.5f, %8.5f)"%(self.phi, self.theta)
        r +=  ": (%7.5f, %7.5f, %7.5f)" % self.xyz()
        r +=  ": (%d, %7.5f, %7.5f)" % self.icos_tuv()
        return r

sc = c_spherical_coord()
sc.from_spherical( (0.1, 0.1) )
print sc
xyz = sc.xyz()
sc.from_xyz( xyz )
print sc

def triangle_corners(t,u,v,fraction,projection):
    """
    Coordinates in triangle are actually ((u,v),(u+1,v),(u,v+1))/(2^fraction)
    """
    p0 = c_spherical_coord()
    p1 = c_spherical_coord()
    p2 = c_spherical_coord()
    f = math.pow(0.5,fraction)
    p0.from_icos_tuv((t,u*f,v*f))
    p1.from_icos_tuv((t,(u+1)*f,v*f))
    p2.from_icos_tuv((t,u*f,(v+1)*f))
    p0 = projection(p0)
    p1 = projection(p1)
    p2 = projection(p2)
    return (p0, p1, p2)

patterson = lambda x:x.project_to_xy_patterson()

def draw_triangle(im,draw,corners,fill=128):
    def imx(x,im=im):
        return ((x*0.99999)*im.size[0])%im.size[0]
    def imy(y,im=im):
        return (y+1)*im.size[1]/2
    coords = (imx(corners[0][0]), imy(corners[0][1]), 
              imx(corners[1][0]), imy(corners[1][1]), 
              imx(corners[2][0]), imy(corners[2][1]), 
              imx(corners[0][0]), imy(corners[0][1]))
    draw.line(coords,fill=fill)
    pass

png_filename = "../../1_earth_16k_div10.png"
from PIL import Image, ImageDraw
png = Image.open(png_filename)
im = Image.new("RGB", (512, 512), "white")
draw = ImageDraw.Draw(im)
f=3
for t in range(20):
    for u in range(1<<f):
        for v in range(1<<f):
            if (u+v<1<<f):
                draw_triangle(im,draw,triangle_corners(t,u,v,f,patterson),fill=(255,0,0))
            pass
        pass
    pass
im.save("test.png")

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
"""
"""
def tex_coord(scale,m,u,v):
    (tx,ty,half,uv00,uv10,uv01) = m
    tx = tx * scale
    ty = ty * scale
    #print tx,ty,u,v
    tx += (uv10[0]-uv00[0])*u + (uv01[0]-uv00[0])*v + scale*uv00[0]
    ty += (uv10[1]-uv00[1])*u + (uv01[1]-uv00[1])*v + scale*uv00[1]
    #print (tx,ty)
    return (tx,ty)
def im_get_pixel(im,xy):
    """0<x<1, -1<y<1"""
    (x,y)=xy
    if x<0: x+=1
    if (x>1): x-=1
    def imx(x,im=im):
        return ((x*0.99999)*im.size[0])%im.size[0]
    def imy(y,im=im):
        return (y+1)*im.size[1]/2
    x=imx(x)
    y=imy(y)
    return im.getpixel((x,y))
def im_set_pixel(im,xy,c):
    if (xy[0]<0):return
    if (xy[1]<0):return
    if (xy[0]>=im.size[0]):return
    if (xy[1]>=im.size[1]):return
    im.putpixel(xy,c)
    return
scale = 256
im = Image.new("RGB", (scale*2,scale*5), "white")
draw = ImageDraw.Draw(im)
p = c_spherical_coord()
for t in triangle_map:
    #if t not in [1]: continue
    for u in range(scale):
        for v in range(scale):
            if (u+v>=scale):break
            p.from_icos_tuv((t,u/(scale+0.0),v/(scale+0.0)))
            xy = p.project_to_xy_patterson()
            tex_xy = tex_coord(scale,triangle_map[t],u,v)
            im_set_pixel(im,tex_xy,im_get_pixel(png,xy))
            pass
        pass
    pass
im.save("test2.png")

asd
t=10
print triangle_corners(t,0,0,0.0,lambda x:x.project_to_xy_patterson())
print triangle_corners(t,0,0,1.0,lambda x:x.project_to_xy_patterson())
print triangle_corners(t,1,0,1.0,lambda x:x.project_to_xy_patterson())
print triangle_corners(t,0,1,1.0,lambda x:x.project_to_xy_patterson())
print    
print triangle_corners(t,0,0,3.0,lambda x:x.project_to_xy_patterson())
print triangle_corners(t,0,1,3.0,lambda x:x.project_to_xy_patterson())
print triangle_corners(t,0,2,3.0,lambda x:x.project_to_xy_patterson())
print triangle_corners(t,0,3,3.0,lambda x:x.project_to_xy_patterson())
print triangle_corners(t,0,4,3.0,lambda x:x.project_to_xy_patterson())
print triangle_corners(t,0,5,3.0,lambda x:x.project_to_xy_patterson())
print triangle_corners(t,0,6,3.0,lambda x:x.project_to_xy_patterson())
print triangle_corners(t,0,7,3.0,lambda x:x.project_to_xy_patterson())
print    
def midpoint_diff(t,u,v,fraction,projection):
    t0 = triangle_corners(t,u,v,fraction+1,projection)
    t1 = triangle_corners(t,u+1,v,fraction+1,projection)
    t2 = triangle_corners(t,u,v+1,fraction+1,projection)
    print t0[2][1]-t0[0][1]
    print t1[2][1]-t1[0][1]
    print t0,t1,t2
    pass
midpoint_diff(0,0,0,2,lambda x:x.project_to_xy_patterson())
for u in range(10+1):
    sc.from_icos_tuv( (1,0.00001,u/10.01+0.001) )
    print u,sc
    tuv = sc.icos_tuv()
    sc.from_icos_tuv(tuv)
    print u,sc
    pass
