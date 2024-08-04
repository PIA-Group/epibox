# built-in
import time
import os
from sys import platform
from pathlib import Path

# third-party
import paho.mqtt.client as mqtt
from epibox.common.get_defaults import get_default
from epibox.exceptions.system_exceptions import (
    MQTTConnectionError,
    PlatformNotSupportedError,
    StorageTimeout,
)

# local
from epibox.mqtt_manager.message_handler import on_message, send_default
from epibox.mqtt_manager.utils import random_str
from epibox import config_debug


def setup_client():
    # Set up MQTT client =========================================================================

    client_name = random_str(6)
    config_debug.log(f"Client name (acquisition): {client_name}")
    host_name = "192.168.0.10"
    topic = "rpi"

    # raises ValueError and ConnectionRefusedError
    client = mqtt.Client(client_name)

    setattr(client, "keepAlive", True)
    setattr(client, "pauseAcq", False)
    setattr(client, "newAnnot", None)

    client.username_pw_set(username="preepiseizures",
                           password="preepiseizures")
    client.connect(host_name)  # raises ValueError
    client.subscribe(topic)  # raises ValueError
    client.on_message = on_message
    client.loop_start()
    config_debug.log(f"Successfully subcribed to topic {topic}")

    message_info = client.publish(
        "rpi", str(["STARTING"])
    )  # raises ValueError and TypeError
    if message_info.rc == 4:
        raise MQTTConnectionError

    return client


def setup_config(client):
    # Access default configurations on EpiBOX Core and save them to variables ======================

    # inform the EpiBOX App which are the current default devices
    send_default(client)
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
    opt = check_storage(client, opt)

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

    already_notified_pause = False
    system_started = False
    t_all = []

    return t_all, already_notified_pause, system_started


def check_storage(client, opt):
    # Check if default storage is available | loop runs continuosly until it find the storage or until timeout
    # If timeout, setup loop and acquisition are terminated

    if opt["initial_dir"] == "EpiBOX Core":
        drive_path = os.path.join(Path.home(), "Documents", "EpiBOX Core")
        opt["initial_dir"] = os.path.join(drive_path, "acquisitions")

    else:
        if platform == "linux" or platform == "linux2":
            # linux
            import pwd
            drive_path = os.path.join(
                "/media", pwd.getpwuid(os.getuid())[0], opt["initial_dir"])
        elif platform == "darwin":
            # macos
            drive_path = os.path.join("/Volumes", opt["initial_dir"])
        else:
            drive_path = opt["initial_dir"]

        init_connect_time = time.time()
        last_warning = time.time()
        config_debug.log(f'Searching for storage module: {opt["initial_dir"]}')

        for i in range(1000000000):

            if not client.keepAlive:
                break

            if (time.time() - init_connect_time) > 120:
                raise StorageTimeout

            if os.path.isdir(drive_path):
                opt["initial_dir"] = os.path.join(drive_path, "acquisitions")
                break

            else:
                if time.time() - last_warning > 10:
                    message_info = client.publish(
                        "rpi", str(["INSERT STORAGE"]))
                    last_warning = time.time()
                    if message_info.rc == 4:
                        raise MQTTConnectionError

    return opt
