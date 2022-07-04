# built-in
import json
from time import sleep

# local
from epibox.bit.manage_devices import pause_devices, connect_devices, start_devices
from epibox.exceptions.exception_manager import (
    error_disconnect,
    error_kill,
    client_kill,
)
from epibox.common.setup import setup_client, setup_config, setup_variables
from epibox.common.create_folder import create_folder
from epibox.common.open_file import open_file
from epibox.common.write_file import write_annot_file
from epibox.common.run_system import run_system
from epibox.common import process_data
from epibox import config_debug


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

    try:
        # Setup MQTT client | read default configurations | initiate variables ===========================
        client = setup_client()
        opt, channels, sensors, service, save_raw = setup_config(client)

        t_all, already_notified_pause, system_started, files_open = setup_variables()

        # Create folder with patient ID
        directory = create_folder(
            opt["initial_dir"], "{}".format(opt["patient_id"]), service
        )
        already_timed_out = False

        # Start loop to connect PyEpiBOX to acquisition devices =========================================
        devices = connect_devices(
            client, devices, opt, already_timed_out, files_open=False
        )

    except Exception as e:
        sleep(3)
        error_kill(
            client,
            devices,
            msg="Failed initial setup",
            files_open=False,
            devices_connected=False,
        )

    try:
        # Open acquisition file | get format and header info ============================================
        a_file, save_fmt, header = open_file(
            directory, devices, channels, sensors, opt["fs"], save_raw, service
        )
        files_open = True

    except Exception as e:
        error_kill(client, devices, msg="Failed to open the files", files_open=False)

    # Starting acquisition loop ===========================================================================
    # This loop runs continuously unless the user stops the acquisition on the EpiBOX App or at least one of
    # the devices disconnects
    try:
        while client.keepAlive == True:

            if client.newAnnot != None:
                # Write user annotation to file if one is received via MQTT ===============================
                config_debug.log(f"annot: {client.newAnnot}")
                write_annot_file(a_file.name, client.newAnnot)
                client.newAnnot = None

            config_debug.log("im here")
            if client.pauseAcq and not already_notified_pause:
                # Pause acquisition if command is received via MQTT ========================================
                devices = pause_devices(client, devices)
                already_notified_pause = True

            elif not client.pauseAcq:

                if already_notified_pause:
                    client.publish("rpi", str(["RECONNECTING"]))
                    already_notified_pause = False

                if not system_started:
                    # If the devices have not yet started acquiring or they are paused, start acquisition
                    try:
                        sync_param = start_devices(
                            client, devices, opt["fs"], channels, header
                        )
                        system_started = True
                        already_timed_out = False

                    except Exception as e:
                        config_debug.log(e)
                        pass

                try:
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
                    client.publish("rpi", json_data)

                    already_timed_out = False

                # Handle misconnection of the devices ============================================================
                except Exception as e:
                    devices, system_started = error_disconnect(
                        client, devices, e, a_file
                    )
                    devices = connect_devices(
                        client, devices, opt, already_timed_out, a_file
                    )
                    system_started = False
                    a_file, save_fmt, header = open_file(
                        directory,
                        devices,
                        channels,
                        sensors,
                        opt["fs"],
                        save_raw,
                        service,
                    )

            else:
                pass

        client_kill(
            client, devices, "You have stopped the acquisition", a_file, files_open
        )

    except KeyboardInterrupt:
        client_kill(
            client, devices, "You have stopped the acquisition", a_file, files_open
        )

    # =========================================================================================================
