#!/usr/bin/env python

#a Imports
from OpenGL.GLUT import *
from OpenGL.GLU import *
from OpenGL.GL import *
from gjslib.graphics import opengl_utils, opengl_obj
from gjslib.math import vectors
import OpenGL.arrays.vbo as vbo
import numpy

#a Notes
"""
A widget is the basic display object class.

A basic widget has decoration, paddings, and a background. It may have
children; if so, the children are further widgets.  If a widget has
children then the widget will have a 'layout' class instance that lays
out the children within the widget itself.

A layout class could be simple placement (child is placed at some xyz
in the parent widget); it could be packed (children have some whd and
some order) where the children are automatically placed and (as
desired) grown to fill their spaces.

The content of a widget may have a transformation applied to it.  This
transformation is applied before displaying the content, and hence has
to be applied to the bbox in geometry handling too.

We still need a style inheritance system (widgets needs a class name
and an id name) and animation... Not sure when to invoke relayout
based on animated values.

A table layout widget can be made
A table consists of rows of cells
The table may have a margin, border, padding, then content
Each row may have a border, then content
Each cell may have a border, padding, then content
At the table or row level the border style can be 'collapse', which means that the layer below it
does not have separate borders between items, but the right-border on the left-item replaces the
left-border on the right item
Each cell has a minimum content geometry and a growth weighting (independent for X and Y)
Layout is first by determining the minimum geomertry of each cell, then for each row, then for the table
(bottom-up minimum determinations)
Then the layout is performed top-down with displayed sizes applied

For drawing
"""

#a Class for c_opengl_widget
#c c_opengl_widget_decoration
class c_opengl_widget_decoration(object):
    """
    Single color widget decoration using the standard color shader
    """
    def __init__(self, color=None, vertex_data=None, indices=None):
        self.color = color
        self.num_indices = len(indices)
        self.vectors = vbo.VBO(data=numpy.array(vertex_data, dtype=numpy.float32), target=GL_ARRAY_BUFFER)
        self.indices = vbo.VBO( data=numpy.array(indices, dtype=numpy.uint8),
                                target=GL_ELEMENT_ARRAY_BUFFER )
        pass
    def draw(self, og):
        og.shader_use("color_standard")
        self.vectors.bind()
        self.indices.bind()
        og.matrix_use()
        og.shader_set_attributes(t=3, v=0, C=self.color)
        glDrawElements(GL_TRIANGLES,self.num_indices,GL_UNSIGNED_BYTE,self.indices)
        self.vectors.unbind()
        self.indices.unbind()
        pass

