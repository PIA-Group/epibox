# third-party
import bitalino
import scientisst
from serial.tools.list_ports import comports

# local
from epibox import config_debug
from epibox.exceptions.system_exceptions import (
    BITalinoParameterError,
    MQTTConnectionError,
    ScientISSTConnectionError,
    ScientISSTNotFound,
)


def connect_device(address, client, devices, service):

    connected = False
    devices = [d for d in devices if d]  # remove None

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
            device = bitalino.BITalino(address, timeout=5)
            setattr(device, "address", address) # Bitalino uses "address" attribute and ScientISST uses "address"
            devices += [device]

        elif service == "scientisst":

            # TODO: implement for windows - find COM port through MAC
            # ports = comports()
            # address = [port.device for port in ports if address in port.device]

            # if address == []:
            #     raise ScientISSTNotFound
            # else:
            #     address = address[0]

            device = scientisst.ScientISST(address)
            devices += [device]

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
