import json
import ast
import os
import pwd
from sys import platform

# local
from epibox.exceptions.system_exceptions import PlatformNotSupportedError


def get_default(username):

    username = pwd.getpwuid(os.getuid())[0]

    if platform == "linux" or platform == "linux2":
        # linux
        defaults_path = f"/home/{username}/Documents/epibox/args.json"
    elif platform == "darwin":
        # macos
        defaults_path = "/Users/anasofiacc/Documents/epibox/args.json"
    else:
        raise PlatformNotSupportedError

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
            "devices_mac": {"MAC1": "12:34:56:78:91:10", "MAC2": "01:19:87:65:43:21"},
            "save_raw": "true",
            "patient_id": "default",
            "service": "Bitalino",
        }

    with open(defaults_path, "w+") as json_file:
        json.dump(defaults, json_file)

    return defaults
