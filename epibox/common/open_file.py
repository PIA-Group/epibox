# built-in
from datetime import datetime
import os

# local
from epibox.bit.header2bitalino import header2bitalino
from epibox.scientisst.header2scientisst import header2scientisst

def open_timestamps_file(directory, stage, save_time=None):
    if save_time is None:
        now = datetime.now()
        save_time = now.strftime("%Y-%m-%d %H-%M-%S").rstrip('0')

    #a_file = open(os.path.join(directory, 'mqtt_timestamps_' + '{}_'.format(stage) + save_time + '.txt'), 'w')
    a_file = open(os.path.join(directory, 'mqtt_timestamps_{}_{}.txt'.format(stage, save_time)), 'w')

    return a_file, save_time


def open_file(directory, devices, mac_channels, sensors, fs, saveRaw, service):

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
    
    if service == 'Bitalino' or service == 'Mini':
        save_fmt, header = header2bitalino(a_file, file_time, file_date, devices, mac_channels, sensors, fs, saveRaw, service)
    else:
        save_fmt, header = header2scientisst(a_file, file_time, file_date, devices, mac_channels, sensors, fs, saveRaw)
    
    drift_log_file = open(os.path.join(directory, 'drift_log_file_'+ save_time +'.txt'), 'w')


    return a_file, annot_file, drift_log_file, save_fmt, header
