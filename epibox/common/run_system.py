

# built-in
import time
import sys
from datetime import datetime

# third-party
import numpy as np

# local 
from epibox.common.read_modules import read_modules
from epibox.common.close_file import close_file
from epibox.common.write_file import write_file
from epibox.common.open_file import open_file


def run_system(devices, a_file, annot_file, drift_log_file, sync_param, directory, mac_channels, sensors, fs, save_fmt, header):
    
    if time.time()-sync_param['strtime'] > 5:

        sync_param['strtime'] = time.time()
        now = datetime.now()
        sync_time = now.strftime("%Y-%m-%d %H:%M:%S.%f").rstrip('0')
        sync_param['sync_time'] = sync_time
        sync_param['connection'] = 1
        sync_param['sync_append'] = 0
    
    for i,device in enumerate(devices):
        sync_param['sync_arr_'+chr(ord('@')+i+1)] = np.zeros(1000, dtype = float)
    
    now = datetime.now()
    sync_param['sync_time'] = now.strftime("%Y-%m-%d %H:%M:%S.%f")
    t, t_str, t_display = read_modules(devices, mac_channels, sensors, header)

    
    # Open new file each hour
    if time.time()-sync_param['inittime'] > 60*60:
        sync_param['close_file'] = 1

    i = time.time() - sync_param['inittime']

    # print elapsed time
    sys.stdout.write("\rElapsed time (seconds): % i " % i)
    sys.stdout.flush()
    
    #print('in run system: {}'.format(t))
    try:
        write_file(t, a_file, drift_log_file, sync_param, str(i), save_fmt)
        
    except Exception as e:
        print(e)

    # Open new file each hour
    if sync_param['close_file'] == 1:
        # close the file
        print('closing')
        close_file(a_file, annot_file, drift_log_file)

        # Open a new file
        print('Opening new file')
        a_file, annot_file, drift_log_file, save_fmt = open_file(directory, devices, mac_channels, sensors, fs)

        sync_param['close_file'] = 0
        sync_param['inittime'] = time.time()

    # -----------------------------------------------------------------
    return t, t_display, a_file, drift_log_file, sync_param
