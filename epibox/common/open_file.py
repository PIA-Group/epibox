# built-in
from datetime import datetime
import os

# local
from epibox.bit.header2bitalino import header2bitalino

def open_file(directory, devices, mac_channels, sensors, fs, save_raw, service):

    # for txt format
    now = datetime.now()
    save_time = now.strftime("%Y-%m-%d %H-%M-%S").rstrip('0')
    file_time = now.strftime("%Y-%m-%d %H:%M:%S.%f").rstrip('0')
    file_time = file_time[11:]
    file_time = '"' + file_time + '"'
    file_date = '"' + save_time[0:10] + '"'
    
    # we don't open the annot_file because it will be used in another thread
    annot_file = os.path.join(directory, 'ANNOT' + save_time +'.txt') #annotation file
    with open(annot_file, 'w') as fp:
        pass
    
    a_file = open(os.path.join(directory, 'A' + save_time + '.txt'), 'w') #data file
    
    
    save_fmt, header = header2bitalino(a_file, file_time, file_date, devices, mac_channels, sensors, fs, save_raw, service)
    
    
    drift_log_file = open(os.path.join(directory, 'drift_log_file_'+ save_time +'.txt'), 'w')


    return a_file, annot_file, drift_log_file, save_fmt, header
