import numpy as np

def detect_event(t, sensors):
    strength_list = [0] * len(sensors)

    for i,chn in enumerate(t):
        
        if sensors[i] == 'EMG':
            print(f'sum square: {np.sum(np.square(chn-np.mean(chn)))} | variance: {np.var(chn)} | mean sqrt: {np.mean(np.sqrt(chn))}\n')
            if np.sum(np.sum(np.square(chn-np.mean(chn)))) > 20000:
                strength_list[i] = 1
            if np.sum(np.sum(np.square(chn-np.mean(chn)))) > 60000:
                strength_list[i] = 2


    return strength_list


