import json
import ast
import os
import time
from pathlib import Path


def get_default():

    defaults_dir = os.path.join(
        Path.home(), "Documents", "EpiBOX Core")
    defaults_path = os.path.join(defaults_dir, "args.json")

    defaults = {
        "initial_dir": "EpiBOX Core",
        "fs": 1000,
        "channels": [],
        "devices_mac": {"MAC1": "34:94:54:5E:32:2E"},
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


def set_new_default_item(item_key, item):

    defaults = get_default()
    defaults[item_key] = item

    with open(
        os.path.join(Path.home(), "Documents",
                     "EpiBOX Core", "args.json"), "w+"
    ) as json_file:
        json.dump(defaults, json_file)

    time.sleep(5)
