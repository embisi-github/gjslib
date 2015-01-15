#a Imports
import image

#a Base sprite class - a placed image
#c c_sprite
class c_sprite( object ):
    def __init__( self, image, **kwargs ):
        self.position = (0,0)
        self.image = image
        pass
    def move( self, position, relative=False ):
        if relative:
            self.position = (position[0]+self.position[0], position[1]+self.position[1])
            return
        self.position = (position[0], position[1])
        pass
    def blit( self, surface ):
        self.image.blit( surface, self.position )
        pass
    pass
