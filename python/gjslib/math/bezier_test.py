#!/usr/bin/env python
#a Imports
import pygame
import sys
import socket

import bezier

#for i in range(11):
#    for j in range(11):
#        print i,j,bp.coord(i/10.0,j/10.0)
#        pass
#    pass
#asdjh

#a Drawing functions
#c c_screen
class c_screen( object ):
    def __init__( self, screen ):
        self.screen = screen
        pass
    def draw_line( self, x0, y0, x1, y1, color ):
        draw_line( self.screen, x0, y0, x1, y1, color )
        pass
    def draw_dot( self, x, y, color ):
        draw_dot( self.screen, x, y, color )
        pass

#f draw_dot
def draw_dot( screen, x, y, color ):
    screen.fill(color, rect=(x,y,1,1) )

#f draw_line
def draw_line( screen, x0, y0, x1, y1, color ):
    if (x0>x1): return draw_line( screen, x1, y1, x0, y0, color )
    dx = x1-x0
    dy = y1-y0
    if (dy>0) and (dx>=dy):  return draw_line_by_dx( screen, x0, y0, dx, dy, +1, color )
    if (dy<=0) and (dx>=-dy): return draw_line_by_dx( screen, x0, y0, dx, -dy, -1, color )
    if (dy<0): (x0,y0,x1,y1) = (x1,y1,x0,y0)
    dx = x1-x0
    dy = y1-y0
    if (dx>0):
        return draw_line_by_dy( screen, x0, y0, dx, dy, +1, color )
    return draw_line_by_dy( screen, x0, y0, -dx, dy, -1, color )

#f draw_line_by_dx
def draw_line_by_dx( screen, x, y, dx, dy, pdy, color ):
    """Called if dx>=dy"""
    px = int(x)
    py = int(y)
    error = -(dx/2)
    for i in range(int(dx)):
        draw_dot(screen,px,py,color)
        px = px+1
        error = error + dy
        if error>0:
            py=py+pdy
            error = error-dx
            pass
        pass
    pass

#f draw_line_by_dy
def draw_line_by_dy( screen, x, y, dx, dy, pdx, color ):
    """Called if dy>dx"""
    px = int(x)
    py = int(y)
    error = -(dy/2)
    for i in range(int(dy)):
        draw_dot(screen,px,py,color)
        py = py+1
        error = error + dx
        if error>0:
            px=px+pdx
            error = error-dy
            pass
        pass
    pass

#f draw_world
def draw_world(screen, object_lists):
    screen.draw_line( 0,0, 100,100, (128,128,128,255) )
    screen.draw_line( 200,150, 100,100, (128,128,128,255) )
    screen.draw_line( 200,150, 300,600, (128,128,128,255) )
    for ol in object_lists:
        for o in ol:
            o.draw(screen)
            pass
        pass
    pass

#a Toplevel
(w,h) = (640,400)
max_straightness = 2

screen = pygame.display.set_mode((w,h),pygame.DOUBLEBUF|pygame.HWSURFACE)
my_screen = c_screen(screen)

import time
beziers = []

beziers.append( bezier.c_bezier( (100,100), (400,100), (0,50), (0,-50) ) )
beziers.append( bezier.c_bezier( (400,100), (600,100), (0,-50), (0,150) ) )
beziers.append( bezier.c_bezier( (300,300), (300,100), (200,0), (-200,0) ) )
beziers.append( bezier.c_bezier( (300,300), (300,100), (-200,0), (200,0) ) )

split_beziers = []
for b in beziers:
    splits = [b]
    while len(splits)>0:
        a = splits.pop(0)
        if a.straightness()<max_straightness:
            split_beziers.append(a)
            pass
        else:
            (b0,b1) = a.split()
            splits.append(b0)
            splits.append(b1)
            pass
        pass
    pass
print split_beziers
def loop():
    alive = True
    while alive:
        times = [ time.time() ]
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit();
                pass
            pass

        draw_world( my_screen, (split_beziers,) )
        #draw_world( my_screen, (beziers, split_beziers) )
        #draw_world( my_screen, (beziers,) )

        pygame.display.flip()
        msElapsed = clock.tick(15)
        pass
    pass

clock = pygame.time.Clock()
loop()
