#!/usr/bin/env python

#a Imports

#a Class for c_opengl
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
        self.menu_list = []
        self.menu_gluts = {}
        pass
    #f add_menu
    def add_menu(self, menu_name):
        self.menu_list.append( (menu_name,[]) )
        pass
    #f add_menu_item
    def add_menu_item(self,text,item_id):
        self.menu_list[-1][1].append((text,len(self.ids)))
        self.ids.append(item_id)
        pass
    #f add_menu_submenu
    def add_menu_submenu(self,text,menu_name):
        self.menu_list[-1].append( (text,menu_name) )
        return
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
        pass
    #f destroy_opengl_menus
    def destroy_opengl_menus(self):
        if len(self.menus)==0:
            return
        glutDetachMenu()
        for n in self.menu_gluts:
            glutDeleteMenu(self.menu_gluts[n])
            pass
        self.menu_gluts = {}
        pass
    #f create_opengl_menus
    def create_opengl_menus(self):
        self.destroy_opengl_menus()
        for (name, items) in self.menu_list:
            m = glutCreateMenu(lambda x:self.menu_callback(name,x))
            self.menu_gluts[name] = m
            for (text,item) in items:
                if type(item)==int:
                    glutAddMenuEntry(text, item)
                    pass
                else:
                    glutAddSubMenu(text, self.menu_gluts[name])
                    pass
                pass
            pass
        pass
