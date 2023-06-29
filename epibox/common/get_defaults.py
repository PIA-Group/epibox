import json
import ast
import os
from pathlib import Path


def get_default():

    defaults_dir = os.path.join(
        Path.home(), "Documents", "EpiBOX Core")
    defaults_path = os.path.join(defaults_dir, "args.json")

    defaults = {
            "initial_dir": "EpiBOX Core",
            "fs": 1000,
            "channels": [],
            "devices_mac": {"MAC1": "COM3"},
            "save_raw": "true",
            "patient_id": "default",
            "service": "scientisst",
        }

    if os.path.isdir(defaults_dir):
        
        if os.path.isfile(defaults_path):
            with open(defaults_path, "r") as json_file:
                defaults = json_file.read()
                defaults = ast.literal_eval(defaults)

    else:  # the first time using EpiBOX Core, there will be no default file
        os.makedirs(defaults_dir)

    with open(defaults_path, "w+") as json_file:
        json.dump(defaults, json_file)

    return defaults