#c c_opengl_widget
class c_opengl_widget(object):
    """
    A basic opengl widget is something that is displayed
    """
    margin = None
    border = None
    padding = None
    border_colors = ((1,1,1),)
    background_color = None
    width = 1
    height = 1
    depth = 0
    #f __init__
    def __init__(self, og, parent=None, layout_class=None, **kwargs):
        self.og = og
        self.decorations = {}
        self.backgrounds = {}
        self.mouse_widget = None
        self.parent = parent
        self._layout = None
        self.content_transformation = None
        self.display_iter = None
        self.interact_iter = None
        if layout_class is None:
            self._layout = None
            self.children = []
            self.display_iter = self.children.__iter__
            self.interact_iter = self.children.__iter__
            pass
        else:
            #layout_class = opengl_layout.c_opengl_layout_depth_contents
            self._layout  = layout_class(self, **kwargs)
            pass
        #content["inverse_transformation"] = content["transformation"].inverse()
        pass
    #f __create_vbos
    def __create_vbos(self):
        self.decorations = {}
        self.backgrounds = {}
        if self.border is not None:
            b_xxyyzz = self.border_bbox
            i_xxyyzz = self.inner_bbox
            (blx,brx,bby,bty,_,_) = b_xxyyzz
            (ilx,irx,iby,ity,_,_) = i_xxyyzz
            print "border",blx,brx,bby,bty,ilx,irx,iby,ity
            d = c_opengl_widget_decoration( color=self.border_colors[0],
                                            vertex_data = (blx,bby,0, brx,bby,0, brx,bty,0, blx,bty,0,
                                                           ilx,iby,0, irx,iby,0, irx,ity,0, ilx,ity,0,
                                                           ),
                                            indices = (0,4,1, 1,4,5, 1,5,2, 2,5,6,
                                                       2,6,3, 3,6,7, 3,7,0, 0,7,4) )
            self.decorations["border_one_color"] = d
            pass
        if self.background_color is not None: # Not so good for 3D?
            i_xxyyzz = self.inner_bbox
            (ilx,irx,iby,ity,_,_) = i_xxyyzz
            print "bg",i_xxyyzz, ilx, irx, iby, ity
            d = c_opengl_widget_decoration( color=self.background_color,
                                            vertex_data = (ilx,iby,0, irx,iby,0, irx,ity,0, ilx,ity,0,),
                                            indices = (0,3,1, 1,3,2,) )
            self.backgrounds["content"] = d
            pass
        print self
        pass
    #f __margin_border_padding
    def __margin_border_padding(self):
        m = (0,0,0,0,0,0)
        if self.margin is not None:
            m = self.margin
            if type(m)!=tuple:
                m = (m,m,0,m,m,0)
                pass
            pass
        b = (0,0,0,0,0,0)
        if self.border is not None:
            b = self.border
            if type(b)!=tuple:
                b = (b,b,0,b,b,0)
                pass
            pass
        p = (0,0,0,0,0,0)
        if self.padding is not None:
            p = self.padding
            if type(p)!=tuple:
                p = (p,p,0,p,p,0)
                pass
            pass
        return (m,b,p)
    #f add_widget
    def add_widget(self, widget, **kwargs):
        if self._layout is None:
            self.children.append(widget)
            pass
        else:
            self._layout.add_widget(widget, **kwargs)
            pass
        return widget
    #f get_minimum_bbox
    def get_minimum_bbox(self, content_bbox=None, content_includes_borders=False):
        """
        Return ( (xxyyzz), (exp tuple) )
        Units are the same as the layout of the parent
        UNLESS we potentially apply a transformation
        This method MUST be invoked by a subclass widget at the
        end of its get_minimum_bbox method
        """
        if self._layout is not None:
            content_bbox = self._layout.get_content_bbox()
            pass
        if content_bbox is None:
            content_bbox = (0,0, 0,0, 0,0)
            pass
        (m,b,p) = self.__margin_border_padding()
        t = vectors.vector_add(m,vectors.vector_add(b,p))
        if content_includes_borders:
            content_bbox = opengl_utils.xxyyzz_add_border(content_bbox,t)
            pass
        xxyyzz = opengl_utils.xxyyzz_add_border(content_bbox,t,scale=-1.0)
        self.content_bbox = content_bbox
        print self,content_bbox,xxyyzz
        return (xxyyzz, None)
    #f set_bbox
    def set_bbox(self, xxyyzz):
        """
        Set geometry to fit within bbox (xxyyzz)
        Return the content geometry xxyyzz
        """
        self.display_bbox = xxyyzz[:]
        (m,b,p) = self.__margin_border_padding()

        b_xxyyzz = opengl_utils.xxyyzz_add_border(  xxyyzz,m)
        i_xxyyzz = opengl_utils.xxyyzz_add_border(b_xxyyzz,b)
        c_xxyyzz = opengl_utils.xxyyzz_add_border(i_xxyyzz,p)

        self.border_bbox  = b_xxyyzz
        self.inner_bbox   = i_xxyyzz
        self.content_bbox = c_xxyyzz
        self.__create_vbos()

        print self,xxyyzz,b_xxyyzz,m,b,p
        if self._layout is not None:
            self._layout.set_content_bbox(self.content_bbox)
            pass

        return c_xxyyzz
    #f display_decoration
    def display_decoration(self):
        if self.decorations is None: return
        self.og.matrix_use()
        for k,d in self.decorations.iteritems():
            d.draw(self.og)
            pass
        pass
    #f display
    def display(self):
        self.display_decoration()
        if self.content_transformation is not None:
            self.og.matrix_push()
            self.og.matrix_mult(self.content_transformation)
            pass
        self.display_contents()
        if self.content_transformation is not None:
            self.og.matrix_pop()
            pass
        self.display_background()
        pass
    #f display_contents
    def display_contents(self):
        if self.display_iter is None: return
        for c in self.display_iter():
            c.display()
            pass
        pass
    #f display_background
    def display_background(self):
        if self.backgrounds is None: return
        self.og.matrix_use()
        for k,d in self.backgrounds.iteritems():
            d.draw(self.og)
            pass
        pass
    #f motion
    def motion(self,x,y):
        print "epm:motion",x,y,self.motion_event_layer
        if self.motion_event_layer is not None:
            self.motion_event_layer.motion_event(self.mouse_state,x,y)
            pass
        pass
    #f mouse
    def mouse(self,b,s,m,x,y):
        """
        Turn a mouse press/release into individual method calls for press/release with xyz,dxyz coordinates
        """
        if self.mouse_state is None:
            if state==GLUT_DOWN:
                self.mouse_state = {"xy":(x,y),
                                    button:state}
                pass
            pass
        else:
            if state==GLUT_UP:
                if button in self.mouse_state:
                    del(self.mouse_state[button])
                    pass
                pass
            if state==GLUT_DOWN:
                self.mouse_state[button] = state
                pass
            pass
        if len(self.mouse_state)==1: # just xy
            self.mouse_state = None
            pass

        if self.motion_event_layer is not None:
            self.motion_event_layer = self.motion_event_layer.mouse_event(self.mouse_state,b,s,m,x,y)
            return
        xy = (x,y)
        layers = self.layers.find_layers_at_xy(xy)
        if len(layers)==0:
            self.point_set_end()
            return True
        l = layers[0]
        if l in self.image_layers:
            return self.mouse_in_image(l,b,s,m,xy)
        self.motion_event_layer = l.mouse_event(self.mouse_state,b,s,m,x,y)
        return True
    #f mouse_event
    def mouse_event(self, b,s,m,xyz,dxyz):
        print self,"mev",b,s,m,xyz
        if self.mouse_widget is not None:
            self.mouse_widget = self.mouse_press_continue(b,s,m,xyz,dxyz)
            if self.mouse_widget is None:
                return None
            return self
        r = self.mouse_press_initiate(b,s,m,xyz,dxyz)
        if r is not None:
            self.mouse_widget = r
            return self
        self.mouse_widget = None
        return None
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
        


    #f mouse_press_initiate
    def mouse_press_initiate(self, b,s,m,xyz,dxyz):
        print self, "mpi",b,s,m,xyz
        if "border_one_color" in self.decorations:
            if s=="down":
                self.decorations["border_one_color"].color = (1.0,0.0,0.0)
            else:
                self.decorations["border_one_color"].color = (0.0,0.0,0.0)
                pass
            return self
        pass
    #f mouse_press_continue
    def mouse_press_continue(self,b,s,m,xyz,dxyz):
        """
        w should be self at this point for a 'terminal' widget - i.e. one that returned self to mouse_press_initiate
        """
        if self.mouse_widget is not None:
            self.mouse_widget = self.mouse_widget.mouse_press_continue(b,s,m,xyz,dxyz)
            if self.mouse_widget is None: return None
            return self
        print self, "mpc",b,s,m,xyz
        if "border_one_color" in self.decorations:
            if s=="down":
                self.decorations["border_one_color"].color = (1.0,0.0,0.0)
                return self
            else:
                self.decorations["border_one_color"].color = (0.0,0.0,0.0)
                return None
                pass
            pass
        return None
    #f motion_event
    def motion_event(self, xyz, dxyz):
        #print "widget:motion",self,xyz,dxyz,self.mouse_widget
        if self.mouse_widget is not None:
            self.mouse_widget = self.mouse_widget.motion_event(xyz,dxyz)
            pass
        if self.mouse_widget is None:
            return None
        return self
    #f ray_transform
    def ray_transform(self,c,xyz,dxyz):
        xyz = c["inverse_transformation"].apply((xyz[0],xyz[1],xyz[2],1.0))
        dxyz = c["inverse_transformation"].apply((dxyz[0],dxyz[1],dxyz[2],1.0))
        return (xyz[:3], dxyz[:3])
    #f mouse_press_continue
    def mouse_press_continue(self,b,s,m,xyz,dxyz):
        if self.mouse_widget is None: return None
        (xyz,dxyz) = self.ray_transform(self.mouse_widget,xyz,dxyz)
        return self.mouse_widget["widget"].mouse_event(b,s,m,xyz,dxyz)
    #f mouse_press_initiate
    def mouse_press_initiate(self, b,s,m,xyz,dxyz):
        for c in self:
            (xyz,dxyz) = self.ray_transform(c,xyz,dxyz)
            r = c["widget"].mouse_event(b,s,m,xyz,dxyz)
            if r is not None:
                return c
            pass
        return None
    #f motion_event
    def motion_event(self, xyz,dxyz):
        print "ocw:motion",self,self.mouse_widget,xyz,dxyz
        if self.mouse_widget is None:
            return
        (xyz,dxyz) = self.ray_transform(self.mouse_widget,xyz,dxyz)
        r = self.mouse_widget["widget"].motion_event(xyz,dxyz)
        #if r is not None:
    #f layout
    def layout(self):
        """
        Layout a widget
        Should only be invoked on the top level of the hierarchy
        """
        g,e = self.get_minimum_bbox()
        self.set_bbox(g)
        pass
    #f All done
    pass

