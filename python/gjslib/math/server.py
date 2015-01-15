#!/usr/bin/env python
#a Documentation
"""
"""

#a Imports
import time
import server_threads
import world

#a Toplevel
#b Create world
world = world.c_world()

#b Set up world, server and client threads and start them
threads = server_threads.c_server_client_thread_set()
threads.add_signal_handler()
threads.create_threads( world=world, num_clients=1  )
threads.start_threads()

#b Run until kill request (ctrl-C / SIGINT)
while threads.is_alive():
    time.sleep(0.3)

#b Stop all threads and join
threads.stop_threads()
threads.join_threads()
