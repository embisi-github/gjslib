#!/usr/bin/env python
# PYTHONPATH=`pwd`/../python:$PYTHONPATH ./mapping.py

#a Documentation
"""
An image should have a 'viewed from' 3D point, a unit view direction, a unit 'up' vector
and two scale factors (one for x, one for y).
The unit view direction has 2 DOF; the up vector must be perpendicular to the view direction and so has 1 DOF
This is a total of 5 DOF plus the 3D view point.

Note that a glutPerspective has FOV, aspect, zNear, zFar, plus a translation. The zNear/zFar provide a scaling factor, hence 1DOF.
In fact, these four probably supply 2 DOF for the view.

We can treat the image as a projection of the model onto a clip plain, and this clip plane as having 3 axes with an origin at the center of the image:
1. the axis perpendicular to the image (Z), which has (at distance 1 on the axis) the 'center of the clip'
2. the axis for the 'left-right' of the clip plane (X) which at distance 1 is the right-hand center of the image
3. the axis for the 'up-down' of the clip plane (Y) which at distance 1 is the top center of the image

If we have a matrix and translation that converts from model to projection we have
Clip(obj) = P . (obj - T)
OR, inverting:
obj(Clip) = T + P'.Clip

Now we have defined:
Clip(viewed from)     = (0,0,0) -> T = viewed_from
Clip(center of image) = (0,0,1)
Clip(center-right-of-image) = (1,0,1)
Clip(center-top-of-image)   = (0,1,1)

For the "Main" image we can have a view_from as Obj(0,0,0) and image center as Obj(0,0,1), image right as Obj(1,0,1), etc
This means that Clip() = Obj() for "Main" image - i.e. P is the identity (perspective) matrix

From the "Main" image we can cast rays for each known image point in model space; if the point as at (x,y) in the image, then
it must be at (x,y,1) in clip space (since that is where the image lies), and hence the model point is in model space at
(kx,ky,k) for some unknown k

For non-Main image we can cast rays, and each model point will be on the line ViewFrom(img)+k*ViewVector(img,x,y)

Now for another image we will need to determine its model space view from point, its model space unit view direction, its model space view 'up' unit vector, and its two scaling factors (X and Y)

If we fully know a model space point (Mx,My,Mz) and we know its image (Ix,Iy) we have:
Clip(Mx,My,Mz) = (Ix.Iw,Iy.Iw,Iz.Iw,Iw) = [Pimg,Timg] . (Mx,My,Mz,1)


We could assume the image projections are all perfect, and then find model positions for each image point.
This would be done by creating a set of lines that each image point must lie on in model space.

We then want to find the model space point that has the least distance from all the lines.

Line_set(p) = For all image that have pt p [ ImgToModel(image,image_coords[image,p]) ]

One approach is to find the O(N^2) set of midpoints of 'closest points between 2 lines'
and do a reasonable average


We can also assume the model positions are all perfect, and adjust Pimg and Timg for an image such that the error in the image points is smallest


"""

#a Imports
import gjslib.graphics.obj
import gjslib.graphics.opengl
import math
from OpenGL.GLUT import *
from OpenGL.GLU import *
from OpenGL.GL import *

from gjslib.math.quaternion import c_quaternion
from gjslib.math import matrix

def vector_add(a,b,scale=1.0):
    d = []
    for i in range(len(a)):
        d.append(a[i]+b[i]*scale)
        pass
    return d

def dot_product(a,b):
    r = 0
    for i in range(len(a)):
        r += a[i]*b[i]
        pass
    return r

#a Correlation
class c_correlation(object):
    def __init__(self):
        self.sum_x = 0
        self.sum_y = 0
        self.sum_xy = 0
        self.sum_x2 = 0
        self.sum_y2 = 0
        self.n = 0
        pass
    def add_entry(self,x,y):
        self.sum_x += x
        self.sum_y += y
        self.sum_x2 += x*x
        self.sum_y2 += y*y
        self.sum_xy += x*y
        self.n += 1
        pass
    def correlation_coefficient(self):
        if self.n==0: return 0
        rn = self.sum_xy*self.n - self.sum_x*self.sum_y
        rd = ( math.sqrt(self.n*self.sum_x2 - self.sum_x*self.sum_x) *
               math.sqrt(self.n*self.sum_y2 - self.sum_y*self.sum_y) )
        if (rd<0.000001): return 0
        return rn/rd

#a Mapping data
object_guess_locations = {}
object_guess_locations["clkcenter"] = (0.0,0.0,6.5)
object_guess_locations["lspike"] = (-3.0,0.0,8.5)
object_guess_locations["rspike"] = ( 3.0,0.0,8.5)
faces = {}
faces["frontleft"]  = ["tl", "flcr", "flbr", "bl"]
faces["frontright"] = ["tr", "br", "frbl", "frcl"]
faces["clock"]      = ["clktl", "clkmtr", "clkmtl", "clktr", "clkbr", "clkbl"]
faces["lspike.fl"]  = ["lspikel", "lspike", "lspikef"]
faces["lspike.fr"]  = ["lspikef", "lspike", "lspiker"]
faces["rspike.fl"]  = ["rspikel", "rspike", "rspikef"]
faces["rspike.fr"]  = ["rspikef", "rspike", "rspiker"]

image_mapping_data = {}
image_mapping_data["main"] = {}
image_mapping_data["main"]["filename"] = "sidsussexbell.jpg"
image_mapping_data["main"]["size"] = (4272,2848)
image_mapping_data["main"]["projection"] = {"camera":(-6.0,-12.0,2.0),
                                            "target":(5.0,0.0,4.0),
                                            "up":(0.0,0.0,1.0),
                                            "xscale":1.3,
                                            "yscale":1.75}
