# built-in
import ast
import os
import subprocess
import json
import shutil
from sys import platform
from pathlib import Path
from datetime import datetime

# local
from epibox import config_debug
from epibox.common.get_defaults import get_default
from epibox.exceptions.system_exceptions import (
    MQTTConnectionError,

)


def send_default(client):

    ######## Available drives ########
    listDrives = ["DRIVES"]

    if platform == "linux" or platform == "linux2":
        # linux
        import pwd
        drive_path = os.path.join("/media", pwd.getpwuid(os.getuid())[0])
        drives = [os.path.join(drive_path, d) for d in os.listdir(drive_path)]
    elif platform == "darwin":
        # macos
        drive_path = "/Volumes"
        drives = [os.path.join(drive_path, d) for d in os.listdir(drive_path)]
    else:
        import win32api
        import win32con
        import win32file
        drives = [i for i in win32api.GetLogicalDriveStrings().split('\x00') if i]
        drives = [d for d in drives if win32file.GetDriveType(
            d) == win32con.DRIVE_REMOVABLE]

    for drive in drives:
        total, _, free = shutil.disk_usage(drive)
        listDrives += ["{} ({:.1f}% livre)".format(drive,
                                                   (free / total) * 100)]

    message_info = client.publish(
        topic="rpi", qos=2, payload="{}".format(listDrives)
    )  # raises ValueError and TypeError
    if message_info.rc == 4:
        raise MQTTConnectionError

    ######## Default MAC addresses ########

    defaults = get_default()
    listMAC = defaults["devices_mac"]
    listMAC2 = json.dumps(["DEFAULT MAC"] +
                          [

        "{}".format(address) for address in list(listMAC.values())
    ]
    )

    message_info = client.publish(
        topic="rpi", qos=2, payload=listMAC2
    )  # raises ValueError and TypeError
    if message_info.rc == 4:
        raise MQTTConnectionError

    config = json.dumps(["DEFAULT CONFIG", defaults])

    message_info = client.publish(
        topic="rpi", qos=2, payload=config
    )  # raises ValueError and TypeError
    if message_info.rc == 4:
        raise MQTTConnectionError


def on_message(client, userdata, message):

    message = str(message.payload.decode("utf-8"))
    message = ast.literal_eval(message)

    if message[0] == "RESTART":
        # client.loop_stop()
        # client.keepAlive = False
        config_debug.log("Not sure what to do here yet")

    elif message[0] == "INTERRUPT":
        client.keepAlive = False

    elif message[0] == "PAUSE ACQ":
        config_debug.log("PAUSING ACQUISITION")
        client.pauseAcq = True

    elif message[0] == "RESUME ACQ":
        config_debug.log("RESUMING ACQUISITION")
        client.pauseAcq = False

    elif message[0] == "ANNOTATION":
        config_debug.log(
            "RECEIVED ANNOT {} ----------------------".format(message[1]))
        client.newAnnot = message[1] + \
            [datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')]

    elif message[0] == "TURN OFF":
        config_debug.log("TURNING OFF RPI")
        message_info = client.publish(topic="rpi", payload=str(["TURNED OFF"]))
        if message_info.rc == 4:
            raise MQTTConnectionError

    elif message[0] == "TURNED OFF":
        subprocess.run(["sudo", "shutdown", "-h", "now"])

    elif message == ["Send default"]:
        send_default(client)

    ######## New default configuration ########

    elif message[0] == "NEW CONFIG DEFAULT":
        defaults = get_default()

        for key in message[1].keys():
            defaults[key] = message[1][key]

        with open(
            os.path.join(Path.home(), "Documents",
                         "EpiBOX Core", "args.json"), "w+"
        ) as json_file:
            json.dump(defaults, json_file)

        msg = json.dumps(["RECEIVED DEFAULT"])
        message_info = client.publish(topic="rpi", qos=2, payload=msg)
        if message_info.rc == 4:
            raise MQTTConnectionError

        client.keepAlive = False
