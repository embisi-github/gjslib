#a Imports
import pygame.image

#a Simple background
#c c_image
class c_image( object ):
    def __init__( self, **kwargs ):
        self.image = None
        self.scaled_image = None
        self.size = (0,0)
        self.scaled_size = (0,0)
        self.last_scale = 1
        pass
    def load( self, image_filename ):
        self.image = pygame.image.load( image_filename )
        self.size = self.image.get_rect().size
        self.scaled_image = self.image
        self.scaled_size = self.size
        return self
    def scale( self, by=None, width=None, height=None ):
        if by is not None:
            width = by * self.size[0]
            height = by * self.size[1]
            pass
        if height is None: height=width
        self.last_scale = width / self.size[0]
        self.scaled_image = pygame.transform.scale( self.image, (width, height) )
        self.scaled_size = (width, height)
        return self
    def blit( self, surface, position=(0,0) ):
        """
        Put centered at world position
        """
        surface.blit( self.scaled_image, (position[0]-self.size[0]/2, position[1]+self.size[1]/2) )
        pass
    def rotated_blit( self, surface, position=(0,0), angle=0 ):
        """
        Put centered at world position rotated by angle 'angle'

        We use the scaled image, as that is required.
        The rotated image will be 'scaled_image' size bigger, plus additional room to account for the 'square' bits that fall outside
        So the rotated image / last scale is the world size of the image, and move it by half of that
        """
        rotated_image = pygame.transform.rotate( self.scaled_image, angle )
        rotated_size = rotated_image.get_rect().size
        surface.blit( rotated_image, (position[0]-rotated_size[0]/2/self.last_scale, position[1]+rotated_size[1]/2/self.last_scale) )
        if False:
            surface.rect( (position[0]-rotated_size[0]/2/self.last_scale,
                           position[1]-rotated_size[1]/2/self.last_scale,
                           position[0]+rotated_size[0]/2/self.last_scale,
                           position[1]+rotated_size[1]/2/self.last_scale,
                           ) )
        pass
