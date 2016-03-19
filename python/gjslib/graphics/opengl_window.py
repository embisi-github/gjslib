#!/usr/bin/env python

#a Imports
from OpenGL.GLUT import *
from OpenGL.GLU import *
from OpenGL.GL import *
from gjslib.graphics import opengl_utils, opengl_widget

#a Class for c_opengl_window
class c_old:
    #f scaled_xy
    def scaled_xy(self, xy):
        """
        Return (xy) in 0->1 range for a given window set xy
        """
        return ((xy[0]-self.xywh[0])/float(self.xywh[2]),
                (xy[1]-self.xywh[1])/float(self.xywh[3]))
    #f mouse_event
    def mouse_event(self,state,b,s,m,x,y):
        xy = self.scaled_xy((x,y))
        xyz = (xy[0], xy[1], -10)
        dxyz = (0,0,1)
        print "window mev", self.mouse_widget
        if (s=="down") and (self.mouse_widget is None):
            print s, self.mouse_widget
            for c in self.reverse():
                w = c.mouse_event(b,s,m,xyz, dxyz)
                if w is not None:
                    self.mouse_widget = w
                    break
                pass
            pass
        elif self.mouse_widget is not None:
            self.mouse_widget = self.mouse_widget.mouse_event(b,s,m,xyz,dxyz)
            if self.mouse_widget is None: return None
            return self
        print "Done", self.mouse_widget
        if self.mouse_widget is not None:
            return self
        pass
    #f motion_event
    def motion_event(self,state,x,y):
        print "ogl:motion",self,state,x,y,self.mouse_widget
        if self.mouse_widget is not None:
            xy = self.scaled_xy((x,y))
            xyz = (xy[0], xy[1], -10)
            dxyz = (0,0,1)
            r = self.mouse_widget.motion_event(xyz, dxyz)
            if not r:
                self.mouse_widget = None
            pass
        pass
    #f All done
    pass

#c c_opengl_window
class c_opengl_window(opengl_widget.c_opengl_widget):
    """
    Windows is a 2D widget that contains other widgets
    which are drawn constrained within a viewport (so the do not overflow)
    Windows need to know the OpenGL context window size to set the viewport
    bounds.
    """
    #f __init__
    def __init__(self, og, wh=None, autoclear=None, **kwargs):
        opengl_widget.c_opengl_widget.__init__(self, og, **kwargs)
        self.autoclear = autoclear
        self.width  = wh[0]
        self.height = wh[1]
        self.border=(3,3,3,3,0,0)
        self.padding=(2,2,2,2,0,0)
        self.border_colors = ((0.9,0.9,0.5),)
        self.background_color = (0.1,0.1,0.5)
        pass
    #f get_minimum_bbox
    def get_minimum_bbox(self):
        return opengl_widget.c_opengl_widget.get_minimum_bbox(self, content_bbox=(0,self.width,0,self.height,0,0), content_includes_borders=True)
    #f display
    def display(self):
        (xyz,whd) = opengl_utils.xyz_whd_from_xxyyzz(self.display_bbox)
        if self.parent is None:
            self.og.matrix_push(matrix="project")
            m = opengl_utils.transformation(map_xywh=((xyz[0],xyz[1],whd[0],whd[1]),(-1.0,1.0,2.0,-2.0)))
            self.og.matrix_set(m,"project")
            self.og.matrix_identity("view")
            self.og.matrix_identity("model")
            pass
        self.og.clip_push(xyz[0], xyz[1], whd[0], whd[1])
        if self.autoclear in ["depth"]:
            glClear(GL_DEPTH_BUFFER_BIT)
            pass
        elif self.autoclear in ["all"]:
            glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)
            pass
        self.display_decoration()
        (xyz,whd) = opengl_utils.xyz_whd_from_xxyyzz(self.content_bbox)
        self.og.clip_push(xyz[0], xyz[1], whd[0], whd[1])
        self.display_contents()
        self.og.clip_pop()
        self.display_background()
        self.og.clip_pop()
        if self.parent is None:
            self.og.matrix_pop(matrix="project")
            pass
        pass
#a Useful functions
def in_rectangle(xy, xywh):
    if xy[0]-xywh[0]<0: return False
    if xy[1]-xywh[1]<0: return False
    if xy[0]-xywh[0]>=xywh[2]: return False
    if xy[1]-xywh[1]>=xywh[3]: return False
    return True

    #f find_windows_at_xy
    def find_windows_at_xy(self,xy):
        r = []
        for l in self:
            if in_rectangle(xy, l.xywh):
                r.append(l)
                pass
            pass
        return r
