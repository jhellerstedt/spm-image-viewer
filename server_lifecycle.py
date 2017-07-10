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

def on_server_loaded(server_context):
    pass
    
def on_server_unloaded(server_context):
    pass

def on_session_created(session_context):
    pass

def on_session_destroyed(session_context):
    try:
        open_ports = pickle.load(open_ports.p)
        port = bokeh.Server.port
        open_ports.remote(port)
        pickle.dump(open_ports, open_ports.p)
    except:
        print("port not excised from open_ports")
    pid = os.getpid()
    os.kill(pid, signal.SIGTERM)
    return