############### Importing Buid-in Modules ####################################

import threading
import sys

############### Importing Periphericals Manager Modules ######################

import serverconfig as sc
import serverfunctions as sf

from perifericos.generico import ciermagtransducer
from perifericos.generico import parameterlib as pl

from threads import HTTPServer_thread as HTTP_t
from threads import Generico_thread as Gen_t

############### Include/Setup Python Features #################################

sys.path.append('../')
from remotedebugfeature import RemoteDebug  
#global remote_debug

def end_threads():

    if server.isAlive:
        server._Thread__stop()
        print("server ended")

    if transducer_manager.isAlive:
        transducer_manager._Thread__stop()
        print("manager ended")

    print("done")


if __name__ == "__main__":
    
    #####################REMOTE DEBUG CALL##########################
    remote_debug = False # Set this flag true for Remote Debug Interface Activate on Eclipse
    if remote_debug == True:
        RemoteDebug()    
    #################################################################
        
    server = HTTP_t.HTTPServer()
    transducer_manager = Gen_t.TransducerManager()    
    server.start()
    transducer_manager.start()
