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
        header_dict[device.address] = {}
        header_dict[device.address]["sensor"] = []
        for i, elem in enumerate(mac_channels):
            if elem[0] == device.address:
                header_dict[device.address]["sensor"] += [sensors[i]]
                if save_raw:
                    fmt += ["%i"]
                else:
                    fmt += ["%.2f"]
        header_dict[device.address]["device name"] = "Device " + \
            str(n_device + 1)

        aux = [elem[1]
               for elem in mac_channels if elem[0] == device.address]
        header_dict[device.address]["column"] = ["nSeq"] + aux
        columns += header_dict[device.address]["column"]

        header_dict[device.address]["start time"] = file_time
        header_dict[device.address]["device connection"] = device.address

        header_dict[device.address]["channels"] = [
            int(elem[1]) for elem in mac_channels if elem[0] == device.address
        ]

        header_dict[device.address]["date"] = file_date
        # header_dict[device.address]["firmware version"] = device.version()

        if service == "bitalino":
            header_dict[device.address]["device"] = "bitalino_rev"
            aux = [10, 10, 10, 10, 6, 6]  # resolution
        elif service == "scientisst":
            header_dict[device.address]["device"] = "scientisst_sense"
            aux = [12, 12, 12, 12, 12, 12]
        else:
            raise ValueError("Device not recognized")

        aux2 = [1 for elem in mac_channels if elem[0] == device.address]
        header_dict[device.address]["resolution"] = [4] + [
            aux[i] for i in range(len(aux2))
        ]
        resolution[device.address] = header_dict[device.address]["resolution"]

        header_dict[device.address]["sampling rate"] = fs

        if save_raw:
            header_dict[device.address]["label"] = [
                "RAW" for elem in mac_channels if elem[0] == device.address
            ]
        else:
            header_dict[device.address]["label"] = [
                sensors[i]
                for i, elem in enumerate(mac_channels)
                if elem[0] == device.address
            ]

    header = {"resolution": resolution,
              "save_raw": save_raw, "service": service}

    config_debug.log(f"# {header_dict} \n")
    config_debug.log(f"# {columns} \n")

    filename.write("# " + str(header_dict) + "\n")
    filename.write("\t".join(columns) + "\n")

    return tuple(fmt), header
