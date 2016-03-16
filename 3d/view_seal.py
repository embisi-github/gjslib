#!/usr/bin/env python
# PYTHONPATH=`pwd`/../python:$PYTHONPATH ./view_obj.py

#a Imports
from gjslib.graphics import opengl_app, opengl_utils, opengl_obj
from gjslib.math import quaternion

import math
from OpenGL.GLUT import *
from OpenGL.GLU import *
from OpenGL.GL import *
import OpenGL.arrays.vbo as vbo
import numpy

#a Classes
#c c_view_obj
class c_view_obj(opengl_app.c_opengl_camera_app):
    #f __init__
    def __init__(self, obj, seals, texture_filename, **kwargs):
        opengl_app.c_opengl_camera_app.__init__(self, **kwargs)
        self.seals = seals
        self.obj = obj
        self.xxx = 0.0
        self.yyy = 0.0
        self.window_title = "Viewing object"
        self.texture_filename = texture_filename
        self.seal_trails = {}
        self.years = {2005:False, 2006:True, 2007:True, 2010:True}
        self.display_time = 0
        self.select_years()
        pass
    #f seal_xyz
    def seal_xyz(self, seal, d):
        (lat,lon) = self.seals[seal].data[d][1],self.seals[seal].data[d][2]
        #lat = 0 + self.yyy*10
        #l#on = 45.0
        return self.ll_to_xyz(lat,lon)
    #f ll_to_xyz
    def ll_to_xyz(self, lat, lon):
        lon -= 90.0
        #lat -= 10.0
        q = quaternion.c_quaternion.pitch(-lat,degrees=True).multiply(quaternion.c_quaternion.roll(-lon,degrees=True))
        xyz = q.get_matrixn(order=3).apply((1.01,0,0))
        return xyz
    #f seal_trail
    def seal_trail(self,seal):
        s = self.seals[seal]
        vertices = []
        for d in s.data:
            vertices.append(self.ll_to_xyz(d[1],d[2]))
            vertices.append(self.ll_to_xyz(d[1],d[2]))
            pass
        if len(vertices)==0:
            print "Argh",seal
            return
        vertices.pop(0)
        vertices.pop()
        self.seal_trails[seal] = {"vectors":vbo.VBO(data=numpy.array(vertices, dtype=numpy.float32), target=GL_ARRAY_BUFFER ),
                                  "nvertices":len(vertices),
                                  }
        pass
    #f opengl_post_init
    def opengl_post_init(self):
        self.texture = opengl_utils.texture_from_png(self.texture_filename)
        self.obj.create_opengl_surface()
        for s in self.seals:
            self.seal_trail(s)
            pass
        self.camera["facing"] = quaternion.c_quaternion(euler=(-156.3232,21.7793,-30.0554),degrees=True)
        self.camera["position"] = [1.837988774095713, 3.94907536416929, -9.001477713931706]
        pass
    #f select_years
    def select_years(self,year=None):
        for y in self.years:
            self.years[y] = (year is None)
            pass
        if year is not None:
            self.years[year]=True
            print "Displaying",year
            pass
        min_t, max_t = None,None
        for s in self.seals:
            if self.years[self.seals[s].year]:
                (t0,t1) = self.seals[s].get_time_bounds()
                if min_t is None: min_t=t0
                if max_t is None: max_t=t1
                min_t = min(min_t,t0)
                max_t = max(max_t,t1)
                pass
            pass
        self.display_min_time = min_t
        self.display_max_time = max_t
        print min_t, max_t
    #f keypress
    def keypress(self, key,m,x,y):
        if key in ["1"]:
            print self.camera
            print key
            return True
        if key in ["2"]:
            self.select_years()
            return True
        if key in ["3"]:
            self.select_years(2005)
            return True
        if key in ["4"]:
            self.select_years(2006)
            return True
        if key in ["5"]:
            self.select_years(2007)
            return True
        if key in ["6"]:
            self.select_years(2010)
            return True
        return opengl_app.c_opengl_camera_app.keypress(self, key,m,x,y)
    #f display
    def display(self):
        opengl_app.c_opengl_camera_app.display(self)
        self.display_time = max(self.display_min_time, self.display_time)
        if self.display_time>self.display_max_time: self.display_time=self.display_min_time
        self.display_time += 1000

        self.yyy += 0.03
        lightZeroPosition = [4.+3*math.sin(self.yyy),4.,4.-3*math.cos(self.yyy),1.]
        lightZeroColor = [0.7,1.0,0.7,1.0] #white
        ambient_lightZeroColor = [1.0,1.0,1.0,1.0] #green tinged

        #glPushMatrix()
        #color = [1.0,0.,0.,1.]
        #glTranslate(lightZeroPosition[0],lightZeroPosition[1],lightZeroPosition[2])
        #glScale(0.3,0.3,0.3)
        #glutSolidSphere(2,40,40)
        #glPopMatrix()

        color = [0.5,0,0.,0.,1.]

        self.matrix_push()
        brightness = 0.4

        glBindTexture(GL_TEXTURE_2D, self.texture)
        self.matrix_push()
        self.matrix_scale(4)

        self.matrix_use()
        self.shader_use("color_standard")

        for seal in self.seals:
            if self.years[self.seals[seal].year]:
                self.matrix_use()
                self.seal_trails[seal]["vectors"].bind()
                self.shader_set_attributes( t=3, v=0, C=self.seals[seal].color )
                glDrawArrays(GL_LINES,0,self.seal_trails[seal]["nvertices"])
                self.seal_trails[seal]["vectors"].unbind()
                n = self.seals[seal].data_at_time(self.display_time)
                xyz = self.seal_xyz(seal,n)
                self.draw_simple_object("cross", self.seals[seal].color, xyz, 0.0003, 5*self.yyy)
                pass
            pass

        self.shader_use("texture_standard")
        self.matrix_use()
        self.obj.draw_opengl_surface(self)
        self.matrix_pop()
        self.matrix_pop()

        glutSwapBuffers()
        return
    #f All done
    pass

