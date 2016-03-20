#!/usr/bin/env python
# PYTHONPATH=`pwd`/../python:$PYTHONPATH ./view_obj.py

#a Imports
import sys

from gjslib.graphics import opengl_app, opengl_utils, opengl_obj

import math
from OpenGL.GLUT import *
from OpenGL.GLU import *
from OpenGL.GL import *

import datetime, calendar

#a c_seal
class c_seal:
    def __init__(self,filename):
        #data is list of lists
        #structure Date,Time,Latitute,Longitude,Temperature,Nav State,Altitude,N Velocity,E Velocity,D Velocity,PDOP,SV Count
        #example line 24/03/2006,09:13:18,-54.008,-38.051,25.5,3,35,0,0,0,1000,0
        # 2011:
        # 17/01/2012, 09:54:23, 0,0,0,0,9999.999, 9999.999,4.12
        # 17/01/2012, 09:54:23, 0,0,X,X,9999.999, 9999.999,4.12
        # 2012:
        # 2012/12/24, 14:39:06, -54.008572, -38.051189, 21.65,  36.00, 27, -2, 0.00, 1
        self.data=[]
        self.filename = filename
        pass
    def load(self, max_pdop=10):
        f=open(self.filename,"r")
        fmt = None
        for lines in f:
            for line in lines.split("\r"):
                line = line.strip()
                if fmt is None:
                    if line=="Date, Time, Latitude, Longitude, Altitude, Speed, Course, Type, Distance, Essential":
                        fmt = 2012
                    else:
                        fmt = "other"
                        pass
                    pass
                d = line.split(",")
                try:
                    if fmt==2012:
                        d = [d[0],d[1],d[2],d[3],d[4],d[5],d[6],d[7],100]
                        pass
                    # 2011 hack
                    try:
                        dint = int(d[2])
                        useless = float(d[7])
                        if dint>=0 and dint<=12 and useless<0.001:
                            d = [d[0],d[1],d[3],d[4],d[5],d[6],0,0,0]
                            pass
                        else:
                            d = []
                        pass
                    except:
                        pass
                    if (len(d)<12):
                        pdop = int(d[8])
                    else:
                        pdop = int(d[10])
                    if pdop>max_pdop: continue
                    d[2] = float(d[2])
                    d[3] = float(d[3])
                    #d[4] = float(d[4])
                    #d[5] = float(d[5])
                    d[6] = float(d[6])
                    (day,mon,yr) = d[0].split("/")
                    (day,mon,yr) = (int(day),int(mon),int(yr))
                    if day>31: (day,mon,yr) = (yr,mon,day)
                    (h,m,s) = d[1].split(":")[:3]
                    (h,m,s) = (int(h),int(m),int(s))
                    seconds = calendar.timegm(datetime.datetime(yr,mon,day,h,m,s).timetuple())
                    self.data.append((seconds,d[2],d[3],d[4],d[5],d[6]))
                except:
                    pass
                pass
            pass
        #self.data.sort(cmp=lambda x,y:(x[0]<y[0] and -1) or 1)
        pass
    def get_time_bounds(self):
        print self.filename
        print self.data[0][0], self.data[-1][0]
        return self.data[0][0], self.data[-1][0]
    def data_at_time(self, t):
        at_or_after=0
        at_or_before=len(self.data)-1
        if at_or_after==at_or_before: return at_or_before
        while True:
            m = (at_or_after + at_or_before)/2
            if self.data[m][0]==t: return m
            if (m==at_or_after):
                return m+1
            if t>self.data[m][0]:
                at_or_after = m
                pass
            else:
                at_or_before = m
                pass
            pass
        pass
    def show(self,start=0,max=20):
        for d in self.data[start:max]:
            print d
            pass
        pass

if __name__=="__main__":
    x = c_seal(sys.argv[1])
    x.load()
    print len(x.data)
    x.show(max=10)
    x.show(start=-10,max=-1)

