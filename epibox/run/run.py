# built-in
import json

# local
from epibox.common.get_defaults import set_new_default_item
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
from epibox.mqtt_manager.message_handler import send_default


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
    except (TimeoutError, ConnectionAbortedError):
        config_debug.log("Wrong network - connect to PreEpiSeizures")
        kill_case_1()

    try:
        opt, channels, sensors, service, save_raw = setup_config(client)

        (
            t_all,
            already_notified_pause,
            system_started,
        ) = setup_variables()  # raises no errors

        # Create folder with patient ID
        directory = create_folder(
            opt["initial_dir"], "{}".format(opt["patient_id"]))

    except MQTTConnectionError as e:
        kill_case_1()
    except PermissionError:
        client.publish("rpi", str(["STORAGE ERROR"]))
        set_new_default_item(item_key="initial_dir", item="EpiBOX Core")
        send_default(client)
        kill_case_2(client)
    except (
        ConnectionRefusedError,
        ValueError,
        TypeError,
        OSError,
        StorageTimeout,
        PlatformNotSupportedError,
    ) as e:
        config_debug.log(e)
        kill_case_2(client)

    already_timed_out = False

    # Start loop to connect PyEpiBOX to acquisition devices =========================================
    if not client.keepAlive:
        kill_case_2()
    try:
        devices = connect_devices(  # exceptions handled inside
            client, devices, opt, already_timed_out,
        )

    except (
        DeviceConnectionTimeout,
        ValueError,
        TypeError,
        BITalinoParameterError,
    ) as e:
        config_debug.log(e)
        kill_case_3(client, devices)

    except MQTTConnectionError as e:
        config_debug.log(e)
        kill_case_4(devices)

    config_debug.log("Initial setup complete!")

    if not client.keepAlive:
        kill_case_4(devices)

    while client.keepAlive:

        try:

            if client.pauseAcq and not already_notified_pause:
                # Pause acquisition if command is received via MQTT ========================================

                # devices = pause_devices(client, devices)
                system_started = handle_case_6(devices, a_file, system_started)
                message_info = client.publish("rpi", str(["PAUSED"]))
                if message_info.rc == 4:
                    raise MQTTConnectionError
                already_notified_pause = True

            if not client.pauseAcq:

                if already_notified_pause:
                    message_info = client.publish("rpi", str(["RECONNECTING"]))
                    if message_info.rc == 4:
                        raise MQTTConnectionError
                    already_notified_pause = False

                if not system_started:
                    if not client.keepAlive:
                        kill_case_4()

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

                    if client.newAnnot != None:
                        # Write user annotation to file if one is received via MQTT ===============================
                        write_annot_file(a_file.name, client.newAnnot)
                        client.newAnnot = None

                    sync_param = start_devices(
                        client, devices, opt["fs"], channels, header
                    )
                    system_started = True
                    already_timed_out = False

                if client.newAnnot != None:
                    # Write user annotation to file if one is received via MQTT ===============================
                    write_annot_file(a_file.name, client.newAnnot)
                    client.newAnnot = None

                if not client.keepAlive:
                    kill_case_5(client, devices, a_file)

                # Read batch of samples from the acquisition devices and store on the active session's file
                _, t_disp, a_file, sync_param = run_system(
                    devices,
                    a_file,
                    sync_param,
                    channels,
                    sensors,
                    save_fmt,
                    header,
                    client,
                )

                # Subsample batch of samples and send to the EpiBOX App for visualization purposes ================
                t_display = process_data.decimate(t_disp, opt["fs"])
                t_all += t_display[0]
                json_data = json.dumps(["DATA", t_display, channels, sensors])
                message_info = client.publish("rpi", json_data)
                if message_info.rc == 4:
                    raise MQTTConnectionError

                already_timed_out = False

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
            message_info = client.publish("rpi", str(["RECONNECTING"]))
            if message_info.rc == 4:
                raise MQTTConnectionError
            system_started = handle_case_6(devices, a_file, system_started)
            continue

        except MQTTConnectionError as e:
            config_debug.log(e)
            kill_case_7(client, devices, a_file)

    # =========================================================================================================
