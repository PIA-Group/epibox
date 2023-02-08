# built-in
import time
import sys
from datetime import datetime

# third-party
import numpy as np

# local
from epibox.common.read_modules import read_modules
from epibox.common.write_file import write_acq_file


def run_system(
    devices,
    a_file,
    sync_param,
    mac_channels,
    sensors,
    save_fmt,
    header,
    client,
):

    # Read batch of samples from the devices and save to the active session's file  ===============================

    if time.time() - sync_param["strtime"] > 5:

        sync_param["strtime"] = time.time()

    for i, device in enumerate(devices):
        sync_param["sync_arr_" + chr(ord("@") + i + 1)] = np.zeros(1000, dtype=float)

    now = datetime.now()
    sync_param["sync_time"] = now.strftime("%Y-%m-%d %H:%M:%S.%f")

    # read batch of samples from devices
    t, t_str, t_display = read_modules(devices, mac_channels, sensors, header)

    i = time.time() - sync_param["inittime"]

    # config_debug.log elapsed time
    sys.stdout.write("\rElapsed time (seconds): % i " % i)
    sys.stdout.flush()

    # Write batch of samples to file
    write_acq_file(a_file, t, save_fmt)

    return t, t_display, a_file, sync_param
