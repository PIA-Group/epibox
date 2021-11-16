# local
from epibox.common.close_file import close_file 

def disconnect_system(devices, service, a_file=None, annot_file=None, drift_log_file=None, files_open=True): 

    for device in devices:
        try:
            device.stop()
            device.close()
                
        except:
            continue

    if files_open:
        close_file(a_file, annot_file, drift_log_file)


