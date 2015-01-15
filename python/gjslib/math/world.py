#!/usr/bin/env python
#a Documentation
"""
"""

#a Imports
import math
from structure  import c_structure, c_structure_element
import collision

#a Game classes
#c c_world_object
class c_world_object( object ):
    fixed = True
    cor = 0.9
    mass = 10
    velocity = (0,0)
    present = True
    callbacks = {}
    def __init__( self, id=None, id_type=None, world=None, **kwargs ):
        self.id = id
        self.id_type = id_type
        self.state_id = (id,id_type)
        self.world = world
        self.world.add_object( self )
        self.set_collision( circle=(8,) )
        pass
    def set_collision( self, circle=None ):
        self.collision = circle
        pass
    def tick_start( self ):
        self.modification = None
        pass
    def get_state( self ):
        pass
    def get_state_change( self ):
        if self.modification is None: return None
        if self.modification is True: return self.get_state()
        return (self.id,self.modification)
    def find_collision_time( self, velocity, other, min_time ):
        if not other.present: return None
        t = collision.find_collision_time_circle_circle( self.position, velocity, self.collision[0], other.position, (0,0), other.collision[0] )
        if t is None: return None
        if t<min_time: return t
        return None

#c c_obstacle
class c_obstacle( c_world_object ):
    cor = 0.9
    mass = 1000.0
    fixed = True
    def __init__( self, position, **kwargs ):
        self.position = position
        self.callbacks = {"get_state":self.get_state,
                          }
        c_world_object.__init__( self, id_type="obstacle", **kwargs )
        pass
    def get_state( self ):
        return (self.state_id,self.position)
    def tick( self ):
        pass

#c c_monster
class c_monster( c_world_object ):
    cor = 0.9
    mass = 100.0
    fixed = False
    def __init__( self, position, motion, **kwargs ):
        self.position = position
        self.motion = motion
        self.callbacks = {"tick_start":self.tick_start,
                          "tick":self.tick,
                          "get_state":self.get_state,
                          "get_state_change":self.get_state_change,
                          }
        c_world_object.__init__( self, id_type="monster", **kwargs )
        pass
    def get_state( self ):
        return (self.state_id,self.position)
    def tick( self ):
        self.position = self.world.bound_position( self.position[0]+self.motion[0],
                                                   self.position[1]+self.motion[1] )
        self.modification = True
        pass

#c c_player_bullet
class c_player_bullet( c_world_object ):
    max_range = 40
    def __init__( self, player, bullet_number, **kwargs ):
        self.player = player
        self.bullet_number = bullet_number
        self.position=(0,0)
        self.present = False
        self.range_countdown = 0
        self.callbacks = {"tick_start":self.tick_start,
                          "tick":self.tick,
                          "get_state":self.get_state,
                          "get_state_change":self.get_state_change,
                          }
        c_world_object.__init__( self, id_type="bullet", id="%s.b%d"%(player.id,bullet_number), **kwargs )
        pass
    def launch( self, position, velocity, angle, bullet_speed ):
        self.position = position
        r = math.radians(angle)
        c = math.cos(r)
        s = math.sin(r)
        self.velocity = ( velocity[0]+bullet_speed*c,  velocity[1]+bullet_speed*s )
        self.present = True
        self.range_countdown = self.max_range
        pass
    def get_state( self ):
        return (self.state_id,{"pos":self.position,"present":self.present})
    def tick( self ):
        if self.present:
            self.position = self.world.bound_position( self.position[0]+self.velocity[0],
                                                       self.position[1]+self.velocity[1] )
            self.modification = True
            if self.range_countdown>0:
                self.range_countdown -= 1
                pass
            else:
                self.present = False
                self.player.bullet_finished( self, self.bullet_number, 0 )
                pass
            pass
        pass

