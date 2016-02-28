#!/usr/bin/env python

#a Imports
from OpenGL.GLUT import *
from OpenGL.GLU import *
from OpenGL.GL import *
import gjslib.graphics.obj
from gjslib.graphics import opengl

#a Class for c_opengl_widget
#c c_opengl_widget
class c_opengl_widget(object):
    """
    A basic opengl widget is something that is displayed
    """
    #f __init__
    def __init__(self):
        pass
    #f display
    def display(self):
        pass
    #f All done
    pass

#c c_opengl_simple_text_widget
class c_opengl_simple_text_widget(object):
    """
    A simple text widget has text in a single font
    """
    #f __init__
    def __init__(self, og, fontname="font", text=None):
        (self.bitmap_font, self.texture) = og.get_font(fontname)
        self.og_obj = gjslib.graphics.obj.c_text_page()
        self.replace_text(text)
        pass
    #f replace_text
    def replace_text(self, text, baseline_xy=(-1.0,-1.0), scale=(0.001,0.001) ):
        self.og_obj.destroy_opengl_surface()
        if text is not None:
            self.og_obj.add_text(text, self.bitmap_font, baseline_xy, scale )
            self.og_obj.create_opengl_surface()
            pass
        pass
    #f display
    def display(self):
        glBindTexture(GL_TEXTURE_2D, self.texture)
        self.og_obj.draw_opengl_surface()
        pass
    #f All done
    pass

#c c_opengl_container_widget
class c_opengl_container_widget(c_opengl_widget, opengl.c_depth_contents):
    """
    This widget is a container for stuff
    Stuff is an ordered list of things to display - "front" to "back"
    Also the stuff can have interaction functions that are also invoked front to back
    So the start of 'stuff' is front-most

    Each 'subwidget' has a separate translation/transformation matrix
    """
    #f __init__
    def __init__(self, **kwargs):
        opengl.c_depth_contents.__init__(self, **kwargs)
        c_opengl_widget.__init__(self, **kwargs)
        pass
    #f add_widget
    def add_widget(self, widget, depth=0, **kwargs):
        content = {"widget":widget,
                   "transformation":opengl.transformation(**kwargs),}
        self.add_contents(content=content,
                          depth=depth)
        pass
    #f display
    def display(self):
        for c in self:
            glPushMatrix()
            glMultMatrixf(c["transformation"])
            c["widget"].display()
            glPopMatrix()
            pass
        pass
    #f All done
    pass
