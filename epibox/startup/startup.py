# built-in
import ast
import string 
import random
import os
import subprocess
import json
import shutil

# third-party
import paho.mqtt.client as mqtt

# local
from epibox.common.connect_device import connect_device
from epibox.run import run_bitalino
from epibox.run import run_scientisst

def random_str(length):

    letters = string.ascii_letters

    return ''.join(random.choice(letters) for i in range(length))

def on_message(client, userdata, message):

    global sys_args
    global devices

    message = str(message.payload.decode("utf-8"))
    print(message)
    message = ast.literal_eval(message)

    if message == ['Send default']:

        ######## Default MAC addresses ########

        with open('/home/pi/Documents/epibox/listMAC.json', 'r') as json_file:
            listMAC = json_file.read()

        listMAC = ast.literal_eval(listMAC)
        listMAC2 = json.dumps(['DEFAULT MAC','{}'.format(list(listMAC.values())[0]),'{}'.format(list(listMAC.values())[1])])

        client.publish(topic='rpi', qos=2, payload=listMAC2)

        ######## Available drives ########

        listDrives = ['DRIVES']
        drives = os.listdir('/media/pi')

        for drive in drives:
            total, _ , free = shutil.disk_usage('/media/pi/{}'.format(drive))
            listDrives += ['{} ({:.1f}% livre)'.format(drive, (free/total)*100)]

        total, _ , free = shutil.disk_usage('/')
        listDrives += ['RPi ({:.1f}% livre)'.format((free/total)*100)]

        client.publish(topic='rpi', qos=2, payload="{}".format(listDrives))

        
        ######## Default configurations ########

        with open('/home/pi/Documents/epibox/config_default.json', 'r') as json_file:
            defaults = json_file.read()

        defaults = ast.literal_eval(defaults)
        config = json.dumps(['DEFAULT CONFIG', defaults])

        client.publish(topic='rpi', qos=2, payload=config)


    ######## New default configuration ########

    elif message[0] == 'NEW CONFIG DEFAULT':
        config = message[1]
        defaults = {'initial_dir': config[0], 'fs': config[1], 'channels': config[2], 'saveRaw': config[3]}

        with open('/home/pi/Documents/epibox/config_default.json', 'w') as json_file:
            json.dump(defaults, json_file)

            

    elif message[0] == 'NEW MAC':
        listMAC = message[1]

        with open('/home/pi/Documents/epibox/listMAC.json', 'w') as json_file:
            json.dump(listMAC, json_file)


    ######## Update time ########

    elif message[0] == 'TIME':
        subprocess.run(["sudo", "date", "-s", message[1]])
        subprocess.run(["sudo", "date"], capture_output=True, text=True)


    ##### Connect devices #####

    elif message[0] == 'CONNECT':
        mac = message[1]
        service = message[2]

        if mac != ' ' and mac != '' and message[1] not in sys_args['devices_mac']:
            sys_args['devices_mac'] += [mac]

        _, devices = connect_device(mac, client, devices, service)


    ####### Set configurations ########

    elif message[0] == 'FOLDER':

        if message[1] == 'RPi':
            folder = '/home/pi/Documents/epibox/acquisitions'

        else: 
            folder = '/media/pi/' + message[1] + '/acquisitions'

        sys_args['initial_dir'] = folder

    
    elif message[0] == 'FS':
        fs = message[1]
        sys_args['fs'] = fs

    
    elif message[0] == 'SAVE RAW':
        saveRaw = message[1]
        sys_args['saveRaw'] = saveRaw


    elif message[0] == 'EPI SERVICE':
        epi_service = message[1]
        sys_args['service'] = epi_service


    elif message[0] == 'CHANNELS':
        channels = message[1]
        sys_args['channels'] = channels

        client.publish(topic='rpi', qos=2, payload=str(['RECEIVED CONFIG']))

    
    elif message[0] == 'ID':
        patient_id = message[1]
        sys_args['patient_id'] = patient_id


    ####### System actions #######

    elif message[0] == 'TURN OFF':
        print('TURNING OFF RPI')
        client.publish(topic='rpi', qos=2, payload=str(['TURNED OFF']))

    elif message[0] == 'TURNED OFF':
        subprocess.run(['sudo', 'shutdown', '-h', 'now'])


    elif message[0] == 'START':
        client.keepAlive = False

 
def main():

    global devices
    devices = []

    global sys_args
    sys_args = {'initial_dir': None, 'fs': None, 'channels': None, 'saveRaw': None, 'devices_mac': [], 'patient_id': None, 'service': None}

    client_name = random_str(6)
    print('Client name (startup):', client_name)
    host_name = '192.168.0.10'
    topic = 'rpi'

    client = mqtt.Client(client_name)
    setattr(client, 'keepAlive', True)

    client.username_pw_set(username='preepiseizures', password='preepiseizures')
    try:
        client.connect(host_name)
        client.subscribe(topic, 1)
        client.on_message = on_message
        client.loop_start()

        print('Successfully subcribed to topic', topic)

        while client.keepAlive == True:
            continue

        else:
            client.loop_stop()

            with open('/home/pi/Documents/epibox/args.json', 'w') as json_file:
                json.dump(sys_args, json_file)

            if sys_args['service'] == 'Bitalino' or sys_args['service'] == 'Mini':
                run_bitalino.main(devices)
            else:
                run_scientisst.main(devices)

    except Exception as e:
        print(e)
    
if __name__ == '__main__':

    main()

