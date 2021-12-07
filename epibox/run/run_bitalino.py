# built-in
import ast
import json
import random
import time
import string
import subprocess
from datetime import datetime
import pwd
import os

# third-party
import numpy as np
import paho.mqtt.client as mqtt
from epibox.common.emg_detection import detect_event

# local
from epibox.startup import startup
from epibox.common.disconnect_system import disconnect_system
from epibox.common.create_folder import create_folder
from epibox.common.open_file import open_file
from epibox.common.write_file import write_annot_file
from epibox.common.start_system import start_system
from epibox.common.run_system import run_system
from epibox.common.connect_device import connect_device
from epibox.common import process_data


def random_str(length):
    letters = string.ascii_letters
    return ''.join(random.choice(letters) for i in range(length))


def on_message(client, userdata, message):

    message = str(message.payload.decode("utf-8"))
    message = ast.literal_eval(message)
    #print("message received: ", message)

    if message[0] == 'RESTART':
        client.loop_stop()
        startup.main()

    elif message[0] == 'INTERRUPT':

        client.keepAlive = False

    elif message[0] == 'PAUSE ACQ':
        print('PAUSING ACQUISITION')
        global pause_acq
        pause_acq = True

    elif message[0] == 'RESUME ACQ':
        print('RESUMING ACQUISITION')
        pause_acq = False

    elif message[0] == 'ANNOTATION':
        print('RECEIVED ANNOT {} ----------------------'.format(message[1]))
        global new_annot
        global write_annot
        new_annot = message[1]
        write_annot = True

    elif message[0] == 'TURN OFF':
        print('TURNING OFF RPI')

        client.publish(topic='rpi', payload=str(['TURNED OFF']))

    elif message[0] == 'TURNED OFF':
        subprocess.run(['sudo', 'shutdown', '-h', 'now'])

# ****************************** MAIN SCRIPT ***********************************


