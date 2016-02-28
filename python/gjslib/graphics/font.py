#!/usr/bin/env python

#a Imports
import gjslib.math.bezier as bezier
import gjslib.math.mesh as mesh
from PIL import Image
import math

#a Classes
#c c_glyph
class c_glyph( object ):
    """
    An outline font glyph has the following attributes:

    name - name of the glyph, not used internally
    unichr - unicode character that the glyph represents
    metrics - dictionary of key->value, keys of
      advance_width     - amount to move X on after the glyph is rendered
      left_side_bearing - X displacement for rendering (e.g. letter y may have -ve value)
      xMin              - X bounding box minimum value
      xMax              - X bounding box maximum value
      yMin              - Y bounding box minimum value
      yMax              - Y bounding box maximum value
    glyph - contours making the outline
    mesh - mesh of triangles created from bezier curves
    """
    #f __init__
    def __init__( self, unichr, name ):
        self.name = name
        self.unichr = unichr
        self.metrics = {}
        self.glyph = None
        self.mesh = None
        pass
    #f ttx_get_element_by_name
    def ttx_get_element_by_name( self, node, tag_name, name ):
        for m in node.getElementsByTagName(tag_name):
            if m.getAttribute("name")==name:
                return m
            pass
        return None
    #f ttx_get_int_attributes
    def ttx_get_int_attributes( self, node, name_map ):
        r = {}
        for t in name_map:
            x = node.getAttribute(t)
            try:
                if x is not None: r[name_map[t]] = int(x)
            except:
                r[name_map[t]] = None
            pass
        return r
    #f ttx_get_metrics
    def ttx_get_metrics( self, hmtx ):
        # lsb is left-side-bearing;
        # advance width is x-addition to next glyph
        glyph = self.ttx_get_element_by_name(hmtx,"mtx",self.name)
        if glyph is None:
            return
        self.metrics = self.ttx_get_int_attributes(glyph, {"width":"advance_width", "lsb":"left_side_bearing"})
        return
    #f ttx_get_glyph
    def ttx_get_glyph( self, glyf ):
        """
        Get contours for a glyph and any other components

        Currently does not handle components
        <TTGlyph name="agrave" xMin="8" yMin="-15" xMax="386" yMax="658">
          <component glyphName="a" x="4" y="0" flags="0x4"/>
          <component glyphName="grave" x="189" y="-164" flags="0x4"/>
        </TTGlyph>
        """
        glyph = self.ttx_get_element_by_name(glyf, "TTGlyph", self.name)
        if glyph is None:
            return None
        r = self.ttx_get_int_attributes( glyph, {"xMin":"xMin", "yMin":"yMin", "xMax":"xMax", "yMax":"yMax"} )
        self.metrics["xMin"] = r["xMin"]
        self.metrics["xMax"] = r["xMax"]
        self.metrics["yMin"] = r["yMin"]
        self.metrics["yMax"] = r["yMax"]
        contours = []
        for c in glyph.getElementsByTagName("contour"):
            pts = []
            last = None
            def add_point(x,y,on,last,pts=pts):
                if last is not None:
                    if (not last["on"]) and (not on):
                        pts.append(((last["x"]+x)/2.0, (last["y"]+y)/2.0))
                        pass
                    elif (last["on"]) and (on):
                        pts.append(((last["x"]+x)/2.0, (last["y"]+y)/2.0))
                        pass
                pts.append( (x,y) )
                return  {"x":x, "y":y, "on":on}
            for p in c.getElementsByTagName("pt"):
                x  = int(p.getAttribute("x"))
                y  = int(p.getAttribute("y"))
                on = int(p.getAttribute("on"))
                if last is None:
                    first_point = (x,y,on)
                    pass
                last = add_point(x,y,on,last)
                pass
            last = add_point( first_point[0], first_point[1], first_point[2], last )
            contours.append(pts)
            pass
        self.glyph = contours
        pass
    #f create_bezier_lists
    def create_bezier_lists( self ):
        bezier_lists = []
        for c in self.glyph:
            beziers = []
            i = 0
            p0 = c0 = p1 = None
            while i<len(c):
                (p0,c0,p1) = (c0,p1,bezier.c_point(coords=c[i]))
                if ((i&1)==0) and p0 is not None:
                    beziers.append( bezier.c_bezier2( pts=(p0,c0,p1) ) )
                    pass
                i += 1
                pass
            bezier_lists.append(beziers)
            pass
        return bezier_lists
    #f create_straight_lines
    def create_straight_lines(self, straightness=50):
        lines = []
        contours = self.create_bezier_lists()
        for bl in contours:
            points = []
            lines.append(points)
            for b in bl:
                subbeziers = b.break_into_segments(straightness)
                for s in subbeziers:
                    points.append(s.pts[0])
                    pass
                pass
            pass
        return lines
    #f get_mesh
    def get_mesh( self, straightness=50 ):
        if self.mesh is not None: return self.mesh
        m = mesh.c_mesh()
        contours = self.create_bezier_lists()
        for bl in contours:
            m.add_bezier_list_contour( bezier_list=bl, closed=True, contour_data=None, straightness=straightness )
            pass
        m.map_contours_to_mesh()
        m.normalize()
        m.fill_convex_hull_with_triangles()
        m.remove_small_lines(min_length=0.01)
        m.remove_small_area_triangles( min_area=0.01)
        for i in range(10):
            if m.shorten_quad_diagonals()==0: break
            pass
        for i in range(10):
            m.ensure_contours_on_mesh()
            m.shorten_quad_diagonals()
            m.remove_small_lines(min_length=0.01)
            m.remove_small_area_triangles( min_area=0.01)
            pass
        m.assign_winding_order_to_contours()
        m.assign_winding_order_to_mesh()
        #m.check_consistent()
        self.mesh = m
        return m
    #f get_bbox
    def get_bbox( self ):
        if self.metrics["xMax"] is None: return (0,0,0,0)
        if self.metrics["xMin"] is None: return (0,0,0,0)
        if self.metrics["yMax"] is None: return (0,0,0,0)
        if self.metrics["yMin"] is None: return (0,0,0,0)
        lx = self.metrics["xMin"]
        w = self.metrics["xMax"] - self.metrics["xMin"]
        if w<0:
            w=-w
            lx = self.metrics["xMax"]
            pass
        by = self.metrics["yMin"]
        h = self.metrics["yMax"] - self.metrics["yMin"]
        if h<0:
            h=-h
            by = self.metrics["xMin"]
            pass
        return (lx,by,w,h)
    #f get_metrics
    def get_metrics( self ):
        r = {"lx":0, "by":0, "w":0, "h":0, "advance_width":0, "left_side_bearing":0}
        if "xMin" in self.metrics:
            r["lx"] = self.metrics["xMin"]
            if "xMax" in self.metrics:
                r["w"] = self.metrics["xMax"] - self.metrics["xMin"]
                pass
            pass
        if "yMin" in self.metrics:
            r["by"] = self.metrics["yMin"]
            if "yMax" in self.metrics:
                r["h"] = self.metrics["yMax"] - self.metrics["yMin"]
                pass
            pass
        if "advance_width" in self.metrics:
            r["advance_width"] = self.metrics["advance_width"]
            pass
        if "left_side_bearing" in self.metrics:
            r["left_side_bearing"] = self.metrics["left_side_bearing"]
            pass
        return r
    #f draw
    def draw(self, size=(60,60), metrics={"MaxWidth":1.0, "MaxHeight":1.0}, straightness=100):
        import draw
        d = draw.c_draw_buffer(size=size,mode="1")
        lines = self.create_straight_lines(straightness=straightness)
        scale = (size[0]/float(metrics["MaxWidth"]), size[1]/float(metrics["MaxHeight"]))
        offset = (-float(self.metrics["xMin"])*scale[0], -float(self.metrics["yMin"])*scale[1])
        scale = (scale[0],-scale[1])
        offset = (offset[0],size[1]-offset[1])
        paths = []
        for l in lines:
            paths.append([])
            for p in l:
                paths[-1].append(p.get_coords(offset=offset,scale=scale))
                pass
            pass
        d.fill_paths(paths=paths,value=255)
        return d
    #f __repr__
    def __repr__( self ):
        result = "glyph '%s' ('%s') : %s : %s"%(self.unichr,self.name,str(self.metrics),str(self.glyph))
        return result

