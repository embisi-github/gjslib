#!/usr/bin/env python

#a Imports
import gjslib.math.bezier as bezier
import gjslib.math.mesh as mesh

#c Classes
#c c_glyph
class c_glyph( object ):
    #f __init__
    def __init__( self, name ):
        self.name = name
        self.metrics = {}
        self.glyph = {}
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
    def ttx_get_int_attributes( self, node, names ):
        r = {}
        for t in names:
            x = node.getAttribute(t)
            try:
                if x is not None: r[t] = int(x)
            except:
                r[t] = None
            pass
        return r
    #f ttx_get_metrics
    def ttx_get_metrics( self, hmtx ):
        glyph = self.ttx_get_element_by_name(hmtx,"mtx",self.name)
        if glyph is None:
            return
        self.metrics = self.ttx_get_int_attributes(glyph, ("width", "lsb"))
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
        glyph = self.ttx_get_element_by_name( glyf, "TTGlyph", self.name )
        if glyph is None:
            return None
        r = self.ttx_get_int_attributes( glyph, ("xMin", "yMin", "xMax", "yMax") )
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
        r["contours"] = contours
        self.glyph = r
        pass
    #f create_bezier_lists
    def create_bezier_lists( self ):
        bezier_lists = []
        for c in self.glyph["contours"]:
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
        if self.glyph["xMax"] is None: return (0,0,0,0)
        if self.glyph["xMin"] is None: return (0,0,0,0)
        if self.glyph["yMax"] is None: return (0,0,0,0)
        if self.glyph["yMin"] is None: return (0,0,0,0)
        lx = self.glyph["xMin"]
        w = self.glyph["xMax"] - self.glyph["xMin"]
        if w<0:
            w=-w
            lx = self.glyph["xMax"]
            pass
        by = self.glyph["yMin"]
        h = self.glyph["yMax"] - self.glyph["yMin"]
        if h<0:
            h=-h
            by = self.glyph["xMin"]
            pass
        return (lx,by,w,h)
    #f draw
    def draw(self, size=(60,60), bbox=(0.0,0.0,600.0,600.0), straightness=100):
        import draw
        d = draw.c_draw_buffer(size=size,bytes_per_pixel=1)
        lines = self.create_straight_lines(straightness=straightness)
        scale = (size[0]/float(bbox[2]), size[1]/float(bbox[3]))
        offset = (-float(bbox[0])*scale[0], -float(bbox[1])*scale[1])
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
        result = "glyph '%s' : %s : %s"%(self.name,str(self.metrics),str(self.glyph))
        return result

#c c_font
class c_font( object ):
    """
    A simple font class to permit font handling particularly for OpenGL

    It uses a fairly simple internal data structure, which can be loaded from a pickled structure of from a TTX fonts

    TTX Fonts can be created from TTF fonts (TrueType) using a static method

    Many TTF fonts are available, and OSX and Windows use TTF.
    No hinting support is provided in this class, as the rendering is expected to be used in OpenGL (for which hints are pointless)
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
        pass
    #f load_from_ttx
    def load_from_ttx( self, ttx_filename ):
        from xml.dom.minidom import parse
        ttx = parse(ttx_filename)
        glyph_order = ttx.getElementsByTagName("GlyphOrder").item(0)
        self.glyphs = {}
        for i in glyph_order.getElementsByTagName("GlyphID"):
            self.glyphs[i.getAttribute("name")] = None
            pass
        # cmap is the actual character map?
        hmtx = ttx.getElementsByTagName("hmtx").item(0)
        glyf = ttx.getElementsByTagName("glyf").item(0)

        for gn in self.glyphs.keys():
            self.glyphs[gn] = c_glyph(gn)
            self.glyphs[gn].ttx_get_metrics(hmtx)
            self.glyphs[gn].ttx_get_glyph(glyf)
        return self
    #f get_glyph_names
    def get_glyph_names(self):
        return self.glyphs.keys()
    #f get_bbox
    def get_bbox( self, glyph_name=None, glyph_name_list=None ):
        if glyph_name_list is not None:
            glyph_names = self.get_glyph_names()
            bbox = [0,0,0,0]
            for g in glyph_name_list:
                if g in glyph_names:
                    b = self.glyphs[g].get_bbox()
                    if (b[0]<bbox[0]): bbox[0]=b[0]
                    if (b[1]<bbox[1]): bbox[1]=b[1]
                    if (b[2]>bbox[2]): bbox[2]=b[2]
                    if (b[3]>bbox[3]): bbox[3]=b[3]
                    pass
                pass
            return bbox
        glyph = self.glyphs[glyph_name]
        return glyph.get_bbox()
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

#a Toplevel
if __name__=="__main__":
    f = c_font("fred")
    if False:
        c_font.convert_ttf_to_ttx(ttf_filename="../../fonts/cabin/Cabin-Bold-TTF.ttf",
                                  ttx_filename="../../fonts/cabin-bold.ttx")
    #f.load_from_ttx("../../fonts/cabin-bold.ttx")
    f.load_from_ttx("../../fonts/a.ttx")
    if False:
        for gn in f.get_glyph_names():
            print gn, f.get_bbox(glyph_name=gn)
            pass
        pass
    gn =u'D'
    if False:
        print
        print "Beziers",f.create_bezier_lists(gn)
        lines = f.create_straight_lines(gn,straightness=100)
        print
        print "Straightness 100", lines
        lines = f.create_straight_lines(gn,straightness=1)
        print
        print "Straightness 1", lines
        pass
    if False:
        import draw
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
    if True:
        names = (u'A', u'B', u'C', u'D', u'E', u'F', u'Q', u'M')
        bbox = f.get_bbox(glyph_name_list=names)
        for gn in names:
            d = f.glyphs[gn].draw(size=(120,120),bbox=bbox)
            print d.string_scale(2)
            pass
        
