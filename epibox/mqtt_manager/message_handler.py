# built-in
import ast
import os
import subprocess
import json
import shutil
from sys import platform

# local
from epibox import config_debug
from epibox.common.get_defaults import get_default
from epibox.exceptions.system_exceptions import (
    MQTTConnectionError,
    PlatformNotSupportedError,
)


def send_default(client, username):

    ######## Available drives ########

    if platform == "linux" or platform == "linux2":
        # linux
        drive_path = f"/media/{username}"
    elif platform == "darwin":
        # macos
        drive_path = "/Volumes"
    else:
        raise PlatformNotSupportedError

    listDrives = ["DRIVES"]
    drives = os.listdir(f"/{drive_path}/")

    for drive in drives:
        total, _, free = shutil.disk_usage(f"/{drive_path}/{drive}")
        listDrives += ["{} ({:.1f}% livre)".format(drive,
                                                   (free / total) * 100)]

    message_info = client.publish(
        topic="rpi", qos=2, payload="{}".format(listDrives)
    )  # raises ValueError and TypeError
    if message_info.rc == 4:
        raise MQTTConnectionError

    ######## Default MAC addresses ########

    defaults = get_default(username)
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

    username = pwd.getpwuid(os.getuid())[0]
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
        client.newAnnot = message[1]

    elif message[0] == "TURN OFF":
        config_debug.log("TURNING OFF RPI")
        message_info = client.publish(topic="rpi", payload=str(["TURNED OFF"]))
        if message_info.rc == 4:
            raise MQTTConnectionError

    elif message[0] == "TURNED OFF":
        subprocess.run(["sudo", "shutdown", "-h", "now"])

    elif message == ["Send default"]:
        send_default(client, username)

    ######## New default configuration ########

    elif message[0] == "NEW CONFIG DEFAULT":
        defaults = get_default(username)

        for key in message[1].keys():
            defaults[key] = message[1][key]

        with open(
            "/home/{}/Documents/epibox/args.json".format(username), "w+"
        ) as json_file:
            json.dump(defaults, json_file)

        msg = json.dumps(["RECEIVED DEFAULT"])
        message_info = client.publish(topic="rpi", qos=2, payload=msg)
        if message_info.rc == 4:
            raise MQTTConnectionError