image_mapping_data["main"]["projection"] = {'xscale': 1.16, 'camera': [-6.1199999999999735, -13.125000000000012, 2.2950000000000026], 'yscale': 1.83, 'target': [5.649999999999998, -0.02500000000000001, 3.879999999999999], 'up': (0.0, 0.0, 1.0)}
image_mapping_data["main"]["projection"] = {'xscale': 1.14, 'camera': [-5.4199999999999635, -13.300000000000015, 2.0950000000000033], 'yscale': 1.84, 'target': [5.624999999999997, 0.024999999999999994, 3.9799999999999986], 'up': (0.0, 0.0, 1.0)}
image_mapping_data["main"]["projection"] = {'xscale': 1.12, 'camera': [-5.044999999999958, -13.350000000000016, 2.0200000000000036], 'yscale': 1.85, 'target': [5.624999999999997, 0.049999999999999996, 4.029999999999999], 'up': (0.0, 0.0, 1.0)}
image_mapping_data["main"]["projection"] = {'xscale': 1.10, 'camera': [-4.6449999999999525, -13.400000000000016, 1.920000000000004], 'yscale': 1.87, 'target': [5.624999999999997, 0.075, 4.08], 'up': (0.0, 0.0, 1.0)}
image_mapping_data["main"]["projection"] = {'xscale': 1.08, 'camera': [-4.144999999999945, -13.425000000000017, 1.7700000000000045], 'yscale': 1.875, 'target': [5.574999999999997, 0.075, 4.155000000000001], 'up': (0.0, 0.0, 1.0)}
image_mapping_data["main"]["projection"] = {'xscale': 1.065, 'camera': [-3.7699999999999445, -13.400000000000016, 1.6950000000000047], 'yscale': 1.895, 'target': [5.574999999999997, 0.1, 4.205000000000002], 'up': (0.0, 0.0, 1.0)}
image_mapping_data["main"]["projection"] = {'xscale': 1.057, 'camera': [-3.4949999999999455, -13.400000000000016, 1.620000000000005], 'yscale': 1.895, 'target': [5.574999999999997, 0.125, 4.255000000000003], 'up': (0.0, 0.0, 1.0)}
image_mapping_data["main"]["projection"] = {'xscale': 1.052, 'camera': [-3.319999999999946, -13.375000000000016, 1.5700000000000052], 'yscale': 1.90, 'target': [5.574999999999997, 0.15, 4.280000000000003], 'up': (0.0, 0.0, 1.0)}

image_mapping_data["main"]["mappings"] = {"lspike":     ( 847, 335),
                                          "lspikel":    (785.2,596.0),
                                          "lspikef":    (833.2,596.5),
                                          "lspiker":    (854.0,613),
                                          
                                          "rspike":     (1839, 657),
                                          "rspikel":    (1805.2,863.2),
                                          "rspikef":    (1848.0,861.8),
                                          "rspiker":    (1854.0,875.2),

                                          "belltl":     (1342, 207),
                                          "belltr":     (1523, 270),
                                          "clkcenter":  (1377, 887),
                                          "ldrspike":   (1206,1334),
                                          "rdrspike":   (1584,1393),
                                          "cp":         (1400,1442),
                                          "tr":         (2330,1064),
                                          "br":         (2304,2163),
                                          "ldtl":       ( 365,1630),
                                          "ldtr":       ( 626,1656),
                                          "ldbl":       ( 371,2160),
                                          "ldbr":       ( 526,2158),

                                          "tl":         (-96,459),
                                          "flcr":       (1105,746),
                                          "flbr":       (1067,2148),
                                          "bl":         (-290,2148),

                                          #"tr":         (-96,459),
                                          "frcl":       (1597,870),
                                          "frbl":       (1562,2158),
                                          #"br":         (-290,2148)

                                          "clktl": (1206,546.5),
                                          "clkmtr":  (1299,589.5),
                                          "clkmtl":  (1502,647),
                                          "clktr":  (1583,669),
                                          "clkbr":  (1525.5,1602),
                                          "clkbl":  (1127,1573),
                                          }

image_mapping_data["img_1"] = {}
image_mapping_data["img_1"]["filename"] = "sidsussexbell_1.jpg"
image_mapping_data["img_1"]["size"] = (640,480)
image_mapping_data["img_1"]["projection"] = {"camera":(+7.0,-6.0,6.7),
                                            "target":(-1.0,0.0,5.5),
                                            "up":(0.0,0.0,1.0),
                                            "xscale":2.2,
                                            "yscale":2.1}
image_mapping_data["img_1"]["projection"] = {'xscale': 2.2, 'camera': [7.450000000000001, -5.575000000000011, 6.924999999999999], 'yscale': 2.1, 'target': [-1.0, 0.0, 5.449999999999999], 'up': (0.0, 0.0, 1.0)}
image_mapping_data["img_1"]["projection"] = {'xscale': 2.0, 'camera': [7.450000000000001, -5.575000000000011, 6.924999999999999], 'yscale': 2.1, 'target': [-1.0, 0.0, 5.449999999999999], 'up': (0.0, 0.0, 1.0)}
image_mapping_data["img_1"]["projection"] = {'xscale': 1.87, 'camera': [6.349999999999985, -7.225000000000034, 6.599999999999994], 'yscale': 2.35, 'target': [-1.0499999999999998, -0.025, 5.575000000000001], 'up': (0.0, 0.0, 1.0)}
image_mapping_data["img_1"]["projection"] = {'xscale': 1.83, 'camera': [5.97499999999998, -7.750000000000042, 6.449999999999992], 'yscale': 2.43, 'target': [-1.0749999999999997, -0.025, 5.625000000000002], 'up': (0.0, 0.0, 1.0)}
image_mapping_data["img_1"]["projection"] = {'xscale': 1.80, 'camera': [5.874999999999979, -7.950000000000045, 6.374999999999991], 'yscale': 2.46, 'target': [-1.0999999999999996, -0.025, 5.625000000000002], 'up': (0.0, 0.0, 1.0)}
image_mapping_data["img_1"]["projection"] = {'xscale': 1.78, 'camera': [5.7249999999999766, -8.025000000000045, 6.349999999999991], 'yscale': 2.49, 'target': [-1.0999999999999996, -0.025, 5.650000000000002], 'up': (0.0, 0.0, 1.0)}
image_mapping_data["img_1"]["projection"] = {'xscale': 1.78, 'camera': [5.7249999999999766, -8.050000000000045, 6.349999999999991], 'yscale': 2.495, 'target': [-1.0999999999999996, -0.025, 5.650000000000002], 'up': (0.0, 0.0, 1.0)}