#c c_player
class c_player( c_world_object ):
    cor = 0.95
    mass = 10.0
    fixed = False

    max_speed = 8
    max_angular_speed = 15
    angular_drag = 15
    angular_jet_power = 15
    drag = 3
    jet_power = 3

    max_bullets = 10
    reload_delay = 3
    bullet_speed = 5

    def __init__( self, position, id=None, **kwargs ):
        self.position = position
        self.angle = 0
        self.velocity = (0,0)
        self.angular_speed = 0
        self.present = False
        self.motion = {}
        self.callbacks = {"tick_start":self.tick_start,
                          "tick":self.tick,
                          "get_state":self.get_state,
                          "get_state_change":self.get_state_change,
                          }
        c_world_object.__init__( self, id_type="player", id=id, **kwargs )
        self.bullets = []
        self.bullets_ready = []
        self.bullets_in_action = []
        self.reloading_countdown = 0
        for i in xrange(self.max_bullets):
            b = b=c_player_bullet( self, i, **kwargs )
            self.world.add_object( b )
            self.bullets.append(b)
            self.bullets_ready.append(b)
            pass
        pass
    def enable( self, enabled ):
        self.present = enabled
        print "Enabling player %s"%(str(self.id))
        pass
    def input( self, player_input ):
        self.motion={}
        for k in ['forward', 'fire', 'right', 'left']:
            if (k in player_input) and player_input[k]: self.motion[k]=True
            pass
        if ("left" in self.motion) and ("right" in self.motion):
            del self.motion["left"], self.motion["right"]
            pass
        pass
    def get_state( self ):
        return (self.state_id, {"pos":self.position,
                "angle":self.angle,
                "present":self.present})
    def change_velocity( self ):
        """
        """
        if not self.present: return
        if (self.angular_speed<0):
            self.angular_speed += self.angular_drag
            if self.angular_speed>0: self.angular_speed=0
            pass
        elif (self.angular_speed>0):
            self.angular_speed -= self.angular_drag
            if self.angular_speed<0: self.angular_speed=0
            pass
        if "left" in self.motion:
            self.angular_speed += self.angular_jet_power
            pass
        if "right" in self.motion:
            self.angular_speed -= self.angular_jet_power
            pass
        if self.angular_speed<-self.max_angular_speed: self.angular_speed=-self.max_angular_speed
        if self.angular_speed>+self.max_angular_speed: self.angular_speed=+self.max_angular_speed

        self.angle = self.angle + self.angular_speed

        speed_squared = self.velocity[0]*self.velocity[0] + self.velocity[1]*self.velocity[1]
        if speed_squared>0:
            slowdown = (speed_squared - self.drag) / speed_squared
            if slowdown<0: slowdown=0
            self.velocity = (self.velocity[0]*slowdown, self.velocity[1]*slowdown)
            pass
            
        if ("forward" in self.motion):
            r = math.radians(self.angle)
            c = math.cos(r)
            s = math.sin(r)
            self.velocity = ( self.velocity[0]+self.jet_power*c,  self.velocity[1]+self.jet_power*s )
            speed_squared = self.velocity[0]*self.velocity[0] + self.velocity[1]*self.velocity[1]
            if speed_squared>self.max_speed*self.max_speed:
                slowdown = self.max_speed / math.sqrt(speed_squared)
                self.velocity = (self.velocity[0]*slowdown, self.velocity[1]*slowdown)
                pass
            pass

        self.modification = True
        pass
    def move( self ):
        """
        """
        if not self.present: return
        smallest_time = 0.00009
        self.change_velocity()
        time_left = 1.0
        max_collisions = 2
        while (time_left>smallest_time) and (max_collisions>0):
            (t, obj) = self.world.find_first_collision( self, self.velocity, time_left )
            if (t is None) or (obj is None) or (t>time_left):
                self.position = self.world.bound_position( self.position[0]+time_left*self.velocity[0], self.position[1]+time_left*self.velocity[1] )
                break
            if (t>smallest_time):
                self.position = self.world.bound_position( self.position[0]+0.9*t*self.velocity[0], self.position[1]+0.9*t*self.velocity[1] )
                pass
            else:
                t = smallest_time
                pass
            (dv0, dv1) = collision.find_velocities_after_bounce( obj.cor, self.position, self.velocity, self.mass, obj.position, obj.velocity, obj.mass )
            if not obj.fixed: obj.velocity = (obj.velocity[0]+dv1[0], obj.velocity[1]+dv1[1] )
            self.velocity = ( self.velocity[0]+dv0[0], self.velocity[1]+dv0[1] )
            # do bounce
            print "BOING",t, self,obj, self.present, obj.present #obj.position, self.position, self.velocity, obj.velocity, dv0#, dv1
            #self.velocity = (-self.velocity[0]*0.9, -self.velocity[1]*0.9)
            time_left = time_left-t
            max_collisions -= 1
            pass
        pass

    def fire( self ):
        if self.reloading_countdown>0: self.reloading_countdown-=1
        if "fire" in self.motion:
            if self.reloading_countdown==0:
                if len(self.bullets_ready)>0:
                    self.reloading_countdown = self.reload_delay
                    b = self.bullets_ready.pop()
                    self.bullets_in_action.append( b )
                    b.launch( self.position, self.velocity, self.angle, self.bullet_speed )
                    pass
                pass
            pass
        pass
    def bullet_finished( self, bullet, bullet_number, reason ):
        for i in xrange(len(self.bullets_in_action)):
            if self.bullets_in_action[i] == bullet:
                self.bullets_in_action.pop(i)
                break
            pass
        self.bullets_ready.append(bullet)
        pass
    def tick(self):
        self.move()
        self.fire()
        pass
    pass

