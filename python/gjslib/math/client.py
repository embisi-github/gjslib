#!/usr/bin/env python
import pygame
import sys
import socket
from transaction_socket import c_transaction_socket

file_root='./'

from background import c_background
from sprite import c_sprite
from image import c_image
#from game.structure import c_structure, c_structure_element

class c_monster( c_sprite ):
    def __init__( self, world, data ):
        c_sprite.__init__( self, position=data, image=world.images["monster"] )
        self.position = data
        pass
    def state_change( self, delta ):
        pass

class c_obstacle( c_sprite ):
    def __init__( self, world, data ):
        c_sprite.__init__( self, position=data, image=world.images["obstacle"] )
        self.position = data
        pass
    def state_change( self, delta ):
        self.position = delta
        pass

class c_player( c_sprite ):
    def __init__( self, world, data ):
        c_sprite.__init__( self, position=data["pos"], image=world.images["player"] )
        self.angle = data["angle"]
        self.position = data["pos"]
        pass
    def state_change( self, delta ):
        self.position = delta["pos"]
        self.angle = delta["angle"]
        pass
    def blit( self, surface ):
        self.image.rotated_blit( surface, self.position, angle=self.angle )
        pass

class c_bullet( c_sprite ):
    def __init__( self, world, data ):
        c_sprite.__init__( self, position=data["pos"], image=world.images["bullet"] )
        self.position = data["pos"]
        self.present = data["present"]
        pass
    def state_change( self, delta ):
        self.position = delta["pos"]
        self.present = delta["present"]
        pass
    def blit( self, surface ):
        if self.present:
            c_sprite.blit( self, surface )
            pass
        pass

class c_world( object ):
    image_file_map = { "monster":'rocks.png',
                       "obstacle":'boinger.png',
                       "player":'rocket.png',
                       "bullet":'bullet.png',
                       "background":'background.png',
               }
    server_timeout = 5.0
    def __init__( self, image_file_root, scale=1 ):
        self.images = {}
        self.server_skt = None
        self.server_transaction_skt = None
        self.scale = scale
        for it in self.image_file_map:
            self.images[it] = c_image().load(image_file_root+self.image_file_map[it]).scale(by=scale)
            pass
        self.background = None
        self.sprites = []
        pass
    def connect( self, server ):
        self.server_skt = socket.socket( socket.AF_INET, socket.SOCK_STREAM )
        self.server_skt.settimeout( self.server_timeout )
        try:
            self.server_skt.connect( server )
            pass
        except:
            raise Exception( "Failed to connect to server %s"%str(server) )
        self.server_transaction_skt = c_transaction_socket( self.server_skt )
        self.game_state = None
        pass
    def tick_start( self, keys ):
        # could send player keys
        self.server_transaction_skt.send_data(keys.data())
        #self.structure.tick_start()
        pass
    def tick( self ):
        if not self.server_transaction_skt.is_alive():
            return False
        i = 0
        while (i<5):
            data = self.server_transaction_skt.poll_data()
            if data is None:
                break
            self.handle_server_data( data )
            i += 1
            pass
        #self.structure.tick()
        return True
    def handle_server_data( self, data ):
        if (self.game_state is None):
            self.background = None
            self.sprites = {}
            self.game_state = {}
            print data
            for (ids,id_data) in data:
                if ids[1]=="background":
                    self.background = c_background(self.images["background"],width=id_data[0],height=id_data[1], scale=self.scale)
                    pass
                elif ids[1]=="monster":
                    monster = c_monster(world=self,data=id_data)
                    self.game_state[ids[0]] = monster
                    self.sprites[ids[0]] = monster
                elif ids[1]=="obstacle":
                    print ids, id_data
                    obstacle = c_obstacle(world=self,data=id_data)
                    self.game_state[ids[0]] = obstacle
                    self.sprites[ids[0]] = obstacle
                elif ids[1]=="player":
                    print ids, id_data
                    player = c_player(world=self,data=id_data)
                    self.game_state[ids[0]] = player
                    self.sprites[ids[0]] = player
                elif ids[1]=="bullet":
                    print ids, id_data
                    bullet = c_bullet(world=self,data=id_data)
                    self.game_state[ids[0]] = bullet
                    self.sprites[ids[0]] = bullet
                pass
            pass
        else:
            for (ids, id_delta) in data:
                id = ids[0]
                if id in self.game_state:
                    self.game_state[id].state_change(id_delta)
                    pass
                pass
            pass
        pass
    def blit( self, surface ):
        if self.background is not None:
            self.background.blit( surface )
        for s in self.sprites:
            self.sprites[s].blit( surface )
            pass
        pass
    pass

class c_keys( object ):
    keys = { pygame.K_a:"left",
             pygame.K_d:"right",
             pygame.K_SPACE:"forward",
             pygame.K_RETURN:"fire",
             }
    def __init__( self ):
        self.keys_down = {}
        for k in self.keys:
            self.keys_down[self.keys[k]] = False
            pass
        pass
    def event( self, event ):
        for (k,t) in self.keys.iteritems():
            if event.key == k: self.keys_down[t] = (event.type == pygame.KEYDOWN)
            pass
        pass
    def data( self ):
        return self.keys_down

class c_scaled_surface( object ):
    def __init__( self, surface, scale=1.0 ):
        self.surface = surface
        self.scale = scale
        self.size = self.surface.get_rect().size
        self.set_scale(scale)
        pass
    def set_scale( self, scale ):
        self.scale = scale
        self.size = (self.size[0]/scale, self.size[1]/scale)
        pass
    def screen_from_world( self, position, dx=0, dy=0 ):
        return (position[0]*self.scale+dx,
                (self.size[1]-position[1])*self.scale-1+dy )
    def rect( self, bbox ):
        (left,bottom) = self.screen_from_world( (bbox[0], bbox[1] )  ) # inclusive
        (right,top)   = self.screen_from_world( (bbox[2], bbox[3] ), dx=-1, dy=1  ) # make inclusive from exclusive
        pygame.draw.rect( self.surface, (255,0,0), (left,top,right-left+1,bottom-top+1), 1 )
        pass
    def blit( self, image, position ):
        """
        Put image top left at world position - image itself should be prescaled
        """
        position = self.screen_from_world( position, dy=1 ) # Move down by 1 on the Y as it is inclusive
        self.surface.blit( image, position )
        pass
    pass

scale=2
#screen = pygame.display.set_mode(resolution=(500*scale,500*scale),flags=pygame.DOUBLEBUF|pygame.HWSURFACE)
screen = pygame.display.set_mode((500*scale,500*scale),pygame.DOUBLEBUF|pygame.HWSURFACE)
print pygame.version.vernum
print pygame.display.Info()
scaled_screen = c_scaled_surface( screen, scale )
world = c_world( file_root+'images/', scale=scale )
keys = c_keys()

import time
world.connect( ("",12345) )
def loop(keys):
    alive = True
    while alive:
        times = [ time.time() ]
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit();
            if (event.type == pygame.KEYDOWN) or (event.type == pygame.KEYUP):
                keys.event(event)
                pass
        times.append( time.time() )
        world.tick_start( keys )
        times.append( time.time() )
        if not world.tick(): alive=False
        times.append( time.time() )
        world.blit( scaled_screen )
        times.append( time.time() )

        pygame.display.flip()

        times.append( time.time() )

        for i in xrange(len(times)-1): times[i+1] = times[i+1] - times[0]
        print times

        msElapsed = clock.tick(15)
        pass
    pass

clock = pygame.time.Clock()
loop(keys)

