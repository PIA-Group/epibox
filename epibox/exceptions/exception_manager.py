# built-in
import subprocess
import time
import sys

# local
from epibox.common.write_file import write_summary_file
from epibox import config_debug


def kill_subprocess():

    config_debug.log("  -- killing subprocess --")
    time.sleep(5)
    sys.exit()


def kill_client(client):

    try:
        client.publish("rpi", str(["STOPPED"]))
        client.loop_stop()
        config_debug.log("  -- client loop stopped --")

    except:
        pass


def close_devices(devices):

    for device in devices:
        try:
            device.close()
        except:
            device.disconnect()

    config_debug.log("  -- all devices closed --")


def stop_devices(devices):

    for device in devices:
        device.stop()

    config_debug.log("  -- all devices stopped --")


# Kill and error handling cases ===========================================================================


# | | __client__ | __devices open__ | __file open__ | __devices started__ | __acquired__|
# |:---: | :---: | :----: | :---: | :---: | :---: |
# |__kill 1__ | N | N | N | N | N |
# |__kill 2__ | Y | N | N | N | N |
# |__kill 3__ | Y | Y - | N | N | N |
# |__kill 4__ | N | Y - | N | N | N |
# |__kill 5__ | Y | Y - | Y | Y - | Y |
# |__handle 6__ | Y | Y | Y | N - | Y |
# |__kill 7__ | N | Y | Y | Y | Y |


def kill_case_1():
    # Client: N
    # Devices open: N
    # File open: N
    # Devices started: N

    kill_subprocess()


def kill_case_2(client):
    # Client: Y
    # Devices open: N
    # File open: N
    # Devices started: N

    kill_client(client)
    kill_subprocess()


def kill_case_3(client, devices):
    # Client: Y
    # Devices open: Y (might not be true for all devices)
    # File open: N
    # Devices started: N

    close_devices(devices)
    kill_client(client)
    kill_subprocess()


def kill_case_4(devices):
    # Client: N
    # Devices open: Y (might not be true for all devices)
    # File open: N
    # Devices started: N

    close_devices(devices)
    kill_subprocess()


def kill_case_5(client, devices, a_file):
    # Client: Y
    # Devices open: Y (might not be true for all devices)
    # File open: Y
    # Devices started: Y (might not be true for all devices)
    stop_devices(devices)
    close_devices(devices)
    write_summary_file(a_file.name)
    a_file.close()
    kill_client(client)
    kill_subprocess()


def handle_case_6(devices, a_file, system_started):
    # Client: Y
    # Devices open: Y
    # File open: Y
    # Devices started: N (might not be true for all devices)

    stop_devices(devices)
    write_summary_file(a_file.name)
    a_file.close()
    system_started = False

    return system_started


def kill_case_7(devices, a_file):
    # Client: N
    # Devices open: Y
    # File open: Y
    # Devices started: Y

    stop_devices(devices)
    close_devices(devices)
    write_summary_file(a_file.name)
    a_file.close()
    kill_subprocess()