#c c_opengl_simple_text_widget
class c_opengl_simple_text_widget(c_opengl_widget):
    """
    A simple text widget has text in a single font
    """
    #f __init__
    def __init__(self, og, scale=(1.0,1.0), fontname="font", text=None, **kwargs):
        c_opengl_widget.__init__(self, og=og, **kwargs)
        self.scale = scale
        (self.bitmap_font, self.texture) = og.get_font(fontname)
        self.og_obj = opengl_obj.c_text_page()
        self.replace_text(text)
        self.border=(50,50,50,50,0,0)
        self.padding=(2,2,2,2,0,0)
        self.background_color = (0.1,0.1,0.5)
        pass
    #f get_minimum_bbox
    def get_minimum_bbox(self):
        """
        Return ( (w,h,d), (exp tuple) )
        """
        (xyz0, xyz1) = self.og_obj.find_bbox()
        xxyyzz = opengl_utils.xxyyzz_from_xyz_pair(xyz0,xyz1)
        self.text_xyz = (xxyyzz[0], xxyyzz[2], xxyyzz[4])
        return c_opengl_widget.get_minimum_bbox(self, content_bbox=xxyyzz)
    #f set_bbox
    def set_bbox(self, xxyyzz):
        xxyyzz = c_opengl_widget.set_bbox(self, xxyyzz)
        self.dxyz = vectors.vector_add((xxyyzz[0],xxyyzz[2],xxyyzz[4]),self.text_xyz,scale=-1.0)
        pass
    #f replace_text
    def replace_text(self, text, baseline_xy=(-1.0,-1.0), scale=(1.0,1.0) ):
        self.og_obj.reset()
        if text is not None:
            self.og_obj.add_text(text, self.bitmap_font, baseline_xy, scale=(scale[0]*self.scale[0], scale[1]*self.scale[1]) )
            self.og_obj.create_opengl_surface()
            pass
        pass
    #f display_contents
    def display_contents(self):
        #print self.content_bbox
        self.og.shader_use("font_standard")
        self.og.shader_set_attributes(C=(0.9,0.8,0.8))
        self.og.matrix_push()
        self.og.matrix_translate(self.dxyz)
        self.og.matrix_use()
        glBindTexture(GL_TEXTURE_2D, self.texture)
        self.og_obj.draw_opengl_surface(og=self.og)
        self.og.matrix_pop()
        #sys.exit()
        pass
    #f All done
    pass

