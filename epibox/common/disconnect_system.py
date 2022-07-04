# local
from epibox import config_debug
from epibox.common.close_file import close_file


def disconnect_system(devices, a_file=None, files_open=True, devices_connected=True):

    if devices_connected:
        for device in devices:
            try:
                device.stop()
                device.close()

            except:
                continue

    if files_open:
        close_file(a_file)
