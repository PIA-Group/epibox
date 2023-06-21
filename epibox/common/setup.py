# built-in
import time
import os
from sys import platform

# third-party
from epibox.common.get_defaults import get_default
from epibox.exceptions.system_exceptions import (
    MQTTConnectionError,
    PlatformNotSupportedError,
    StorageTimeout,
)

# local
from epibox import config_debug



def setup_config():
    # Access default configurations on EpiBOX Core and save them to variables ======================


    # inform the EpiBOX App which are the current default devices
    opt = get_default()

    if not opt["channels"]:
        # if default "channels" is empty, acquire all
        channels = []
        for device in opt["devices_mac"].values():
            for i in range(1, 7):
                channels += [[device, str(i)]]
        sensors = ["-" for i in range(len(channels))]

    else:
        # default "channels" is saved in the format [[MAC1, channel1, sensor1], [MAC1, channel2, sensor2], ...]
        channels = []
        sensors = []
        try:
            for triplet in opt["channels"]:
                triplet[0] = opt["devices_mac"][
                    triplet[0]
                ]  # replace MAC ID for corresponding MAC
                channels += [triplet[:2]]
                sensors += [triplet[2]]

        except Exception as e:  # TODO what kind of errors are raised?
            config_debug.log(e)
            for tt, triplet in enumerate(opt["channels"]):
                if tt < 7:
                    triplet[0] = opt["devices_mac"]["MAC1"]
                else:
                    triplet[0] = opt["devices_mac"]["MAC2"]
                channels += [triplet[:2]]
                sensors += [triplet[2]]

    save_raw = bool(opt["save_raw"])
    service = opt["service"]

    opt["devices_mac"] = [m for m in opt["devices_mac"].values() if m != ""]

    # check if default storage is available | if not, terminate setup loop and acquisition
    opt = check_storage(opt)

    config_debug.log("ID: {}".format(opt["patient_id"]))
    config_debug.log("folder: {}".format(opt["initial_dir"]))
    config_debug.log("fs: {}".format(opt["fs"]))
    config_debug.log(f"save_raw: {save_raw}")
    config_debug.log(f"channels: {channels}")
    config_debug.log("devices: {}".format(opt["devices_mac"]))
    config_debug.log(f"sensors: {sensors}")
    config_debug.log(f"service: {service}")

    return opt, channels, sensors, service, save_raw


def setup_variables():

    system_started = False
    t_all = []

    return t_all, system_started


def check_storage(opt):
    # Check if default storage is available | loop runs continuosly until it find the storage or until timeout
    # If timeout, setup loop and acquisition are terminated


    if platform == "linux" or platform == "linux2":
        # linux
        drive_path = f"/media/{os.environ.get('USERNAME')}"
    elif platform == "darwin":
        # macos
        drive_path = "/Volumes"
    else:
        # import win32api
        # import win32con
        # import win32file
        # drives = [i for i in win32api.GetLogicalDriveStrings().split('\x00') if i]
        # drive_path = [d for d in drives if win32file.GetDriveType(d) == win32con.DRIVE_REMOVABLE]
        drive_path = ""

    init_connect_time = time.time()
    config_debug.log(f'Searching for storage module: {opt["initial_dir"]}')

    for i in range(100000):

        if (time.time() - init_connect_time) > 120:
            raise StorageTimeout

        if os.path.isdir(f"/{drive_path}/" + opt["initial_dir"]):
            opt["initial_dir"] = (
                f"/{drive_path}/" + opt["initial_dir"] + "/acquisitions"
            )
            break

    return opt