image_mapping_data["img_1"]["mappings"] = {"lspike":     ( 250, 87),
                                          #"lspikel":    (785.2,596.0),
                                          "lspikef":    (243.6,149.9),
                                          "lspiker":    (256.4,151.5),

                                          "rspike":     ( 550, 33),
                                          "rspikel":    (538.6, 127.6),
                                          "rspikef":    (545.5,126.9),
                                          "rspiker":    (562.9,125.1),

                                          "clkcenter":  ( 370, 191),
                                          "ldrspike":   ( 301, 343),
                                          "rdrspike":   ( 405, 360),
                                          "cp":         ( 347, 378),
                                          "ldtl":       ( 210, 393),
                                          "ldtr":       ( 244, 402),

                                          "tl":         (137,178),
                                          "flcr":       (309,167),
                                          #"flbr":       (),
                                          "bl":         (144,461),

                                          #"tr":         (-96,459),
                                          "frcl":       (454.7,157.7),
                                          #"frbl":       (1562,2158),
                                          #"br":         (-290,2148)

                                           "clktl": (313.3,107,0),
                                           "clkmtr":  (336.7,104.3),
                                           "clkmtl":  (396.3,95.3),
                                           "clktr":  (426.0,92.3),
                                           "clkbr":  (427.3,424.0),
                                           "clkbl":  (318.0,400.4),

                                          }

image_mapping_data["img_2"] = {}
image_mapping_data["img_2"]["filename"] = "sidsussexbell_2.jpg"
image_mapping_data["img_2"]["size"] = (1024,772)
image_mapping_data["img_2"]["projection"] = {"camera":(0.0,-6.0,2.0),
                                            "target":( 0.0,0.0,7.2),
                                            "up":(0.01,0.0,1.0),
                                            "xscale":2.45,
                                            "yscale":3.8}
image_mapping_data["img_2"]["mappings"] = {"lspike":    (  72,208),
                                          "lspikel":    (36.7,376.0),
                                          "lspikef":    (60.0,368.7),
                                          "lspiker":    (90.0,383.3),

                                          "rspike":     ( 929,221),
                                          "rspikel":    (920.7,385.3),
                                          "rspikef":    (950.7,376.0),
                                          "rspiker":    (970.7,389.3),

                                          "clkcenter":  ( 515, 489),
                                          "belltl":     ( 428,   0),
                                          "belltr":     ( 583,   3),

                                          #"tl":         (137,178),
                                          "flcr":       (292.2,432.2),
                                          #"flbr":       (),
                                          #"bl":         (144,461),

                                          #"tr":         (-96,459),
                                          "frcl":       (727,435.8),
                                          #"frbl":       (1562,2158),
                                          #"br":         (-290,2148)

                                           "clktl":  (346.5,281.5),
                                           "clkmtr": (424.0,285.5),
                                           "clkmtl": (598.0,288.5),
                                           "clktr":  (675.0,288.5),
                                           #"clkbr":  (
                                           #"clkbl":  (

                                          }
image_mapping_data["img_2"]["projection"] = {'xscale': 2.445, 'camera': (-0.2, -6.2, 2.225), 'yscale': 3.77, 'target': (0.025, 0.025, 7.2), 'up': (0.01, 0.0, 1.0)}


image_mapping_data["img_3"] = {}
image_mapping_data["img_3"]["filename"] = "sidsussexbell_3.jpg"
image_mapping_data["img_3"]["size"] = (320,370)
image_mapping_data["img_3"]["projection"] = {'xscale': 3.0, 'camera': [0.05, -9.999999999999986, -0.8000000000000006], 'yscale': 2.97, 'target': [0.25, 0.2, 4.999999999999997], 'up': (0.0, 0.0, 1.0)}
image_mapping_data["img_3"]["projection"] = {'xscale': 3.0, 'camera': [0.05, -9.999999999999986, -0.8000000000000006], 'yscale': 2.97, 'target': [0.25, 0.2, 4.999999999999997], 'up': (0.0, 0.0, 1.0)}
image_mapping_data["img_3"]["projection"] = {'xscale': 3.0, 'camera': [0.05, -9.999999999999986, -0.7250000000000005], 'yscale': 2.95, 'target': [0.25, 0.2, 4.999999999999997], 'up': (0.0, 0.0, 1.0)}
image_mapping_data["img_3"]["projection"] = {'xscale': 3.0, 'camera': [0.05, -9.999999999999986, -0.6750000000000005], 'yscale': 2.94, 'target': [0.25, 0.2, 4.999999999999997], 'up': (0.0, 0.0, 1.0)}
image_mapping_data["img_3"]["projection"] = {'xscale': 3.0, 'camera': [0.05, -9.999999999999986, -0.6500000000000005], 'yscale': 2.93, 'target': [0.25, 0.2, 4.999999999999997], 'up': (0.0, 0.0, 1.0)}

