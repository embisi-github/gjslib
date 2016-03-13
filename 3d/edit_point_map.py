#!/usr/bin/env python
# PYTHONPATH=`pwd`/../python:$PYTHONPATH ./mapping.py

#a Imports
from gjslib.graphics import opengl, opengl_obj, opengl_app, opengl_layer, opengl_widget, opengl_utils, opengl_menu
from gjslib.math import vectors
from image_projection import c_image_projection

from OpenGL.GLUT import *
from OpenGL.GLU import *
from OpenGL.GL import *

from image_point_mapping import c_point_mapping
import argparse

#a c_undo_buffer
class c_undo_buffer(object):
    """
    The undo buffer is appended to when an operation is performed.

    When an undo is first performed, the undo ptr is set to the end of the buffer
    and an undo operation performed.

    If another undo is requested then the undo operation is performed.
    The undo operation is: buffer[--undo_ptr] is returned, and
    'undo' of that op is added to the buffer.
    """
    def __init__(self):
        self.buffer = []
        self.undo_ptr = None
        pass
    def add_operation(self, op):
        self.buffer.append((True,op))
        self.undo_ptr = None
        pass
    def undo_operation(self):
        if self.undo_ptr is None:
            self.undo_ptr = len(self.buffer)
            pass
        self.undo_ptr -= 1
        if self.undo_ptr<0:
            self.undo_ptr = 0
            return None
        if len(self.buffer)==0:
            return None
        (undo,op) = self.buffer[self.undo_ptr]
        self.buffer.append((not undo,op))
        return (undo, op)
    def redo_operation(self):
        if self.undo_ptr is None:
            return None
        if self.undo_ptr>=len(self.buffer):
            self.undo_ptr = None
            return None
        (undo,op) = self.buffer[self.undo_ptr]
        self.undo_ptr += 1
        if self.undo_ptr>=len(self.buffer):
            self.undo_ptr = None
            pass
        return (not undo, op)
    pass
