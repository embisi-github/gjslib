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
    def __init__(self, og, **kwargs):
        self.og = og
        self.decorations = {}
        self.backgrounds = {}
        self.mouse_widget = None
        pass
    #f __create_vbos
    def __create_vbos(self):
        self.decorations = {}
        self.backgrounds = {}
        if self.border is not None:
            (bxyz, bwhd) = self.border_geometry
            (ixyz, iwhd) = self.border_inner_geometry
            (bx, by, _) = bxyz
            (bw, bh, _) = bwhd
            (ix, iy, _) = ixyz
            (iw, ih, _) = iwhd
            d = c_opengl_widget_decoration( color=self.border_colors[0],
                                            vertex_data = (bx,by,0, bx+bw,by,0, bx+bw,by+bh,0, bx,by+bh,0,
                                                           ix,iy,0, ix+iw,iy,0, ix+iw,iy+ih,0, ix,iy+ih,0,),
                                            indices = (0,4,1, 1,4,5, 1,5,2, 2,5,6,
                                                       2,6,3, 3,6,7, 3,7,0, 0,7,4) )
            self.decorations["border_one_color"] = d
            pass
        if self.background_color is not None: # Not so good for 3D?
            (cxyz, cwhd) = self.border_inner_geometry
            (cx, cy, _) = cxyz
            (cw, ch, _) = cwhd
            d = c_opengl_widget_decoration( color=self.background_color,
                                            vertex_data = (cx,cy,0, cx+cw,cy,0, cx+cw,cy+ch,0, cx,cy+ch,0,),
                                            indices = (0,3,1, 1,3,2,) )
            self.backgrounds["content"] = d
            pass
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
    #f get_minimum_geometry
    def get_minimum_geometry(self, content_geometry=None):
        """
        Return ( (w,h,d), (exp tuple) )
        """
        (w,h,d) = (0.0,0.0,0.0)
        (m,b,p) = self.__margin_border_padding()
        if content_geometry is not None:
            (w,h,d) = vectors.vector_add(content_geometry[1], content_geometry[0], scale=-1.0)
            pass
        if w<0: w=-w
        if h<0: h=-h
        if d<0: d=-d
        w += m[0]+m[3]+b[0]+b[3]+p[0]+p[3]
        h += m[1]+m[4]+b[1]+b[4]+p[1]+p[4]
        d += m[2]+m[5]+b[2]+b[5]+p[2]+p[5]
        return ((w,h,d), None)
        pass
    #f set_geometry
    def set_geometry(self, xyz, whd):
        """
        Set geometry to ( xyz, whd )
        """
        self.display_geometry = (xyz, whd)
        (m,b,p) = self.__margin_border_padding()

        bxyz = vectors.vector_add( xyz,m[0:3])
        bwhd = vectors.vector_add( whd,m[0:3],scale=-1)
        bwhd = vectors.vector_add(bwhd,m[3:6],scale=-1)

        ixyz = vectors.vector_add(bxyz,b[0:3])
        iwhd = vectors.vector_add(bwhd,b[0:3],scale=-1)
        iwhd = vectors.vector_add(iwhd,b[3:6],scale=-1)

        cxyz = vectors.vector_add(ixyz,p[0:3])
        cwhd = vectors.vector_add(iwhd,p[0:3],scale=-1)
        cwhd = vectors.vector_add(cwhd,p[3:6],scale=-1)

        self.border_geometry       = (bxyz, bwhd)
        self.border_inner_geometry = (ixyz, iwhd)
        self.content_geometry      = (cxyz, cwhd)
        self.__create_vbos()
        return (cxyz, cwhd)
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
        pass
    #f display_background
    def display_background(self):
        if self.backgrounds is None: return
        self.og.matrix_use()
        for k,d in self.backgrounds.iteritems():
            d.draw(self.og)
            pass
        pass
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
    #f All done
    pass

#c c_opengl_layout
def min(a,b,c=None):
    if a is None: a=b
    if a>b:a=b
    if c is not None and a>c: a=c
    return a
def max(a,b,c=None):
    if a is None: a=b
    if a<b:a=b
    if c is not None and a<c: a=c
    return a
class c_opengl_layout(c_opengl_widget):
    """
    A simple placed-layout geometry
    There is no intelligence here - whatever the children are added with is what they get
    """
    #f __init__
    def __init__(self, **kwargs):
        c_opengl_widget.__init__(self,**kwargs)
        self.children = []
        pass
    #f add_child
    def add_child(self, c, xyz, **kwargs):
        self.children.append( [xyz, None, c] )
        pass
    #f get_minimum_geometry
    def get_minimum_geometry(self):
        (x0,y0,z0,x1,y1,z1) = (None,None,None,None,None,None)
        for i in range(len(self.children)):
            (xyz,whd,c) = self.children[i]
            ((w,h,d),_) = c.get_minimum_geometry()
            self.children[i][1] = (w,h,d)
            x0 = min(x0,xyz[0],xyz[0]+w)
            y0 = min(y0,xyz[1],xyz[1]+h)
            z0 = min(z0,xyz[2],xyz[2]+d)
            x1 = max(x1,xyz[0],xyz[0]+w)
            y1 = max(y1,xyz[1],xyz[1]+h)
            z1 = max(z1,xyz[2],xyz[2]+d)
            pass
        return ((x1-x0, y1-y0, z1-z0), None)
    #f set_geometry
    def set_geometry(self, xyz, whd):
        for (xyz, whd, c) in self.children:
            c.set_geometry(xyz, whd)
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
        self.border=(0.01,0.01,0, 0.01,0.01,0)
        self.padding=(0.002,0.002,0, 0.002,0.002,0)
        self.background_color = (0.1,0.1,0.5)
        pass
    #f get_minimum_geometry
    def get_minimum_geometry(self):
        """
        Return ( (w,h,d), (exp tuple) )
        """
        (xyz0,xyz1) = self.og_obj.find_bbox()
        self.text_xyz = xyz0
        return c_opengl_widget.get_minimum_geometry(self, content_geometry=(xyz0, xyz1))
    #f replace_text
    def replace_text(self, text, baseline_xy=(-1.0,-1.0), scale=(1.0,1.0) ):
        self.og_obj.reset()
        if text is not None:
            self.og_obj.add_text(text, self.bitmap_font, baseline_xy, scale=(scale[0]*self.scale[0], scale[1]*self.scale[1]) )
            self.og_obj.create_opengl_surface()
            pass
        pass
    #f set_geometry
    def set_geometry(self, xyz, whd):
        (xyz, whd) = c_opengl_widget.set_geometry(self, xyz, whd)
        self.xyz = vectors.vector_add(xyz,self.text_xyz,scale=-1.0)
        pass
    #f display
    def display(self):
        self.og.shader_use("font_standard")
        self.og.shader_set_attributes(C=(0.9,0.8,0.8))
        self.og.matrix_push()
        self.og.matrix_translate(self.xyz)
        self.og.matrix_use()
        glBindTexture(GL_TEXTURE_2D, self.texture)
        self.og_obj.draw_opengl_surface(og=self.og)
        self.og.matrix_pop()
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
        content["inverse_transformation"] = content["transformation"].inverse()
        self.add_contents(content=content,
                          depth=depth)
        pass
    #f display
    def display(self):
        for c in self:
            self.og.matrix_push()
            self.og.matrix_mult(c["transformation"])
            c["widget"].display_decoration()
            c["widget"].display()
            c["widget"].display_background()
            self.og.matrix_pop()
            pass
        pass
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
    #f All done
    pass
