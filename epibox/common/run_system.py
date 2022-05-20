

# built-in
import time
import sys
from datetime import datetime

# third-party
import numpy as np
from epibox import config_debug

# local 
from epibox.common.read_modules import read_modules
from epibox.common.write_file import write_file
from epibox.exceptions.exception_manager import kill_after_duration


def run_system(devices, a_file, sync_param, directory, mac_channels, sensors, fs, save_raw, service, save_fmt, header, client):
    
    # Read batch of samples from the devices and save to the active session's file  ===============================

    if time.time()-sync_param['strtime'] > 5:

        sync_param['strtime'] = time.time()
    
    for i,device in enumerate(devices):
        sync_param['sync_arr_'+chr(ord('@')+i+1)] = np.zeros(1000, dtype = float)
    
    now = datetime.now()
    sync_param['sync_time'] = now.strftime("%Y-%m-%d %H:%M:%S.%f")

    # read batch of samples from devices
    t, t_str, t_display = read_modules(devices, mac_channels, sensors, header)    

    i = time.time() - sync_param['inittime']

    # config_debug.log elapsed time
    sys.stdout.write("\rElapsed time (seconds): % i " % i)
    sys.stdout.flush()
    
    # Write batch of samples to file
    write_file(t, a_file, sync_param, str(i), save_fmt)

    # Open new file each hour
    if sync_param['close_file'] == 1:
        kill_after_duration(client, devices, a_file)

    return t, t_display, a_file, sync_param
