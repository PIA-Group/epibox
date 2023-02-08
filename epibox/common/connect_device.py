# built-in
import string
import random

# third-party
import bitalino

# local
from epibox import config_debug
from epibox.exceptions.system_exceptions import (
    BITalinoParameterError,
    MQTTConnectionError,
)


def connect_device(macAddress, client, devices):

    connected = False
    devices = [d for d in devices if d]  # remove None
    config_debug.log(f" devices: {devices}")

    if macAddress in [d.macAddress for d in devices]:
        try:
            config_debug.log(
                f"{macAddress} state: {[d.state()for d in devices if d.macAddress==macAddress]}"
            )
            connected = True

        except AttributeError:
            del devices[[d.macAddress for d in devices].index(macAddress)]

    else:

        try:
            device = bitalino.BITalino(macAddress, timeout=5)
            devices += [device]

        except Exception as e:
            config_debug.log(e)
            raise BITalinoParameterError

    devices = [d for d in devices if d]  # remove None

    if not connected or macAddress not in [d.macAddress for d in devices]:
        message_info = client.publish(
            topic="rpi",
            qos=2,
            payload="['MAC STATE', '{}', '{}']".format(macAddress, "failed"),
        )
        if message_info.rc == 4:
            raise MQTTConnectionError
    else:
        message_info = client.publish(
            topic="rpi",
            qos=2,
            payload="['MAC STATE', '{}', '{}']".format(macAddress, "connected"),
        )
        if message_info.rc == 4:
            raise MQTTConnectionError

    return connected, devices
