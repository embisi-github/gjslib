#!/usr/bin/env python
# PYTHONPATH=`pwd`/../python:$PYTHONPATH ./view_obj.py
import gjslib.graphics.obj
import gjslib.graphics.opengl

x = gjslib.graphics.obj.c_obj()
f = open("icosahedron.obj")
x.load_from_file(f)

if __name__ == '__main__': gjslib.graphics.opengl.main()