image_mapping_data["img_3"]["mappings"] = {"lspike":    ( 40.5, 53.2),
                                          "lspikel":    (33.4,95.8),
                                          "lspikef":    (39.0,94.9),
                                          "lspiker":    (46.5,96.3),

                                          "rspike":     (259.8,56.5),
                                          "rspikel":    (255.7,97.6),
                                          "rspikef":    (262.6,97.5),
                                          "rspiker":    (268.0,97.4),

                                          "clkcenter":  (152.2,122.2),
                                          "belltl":     (131.8,   0),
                                          "belltr":     (172.2,   1),
                                          "ldtr":       ( 16.5, 272.2),
                                          "cp":         (153.0, 219.2),
                                          "ldrspike":   (109.5,207.8),
                                          "rdrspike":   (194.9,205.1),

                                           "clktl":  (109.8,72.1),
                                           "clkmtr": (129.5,71.8),
                                           "clkmtl": (175.0,72.8),
                                           "clktr":  (193.6,73.),
                                           "clkbr":  (197.8,248.0),
                                           "clkbl":  (104.9,246.9),

                                          }

#a Closest meeting of two lines
def closest_meeting_of_two_lines(p0, d0, p1, d1, too_close=0.0001):
    """
    Points on the lines are p0+s.d0 and p1+t.d1
    The closest points are c0 and c1, with sc and tc the closest coefficients

    Consider a 3D space with the axes d0, d1 and d0 x d1
    Every point in space can be represented as (a,b,c) = a.d0 + b.d1 + c.(d0 x d1)
    for some a,b,c for the point

    Points on p0+s.d0 are expressed in this space as s'.d0 + P0b.d1 + P0c.(d0 x d1)
    Points on p1+t.d1 are expressed in this space as P1a.d0 + t'.d1 + P1c.(d0 x d1)

    A vector between these two points is then:
    (s'-P1a).d0 + (P0b-t').d1 + (P0c-P1c).(d0 x d1)

    This has minimum length when s'-P1a is zero and P0b-t' is zero (since d0 x d1 is perpendicular to d0 and d1)

    Now, p0 is at P0a.d0 + P0b.d1 + P0c.(d0 x d1), and s=s'-P0a (and t=t'-P1b)
    p0.d0 = P0a.(d0.d0) + P0b.(d1.d0)
    p0.d1 = P0a.(d0.d1) + P0b.(d1.d1)
    i.e. [d0.d0 d1.d0] [P0a]  = [p0.d0]
         [d0.d1 d1.d1] [P0b]    [p0.d1]
    and
         [d0.d0 d1.d0] [P1a]  = [p1.d0]
         [d0.d1 d1.d1] [P1b]    [p1.d1]
    =>  P0a = 1/(d0.d0 . d1.d1 - d1.d0 . d0.d1) ( d1.d1 . p0.d0 - d1.d0 . p0.d1)
    and P0b = 1/(d0.d0 . d1.d1 - d1.d0 . d0.d1) (-d1.d0 . p0.d0 + d0.d0 . p0.d1)
    and P1a = 1/(d0.d0 . d1.d1 - d1.d0 . d0.d1) ( d1.d1 . p1.d0 - d1.d0 . p1.d1)
    and P1b = 1/(d0.d0 . d1.d1 - d1.d0 . d0.d1) (-d1.d0 . p1.d0 + d0.d0 . p1.d1)

    Now s=s'-P0a = P1a-P0a, t=t'-P1b = P0b-P1b
    s = 1/(d0.d0 . d1.d1 - d1.d0 . d0.d1) . (d1.d1 . d0.(p1-p0) - d1.d0 . d1.(p1-p0) )
    t = 1/(d0.d0 . d1.d1 - d1.d0 . d0.d1) . (d0.d0 . d1.(p1-p0) - d1.d0 . d0.(p1-p0) )
    
    If we set D = (d0.d0 . d1.d1 - d1.d0 . d0.d1) (determinant of our solution matrix)
    we can see when the solution is degenerate

    D = |d0|^2 . |d1|^2 - (|d0||d1|cos(d0d1) )^2
    D = sin^2(d0d1) . (|d0||d1|)^2
    If d0 and d1 are approximately unit vectors, D is then sin^2(angle) between
    i.e. D<epsilon implies the lines are too close to parallel

    We can also see how 'close' the lines are by |c1-c0|, or (c1-c0).(c1-c0)
    Indeed, we can have a measure of 'goodness' using (c1-c0).(c1-c0) / D

    """
    p1p0 = vector_add(p1,p0,scale=-1.0)
    d0d0 = dot_product(d0,d0)
    d1d1 = dot_product(d1,d1)
    d0d1 = dot_product(d0,d1)

    d0p10 = dot_product(d0,p1p0)
    d1p10 = dot_product(d1,p1p0)

    D = d0d0*d1d1 - d0d1*d0d1

    if D<too_close:
        return ( (0.0,0.0), (0.0,0.0), 0.0, 1.0/too_close )

    s = (d1d1*d0p10 - d0d1*d1p10) / D
    t = (d0d1*d0p10 - d0d0*d1p10) / D

    c0 = vector_add(p0,d0,scale=s)
    c1 = vector_add(p1,d1,scale=t)

    dc = vector_add(c1,c0,scale=-1.0)
    dc2 = dot_product(dc,dc)

    goodness = dc2/D
    if goodness>1.0/too_close: goodness=1.0/too_close
    return (c0, c1, dc2, goodness)

class c_set_of_lines(object):
    def __init__(self):
        self.lines = []
        pass
    def add_line(self, pt, drn):
        drn = list(drn)
        matrix.normalize(drn)
        self.lines.append( (pt,drn) )
        pass
    def generate_meeting_points(self, too_close=0.0001):
        self.line_meetings = []
        self.posn = (0.0,0.0,0.0)
        for i in range(len(self.lines)):
            (p0,d0) = self.lines[i]
            for j in range(len(self.lines)):
                if (i>j):
                    (p1,d1) = self.lines[j]
                    meet = closest_meeting_of_two_lines(p0,d0,p1,d1,too_close)
                    self.line_meetings.append(meet)
                    pass
                pass
            pass
        if len(self.line_meetings)==0:
            return
        posn = (0.0,0.0,0.0)
        total_weight = 0
        for (c0,c1,dist,goodness) in self.line_meetings:
            weight = 1/(5.0+goodness)
            posn = vector_add(posn, c0, scale=0.5*weight)
            posn = vector_add(posn, c1, scale=0.5*weight)
            total_weight += weight
            #print c0,c1,weight,total_weight,posn
            pass
        #print posn, total_weight
        self.posn = vector_add((0.0,0.0,0.0), posn, scale=1/total_weight)
        pass