#c c_bitmap_font
class c_bitmap_font(object):
    """
    Font metric data needs a header with a font name (64 characters), glyph size w,h (8-bits each, pixels), glyph bbox aspect ratio (2.14 fixed point), glyphs wide and glyphs high (8 bits each),  and number of glyphs (16 bits)
    Then a list of glyphs with 16B per glyph
    This is 32-bit unicode, glyph number in bitmap, X,Y pixel offset of (0,0) in glyph space (2.14 fixed point), and (w,h) in pixels
    Total size is 128 for first header (generous) and 16B per glyph
    If the smallest image is 16x16 then a character is 32B of storage
    """
    #f __init__
    def __init__(self):
        self.image = None
        self.fontname = "font"
        self.glyph_data = {}
        self.glyph_names = []
        pass
    #f get_bitmap_data
    def get_bitmap_data(self):
        return self.image.getdata()
    #f offset
    def offset(self, offset):
        return (offset%self.image_size[0], offset/self.image_size[0])
    #f header_read_byte
    def header_read_byte(self, offset):
        value=self.image.getpixel(offset)
        if (offset[0]==self.image_size[0]-1):
            offset = (0,offset[1]+1)
            pass
        else:
            offset = (offset[0]+1,offset[1])
            pass
        return (offset,value)
    #f header_read_int
    def header_read_int(self, offset, num_bytes=1):
        value = 0
        for i in range(num_bytes):
            (offset,v) = self.header_read_byte(offset)
            value = value | (v<<(8*i))
        return (offset, value)
    #f header_read_signed_int
    def header_read_signed_int(self, offset, num_bytes=1):
        value = 0
        for i in range(num_bytes):
            (offset,v) = self.header_read_byte(offset)
            value = value | (v<<(8*i))
            pass
        if (value>>(8*num_bytes-1)):
            value = value - (1<<(8*num_bytes))
            pass
        return (offset, value)
    #f header_read_unicode
    def header_read_unicode(self, offset):
        (offset, v) = self.header_read_int(offset, num_bytes=4)
        return (offset, unichr(v))
    #f header_read_string
    def header_read_string(self, offset, num_bytes=1):
        r = ""
        for i in range(num_bytes):
            (offset, v) = self.header_read_byte(offset)
            if v!=0:
                r += chr(v)
                pass
            pass
        return (offset, r)
    #f header_write_byte
    def header_write_byte(self, offset, value):
        self.image.putpixel(offset,value)
        if (offset[0]==self.image_size[0]-1):
            return (0,offset[1]+1)
        return (offset[0]+1,offset[1])
    #f header_write_int
    def header_write_int(self, offset, value, num_bytes=1):
        for i in range(num_bytes):
            offset = self.header_write_byte(offset,value&0xff)
            value = value >> 8
        return offset
    #f header_write_unicode
    def header_write_unicode(self, offset, value):
        return self.header_write_int(offset, ord(value), num_bytes=4)
    #f header_write_string
    def header_write_string(self, offset, value, num_bytes=1):
        for i in range(num_bytes):
            if i>=len(value):
                offset = self.header_write_byte(offset,0)
                pass
            else:
                offset = self.header_write_byte(offset,ord(value[i]))
                pass
            pass
        return offset
    #f read_header
    def read_header(self):
        self.glyph_size = [0,0]
        self.array_size = [0,0]
        self.glyph_data = {}
        self.glyph_names = []
        offset = self.offset(0)
        (offset, self.fontname)      = self.header_read_string(offset, 64)
        (offset, num_glyphs)         = self.header_read_int(offset, 2)
        (offset, self.glyph_size[0]) = self.header_read_int(offset, 1)
        (offset, self.glyph_size[1]) = self.header_read_int(offset, 1)
        (offset, self.array_size[0]) = self.header_read_int(offset, 1)
        (offset, self.array_size[1]) = self.header_read_int(offset, 1)
        (offset, self.ascent)        = self.header_read_signed_int(offset, 2)
        (offset, self.descent)       = self.header_read_signed_int(offset, 2)
        (offset, self.line_gap)      = self.header_read_int(offset, 2)
        (offset, self.line_spacing)  = self.header_read_int(offset, 2)
        #offset = self.header_write_int(offset, 1<<14, 2)
        for i in range(num_glyphs):
            offset = self.offset(128 + 16*i)
            gd = {}
            gd["metrics"] = {"lx":0,"by":0,"w":0,"h":0, "advance_width":0, "left_side_bearing":0}
            (offset,gn)            = self.header_read_unicode(offset)
            (offset,gd["metrics"]["lx"]) = self.header_read_signed_int(offset,2)
            (offset,gd["metrics"]["by"]) = self.header_read_signed_int(offset,2)
            (offset,gd["metrics"]["w"]) = self.header_read_int(offset,2)
            (offset,gd["metrics"]["h"]) = self.header_read_int(offset,2)
            (offset,gd["metrics"]["advance_width"]) = self.header_read_signed_int(offset,2)
            (offset,gd["metrics"]["left_side_bearing"]) = self.header_read_signed_int(offset,2)
            self.glyph_names.append(gn)
            gd["index"] = i
            gd["gx"] = self.glyph_size[0] * (  gd["index"]%self.array_size[0])
            gd["gy"] = self.glyph_size[1] * (1+gd["index"]/self.array_size[0])
            self.glyph_data[gn] = gd
            #print gn, gd
            pass
        pass
    #f set_header
    def set_header(self):
        offset = self.offset(0)
        offset = self.header_write_string(offset, self.fontname, 64)
        offset = self.header_write_int(offset, len(self.glyph_data), 2)
        offset = self.header_write_int(offset, self.glyph_size[0], 1)
        offset = self.header_write_int(offset, self.glyph_size[1], 1)
        offset = self.header_write_int(offset, self.array_size[0], 1)
        offset = self.header_write_int(offset, self.array_size[1], 1)
        offset = self.header_write_int(offset, self.ascent, 2)
        offset = self.header_write_int(offset, self.descent, 2)
        offset = self.header_write_int(offset, self.line_gap, 2)
        offset = self.header_write_int(offset, self.line_spacing, 2)
        offset = self.header_write_int(offset, 1<<14, 2)
        i = 0
        for gn in self.glyph_names:
            offset = self.offset(128 + 16*i)
            gd = self.glyph_data[gn]
            offset = self.header_write_unicode(offset, gn)
            offset = self.header_write_int(offset,gd["metrics"]["lx"],2)
            offset = self.header_write_int(offset,gd["metrics"]["by"],2)
            offset = self.header_write_int(offset,gd["metrics"]["w"],2)
            offset = self.header_write_int(offset,gd["metrics"]["h"],2)
            offset = self.header_write_int(offset,gd["metrics"]["advance_width"],2)
            offset = self.header_write_int(offset,gd["metrics"]["left_side_bearing"],2)
            i += 1
            pass
        pass
    #f load
    def load(self, filename):
        self.image = Image.open(filename+".png")
        self.image_size = self.image.size
        self.read_header()
        pass
    #f save
    def save(self, filename):
        self.set_header()
        self.image.save(filename+".png")
        pass
    #f new_from_glyphs
    def new_from_glyphs(self, fontname="font", font_metrics={}, glyph_names=('a'), glyph_size=(32,32) ):
        self.fontname = fontname
        self.glyph_names = glyph_names
        n = len(glyph_names)
        header_byte_size = 128 + 16*n
        glyph_byte_size = glyph_size[0]*glyph_size[1]
        gw = 1+int(math.sqrt(n))
        if gw < 1+((header_byte_size-1)/glyph_byte_size):
            gw = 1+((header_byte_size-1)/glyph_byte_size)
            pass
        gh = 2+(len(glyph_names)-1)/gw
        ysc = float(glyph_size[1]) / font_metrics["MaxHeight"]
        xsc = float(glyph_size[0]) / font_metrics["MaxWidth"]
        self.line_gap = int(font_metrics["line_gap"] * ysc)
        self.ascent   = int(font_metrics["ascent"] * ysc)
        self.descent  = int(font_metrics["descent"] * ysc)
        self.line_spacing = int((font_metrics["line_gap"]+font_metrics["ascent"]-font_metrics["descent"]) * ysc)
        self.array_size = (gw, gh)
        self.glyph_size = glyph_size
        self.image_size = (gw*glyph_size[0], gh*glyph_size[1])
        self.image = Image.new(mode="L",size=self.image_size,color="black")
        self.bitmap = self.image.load()
        self.glyph_data = {}
        i = 0
        for gn in glyph_names:
            self.glyph_data[gn] = {"index":i}
            self.glyph_data[gn]["gx"] = i%gw
            self.glyph_data[gn]["gy"] = 1+(i/gw)
            #print gn, self.glyph_data[gn]
            i += 1
            pass
        pass
    #f set_glyph
    def set_glyph(self, glyph_name, image=None, metrics={"lx":0,"by":0,"w":0,"h":0, "advance_width":0, "left_side_bearing":0}):
        if glyph_name not in self.glyph_data:
            raise Exception("Glyph '%s' not in font"%glyph_name)

        glyph_index = self.glyph_data[glyph_name]["index"]
        tlx = self.glyph_size[0] * (glyph_index%self.array_size[0])
        tly = self.glyph_size[1] * (1+(glyph_index/self.array_size[0]))
        if image is not None:
            self.image.paste(image,(tlx,tly))
            pass
        self.glyph_data[glyph_name]["metrics"] = metrics
        pass

    #f map_char
    def map_char(self, unichar, baseline_xy, scale=(1.0,1.0)):
        r = {}
        #r["src_uv"] = (x,y,w,h)
        #r["tgt_xy"] = (x,y,w,h)
        #r["adv"] =
        if unichar not in self.glyph_data:
            return {"src_uv":None, "tgt_xy":None, "adv":self.ascent/4*scale[0]}
        gd = self.glyph_data[unichar]
        metrics = gd["metrics"]
        tgt_x = baseline_xy[0] + metrics["left_side_bearing"]*scale[0]
        tgt_y = baseline_xy[1]-(metrics["h"]+metrics["by"])*scale[1]
        tgt_w = metrics["w"]*scale[0]
        tgt_h = metrics["h"]*scale[1]
        src_u = gd["gx"]
        src_v = gd["gy"] + self.glyph_size[1]-metrics["h"]
        src_w = metrics["w"]
        src_h = metrics["h"]
        src_u = src_u / float(self.glyph_size[0]*self.array_size[0])
        src_v = src_v / float(self.glyph_size[1]*self.array_size[1])
        src_w = src_w / float(self.glyph_size[0]*self.array_size[0])
        src_h = src_h / float(self.glyph_size[1]*self.array_size[1])
        r["tgt_xy"] = (tgt_x, tgt_y, tgt_w, tgt_h)
        r["src_uv"] = (src_u, src_v, src_w, src_h)
        r["adv"] = metrics["advance_width"]*scale[0]
        return r
    #f blit_glyph
    def blit_glyph(self, glyph_name, image, baseline_xy, scale=(1.0,1.0)):
        if glyph_name not in self.glyph_data:
            return baseline_xy
        gd = self.glyph_data[glyph_name]
        metrics = gd["metrics"]
        #print glyph_name, gd["index"],metrics
        tgt_pixels = image.load()
        tgt_size = image.size
        tgt_x = baseline_xy[0] + metrics["left_side_bearing"]*scale[0]
        tgt_y = baseline_xy[1]-(metrics["h"]+metrics["by"])*scale[1]
        tgt_w = int(metrics["w"]*scale[0])
        tgt_h = int(metrics["h"]*scale[1])

        src_pixels = self.image.load()
        src_x = gd["gx"]
        src_y = gd["gy"] + self.glyph_size[1]-metrics["h"]
        #print glyph_name, self.image_size, src_x, src_y, tgt_x, tgt_y, tgt_size
        for dy in range(tgt_h):
            if tgt_y+dy<0: continue
            if tgt_y+dy>=tgt_size[1]: break
            for dx in range(tgt_w):
                if tgt_x+dx<0: continue
                if tgt_x+dx>=tgt_size[0]: break
                v = src_pixels[src_x+int(dx/scale[0]),src_y+int(dy/scale[1])]
                if v!=0:
                    tgt_pixels[tgt_x+dx,tgt_y+dy] = v
                    pass
                pass
            pass
        return (baseline_xy[0]+int(metrics["advance_width"]*scale[0]), baseline_xy[1])
    #f blit_string
    def blit_string(self, text, image, baseline_xy, scale=(1.0,1.0), interword_spacing=0.25):
        for u in text:
            if u == " ":
                baseline_xy = (baseline_xy[0]+int(self.glyph_size[0]*scale[0]*interword_spacing),baseline_xy[1])
                continue
            else:
                baseline_xy = self.blit_glyph(u, image, baseline_xy, scale=scale)
                #baseline_xy = (baseline_xy[0]+int(self.glyph_size[0]*scale[0]*interletter_spacing),baseline_xy[1])
            pass
        return baseline_xy
    #f All done
    pass
