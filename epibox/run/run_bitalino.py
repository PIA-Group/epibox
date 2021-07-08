# built-in
import ast
import json
import random
import time
import string
import subprocess

# third-party
import paho.mqtt.client as mqtt
import pexpect
from scipy import signal

# local
from epibox.startup import startup 
from epibox.bitalino import bitalino
from epibox.common.disconnect_system import disconnect_system
from epibox.common.create_folder import create_folder
from epibox.common.write_file import write_annot_file
from epibox.common.start_system import start_system

from write_file import * 
from run_system import *
from system_except import *




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

#****************************** MAIN SCRIPT ***********************************

def main():
    
    try:
    
        subprocess.call(['rfkill', 'block', 'bluetooth'])
        subprocess.call(['rfkill', 'unblock', 'bluetooth'])
        
        with open('/home/pi/Documents/epibox/args.json', 'r') as json_file:
            opt = json_file.read()
        opt = ast.literal_eval(opt)
        
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
        init = False
        client.publish('rpi', "['STARTING']")
        
        if not opt['channels']:
            channels = []
            for device in opt['devices_mac']:
                for i in range(1,7):
                    channels += [[device,str(i)]]
            sensors = ['-' for i in range(len(channels))]
        
        else:
            channels = []
            sensors = []
            for triplet in opt['channels']:
                channels += [triplet[:2]] 
                sensors += [triplet[2]]
        
        saveRaw = bool(opt['saveRaw'])
        service = opt['service']
        
        global write_annot
        global new_annot
        global pause_acq
        write_annot = False
        pause_acq = False
        already_notified_pause = False
        
        print('ID: {}'.format(opt['patient_id']))
        print('folder: {}'.format(opt['initial_dir']))
        print('fs: {}'.format(opt['fs']))
        print('saveRaw: {}'.format(saveRaw))
        print('channels: {}'.format(channels))
        print('devices: {}'.format(opt['devices_mac']))
        print('sensors: {}'.format(sensors))
        
    
        # pair BITalino devices if not already ===============================================================
        
        paired_devices = subprocess.run(['bluetoothctl', 'paired-devices'], capture_output=True, text=True).stdout.split('\n')
        paired = [mac in [p.split()[1] for p in paired_devices[:-1]] for mac in opt['devices_mac']]
        
        if not all(paired):
            client.publish('rpi', "['PAIRING']")
            
        already_timed_out = False
        init_connect_time = time.time()
        
        while not all(paired):
            
            if (time.time() - init_connect_time) > 120 or client.keepAlive == False:
                client.publish('rpi', "['STOPPED']")
                client.loop_stop()
                print('TIMEOUT')
                # Disconnect the system
                disconnect_system(devices, a_file, annot_file, drift_log_file)
                client.keepAlive = False
                pass
            
    
            if already_timed_out == True and time.time() - init_connect_time > 10:
                already_timed_out = False
                    
            for imac,mac in enumerate(opt['devices_mac']):
                
                if not paired[imac]:
                    print('Trying to pair {}'.format(mac))
                    try:
                        child = pexpect.spawn('bluetoothctl')
                        child.expect('#')
                        child.sendline('default agent')
                        child.expect('#')
                        child.sendline('scan on')
                        child.expect('#')
                        child.sendline('pair {}'.format(mac))
                        child.expect('Enter PIN code: ')
                        child.sendline('1234')
                        
                        print('Successfully paired {}!'.format(mac))
                        paired[imac] = True
                        
                    except Exception as e:
                        print(e)
                        if already_timed_out == False and time.time() - init_connect_time > 10:
                            timeout_json = json.dumps(['TIMEOUT', '{}'.format(mac)])
                            client.publish('rpi', timeout_json)
                            print('SENT TIMEOUT')
                            already_timed_out = True
                            init_connect_time = time.time()
    
    
        # Use/create the patient folder =============================================================== 
        directory = create_folder(opt['initial_dir'], '{}'.format(opt['patient_id']), service)
        already_timed_out = False   
    
        
        #*********** Connection to BITalino devices ***********#
        devices = []
        for i, mac in enumerate(opt['devices_mac']):
        
            init_connect_time = time.time()
            print('Searching for Module...' + mac)
            
            while client.keepAlive == True:
    
                if (time.time() - init_connect_time) > 120:
                    client.publish('rpi', "['STOPPED']")
                    client.loop_stop()
                    print('TIMEOUT')
                    # Disconnect the system
                    disconnect_system(devices, a_file, annot_file, drift_log_file)
                    client.keepAlive == False
                    pass
                
                try:
                    if already_timed_out == True and time.time() - init_connect_time > 10:
                        already_timed_out = False
                    
                    bt_devices = subprocess.getoutput('hcitool con')
                    print(bt_devices)
                    print(devices)
                    if mac not in bt_devices.split():
                        device = BITalino(mac, timeout=5)
                        print('Device {} connected!'.format(mac))
                        devices.append(device)
                    elif mac not in [d.macAddress for d in devices]:
                        print('Already connected, but not in devices'.format(mac))
                        device = BITalino(mac, timeout=5)
                        devices.append(device)
                        print('Device {} connected!'.format(mac))
                    else:
                        print('Already connected | devices: {}'.format(devices))
                        
                    break
    
                except Exception as e:
                    print(e)
                    print('Failed at connecting to BITalino')
                    if already_timed_out == False and time.time() - init_connect_time > 10:
                        timeout_json = json.dumps(['TIMEOUT', '{}'.format(mac)])
                        client.publish('rpi', timeout_json)
                        print('SENT TIMEOUT')
                        already_timed_out = True
                        init_connect_time = time.time()
            
        
        print('Devices in list: {}'.format([d.macAddress for d in devices]))
        
        try:
            a_file, annot_file, drift_log_file, save_fmt, header = open_file(directory, devices, channels, sensors, opt['fs'], saveRaw)
        
        except Exception as e:
            print(e)
            client.publish('rpi', "['ERROR']")
            client.loop_stop()
            
            # Disconnect the system
            # disconnect_system(devices, a_file, annot_file, drift_log_file)
            print('Acquisition could not start. Turn devices off and on. Then restart.')
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
                    
                    for i,device in enumerate(devices):
                        try:
                            device.stop()
                        except Exception as e:
                            print(e)
                            continue
                     
                    client.publish('rpi', "['PAUSED']")
                    already_notified_pause = True
                
                    
                    
                elif not pause_acq:
                    
                    already_notified_pause = False
                    
                    try:

                        
                        _, t_disp, sync_param = start_system(devices, a_file, drift_log_file, opt['fs'], channels, sensors, save_fmt, header)
                        client.publish('rpi', "['ACQUISITION ON']")
    
                        # if phisiological signal downsample to 100Hz, if acc decimate 10Hz
                        t_display = []
                        if opt['fs'] == 1000:# changes sampling rate to 100 (if larger)
                            for i in range(t_disp.shape[1]):
                                t_display += [signal.decimate(t_disp[:,i], 10).tolist()]
                        else:
                            for i in range(t_disp.shape[1]):
                                t_display += [t_disp[:,i].tolist()]  
                                    
                        json_data = json.dumps(['DATA', t_display, channels, sensors])
                        client.publish('rpi', json_data)
                        already_timed_out = False
                        
                    except Exception as e:
                        #sync_param['mode'] = 0
                        print(e)
                        pass
                    
                    # Acquisition LOOP =========================================================================
                    # try to read from the device--------------------------------------------------------------------------------------------------
                    
                    if write_annot:
                        print('SAVED ANNOT')
                        write_annot_file(annot_file, new_annot)
                        write_annot = False
                                
                
                    try:
                        _, t_disp, a_file, drift_log_file, sync_param = run_system(devices, a_file, annot_file, drift_log_file, sync_param, directory, channels, sensors, opt['fs'], save_fmt, header)
                        
                        t_display = []
                        if opt['fs'] == 1000:# changes sampling rate to 100 (if larger)
                            for i in range(t_disp.shape[1]):
                                t_display += [signal.decimate(t_disp[:,i], 10).tolist()]
                        else:
                            for i in range(t_disp.shape[1]):
                                t_display += [t_disp[:,i].tolist()]  
                                    
                        json_data = json.dumps(['DATA', t_display, channels, sensors])
                        client.publish('rpi', json_data)
                        already_timed_out = False
                        
                    # Handle misconnection of the devices--------------------------------------------------------------------------------------------
                    except Exception as e:
                        print('')
                        print('')
                        print('The system has stopped running because ' + str(e) + '! Please check Modules!')
                        print('Trying to Reconnect....')
                        client.publish('rpi', "['RECONNECTING']")
                        
                        # Disconnect the system
                        disconnect_system(devices, a_file, annot_file, drift_log_file)
                        sync_param['mode'] = 0
                        
                        # Reconnect the devices
                        try:
                            #*********** Connection to BITalino devices ***********#
                            subprocess.call(['rfkill', 'block', 'bluetooth'])
                            subprocess.call(['rfkill', 'unblock', 'bluetooth'])
                            devices = []
                            for i, mac in enumerate(opt['devices_mac']):
                            
                                init_connect_time = time.time()
                                print('Searching for Module...' + mac)
                                
                                while client.keepAlive == True:
    
                                    if (time.time() - init_connect_time) > 120:
                                        client.publish('rpi', "['STOPPED']")
                                        client.loop_stop()
                                        print('TIMEOUT')
                                        
                                        # Disconnect the system
                                        disconnect_system(devices, a_file, annot_file, drift_log_file)
                                        client.keepAlive == False
                                        pass
                                    
                                    try:
                                        if already_timed_out == True and time.time() - init_connect_time > 10:
                                            already_timed_out = False
                                        
                                        bt_devices = subprocess.getoutput('hcitool con')
                                        print(bt_devices)
                                        print(devices)
                                        if mac not in bt_devices.split():
                                            device = BITalino(mac, timeout=5)
                                            print('Device {} connected!'.format(mac))
                                            devices.append(device)
                                        elif mac not in [d.macAddress for d in devices]:
                                            print('Already connected, but not in devices'.format(mac))
                                            device = BITalino(mac, timeout=5)
                                            devices.append(device)
                                            print('Device {} connected!'.format(mac))
                                        else:
                                            print('Already connected | devices: {}'.format(devices))
                                            
                                        break
    
                                    except Exception as e:
                                        print(e)
                                        print('Failed at connecting to BITalino')
                                        sync_param['mode'] = 0
                                        if already_timed_out == False and time.time() - init_connect_time > 10:
                                            timeout_json = json.dumps(['TIMEOUT', '{}'.format(mac)])
                                            client.publish('rpi', timeout_json)
                                            print('SENT TIMEOUT')
                                            already_timed_out = True
                                            init_connect_time = time.time()
                            
                            print('Devices in list: {}'.format([d.macAddress for d in devices]))
                            
                            a_file, annot_file, drift_log_file, save_fmt, header = open_file(directory, devices, channels, sensors, opt['fs'], saveRaw)
                        
                            # Acquisition LOOP =========================================================================
                            
                            if service != 'Mini':
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
                            print('The system is running again ...')
                            client.publish('rpi', "['ACQUISITION ON']")
                            
                            t_display = []
                            if opt['fs'] == 1000:# changes sampling rate to 100 (if larger)
                                for i in range(t_disp.shape[1]):
                                    t_display += [signal.decimate(t_disp[:,i], n).tolist()]
                            else:
                                for i in range(t_disp.shape[1]):
                                    t_display += [t_disp[:,i].tolist()]
                                        
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
            client.publish('rpi', "['STOPPED']")
            client.loop_stop()
            
            # Disconnect the system
            disconnect_system(devices, a_file, annot_file, drift_log_file)
            client.keepAlive == False
            pass
    
            
        	# -----------------------------------------------------------------------------------------------------------------------------------------
        
        print('')
        client.publish('rpi', "['STOPPED']")
        client.loop_stop()
        
        # Disconnect the system
        disconnect_system(devices, a_file, annot_file, drift_log_file)
        print('You have stopped the acquistion. Saving all the files ...')
        time.sleep(3)
        pid = subprocess.run(['sudo', 'pgrep', 'python'], capture_output=True, text=True).stdout.split('\n')[:-1]
        for p in pid:
            subprocess.run(['kill', '-9', p])
        
    except Exception as e:
        print(e)
        client.publish('rpi', "['STOPPED']")
        client.loop_stop()
        
        # Disconnect the system
        disconnect_system(devices, a_file, annot_file, drift_log_file)
        print('You have stopped the acquistion. Saving all the files ...')
        time.sleep(3)
        pid = subprocess.run(['sudo', 'pgrep', 'python'], capture_output=True, text=True).stdout.split('\n')[:-1]
        for p in pid:
            subprocess.run(['kill', '-9', p])
    
    # =========================================================================================================

if __name__ == '__main__':

    main()