def main(devices):

    try:

        client_name = random_str(6)
        print('Client name (acquisition):', client_name)
        host_name = '192.168.0.10'
        topic = 'rpi'

        client = mqtt.Client(client_name)
        setattr(client, 'keepAlive', True)
        client.username_pw_set(username='preepiseizures', password='preepiseizures')
        client.connect(host_name)
        client.subscribe(topic)
        client.on_message = on_message
        client.loop_start()
        print('Successfully subcribed to topic', topic)

        client.publish('rpi', str(['STARTING']))

        username = pwd.getpwuid(os.getuid())[0]
        with open('/home/{}/Documents/epibox/args.json'.format(username), 'r') as json_file:
            opt = json_file.read()

        print(opt)
        opt = ast.literal_eval(opt)

        if not opt['channels']:
            channels = []
            for device in opt['devices_mac']:
                for i in range(1, 7):
                    channels += [[device, str(i), 0]]
            sensors = ['-' for i in range(len(channels))]

        else:
            channels = []
            sensors = []
            for triplet in opt['channels']:
                channels += [triplet[:2] + [0]] # added the 0 here
                sensors += [triplet[2]]

        save_raw = bool(opt['save_raw'])
        service = opt['service']

        global write_annot
        global new_annot
        global pause_acq

        write_annot = False
        pause_acq = False
        already_notified_pause = False
        system_started = False

        t_buffer = [[]] * len(channels)
        strength_flag = [0] * len(channels)

        print('ID: {}'.format(opt['patient_id']))
        print('folder: {}'.format(opt['initial_dir']))
        print('fs: {}'.format(opt['fs']))
        print('save_raw: {}'.format(save_raw))
        print('channels: {}'.format(channels))
        print('devices: {}'.format(opt['devices_mac']))
        print('sensors: {}'.format(sensors))
        print('service: {}'.format(service))
        print('Devices in list: {}'.format([d.macAddress for d in devices]))

        t_all = []

        # Use/create the patient folder ===============================================================
        directory = create_folder(opt['initial_dir'], '{}'.format(opt['patient_id']), service)
        already_timed_out = False

        try:
            a_file, annot_file, drift_log_file, save_fmt, header = open_file(directory, devices, channels, sensors, opt['fs'], save_raw, service)

        except Exception as e:
            print(e)

            client.publish('rpi', str(['ERROR']))

            client.loop_stop()

            # Disconnect the system
            print('Could not open the files')
            disconnect_system(devices, service, files_open=False)

            system_started = False
            pid = subprocess.run(['sudo', 'pgrep', 'python'], capture_output=True, text=True).stdout.split('\n')[:-1]
            for p in pid:
                subprocess.run(['kill', '-9', p])


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

                if pause_acq and not already_notified_pause:

                    sync_param['mode'] = 0

                    for i, device in enumerate(devices):
                        try:
                            device.stop()
                        except Exception as e:
                            print(e)
                            continue

                    client.publish('rpi', str(['PAUSED']))
                    already_notified_pause = True

                elif not pause_acq:

                    if (already_notified_pause):
                        print('paused and restarting')

                        client.publish('rpi', str(['RECONNECTING']))


                    already_notified_pause = False

                    if not system_started:

                        start_time = time.time()

                        try:

                            _, t_disp, sync_param = start_system(devices, a_file, drift_log_file, opt['fs'], channels, sensors, save_fmt, header)
                            system_started = True


                            client.publish('rpi', str(['ACQUISITION ON']))

                            t_display = process_data.decimate(t_disp, opt['fs'])
                            print('t_display: {}'.format(t_display))


                            json_data = json.dumps(['DATA', t_display, channels, sensors])

                            client.publish('rpi', json_data)

                            already_timed_out = False


                        except Exception as e:
                            print(e)
                            pass

                    # Acquisition LOOP =========================================================================
                    # try to read from the device--------------------------------------------------------------------------------------------------

                    # if time.time() - start_time > 5*60:
                    #     client.keepAlive = False

                    if write_annot:
                        print('SAVED ANNOT')
                        write_annot_file(annot_file, new_annot)
                        write_annot = False

                    try:
                        _, t_disp, a_file, drift_log_file, sync_param = run_system(devices, a_file, annot_file, drift_log_file, sync_param, directory, channels, sensors, opt['fs'], save_fmt, header)

                        t_display = process_data.decimate(t_disp, opt['fs'])
                        t_all += t_display[0]

                        nbuffer = 30
                        if len(t_buffer[0]) >= nbuffer:
                            t_buffer = [tb_aux[-(nbuffer-len(t_display[0])):] + t_display[tb] for tb,tb_aux in enumerate(t_buffer)]
                            strength_flag = detect_event(t_buffer, sensors)
                        
                        else:
                            t_buffer = [tb_aux + t_display[tb] for tb,tb_aux in enumerate(t_buffer)]
                        
                        channels = [chn[:2]+[strength_flag[c]] for c, chn in enumerate(channels)]
                        print(channels)

                        json_data = json.dumps(['DATA', t_display, channels, sensors])
                        client.publish('rpi', json_data)

                        already_timed_out = False

                    # Handle misconnection of the devices--------------------------------------------------------------------------------------------
                    except Exception as e:
                        print('')
                        print('')
                        print('The system has stopped running because ' + str(e) + '! Please check Modules!')
                        print('Trying to Reconnect....')

                        client.publish('rpi', str(['RECONNECTING']))

                        # Disconnect the system
                        now = datetime.now()
                        save_time = now.strftime("%H-%M-%S").rstrip('0')
                        write_annot_file(annot_file, ['disconnection', save_time])

                        disconnect_system(devices, service, a_file, annot_file, drift_log_file)
                        devices = []
                        system_started = False
                        sync_param['mode'] = 0

                        print('gonna try to reconnect now')

                        # Reconnect the devices
                        try:
                            #*********** Connection to BITalino devices ***********#
                            for i, mac in enumerate(opt['devices_mac']):

                                init_connect_time = time.time()
                                print('Searching for Module...' + mac)

                                while client.keepAlive == True:

                                    if (time.time() - init_connect_time) > 120:

                                        client.publish('rpi', str(['STOPPED']))

                                        client.loop_stop()
                                        print('TIMEOUT')

                                        # Disconnect the system
                                        disconnect_system(devices, service, a_file, annot_file, drift_log_file)
                                        client.keepAlive == False
                                        pass

                                    try:
                                        if already_timed_out == True and time.time() - init_connect_time > 10:
                                            already_timed_out = False

                                        connected = False
                                        time.sleep(5)
                                        connected, devices = connect_device(mac, client, devices, service)

                                        if connected and mac in [d.macAddress for d in devices]:
                                            now = datetime.now()
                                            save_time = now.strftime("%H-%M-%S").rstrip('0')
                                            write_annot_file(annot_file, ['reconnection', save_time])
                                            break

                                    except Exception as e:
                                        print(e)
                                        print('HERE Failed at connecting to BITalino')
                                        sync_param['mode'] = 0
                                        if already_timed_out == False and time.time() - init_connect_time > 10:

                                            timeout_json = json.dumps(['TIMEOUT', '{}'.format(mac)])
                                            client.publish('rpi', timeout_json)

                                            already_timed_out = True
                                            init_connect_time = time.time()

                            print('Devices in list: {}'.format([d.macAddress for d in devices]))

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

                            _, t_disp, sync_param = start_system(devices, a_file, drift_log_file, opt['fs'], channels, sensors, save_fmt, header)
                            system_started = True
                            print('The system is running again ...')

                            client.publish('rpi', str(['ACQUISITION ON']))

                            t_display = process_data.decimate(t_disp, opt['fs'])

                            json_data = json.dumps(['DATA', t_display, channels, sensors])

                            client.publish('rpi', json_data)

                            already_timed_out = False

                        except:
                            pass

                else:
                    pass

        except KeyboardInterrupt:
            print('')
            print('You have stopped the acquistion. Saving all the files ...')

            client.publish('rpi', str(['STOPPED']))

            client.loop_stop()

            # Disconnect the system
            disconnect_system(devices, service, a_file, annot_file, drift_log_file)
            client.keepAlive == False
            pass


            # -----------------------------------------------------------------------------------------------------------------------------------------

        client.publish('rpi', str(['STOPPED']))

        client.loop_stop()

        # Disconnect the system
        disconnect_system(devices, service, a_file, annot_file, drift_log_file)
        system_started = False
        print('You have stopped the acquistion. Saving all the files ...')
        time.sleep(3)
        pid = subprocess.run(['sudo', 'pgrep', 'python'], capture_output=True, text=True).stdout.split('\n')[:-1]
        for p in pid:
            subprocess.run(['kill', '-9', p])

    except Exception as e:
        print(e)
        client.publish('rpi', str(['STOPPED']))

        client.loop_stop()


        # Disconnect the system
        disconnect_system(devices, service, a_file, annot_file, drift_log_file)
        system_started = False
        print('You have stopped the acquistion. Saving all the files ...')
        time.sleep(3)
        pid = subprocess.run(['sudo', 'pgrep', 'python'], capture_output=True, text=True).stdout.split('\n')[:-1]
        for p in pid:
            subprocess.run(['kill', '-9', p])

    # =========================================================================================================