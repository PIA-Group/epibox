# third-party
from scipy import signal
import itertools
import numpy as np

from epibox import config_debug

def get_factors(n):

    
    n2 = n
    i = 2
    factors = []
    while i * i <= n:
        if n % i:
            i += 1
        else:
            n //= i
            factors.append(i)
    if n > 1:
        factors.append(n)
    
    factors.sort(reverse=True) 
    final_factors = [f for f in factors if f > 13]
    to_combine = [f for f in factors if f < 13]
    combos = list(itertools.combinations(to_combine, 2))

    while np.prod(final_factors) != n2:
        
        config_debug.log(f'combos: {combos}')
        combination = [[i,p] for i,p in enumerate([x * y for x,y in combos]) if p <= 13]

        final_factors += [combination[0][1]]
        config_debug.log(f'final_factors: {final_factors}')

        combos.remove(combos[combination[0][0]])
    
    return final_factors

def decimate(t, fs):
    # if phisiological signal downsample to 100Hz, if acc decimate 10Hz
    t_display = []

    for i in range(t.shape[1]):
        t_aux = t[:,i]
#         for n in get_factors(fs / 100):
#             try:
#                 t_aux = signal.decimate(t_aux, int(n))
#                 config_debug.log('after decimate: {}'.format(t_aux))
#             except Exception as e:
#                 config_debug.log(e)
#                 pass
        if fs >= 1000:
            t_aux = signal.decimate(t_aux, 10)
            
        t_display += [t_aux.tolist()]


    return t_display