# built-in
from http import client
import pwd
import os
import ast

# third-party
import paho.mqtt.client as mqtt

# local
from epibox.mqtt_manager.message_handler import on_message, send_default
from epibox.mqtt_manager.utils import random_str

def setup_client():
    client_name = random_str(6)
    print('Client name (acquisition):', client_name)
    host_name = '192.168.0.10'
    topic = 'rpi'

    client = mqtt.Client(client_name)

    setattr(client, 'keepAlive', True)
    setattr(client, 'pauseAcq', False)
    setattr(client, 'newAnnot', None)

    client.username_pw_set(username='preepiseizures', password='preepiseizures')
    client.connect(host_name)
    client.subscribe(topic)
    client.on_message = on_message
    client.loop_start()
    print('Successfully subcribed to topic', topic)

    client.publish('rpi', str(['STARTING']))

    return client


def setup_config(client):
    
    username = pwd.getpwuid(os.getuid())[0]

    send_default(client, username)

    with open('/home/{}/Documents/epibox/args.json'.format(username), 'r') as json_file:
        opt = json_file.read()
        opt = ast.literal_eval(opt)

    try: 
        opt['devices_mac'].values()
    except Exception as e:
        opt['devices_mac'] = {'MAC1': '12:34:56:78:91:10','MAC2': ''}

    if not opt['channels']:
        channels = []
        for device in opt['devices_mac'].values():
            for i in range(1, 7):
                channels += [[device, str(i)]]
        sensors = ['-' for i in range(len(channels))]

    else:
        channels = []
        sensors = []
        try:
            for triplet in opt['channels']:
                triplet[0] = opt['devices_mac'][triplet[0]] # replace MAC ID for corresponding MAC
                channels += [triplet[:2]]
                sensors += [triplet[2]]
        except Exception as e:
            print(e)
            for tt,triplet in enumerate(opt['channels']):
                if tt < 7:
                    triplet[0] = opt['devices_mac']['MAC1'] 
                else: 
                    triplet[0] = opt['devices_mac']['MAC2']
                channels += [triplet[:2]]
                sensors += [triplet[2]]


    if 'save_raw' in opt.keys(): save_raw = bool(opt['save_raw'])
    else: save_raw = bool(opt['saveRaw'])

    service = opt['service']
    opt['devices_mac'] = [m for m in opt['devices_mac'].values() if m != '']

    if opt['initial_dir'] == 'EpiBOX Core':
        opt['initial_dir'] = '/home/{}/Documents/epibox/acquisitions'.format(username)
    else: 
        if os.path.isdir('/media/{}/'.format(username) + opt['initial_dir']):
            opt['initial_dir'] = '/media/{}/'.format(username) + opt['initial_dir'] + '/acquisitions'
        else:
            opt['initial_dir'] = '/home/{}/Documents/epibox/acquisitions'.format(username)

    print('ID: {}'.format(opt['patient_id']))
    print('folder: {}'.format(opt['initial_dir']))
    print('fs: {}'.format(opt['fs']))
    print('save_raw: {}'.format(save_raw))
    print('channels: {}'.format(channels))
    print('devices: {}'.format(opt['devices_mac']))
    print('sensors: {}'.format(sensors))
    print('service: {}'.format(service))

    return opt, channels, sensors, service, save_raw


def setup_variables():

    already_notified_pause = False
    system_started = False
    files_open = False 
    t_all = []

    return t_all, already_notified_pause, system_started, files_open

