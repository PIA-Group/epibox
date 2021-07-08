# built-in
import ast
import string 
import random
import json
import sys
import subprocess

# third-party
import paho.mqtt.client as mqtt

# local
from epibox.run import run_bitalino, run_scientisst

def random_str(length):
    letters = string.ascii_letters
    return ''.join(random.choice(letters) for i in range(length))

def on_message(client, userdata, message):
    
    #print("message received: ", str(message.payload.decode("utf-8")))
    message = str(message.payload.decode("utf-8"))
    message = ast.literal_eval(message)
    
    print(message)
    
    ######## Device selection ########
    if message[0] == 'NEW MAC': #set new default
        listMAC = message[1]
        with open('/home/pi/Documents/epibox/listMAC.json', 'w') as json_file:
            json.dump(listMAC, json_file)
            
    elif message[0] == 'USE MAC': 
        listMAC = message[1]
        print('MAC:', listMAC)
        devices_mac = [listMAC[device] for device in listMAC.keys() if (listMAC[device] != ' ' and listMAC[device] != '')]
        sys.argv += ['devices_mac', devices_mac]
        
        client.publish(topic='rpi', payload="['RECEIVED MAC']")
        
    elif message[0] == 'ID':
        patient_id = message[1]
        sys.argv += ['patient_id', patient_id]
        
    elif message[0] == 'RESTART':
        client.loop_stop()
        subprocess.run(['python3', '/home/pi/.local/lib/python3.7/site-packages/epibox/mqtt_startup.py'])
                
    ####### Configurations ########
    elif message[0] == 'FOLDER':
        if message[1] == 'RPi':
            folder = '/home/pi/Documents/epibox/acquisitions'
        else: 
            folder = '/media/pi/' + message[1] + '/acquisitions'
        sys.argv += ['initial_dir', folder]
    
    elif message[0] == 'FS':
        fs = message[1]
        sys.argv += ['fs', fs]
    
    elif message[0] == 'SAVE RAW':
        saveRaw = message[1]
        sys.argv += ['saveRaw', saveRaw]
        
    elif message[0] == 'EPI SERVICE':
        global epi_service
        epi_service = message[1]
        sys.argv += ['service', epi_service]
        
    elif message[0] == 'CHANNELS':
        channels = message[1]
        sys.argv += ['channels', channels]
        client.publish(topic='rpi', payload=str(['RECEIVED CONFIG']))
        
    elif message[0] == 'NEW CONFIG DEFAULT':
        config = message[1]
        defaults = {'initial_dir': config[0], 'fs': config[1], 'channels': config[2], 'saveRaw': config[3]}
        with open('/home/pi/Documents/epibox/config_default.json', 'w') as json_file:
            json.dump(defaults, json_file)
        
        
    elif message[0] == 'START':
        client.keepAlive = False 
        
    elif message[0] == 'TURN OFF':
        print('TURNING OFF RPI')
        client.publish(topic='rpi', payload=str(['TURNED OFF']))
    
    elif message[0] == 'TURNED OFF':
        subprocess.run(['sudo', 'shutdown', '-h', 'now'])
        
        

def main():

    with open('/home/pi/Documents/epibox/config_default.json', 'r') as json_file:
        arguments = json_file.read()   
    arguments = ast.literal_eval(arguments)
    
    sys.argv = []
    global epi_service
    epi_service = 'Bitalino'
    
    client_name = random_str(6)
    print('Client name (devices):', client_name)
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
    
    while client.keepAlive == True:
        continue
    
    else:
        client.loop_stop()
        for i in range(0, len(sys.argv), 2):
            arguments[sys.argv[i]] = sys.argv[i+1]
        
        with open('/home/pi/Documents/epibox/args.json', 'w') as json_file:
            json.dump(arguments, json_file)
        
        if epi_service == 'Bitalino' or 'Mini':
            run_bitalino.main()
            # subprocess.run(['python3', '-i', '/home/pi/.local/lib/python3.7/site-packages/epibox/PreEpiSeizures.py'])
        else: # epi_service == 'sense'
            run_scientisst.main()
            # subprocess.run(['python3', '-i', '/home/pi/.local/lib/python3.7/site-packages/epibox/sense.py'])
    
    
if __name__ == '__main__':

    main()
