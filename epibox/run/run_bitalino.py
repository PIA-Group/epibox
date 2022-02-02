# built-in
import json

# local
from epibox.bit.manage_devices import pause_devices, connect_devices, start_devices
from epibox.exceptions.exception_manager import error_disconnect, error_kill, client_kill
from epibox.common.setup import setup_client, setup_config, setup_variables
from epibox.common.create_folder import create_folder
from epibox.common.open_file import open_file
from epibox.common.write_file import write_annot_file
from epibox.common.run_system import run_system
from epibox.common import process_data
from epibox.bit.get_battery import get_battery


# ****************************** MAIN SCRIPT ***********************************


def main():

    devices = []

    try:
        client = setup_client()
        opt, channels, sensors, service, save_raw = setup_config(client)
        t_all, already_notified_pause, system_started, files_open = setup_variables()

        # Use/create the patient folder ===============================================================
        directory = create_folder(opt['initial_dir'], '{}'.format(opt['patient_id']), service)
        already_timed_out = False

        devices = connect_devices(client, devices, opt, already_timed_out, files_open=False)
    
    except Exception as e:
        error_kill(client, devices, msg='Failed initial setup', files_open=False, devices_connected=False)

    try:
        a_file, save_fmt, header = open_file(directory, devices, channels, sensors, opt['fs'], save_raw, service)
        files_open = True

    except Exception as e:
        error_kill(client, devices, msg='Failed to open the files', files_open=False)


    # Starting Acquisition LOOP =========================================================================
    try:
        while client.keepAlive == True:

            if client.newAnnot != None:
                print(f'annot: {client.newAnnot}')
                write_annot_file(a_file.name, client.newAnnot)
                client.newAnnot = None

            if client.pauseAcq and not already_notified_pause:

                devices = pause_devices(client, devices)
                already_notified_pause = True

            elif not client.pauseAcq:

                if already_notified_pause:
                    client.publish('rpi', str(['RECONNECTING']))
                    already_notified_pause = False

                if not system_started:

                    # get_battery(client, devices, service)
                    
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
                    _, t_disp, a_file, sync_param = run_system(devices, a_file, sync_param, directory, channels, sensors, opt['fs'], save_raw, service, save_fmt, header, client)

                    t_display = process_data.decimate(t_disp, opt['fs'])
                    t_all += t_display[0]

                    json_data = json.dumps(['DATA', t_display, channels, sensors])
                    client.publish('rpi', json_data)

                    already_timed_out = False

                # Handle misconnection of the devices--------------------------------------------------------------------------------------------
                except Exception as e:
                    
                    devices, system_started = error_disconnect(client, devices, e, a_file)

                    # Reconnect the devices
                    devices = connect_devices(client, devices, opt, already_timed_out, a_file)

                    system_started = False
                    a_file, save_fmt, header = open_file(directory, devices, channels, sensors, opt['fs'], save_raw, service)

            else:
                pass

        client_kill(client, devices, 'You have stopped the acquisition', a_file, files_open)

    except KeyboardInterrupt:
        client_kill(client, devices, 'You have stopped the acquisition', a_file, files_open)


    # =========================================================================================================