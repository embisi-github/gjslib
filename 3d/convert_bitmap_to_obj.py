#!/usr/bin/env python
# PYTHONPATH=`pwd`/../python:$PYTHONPATH ./convert_bitmap_to_obj.py
import gjslib.graphics.obj
from PIL import Image


def convert_bitmap_to_obj(bitmap_name):
    obj = gjslib.graphics.obj.c_obj()
    image = Image.open(bitmap_name+".png")
    f = open(bitmap_name+".obj","w")
    obj.from_bitmap(image,(1.0,0.125,1.0))
    obj.save_to_file(f)
    pass

convert_bitmap_to_obj("mm_plant")
convert_bitmap_to_obj("mm_conveyor")
convert_bitmap_to_obj("mm_sand")
convert_bitmap_to_obj("mm_dirt")
convert_bitmap_to_obj("mm_stalactite")
convert_bitmap_to_obj("mm_robot")
convert_bitmap_to_obj("mm_willy")
