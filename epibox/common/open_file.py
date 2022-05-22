# built-in
from datetime import datetime
import os

# local
from epibox.bit.header2bitalino import header2bitalino


def open_file(directory, devices, mac_channels, sensors, fs, save_raw, service):

    # for txt format
    now = datetime.now()
    save_time = now.strftime("%Y-%m-%d %H-%M-%S").rstrip("0")
    file_time = now.strftime("%Y-%m-%d %H:%M:%S.%f").rstrip("0")
    file_time = file_time[11:]
    file_time = '"' + file_time + '"'
    file_date = '"' + save_time[0:10] + '"'

    a_file = open(os.path.join(directory, "A" + save_time + ".txt"), "w")  # data file

    # create header for the acquisition file
    save_fmt, header = header2bitalino(
        a_file,
        file_time,
        file_date,
        devices,
        mac_channels,
        sensors,
        fs,
        save_raw,
        service,
    )

    return a_file, save_fmt, header
