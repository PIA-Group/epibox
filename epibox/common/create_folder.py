# built-in
import os

# local
from epibox import config_debug


def create_folder(initial_dir, nb):

    # Create folder with patient ID unless it already exists
    directory = os.path.join(initial_dir, nb)

    if not os.path.exists(directory):
        os.makedirs(directory)
        config_debug.log(f"Created patient directory -- {directory}")

    else:
        config_debug.log(f"Directory -- {directory} -- already exists")

    return directory
