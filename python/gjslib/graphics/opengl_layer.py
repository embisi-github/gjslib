#!/usr/bin/env python

#a Imports
from OpenGL.GLUT import *
from OpenGL.GLU import *
from OpenGL.GL import *
from gjslib.graphics import opengl_utils

#a Useful functions
def in_rectangle(xy, xywh):
    if xy[0]-xywh[0]<0: return False
    if xy[1]-xywh[1]<0: return False
    if xy[0]-xywh[0]>=xywh[2]: return False
    if xy[1]-xywh[1]>=xywh[3]: return False
    return True

#a Class for c_opengl_layer
#c c_opengl_layer
class c_opengl_layer(opengl_utils.c_depth_contents):
    """
    An OpenGL layer is used in the opengl GUI
    A layer has a window viewport (x,y,w,h), and so must be rectangular
    A layer may be configured to autoclear before display.
    It can autoclear depth buffer, all, or none

    A layer clear of 'none' makes no sense to me at the moment
    If a layer clears just the depth buffer then it is effectively an overlay
    If a layer clears all then it is destructive and is like an 'in-front-of' window

    Possibly in the future a layer could be defined to have a stencil to limit it to a particular
    shaped region
    In this case the layer depth buffer would be cleared; the 'outside' of the stencil depth buffer would be drawn
    with depth 0

    The layer is dependent on the window size - so it is a GUI-window-dependent structure

    self.contents is a dictionary of depth:[display objects]

    The layer is drawn with lowest depth objects first, in the order in which they are added
    """
    #f __init__
    def __init__(self, xywh, autoclear="depth" ):
        self.xywh = xywh
        self.autoclear = autoclear
        opengl_utils.c_depth_contents.__init__(self)
        pass
    #f display_init
    def display_init(self):
        pass
    #f display
    def display(self):
        xywh = self.xywh
        glViewport(xywh[0],xywh[1],xywh[2],xywh[3])
        glScissor(xywh[0],xywh[1],xywh[2],xywh[3])
        glEnable(GL_SCISSOR_TEST)
        if self.autoclear in ["depth"]:
            glClear(GL_DEPTH_BUFFER_BIT)
            pass
        elif self.autoclear in ["all"]:
            glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)
            pass

        self.display_init()
        for c in self:
            c.display()
            pass

        glDisable(GL_SCISSOR_TEST)
        pass
    #f scaled_xy
    def scaled_xy(self, xy):
        """
        Return (xy) in 0->1 range for a given layer set xy
        """
        return ((xy[0]-self.xywh[0])/float(self.xywh[2]),
                (xy[1]-self.xywh[1])/float(self.xywh[3]))
    #f All done
    pass

#c c_opengl_layer_set
class c_opengl_layer_set(opengl_utils.c_depth_contents):
    """
    Layers in a layer set are displayed back-to-front
    """
    #f new_layer
    def new_layer(self,xywh,depth=0,**kwargs):
        layer = c_opengl_layer(xywh, **kwargs)
        self.add_contents(depth=depth, content=layer)
        return layer
    #f display
    def display(self):
        for l in self:
            l.display()
        pass
    #f find_layers_at_xy
    def find_layers_at_xy(self,xy):
        r = []
        for l in self:
            if in_rectangle(xy, l.xywh):
                r.append(l)
                pass
            pass
        return r
