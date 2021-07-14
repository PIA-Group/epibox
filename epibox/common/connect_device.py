import bitalino
import time

def connect_device(macAddress, client, devices):
    
    connected = False
    devices = [d for d in devices if d] # remove None
    
    if macAddress in [d.macAddress for d in devices]:
        try:
            print('{} state: {}'.format(macAddress, [d.state()for d in devices if d.macAddress==macAddress]))
            connected = True
        
        except Exception as e:
            print('error in connect_device: {}'.format(e))
            del devices[[d.macAddress for d in devices].index(macAddress)]
    else:
        print('trying to connect')

        try:
            device = bitalino.BITalino(macAddress, timeout=5)
            devices += [device]
            if macAddress in [d.macAddress for d in devices]:
                connected = True
            
        except Exception as e:
            print(e)
    
    devices = [d for d in devices if d] # remove None

    if not connected or macAddress not in [d.macAddress for d in devices]:
        client.publish(topic='rpi', qos=2, payload="['MAC STATE', '{}', '{}']".format(macAddress, 'failed'))
    else:
        client.publish(topic='rpi', qos=2, payload="['MAC STATE', '{}', '{}']".format(macAddress, 'connected'))
    
    return connected, devices