c = c_set_of_lines()
c.add_line( (0.0,0.0,0.0), (0.0,0.0,1.0) )    
c.add_line( (0.0,0.1,1.1), (1.0,0.0,1.0) )    
c.generate_meeting_points()
print c.line_meetings
#die

#a c_point_mapping
class c_point_mapping(object):
    def __init__(self):
        self.mappings = {}
        self.positions = {}
        pass
    def add_named_point(self,name):
        if name not in self.mappings:
            self.mappings[name] = {}
            pass
        pass
    def add_image_location(self,name,projection,image,xy):
        self.mappings[name][image] = (projection,xy)
        pass
    def get_xy(self, name, image ):
        if name not in self.mappings:
            return None
        if image not in self.mappings[name]:
            return None
        return self.mappings[name][image][1]
    def find_line_sets(self):
        line_sets = {}
        for n in self.mappings:
            m = self.mappings[n]
            line_sets[n] = c_set_of_lines()
            for img_name in m:
                (p,xy) = m[img_name]
                line = p.model_line_for_image(xy)
                line_sets[n].add_line(line[0],line[1])
                pass
            line_sets[n].generate_meeting_points()
            #print n, line_sets[n].line_meetings
            pass
        self.line_sets = line_sets
        pass
    def approximate_positions(self):
        for n in self.line_sets:
            self.positions[n] = self.line_sets[n].posn
            pass
        pass
#a c_image_projection
class c_image_projection(object):
    #f __init__
    def __init__(self,name,image_filename,size=(1.0,1.0)):
        self.name = name
        self.image_filename = image_filename
        self.texture = None
        self.mvp = None
        self.ip = None
        self.size = size
        pass
    #f set_projection
    def set_projection(self, projection=None, deltas=None, camera=(0.0,0.0,0.0), target=(0.0,0.0,0.0), up=(0.0,0.0,1.0), xscale=1.0, yscale=1.0, delta_scale=1.0, resultant_projection=None ):
        if projection is not None:
            camera = projection["camera"]
            target = projection["target"]
            up     = projection["up"]
            xscale = projection["xscale"]
            yscale = projection["yscale"]
            pass
        if deltas is not None:
            if "camera" in deltas: camera = vector_add(camera,deltas["camera"],scale=delta_scale)
            if "target" in deltas: target = vector_add(target,deltas["target"],scale=delta_scale)
            if "up" in deltas:     up     = vector_add(target,deltas["up"],scale=delta_scale)
            if "xscale" in deltas: xscale = xscale * deltas["xscale"]
            if "yscale" in deltas: yscale = yscale * deltas["yscale"]
            pass
        self.mvp = matrix.c_matrix4x4( r0=(xscale,0.0,0.0,0.0),
                                       r1=(0.0,yscale,0.0,0.0),
                                       r2=(0.0,0.0,1.0,0.0),
                                       r3=(0.0,0.0,-1.0,0.0),)
        m = matrix.c_matrix3x3()
        self.camera = camera[:]
        self.target = target[:]
        self.scales = (xscale,yscale)
        self.projection = { "camera":camera[:],
                            "target":target[:],
                            "up":    up[:],
                            "xscale":xscale,
                            "yscale":yscale}
        m.lookat( camera, target, up )
        #print m
        self.mvp.mult3x3(m=m)
        self.mvp.translate(camera, scale=-1)
        #print self.mvp
        self.ip = self.mvp.projection()
        self.ip.invert()
        if resultant_projection is not None:
            resultant_projection["camera"] = camera[:]
            resultant_projection["target"] = target[:]
            resultant_projection["up"]     = up[:]
            resultant_projection["xscale"] = xscale
            resultant_projection["yscale"] = yscale
            pass
        pass
    #f image_of_model
    def image_of_model(self,xyz):
        xy = self.mvp.apply(xyz,perspective=True)
        img_xy = ((1.0+xy[0])/2.0*self.size[0], (1.0-xy[1])/2.0*self.size[1])
        return (xy,img_xy)
    #f model_line_for_image
    def model_line_for_image(self,xy):
        dirn = [xy[0],xy[1],-1]
        dirn = self.ip.apply(dirn)
        return (self.camera, dirn)
    #f add_point_mapping
    def add_point_mapping(self, pm, name, xy):
        scaled_xy = (-1.0+2.0*xy[0]/(self.size[0]+0.0), 1.0-2.0*xy[1]/(self.size[1]+0.0))
        pm.add_image_location(name, self, self.name, scaled_xy)
        pass
    #f mapping_error
    def mapping_error(self, name, xy, corr=None):
        scaled_xy = (-1.0+2.0*xy[0]/(self.size[0]+0.0), 1.0-2.0*xy[1]/(self.size[1]+0.0))
        abs_error = 0
        if name in object_guess_locations:
            img_of_model = self.image_of_model(object_guess_locations[name])
            abs_error += ( (scaled_xy[0]-img_of_model[0][0])*(scaled_xy[0]-img_of_model[0][0]) +
                          (scaled_xy[1]-img_of_model[0][1])*(scaled_xy[1]-img_of_model[0][1]))
            xscale = scaled_xy[0] / img_of_model[0][0] * self.scales[0]
            yscale = scaled_xy[1] / img_of_model[0][1] * self.scales[1]
            if corr is not None:
                corr[0].add_entry(scaled_xy[0], img_of_model[0][0])
                corr[1].add_entry(scaled_xy[1], img_of_model[0][1])
                pass
            print name, xscale,yscale, xy, scaled_xy, img_of_model
            pass
        return abs_error
    #f load_texture
    def load_texture(self):
        self.texture = gjslib.graphics.opengl.texture_from_png(self.image_filename)
        self.object = gjslib.graphics.obj.c_obj()
        self.object.add_rectangle( (-10.0,10.0,0.0), (20.0,0.0,0.0), (0.0,-20.0,0.0) )
        self.object.create_opengl_surface()
        pass
    #f display
    def display(self):
        glPushMatrix()
        if self.texture is not None:
            glBindTexture(GL_TEXTURE_2D, self.texture)
            self.object.draw_opengl_surface()
            return
        glPushMatrix()
        glTranslate(self.camera[0],self.camera[1],self.camera[2])
        glutSolidCube(0.1)
        glPopMatrix()
        glColor3f(1.0, 1.0, 1.0)
        glLineWidth(1.0)
        glBegin(GL_LINES);
        glVertex3f(self.camera[0],self.camera[1],self.camera[2])
        glVertex3f(self.target[0],self.target[1],self.target[2])
        glEnd()
        glPopMatrix()
        pass
    pass