#a c_edit_point_map_image
class c_edit_point_map_image(object):
    """
    This class represents an image that can be presented in an OpenGL widget frame,
    that corresponds to an image with a point mapping of (x,y) points to names

    When displayed it shows the image (-1,-1) to (+1,+1) and an optional 'focus' indicator
    The center of the source image for (0,0) can be selected, as can the scale (i.e. zoom)

    Optionally the image can display the point-map points; these will be represented in
    the first instance as spinning glowing '+' marks on the relevant spots of the image

    The 'focus' indicator defaults to a white border of a configurable OpenGL-coord width/height
    """
    #f __init__
    def __init__(self, filename=None, image_name=None, epm=None, pm=None, projection=None):
        self.filename = filename
        self.image_name = image_name
        self.texture = None
        self.object = None
        self.focus_object = None
        self.epm = epm
        self.point_mappings = pm
        self.projection = projection
        self.center = (0.0,0.0)
        self.scale = (1.0,1.0)
        self.display_options = {}
        self.display_options["points"] = True
        self.display_options["projected_points"] = True
        self.display_options["focus"] = True
        self.display_options["focus_w"] = 0.01
        self.display_options["focus_h"] = 0.01
        pass
    #f set_focus
    def set_focus(self, focus=True):
        """
        Enable or disable the display of the 'focus frame'
        """
        self.display_options["focus"] = focus
        pass
    #f focus_on_point
    def focus_on_point(self, pt_name, force_focus=False):
        """
        Set the center of the image in the display window to be the point name in the
        point mappings; if the image has no map, then either do not move the centering
        or force the focus to move to the center of the image.
        """
        xy = self.point_mappings.get_xy(pt_name, self.image_name )
        if xy is None:
            if self.projection is not None:
                xyz = self.point_mappings.get_approx_position(pt_name)
                if xyz is not None:
                    ui = self.projection.image_of_model(xyz)
                    if ui is not None:
                        (uvzw,img_xy) = ui
                        xy = (uvzw[0],uvzw[1])
                        pass
                    pass
                pass
            pass
            
        if xy is None:
            if force_focus:
                self.center = (0,0)
                pass
            return
        self.center = (-xy[0],-xy[1])
        pass
    #f adjust
    def adjust(self, scale=(1.0,1.0), translate=(0.0,0.0), scaled=True ):
        """
        Adjust the view of the image by a scale and translation.

        If 'scaled' then scale the translation.
        """
        if type(scale)==float:
            scale = (scale,scale)
            pass
        if scale[0]<0:
            scale = (1.0/self.scale[0], 1.0/self.scale[1])
            pass
        if scaled:
            translate = (translate[0]/self.scale[0], translate[1]/self.scale[1])
            pass
        self.center = (self.center[0] + translate[0],
                       self.center[1] + translate[1])
        self.scale = (self.scale[0]*scale[0], self.scale[1]*scale[1] )
        pass
    #f load_texture
    def load_texture(self):
        """
        Load the texture and create any OpenGL objects required for display.

        This is done in a lazy fashion - only create the image etc when required
        """
        if (self.texture is None):
            self.texture = opengl_utils.texture_from_png(self.filename)
            pass
        if self.object is None:
            self.object = opengl_obj.c_opengl_obj()
            self.object.add_rectangle( (-1.0,1.0,0.0), (2.0,0.0,0.0), (0.0,-2.0,0.0) )
            self.object.create_opengl_surface()
            pass
        if self.focus_object is None:
            self.focus_object = opengl_obj.c_opengl_obj()
            fw = self.display_options["focus_w"]
            fh = self.display_options["focus_h"]
            self.focus_object.add_rectangle( (-1.0,-1.0,0.0), (2.0,0.0,0.0), (0.0,fh,0.0) )
            self.focus_object.add_rectangle( (-1.0,-1.0,0.0), (fw,0.0,0.0),  (0.0,2.0,0.0) )
            self.focus_object.add_rectangle(  (1.0,1.0,0.0),  (-2.0,0.0,0.0), (0.0,-fh,0.0) )
            self.focus_object.add_rectangle(  (1.0,1.0,0.0),  (-fw,0.0,0.0), (0.0,-2.0,0.0) )
            self.focus_object.create_opengl_surface()
            pass
        pass
    #f uniform_xy
    def uniform_xy(self, xy):
        """
        Return the corresponding uniform xy (-1->1) for a view port xy 0->1.
        This depends on the scaling and centering of the view port onto the image
        """
        # Get xy in range -1 -> 1
        xy = (2.0*xy[0]-1.0, 2.0*xy[1]-1.0)
        xy = (xy[0]/self.scale[0], xy[1]/self.scale[1])
        xy = (xy[0]-self.center[0], xy[1]-self.center[1])
        return xy
    #f uv_from_image_xyz
    def uv_from_image_xyz(self, xyz):
         proj=self.projection
         ui = proj.image_of_model(xyz)
         if ui is None:
             return None
         (uvzw,img_xy) = ui
         return (uvzw[0],uvzw[1])
    #f display_grid
    def display_grid(self):
        glLineWidth(1.0)
        glBegin(GL_LINES)
        for axis in range(3):
            for i in range(2*n+1):
                xyz0 = (0.,0.,float(i-n),0.,0.)[axis:axis+3]
                xyz1 = (0.,0.,float(i-n),0.,0.)[axis:axis+3]
                uv0 = self.uv_from_image_xyz(xyz0)
                uv1 = self.uv_from_image_xyz(xyz1)
                glVertex3f(uv0[0],uv0[1],-0.1)
                glVertex3f(uv1[0],uv1[1],-0.1)
                pass
            pass
        glEnd()
        pass
    #f display_points
    def display_points(self):
        c = self.epm.glow_colors[self.epm.glow_tick]
        glMaterialfv(GL_FRONT,GL_DIFFUSE,c)
        glMaterialfv(GL_FRONT,GL_AMBIENT,c)
        glDisable(GL_TEXTURE_2D)
        for m in self.epm.point_mapping_names:
            pt = self.point_mappings.get_xy(m, self.image_name)
            if pt is not None:
                glPushMatrix()
                glTranslate(pt[0],pt[1],-0.1)
                sc = 0.005/self.scale[0]
                if self.epm.point_mapping_names[self.epm.point_mapping_index]==m:
                    sc = sc * (1+2*(self.epm.tick%100)/100.0)
                    pass
                glRotate(self.epm.tick,0.0,0.0,1.0)
                glPushMatrix()
                glScale(sc,4*sc,1.0)
                glutSolidCube(1.0)
                glPopMatrix()
                glScale(4*sc,sc,1.0)
                glutSolidCube(1.0)
                glPopMatrix()
                pass
            pass
        pass
    #f display_projected_points
    def display_projected_points(self):
        if self.projection is None:
            return
        c = self.epm.glow_colors[self.epm.glow_tick]
        glMaterialfv(GL_FRONT,GL_DIFFUSE,c)
        glMaterialfv(GL_FRONT,GL_AMBIENT,c)
        glDisable(GL_TEXTURE_2D)
        for pt in self.epm.point_mapping_names:
            xyz = self.epm.point_mappings.get_xyz(pt)
            if xyz is not None:
                uv = self.uv_from_image_xyz(xyz)
                if uv is not None:
                    pt_uv = self.epm.point_mappings.get_xy(pt, self.image_name)
                    if pt_uv is not None:
                        glLineWidth(2.0)
                        glBegin(GL_LINES);
                        glVertex3f(uv[0],uv[1],-0.1)
                        glVertex3f(pt_uv[0],pt_uv[1],-0.1)
                        glEnd()
                        pass

                    glPushMatrix()
                    glTranslate(uv[0],uv[1],-0.1)
                    sc = 0.005/self.scale[0]
                    glRotate(-6*self.epm.tick,0.0,0.0,1.0)
                    glPushMatrix()
                    glScale(sc,4*sc,1.0)
                    glutSolidCube(1.0)
                    glPopMatrix()
                    glScale(4*sc,sc,1.0)
                    glutSolidCube(1.0)
                    glPopMatrix()
                    pass
                pass
            pass
        pass
    #f display
    def display(self):
        """
        Display the point map image with focus if required to the current OpenGL context
        """
        self.load_texture()

        if self.display_options["focus"]:
            if self.focus_object is not None:
                glMaterialfv(GL_FRONT,GL_DIFFUSE,[1.0,1.0,1.0,1.0])
                glMaterialfv(GL_FRONT,GL_AMBIENT,[1.0,1.0,1.0,1.0])
                glDisable(GL_TEXTURE_2D)
                self.focus_object.draw_opengl_surface()
                pass
            pass

        glPushMatrix()
        glScale(self.scale[0],self.scale[1],1.0)
        glTranslate(self.center[0],self.center[1],0.0)

        if self.display_options["grid"]:
            self.display_grid()
            pass

        if self.display_options["points"]:
            self.display_points()
            pass

        if self.display_options["projected_points"]:
            self.display_projected_points()
            pass

        if self.texture is not None:
            glBindTexture(GL_TEXTURE_2D, self.texture)
            pass

        if self.object is not None:
            glMaterialfv(GL_FRONT,GL_DIFFUSE,[1.0,1.0,1.0,1.0])
            glMaterialfv(GL_FRONT,GL_AMBIENT,[1.0,1.0,1.0,1.0])
            glEnable(GL_TEXTURE_2D)
            self.object.draw_opengl_surface()
            pass

        glPopMatrix()
        pass
    #f All done
    pass

