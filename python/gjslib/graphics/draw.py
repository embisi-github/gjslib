#!/usr/bin/env python
#a Imports

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
        pass
    pass

#c c_draw_buffer
class c_draw_buffer(object):
    #f __init__
    def __init__(self, size=(100,100), bytes_per_pixel=1):
        self.size = size
        self.bytes_per_pixel = bytes_per_pixel
        self.buffer = bytearray(size[0]*size[1]*bytes_per_pixel)
        pass
    #f pixel - get pixel value at (x,y)
    def pixel(self,x,y):
        v = 0
        if (x<0) or (y<0) or (x>=self.size[0]) or (y>=self.size[1]): return 0
        p = (y*self.size[0]+x)*self.bytes_per_pixel
        for i in range(self.bytes_per_pixel):
            v = (v<<8) | self.buffer[p]
            p += 1
            pass
        return v
    #f set_pixel - set pixel value at (x,y)
    def set_pixel(self,x,y,value=255):
        v = 0
        if (x<0) or (y<0) or (x>=self.size[0]) or (y>=self.size[1]): return
        p = (y*self.size[0]+x)*self.bytes_per_pixel
        for i in range(self.bytes_per_pixel):
            self.buffer[p] = value&0xff
            value = value>>8
            p += 1
            pass
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
    #f __repr__
    def __repr__(self):
        r = "draw_buffer\n"
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
    d = c_draw_buffer(size=(80,80),bytes_per_pixel=1)
    d.set_pixel(16,16)
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
    print d


