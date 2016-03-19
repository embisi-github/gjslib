#!/usr/bin/env python

#a Imports
from OpenGL.GLUT import *
from OpenGL.GLU import *
from OpenGL.GL import *
from gjslib.graphics import opengl_utils

#a Layout classes
#c c_opengl_layout
class c_opengl_layout(object):
    """
    A simple placed-layout geometry
    There is no intelligence here - whatever the children are added with is what they get
    """
    #f __init__
    def __init__(self, widget, **kwargs):
        self.widget = widget
        # Must set:
        #self.widget.display_iter  = self.contents.__iter__
        #self.widget.interact_iter = self.contents.reverse
        pass
    #f add_widget
    def add_widget(self, widget, **kwargs):
        """
        Add a widget to the layout, with relevant parameters
        """
        pass
    #f get_content_bbox
    def get_content_bbox(self):
        """
        Return (xxyyzz) for the contents' minimum layout
        """
        return (0,0, 0,0, 0,0)
    #f set_content_bbox
    def set_content_bbox(self):
        """
        Set the content bbox
        """
        return
    #f All done
    pass

#c c_opengl_layout_place
class c_opengl_layout_place(c_opengl_layout):
    """
    A simple placed-layout geometry
    There is no intelligence here - whatever the children are added with is what they get
    """
    #f __init__
    def __init__(self, widget, **kwargs):
        c_opengl_layout.__init__(self, widget, **kwargs)
        self.contents = []
        self.widget.children = self.contents
        self.widget.display_iter  = lambda: [c[0] for c in self.contents]
        self.widget.interact_iter = lambda: [c[0] for c in self.contents]
        pass
    #f add_widget
    def add_widget(self, widget, xyz=(0,0,0), **kwargs):
        #xxyyzz = opengl_utils.xxyyzz_from_xyz_pair(xyz,(0,0,0))
        self.contents.append( [widget, xyz, (0,0,0)] )
        pass
    #f get_content_bbox
    def get_content_bbox(self):
        """
        Get the content bbox based on the content size and the placed xyz
        Each content bbox is deemed to be in the same units as the layout widget units
        This is called by the widget containing the layout to determine the bbox of
        the widget (by adding borders etc)
        """
        xxyyzz = (None,None,None,None,None,None)
        for c in self.contents:
            (w,xyz,_) = c
            (w_xxyyzz, w_e) = w.get_minimum_bbox()
            whd = opengl_utils.whd_from_xxyyzz(w_xxyyzz)
            c[2] = whd
            w_xxyyzz = opengl_utils.xxyyzz_from_xyz_whd(xyz,whd)
            xxyyzz = opengl_utils.xxyyzz_minmax(xxyyzz, w_xxyyzz)
            pass
        return xxyyzz
    #f set_content_bbox
    def set_content_bbox(self, xxyyzz):
        """
        Set the content bbox
        """
        for (w,xyz,whd) in self.contents:
            w_xxyyzz = opengl_utils.xxyyzz_from_xyz_whd(xyz,whd)
            w.set_bbox(w_xxyyzz)
            pass
        pass
    #f layout
    def layout(self):
        g,e = self.get_minimum_geometry()
        self.set_geometry((0.0,0.0,0.0),g)
        pass
    #f display_decoration
    def display_decoration(self):
        for (xyz,whd,c) in self.children:
            c.display_decoration()
            pass
        pass
    #f display
    def display(self):
        for (xyz,whd,c) in self.children:
            c.display()
            pass
        pass
    #f display_background
    def display_background(self):
        for (xyz,whd,c) in self.children:
            c.display_background()
            pass
        pass
    #f mouse_press_initiate
    def mouse_press_initiate(self, b,s,m,xyz,dxyz):
        print self,"mpi",b,s,m,xyz,dxyz
        for (xyz,whd,c) in self.children:
            r = c.mouse_press_initiate(b,s,m,xyz,dxyz)
            if r is not None:
                return r
            pass
        return None
    #f motion_event
    #def motion_event(self, xyz, dxyz):
    #    if self.mouse_widget is None:
    #        return None
        


#c c_opengl_layout_depth_contents
class c_opengl_layout_depth_contents(c_opengl_layout):
    #f __init__
    def __init__(self, widget, **kwargs):
        self.widget = widget
        self.contents = opengl_utils.c_depth_contents()
        widget.children = self.contents
        widget.display_iter  = lambda: self.contents.get_iter(fwd=True, selector=lambda x:x[0])
        widget.interact_iter = lambda: self.contents.get_iter(fwd=False, selector=lambda x:x[0])
        pass
    #f add_widget
    def add_widget(self, widget, xyz=(0,0,0), depth=0, **kwargs):
        self.contents.add_contents(depth=depth, content=[widget, xyz, (0,0,0)])
        return widget
    #f get_content_bbox
    def get_content_bbox(self):
        xxyyzz = (None,None,None,None,None,None)
        for c in self.contents:
            (w,xyz,_) = c
            (w_xxyyzz, w_e) = w.get_minimum_bbox()
            whd = opengl_utils.whd_from_xxyyzz(w_xxyyzz)
            c[2] = whd
            w_xxyyzz = opengl_utils.xxyyzz_from_xyz_whd(xyz,whd)
            xxyyzz = opengl_utils.xxyyzz_minmax(xxyyzz, w_xxyyzz)
            pass
        return xxyyzz
    #f set_content_bbox
    def set_content_bbox(self, xxyyzz):
        """
        Set the content bbox
        """
        for (w,xyz,whd) in self.contents:
            w_xxyyzz = opengl_utils.xxyyzz_from_xyz_whd(xyz,whd)
            w.set_bbox(w_xxyyzz)
            pass
        pass
