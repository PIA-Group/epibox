# built-in
from datetime import datetime
import os

# third-party
import numpy as np

# local
from epibox import config_debug


def write_acq_file(a_file, t, fmt):
    np.savetxt(
        a_file,
        t,
        fmt=fmt,
        delimiter="	",
        newline="\n",
        header="",
        footer="",
        comments="",
    )


def write_annot_file(recording_name, annot):

    with open(
        os.path.join(os.path.split(recording_name)[0], "annotations" + ".txt"), "a+"
    ) as file:
        file.write(
            f"{os.path.split(recording_name)[1]}    {annot[0]}    {annot[1]}    {datetime.now()}\n"
        )


def write_summary_file(recording_name):

    duration = datetime.now() - datetime.strptime(
        os.path.split(recording_name)[1][1:-4], "%Y-%m-%d %H-%M-%S"
    )
    config_debug.log(f"duration: {str(duration)}")

    with open(
        os.path.join(os.path.split(recording_name)[0], "summary" + ".txt"), "a+"
    ) as file:
        file.write(
            "{}  {}\n".format(
                os.path.split(recording_name)[1], str(duration).split(".")[0]
            )
        )
