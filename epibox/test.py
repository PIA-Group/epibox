import numpy as np
import os 
import time

from epibox.common.write_file import write_mqtt_timestamp

timestamps_file = open(os.path.join('/home/ana/Documents', 'mqtt_timestamps.txt'), 'w')

t = time.time()
write_mqtt_timestamp(timestamps_file, t, 'id', 'key')

timestamps_file.close()
