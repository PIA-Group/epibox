# built-in
from datetime import datetime
import os
from time import strptime 

# third-party
import numpy as np


def write_file(t, a_file, sync_param, time, fmt):
    write_acq_file(a_file, t, time, fmt)


def write_acq_file(a_file, t, time, fmt):
	np.savetxt(a_file, t, fmt=fmt, delimiter='	', newline='\n', header='', footer='', comments ='')


def write_drift_log(filename, sync_param):

    sync_time = sync_param['sync_time']
    
    if not sync_param['mode']:
        filename.write('%s' % sync_time + '\n')
        sync_param['mode'] = 1
    else:
        filename.write('\n')
    
    print('%s' % '  ' + sync_time)


def write_annot_file(recording_name, annot):
    with open(os.path.join(os.path.split(recording_name)[0], 'ANNOT' + os.path.split(recording_name)[1][1:]), 'a+') as file:
        file.write('{}	{}\n'.format(annot[0], annot[1]))
  

def write_summary_file(recording_name):

    duration = datetime.now() - datetime.strptime(os.path.split(recording_name)[1][1:-4], '%Y-%m-%d %H-%M-%S')
    print(f'duration: {str(duration)}')

    with open(os.path.join(os.path.split(recording_name)[0], 'summary' + '.txt'), 'a+') as file:
        file.write('{}	{}\n'.format(os.path.split(recording_name)[1], str(duration).split('.')[0]))