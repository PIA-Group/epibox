# built-in
import json

# local
from epibox.devices.manage_devices import connect_devices, start_devices
from epibox.exceptions.exception_manager import (
    handle_case_6,
    kill_case_1,
    kill_case_2,
    kill_case_3,
    kill_case_4,
    kill_case_5,
    kill_case_7,
)
from epibox.common.setup import setup_client, setup_config, setup_variables
from epibox.common.create_folder import create_folder
from epibox.common.open_file import open_file
from epibox.common.write_file import write_annot_file
from epibox.common.run_system import run_system
from epibox.common import process_data
from epibox import config_debug
from epibox.exceptions.system_exceptions import (
    BITalinoParameterError,
    DeviceConnectionTimeout,
    DeviceNotIDLEError,
    DeviceNotInAcquisitionError,
    MQTTConnectionError,
    PlatformNotSupportedError,
    StorageTimeout,
)


# ****************************** MAIN SCRIPT ***********************************
# This is the main script. It is lauched by EpiBOX Core, through the epibox_startup.sh Bash script.

# This script attempts to connect to the default biosignal acquisition devices in a continuous loop.
# The loop stops only if:
#       - connection is successful
#       - timeout is achieved (2min)

# If timeout, the script ends (being later lauched again by EpiBOX Core)
# If connection is successful, acquisition starts and PyEpiBOX receives and handles data from the
# acquisition devices.
# The loop stops only if:
#       - user stops the acquisition
#       - at least one of the devices disconnects


class Client(object):
    def __init__(self):
        self.keepAline = True

def main():

    devices = []
    # Setup MQTT client | read default configurations | initiate variables ===========================
    
    try:
        client = Client()
        opt, channels, sensors, service, save_raw = setup_config()

        (
            t_all,
            system_started,
        ) = setup_variables()  # raises no errors

        # Create folder with patient ID
        directory = create_folder(
            opt["initial_dir"], "{}".format(opt["patient_id"]))

    except (
        ConnectionRefusedError,
        ValueError,
        TypeError,
        OSError,
        StorageTimeout,
        PlatformNotSupportedError,
    ) as e:
        config_debug.log(e)
        kill_case_2()


    # Start loop to connect PyEpiBOX to acquisition devices =========================================
    try:
        devices = connect_devices(  # exceptions handled inside
            devices, opt
        )

    except (
        DeviceConnectionTimeout,
        ValueError,
        TypeError,
        BITalinoParameterError,
    ) as e:
        config_debug.log(e)
        kill_case_3(devices)

    except MQTTConnectionError as e:
        config_debug.log(e)
        kill_case_4(devices)

    config_debug.log("Initial setup complete!")

    while client.keepAlive:

        try:

            if not system_started:
                # If the devices have not yet started acquiring or they are paused, start acquisition
                a_file, save_fmt, header = open_file(
                    directory,
                    devices,
                    channels,
                    sensors,
                    opt["fs"],
                    save_raw,
                    service,
                )
                sync_param = start_devices(
                    devices, opt["fs"], channels, header
                )
                system_started = True

            # Read batch of samples from the acquisition devices and store on the active session's file
            _, t_disp, a_file, sync_param = run_system(
                devices,
                a_file,
                sync_param,
                channels,
                sensors,
                save_fmt,
                header,
            )

            # Subsample batch of samples and send to the EpiBOX App for visualization purposes ================
            t_display = process_data.decimate(t_disp, opt["fs"])
            t_all += t_display[0]

        except (
            DeviceNotIDLEError,
            BITalinoParameterError,
            FileNotFoundError,
            PermissionError,
            OSError,
            KeyboardInterrupt,
        ) as e:
            config_debug.log(e)
            kill_case_5(devices, a_file)

        except DeviceNotInAcquisitionError as e:
            config_debug.log(e)

            system_started = handle_case_6(devices, a_file, system_started)
            continue

        except MQTTConnectionError as e:
            config_debug.log(e)
            kill_case_7(devices, a_file)

    # =========================================================================================================
