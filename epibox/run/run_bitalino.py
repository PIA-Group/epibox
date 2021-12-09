# built-in
import ast
import json
import time
from datetime import datetime

# local
from epibox.bit.manage_devices import pause_devices, reconnect_devices, start_devices
from epibox.exceptions.exception_manager import error_disconnect, error_kill, client_kill
from epibox.mqtt_manager.setup import setup_client, setup_config, setup_variables
from epibox.common.create_folder import create_folder
from epibox.common.open_file import open_file
from epibox.common.write_file import write_annot_file
from epibox.common.run_system import run_system
from epibox.common import process_data


# ****************************** MAIN SCRIPT ***********************************


def main(devices):

    try:

        client = setup_client()
        opt, channels, sensors, service, save_raw = setup_config()
        t_all, already_notified_pause, system_started, files_open = setup_variables()

        # Use/create the patient folder ===============================================================
        directory = create_folder(opt['initial_dir'], '{}'.format(opt['patient_id']), service)
        already_timed_out = False
    
    except Exception as e:
        error_kill(client, devices, msg='Failed initial setup', files_open=False)

    try:
        a_file, annot_file, drift_log_file, save_fmt, header = open_file(directory, devices, channels, sensors, opt['fs'], save_raw, service)
        files_open = True

    except Exception as e:
        error_kill(client, devices, msg='Failed to open the files', files_open=False)


    #*********** ****************************** ***********#
    if service != 'Mini':
        battery = {}
        for device in devices:
            state = device.state()
            if state['battery'] > 63:
                battery_volts = 2 * ((state['battery']*3.3) / (2**10-1))
            else:
                battery_volts = 2 * ((state['battery']*3.3) / (2**6-1))

            battery[device.macAddress] = battery_volts

        battery_json = json.dumps(['BATTERY', battery])
        client.publish('rpi', battery_json)

    # Starting Acquisition LOOP =========================================================================
    try:
        while client.keepAlive == True:

            if client.newAnnot != None:
                write_annot_file(annot_file, client.newAnnot)
                client.newAnnot = None

            if client.pauseAcq and not already_notified_pause:

                devices = pause_devices(client, devices)
                already_notified_pause = True

            elif not client.pauseAcq:

                if already_notified_pause:
                    client.publish('rpi', str(['RECONNECTING']))
                    already_notified_pause = False

                if not system_started:
                    try:
                        sync_param = start_devices(client, devices, opt['fs'], channels, header)
                        system_started = True
                        already_timed_out = False

                    except Exception as e:
                        print(e)
                        pass

                # if time.time() - start_time > 5*60:
                #     client.keepAlive = False

                try:
                    _, t_disp, a_file, drift_log_file, sync_param = run_system(devices, a_file, annot_file, drift_log_file, sync_param, directory, channels, sensors, opt['fs'], save_fmt, header)

                    t_display = process_data.decimate(t_disp, opt['fs'])
                    t_all += t_display[0]

                    json_data = json.dumps(['DATA', t_display, channels, sensors])
                    client.publish('rpi', json_data)

                    already_timed_out = False

                # Handle misconnection of the devices--------------------------------------------------------------------------------------------
                except Exception as e:
                    devices, system_started = error_disconnect(client, devices, e, a_file, annot_file, drift_log_file)

                    # Reconnect the devices
                    devices = reconnect_devices(client, opt, already_timed_out, a_file, annot_file, drift_log_file)

                    print('Devices in list: {}'.format([d.macAddress for d in devices]))

                    system_started = False
                    a_file, annot_file, drift_log_file, save_fmt, header = open_file(directory, devices, channels, sensors, opt['fs'], save_raw, service)

                    # Acquisition LOOP =========================================================================

                    for device in devices:
                        state = device.state()
                        if state['battery'] > 63:
                            battery_volts = 2 * ((state['battery']*3.3) / (2**10-1))
                        else:
                            battery_volts = 2 * ((state['battery']*3.3) / (2**6-1))

                        battery[device.macAddress] = battery_volts

                    battery_json = json.dumps(['BATTERY', battery])
                    client.publish('rpi', battery_json)

            else:
                pass

        client_kill(client, devices, 'You have stopped the acquisition', a_file, annot_file, drift_log_file, files_open)

    except KeyboardInterrupt:
        client_kill(client, devices, 'You have stopped the acquisition', a_file, annot_file, drift_log_file, files_open)


    # =========================================================================================================