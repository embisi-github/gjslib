#!/usr/bin/env python

#a Imports
from OpenGL.GLUT import *
from OpenGL.GLU import *
from OpenGL.GL import *
from gjslib.graphics import opengl_utils, opengl_obj

#a Class for c_opengl_widget
#c c_opengl_widget
class c_opengl_widget(object):
    """
    A basic opengl widget is something that is displayed
    """
    #f __init__
    def __init__(self, og):
        self.og = og
        pass
    #f display
    def display(self):
        pass
    #f All done
    pass

#c c_opengl_simple_text_widget
class c_opengl_simple_text_widget(c_opengl_widget):
    """
    A simple text widget has text in a single font
    """
    #f __init__
    def __init__(self, og, fontname="font", text=None, **kwargs):
        c_opengl_widget.__init__(self, og=og, **kwargs)
        (self.bitmap_font, self.texture) = og.get_font(fontname)
        self.og_obj = opengl_obj.c_text_page()
        self.replace_text(text)
        pass
    #f replace_text
    def replace_text(self, text, baseline_xy=(-1.0,-1.0), scale=(0.001,0.001) ):
        self.og_obj.reset()
        if text is not None:
            self.og_obj.add_text(text, self.bitmap_font, baseline_xy, scale )
            self.og_obj.create_opengl_surface()
            pass
        pass
    #f display
    def display(self):
        self.og.shader_use("font_standard")
        self.og.shader_set_attributes(C=(0.9,0.8,0.8))
        self.og.matrix_use()
        glBindTexture(GL_TEXTURE_2D, self.texture)
        self.og_obj.draw_opengl_surface(og=self.og)
        pass
    #f All done
    pass

#c c_opengl_container_widget
class c_opengl_container_widget(c_opengl_widget, opengl_utils.c_depth_contents):
    """
    This widget is a container for stuff
    Stuff is an ordered list of things to display - "front" to "back"
    Also the stuff can have interaction functions that are also invoked front to back
    So the start of 'stuff' is front-most

    Each 'subwidget' has a separate translation/transformation matrix
    """
    #f __init__
    def __init__(self, **kwargs):
        opengl_utils.c_depth_contents.__init__(self, **kwargs)
        c_opengl_widget.__init__(self, **kwargs)
        pass
    #f add_widget
    def add_widget(self, widget, depth=0, **kwargs):
        content = {"widget":widget,
                   "transformation":opengl_utils.transformation(**kwargs),}
        self.add_contents(content=content,
                          depth=depth)
        pass
    #f display
    def display(self):
        for c in self:
            self.og.matrix_push()
            self.og.matrix_mult(c["transformation"])
            c["widget"].display()
            self.og.matrix_pop()
            pass
        pass
    #f All done
    pass