#c c_font
class c_font( object ):
    """
    A simple font class to permit font handling particularly for OpenGL

    It uses a fairly simple internal data structure, which can be loaded from a pickled structure of from a TTX fonts

    TTX Fonts can be created from TTF fonts (TrueType) using a static method

    Many TTF fonts are available, and OSX and Windows use TTF.
    No hinting support is provided in this class, as the rendering is expected to be used in OpenGL (for which hints are pointless)

    A c_font has the following attributes:
    glyphs: dictionary of unicode -> c_glyph
    
    """
    #f convert_ttf_to_ttx
    @staticmethod
    def convert_ttf_to_ttx( ttf_filename, ttx_filename ):
        import fontTools.ttLib
        tt = fontTools.ttLib.TTFont(ttf_filename)
        tt.saveXML(ttx_filename)
        pass
    #f __init__
    def __init__( self, font_name ):
        self.font_name = font_name
        self.glyphs = {}
        self.map = {}
        self.metrics = {}
        pass
    #f ttx_get_metrics
    def ttx_get_metrics( self, hhea ):
        #<ascent value="965"/>
        #<descent value="-250"/>
        #<lineGap value="0"/>
        ascent   = hhea.getElementsByTagName("ascent")[0]
        descent  = hhea.getElementsByTagName("descent")[0]
        line_gap = hhea.getElementsByTagName("lineGap")[0]
        self.metrics["ascent"] = int(ascent.getAttribute("value"))
        self.metrics["descent"] = int(descent.getAttribute("value"))
        self.metrics["line_gap"] = int(line_gap.getAttribute("value"))
        return
    #f ttx_get_map
    def ttx_get_map(self, ttx):
        #<cmap, cmap_format_4, map code="hex unicode" name=glyph_name
        unicode_to_name_map = {}
        cmap = ttx.getElementsByTagName("cmap")[0]
        cmap = cmap.getElementsByTagName("cmap_format_4")[0]
        for m in cmap.getElementsByTagName("map"):
            s = m.getAttribute("code")
            if s[0:2]=="0x":
                u = int(s[2:],16)
                pass
            else:
                u=int(s)
                pass
            glyph_char = unichr(u)
            glyph_name = m.getAttribute("name")
            unicode_to_name_map[glyph_char] = glyph_name
            pass
        return unicode_to_name_map
    #f load_from_ttx
    def load_from_ttx( self, ttx_filename ):
        from xml.dom.minidom import parse
        ttx = parse(ttx_filename)
        unicode_to_name_map = self.ttx_get_map(ttx)
        glyph_order = ttx.getElementsByTagName("GlyphOrder").item(0)

        hhea = ttx.getElementsByTagName("hhea").item(0)
        hmtx = ttx.getElementsByTagName("hmtx").item(0)
        glyf = ttx.getElementsByTagName("glyf").item(0)

        self.glyphs = {}
        self.ttx_get_metrics(hhea)
        for (gu,gn) in unicode_to_name_map.iteritems():
            self.glyphs[gu] = c_glyph(gu,gn)
            self.glyphs[gu].ttx_get_metrics(hmtx)
            self.glyphs[gu].ttx_get_glyph(glyf)
            pass

        return self
    #f get_glyph_unichrs
    def get_glyph_unichrs(self):
        return self.glyphs.keys()
    #f get_glyph_bbox
    def get_glyph_bbox( self, glyph_unichr ):
        glyph = self.glyphs[glyph_unichr]
        return glyph.get_bbox()
    #f get_glyph_metrics
    def get_glyph_metrics( self, glyph_name ):
        glyph = self.glyphs[glyph_name]
        return glyph.get_metrics()
    #f get_metrics
    def get_metrics( self, glyph_unichrs=None ):
        metrics = {}
        metrics["MaxWidth"] = 0
        metrics["MaxHeight"] = 0
        metrics["ascent"]   = self.metrics["ascent"]
        metrics["descent"]  = self.metrics["descent"]
        metrics["line_gap"] = self.metrics["line_gap"]

        font_glyph_unichrs = self.get_glyph_unichrs()
        for gu in glyph_unichrs:
            if gu in font_glyph_unichrs:
                b = self.glyphs[gu].get_bbox()
                if b[2] > metrics["MaxWidth"]:  metrics["MaxWidth"] = b[2]
                if b[3] > metrics["MaxHeight"]: metrics["MaxHeight"] = b[3]
                pass
            pass
        return metrics
    #f create_bezier_lists
    def create_bezier_lists( self, glyph_name ):
        glyph = self.glyphs[glyph_name]
        return glyph.create_bezier_lists()
    #f create_straight_lines
    def create_straight_lines( self, glyph_name, straightness=50 ):
        glyph = self.glyphs[glyph_name]
        return glyph.create_straight_lines(straightness=straightness)
    #f get_mesh
    def get_mesh( self, glyph_name, straightness=50 ):
        glyph = self.glyphs[glyph_name]
        return glyph.get_mesh( straightness=straightness )
    #f generate_bitmap
    def generate_bitmap(self, size=(64,64), glyphs='ab', straightness=10):
        font_glyphs = self.get_glyph_unichrs()
        accepted_glyphs = []
        for gu in glyphs:
            if gu in font_glyphs:
                accepted_glyphs.append(gu)
                pass
            pass
        glyphs = accepted_glyphs

        font_metrics = self.get_metrics(glyph_unichrs=glyphs)
        bitmap_font = c_bitmap_font()
        bitmap_font.new_from_glyphs(fontname="font",
                                    font_metrics = font_metrics,
                                    glyph_names=glyphs,
                                    glyph_size=size
                                    )
        for gn in glyphs:
            if gn not in self.glyphs:
                continue
            glyph_metrics = self.get_glyph_metrics(gn)
            d = self.glyphs[gn].draw(size=size, metrics=font_metrics, straightness=straightness)
            glyph_metrics = {"advance_width":size[0]*glyph_metrics["advance_width"]/font_metrics["MaxWidth"],
                             "left_side_bearing":size[0]*glyph_metrics["left_side_bearing"]/font_metrics["MaxWidth"],
                             "lx":size[0]*glyph_metrics["lx"]/font_metrics["MaxWidth"],
                             "by":size[1]*glyph_metrics["by"]/font_metrics["MaxHeight"],
                             "w":size[0]*glyph_metrics["w"]/font_metrics["MaxWidth"],
                             "h":size[1]*glyph_metrics["h"]/font_metrics["MaxHeight"],}
            bitmap_font.set_glyph(gn, image=d.get_image(), metrics=glyph_metrics)
            pass
        return bitmap_font

