# built-in
import time
from datetime import datetime

# third-party
import numpy as np

# local
from epibox.common.write_file import write_file
from epibox.common.read_modules import read_modules


def start_system(devices, a_file, drift_log_file, fs, mac_channels, sensors, save_fmt, header):

    dig_Out = 0
    now = datetime.now()
    sync_param = {'flag_sync' : 0 , 'inittime' : time.time(), 'strtime': time.time(), 'sync_time' : now.strftime("%Y-%m-%d %H:%M:%S.%f").rstrip('0'), 'dig_Out' : dig_Out, 'close_file' : 0, 'mode': 0, 'diff': 1000, 'save_log': 1, 'count_a': 1000, 'sync_append': 0}
    # mode: 0 if not started acquisition yet (or if paused) and 1 otherwise (used to write in drift_log_file)
    
    for i in range(len(devices)):
        sync_param['sync_arr_'+chr(ord('@')+i+1)] = np.zeros(1000, dtype = float)


    # Initialize devices
    for device in devices:
        if header['service'] == 'Bitalino' or header['service'] == 'Mini':
            channels = [int(elem[1])-1 for elem in mac_channels if elem[0]==device.macAddress]
        else:
            channels = [int(elem[1]) for elem in mac_channels if elem[0]==device.macAddress]
                
        print('channels: {}'.format(channels))
        device.start(SamplingRate=fs, analogChannels=channels)
        print('START SYSTEM')

  
    now = datetime.now()
    print('start {}'.format(datetime.now()))
    sync_param['sync_time'] = now.strftime("%Y-%m-%d %H:%M:%S.%f")
    print('just before read_modules')
    t, t_str, t_display = read_modules(devices, mac_channels, sensors, header)
 
    sync_param['save_log'] = 1
            
    write_file(t, a_file, drift_log_file, sync_param, str(sync_param['inittime']), save_fmt)
    print('System initiated')                    
    
    return t, t_display, sync_param
    
