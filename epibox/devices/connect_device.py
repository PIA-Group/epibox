# third-party
import bitalino
import scientisst

# local
from epibox import config_debug
from epibox.exceptions.system_exceptions import (
    BITalinoParameterError,
    MQTTConnectionError,
    ScientISSTConnectionError,
)


def connect_device(address, client, devices, service):

    connected = False
    devices = [d for d in devices if d]  # remove None
    config_debug.log(f" devices: {devices}")

    if address in [d.address for d in devices]:
        try:
            config_debug.log(
                f"{address} state: {[d.state()for d in devices if d.address==address]}"
            )
            connected = True

        except AttributeError:
            del devices[[d.address for d in devices].index(address)]

    else:

        if service == "bitalino":
            try:
                device = bitalino.BITalino(address, timeout=5)
                devices += [device]

            except Exception as e:
                config_debug.log(e)
                raise BITalinoParameterError

        elif service == "scientisst":
            try:
                device = scientisst.ScientISST(address)
                devices += [device]

            except Exception as e:
                config_debug.log(e)
                raise ScientISSTConnectionError

    devices = [d for d in devices if d]  # remove None

    if not connected or address not in [d.address for d in devices]:
        message_info = client.publish(
            topic="rpi",
            qos=2,
            payload="['MAC STATE', '{}', '{}']".format(address, "failed"),
        )
        if message_info.rc == 4:
            raise MQTTConnectionError
    else:
        message_info = client.publish(
            topic="rpi",
            qos=2,
            payload="['MAC STATE', '{}', '{}']".format(address, "connected"),
        )
        if message_info.rc == 4:
            raise MQTTConnectionError

    return connected, devices