#a c_edit_point_map_info
class c_edit_point_map_info(opengl_widget.c_opengl_container_widget):
    """
    This class represents an OpenGL widget that contains information frames for the edit point map

    It contains a set of subwidgets that are updated when the 'update' call is invoked
    """
    #f __init__
    def __init__(self, epm=None, pm=None, **kwargs):
        opengl_widget.c_opengl_container_widget.__init__(self, **kwargs)
        self.info_widget    = opengl_widget.c_opengl_simple_text_widget(og=epm)
        self.image_widget   = opengl_widget.c_opengl_simple_text_widget(og=epm)
        self.mapping_widget = opengl_widget.c_opengl_simple_text_widget(og=epm)
        self.epm = epm
        self.point_mappings = pm
        self.add_widget(self.info_widget,   map_xywh=( (0.0,0.0,6000.0,100.0), ( -1.0,0.9,2.0,-2*0.1) ) )
        self.add_widget(self.image_widget,  map_xywh=( (0.0,0.0,6000.0,4000.0), ( 0.0,0.7,2.0,-2*0.7) ) )
        self.add_widget(self.mapping_widget,map_xywh=( (0.0,0.0,6000.0,4000.0), (-1.0,0.7,2.0,-2*0.7) ) )
        pass
    #f update
    def update(self):
        info = ""
        cur_image = self.epm.displayed_images[self.epm.focus_image]
        image_data = self.epm.point_mappings.get_image_data(cur_image)
        info += "Image %s (%s) (use for pts %d)\n"%(cur_image, image_data["filename"], image_data["use_for_points"])
        cur_pt = self.epm.point_mapping_names[self.epm.point_mapping_index]
        xyz = self.point_mappings.get_xyz(cur_pt)
        if xyz is None:
            xyz = "<unknown>"
        else:
            xyz = "(%4f,%4f,%4f)"%(xyz[0],xyz[1],xyz[2])
        info += "Current pt '%s'\nXYZ: %s\n"%(cur_pt,xyz)
        info += "Scale %6f\n"%self.epm.last_scale
        self.info_widget.replace_text(info, baseline_xy=(0.0,64.0), scale=(1.0,1.0))

        import string
        image_list = self.point_mappings.get_images()
        image_list.sort()
        image_list = string.join(image_list,"\n")
        self.image_widget.replace_text(str(image_list), baseline_xy=(0.0,64.0), scale=(1.0,1.0))

        mapping_list = self.epm.point_mapping_names
        mapping_list.sort()
        mapping_list = string.join(mapping_list,"\n")
        self.mapping_widget.replace_text(mapping_list, baseline_xy=(0.0,64.0), scale=(1.0,1.0))
        pass
    #f All done
    pass

