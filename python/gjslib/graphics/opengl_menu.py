#!/usr/bin/env python

#a Imports
from OpenGL.GLUT import *

#a Class for c_opengl_menu
#c c_opengl_menu
class c_opengl_menu(object):
    #f __init__
    def __init__(self, callback=None):
        self.reset()
        self.callback = callback
        pass
    #f reset
    def reset(self):
        self.ids = []
        self.last_menu = None
        self.menus = {}
        self.menu_gluts = {}
        self.dependencies = {}
        pass
    #f add_menu
    def add_menu(self, menu_name):
        self.menus[menu_name] = []
        self.last_menu = menu_name
        self.dependencies[menu_name] = []
        pass
    #f add_item
    def add_item(self,text,item_id, menu_name=None):
        if menu_name is None: menu_name=self.last_menu
        self.last_menu = menu_name
        self.menus[menu_name].append((text,len(self.ids)))
        self.ids.append(item_id)
        pass
    #f add_submenu
    def add_submenu(self,text,submenu_name,menu_name=None):
        if menu_name is None: menu_name=self.last_menu
        self.last_menu = menu_name
        self.menus[menu_name].append((text,submenu_name))
        self.dependencies[menu_name].append(submenu_name)
        return
    #f add_hierarchical_select_menu
    def add_hierarchical_select_menu(self, menu_name, items, item_select_value):
        name_prefix = ""
        menu_stack = [(menu_name, "")]
        for item_name in items:
            # First pop menu_stack until we have a matching prefix
            npl = len(name_prefix)
            while (npl>0) and (name_prefix[:npl]!=item_name[:npl]):
                #print "Pop",npl,name_prefix,item_name
                (m,name_prefix) = menu_stack.pop()
                npl = len(name_prefix)
                pass
            # Push menu for first dot
            while "." in item_name[npl:]:
                spl = item_name[npl:].index(".")
                name_prefix = item_name[:npl+spl+1]
                menu_name = "points."+name_prefix[:-1]
                #print "Add submenu entry to '%s' text '%s' submenu '%s'"%(menu_stack[-1][0],name_prefix[npl:npl+spl],menu_name)
                self.add_submenu(name_prefix[npl:npl+spl],"points."+name_prefix[:-1],menu_name=menu_stack[-1][0])
                self.add_menu(menu_name)
                menu_stack.append( (menu_name,name_prefix[:npl]) )
                npl = len(name_prefix)
                pass
            # Add menu item
            #print "Add item '%s' (point %s) to menu '%s'"%(item_name[npl:],item_name,menu_stack[-1][0])
            self.add_item(item_name[npl:],item_select_value(item_name),menu_name=menu_stack[-1][0])
            pass
        pass
    #f glut_id
    def glut_id(self, name):
        return self.menu_gluts[name]
    #f menu_callback
    def menu_callback(self, name, x):
        if (x>=0) and (x<len(self.ids)):
            x = self.ids[x]
            pass
        if self.callback is not None:
            self.callback(name,x)
            pass
        return 0
    #f destroy_opengl_menus
    def destroy_opengl_menus(self):
        if len(self.menu_gluts)==0:
            return
        glutDetachMenu()
        for n in self.menu_gluts:
            glutDeleteMenu(self.menu_gluts[n])
            pass
        self.menu_gluts = {}
        pass
    #f order_menus
    def order_menus(self):
        self.menu_order_list = []
        while len(self.dependencies)>len(self.menu_order_list):
            ordered = 0
            for m in self.dependencies:
                if m in self.menu_order_list:
                    continue
                found = True
                for d in self.dependencies[m]:
                    if d not in self.menu_order_list:
                        found = False
                        break
                    pass
                if found:
                    self.menu_order_list.append(m)
                    ordered += 1
                    pass
                pass
            if ordered==0:
                raise Exception("Circular dependency in menu list")
            pass
        pass
    #f create_opengl_menus
    def create_opengl_menus(self):
        self.destroy_opengl_menus()
        self.order_menus()
        for name in self.menu_order_list:
            items = self.menus[name]
            m = glutCreateMenu(lambda x:self.menu_callback(name,x))
            self.menu_gluts[name] = m
            for (text,item) in items:
                if type(item)==int:
                    glutAddMenuEntry(text, item)
                    pass
                else:
                    if item not in self.menu_gluts:
                        raise Exception("Failed to find submenu '%s' in menus",item)
                    glutAddSubMenu(text, self.menu_gluts[item])
                    pass
                pass
            pass
        pass
