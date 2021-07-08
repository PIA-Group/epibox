# local
from epibox.bitalino import bitalino
from epibox.scientisst import scientisst
from . import close_file 

def disconnect_system(devices, a_file, annot_file, drift_log_file, header): 

    for device in devices:
        try:
            device.stop()
            if header['service'] == 'Bitalino' or header['service'] == 'Mini':
                device.close()
        except:
            continue
    

    close_file.close_file(a_file, annot_file, drift_log_file)