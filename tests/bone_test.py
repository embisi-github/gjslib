#!/usr/bin/arch -32 /System/Library/Frameworks/Python.framework/Versions/2.7/bin/python
#a Imports
import sys, os
import pygame
import pygame_test

sys.path.insert(0, os.path.abspath('../python'))
#import gjslib.graphics.bone as bone

#a Test stuff
def main():
    global ship
    import sample_ship
    import imp
    imp.reload(sample_ship)
    ship = sample_ship.build_ship()

    print ship.create_dependencies(  )
    dependent_expression_list = ship.collate_dependencies()
    undefined_vars = {}
    dependent_vars = {}
    for t in dependent_expression_list:
        (node,id,deps,defs) = t
        for d in defs:
            if d not in undefined_vars: undefined_vars[d] = []
            undefined_vars[d].append( t )
            for p in deps:
                if p in defs: continue
                if p not in dependent_vars: dependent_vars[p] = []
                if d not in dependent_vars[p]:
                    dependent_vars[p].append(d)
                    pass
                pass
            pass
        pass
    print "undefined_vars", undefined_vars
    i = 0
    for d in undefined_vars.keys():
        id = d.instance().get_implicit_dependents()
        if len(id)>0:
            for i in id:
                if i not in undefined_vars: undefined_vars[i] = []
                undefined_vars[i].append( (None, "imp", [d], [i] ) )
                pass
            pass
        pass
    print "dependent_vars", dependent_vars
    defined_vars = {}
    for d in dependent_vars:
        if d not in undefined_vars:
            defined_vars[d] = 0
            pass
        pass
    print defined_vars
    predefined_vars = defined_vars.copy()
    ordered_expressions = []
    stage = 0
    while len(undefined_vars)>0:
        stage = stage + 1
        undefined_vars_list = undefined_vars.keys()
        n = len(undefined_vars_list)
        for d in undefined_vars_list:
            can_define = True
            if d not in undefined_vars: continue
            for t in undefined_vars[d]:
                (node,id,deps,defs) = t
                for dd in deps:
                    if (dd in undefined_vars_list) and (dd not in defs):
                        can_define = False
                        break
                    pass
                pass
            if can_define:
                tl = undefined_vars[d]
                for t in tl:
                    (node,id,deps,defs) = t
                    ordered_expressions.append(t)
                    for dd in defs:
                        if dd in undefined_vars:
                            del undefined_vars[dd]
                            pass
                        defined_vars[dd] = stage
                        pass
                    pass
                pass
            pass
        if len(undefined_vars)==n:
            raise Exception("Cyclic dependency chain:%s"%(str(undefined_vars_list)))
        pass
    print defined_vars
    print ordered_expressions
    expr_deps = predefined_vars
    expr_defs = defined_vars
    for d in expr_deps:
        if d in expr_defs:
            del expr_defs[d]
    expr_deps = expr_deps.keys()
    expr_defs = expr_defs.keys()
    expressions = []
    for t in ordered_expressions:
        (node,id,deps,defs) = t
        if node is not None:
            expressions.append( (node,id) )
            pass
        pass
    print expr_deps
    print expr_defs
    print expressions

    for (node,id) in expressions:
        node.evaluate_expressions( ids=(id,) )
        pass

#a Toplevel
def draw_fn( screen ):
    pygame.font.init()
    pyfont = pygame.font.SysFont(u'palatino',10)
    def screen_coords( pt, scale=-50, offset=500 ):
        c = pt.get_coords()
        return (c[0]*scale+offset,c[1]*scale+offset)
    def draw_cb( node, show_bones=False ):
        if node.has_instance:
            vis = node.instance().visualization()
            if vis[0] == "vector":
                p = pyfont.render(node.name,False,(0,0,0))
                #screen.blit(p,screen_coords(vis[1]))
                pass
            elif vis[0] == "bezier":
                bez = vis[1]
                last_pt = None
                if show_bones or ("bone" not in vis[3].parent.name):
                    for i in range(40+1):
                        pt = screen_coords(bez.coord((i+0.0)/40))
                        if last_pt is not None:
                            screen.draw_line( last_pt[0],last_pt[1],pt[0], pt[1], (0,0,0,255) )
                            pass
                        last_pt = pt
                        pass
                    pass
                pass
            pass
        pass
    screen.fill((255,255,255))
    ship.iterate(draw_cb)
    pass

if __name__ == '__main__':
    main()
    def key_fn(k):
        if k==pygame.K_q: return True
        if k==pygame.K_r:
            main()
            return False
        print k
        return False
    pygame_test.pygame_display( draw_fn=draw_fn, key_fn=key_fn )
