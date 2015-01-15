#a Imports
from overlap import c_overlap_2d

#a Structure element class - a piece of 'background' that has an image and is slightly dynamic
#c c_structure_element
class c_structure_element( object ):
    """
    An element of a structure

    This has a position and a list of images that can be used to represent the element on the screen
    Most structure elements use just one image
    """
    has_tick = False
    debug_bboxes = False
    #f __init__
    def __init__( self, structure, position, images, size, **kwargs ):
        self.structure = structure
        self.position = (position[0], position[1])
        self.images = images
        self.image_number = 0
        self.size = size
        self.bbox = (self.position[0], self.position[1], self.position[0]+size[0], self.position[1]+size[1] )
        pass
    #f set_image
    def set_image( self, image_number ):
        self.image_number = image_number
        if image_number>=len(self.images):
            raise Exception("Attempt to set element image number to be %d which is greater than the image list length %d for the element"%(image_number,len(self.images)))
    #f tick_start
    def tick_start( self, **kwargs ):
        raise Exception("Element needs a tick_start method if has_tick is True")
    #f tick
    def tick( self, **kwargs ):
        raise Exception("Element needs a tick method if has_tick is True")
    #f move
    def move( self, by=None ):
        old_bbox = self.bbox
        if by is not None:
            self.position = (self.position[0]+by[0],
                             self.position[1]+by[1])
            self.bbox = (self.position[0], self.position[1], self.position[0]+self.size[0], self.position[1]+self.size[1] )
            self.structure.move_element( element=self, old_bbox=old_bbox )
            return
        pass
    #f blit
    def blit( self, surface, view=None ):
        self.images[self.image_number].blit( surface, self.position )
        if self.debug_bboxes:
            surface.rect( self.bbox )
        pass
    pass

#c c_structure
class c_structure( object ):
    """
    This class contains the 'structure' of a level of a platform game

    The structure is the set of elements that changes slowly or never; it can include walls, vanishing floors, and moving platforms
    It should not include players and enemies

    The structure is expected to reuse images for its elements; so it maintains a set of images, referred to by name
    """
    #f __init__
    def __init__( self, **kwargs ):
        self.elements = {}
        self.images = {}
        self.overlap = c_overlap_2d( bucket_size=32 )
        self.elements_to_tick = []
        pass
    #f add_image
    def add_image( self, image_name, image ):
        """
        Add an image to the set available to the structure elements
        """
        self.images[ image_name ] = image
        pass
    #f add_element
    def add_element( self, element_tag, image_names=[], element_class=c_structure_element, **kwargs ):
        """
        Add an element to the structure
        """
        images = []
        for i in image_names: images.append(self.images[i])
        element = element_class( structure = self,
                                 images = images,
                                 **kwargs )
        self.elements[ element_tag ] = element
        self.overlap.add_element( element.bbox, element )
        if element.has_tick:
            self.elements_to_tick.append(element)
            pass
        pass
    #f move_element
    def move_element( self, element, old_bbox ):
        self.overlap.remove_element( old_bbox, element )
        self.overlap.add_element( element.bbox, element )
        pass
    #f find_elements_overlapping
    def find_elements_overlapping( self, bbox ):
        return self.overlap.find_overlap( bbox )
    #f tick_start
    def tick_start( self, **kwargs ):
        for e in self.elements_to_tick:
            e.tick_start( **kwargs )
            pass
        pass
    #f tick
    def tick( self, **kwargs ):
        for e in self.elements_to_tick:
            e.tick( **kwargs )
            pass
        pass
            
    #f blit
    def blit( self, surface ):
        for e in self.elements:
            self.elements[e].blit( surface )
            pass
        pass
    pass
