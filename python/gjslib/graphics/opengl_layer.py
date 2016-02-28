#!/usr/bin/env python

#a Imports
from OpenGL.GLUT import *
from OpenGL.GLU import *
from OpenGL.GL import *
#from gjslib.graphics.opengl import opengl

#a Class for c_opengl_layer
#c c_depth_contents_iter
class c_depth_contents_iter(object):
    def __init__(self, dc):
        self.dc = dc
        self.depths = dc.contents.keys()
        self.content_index = 0
        pass
    def next(self):
        if len(self.depths)==0:
            raise StopIteration()
        d = self.depths[0]
        if d not in self.dc.contents:
            raise StopIteration()
        if self.content_index<len(self.dc.contents[d]):
            self.content_index += 1
            return self.dc.contents[d][self.content_index-1]
        self.content_index = 0
        self.depths.pop(0)
        return self.next()
        
#c c_depth_contents
class c_depth_contents(object):
    #f __init__
    def __init__(self):
        self.contents = {}
        pass
    pass
    #f clear_contents
    def clear_contents(self, depth=None):
        if depth is None:
            self.contents = {}
            return
        if depth in self.contents:
            self.contents[depth] = []
            pass
        pass
    #f add_contents
    def add_contents(self, content, depth=0):
        if depth not in self.contents:
            self.contents[depth] = []
            pass
        self.contents[depth].append(content)
        pass
    #f remove_contents
    def remove_contents(self, content, depth=None):
        for d in self.contents:
            if (depth is not None) and (d!=depth):
                continue
            self.contents[d].remove(content)
            return
        raise Exception("Failed to find content to remove (at specified depth)")
    #f __iter__
    def __iter__(self):
        return c_depth_contents_iter(self)
    #f All done
    pass

#c c_opengl_layer
class c_opengl_layer(c_depth_contents):
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
        c_depth_contents.__init__(self)
        pass
    #f display_init
    def display_init(self):
        glLightfv(GL_LIGHT1, GL_AMBIENT, [1.0,1.0,1.0,1.0])
        glEnable(GL_LIGHT1)
        glEnable(GL_TEXTURE_2D)
        glMaterialfv(GL_FRONT,GL_DIFFUSE,[1.0,1.0,1.0,1.0])
        glMaterialfv(GL_FRONT,GL_AMBIENT,[1.0,1.0,1.0,1.0])

        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()

        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        pass
    #f display
    def display(self):
        xywh = self.xywh
        glEnable(GL_SCISSOR_TEST)
        glViewport(xywh[0],xywh[1],xywh[2],xywh[3])
        glScissor(xywh[0],xywh[1],xywh[2],xywh[3])
        if self.autoclear in ["depth"]:
            glClear(GL_DEPTH_BUFFER_BIT)
            pass
        elif self.autoclear in ["all"]:
            glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)
            pass

        self.display_init()
        for c in self:
            c.display()
        glDisable(GL_SCISSOR_TEST)
        pass
    #f All done
    pass

#c c_opengl_layer_set
class c_opengl_layer_set(c_depth_contents):
    """
    Layers in a layer set are displayed back-to-front
    """
    def new_layer(self,xywh,depth=0,**kwargs):
        layer = c_opengl_layer(xywh, **kwargs)
        self.add_contents(depth=depth, content=layer)
        return layer
    #f display
    def display(self):
        for l in self:
            l.display()
        pass
