#a Imports
import image

#a Simple background - just an image to start with
#c c_background
class c_background( object ):
    def __init__( self, image, width, height, scale ):
        self.image = image.scale( width=width*scale, height=height*scale )
        self.position = (0,height)
        pass
    def blit( self, surface ):
        surface.blit( image=self.image.scaled_image, position=self.position )
        pass
    pass
