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