#a Test functions
#f test_convert_ttx_to_ttf    
def test_convert_ttx_to_ttf(ttf_filename="../../fonts/cabin/Cabin-Bold-TTF.ttf",
                            ttx_filename="../../fonts/cabin-bold.ttx"):
    return c_font.convert_ttf_to_ttx(ttf_filename=ttf_filename,
                                  ttx_filename=ttx_filename)

#f test_show_glyph_data
def test_show_glyph_data(ttx_filename):
    f = c_font("fred")
    f.load_from_ttx(ttx_filename)
    for gu in f.get_glyph_unichrs():
        print gn, f.get_glyph_bbox(glyph_unichr=gu)
        pass
    pass

#f test_get_bezier
def test_get_bezier(ttx_filename, gn):
    f = c_font("fred")
    f.load_from_ttx(ttx_filename)
    print
    print "Beziers",f.create_bezier_lists(gn)
    lines = f.create_straight_lines(gn,straightness=100)
    print
    print "Straightness 100", lines
    lines = f.create_straight_lines(gn,straightness=1)
    print
    print "Straightness 1", lines
    pass

#f test_draw_glyph
def test_draw_glyph(ttx_filename, gn):
    import draw
    f = c_font("fred")
    f.load_from_ttx(ttx_filename)
    d = draw.c_draw_buffer(size=(60,60),bytes_per_pixel=1)
    print
    print "Beziers",f.create_bezier_lists(gn)
    lines = f.create_straight_lines(gn,straightness=100)
    paths = []
    for l in lines:
        paths.append([])
        for p in l:
            paths[-1].append(p.get_coords(offset=(0.0,55.0),scale=(60.0/700.0,-60.0/700.0)))
            pass
        pass
    print paths
    d.fill_paths(paths=paths,value=255)
    print d
    pass

