from epibox import config_debug


def get_header(
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

    header_dict = {}
    resolution = {}
    columns = []
    fmt = []  # get format to save values in txt

    for n_device, device in enumerate(devices):

        fmt += ["%i"]
        header_dict[device.macAddress] = {}
        header_dict[device.macAddress]["sensor"] = []
        for i, elem in enumerate(mac_channels):
            if elem[0] == device.macAddress:
                header_dict[device.macAddress]["sensor"] += [sensors[i]]
                if save_raw:
                    fmt += ["%i"]
                else:
                    fmt += ["%.2f"]
        header_dict[device.macAddress]["device name"] = "Device " + \
            str(n_device + 1)

        aux = [elem[1]
               for elem in mac_channels if elem[0] == device.macAddress]
        header_dict[device.macAddress]["column"] = ["nSeq"] + aux
        columns += header_dict[device.macAddress]["column"]

        header_dict[device.macAddress]["start time"] = file_time
        header_dict[device.macAddress]["device connection"] = device.macAddress

        header_dict[device.macAddress]["channels"] = [
            int(elem[1]) for elem in mac_channels if elem[0] == device.macAddress
        ]

        header_dict[device.macAddress]["date"] = file_date
        # header_dict[device.macAddress]["firmware version"] = device.version()

        if service == "bitalino":
            header_dict[device.macAddress]["device"] = "bitalino_rev"
            aux = [10, 10, 10, 10, 6, 6]  # resolution
        elif service == "scientisst":
            header_dict[device.macAddress]["device"] = "scientisst_sense"
            aux = [12, 12, 12, 12, 12, 12]
        else:
            raise ValueError("Device not recognized")

        aux2 = [1 for elem in mac_channels if elem[0] == device.macAddress]
        header_dict[device.macAddress]["resolution"] = [4] + [
            aux[i] for i in range(len(aux2))
        ]
        resolution[device.macAddress] = header_dict[device.macAddress]["resolution"]

        header_dict[device.macAddress]["sampling rate"] = fs

        if save_raw:
            header_dict[device.macAddress]["label"] = [
                "RAW" for elem in mac_channels if elem[0] == device.macAddress
            ]
        else:
            header_dict[device.macAddress]["label"] = [
                sensors[i]
                for i, elem in enumerate(mac_channels)
                if elem[0] == device.macAddress
            ]

    header = {"resolution": resolution,
              "save_raw": save_raw, "service": service}

    config_debug.log(f"# {header_dict} \n")
    config_debug.log(f"# {columns} \n")

    filename.write("# " + str(header_dict) + "\n")
    filename.write("# " + str(columns) + "\n")

    return tuple(fmt), header
