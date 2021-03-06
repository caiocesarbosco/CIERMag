import threading
#import sys

#sys.path.append("/home/pi/front-end/server")

from perifericos.generico import ciermagthread
from perifericos.generico import ciermagtransducer
from perifericos.generico import parameterlib as pl
import serverconfig as sc
from perifericos.generico import serverfunctions as sf

exit_var = True

class TransducerManager(threading.Thread):
    """Perform transducer creation and operations"""
    def __init__(self):
        threading.Thread.__init__(self)

    def run(self):
        

        import time #test only
        chengedtedslist = ciermagthread.changed_teds
        
        system_transducers = {}
        time1 = 0
        maxlen = 30 * 60 * 8

        global looptime

        while exit_var:
                
            for modteds in list(chengedtedslist):
                
                with ciermagthread.changed_teds_lock:
                    tedsdict = pl.load_teds(sc.MAIN_PATH + pl.TEDS_FOLDER + '/' + modteds)
                    system_transducers[tedsdict['ID']] = ciermagtransducer.Transducer(tedsdict)
                    chengedtedslist.remove(modteds)
                    print(modteds, ' created')

                with ciermagthread.actuator_data_lock:
                    actuatordata = ciermagtransducer.create_actuator_data(system_transducers)
                    sf.save_data(actuatordata, sc.MAIN_PATH + pl.FILE_FOLDER + '/' + pl.CONTROLLERDATAFILE)
                    
            if ciermagthread.actuator_update:
                
                with ciermagthread.actuator_data_lock:
                    actuatordata = sf.load_controllers_data(sc.MAIN_PATH + pl.FILE_FOLDER + '/' + pl.CONTROLLERDATAFILE)
                    ciermagtransducer.process_actuator_data(actuatordata, system_transducers)
                    ciermagthread.actuator_update = False
                    actuatordata = ciermagtransducer.create_actuator_data(system_transducers)
                    sf.save_data(actuatordata,sc.MAIN_PATH + pl.FILE_FOLDER + '/' + pl.CONTROLLERDATAFILE)

            if time.time() > time1 + 5:
                
                with ciermagthread.sensor_data_lock:
                    sensordata = sf.load_sensor_data(sc.MAIN_PATH + pl.FILE_FOLDER + '/' + pl.SENSORDATAFILE)
                    ciermagtransducer.update_sensor_data(sensordata,system_transducers,maxlen)
                    sf.save_data(sensordata, sc.MAIN_PATH + pl.FILE_FOLDER + '/' + pl.SENSORDATAFILE)
                time1 = time.time()


            time.sleep(0.05)
