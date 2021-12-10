# built-in
import ast
import os
import subprocess
import json
import shutil
import pwd

def on_message(client, userdata, message):

    message = str(message.payload.decode("utf-8"))
    message = ast.literal_eval(message)

    if message[0] == 'RESTART':
        client.loop_stop()
        #client.keepAlive = False

    elif message[0] == 'INTERRUPT':
        client.keepAlive = False

    elif message[0] == 'PAUSE ACQ':
        print('PAUSING ACQUISITION')
        client.pauseAcq = True

    elif message[0] == 'RESUME ACQ':
        print('RESUMING ACQUISITION')
        client.pauseAcq = False

    elif message[0] == 'ANNOTATION':
        print('RECEIVED ANNOT {} ----------------------'.format(message[1]))
        client.newAnnot = message[1]

    elif message[0] == 'TURN OFF':
        print('TURNING OFF RPI')
        client.publish(topic='rpi', payload=str(['TURNED OFF']))

    elif message[0] == 'TURNED OFF':
        subprocess.run(['sudo', 'shutdown', '-h', 'now'])

    elif message == ['Send default']:

        username = pwd.getpwuid(os.getuid())[0]

        ######## Default MAC addresses ########

        try:
            with open('/home/{}/Documents/epibox/args.json'.format(username), 'r') as json_file:
                defaults = json_file.read()
                defaults = ast.literal_eval(defaults)
                listMAC = defaults['devices_mac']
        except Exception as e:
            listMAC = {"MAC1": "", "MAC2": ""}

        listMAC2 = json.dumps(['DEFAULT MAC','{}'.format(list(listMAC.values())[0]),'{}'.format(list(listMAC.values())[1])])
        
        client.publish(topic='rpi', qos=2, payload=listMAC2)

        ######## Available drives ########

        listDrives = ['DRIVES']
        drives = os.listdir('/media/{}/'.format(username))

        for drive in drives:
            total, _ , free = shutil.disk_usage('/media/{}/{}'.format(username, drive))
            listDrives += ['{} ({:.1f}% livre)'.format(drive, (free/total)*100)]

        total, _ , free = shutil.disk_usage('/')

        listDrives += ['EpiBOX Core ({:.1f}% livre)'.format((free/total)*100)]

        client.publish(topic='rpi', qos=2, payload="{}".format(listDrives))

        
        ######## Default configurations ########

        try:
            with open('/home/{}/Documents/epibox/args.json'.format(username), 'r') as json_file:
                defaults = json_file.read()
                defaults = ast.literal_eval(defaults)
        except Exception as e:
            defaults = {'initial_dir': 'EpiBOX Core', 'fs': 1000, 'channels': [], 'save_raw': 'true', 'service': 'Bitalino'}

        config = json.dumps(['DEFAULT CONFIG', defaults])
        client.publish(topic='rpi', qos=2, payload=config)


    ######## New default configuration ########

    elif message[0] == 'NEW CONFIG DEFAULT':
        username = pwd.getpwuid(os.getuid())[0]

        try:
            with open('/home/{}/Documents/epibox/args.json'.format(username), 'r') as json_file:
                defaults = json_file.read()
                defaults = ast.literal_eval(defaults)
        except Exception as e:
            defaults = {'initial_dir': 'EpiBOX Core', 'fs': 1000, 'channels': [], 'save_raw': 'true', 'service': 'Bitalino'}

        for key in message[1].keys():
            defaults[key] = message[1][key]
        
        with open('/home/{}/Documents/epibox/args.json'.format(username), 'w+') as json_file:
            json.dump(defaults, json_file)

        
    elif message[0] == 'NEW MAC':
        username = pwd.getpwuid(os.getuid())[0]

        try:
            with open('/home/{}/Documents/epibox/args.json'.format(username), 'r') as json_file:
                defaults = json_file.read()
                defaults = ast.literal_eval(defaults)
        except Exception as e:
            defaults = {'initial_dir': 'EpiBOX Core', 'fs': 1000, 'channels': [], 'save_raw': 'true', 'service': 'Bitalino'}

        defaults['devices_mac'] = message[1]

        with open('/home/{}/Documents/epibox/args.json'.format(username), 'w+') as json_file:
            json.dump(defaults, json_file)