#a c_edit_point_map
class c_edit_point_map(opengl_app.c_opengl_app):
    """
    Top level class for the editing of point maps application

    
    """
    glow_colors = []
    n = 10
    r = 0.5
    for i in range(3):
        for j in range(n):
            v = r*j/float(n)
            glow_colors.append((1-r+v, 1-v, r, 1-r+v, 1-v)[i:i+3])
            pass
        pass

    #f __init__
    def __init__(self, point_mapping_filename, **kwargs):
        opengl_app.c_opengl_app.__init__(self, **kwargs)
        self.tick = 0
        self.aspect = 1.0
        self.zNear=1.0
        self.zFar=40.0
        self.images = {}
        self.undo_buffer = c_undo_buffer()
        self.image_projections = {}
        self.point_mapping_filename = point_mapping_filename
        self.last_scale = 0.01
        pass
    #f save_point_mapping
    def save_point_mapping(self, point_map_filename):
        if point_map_filename == self.original_point_map_filename:
            import os, time
            backup_name = self.original_point_map_filename+(".bkp_%d"%int(time.time()))
            os.rename(self.original_point_map_filename, backup_name)
            print "Backing up point mapping to '%s'"%backup_name
        self.point_mappings.save_data(point_map_filename)
        print "Saving point mapping to '%s'"%point_map_filename
        pass
    #f load_point_mapping
    def load_point_mapping(self, point_map_filename):
        self.original_point_map_filename = point_map_filename
        self.point_mappings.reset()
        self.point_mappings.load_data(point_map_filename)
        self.point_mapping_names = self.point_mappings.get_mapping_names()
        self.point_mapping_names.sort()
        self.point_mapping_index = 0
        pass
    #f load_images
    def load_images(self):
        image_names = self.point_mappings.get_images()
        for k in image_names:
            image_data = self.point_mappings.get_image_data(k)
            self.image_projections[k] = image_data["projection"]
            self.images[k] = c_edit_point_map_image(epm=self,
                                                    pm = self.point_mappings,
                                                    image_name=k,
                                                    filename=image_data["filename"],
                                                    projection = self.image_projections[k],
                                                    )
            pass
        pass
    #f opengl_post_init
    def opengl_post_init(self):
        font_dir = "../../fonts/"
        self.load_font(font_dir+"cabin-bold")
        self.point_mappings = c_point_mapping()
        self.load_point_mapping(self.point_mapping_filename)
        self.epm_info = c_edit_point_map_info(epm=self, pm=self.point_mappings)
        self.load_images()

        self.point_mappings.find_line_sets()
        self.point_mappings.approximate_positions()

        self.point_set_start_tick = None

        glutSetCursor(GLUT_CURSOR_CROSSHAIR)

        self.image_names = self.images.keys()
        self.image_names.sort()

        self.menus = opengl_menu.c_opengl_menu(callback=self.menu_select)
        self.menus.add_menu("images")
        for i in self.image_names:
            self.menus.add_item(i,("image",i))
            pass
        self.menus.add_menu("points")
        self.menus.add_hierarchical_select_menu("points",self.point_mapping_names, item_select_value=lambda x:("point",x))
        self.menus.add_menu("optimize")
        self.menus.add_item("Step size 1",("projection","small",1.0))
        self.menus.add_item("Step size 0.1",("projection","small",0.1))
        self.menus.add_item("Step size 0.01",("projection","small",0.01))
        self.menus.add_item("Step size 0.001",("projection","small",0.001))
        self.menus.add_item("Step size 1E-3",("projection","small",1E-3))
        self.menus.add_item("Step size 1E-4",("projection","small",1E-4))
        self.menus.add_item("Step size 1E-5",("projection","small",1E-5))
        self.menus.add_item("Step size 1E-6",("projection","small",1E-6))
        self.menus.add_item("Corners",("projection","corners",0))
        self.menus.add_item("References",("projection","references",0))
        self.menus.add_menu("main_menu")
        self.menus.add_submenu("Images","images")
        self.menus.add_submenu("Points","points")
        self.menus.add_submenu("Optimize","optimize")
        self.menus.add_item("Toggle image use",("use_for_points",0))
        self.menus.add_item("Save",("save",0))
        self.menus.create_opengl_menus()
        self.attach_menu(self.menus, "main_menu")

        self.displayed_images = [self.image_names[0], self.image_names[1]]
        self.focus_image = 0
        self.layers = opengl_layer.c_opengl_layer_set()
        self.image_layers = (self.layers.new_layer( (0,300,900,900), depth=10),
                             self.layers.new_layer( (900,300,900,900), depth=10 ))
        self.info_layer = self.layers.new_layer( (0,0,1800,300), depth=1, autoclear="all" )
        self.info_layer.add_contents(self.epm_info)

        for i in range(len(self.image_layers)):
            self.image_layers[i].add_contents(self.images[self.displayed_images[i]])
            self.images[self.displayed_images[i]].set_focus(False)
            pass
        self.images[self.displayed_images[self.focus_image]].set_focus(True)

        self.epm_info.update()

        pass
    #f display
    def display(self):
        self.tick += 1
        if self.point_set_start_tick is not None:
            if (self.tick - self.point_set_start_tick)==50:
                self.point_set_held()
                pass
            pass
        self.glow_tick = (self.tick/10) % len(self.glow_colors)
        glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)
        self.layers.display()
        glutSwapBuffers()
        pass
    #f shift_focus
    def shift_focus(self, fwd=True, focus_image=None):
        self.images[self.displayed_images[self.focus_image]].set_focus(False)
        self.focus_image += 1
        if not fwd:
            self.focus_image -= 2
            pass
        if focus_image is not None:
            self.focus_image = focus_image
            pass
        self.focus_image = self.focus_image % len(self.displayed_images)
        self.images[self.displayed_images[self.focus_image]].set_focus(True)
        pass
    #f adjust_image
    def adjust_image(self,sxyg, scale=1.0):
        if sxyg[3]:
            for image_name in self.displayed_images:
                self.images[image_name].focus_on_point(self.point_mapping_names[self.point_mapping_index])
                pass
            pass
        scale_xy = (sxyg[0]*scale,sxyg[0]*scale)
        self.images[self.displayed_images[self.focus_image]].adjust(scale=scale_xy, translate=(scale*sxyg[1]/20,scale*sxyg[2]/20) )
        pass
    #f change_point
    def change_point(self, adjustment=None, point_name=None ):
        if adjustment is not None:
            l = len(self.point_mapping_names)
            self.point_mapping_index = (self.point_mapping_index + adjustment[0]) % l
            pass
        if point_name is not None:
            if point_name in self.point_mapping_names:
                self.point_mapping_index = self.point_mapping_names.index(point_name)
                pass
            pass
        self.adjust_image((1.0,0.0,0.0,1))
        self.epm_info.update()
        pass
    #f do_undoable_operation
    def do_undoable_operation(self,op,undo=False,record=True):
        undo_data = None
        if op[0] == "add_uniform_image_location":
            if undo:
                self.point_mappings.undo_add_image_location(op[2],verbose=True)
                pass
            else:
                (pt_name, image_name, image_xy) = op[1]
                undo_data = self.point_mappings.add_image_location(pt_name,image_name,image_xy,uniform=True,verbose=True)
                pass
            pass
        elif op[0] == "delete_image_location":
            if undo:
                self.point_mappings.undo_delete_image_location(op[2],verbose=True)
                pass
            else:
                (pt_name, image_name) = op[1]
                undo_data = self.point_mappings.delete_image_location(pt_name,image_name,verbose=True)
                pass
            pass
        elif op[0] == "change_projection":
            (image_name, operation, scale) = op[1]
            if undo:
                self.point_mappings.set_projection(image=image_name, projection=op[2])
                print "Undo set projection",image_name,op[2]
                pass
            else:
                undo_data = self.point_mappings.get_projection(image=image_name)
                self.point_mappings.find_line_sets()
                self.point_mappings.approximate_positions()
                proj = self.point_mappings.images[image_name]["projection"]
                if operation in ["initial"]:
                    proj.guess_initial_projection_matrix(self.point_mappings)
                    pass
                elif operation in ["much"]:
                    proj.run_optimization(point_mappings=self.point_mappings, coarse=False)
                    pass
                elif operation in ["corners"]:
                    proj.optimize_projection_from_select_points(self.point_mappings, use_corners=True)
                    pass
                elif operation in ["references"]:
                    proj.optimize_projection_from_select_points(self.point_mappings, use_corners=False)
                    pass
                else: # "small"
                    self.point_mappings.optimize_projections(image=image_name, fov_iterations=1, orientation_iterations=200, camera_iterations=1, do_fov=False, do_camera=False, delta_scale=scale)
                    pass
                print "Set projection (through optimization)",image_name,self.point_mappings.get_projection(image=image_name)
                pass
            self.point_mappings.find_line_sets()
            self.point_mappings.approximate_positions()
            pass
        else:
            raise Exception("Unknown operation to perform '%s'"%str(op))
        if record:
            op = (op[0], op[1], undo_data)
            self.undo_buffer.add_operation( op )
            pass
        self.epm_info.update()
        pass
    #f undo_redo
    def undo_redo(self,redo=False):
        if redo:
            undo_op = self.undo_buffer.redo_operation()
            pass
        else:
            undo_op = self.undo_buffer.undo_operation()
            pass
        if undo_op is None: return
        (undo,op) = undo_op
        self.do_undoable_operation(op=op, undo=undo, record=False)
        pass
    #f point_set_start
    def point_set_start(self,image_name,xy,layer_xy,image_xy):
        self.point_set_start_tick = self.tick
        self.point_set_data = [False,image_name,xy,layer_xy,image_xy]
        pass
    #f point_set_held
    def point_set_held(self):
        self.point_set_data[0] = True
        pass
    #f point_set_end
    def point_set_end(self,image_name=None,xy=None,layer_xy=None,image_xy=None,pt_name=None):
        if image_name is None:
            self.point_set_start_tick = None
        if self.point_set_start_tick is None:
            return
        if not self.point_set_data[0]:
            return
        if (self.point_set_data[1] != image_name):
            return
        if pt_name is None:
            return
        self.do_undoable_operation( ("add_uniform_image_location",(pt_name,image_name,image_xy)) )
        pass
    #f point_delete
    def point_delete(self,image_name=None, pt_name=None):
        if image_name is None:
            return
        if pt_name is None:
            return
        self.do_undoable_operation( ("delete_image_location",(pt_name,image_name)) )
        pass
    #f change_projection
    def change_projection(self, image_name=None, operation="small", scale=None):
        if scale is None:
            scale = self.last_scale
            pass
        self.last_scale = scale
        self.do_undoable_operation( ("change_projection",(image_name,operation,scale)) )
        pass
    #f select_image
    def select_image(self, image_name, image=None):
        if image is None:
            image=self.focus_image
            pass
        print "Select",image_name,image
        prev_image_name = self.displayed_images[image]
        self.images[prev_image_name].set_focus(False)
        self.displayed_images[image] = image_name
        self.image_layers[image].clear_contents()
        self.image_layers[image].add_contents(self.images[image_name])
        if image==self.focus_image:
            self.images[image_name].set_focus(True)
            pass
        self.epm_info.update()
        pass
    #f test
    def test(self, image_name, pt_name):
        proj = self.point_mappings.images[image_name]["projection"]
        proj.blah(self.point_mappings)
        pass
    #f menu_select
    def menu_select(self, menu, value):
        if type(value)==tuple:
            if value[0]=="image":
                self.select_image(value[1])
                return True
            if value[0]=="point":
                self.change_point(point_name=value[1])
                return True
            if value[0]=="projection":
                self.change_projection(image_name=self.displayed_images[self.focus_image], operation=value[1], scale=value[2])
                return True
            if value[0]=="use_for_points":
                self.point_mappings.use_for_points(image=self.displayed_images[self.focus_image], toggle=True)
                self.epm_info.update()
                return True
            if value[0]=="save":
                self.save_point_mapping(self.point_mapping_filename)
                return True
            pass
        print menu, value
        return True
    #f keypress
    def keypress(self,k,m,x,y):
        sc = 1.0
        if (m & GLUT_ACTIVE_SHIFT): sc=4.0
        image_controls = {"D":(1.0,-sc,0.0,0),
                          "d":(1.0,-sc,0.0,0),
                          "a":(1.0,+sc,0.0,0),
                          "A":(1.0,+sc,0.0,0),
                          "w":(1.0,0.0,-sc,0),
                          "W":(1.0,0.0,-sc,0),
                          "s":(1.0,0.0,+sc,0),
                          "S":(1.0,0.0,+sc,0),
                          "=":(1.05*sc,0.0,0.0,0),
                          "+":(1.05*sc,0.0,0.0,0),
                          "-":(1/1.05/sc,0.0,0.0,0),
                          "_":(1/1.05/sc,0.0,0.0,0),
                          "1":(-1.0,0.0,0.0,0),
                          "g":(1.0,0.0,0.0,1),
                          }
        point_controls = {".":(-1,),
                          ";":(+1,),
                          }
        image_name = self.displayed_images[self.focus_image]
        pt_name = self.point_mapping_names[self.point_mapping_index]

        if ord(k)==27:
            self.point_set_end()
            return True
        if k in ["t"]:
            self.test(image_name=image_name, pt_name=pt_name)
            return True
        if k in ["F"]:
            self.change_projection(image_name=image_name, operation="corners", scale=0)
            return True
        if k in ["f"]:
            self.point_mappings.find_line_sets()
            self.point_mappings.approximate_positions()
            for n in self.point_mappings.line_sets:
                print n, 
                print "positions:",self.point_mappings.positions[n]
                print "line meetings:", self.point_mappings.line_sets[n].line_meetings
                print "weighted_points:", self.point_mappings.line_sets[n].weighted_points
                #for meet in self.point_mappings.line_sets[n].line_meetings:
                #    (p0,p1,g,d) = meet
                #    proj = self.point_mappings.images['left']["projection"]
                #    print proj.image_of_model(p0)
                #    print proj.image_of_model(p1)
                pass
            pass
        if k in ["o", "O"]:
            op = "small"
            if k == "O": op="much"
            self.change_projection(image_name=image_name, operation=op)
            return True
        if k in ["i"]:
            self.change_projection(image_name=image_name, operation="initial")
            return True
        if (ord(k)==127) and (m&GLUT_ACTIVE_CTRL):
            self.point_delete(image_name=image_name, pt_name=pt_name)
            return True
        if k in ["u", "U"]:
            self.undo_redo(redo=(k=="U"))
            return True
        if (k=='\t') or (ord(k)==25):
            fwd = True
            if (m & GLUT_ACTIVE_SHIFT): fwd=False
            self.shift_focus(fwd)
            return True
        if k in image_controls:
            self.adjust_image(image_controls[k])
            return True
        if k in point_controls:
            self.change_point(adjustment=point_controls[k])
            return True
        if k in ["n", "p"]:
            i = self.image_names.index(image_name) + 1
            if k=="p": i-=2
            i = i%len(self.image_names)
            self.select_image(image_name=self.image_names[i])
            return True
        print ord(k),x,y
        pass
    #f mouse
    def mouse(self,b,s,m,x,y):
        xy = (x,y)
        layers = self.layers.find_layers_at_xy(xy)
        if len(layers)==0:
            self.point_set_end()
            return True
        l = layers[0]
        for i in range(len(self.image_layers)):
            if l==self.image_layers[i]:
                layer_xy = l.scaled_xy(xy)
                image_name = self.displayed_images[i]
                epmi = self.images[image_name]
                image_xy = epmi.uniform_xy(layer_xy)
                if (m & GLUT_ACTIVE_SHIFT) and (b=="left") and (s=="down"):
                    closest_pt = (1000000, None, None)
                    for p in self.point_mapping_names:
                        pt = self.point_mappings.get_xy(p, image_name)
                        if pt is not None:
                            dxy = (pt[0]-image_xy[0])*(pt[0]-image_xy[0]) + (pt[1]-image_xy[1])*(pt[1]-image_xy[1])
                            if dxy<closest_pt[0]:
                                closest_pt = (dxy, p, pt)
                                pass
                            pass
                        pass
                    if closest_pt[1] is not None:
                        self.shift_focus(focus_image=i)
                        self.change_point(point_name=closest_pt[1])
                        pass
                    self.point_set_end()
                    return True
                if (b=="left") and (s=="down"):
                    self.shift_focus(focus_image=i)
                    self.point_set_start(image_name,xy,layer_xy,image_xy)
                    return True
                if (b=="left") and (s=="up"):
                    self.point_set_end(image_name,xy,layer_xy,image_xy,self.point_mapping_names[self.point_mapping_index])
                    return True
                self.point_set_end()
                pass
            pass
        pass
    pass

#a Main
def main():
    help_text = "Help"
    parser = argparse.ArgumentParser(
        description='Point map editor for 3D-from-photos.',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=help_text)#textwrap.dedent(help_text))

    parser.add_argument('-wh', '--window-size', dest='ws',
                        help='Window size')
    parser.add_argument('-m', '--map', dest='map', default=None,
                        help='Map filename')
    args = parser.parse_args()

    if args.map is None:
        args.map = "corridor.map"
    m = c_edit_point_map( point_mapping_filename=args.map,
                          window_size = (1800,1100))
    m.init_opengl()
    m.main_loop()

if __name__ == '__main__':
    main()

