import numpy as np
import os
import time

timestamps_file = open(os.path.join('/home/ana/Documents/', 'mqtt_timestamps.txt'), 'w')

t = time.time()
np.savetxt(timestamps_file, [[1234, 1]], fmt='%s %s' ,delimiter='  ', newline='\n', header='', footer='', comments ='')

timestamps_file.close()