#f test_draw_glyph_set
def test_draw_glyph_set(ttx_filename, names):
    import draw
    f = c_font("fred")
    f.load_from_ttx(ttx_filename)
    d = draw.c_draw_buffer(size=(60,60))
    metrics = f.get_metrics(glyph_unichrs=names)
    for gn in names:
        d = f.glyphs[gn].draw(size=(120,120),metrics=metrics)
        print d.string_scale(2)
        pass
    pass

#f test_create_bitmap_font
def test_create_bitmap_font(ttx_filename, glyphs, bitmap_filename):
    f = c_font("fred")
    f.load_from_ttx(ttx_filename)
    bf = f.generate_bitmap(size=(128,128), glyphs=glyphs)
    bf.save(bitmap_filename)
    pass

#f test_use_bitmap_font
def test_use_bitmap_font(bitmap_filename, text="Test text"):
    import draw
    d = draw.c_draw_buffer(size=(1024,1024),mode="L")
    bf = c_bitmap_font()
    bf.load(bitmap_filename)
    lines = text.split("\n")
    scale=(0.5,0.5)
    ln = 0
    for l in lines:
        l.rstrip()
        bf.blit_string(l, d.get_image(), (8,64+bf.line_spacing*ln*scale[1]), scale=scale)
        ln += 1
        pass
    print d.string_scale(8)
    d.save(filename="blah.png")
    pass

