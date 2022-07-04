# built-in
import subprocess
import time

# local
from epibox.common.disconnect_system import disconnect_system
from epibox.common.write_file import write_summary_file
from epibox import config_debug


def error_kill(
    client,
    devices,
    msg,
    mqtt_msg="ERROR",
    a_file=None,
    files_open=True,
    devices_connected=True,
):

    config_debug.log(msg)
    client.publish("rpi", str([mqtt_msg]))
    client.loop_stop()

    # Disconnect the system
    disconnect_system(devices, a_file, files_open, devices_connected)

    pid = subprocess.run(
        ["sudo", "pgrep", "python"], capture_output=True, text=True
    ).stdout.split("\n")[:-1]
    for p in pid:
        subprocess.run(["kill", "-9", p])

    config_debug.log("killed")


def error_disconnect(client, devices, msg, a_file=None, files_open=True):

    config_debug.log("The system has stopped running because " + str(msg))
    client.publish("rpi", str(["RECONNECTING"]))

    # Disconnect the system
    write_summary_file(a_file.name)
    disconnect_system(devices, a_file, files_open)

    devices = []
    system_started = False

    return devices, system_started


def kill_after_duration(client, devices, a_file=None, files_open=True):

    client.publish("rpi", str(["STOPPED"]))
    client.loop_stop()

    # Disconnect the system
    write_summary_file(a_file.name)
    disconnect_system(devices, a_file, files_open)

    pid = subprocess.run(
        ["sudo", "pgrep", "python"], capture_output=True, text=True
    ).stdout.split("\n")[:-1]
    for p in pid:
        subprocess.run(["kill", "-9", p])


def client_kill(client, devices, msg, a_file=None, files_open=True):

    config_debug.log(msg)
    client.publish("rpi", str(["STOPPED"]))
    client.loop_stop()

    # Disconnect the system
    disconnect_system(devices, a_file, files_open)

    pid = subprocess.run(
        ["sudo", "pgrep", "python"], capture_output=True, text=True
    ).stdout.split("\n")[:-1]
    for p in pid:
        subprocess.run(["kill", "-9", p])
