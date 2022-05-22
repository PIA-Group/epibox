from glob import glob
from epibox import config_debug


def header2bitalino(
    filename,
    file_time,
    file_date,
    devices,
    mac_channels,
    sensors,
    fs,
    save_raw,
    service,
):

    filename.write("# OpenSignals Text File Format" + "\n")

    mac_dict = {}
    resolution = {}
    fmt = []  # get format to save values in txt

    for n_device, device in enumerate(devices):

        fmt += ["%i"]
        mac_dict[device.macAddress] = {}
        config_debug.log("1")
        mac_dict[device.macAddress]["sensor"] = []
        for i, elem in enumerate(mac_channels):
            if elem[0] == device.macAddress:
                mac_dict[device.macAddress]["sensor"] += [sensors[i]]
                if save_raw:
                    fmt += ["%i"]
                else:
                    fmt += ["%.2f"]
        config_debug.log("2")
        mac_dict[device.macAddress]["device name"] = "Device " + str(n_device + 1)
        config_debug.log("3")

        aux = ["A" + elem[1] for elem in mac_channels if elem[0] == device.macAddress]
        config_debug.log("4")
        mac_dict[device.macAddress]["column"] = ["nSeq"] + aux

        mac_dict[device.macAddress]["sync interval"] = 2  # ???

        mac_dict[device.macAddress]["start time"] = file_time
        config_debug.log("5")
        mac_dict[device.macAddress]["device connection"] = device.macAddress
        config_debug.log("6")

        mac_dict[device.macAddress]["channels"] = [
            int(elem[1]) for elem in mac_channels if elem[0] == device.macAddress
        ]
        config_debug.log("7")

        mac_dict[device.macAddress]["date"] = file_date
        config_debug.log("8")
        mac_dict[device.macAddress]["firmware version"] = device.version()
        config_debug.log("9")

        if service == "Bitalino":
            mac_dict[device.macAddress]["device"] = "bitalino_rev"
        else:
            mac_dict[device.macAddress]["device"] = "bitalino_mini"

        mac_dict[device.macAddress]["sampling rate"] = fs

        config_debug.log("10")
        if save_raw:
            mac_dict[device.macAddress]["label"] = [
                "RAW"
                for i, elem in enumerate(mac_channels)
                if elem[0] == device.macAddress
            ]
        else:
            mac_dict[device.macAddress]["label"] = [
                sensors[i]
                for i, elem in enumerate(mac_channels)
                if elem[0] == device.macAddress
            ]
        config_debug.log("11")
        aux = [10, 10, 10, 10, 6, 6]
        aux2 = [1 for elem in mac_channels if elem[0] == device.macAddress]
        mac_dict[device.macAddress]["resolution"] = [4] + [
            aux[i] for i in range(len(aux2))
        ]
        resolution[device.macAddress] = mac_dict[device.macAddress]["resolution"]

    header = {"resolution": resolution, "save_raw": save_raw, "service": service}

    config_debug.log(f"# {mac_dict} \n")
    filename.write("# " + str(mac_dict) + "\n")
    filename.write("# EndOfHeader" + "\n")

    return tuple(fmt), header
