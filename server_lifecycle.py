#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Dec 19 17:29:28 2016

@author: jack
"""

import core_functions as cf

import os
import signal
import pickle
import psutil

def on_server_loaded(server_context):
    pass
    
def on_server_unloaded(server_context):
    pass

def on_session_created(session_context):
    pass

def on_session_destroyed(session_context):
    pid = os.getpid()
    try:
        port_filename = os.getcwd() + "/spm-image-viewer/open_ports.p"
        with open(port_filename, 'rb') as pickle_file:
            open_ports = pickle.load(pickle_file)
            pickle_file.close()
        port = psutil.Process(pid).connections()[0].laddr[1]
        open_ports.remove(port)
        with open(port_filename, 'wb') as pickle_file:
            pickle.dump(open_ports, pickle_file)
            pickle_file.close()
    except:
        print("port not excised from open_ports")
    
    os.kill(pid, signal.SIGTERM)
    return