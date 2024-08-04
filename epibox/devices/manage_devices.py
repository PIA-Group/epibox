# built-in
import time
from datetime import datetime
import json

# third-party

import numpy as np
import serial

# local
from epibox.devices.connect_device import connect_device
from epibox import config_debug
from epibox.exceptions.system_exceptions import (
    DeviceConnectionTimeout,
    DeviceNotIDLEError,
    DeviceNotInAcquisitionError,
    MQTTConnectionError,
    ScientISSTNotFound,
)


def start_devices(client, devices, fs, mac_channels, header):

    # Start acquisition with the biosignal acquisition devices, considering the chosen sampling ferquency
    # and channels

    dig_Out = 0
    now = datetime.now()
    sync_param = {
        "flag_sync": 0,
        "inittime": time.time(),
        "strtime": time.time(),
        "sync_time": now.strftime("%Y-%m-%d %H:%M:%S.%f").rstrip("0"),
        "dig_Out": dig_Out,
        "close_file": 0,
        "mode": 0,
        "diff": 1000,
        "save_log": 1,
        "count_a": 1000,
        "sync_append": 0,
    }
    # mode: 0 if not started acquisition yet (or if paused) and 1 otherwise (used to write in drift_log_file)

    for i in range(len(devices)):
        sync_param["sync_arr_" + chr(ord("@") + i + 1)
                   ] = np.zeros(1000, dtype=float)

    # Initialize devices
    for device in devices:

        if header["service"] == "bitalino":
            channels = [
                int(elem[1]) - 1
                for elem in mac_channels
                if elem[0] == device.address
            ]
        else:
            channels = [
                int(elem[1]) for elem in mac_channels if elem[0] == device.address
            ]

        try:
            if header["service"] == "bitalino":
                device.start(SamplingRate=fs, analogChannels=channels)

            elif header["service"] == "scientisst":
                device.start(sample_rate=fs, channels=channels)

        except Exception as e:
            config_debug.log(e)
            raise DeviceNotIDLEError

    now = datetime.now()

    config_debug.log("start {now}")
    sync_param["sync_time"] = now.strftime("%Y-%m-%d %H:%M:%S.%f")

    message_info = client.publish("rpi", str(["ACQUISITION ON"]))
    if message_info.rc == 4:  # MQTT_ERR_NO_CONN
        raise MQTTConnectionError

    return sync_param


def connect_devices(
    client, devices, opt, already_timed_out,
):

    # This script attempts to connect to the default biosignal acquisition devices in a continuous loop.
    # The loop stops only if:
    #       - connection is successful
    #       - timeout is achieved (2min)

    for mac in opt["devices_mac"]:

        init_connect_time = time.time()
        config_debug.log(f"Searching for Module... {mac}")

        for i in range(10000000):

            if not client.keepAlive:
                break

            if (time.time() - init_connect_time) > 120:
                raise DeviceConnectionTimeout

            try:
                connected = False
                connected, devices = connect_device(
                    mac, client, devices, opt["service"]
                )

                if not (connected and mac in [d.address for d in devices]):
                    if time.time() - init_connect_time > 3 * i:
                        timeout_json = json.dumps(
                            ["TRYING TO CONNECT", "{}".format(mac)]
                        )
                        message_info = client.publish("rpi", timeout_json)
                        if message_info.rc == 4:
                            raise MQTTConnectionError

                else:
                    break

            except serial.SerialException as e:
                time.sleep(2)
                config_debug.log(f"Serial connection refused: {e}")
                if not already_timed_out and (time.time() - init_connect_time > 3 * i):
                    timeout_json = json.dumps(["TIMEOUT", "{}".format(mac)])
                    message_info = client.publish("rpi", timeout_json)
                    if message_info.rc == 4:
                        raise MQTTConnectionError
                    already_timed_out = True

                continue

            except ScientISSTNotFound as e:
                time.sleep(2)
                config_debug.log(f"Connection refused: {e}")
                if not already_timed_out and (time.time() - init_connect_time > 3 * i):
                    timeout_json = json.dumps(["TIMEOUT", "{}".format(mac)])
                    message_info = client.publish("rpi", timeout_json)
                    if message_info.rc == 4:
                        raise MQTTConnectionError
                    already_timed_out = True

                continue

            except Exception as e:
                time.sleep(2)
                config_debug.log(f"Connection refused: {e}")
                if not already_timed_out and (time.time() - init_connect_time > 3 * i):
                    timeout_json = json.dumps(["TIMEOUT", "{}".format(mac)])
                    message_info = client.publish("rpi", timeout_json)
                    if message_info.rc == 4:
                        raise MQTTConnectionError
                    already_timed_out = True

                continue

    return devices


def pause_devices(client, devices):

    try:
        for device in devices:
            device.stop()
    except Exception as e:
        config_debug.log(e)
        raise DeviceNotInAcquisitionError

    message_info = client.publish("rpi", str(["PAUSED"]))
    if message_info.rc == 4:
        raise MQTTConnectionError

    return devices