#a Useful functions
def point_on_plane(p0,p1,p2,k01,k02):
        mp = ( (p0[0] + k01 * (p1[0]-p0[0]) + k02 * (p2[0]-p0[0])),
               (p0[1] + k01 * (p1[1]-p0[1]) + k02 * (p2[1]-p0[1])),
               (p0[2] + k01 * (p1[2]-p0[2]) + k02 * (p2[2]-p0[2])),
               )
        return mp

#a c_mapping
class c_mapping(object):
    camera_deltas = [{"camera":(-0.1,0.0,0.0)},
                     {"camera":(+0.1,0.0,0.0)},
                     {"camera":(0.0,-0.1,0.0)},
                     {"camera":(0.0,+0.1,0.0)},
                     {"camera":(0.0,0.0,-0.1)},
                     {"camera":(0.0,0.0,+0.1)},
                     {}]
    target_deltas = [{"target":(-0.1,0.0,0.0)},
                     {"target":(+0.1,0.0,0.0)},
                     {"target":(0.0,-0.1,0.0)},
                     {"target":(0.0,+0.1,0.0)},
                     {"target":(0.0,0.0,-0.1)},
                     {"target":(0.0,0.0,+0.1)},
                     {}]
    up_deltas = [ {"up":(-0.01,0.0,0.0)},
                  {"up":(+0.01,0.0,0.0)},
                  {"up":(0.0,-0.01,0.0)},
                  {"up":(0.0,+0.01,0.0)},
                  {"up":(0.0,0.0,-0.01)},
                  {"up":(0.0,0.0,+0.01)},
                  {}]
    #f __init__
    def __init__(self):
        self.mvp =  matrix.c_matrix4x4()
        self.camera = gjslib.graphics.opengl.camera
        self.floatywoaty = (0.0,0.0,0.0)    
        self.aspect = 1.0
        self.zNear=1.0
        self.zFar=40.0
        self.point_mappings = c_point_mapping()
        self.image_projections = {}
        self.set_data()
        pass
    #f find_better_projection
    def find_better_projection(self,mappings,image_projection,projection,deltas_list,delta_scale):
        smallest_error = (None,10000)
        for deltas in deltas_list:
            r = {}
            image_projection.set_projection( projection=projection, deltas=deltas, delta_scale=0.25, resultant_projection=r )
            print
            print deltas
            e = 0
            corr = (c_correlation(), c_correlation())
            corr[0].add_entry(0.0,0.0)
            corr[1].add_entry(0.0,0.0)
            for n in mappings:
                e += image_projection.mapping_error(n,mappings[n],corr)
                pass
            print "Total error",e,1-corr[0].correlation_coefficient(), 1-corr[1].correlation_coefficient()
            e += 50.0*(1-corr[0].correlation_coefficient())
            e += 50.0*(1-corr[1].correlation_coefficient())
            if e<smallest_error[1]:
                smallest_error = (deltas,e,r)
                pass
            pass
        print "Smallest error",smallest_error
        print
        return smallest_error
    #f blah
    def blah(self, image_mapping_name):
        global image_mapping_data
        image_data = image_mapping_data[image_mapping_name]
        p = self.image_projections[image_mapping_name].projection
        for i in range(1000):
            for j in range(5):
                (d,e,p) = self.find_better_projection(image_data["mappings"],self.image_projections[image_mapping_name],p,self.camera_deltas,delta_scale=0.05)
                if len(d)==0: break
                pass
            (d,e,p) = self.find_better_projection(image_data["mappings"],self.image_projections[image_mapping_name],p,self.target_deltas,delta_scale=0.0125)
            (d,e,p) = self.find_better_projection(image_data["mappings"],self.image_projections[image_mapping_name],p,self.up_deltas,delta_scale=0.0025)
            pass
        pass
    #f set_data
    def set_data(self):
        global image_mapping_data
        for k in image_mapping_data:
            image_data = image_mapping_data[k]
            self.image_projections[k] = c_image_projection(k, image_data["filename"], size=image_data["size"])
            self.image_projections[k].set_projection( projection=image_data["projection"])

            print
            print k
            e = 0
            corr = (c_correlation(), c_correlation())
            for n in image_data["mappings"]:
                xy = image_data["mappings"][n]
                self.point_mappings.add_named_point(n)
                self.image_projections[k].add_point_mapping(self.point_mappings,n,xy)
                e += self.image_projections[k].mapping_error(n,xy,corr)
                pass
            print "Total error",e,1-corr[0].correlation_coefficient(), 1-corr[1].correlation_coefficient()
            pass
        #self.blah("img_3")
        pass
    #f reset
    def reset(self):
        global image_mapping_data
        gjslib.graphics.opengl.attach_menu("main_menu")
        self.camera["position"] = [0.0,10.0,-2.0]
        self.camera["facing"] = c_quaternion.identity()
        self.camera["facing"] = c_quaternion.pitch(-1*3.1415/2).multiply(self.camera["facing"])
        self.camera["facing"] = c_quaternion.roll(0*3.1415).multiply(self.camera["facing"])
        for k in image_mapping_data:
            #self.image_projections[k].load_texture()
            pass
        self.point_mappings.find_line_sets()
        self.point_mappings.approximate_positions()
        #die
        pass
    #f display_set_projection
    def display_set_projection(self):
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(self.camera["fov"],self.aspect,self.zNear,self.zFar)
        self.mvp.perspective(self.camera["fov"],self.aspect,self.zNear,self.zFar)

        self.camera["facing"] = c_quaternion.roll( self.camera["rpy"][0]).multiply(self.camera["facing"])
        self.camera["facing"] = c_quaternion.pitch(self.camera["rpy"][1]).multiply(self.camera["facing"])
        self.camera["facing"] = c_quaternion.yaw(  self.camera["rpy"][2]).multiply(self.camera["facing"])

        m = self.camera["facing"].get_matrix()
        self.camera["position"][0] += self.camera["speed"]*m[0][2]
        self.camera["position"][1] += self.camera["speed"]*m[1][2]
        self.camera["position"][2] += self.camera["speed"]*m[2][2]

        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        glMultMatrixf(m)
        glTranslate(self.camera["position"][0],self.camera["position"][1],self.camera["position"][2])

        self.mvp.mult3x3(m3=m)
        self.mvp.translate(self.camera["position"])
        pass
    #f display_image_points
    def display_image_points(self):
        global faces
        for n in faces:
            f = faces[n]
            pts = []
            for pt in f:
                if pt in self.point_mappings.positions:
                    pts.append(self.point_mappings.positions[pt])
                    pass
                pass
            if len(pts)>=3:
                i = 0
                j = len(pts)-1
                glBegin(GL_TRIANGLE_STRIP)
                while (j>=i):
                    glVertex3f(pts[i][0],pts[i][1],pts[i][2])
                    i += 1
                    if (i<=j):
                        glVertex3f(pts[j][0],pts[j][1],pts[j][2])
                        pass
                    j -= 1
                    pass
                glEnd()
                pass
            pass
        for n in self.point_mappings.mappings:
            (xyz) = self.point_mappings.line_sets[n].posn
            glPushMatrix()
            glMaterialfv(GL_FRONT,GL_AMBIENT,[1.0,0.3,0.3,1.0])
            glTranslate(xyz[0],xyz[1],xyz[2])
            glScale(0.03,0.03,0.03)
            glutSolidSphere(1,6,6)
            glPopMatrix()
            pass
        #for pt in ["clkcenter", "lspike", "rspike"]:
        for pt in ["rspike"]:
        #for pt in ["clkcenter", "lspike", "rspike", "belltl", "belltr"]:
            (r,g,b) = {"clkcenter":(1.0,0.3,1.0),
                   "rspike":(1.0,0.3,1.0),
                   "lspike":(1.0,0.3,1.0),
                   "belltl":(0.3,1.0,1.0),
                   "belltr":(0.3,1.0,1.0),}[pt]
            for k in self.image_projections:
                p = self.image_projections[k]
                xy = self.point_mappings.get_xy(pt, k)
                if xy is not None:
                    (p0,d0) = p.model_line_for_image(xy)
                    glMaterialfv(GL_FRONT,GL_AMBIENT,[r,g,b,1.0])
                    glLineWidth(2.0)
                    glBegin(GL_LINES);
                    glVertex3f(p0[0]+d0[0]*40.0,
                               p0[1]+d0[1]*40.0,
                               p0[2]+d0[2]*40.0)
                    glVertex3f(p0[0]-d0[0]*40.0,
                               p0[1]-d0[1]*40.0,
                               p0[2]-d0[2]*40.0)
                    glEnd()
                    pass
                pass
            pass
        glPushMatrix()
        glMaterialfv(GL_FRONT,GL_AMBIENT,[1.0,0.3,0.3,1.0])
        glTranslate(self.floatywoaty[0], self.floatywoaty[1], self.floatywoaty[2])
        glScale(0.03,0.03,0.03)
        glutSolidSphere(1,6,6)
        glPopMatrix()
        pass
    #f display_grid
    def display_grid(self,n):
        glLineWidth(1.0)
        glMaterialfv(GL_FRONT,GL_AMBIENT,[1.0,0.3,0.3,1.0])
        glBegin(GL_LINES)
        for i in range(2*10+1):
            glVertex3f(-10.0,(i-10)*1.0,0.0)
            glVertex3f( 10.0,(i-10)*1.0,0.0)
            glVertex3f( (i-10)*1.0,-10.0,0.0)
            glVertex3f( (i-10)*1.0,10.0,0.0)
            pass
        glEnd()
        glMaterialfv(GL_FRONT,GL_AMBIENT,[0.3,1.0,0.3,1.0])
        glBegin(GL_LINES)
        for i in range(2*10+1):
            glVertex3f( -10.0,0.0,(i-10)*1.0)
            glVertex3f(  10.0,0.0,(i-10)*1.0)
            glVertex3f( (i-10)*1.0,0.0,-10.0)
            glVertex3f( (i-10)*1.0,0.0, 10.0)
        glEnd()
        glMaterialfv(GL_FRONT,GL_AMBIENT,[0.3,0.3,1.0,1.0])
        glBegin(GL_LINES)
        for i in range(2*10+1):
            glVertex3f( 0.0, -10.0,(i-10)*1.0)
            glVertex3f( 0.0,  10.0,(i-10)*1.0)
            glVertex3f( 0.0, (i-10)*1.0,-10.0)
            glVertex3f( 0.0, (i-10)*1.0, 10.0)
        glEnd()
        glMaterialfv(GL_FRONT,GL_AMBIENT,[1.0,1.0,1.0,1.0])
        glLineWidth(3.0)
        glBegin(GL_LINES)
        glVertex3f( -12.0, 0.0, 0.0 )
        glVertex3f(  12.0, 0.0, 0.0 )
        glVertex3f( 0.0, -12.0, 0.0 )
        glVertex3f( 0.0,  12.0, 0.0 )
        glVertex3f( 0.0, 0.0, -12.0 )
        glVertex3f( 0.0, 0.0,  12.0 )
        glEnd()
        pass
    #f display_images
    def display_images(self):
        brightness = 1.0
        glEnable(GL_TEXTURE_2D)
        glMaterialfv(GL_FRONT,GL_DIFFUSE,[brightness*1.0,brightness*1.,brightness*1.0,1.])
        glMaterialfv(GL_FRONT,GL_AMBIENT,[1.0,1.0,1.0,1.0])
        for image in self.image_projections:
            self.image_projections[image].display()
            pass
        glDisable(GL_TEXTURE_2D)
        pass
    #f display
    def display(self):
        glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)

        self.display_set_projection()

        ambient_lightZeroColor = [1.0,1.0,1.0,1.0]
        glLightfv(GL_LIGHT1, GL_AMBIENT, ambient_lightZeroColor)
        glEnable(GL_LIGHT1)

        self.display_grid(3)
        self.display_image_points()
        self.display_images()
   
        glutSwapBuffers()
        pass
    #f find_in_triangle
    def find_in_triangle(self, xy, p0, p1, p2):
        """
        Iterative approach to finding a point on a plane that maps by self.mvp to xy on the screen
        """
        k01 = 0.0
        k02 = 0.0
        sp0 = self.mvp.apply(p0)
        sp1 = self.mvp.apply(p1)
        sp2 = self.mvp.apply(p2)
        dxy01 = (sp1[0]-sp0[0], sp1[1]-sp0[1])
        dxy02 = (sp2[0]-sp0[0], sp2[1]-sp0[1])
        #m = matrix2x2((dxy01.dxy01, dxy02.dxy01, dxy01.dxy02, dxy02.dxy02))
        m = matrix.c_matrix2x2((dxy01[0]*dxy01[0]+dxy01[1]*dxy01[1],
                       dxy02[0]*dxy01[0]+dxy02[1]*dxy01[1],
                       dxy02[0]*dxy01[0]+dxy02[1]*dxy01[1],
                       dxy02[0]*dxy02[0]+dxy02[1]*dxy02[1],))
        m.invert()
        def find_better_point(k01, k02):
            mp = point_on_plane(p0,p1,p2, k01,k02)
            sp = self.mvp.apply(mp)
            #print "better_point ks, mp and screen point",k01,k02,mp,sp
            dxy = (xy[0]-sp[0], xy[1]-sp[1])
            #dk01*dxy01 + dk02*dxy02 = dxy
            #dk01*dxy01.dxy01 + dk02*dxy02.dxy01 = dxy.dxy01
            #dk01*dxy01.dxy02 + dk02*dxy02.dxy02 = dxy.dxy02
            #return m.apply( (dxy.dxy01, dxy,dxy02) )
            dk = m.apply( (dxy[0]*dxy01[0] + dxy[1]*dxy01[1],
                             dxy[0]*dxy02[0] + dxy[1]*dxy02[1]) )
            return (k01+dk[0], k02+dk[1])
        for i in range(30):
            (k01,k02) = find_better_point(k01, k02)
        return (k01,k02)
    #f mouse
    def mouse(self,b,s,x,y):
        print "button, state, window x/y",b,s,x,y
        ip = self.mvp.projection()
        ip.invert()

        p0 = [0,0,0]
        p1 = [x,y,(self.zFar+self.zNear)/(self.zFar-self.zNear)]
        p0 = ip.apply(p0)
        p1 = ip.apply(p1)
        for i in range(3):
            p0[i] += self.camera["position"][i]
            p1[i] += self.camera["position"][i]
            pass
        print p0, p1
        # The plane going through p with normal n has points p' such that (p'-p).n = 0
        # The line p0 -> p1 has points px = p0 + k(p1-p0)
        # this intersects a plane in model space that is -10,-10,0 with unit normal 0,0,1
        # We know that (p0 + k(p1-p0) - p).n = 0
        # i.e. k(p1-p0).n = (p-p0).n
        n = (0.0,0.0,1.0)
        p = (0.0,0.0,0.0)
        p10n = (p1[0]-p0[0])*n[0] + (p1[1]-p0[1])*n[1] + (p1[2]-p0[2])*n[2]
        pp0n = (p[0]-p0[0])*n[0]  + (p[1]-p0[1])*n[1]  + (p[2]-p0[2])*n[2]
        k = pp0n/p10n
        p = (p0[0] + k*(p1[0]-p0[0]),
             p0[1] + k*(p1[1]-p0[1]),
             p0[2] + k*(p1[2]-p0[2]))
        print p
        k01 = (10-p[0])/20.0
        k02 = (10-p[1])/20.0
        print "proj coord in image",k01,k02,k01*4272, (1-k02)*2848

        #(k01,k02) = self.find_in_triangle((x,y), (-10.0,-10.0,0.0), (10.0,-10.0,0.0), (-10.0,10.0,0.0) )
        #print "coord in image",k01,k02,k01*4272, (1-k02)*2848
        self.floatywoaty = point_on_plane((-10.0,-10.0,0.0), (10.0,-10.0,0.0), (-10.0,10.0,0.0),k01,k02)
        pass
    pass

#a Main
def main():
    m = c_mapping()
    menus = [ ("submenu",   (("a",1), ("b",2))),
              ("main_menu", (("sub", "submenu"), ("c", 3)))
              ]
    gjslib.graphics.opengl.main(m.reset, m.display, mouse=m.mouse, menus=menus)

if __name__ == '__main__':
    main()

