#!/usr/bin/env python
#a Documentation
"""
Run with the following threads:
1. Main game thread
2. Socket accepting thread
3. One thread per client

This is not designed for more than about 4 clients on a LAN.

The main game thread is the coordination point. It ticks at (say) 30 ticks per second (every 30ms).
At the start of the tick it collates all inputs from all the client threads
It then operates its cycle
It provides a change set to all the client threads
Then it skips until the end of the 30ms.

A connected client thread accepts key state from a client, and it watches for change set indications from the main thread
On a change set indication from the main thread it sends the delta state to the client
It then collates all key press messages and updates the (shared) state with the server

An unconnected client thread is on the thread queue to the socket accepting thread.
It waits for its 'new_client' method to be invoked


The socket accepting thread has a queue of client threads.
If the queue of client threads is not empty, then it accepts a client (with a timeout)
If a client is accepted then the thread's new_client method is invoked


"""

#a Imports
import sys
import random
import threading
import Queue as queue
import time
import socket
import errno
import math
from transaction_socket import c_transaction_socket

from structure  import c_structure, c_structure_element

#a Server thread
#a Base thread
#c c_base_thread
class c_base_thread( threading.Thread ):
    def __init__( self, name ):
        self.stopping = False
        threading.Thread.__init__( self, name=name )
        pass
    def request_stop( self ):
        self.stopping = True
        pass
    def run_init( self ):
        pass
    def exit( self ):
        pass
    def run( self ):
        self.run_init()
        while not self.stopping:
            self.run_iteration()
            pass
        self.exit()
        pass

#c c_server_thread
class c_server_thread( c_base_thread ):
    client_poll_delay = 0.1
    accept_poll_delay = 0.1
    def __init__( self, world_thread ):
        self.server_socket = socket.socket( socket.AF_INET, socket.SOCK_STREAM )
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind( ("",12345) )
        self.server_socket.listen(0)
        self.server_socket.settimeout( self.accept_poll_delay )
        self.client_thread_queue = queue.Queue()
        self.world_thread = world_thread
        c_base_thread.__init__( self, name="Server" )
        pass
    def exit( self ):
        self.server_socket.close()
        self.server_socket = None
        pass
    def run_iteration( self ):
        if (self.server_socket is None):
            self.request_stop()
        elif self.client_thread_queue.empty():
            time.sleep(self.client_poll_delay)
            pass
        else:
            skt = None
            try:
                (skt,skt_address) = self.server_socket.accept()
            except:
                pass
            if skt is not None:
                client_thread = self.client_thread_queue.get_nowait()
                client_thread.new_client( skt, skt_address )
                pass
            pass
        pass
    def add_client( self, client ):
        self.client_thread_queue.put( client )
        if self.stopping:
            client.request_stop()
            pass
        pass
    def world_create_client_queues( self, client_number ):
        return self.world_thread.create_client_queues( client_number )
    def world_lost_client( self, client_number ):
        return self.world_thread.lost_client( client_number )

#c c_client_thread
class c_client_thread( c_base_thread ):
    client_poll_delay = 0.1
    world_thread_timeout = 0.1 # In case of startup, we cannot guarantee data after a single tick - so this should be about 3 ticks or 0.1s max
    def __init__( self, server_thread, client_number ):
        self.server_thread = server_thread
        self.client_skt = None
        self.client_number = client_number
        self.from_world_queue = None
        self.to_world_queue = None
        c_base_thread.__init__( self, name="Client %d"%client_number )
        pass
    def new_client( self, skt, skt_address ):
        print "Client %d accepting new client %s"%(self.client_number,str(skt_address))
        self.client_skt = c_transaction_socket( skt )
        (self.from_world_queue, self.to_world_queue) = self.server_thread.world_create_client_queues( self.client_number )
        print "Client %d has socket %s"%(self.client_number,str(self.client_skt))
        pass
    def run_init( self ):
        self.server_thread.add_client( self )
        pass
    def run_iteration( self ):
        if self.client_skt is not None:
            self.poll_client()
            pass
        else:
            time.sleep(self.client_poll_delay)
            pass
        pass
    def lost_client( self ):
        print "Client %d closed"%self.client_number
        if self.from_world_queue is not None:
            self.server_thread.world_lost_client( self.client_number )
            pass
        if self.client_skt is not None:
            self.client_skt.close()
            pass
        self.from_world_queue = None
        self.to_world_queue = None
        self.client_skt = None
        self.server_thread.add_client( self )
        pass
    def poll_client( self ):
        if not self.client_skt.is_alive():
            self.lost_client()
            return
        try:
            world_data = self.from_world_queue.get( True, timeout=self.world_thread_timeout )
            pass
        except queue.Empty:
            world_data = None
            pass
        client_data = None
        while True:
            new_client_data = self.client_skt.poll_data()
            if new_client_data is None:
                if client_data is not None:
                    self.to_world_queue.put( client_data )
                    pass
                break
            client_data = new_client_data
            pass
        if world_data is not None:
            #print "Would send 'world_data' of %s to client %d"%(str(world_data), self.client_number)
            self.client_skt.send_data(world_data)
            pass
        pass

