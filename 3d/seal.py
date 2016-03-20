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
    def load(self, max_pdop=10, min_dll=0.0003, max_dll=0.2):
        f=open(self.filename,"r")
        fmt = None
        last_ll = None,None
        for lines in f:
            for line in lines.split("\r"):
                line = line.strip()
                if fmt is None:
                    if line=="Date, Time, Latitude, Longitude, Altitude, Speed, Course, Type, Distance, Essential":
                        fmt = 2012
                    elif line=="Date,Time,Latitute,Longitude,Temperature,Nav State,Altitude,N Velocity,E Velocity,D Velocity,PDOP,SV Count":
                        fmt = 2005
                    elif line in ["Date,Time,Latitude,Longitude,Altitude,Residual Error,Clock Error,Cumulative Clock Error,No Satellites Used,No Satellites Provided",
                                 "Date,Time,Latitude,Longitude,Altitude,Residual Error,Clock Error,Cumulative Clock Error,# Sats Used,# Sats Provided,",
                                 "Date,Time,Latitude,Longitude,Altitude,Residual Error,Clock Error,Cumulative Clock Error,No Sats Used,No Sats Provided",
                                 "Date,Time,Latitude,Longitude,Altitude,Residual Error,Clock Error,Cumulative Clock Error,NoSats Used,No Sats Provided,",
                                 "Date,Time,Latitude,Longitude,Altitude,Residual Error,Clock Error,Cumulative Clock Error,No Sats Used,No Sats Provided,",
                                 "Date,Time,Latitude,Longitude,Altitude,Residual_Error,Clock_Error,Cumulative_Clock_Error,No Sats_Used,No Sats_Provided,",
                                 ]:
                        fmt = 2006
                    elif line in ["Date,Time,Latitude,Longitude,Logger ID,Deployment,Altitude,R-Err,C-Err,Total C-Err,No satellites used,No satellites available,Duplicates,Notes",
                                  "Date,Time,Latitude,Longitude,Logger ID,Deployment,Altitude,R-Err,C-Err,Total C-Err,Sats Used,# Sats,Duplicates,Notes",
                                  ]:
                        fmt = 2010
                    elif line in ["Date,Time,No of satellites used,Latitude,Longitude,Altitude,Clock offset,Accuracy indicator,Battery voltage",
                                  "Date,Time,No satellites used,Latitude,Longitude,Altitude,Clock offset,Accuracy indicator,Battery voltage",
                                  "Date,Time,No of satellites used,Latitude,Longitude,Altitude,Clock offset,Accuracy indicator,Battery indicator",
                                  "Date,Time,No of satellites,Latitude,Longitude,Altitude,Clock offset,Accuracy indicator,Battery voltage",
                                  "Date,Time,No satellites used,Latitude ,Longitude,Altitude,Clock offset,Accuracy indicator,Battery voltage",
                                  ]:
                        fmt = 2011
                    else:
                        print line
                        fmt = "other"
                        pass
                    pass
                d = line.split(",")
                try:
                    if fmt==2012:
                        date,time,lat,lon,pdop,nsat = d[0],d[1],d[2],d[3],0,8
                        pass
                    elif fmt==2005:
                        date,time,lat,lon,pdop,nsat = d[0],d[1],d[2],d[3],int(d[10]),int(d[11])
                        pass
                    elif fmt==2006:
                        date,time,lat,lon,pdop,nsat = d[0],d[1],d[2],d[3],0,int(d[8])
                        pass
                    elif fmt==2010:
                        date,time,lat,lon,pdop,nsat = d[0],d[1],d[2],d[3],0,int(d[10])
                        pass
                    elif fmt==2011:
                        date,time,lat,lon,pdop,nsat = d[0],d[1],d[3],d[4],0,int(d[2])
                        useless = float(d[7])
                        if useless>0.001: continue
                        pass
                    else:
                        # not used now
                        date,time,lat,lon,pdop,nsat = d[0],d[1],d[2],d[3],int(d[8]),0
                        pass
                    if nsat<0 or nsat>20: continue
                    if pdop>max_pdop: continue
                    lat = float(lat)
                    lon = float(lon)
                    if last_ll[0] is not None:
                        dlat = abs(lat-last_ll[0])
                        dlon = abs(lon-last_ll[1])
                        if dlat>max_dll: continue
                        if dlon>max_dll: continue
                        if dlat+dlon<min_dll: continue
                    last_ll = (lat,lon)
                    (day,mon,yr) = date.split("/")
                    (day,mon,yr) = (int(day),int(mon),int(yr))
                    if day>31: (day,mon,yr) = (yr,mon,day) # Reverse ymd if it is backwards...
                    (h,m,s) = time.split(":")[:3]
                    (h,m,s) = (int(h),int(m),int(s))
                    seconds = calendar.timegm(datetime.datetime(yr,mon,day,h,m,s).timetuple())
                    self.data.append((seconds,lat,lon))
                except:
                    pass
                pass
            pass
        #print self.data
        #self.data.sort(cmp=lambda x,y:(x[0]<y[0] and -1) or 1)
        pass
    def get_time_bounds(self):
        #print self.filename
        #print self.data[0][0], self.data[-1][0]
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

