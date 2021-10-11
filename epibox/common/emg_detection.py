import numpy as np

def detect_event(t, sensors):

    for i,chn in enumerate(t):
        
        if sensors[i] == 'EMG':
            print(f'median: {np.median(chn)} | variance: {np.var(chn)} | abs sum: {np.sum(np.abs(chn))}\n')

