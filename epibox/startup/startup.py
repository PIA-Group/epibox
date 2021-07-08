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
from epibox.startup import devices


def random_str(length):
    letters = string.ascii_letters
    return ''.join(random.choice(letters) for i in range(length))

    
def on_message(client, userdata, message):
    
    message = str(message.payload.decode("utf-8"))
    message = ast.literal_eval(message)
    
    if message == ['Send MAC Addresses']:
        with open('/home/pi/Documents/epibox/listMAC.json', 'r') as json_file:
            listMAC = json_file.read()
        
        listMAC = ast.literal_eval(listMAC)
        listMAC2 = "'DEFAULT MAC','{}','{}'".format(list(listMAC.values())[0], list(listMAC.values())[1])
        
        client.publish(topic='rpi', payload=listMAC2)
    
    elif message[0] == 'TIME':
        subprocess.run(["sudo", "date", "-s", message[1]])
        subprocess.run(["sudo", "date"], capture_output=True, text=True)
    
    elif message == ['Send drives']:
        listDrives = ['DRIVES']
        drives = os.listdir('/media/pi')
        for drive in drives:
            total, _ , free = shutil.disk_usage('/media/pi/{}'.format(drive))
            listDrives += ['{} ({:.1f}% livre)'.format(drive, (free/total)*100)]
        total, _ , free = shutil.disk_usage('/')
        listDrives += ['RPi ({:.1f}% livre)'.format((free/total)*100)]
        client.publish(topic='rpi', payload="{}".format(listDrives))
        
    elif message == ['Send config']:
        with open('/home/pi/Documents/epibox/config_default.json', 'r') as json_file:
            defaults = json_file.read()
        defaults = ast.literal_eval(defaults)
        drive = defaults['initial_dir']
        config = json.dumps(['DEFAULT CONFIG', [drive, defaults['fs'], defaults['channels']]])
        client.publish(topic='rpi', payload=config)
        
    elif message == ['GO TO DEVICES']:
        client.keepAlive = False
        
    elif message[0] == 'TURN OFF':
        print('TURNING OFF RPI')
        client.publish(topic='rpi', payload=str(['TURNED OFF']))
    
    elif message[0] == 'TURNED OFF':
        subprocess.run(['sudo', 'shutdown', '-h', 'now'])
        

def main():
    
    client_name = random_str(6)
    print('Client name (startup):', client_name)
    host_name = '192.168.0.10'
    topic = 'rpi'
    
    client = mqtt.Client(client_name)
    setattr(client, 'keepAlive', True)
    client.username_pw_set(username='preepiseizures', password='preepiseizures')
    client.connect(host_name)
    client.subscribe(topic, 1)
    client.on_message = on_message
    client.loop_start()
    print('Successfully subcribed to topic', topic)
    
    while client.keepAlive == True:
        continue
    
    else:
        client.loop_stop()
        devices.main()
        #subprocess.run(['python3', '/home/pi/.local/lib/python3.7/site-packages/epibox/mqtt_devices.py'])

        
    

if __name__ == '__main__':

    main()


