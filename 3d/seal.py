#!/usr/bin/env python
# PYTHONPATH=`pwd`/../python:$PYTHONPATH ./view_obj.py

#a Imports
import sys

from gjslib.graphics import opengl_app, opengl_utils, opengl_obj

import math
from OpenGL.GLUT import *
from OpenGL.GLU import *
from OpenGL.GL import *

import datetime
#a c_seal
class c_seal:
    def __init__(self,filename):
        #data is list of lists
        #structure Date,Time,Latitute,Longitude,Temperature,Nav State,Altitude,N Velocity,E Velocity,D Velocity,PDOP,SV Count
        #example line 24/03/2006,09:13:18,-54.008,-38.051,25.5,3,35,0,0,0,1000,0
        self.data=[]
        self.filename = filename
        pass
    def load(self, max_pdop=10):
        f=open(self.filename,"r")
        for line in f:
            line = line.strip()
            d = line.split(",")
            try:
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
                (day,m,y) = d[0].split("/")
                (day,m,y) = (int(day),int(m),int(y))
                seconds = datetime.date(y,m,day).toordinal()*24*60*60
                (h,m,s) = d[1].split(":")[:3]
                (h,m,s) = (int(h),int(m),int(s))
                seconds += h*60*60+m*60+s
                self.data.append((seconds,d[2],d[3],d[4],d[5],d[6]))
            except:
                pass
            pass
        #self.data.sort(cmp=lambda x,y:(x[0]<y[0] and -1) or 1)
        pass
    def get_time_bounds(self):
        print self.filename, self.data[0][0], self.data[-1][0]
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