#a Top level
#f test_object
def test_object():
    glow_colors = []
    n = 10
    r = 0.5
    for i in range(3):
        for j in range(n):
            v = r*j/float(n)
            glow_colors.append((1-r+v, 1-v, r, 1-r+v, 1-v)[i:i+3])
            pass
        pass
    seal_data_years = {}
    seal_data_years[2005] = [("7345","seals/2005_2006/10W7345.csv"),
                 ("7313","seals/2005_2006/11W7313.csv"),
                 ("7316","seals/2005_2006/11W7316.csv"),
                 ("7346","seals/2005_2006/11W7346.csv"),
                 ("7344","seals/2005_2006/20W7344.csv"),
                 ("7310","seals/2005_2006/3W7310.csv"),
                 ("7309","seals/2005_2006/W7309.csv"),
                             ]
    seal_data_years[2006] = [
                 ("6703","seals/2006_2007/W6703gps3_v3.csv"),
                 ("7162","seals/2006_2007/W7162gps1_RTP.csv"),
                 ("7368","seals/2006_2007/W7368gps5.csv"),
                 ("7381","seals/2006_2007/W7381gps3.csv"),
                 ("7387","seals/2006_2007/W7387gps5.csv"),
                 ("7391","seals/2006_2007/W7391gps3_v3.csv"),
                 ("7392","seals/2006_2007/W7392gps5.csv"),
                 ("7393","seals/2006_2007/W7393gps3_RTP.csv"),
                 ("7412","seals/2006_2007/W7412gps1_RTP.csv"),
                 ("7416","seals/2006_2007/W7416gps1_RTP.csv"),
                 ]
    seal_data_years[2007] = [
                 ("gps1_16","seals/2007_2008/Staniland_gps1_16_01_08.csv"),
                 ("gps1_20","seals/2007_2008/Staniland_gps1_20_01_08.csv"),
                 ("gps1_23","seals/2007_2008/Staniland_gps1_23_01_08.csv"),
                 ("gps1_31","seals/2007_2008/Staniland_gps1_31_01_08.csv"),
                 ("gps2_08","seals/2007_2008/Staniland_gps2_08_02_08.csv"),
                 ("gps2_13","seals/2007_2008/Staniland_gps2_13_01_08.csv"),
                 ("gps2_18","seals/2007_2008/Staniland_gps2_18_01_08.csv"),
                 ("gps2_25","seals/2007_2008/Staniland_gps2_25_01_08.csv"),
                 ("gps2_31","seals/2007_2008/Staniland_gps2_31_01_08.csv"),
                 ("gps4_01","seals/2007_2008/Staniland_gps4_01_02_08.csv"),
                 ("gps4_07","seals/2007_2008/Staniland_gps4_07_02_08.csv"),
                 ("gps4_14","seals/2007_2008/Staniland_gps4_14_01_08.csv"),
                 ("gps4_21","seals/2007_2008/Staniland_gps4_21_01_08.csv"),
                 ("gps4_28","seals/2007_2008/Staniland_gps4_28_01_08.csv"),
                 ("gps5_01","seals/2007_2008/Staniland_gps5_01_02_08.csv"),
                 ("gps5_05","seals/2007_2008/Staniland_gps5_05_02_08.csv"),
                 ("gps5_14","seals/2007_2008/Staniland_gps5_14_01_08.csv"),
                 ("gps5_17","seals/2007_2008/Staniland_gps5_17_01_08.csv"),
                 ("gps5_21","seals/2007_2008/Staniland_gps5_21_01_08.csv"),
                 ("gps5_28","seals/2007_2008/Staniland_gps5_28_01_08.csv"),
                 ]
    seal_data_years[2010] = [
        ("17","seals/2010_2011/AFSMai.17.csv"),
        ("18","seals/2010_2011/AFSMai.18.csv"),
        ("19","seals/2010_2011/AFSMai.19.csv"),
        ("20","seals/2010_2011/AFSMai.20.csv"),
        ("21","seals/2010_2011/AFSMai.21.csv"),
        ("22","seals/2010_2011/AFSMai.22.csv"),
        ("24","seals/2010_2011/AFSMai.24.csv"),
        ("25","seals/2010_2011/AFSMai.25.csv"),
        ("26","seals/2010_2011/AFSMai.26.csv"),
        ("27","seals/2010_2011/AFSMai.27.csv"),
        ("28","seals/2010_2011/AFSMai.28.csv"),
        ("29","seals/2010_2011/AFSMai.29.csv"),
        ("30","seals/2010_2011/AFSMai.30.csv"),
        ]


    seals = {}
    for y in seal_data_years:
        i = 0
        for (n,f) in seal_data_years[y]:
            seals[n] = seal.c_seal(f)
            seals[n].color = glow_colors[i*30/len(seal_data_years[y])]
            seals[n].year = y
            i+=1
            pass
        pass
    for k in seals:
        seals[k].load()
        pass

    obj = opengl_obj.c_opengl_obj()

    draft = False
    texture_filename = "earth_ico2048.png"
    subdivide = 5
    if draft:
        texture_filename = "earth_ico256.png"
        subdivide = 4
    obj.create_icosphere(subdivide=subdivide)

    og = c_view_obj(obj=obj,
                    seals=seals,
                    texture_filename=texture_filename,
                    window_size=(1200,1200))
    og.init_opengl()
    og.seal_hack = True
    og.camera["fov"] = 3

    og.zFar = 100.0
    #og.create_menus(menus)
    #og.attach_menu("main_menu")
    og.main_loop()

#f Main
import seal
if __name__ == '__main__':
    test_object()
