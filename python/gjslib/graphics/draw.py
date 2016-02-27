#!/usr/bin/env python
#a Imports
from PIL import Image

#a Classes
#c c_line
class c_line(object):
    #f __init__
    def __init__(self,l):
        self.tl = (l[0],l[1])
        self.br = (l[2],l[3])
        if ((l[1] > l[3]) or
            ((l[1]==l[3]) and (l[0]>l[2]))):
            self.tl = (l[2],l[3])
            self.br = (l[0],l[1])
            pass
        self.dx = l[2]-l[0]
        self.dy = l[3]-l[1]
        pass
    #f x_at_y
    def x_at_y(self, y):
        if self.dy==0: return 0
        #print y, y-self.tl[1], ((y-self.tl[1]) * self.dx) / self.dy
        return ((y-self.tl[1]) * self.dx) / self.dy + self.tl[0]
    #f __repr__
    def __repr__(self):
        r = "( (%d,%d), (%d,%d) )"%(self.tl[0],self.tl[1], self.br[0],self.br[1])
        return r
    pass

#c c_draw_buffer
class c_draw_buffer(object):
    #f __init__
    def __init__(self, mode="RGB", size=(10,10), color=None, filename=None):
        self.image = None
        if filename is not None:
            self.image = Image.open(png_filename)
            self.size = self.image.size
            self.mode = self.image.mode
            pass
        else:
            self.image = Image.new(mode,size,color)
            self.size = size
            self.mode = mode
            pass
        pass
    #f pixel - get pixel value at (x,y)
    def pixel(self,x,y):
        if (x<0) or (y<0) or (x>=self.size[0]) or (y>=self.size[1]): return 0
        return self.image.getpixel((x,y))
    #f set_pixel - set pixel value at (x,y)
    def set_pixel(self,x,y,value=255):
        if (x<0) or (y<0) or (x>=self.size[0]) or (y>=self.size[1]): return
        self.image.putpixel((x,y), value)
        return
    #f draw_line - draw zero-width line
    def draw_line(self,l,resolution_bits=16,value=255):
        """
        # Should we move to (px+1,py) or (px,py+1)?
        # What is current error? it is x-(px<<resolution_bits), (y-py<<resolution_bits)
        # Note that points all have x,y such that (x-x0)/(y-y0) = (x1-x0)/(y1-y0)
        # Hence (x-x0).(y1-y0) = (x1-x0).(y-y0) ; dy.(x-x0) = dx.(y-y0)
        # We keep track of error = dy.(x-x0) - dx.(y-y0)
        # First, if dx is 0 then always move +1 in the Y
        # If error<0 then we have to move +1 in the X
        # If error>0 then we have to move +1 in the Y
        # If error==0 then we have a choice - do X+1 if |dx|>|dy|
        """
        d = 1<<resolution_bits
        l = c_line( (int(l[0]*d),
                     int(l[1]*d),
                     int(l[2]*d),
                     int(l[3]*d)) )
        (x,y) = l.tl
        (dx,dy) = (l.br[0] - l.tl[0], l.br[1] - l.tl[1])
        px = x>>resolution_bits
        py = y>>resolution_bits
        # dy >=0; if dy==0, dx>=0
        self.set_pixel(px,py,value)
        ex = (x-(px<<resolution_bits))
        ey = (y-(py<<resolution_bits))
        sdx = 1
        if dx<0:
            sdx = -1
            pass
        error = (ex*dy - ey*dx*sdx)>>resolution_bits
        while True:
            error_xp1 = error+dy
            error_yp1 = error-dx*sdx
            if (error_xp1<0): error_xp1=-error_xp1
            if (error_yp1<0): error_yp1=-error_yp1
            if (error_xp1<error_yp1):
                error += dy
                px += 1*sdx
                pass
            else:
                error -= dx*sdx
                py += 1
                pass
            self.set_pixel(px,py,value)
            if py > (l.br[1]>>resolution_bits):
                break
            if py == (l.br[1]>>resolution_bits):
                if sdx*(px - (l.br[0]>>resolution_bits)) >= 0:
                    break
                pass
            pass
        pass
    #f fill_paths
    def fill_paths(self, paths, resolution_bits=16, value=255, winding_rule=0):
        """
        paths is a set of lists of points
        Each path is implicitly closed

        The algorithm is to generate a set of lines from the paths
        Sort the lines so lowest top-left y is first; this is the 'ready list'
        Start with an empty 'active lines' set
        For each y pixel line (can start at y=pixel line of first in ready list)
        1. determine if the first of the ready list should be activated; if so, activate
        and move on to the next in the ready list
        2. for all the lines in the active set determine if the line:
        2a. is now inactive (i.e. pixel y >= bottom y), in which case deactivate
        2b. crosses at pixel y - and return its X coordinate
        Note that horizontal lines on a pixel y immediately deactivate
        Now sort the returned X coordinates, and draw rows of pixels according to the winding rule at pixel Y
        Move down a line
        Continue until ready list and active set are all empty
        """
        d = 1<<resolution_bits
        ready_list = []
        for p in paths:
            if len(p)<2: continue
            last_pt = (int(p[-1][0]*d), int(p[-1][1]*d))
            for pt in p:
                pt = (int(pt[0]*d), int(pt[1]*d))
                ready_list.append( c_line((pt[0],pt[1],last_pt[0],last_pt[1])) )
                last_pt = pt
                pass
            pass
        if len(ready_list)<1:
            return
        def sort_lines(l0,l1):
            if (l0.tl[1]<=l1.tl[1]): return -1
            return 1
        ready_list.sort(cmp=sort_lines)
        active_set = set()
        py = (ready_list[0].tl[1])>>resolution_bits
        y = py << resolution_bits
        while (len(ready_list)>0) or (len(active_set)>0):
            while len(ready_list)>0:
                if ready_list[0].tl[1] > y:
                    break
                active_set.add(ready_list.pop(0))
                pass
            lines_complete = []
            x_crossings = []
            for l in active_set:
                if y >= l.br[1]:
                    lines_complete.append(l)
                    pass
                else:
                    x_crossings.append(l.x_at_y(y))
                    pass
                pass
            for l in lines_complete:
                active_set.remove(l)
                pass
            x_crossings.sort()
            rpx = None
            for i in range(len(x_crossings)):
                lpx = rpx
                rpx = x_crossings[i] >> resolution_bits
                if (i%2)==1:
                    for x in range(rpx-lpx):
                        self.set_pixel(lpx+x,py,value)
                        pass
                    pass
                pass

            #print py, x_crossings
            py += 1
            y += 1<<resolution_bits
            pass
        pass
    #f string_scale
    def string_scale(self,scale=1):
        w = self.size[0]/scale
        h = self.size[1]/scale
        r = ""
        for y in range(h):
            l = ""
            for x in range(w):
                v = 0
                for i in range(scale):
                    for j in range(scale):
                        v += self.pixel(x*scale+i,y*scale+j)
                        pass
                    pass
                v = v / (scale*scale)
                if (v>255):v=255
                v = v/64
                l += " -+#"[v]
                pass
            r += l + "\n"
            pass
        return r
    #f __repr__
    def __repr__(self):
        r = ""
        for y in range(self.size[1]):
            l = ""
            for x in range(self.size[0]):
                v = self.pixel(x,y)
                if (v>128):
                    l+="*"
                    pass
                elif (v>0):
                    l+="."
                    pass
                else:
                    l+=" "
                    pass
                pass
            r += l + "\n"
            pass
        return r
    #f Done
    pass

#a Toplevel
if __name__=="__main__":
    d = c_draw_buffer(mode="1",size=(80,80))
    d.set_pixel(16,16)
    d.fill_paths( [((10,10), (70,10), (70,70), (10,70)),
                   ((40,10), (10,40), (40,70), (70,40)),
                   ],value=64 )
    if True:
        d.draw_line( (0,0,80,0), value=64 )
        d.draw_line( (0,0,0,80), value=64 )
        d.draw_line( (79,0,79,79), value=64 )
        d.draw_line( (79,79,0,79), value=64 )
        d.draw_line( (40,40,60,35) )
        d.draw_line( (40,40,60,45) )
        d.draw_line( (40,40,20,35) )
        d.draw_line( (40,40,20,45) )
        d.draw_line( (40,40,45,20) )
        d.draw_line( (40,40,35,20) )
        d.draw_line( (40,40,45,60) )
        d.draw_line( (40,40,35,60) )
        pass
    print d


