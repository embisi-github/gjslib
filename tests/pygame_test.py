#!/usr/bin/arch -32 /System/Library/Frameworks/Python.framework/Versions/2.7/bin/python
#!/usr/bin/env python
#a Imports
import pygame

#a Drawing functions
#c c_screen
class c_screen( object ):
    def __init__( self, screen ):
        self.screen = screen
        pass
    def draw_line( self, x0, y0, x1, y1, color ):
        pygame.draw.line(self.screen, color, (x0,y0), (x1,y1) )
        pass
    def draw_dot( self, x, y, color ):
        draw_dot( self.screen, x, y, color )
        pass
    def fill_polygon( self, points_list, color ):
        pygame.draw.polygon(self.screen, color, points_list )
        pass
    def blit( self, surface, coords ):
        self.screen.blit( surface, coords )
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
            screen.draw_line( o.pts[0].coords[0],1000-o.pts[0].coords[1],
                       o.pts[2].coords[0], 1000-o.pts[2].coords[1], (o.s*50,255,255,255) )
            pass
        pass
    pass

#f draw_polygons
def draw_polygons(screen, polygons):
    for poly in polygons[0],:
        last_pt = poly[-1]
        last_pt = None
        for pt in poly:
            if last_pt is not None:
                screen.draw_line( last_pt.coords[0],last_pt.coords[1],
                                  pt.coords[0], pt.coords[1], (255,128,128,255) )
            last_pt = pt
            pass
        points_list = []
        for pt in poly:
            points_list.append( (pt.coords[0], pt.coords[1]) )
            pass
        screen.fill_polygon( points_list, (128,255,128,255) )
        pass
    pass

#f draw_triangles
def draw_triangles(screen, triangles, scale=(1,1), offset=(0,0), font=None):
    i = 0
    num = len(triangles)
    text_list = []
    for t in triangles:
        points_list = []
        brightness = 100
        if t.winding_order is not None and t.winding_order>0: brightness=255
        centre = [0,0]
        for pt in t.get_points():
            c = pt.coords()
            (x,y) = (c[0]*scale[0]+offset[0], c[1]*scale[1]+offset[1])            
            centre[0] += x/3.0
            centre[1] += y/3.0
            points_list.append( (x,y) )
            pass
        screen.fill_polygon( points_list, (brightness*i/num,brightness-brightness*i/num,brightness,255) )
        if font is not None:
            text_list.append( (centre, str(t.triangle_num)) )
            pass
        i+=1
        pass
    for (centre, text) in text_list:
        p = font.render(text,False,(255,255,255))
        screen.blit(p,centre)
        pass
    pass

#f draw_contour
def draw_contour(screen, polygon, scale=(1,1), offset=(0,0)):
    i = 0
    for l in polygon.line_segments:
        #if not l.on_contour: continue
        coords = []
        for pt in l.get_points():
            c = pt.coords()
            coords.append( c[0]*scale[0]+offset[0] )
            coords.append( c[1]*scale[1]+offset[1] )
            pass
        screen.draw_line( coords[0], coords[1], coords[2], coords[3], (64,255,64,255) )
    pass

#a Toplevel functions
def pygame_display( draw_fn, tick_ms=30, (w,h)=(1000,1000) ):
    screen = pygame.display.set_mode((w,h),pygame.DOUBLEBUF|pygame.HWSURFACE)
    my_screen = c_screen(screen)
    def loop():
        import sys
        alive = True
        while alive:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit(); sys.exit();
                    pass
                if event.type == pygame.KEYDOWN:
                    if event.key==pygame.K_q:
                        pygame.quit(); sys.exit();
                pass
            draw_fn( my_screen )
            pygame.display.flip()
            msElapsed = clock.tick(tick_ms)
            pass
        pass
    clock = pygame.time.Clock()
    loop()
    pass
