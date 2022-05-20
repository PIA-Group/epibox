# built-in
import string 
import random

# third-party
import bitalino

# local
from epibox import config_debug


def random_str(length):

    letters = string.ascii_letters
    return ''.join(random.choice(letters) for i in range(length))


def connect_device(macAddress, client, devices):
    
    connected = False
    devices = [d for d in devices if d] # remove None
    config_debug.log(f'devices: {devices}')
    
    if macAddress in [d.macAddress for d in devices]:
        try:
            config_debug.log(f'{macAddress} state: {[d.state()for d in devices if d.macAddress==macAddress]}')
            config_debug.log(f'{macAddress} state: {[d.state()for d in devices if d.macAddress==macAddress]}')
            connected = True
        
        except Exception as e:
            del devices[[d.macAddress for d in devices].index(macAddress)]
    
    else:

        try: 
            device = bitalino.BITalino(macAddress, timeout=5)
            
            devices += [device]
        except Exception as e:
            config_debug.log(e)
                                
        if macAddress in [d.macAddress for d in devices]:
            connected = True


    devices = [d for d in devices if d] # remove None

    if not connected or macAddress not in [d.macAddress for d in devices]:
        client.publish(topic='rpi', qos=2, payload="['MAC STATE', '{}', '{}']".format(macAddress, 'failed'))

    else:
        client.publish(topic='rpi', qos=2, payload="['MAC STATE', '{}', '{}']".format(macAddress, 'connected'))
    
    return connected, devices