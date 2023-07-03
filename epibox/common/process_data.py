# third-party
from scipy import signal
from scipy.stats import kurtosis
import itertools
import numpy as np

# local
from epibox import config_debug


def get_factors(n):

    n2 = n
    i = 2
    factors = []
    while i * i <= n:
        if n % i:
            i += 1
        else:
            n = i
            factors.append(i)
    if n > 1:
        factors.append(n)

    factors.sort(reverse=True)
    final_factors = [f for f in factors if f > 13]
    to_combine = [f for f in factors if f < 13]
    combos = list(itertools.combinations(to_combine, 2))

    while np.prod(final_factors) != n2:

        config_debug.log(f"combos: {combos}")
        combination = [
            [i, p] for i, p in enumerate([x * y for x, y in combos]) if p <= 13
        ]

        final_factors += [combination[0][1]]
        config_debug.log(f"final_factors: {final_factors}")

        combos.remove(combos[combination[0][0]])

    return final_factors


def decimate(t, fs):
    # if phisiological signal downsample to 100Hz, if acc decimate 10Hz
    t_display = []

    for i in range(t.shape[1]):
        t_aux = t[:, i]
        if fs >= 1000:
            t_aux = signal.decimate(t_aux, 10)

        t_display += [t_aux.tolist()]

    return t_display


def quality_check(t_buffer, sensors):

    """ 
    Check quality from the last 5 seconds of the acquisition file

    Parameters:
    - t_buffer: buffer with 5 seconds to evaluate quality
    - sensors: list of sensors

    Return:
    - list of quality points
    """
    quality = np.ones(t_buffer.shape[1])
    if 'ECG' not in sensors:
        # ECG is by default in position 1
        return list(np.ones(t_buffer.shape[1]) * (kurtosis(t_buffer[:,0]) > 5))
    else:
        for ss, sensor in enumerate(sensors):
            if sensor == 'ECG':
                quality[ss] = int(2 * (kurtosis(t_buffer[:, -t_buffer.shape[1]+ss]) > 5)) # returns 0 or 2
            if sensor == 'RESP':
                quality[ss] = int(2 * (max(t_buffer[:,-t_buffer.shape[1]+ss]) - min(t_buffer[:,-t_buffer.shape[1]+ss]) > 0))
            if sensor == 'ACC':
                quality[ss] = int(2 * (max(t_buffer[:,-t_buffer.shape[1]+ss]) - min(t_buffer[:,-t_buffer.shape[1]+ss]) > 0))
        return quality
    
    
