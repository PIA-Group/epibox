import json
import ast
import os
from pathlib import Path


def get_default():

    defaults_path = os.path.join(
        Path.home(), "Documents", "epibox", "args.json")

    if os.path.isfile(defaults_path):

        with open(defaults_path, "r") as json_file:
            defaults = json_file.read()
            defaults = ast.literal_eval(defaults)

    else:  # the first time using EpiBOX Core, there will be no default file
        os.makedirs(os.path.dirname(defaults_path))
        defaults = {
            "initial_dir": "EpiBOX Core",
            "fs": 1000,
            "channels": [],
            "devices_mac": {"MAC1": "COM3"},
            "save_raw": "true",
            "patient_id": "default",
            "service": "scientisst",
        }

    with open(defaults_path, "w+") as json_file:
        json.dump(defaults, json_file)

    return defaults
