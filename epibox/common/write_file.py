import numpy as np


def write_file(t, a_file, drift_log_file, sync_param, time, fmt):
    write_acq_file(a_file, t, time, fmt)
    write_drift_log(drift_log_file, sync_param)


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


def write_annot_file(annot_file, annot):
    with open(annot_file, 'a') as file:
        file.write('{}	{}\n'.format(annot[0], annot[1]))
  