#c c_world_thread
class c_world_thread( c_base_thread ):
    tick_time = 0.05
    min_sleep_time = 0.02
    def __init__( self, world ):
        self.world = world
        self.new_client_queues = {}
        self.active_client_queues = {}
        self.state_lock = threading.Lock()
        c_base_thread.__init__( self, name="World" )
        pass
    def run_init( self ):
        self.last_tick_time = time.time()
        self.iter = 0
        pass
    def run_iteration( self ):
        #b Get player key presses
        for (client_number,client_queues) in self.active_client_queues.iteritems():
            while not client_queues[1].empty():
                self.world.player_input( client_number, client_queues[1].get() )
                pass
            pass

        #b Tick the world
        self.world.tick_start()
        self.world.tick()

        #b For all new clients, send get_state
        clients_handled = []
        if len(self.new_client_queues)!=0:
            self.state_lock.acquire()
            state = self.world.get_state()
            for (client_number,client_queues) in self.new_client_queues.iteritems():
                client_queues[0].put(state)
                clients_handled.append(client_number)
                self.active_client_queues[ client_number ] = client_queues
                pass
            self.new_client_queues = {}
            self.state_lock.release()
            pass

        #b For all non-new clients, send state_change
        if len(clients_handled)<len(self.active_client_queues):
            state_change = self.world.get_state_change()
            self.state_lock.acquire()
            for (client_number,client_queues) in self.active_client_queues.iteritems():
                if client_number not in clients_handled:
                    client_queues[0].put(state_change)
                    pass
                pass
            self.state_lock.release()
            pass
            
        #print "Sleep iter %d %s"%(self.iter,str(self.active_client_queues))
        #print self.world.get_state_change()
        self.iter += 1

        #b Sleep
        next_tick_time = self.last_tick_time+self.tick_time
        current_time = time.time()
        sleep_time = next_tick_time-current_time
        if (sleep_time<self.min_sleep_time): sleep_time=self.min_sleep_time
        time.sleep(sleep_time)
        self.last_tick_time = current_time+sleep_time
        pass

    def create_client_queues( self, client_number ):
        self.state_lock.acquire()
        if (client_number in self.active_client_queues) or (client_number in self.new_client_queues):
            self.state_lock.release()
            raise Exception("Client %d already active"%client_number)
        qs = (queue.Queue(),queue.Queue())
        self.new_client_queues[client_number] = qs
        self.state_lock.release()
        self.world.enable_player(client_number,True)
        return qs

    def lost_client( self, client_number ):
        self.world.enable_player(client_number,False)
        self.state_lock.acquire()
        if client_number in self.active_client_queues: del self.active_client_queues[client_number]
        if client_number in self.new_client_queues:    del self.new_client_queues[client_number]
        self.state_lock.release()

#a Thread set classes
class c_server_client_thread_set( object ):
    def __init__( self ):
        self.stop_all_threads = False
        pass
    def add_signal_handler( self ):
        import signal 
        def signal_handler(signal, frame, self=self):
            self.stop_all_threads = True
            pass
        signal.signal(signal.SIGINT, signal_handler)
        pass
    def create_threads( self, world , num_clients=4):
        self.world_thread = c_world_thread( world )
        self.server_thread = c_server_thread( self.world_thread )
        self.client_threads = []
        for i in xrange(num_clients):
            self.client_threads.append( c_client_thread( self.server_thread, i ) )
            pass
        pass
    def start_threads( self ):
        self.server_thread.start()
        for c in self.client_threads: c.start()
        self.world_thread.start()
        pass
    def is_alive( self ):
        return not self.stop_all_threads
    def stop_threads( self ):
        self.server_thread.request_stop()
        for c in self.client_threads: c.request_stop()
        self.world_thread.request_stop()
        pass
    def join_threads( self ):
        self.server_thread.join()
        for c in self.client_threads: c.join()
        self.world_thread.join()
        pass
