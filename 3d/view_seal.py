#!/usr/bin/env python
# PYTHONPATH=`pwd`/../python:$PYTHONPATH ./view_obj.py

#a Imports
from gjslib.graphics import opengl_app, opengl_utils, opengl_obj, opengl_window, opengl_widget, opengl_layout
from gjslib.math import quaternion

import math
from OpenGL.GLUT import *
from OpenGL.GLU import *
from OpenGL.GL import *
import OpenGL.arrays.vbo as vbo
import numpy
import datetime

#a Globals
import os, os.path
gjslib_data_dir = os.path.abspath(os.curdir)+"/../../gjslib_data/"
seal_data_dir = gjslib_data_dir+"seals/"
texture_dir   = gjslib_data_dir+"icosphere/"
font_dir = gjslib_data_dir+"fonts/"

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
        self.years = {2005:False, 2006:True, 2007:True, 2009:True, 2010:True, 2011:True, 2012:True}
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
        q = quaternion.c_quaternion(euler=(0,lat,lon),degrees=True)
        xyz = q.get_matrixn(order=3).apply((0,0,1.01))
        return (-xyz[2],xyz[1],xyz[0])
    #f seal_trail
    def seal_trail(self,seal):
        s = self.seals[seal]
        vertices = []
        for d in s.data:
            vertices.extend(self.ll_to_xyz(d[1],d[2]))
            vertices.extend(self.ll_to_xyz(d[1],d[2]))
            pass
        if len(vertices)==0:
            print "Argh, seal has no vertices, will abort",seal
            return
        vertices.pop(0)
        vertices.pop(0)
        vertices.pop(0)
        vertices.pop()
        vertices.pop()
        vertices.pop()
        self.seal_trails[seal] = {"vectors":vbo.VBO(data=numpy.array(vertices, dtype=numpy.float32), target=GL_ARRAY_BUFFER ),
                                  "nvertices":len(vertices)/3,
                                  }
        pass
    #f line_of_latitude
    def line_of_latitude(self,lat,n=180):
        vertices = []
        for i in range(n+1):
            l = (360.0*i/n)
            vertices.extend(self.ll_to_xyz(lat,l))
            vertices.extend(self.ll_to_xyz(lat,l))
            pass
        vertices.pop(0)
        vertices.pop(0)
        vertices.pop(0)
        vertices.pop()
        vertices.pop()
        vertices.pop()
        self.decorations["lat%s"%lat] = {"vectors":vbo.VBO(data=numpy.array(vertices, dtype=numpy.float32), target=GL_ARRAY_BUFFER ),
                                         "nvertices":len(vertices)/3,
                                         }
        pass
    #f line_of_longitude
    def line_of_longitude(self,lon,n=180):
        vertices = []
        for i in range(n+1):
            l = (360.0*i/n)
            vertices.extend(self.ll_to_xyz(l,lon))
            vertices.extend(self.ll_to_xyz(l,lon))
            pass
        vertices.pop(0)
        vertices.pop(0)
        vertices.pop(0)
        vertices.pop()
        vertices.pop()
        vertices.pop()
        self.decorations["lon%s"%lon] = {"vectors":vbo.VBO(data=numpy.array(vertices, dtype=numpy.float32), target=GL_ARRAY_BUFFER ),
                                         "nvertices":len(vertices)/3,
                                         }
        pass
    #f opengl_post_init
    def opengl_post_init(self):
        self.load_font(font_dir+"monospace")
        self.hud = opengl_window.c_opengl_window(og=self, wh=(self.window_size[0],self.window_size[1]), autoclear="depth", layout_class=opengl_layout.c_opengl_layout_place)
        self.hud_text_info = opengl_widget.c_opengl_simple_text_widget(og=self, xyz=(0,0,0))
        self.hud_text_info.background_color = None
        self.hud_text_info.border = None
        self.hud_text_info.margin = None
        self.hud_text_info.padding = None
        self.hud_text_info.replace_text("LOTS OF BLAHLOTS OF BLAHLOTS OF BLAH", scale=(0.3,0.3))
        self.hud.add_widget(self.hud_text_info)
        self.hud.background_color = None
        self.hud.layout()
        self.texture = opengl_utils.texture_from_png(self.texture_filename)
        self.obj.create_opengl_surface()
        for s in self.seals:
            self.seal_trail(s)
            pass
        self.decorations = {}
        for l in (0,15,30,45,60,75):
            self.line_of_latitude(lat=l)
            self.line_of_longitude(lon=l)
            if l==0:
                self.line_of_latitude(lat=-0.1)
                self.line_of_longitude(lon=-0.1)
                pass
            else:
                self.line_of_latitude(lat=-l)
                self.line_of_longitude(lon=-l)
                pass
            pass
        self.camera["facing"] = quaternion.c_quaternion(euler=(-156.3232,21.7793,-30.0554),degrees=True)
        # (0 to 90) 0 0 is polar
        #self.camera["facing"] = quaternion.c_quaternion(euler=(0,0,0),degrees=True)
        # 0,90,0 is focused on lat/lon 0,0 but north pole is on the left
        #self.camera["facing"] = quaternion.c_quaternion(euler=(0,90,0),degrees=True)
        # -90,90,0 is focused on lat/lon 0,0  with north pole up
        #self.camera["facing"] = quaternion.c_quaternion(euler=(-90,90,0),degrees=True)
        # (0,0,30) multiply (-90,90,0) is focused on lat/lon 30,0  with north pole up
        #self.camera["facing"] = quaternion.c_quaternion(euler=(0,0,30),degrees=True).multiply(quaternion.c_quaternion(euler=(-90,90,0),degrees=True))
        # (0,30,0) multiply (-90,90,0) is focused on lat/lon 0,30  with north pole up
        #self.camera["facing"] = quaternion.c_quaternion(euler=(0,30,0),degrees=True).multiply(quaternion.c_quaternion(euler=(-90,90,0),degrees=True))
        # (0,0,30) multiply (0,30,0) multiply (-90,90,0) is focused on lat/lon 30,30  with north pole up
        #self.camera["facing"] = quaternion.c_quaternion(euler=(0,0,30),degrees=True).multiply(quaternion.c_quaternion(euler=(0,30,0),degrees=True).multiply(quaternion.c_quaternion(euler=(-90,90,0),degrees=True)))
        # (0,0,30) multiply (0,10,0) multiply (-90,90,0) is focused on lat/lon 30,10  with north pole up
        # self.camera["facing"] = quaternion.c_quaternion(euler=(0,0,30),degrees=True).multiply(quaternion.c_quaternion(euler=(0,10,0),degrees=True).multiply(quaternion.c_quaternion(euler=(-90,90,0),degrees=True)))
        # (0,0,lat) multiply (0,lon,0) multiply (-90,90,0) is focused on lat,lon  with north pole up
        self.camera["facing"] = quaternion.c_quaternion(euler=(0,0,-54.00),degrees=True).multiply(quaternion.c_quaternion(euler=(0,38.05,0),degrees=True).multiply(quaternion.c_quaternion(euler=(-90,90,0),degrees=True)))
        #self.camera["facing"] = quaternion.c_quaternion(euler=(-90,90,0),degrees=True)
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
        print "Min:",datetime.datetime.utcfromtimestamp(min_t).strftime("%H:%M:%S %d/%m/%y")
        print "Max:",datetime.datetime.utcfromtimestamp(max_t).strftime("%H:%M:%S %d/%m/%y")
        pass
    #f keypress
    def keypress(self, key,m,x,y):
        year_keys = {"2":None,
                     "3":2005,
                     "4":2006,
                     "5":2007,
                     "6":2009,
                     "7":2010,
                     "8":2011,
                     "9":2012,
                     }
        if key in ["1"]:
            print self.camera
            print key
            return True
        if key in year_keys:
            self.select_years(year_keys[key])
            return True
        return opengl_app.c_opengl_camera_app.keypress(self, key,m,x,y)
    #f display
    def display(self):
        opengl_app.c_opengl_camera_app.display(self, show_crosshairs=True,
                                               focus_xxyyzz=(0,0, 0,0, 0,-10))
        self.display_time = max(self.display_min_time, self.display_time)
        if self.display_time>self.display_max_time: self.display_time=self.display_min_time
        self.display_time += 600
        hud_text = datetime.datetime.utcfromtimestamp(self.display_time).strftime("%H:%M:%S %d/%m/%y")

        self.yyy += 0.03
        color = [0.5,0,0.,0.,1.]

        self.matrix_push()
        brightness = 0.4

        self.matrix_push()
        self.matrix_scale(4)

        self.shader_use("color_standard")
        self.matrix_use()

        for d in self.decorations:
            self.decorations[d]["vectors"].bind()
            self.shader_set_attributes( t=3, v=0, C=(1.0,1.0,1.0) )
            glDrawArrays(GL_LINES,0,self.decorations[d]["nvertices"])
            self.decorations[d]["vectors"].unbind()
            pass

        for seal in self.seals:
            if self.years[self.seals[seal].year]:
                self.seal_trails[seal]["vectors"].bind()
                self.matrix_use() # because draw_simple_object messes with the matrix in the shader
                self.shader_set_attributes( t=3, v=0, C=self.seals[seal].color )
                glDrawArrays(GL_LINES,0,self.seal_trails[seal]["nvertices"])
                self.seal_trails[seal]["vectors"].unbind()
                n = self.seals[seal].data_at_time(self.display_time)
                xyz = self.seal_xyz(seal,n)
                self.draw_simple_object("cross", self.seals[seal].color, xyz, 0.0003, 5*self.yyy)
                pass
            pass

        self.shader_use("texture_standard")
        glBindTexture(GL_TEXTURE_2D, self.texture)
        self.matrix_use()
        self.obj.draw_opengl_surface(self)
        self.matrix_pop()
        self.matrix_pop()

        self.hud_text_info.replace_text(hud_text, scale=(0.3,0.3))        
        self.hud.display()

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
    seal_data_years[2005] = [("7345","2005_2006/10W7345.csv"),
                 ("7313","2005_2006/11W7313.csv"),
                 ("7316","2005_2006/11W7316.csv"),
                 ("7346","2005_2006/11W7346.csv"),
                 ("7344","2005_2006/20W7344.csv"),
                 ("7310","2005_2006/3W7310.csv"),
                 ("7309","2005_2006/W7309.csv"),
                             ]
    seal_data_years[2006] = [
                 ("6703","2006_2007/W6703gps3_v3.csv"),
                 ("7162","2006_2007/W7162gps1_RTP.csv"),
                 ("7368","2006_2007/W7368gps5.csv"),
                 ("7381","2006_2007/W7381gps3.csv"),
                 ("7387","2006_2007/W7387gps5.csv"),
                 ("7391","2006_2007/W7391gps3_v3.csv"),
                 ("7392","2006_2007/W7392gps5.csv"),
                 ("7393","2006_2007/W7393gps3_RTP.csv"),
                 ("7412","2006_2007/W7412gps1_RTP.csv"),
                 ("7416","2006_2007/W7416gps1_RTP.csv"),
                 ]
    seal_data_years[2007] = [
                 ("gps1_16","2007_2008/Staniland_gps1_16_01_08.csv"),
                 ("gps1_20","2007_2008/Staniland_gps1_20_01_08.csv"),
                 ("gps1_23","2007_2008/Staniland_gps1_23_01_08.csv"),
                 ("gps1_31","2007_2008/Staniland_gps1_31_01_08.csv"),
                 ("gps2_08","2007_2008/Staniland_gps2_08_02_08.csv"),
                 ("gps2_13","2007_2008/Staniland_gps2_13_01_08.csv"),
                 ("gps2_18","2007_2008/Staniland_gps2_18_01_08.csv"),
                 ("gps2_25","2007_2008/Staniland_gps2_25_01_08.csv"),
                 ("gps2_31","2007_2008/Staniland_gps2_31_01_08.csv"),
                 ("gps4_01","2007_2008/Staniland_gps4_01_02_08.csv"),
                 ("gps4_07","2007_2008/Staniland_gps4_07_02_08.csv"),
                 ("gps4_14","2007_2008/Staniland_gps4_14_01_08.csv"),
                 ("gps4_21","2007_2008/Staniland_gps4_21_01_08.csv"),
                 ("gps4_28","2007_2008/Staniland_gps4_28_01_08.csv"),
                 ("gps5_01","2007_2008/Staniland_gps5_01_02_08.csv"),
                 ("gps5_05","2007_2008/Staniland_gps5_05_02_08.csv"),
                 ("gps5_14","2007_2008/Staniland_gps5_14_01_08.csv"),
                 ("gps5_17","2007_2008/Staniland_gps5_17_01_08.csv"),
                 ("gps5_21","2007_2008/Staniland_gps5_21_01_08.csv"),
                 ("gps5_28","2007_2008/Staniland_gps5_28_01_08.csv"),
                 ]
    seal_data_years[2010] = [
        ("17","2010_2011/AFSMai.17.csv"),
        ("18","2010_2011/AFSMai.18.csv"),
        ("19","2010_2011/AFSMai.19.csv"),
        ("20","2010_2011/AFSMai.20.csv"),
        ("21","2010_2011/AFSMai.21.csv"),
        ("22","2010_2011/AFSMai.22.csv"),
        ("24","2010_2011/AFSMai.24.csv"),
        ("25","2010_2011/AFSMai.25.csv"),
        ("26","2010_2011/AFSMai.26.csv"),
        ("27","2010_2011/AFSMai.27.csv"),
        ("28","2010_2011/AFSMai.28.csv"),
        ("29","2010_2011/AFSMai.29.csv"),
        ("30","2010_2011/AFSMai.30.csv"),
        ]
    seal_data_years[2009] = [
        ("AFSMai_1","2009_2010/AFSMai_1.csv"),
        ("AFSMai_10","2009_2010/AFSMai_10.csv"),
        ("AFSMai_11","2009_2010/AFSMai_11.csv"),
        ("AFSMai_12","2009_2010/AFSMai_12.csv"),
        ("AFSMai_13","2009_2010/AFSMai_13.csv"),
        ("AFSMai_14","2009_2010/AFSMai_14.csv"),
        ("AFSMai_15","2009_2010/AFSMai_15.csv"),
        ("AFSMai_16","2009_2010/AFSMai_16.csv"),
        ("AFSMai_2","2009_2010/AFSMai_2.csv"),
        ("AFSMai_3","2009_2010/AFSMai_3.csv"),
        ("AFSMai_4","2009_2010/AFSMai_4.csv"),
        ("AFSMai_5","2009_2010/AFSMai_5.csv"),
        ("AFSMai_6","2009_2010/AFSMai_6.csv"),
        ("AFSMai_7","2009_2010/AFSMai_7.csv"),
        ("AFSMai_8","2009_2010/AFSMai_8.csv"),
        ("AFSMai_9","2009_2010/AFSMai_9.csv"),
        ("WH10tagx4.csv","2009_2010/WH10tagx4.csv"),
        ("WH11tag8.csv","2009_2010/WH11tag8.csv"),
        ("WH12tag4.csv","2009_2010/WH12tag4.csv"),
        ("WH13tag6.csv","2009_2010/WH13tag6.csv"),
        ("WH14tag7.csv","2009_2010/WH14tag7.csv"),
        ("WH15tag5.csv","2009_2010/WH15tag5.csv"),
        ("WH16tag8.csv","2009_2010/WH16tag8.csv"),
        ("WH17tag4.csv","2009_2010/WH17tag4.csv"),
        ("WH18tagx4.csv","2009_2010/WH18tagx4.csv"),
        ("WH19tag10.csv","2009_2010/WH19tag10.csv"),
        ("WH1tag09.csv","2009_2010/WH1tag09.csv"),
        ("WH2tag04.csv","2009_2010/WH2tag04.csv"),
        ("WH3tag06.csv","2009_2010/WH3tag06.csv"),
        ("WH6tag11.csv","2009_2010/WH6tag11.csv"),
        ("WH7tag8.csv","2009_2010/WH7tag8.csv"),
        ("WH8tag7.csv","2009_2010/WH8tag7.csv"),
        ("WH9tag5.csv","2009_2010/WH9tag5.csv"),
        ]
    seal_data_years[2011] = [
        ("W8253","2011_2012/W8253_110112.csv"),
        ("W8254","2011_2012/W8254_150112.csv"),
        ("W8257","2011_2012/W8257_140112.csv"),
        ("W8288","2011_2012/W8288_290212.csv"),
        ("W8553","2011_2012/W8553_190112.csv"),
        ("W8554","2011_2012/W8554_220112.csv"),
        ("W8555","2011_2012/W8555_250112.csv"),
        ("W8556","2011_2012/W8556_280112.csv"),
        ("W8557","2011_2012/W8557_020212.csv"),
        ("W8558","2011_2012/W8558_100212.csv"),
        ("W8559","2011_2012/W8559_110212.csv"),
        ("W8560","2011_2012/W8560_200212.csv"),
        ("W8561","2011_2012/W8561_180212.csv"),
        ("W8562","2011_2012/W8562_260212.csv"),
        ]
    seal_data_years[2012] = [
        ("ATP01_01","2012_2013/ATP01_01_030113.csv"),
        ("ATP01_02","2012_2013/ATP01_02_150113.csv"),
        ("ATP01_03","2012_2013/ATP01_03_310113.csv"),
        ("ATP01_04","2012_2013/ATP01_04_160213.csv"),
        ("ATP01_05","2012_2013/ATP01_05_280213.csv"),
        ("ATP01_06","2012_2013/ATP01_06_160313.csv"),
        ("ATP01_07","2012_2013/ATP01_07_290313.csv"),
        ("ATP03_01","2012_2013/ATP03_01_030113.csv"),
        ("ATP03_02","2012_2013/ATP03_02_150113.csv"),
        ("ATP03_03","2012_2013/ATP03_03_310113.csv"),
        ("ATP03_04","2012_2013/ATP03_04_160213.csv"),
        ("ATP03_05","2012_2013/ATP03_05_240213.csv"),
        ("ATP03_06","2012_2013/ATP03_06_120313.csv"),
        ("ATP05_01","2012_2013/ATP05_01_250213.csv"),
        ("ATP05_02","2012_2013/ATP05_02_130313.csv"),
        ("ATP05_03","2012_2013/ATP05_03_270313.csv"),
        ("ATP05_04","2012_2013/ATP05_04_060413.csv"),
        ("ATP06_01","2012_2013/ATP06_01_040113.csv"),
        ("ATP06_02","2012_2013/ATP06_02_160113.csv"),
        ("ATP06_03","2012_2013/ATP06_03_010213.csv"),
        ("ATP06_04","2012_2013/ATP06_04_170213.csv"),
        ("ATP06_05","2012_2013/ATP06_05_250213.csv"),
        ("ATP06_06","2012_2013/ATP06_06_130313.csv"),
        ("ATP06_07","2012_2013/ATP06_07_250313.csv"),
        ("ATP07_01","2012_2013/ATP07_01_050113.csv"),
        ("ATP07_02","2012_2013/ATP07_02_170113.csv"),
        ("ATP07_03","2012_2013/ATP07_03_020213.csv"),
        ("ATP07_04","2012_2013/ATP07_04_180213.csv"),
        ("ATP07_05","2012_2013/ATP07_05_260213.csv"),
        ("ATP07_06","2012_2013/ATP07_06_140313.csv"),
        ("ATP07_07","2012_2013/ATP07_07_300313.csv"),
        ("ATP07_08","2012_2013/ATP07_08_070413.csv"),
        ("ATP08_01","2012_2013/ATP08_01_050113.csv"),
        ("ATP08_02","2012_2013/ATP08_02_170113.csv"),
        ("ATP08_03","2012_2013/ATP08_03_020213.csv"),
        ("ATP08_04","2012_2013/ATP08_04_180213.csv"),
        ("ATP08_05","2012_2013/ATP08_05_260213.csv"),
        ("ATP08_06","2012_2013/ATP08_06_020313.csv"),
        ("ATP08_08","2012_2013/ATP08_08_240313.csv"),
        ("ATP09_01","2012_2013/ATP09_01_090113.csv"),
        ("ATP09_02","2012_2013/ATP09_02_250113.csv"),
        ("ATP09_03","2012_2013/ATP09_03_100213.csv"),
        ("ATP09_04","2012_2013/ATP09_04_260213.csv"),
        ("ATP09_05","2012_2013/ATP09_05_140313.csv"),
        ("ATP09_06","2012_2013/ATP09_06_040413.csv"),
        ("ATP10_01","2012_2013/ATP10_01_291212.csv"),
        ("ATP11_01","2012_2013/ATP11_01_160113.csv"),
        ("ATP12_01","2012_2013/ATP12_01_260113.csv"),
        ("ATP12_02","2012_2013/ATP12_02_110213.csv"),
        ("ATP12_03","2012_2013/ATP12_03_270213.csv"),
        ("ATP12_04","2012_2013/ATP12_04_070313.csv"),
        ("ATP13_01","2012_2013/ATP13_01_281212.csv"),
        ("ATP15_01","2012_2013/ATP15_01_070113.csv"),
        ("ATP15_02","2012_2013/ATP15_02_230113.csv"),
        ("ATP15_03","2012_2013/ATP15_03_080213.csv"),
        ("ATP15_04","2012_2013/ATP15_04_240213.csv"),
        ("ATP15_05","2012_2013/ATP15_05_120313.csv"),
        ("ATP16_01","2012_2013/ATP16_01_070113.csv"),
        ("ATP16_02","2012_2013/ATP16_02_230113.csv"),
        ("ATP16_03","2012_2013/ATP16_03_080213.csv"),
        ("ATP16_04","2012_2013/ATP16_04_120313.csv"),
        ("ATP16_06","2012_2013/ATP16_06_280313.csv"),
        ("ATP18_01","2012_2013/ATP18_01_311212.csv"),
        ("ATP19_01","2012_2013/ATP19_01_160113.csv"),
        ("ATP19_02","2012_2013/ATP19_02_010213.csv"),
        ("ATP19_03","2012_2013/ATP19_03_170213.csv"),
        ("ATP19_04","2012_2013/ATP19_04_250213.csv"),
        ("ATP19_05","2012_2013/ATP19_05_130313.csv"),
        ("ATP19_06","2012_2013/ATP19_06_250313.csv"),
        ("ATP19_07","2012_2013/ATP19_07_060413.csv"),
        ("ATP20_01","2012_2013/ATP20_01_170113.csv"),
        ("ATP20_02","2012_2013/ATP20_02_020213.csv"),
        ("ATP20_03","2012_2013/ATP20_03_180213.csv"),
        ("ATP20_04","2012_2013/ATP20_04_260213.csv"),
        ("ATP20_05","2012_2013/ATP20_05_140313.csv"),
        ("ATP21_01","2012_2013/ATP21_01_170113.csv"),
        ("ATP21_02","2012_2013/ATP21_02_020213.csv"),
        ("ATP21_03","2012_2013/ATP21_03_180213.csv"),
        ("ATP21_04","2012_2013/ATP21_04_260213.csv"),
        ("ATP21_05","2012_2013/ATP21_05_140313.csv"),
        ("ATP21_06","2012_2013/ATP21_06_050413.csv"),
        ("ATP21_07","2012_2013/ATP21_07_150413.csv"),
        ("ATP21_08","2012_2013/ATP21_08_190413.csv"),
        ("ATP23_01","2012_2013/ATP23_01_150113.csv"),
        ("ATP23_02","2012_2013/ATP23_02_310113.csv"),
        ("ATP23_03","2012_2013/ATP23_03_160213.csv"),
        ("ATP23_04","2012_2013/ATP23_04_250213.csv"),
        ("ATP23_05","2012_2013/ATP23_05_120313.csv"),
        ("ATP23_06","2012_2013/ATP23_06_010413.csv"),
        ("ATP24_01","2012_2013/ATP24_01_280113.csv"),
        ("ATP24_02","2012_2013/ATP24_02_130213.csv"),
        ("ATP24_03","2012_2013/ATP24_03_250213.csv"),
        ("ATP24_04","2012_2013/ATP24_04_130313.csv"),
        ("ATP24_05","2012_2013/ATP24_05_170313.csv"),
        ("ATP24_06","2012_2013/ATP24_06_250313.csv"),
        ("ATP24_07","2012_2013/ATP24_07_060413.csv"),
        ("ATP24_08","2012_2013/ATP24_08_150413.csv"),
        ("ATP24_09","2012_2013/ATP24_09_190413.csv"),
        ("ATP26_01","2012_2013/ATP26_01_260213.csv"),
        ("ATP26_02","2012_2013/ATP26_02_140313.csv"),
        ("ATP26_03","2012_2013/ATP26_03_050413.csv"),
        ("ATP28_01","2012_2013/ATP28_01_170113.csv"),
        ("ATP28_02","2012_2013/ATP28_02_020213.csv"),
        ("ATP28_03","2012_2013/ATP28_03_180213.csv"),
        ("ATP28_04","2012_2013/ATP28_04_260213.csv"),
        ("ATP28_05","2012_2013/ATP28_05_140313.csv"),
        ("ATP28_06","2012_2013/ATP28_06_280313.csv"),
        ("ATP28_07","2012_2013/ATP28_07_070413.csv"),
        ("ATP29_01","2012_2013/ATP29_01_170113.csv"),
        ("ATP29_02","2012_2013/ATP29_02_220113.csv"),
        ("ATP30_01","2012_2013/ATP30_01_180113.csv"),
        ("ATP30_02","2012_2013/ATP30_02_030213.csv"),
        ("ATP30_03","2012_2013/ATP30_03_190213.csv"),
        ("ATP30_04","2012_2013/ATP30_04_270213.csv"),
        ("ATP30_05","2012_2013/ATP30_05_150313.csv"),
        ("ATP30_06","2012_2013/ATP30_06_280313.csv"),
        ("ATP31_01","2012_2013/ATP31_01_260213.csv"),
        ("ATP31_02","2012_2013/ATP31_02_150313.csv"),
        ("ATP31_03","2012_2013/ATP31_03_260313.csv"),
        ("ATP32_01","2012_2013/ATP32_01_260113.csv"),
        ("ATP32_02","2012_2013/ATP32_02_110213.csv"),
        ("ATP32_03","2012_2013/ATP32_03_230213.csv"),
        ("ATP32_05","2012_2013/ATP32_05_080313.csv"),
        ("ATP33_01","2012_2013/ATP33_01_190113.csv"),
        ("ATP33_02","2012_2013/ATP33_02_040213.csv"),
        ("ATP33_03","2012_2013/ATP33_03_200213.csv"),
        ("ATP33_04","2012_2013/ATP33_04_240213.csv"),
        ("ATP33_05","2012_2013/ATP33_05_120313.csv"),
        ("ATP33_06","2012_2013/ATP33_06_280313.csv"),
        ("ATP34_01","2012_2013/ATP34_01_190113.csv"),
        ("ATP34_02","2012_2013/ATP34_02_040213.csv"),
        ("ATP34_03","2012_2013/ATP34_03_200213.csv"),
        ("ATP34_04","2012_2013/ATP34_04_240213.csv"),
        ("ATP34_05","2012_2013/ATP34_05_120313.csv"),
        ("ATP34_06","2012_2013/ATP34_06_290313.csv"),
        ("ATP36_01","2012_2013/ATP36_01_200113.csv"),
        ("ATP36_02","2012_2013/ATP36_02_050213.csv"),
        ("ATP36_03","2012_2013/ATP36_03_200213.csv"),
        ("ATP36_04","2012_2013/ATP36_04_250213.csv"),
        ("ATP36_05","2012_2013/ATP36_05_130313.csv"),
        ("ATP37_01","2012_2013/ATP37_01_280113.csv"),
        ("ATP37_02","2012_2013/ATP37_02_130213.csv"),
        ("ATP37_03","2012_2013/ATP37_03_250213.csv"),
        ("ATP37_04","2012_2013/ATP37_04_130313.csv"),
        ("ATP37_05","2012_2013/ATP37_05_250313.csv"),
        ("ATP37_06","2012_2013/ATP37_06_060413.csv"),
        ("ATP38_01","2012_2013/ATP38_01_240113.csv"),
        ("ATP38_02","2012_2013/ATP38_02_030213.csv"),
        ("ATP40_01","2012_2013/ATP40_01_260113.csv"),
        ("ATP40_02","2012_2013/ATP40_02_110213.csv"),
        ("ATP40_03","2012_2013/ATP40_03_270213.csv"),
        ("ATP40_04","2012_2013/ATP40_04_170313.csv"),
        ("ATP40_05","2012_2013/ATP40_05_290313.csv"),
        ("ATP40_06","2012_2013/ATP40_06_080413.csv"),
        ("ATP43_01","2012_2013/ATP43_01_010313.csv"),
        ("ATP43_02","2012_2013/ATP43_02_170313.csv"),
        ("ATP43_03","2012_2013/ATP43_03_290313.csv"),
        ("ATP43_04","2012_2013/ATP43_04_100413.csv"),
        ("ATP44_01","2012_2013/ATP44_01_240113.csv"),
        ("ATP44_02","2012_2013/ATP44_02_090213.csv"),
        ("ATP44_03","2012_2013/ATP44_03_250213.csv"),
        ("ATP44_04","2012_2013/ATP44_04_130313.csv"),
        ("ATP44_05","2012_2013/ATP44_05_250313.csv"),
        ("ATP44_06","2012_2013/ATP44_06_070413.csv"),
        ("ATP44_07","2012_2013/ATP44_07_160413.csv"),
        ("ATP46_01","2012_2013/ATP46_01_240113.csv"),
        ("ATP46_02","2012_2013/ATP46_02_090213.csv"),
        ("ATP46_03","2012_2013/ATP46_03_250213.csv"),
        ("ATP46_04","2012_2013/ATP46_04_130313.csv"),
        ("ATP46_05","2012_2013/ATP46_05_250313.csv"),
        ("ATP46_06","2012_2013/ATP46_06_070413.csv"),
        ("ATP47_01","2012_2013/ATP47_01_150313.csv"),
        ("ATP47_02","2012_2013/ATP47_02_310313.csv"),
        ("ATP47_03","2012_2013/ATP47_03_080413.csv"),
        ("W8940","2012_2013/W8940_01_170313.csv"),
        ("W8944","2012_2013/W8944_01_140313.csv"),
        ("W8945","2012_2013/W8945_01_080313.csv"),
        ("W8946","2012_2013/W8946_01_260313.csv"),
        ("W8947","2012_2013/W8947_01_080413.csv"),
        ("W8948","2012_2013/W8948_01_050313.csv"),
        ("W8951","2012_2013/W8951_01_100313.csv"),
        ("W8955","2012_2013/W8955_01_160313.csv"),
        ("W8960","2012_2013/W8960_01_110313.csv"),
        ("W8965","2012_2013/W8965_01_260313.csv"),
        ("W8967","2012_2013/W8967_01_280313.csv"),
        ("W8969","2012_2013/W8969_01_060313.csv"),
        ("W8970","2012_2013/W8970_01_060313.csv"),
        ("W8973","2012_2013/W8973_01_290313.csv"),
        ("W8975","2012_2013/W8975_01_210313.csv"),
        ("W8976","2012_2013/W8976_01_010313.csv"),
        ("W8983","2012_2013/W8983_01_160313.csv"),
        ("W8985","2012_2013/W8985_01_030313.csv"),
        ("W8986","2012_2013/W8986_01_140313.csv"),
        ]

    seals = {}
    for y in seal_data_years:
        i = 0
        t = len(seal_data_years[y])
        print "Reading seal data for year %d (%d seals)"%(y,t)
        for (n,f) in seal_data_years[y]:
            seals[n] = seal.c_seal(seal_data_dir+f)
            if t>20:
                seals[n].color = glow_colors[i%len(glow_colors)]
            else:
                seals[n].color = glow_colors[i*30/len(seal_data_years[y])]
            seals[n].year = y
            seals[n].load(max_pdop=100)
            i+=1
            if (i%50)==0:
                print "Read seal %d"%i
            pass
        pass
    print "Seal data loaded"
    obj = opengl_obj.c_opengl_obj()

    draft = True
    #draft = False
    texture_filename = "earth_ico2048.png"
    subdivide = 5
    if draft:
        texture_filename = "earth_ico256.png"
        subdivide = 4
    obj.create_icosphere(subdivide=subdivide)

    og = c_view_obj(obj=obj,
                    seals=seals,
                    texture_filename=texture_dir+texture_filename,
                    window_size=(1000,1000))
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
