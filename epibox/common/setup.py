# built-in
from http import client
import time
import pwd
import os
import ast

# third-party
import json
import paho.mqtt.client as mqtt
from epibox.common.get_defaults import get_default
from epibox.exceptions.exception_manager import error_kill

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

    client = mqtt.Client(client_name)

    setattr(client, "keepAlive", True)
    setattr(client, "pauseAcq", False)
    setattr(client, "newAnnot", None)

    client.username_pw_set(username="preepiseizures", password="preepiseizures")
    client.connect(host_name)
    client.subscribe(topic)
    client.on_message = on_message
    client.loop_start()
    config_debug.log(f"Successfully subcribed to topic {topic}")

    client.publish("rpi", str(["STARTING"]))

    return client


def setup_config(client):
    # Access default configurations on EpiBOX Core and save them to variables ======================

    username = pwd.getpwuid(os.getuid())[0]

    # inform the EpiBOX App which are the current default devices
    send_default(client, username)
    opt = get_default(username)

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
        except Exception as e:
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
    opt = check_storage(client, [], opt)

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
    files_open = False
    t_all = []

    return t_all, already_notified_pause, system_started, files_open


def check_storage(client, devices, opt):
    # Check if default storage is available | loop runs continuosly until it find the storage or until timeout
    # If timeout, setup loop and acquisition are terminated

    username = pwd.getpwuid(os.getuid())[0]

    init_connect_time = time.time()
    config_debug.log(f'Searching for storage module: {opt["initial_dir"]}')

    i = 0
    while client.keepAlive:

        i += 1

        if (time.time() - init_connect_time) > 120:
            error_kill(
                client,
                devices,
                "Failed to find storage",
                "ERROR",
                files_open=False,
                devices_connected=False,
            )

        try:
            if os.path.isdir("/media/{}/".format(username) + opt["initial_dir"]):
                opt["initial_dir"] = (
                    "/media/{}/".format(username) + opt["initial_dir"] + "/acquisitions"
                )
                break

            else:
                if time.time() - init_connect_time > 3 * i:
                    client.publish("rpi", str(["INSERT STORAGE"]))
                raise Exception

        except Exception as e:
            continue

    return opt
