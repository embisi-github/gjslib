#!/usr/bin/env python
# PYTHONPATH=`pwd`/../python:$PYTHONPATH ./panoram360.py
from gjslib.math.spherical_coords import c_spherical_coord
import math

sc = c_spherical_coord()
sc.from_spherical( (0.1, -0.1) )
print sc
xyz = sc.xyz()
sc.from_xyz( xyz )
print sc

zero=0.000001
one=1.0-3*zero
sc.from_icos_tuv((11,zero,zero))
print sc
sc.from_icos_tuv((11,one,zero))
print sc
sc.from_icos_tuv((11,zero,one))
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
png_filename = "../../1_earth_16k.jpg"
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

triangle_map = c_spherical_coord.triangle_map
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
asd
scale = 1024
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
            tex_xy = p.tex_uv(scalex=scale,scaley=scale)
            tex_xy=(int(tex_xy[0]),int(tex_xy[1]))
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
