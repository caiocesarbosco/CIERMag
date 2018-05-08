import sys
import os
import threading

global RemoteDebug

def RemoteDebug():
    try:
        sys.path.append("/home/pi/eclipse-PyDev/pysrc/")
        import pydevd
        global pydevd
        pydevd.settrace('192.168.0.36', port=5678, suspend=True,trace_only_current_thread=False)
        threading.settrace(pydevd.GetGlobalDebugger().trace_dispatch)
        os.environ['TERM']='xterm'
        print ("Remote Debug works")
    except ImportError:
        sys.stderr.write("Error: " + "Add pysrc to sys.path.append statement or PYTHONPATH.\n")
        sys.exit(1)

