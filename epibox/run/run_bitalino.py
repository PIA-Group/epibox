# built-in
import json

# local
from epibox.bit.manage_devices import pause_devices, connect_devices, start_devices
from epibox.exceptions.exception_manager import (
    client_kill,
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


def main():

    devices = []
    # Setup MQTT client | read default configurations | initiate variables ===========================
    try:
        client = setup_client()

    except (MQTTConnectionError, ConnectionRefusedError, ValueError, TypeError) as e:
        config_debug.log(e)
        kill_case_1()

    try:
        opt, channels, sensors, service, save_raw = setup_config(client)

        (
            t_all,
            already_notified_pause,
            system_started,
            files_open,
        ) = setup_variables()  # raises no errors

        # Create folder with patient ID
        directory = create_folder(
            opt["initial_dir"], "{}".format(opt["patient_id"]), service
        )

    except MQTTConnectionError as e:
        kill_case_1()
    except (
        ConnectionRefusedError,
        ValueError,
        TypeError,
        OSError,
        StorageTimeout,
    ) as e:
        config_debug.log(e)
        kill_case_2(client)

    already_timed_out = False

    # Start loop to connect PyEpiBOX to acquisition devices =========================================
    try:
        devices = connect_devices(  # exceptions handled inside
            client, devices, opt, already_timed_out, files_open=False
        )

    except (
        DeviceConnectionTimeout,
        ValueError,
        TypeError,
        BITalinoParameterError,
    ) as e:
        config_debug.log(e)
        kill_case_3(client, devices, a_file)

    except MQTTConnectionError as e:
        config_debug.log(e)
        kill_case_4(devices)

    config_debug.log("Initial setup complete!")

    try:
        # Open acquisition file | get format and header info ============================================
        a_file, save_fmt, header = open_file(
            directory, devices, channels, sensors, opt["fs"], save_raw, service
        )
        files_open = True

    except OSError as e:
        config_debug.log(e)
        kill_case_3(client, devices)

    # Starting acquisition loop ===========================================================================
    # This loop runs continuously unless the user stops the acquisition on the EpiBOX App or at least one of
    # the devices disconnects
    while client.keepAlive:

        try:

            if client.newAnnot != None:
                # Write user annotation to file if one is received via MQTT ===============================
                config_debug.log(f"annot: {client.newAnnot}")
                write_annot_file(a_file.name, client.newAnnot)
                client.newAnnot = None

            if client.pauseAcq and not already_notified_pause:
                # Pause acquisition if command is received via MQTT ========================================
                devices = pause_devices(client, devices)
                already_notified_pause = True

            else:

                if already_notified_pause:
                    message_info = client.publish("rpi", str(["RECONNECTING"]))
                    if message_info.rc == 4:
                        raise MQTTConnectionError
                    already_notified_pause = False

                if not system_started:
                    # If the devices have not yet started acquiring or they are paused, start acquisition
                    sync_param = start_devices(
                        client, devices, opt["fs"], channels, header
                    )
                    system_started = True
                    already_timed_out = False

                # Read batch of samples from the acquisition devices and store on the active session's file
                _, t_disp, a_file, sync_param = run_system(
                    devices,
                    a_file,
                    sync_param,
                    directory,
                    channels,
                    sensors,
                    opt["fs"],
                    save_raw,
                    service,
                    save_fmt,
                    header,
                    client,
                )

                # Subsample batch of samples and send to the EpiBOX App for visualization purposes ==========
                t_display = process_data.decimate(t_disp, opt["fs"])
                t_all += t_display[0]
                json_data = json.dumps(["DATA", t_display, channels, sensors])
                message_info = client.publish("rpi", json_data)
                if message_info.rc == 4:
                    raise MQTTConnectionError

                already_timed_out = False

                # # Handle misconnection of the devices ============================================================
                # except Exception as e:
                #     devices, system_started = error_disconnect(
                #         client, devices, e, a_file
                #     )
                #     devices = connect_devices(
                #         client, devices, opt, already_timed_out, a_file
                #     )
                #     system_started = False
                #     a_file, save_fmt, header = open_file(
                #         directory,
                #         devices,
                #         channels,
                #         sensors,
                #         opt["fs"],
                #         save_raw,
                #         service,
                #     )

        except (
            DeviceNotIDLEError,
            BITalinoParameterError,
            FileNotFoundError,
            PermissionError,
            OSError,
            KeyboardInterrupt,
        ) as e:
            config_debug.log(e)
            kill_case_5(client, devices, a_file)

        except DeviceNotInAcquisitionError as e:
            config_debug.log(e)
            system_started = handle_case_6(client, devices, a_file, system_started)
            continue

        except MQTTConnectionError as e:
            config_debug.log(e)
            kill_case_7(client, devices, a_file)

    # =========================================================================================================
