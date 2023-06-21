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


def connect_device(address, devices, service):

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
            device = bitalino.BITalino(address, timeout=5)
            devices += [device]

        elif service == "scientisst":
            ports = comports()
            address = [port.device for port in ports if address in port.device]

            if address == []:
                raise ScientISSTNotFound
            else:
                address = address[0]

            device = scientisst.ScientISST(address)
            devices += [device]

    devices = [d for d in devices if d]  # remove None

    return connected, devices