#a Toplevel
if __name__=="__main__":
    test_text  = "It is a period of civil war.\n"
    test_text += "Rebel spaceships, striking\n"
    test_text += "from a hidden base, have won\n"
    test_text += "their first victory against\n"
    test_text += "the evil Galactic Empire.\n"
    test_text += "\n"
    test_text += "During the battle, Rebel spies\n"
    test_text += "managed to steal secret plans\n"
    test_text += "to the Empire's ultimate weapon,\n"
    test_text += "the DEATH STAR, an armored space\n"
    test_text += "station with enough power to\n"
    test_text += "destroy an entire planet.\n"
    test_text += "\n"
    test_text += "Pursued by the Empire's sinister\n"
    test_text += "agents, Princess Leia races\n"
    test_text += "home aboard her starship,\n"
    test_text += "custodian of the stolen plans\n"
    test_text += "that can save her people and\n"
    test_text += "restore freedom to the galaxy...."
    font_dir = "../../fonts/"
    font_data = {}
    font_data["cabin-bold"] = {"ttf_name":"cabin/Cabin-Bold-TTF.ttf",
                               "ttx_name":"cabin-bold.ttx",
                               "bitmap_name":"cabin-bold"}
    font_data["sf"] = {"ttf_name":"SF Old Republic SC Bold.ttf",
                       "ttx_name":"sf-old-rep-bold.ttx",
                       "bitmap_name":"sf-old-rep-bold"}
    font_data["beneg"] = {"ttf_name":"beneg___.ttf",
                       "ttx_name":"beneg.ttx",
                       "bitmap_name":"beneg"}

    fd = font_data["cabin-bold"]
    #fd = font_data["sf"]
    #fd = font_data["beneg"]
    ttf_name = fd["ttf_name"]
    ttx_name = fd["ttx_name"]
    bitmap_name = fd["bitmap_name"]
    if False:
        test_convert_ttx_to_ttf(ttf_filename=font_dir+ttf_name,
                                ttx_filename=font_dir+ttx_name)
        pass
    if False:
        test_show_glyph_data(ttx_filename=font_dir+ttx_name)
        pass
    if False:
        test_get_bezier(ttx_filename=font_dir+ttx_name, gn=u'D')
        pass
    if False:
        test_draw_glyph(ttx_filename=font_dir+ttx_name, gn=u'D')
        pass
    if False:
        test_draw_glyph_set(ttx_filename=font_dir+ttx_name, names = (u'A', u'B', u'C', u'D', u'E', u'F', u'Q', u'M'))
        pass
    if True:
        test_create_bitmap_font(ttx_filename=font_dir+ttx_name,
                                glyphs=("abcdefghijklmnopqrstuvwxyz"+
                                             "ABCDEFGHIJKLMNOPQRSTUVWXYZ"+
                                             "0123456789.,!?_-+*="),
                                bitmap_filename=font_dir+bitmap_name)
        pass
    if True:
        test_use_bitmap_font(bitmap_filename=font_dir+bitmap_name,
                             text = test_text)
        pass
