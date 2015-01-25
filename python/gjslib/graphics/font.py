#!/usr/bin/env python

class c_glyph( object ):
    def __init__( self, name ):
        self.name = name
        self.metrics = {}
        self.glyph = {}
        pass
    def ttx_get_element_by_name( self, node, tag_name, name ):
        for m in node.getElementsByTagName(tag_name):
            if m.getAttribute("name")==name:
                return m
            pass
        return None
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
    def ttx_get_metrics( self, hmtx ):
        glyph = self.ttx_get_element_by_name(hmtx,"mtx",self.name)
        if glyph is None:
            return
        self.metrics = self.ttx_get_int_attributes(glyph, ("width", "lsb"))
        return
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
    def __repr__( self ):
        result = "glyph '%s' : %s : %s"%(self.name,str(self.metrics),str(self.glyph))
        return result

class c_font( object ):
    """
    A simple font class to permit font handling particularly for OpenGL

    It uses a fairly simple internal data structure, which can be loaded from a pickled structure of from a TTX fonts

    TTX Fonts can be created from TTF fonts (TrueType) using a static method

    Many TTF fonts are available, and OSX and Windows use TTF.
    No hinting support is provided in this class, as the rendering is expected to be used in OpenGL (for which hints are pointless)
    """
    @staticmethod
    def convert_ttf_to_ttx( ttf_filename, ttx_filename ):
        import fontTools.ttLib
        tt = fontTools.ttLib.TTFont(ttf_filename)
        tt.saveXML(ttx_filename)
        pass
    def __init__( self, font_name ):
        self.font_name = font_name
        self.glyphs = {}
        self.map = {}
        pass
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
    pass
    def get_bbox( self, glyph_name ):
        glyph = self.glyphs[glyph_name]
        lx = glyph.glyph["xMin"]
        w = glyph.glyph["xMax"] - glyph.glyph["xMin"]
        if w<0:
            w=-w
            lx = glyph.glyph["xMax"]
            pass
        by = glyph.glyph["yMin"]
        h = glyph.glyph["yMax"] - glyph.glyph["yMin"]
        if h<0:
            h=-h
            by = glyph.glyph["xMin"]
            pass
        return (lx,by,w,h)
    def create_bezier_lists( self, glyph_name ):
        import gjslib.math.bezier as bezier
        glyph = self.glyphs[glyph_name]
        bezier_lists = []
        for c in glyph.glyph["contours"]:
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