#c c_world
class c_world( object ):
    #f __init__
    def __init__( self ):
        self.size_of_space = (500,500)
        self.objects = []

        self.callbacks = {"tick_start":[],
                          "tick":[],
                          "get_state":[],
                          "get_state_change":[],
                          }
        self.players = {}
        self.bullets = {}
        self.obstacles = {}
        for i in xrange(3):
            for j in xrange(3):
                self.obstacles["obst_%d_%d"%(i,j)] = c_obstacle( id="obst_%d_%d"%(i,j), world=self, position=(32+i*128,32+j*128) )
                pass
            pass
        self.monsters = { "a":c_monster( id="a", world=self, position=(20,20), motion=(5,3) )
                          }
        for i in xrange(1):
            self.players[i] = c_player( id="p%d"%i, world=self, position=(100+i*100,200) )
            pass

        pass
    #f add_object
    def add_object( self, obj ):
        self.objects.append(obj)
        for t in self.callbacks.keys():
            if t in obj.callbacks:
                self.callbacks[t].append( obj.callbacks[t] )
                pass
            pass
        pass
    #f find_first_collision
    def find_first_collision( self, obj, velocity, max_time ):
        t = max_time
        collision_obj = None
        for o in self.objects:
            if o is not obj:
                obj_t = obj.find_collision_time( velocity, o, t )
                if obj_t is not None:
                    t = obj_t
                    collision_obj = o
                    pass
                pass
            pass
        return (t, collision_obj)
    #f bound_position
    def bound_position( self, x, y ):
        while (x<0): x+=self.size_of_space[0]
        while (x>self.size_of_space[0]): x-=self.size_of_space[0]
        while (y<0): y+=self.size_of_space[1]
        while (y>self.size_of_space[1]): y-=self.size_of_space[1]
        return (x,y)
    #f enable_player
    def enable_player( self, player_number, enabled ):
        """
        Invoked from the world thread when a player joins or leaves
        """
        if player_number in self.players: self.players[player_number].enable( enabled )
        pass
    #f player_input
    def player_input( self, player_number, player_input ):
        """
        Invoked from the world thread when a player's input arrives
        """
        if player_number in self.players: self.players[player_number].input( player_input )
        pass
    #f invoke_callbacks
    def invoke_callbacks( self, callback ):
        for c in self.callbacks[callback]: c()
        pass
    #f tick_start
    def tick_start( self ):
        """
        Called by world thread to start a clock tick
        """
        self.invoke_callbacks("tick_start")
        pass
    #f tick
    def tick( self ):
        """
        Called by world thread to indicate a clock tick event - the world state should change
        """
        self.invoke_callbacks("tick")
        pass
    #f get_state
    def get_state( self ):
        """
        Return the complete state of the game, e.g. for a new client
        """
        state = [ (("space","background"),self.size_of_space) ]
        for c in self.callbacks["get_state"]: state.append( c() )
        return state
    #f get_state_change
    def get_state_change( self ):
        """
        Return the change in state of the game since the last tick_start
        """
        state_change = []
        for c in self.callbacks["get_state_change"]:
            delta = c()
            if delta is not None: state_change.append(delta)
            pass
        return state_change
    pass

