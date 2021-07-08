# built-in
from copy import copy

# third-party
import numpy as np


def read_modules(devices, mac_channels, sensors, header):
    
    t = np.array([])
    t_display = np.array([])
    print('devices: {}'.format([d.macAddress for d in devices]))
    
    for i, device in enumerate(devices):
        
        t_read = device.read(100)
        t_read = np.delete(t_read, np.arange(1,5), axis=1) # remove digital channels
        t_nseq = t_read[:,1:] # remove nSeq column (add again in the end)
        
        n = 0
        display_aux = np.array([])
        for j,chn in enumerate(mac_channels):
            
            if chn[0] == device.macAddress:
                
                if header['saveRaw']:
                    signal_type = 'RAW'
                else:
                    signal_type = sensors[j]
                    
                r = header['resolution'][device.macAddress][n+1]
                
                t_aux = get_transform(t_nseq[:,n], signal_type, r) # receives and returns a column with 100 samples
                    
                n += 1
                if len(display_aux) == 0:
                    display_aux = copy(t_aux)
                else:
                    display_aux = np.concatenate((display_aux, t_aux), axis=1)
        
        
        if len(t_display) == 0:
            t_display = copy(display_aux)
            t = np.concatenate((np.reshape(t_read[:,0], (-1,1)), display_aux), axis=1)
        else:
            t_display = np.concatenate((t_display, display_aux), axis=1)
            aux = np.concatenate((np.reshape(t_read[:,0], (-1,1)), display_aux), axis=1)
            t = np.concatenate((t, aux), axis=1)
    
    t_str = '\n'.join(' '.join('%0.1f' %x for x in y) for y in t)
    return t, t_str, t_display


def get_transform(raw, signal_type, res):
    
    if signal_type == 'ECG':
        aux = list(map(lambda x: (((x/(2**res)-0.5)*3.3)/1100)*1000, raw))
    elif signal_type == 'EEG':
        aux = list(map(lambda x: (((x/(2**res)-0.5)*3.3)/41782)*(10**(6)), raw))
    elif signal_type == 'EOG':
        aux = list(map(lambda x: (((x/(2**res)-0.5)*3.3)/2040)*1000, raw))
    elif signal_type == 'EMG':
        aux = list(map(lambda x: (((x/(2**res)-0.5)*3.3)/1009)*1000, raw))
    elif signal_type == 'PZT':
        aux = list(map(lambda x: (x/(2**res)-0.5)*100, raw))
    elif signal_type == 'EDA':
        aux = list(map(lambda x: (((x/(2**res))*3.3)/0.132), raw))
    else:
        aux = list(raw)
    
    return np.reshape(np.asarray(aux), (-1,1))
        
