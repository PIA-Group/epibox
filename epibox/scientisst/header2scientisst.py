
from epibox.scientisst import scientisst

def header2scientisst(filename, file_time, file_date, devices, mac_channels, sensors, fs, saveRaw):
    
    filename.write('# OpenSignals Text File Format' + '\n')
    
    mac_dict = {}
    resolution = {}
    fmt = []# get format to save values in txt
    
    for n_device,device in enumerate(devices):
        
        fmt += ['%i']
        mac_dict[device.macAddress] = {}
        
        mac_dict[device.macAddress]['sensor'] = []
        for i,elem in enumerate(mac_channels):
            if elem[0]==device.macAddress:
                mac_dict[device.macAddress]['sensor'] += [sensors[i]]
                if saveRaw:
                    fmt += ['%i']
                else:
                    fmt += ['%.2f']
        
        mac_dict[device.macAddress]['device name'] = 'Device '+str(n_device+1) 
        
        aux = ['A'+elem[1] for elem in mac_channels if elem[0]==device.macAddress]
        mac_dict[device.macAddress]['column'] = ["nSeq"]+aux
        
        mac_dict[device.macAddress]['sync interval'] = 2 #???
        
        mac_dict[device.macAddress]['start time'] = file_time
        
        mac_dict[device.macAddress]['device connection'] = device.macAddress
                
        mac_dict[device.macAddress]['channels'] = [int(elem[1]) for elem in mac_channels if elem[0]==device.macAddress]
        
        mac_dict[device.macAddress]['date'] = file_date
        
        mac_dict[device.macAddress]['firmware version'] = device.version() 
        
        mac_dict[device.macAddress]['device'] = 'scientisst_sense'
        
        mac_dict[device.macAddress]['sampling rate'] = fs
        
        if saveRaw:
            mac_dict[device.macAddress]['label'] = ['RAW' for i,elem in enumerate(mac_channels) if elem[0]==device.macAddress]
        else:
            mac_dict[device.macAddress]['label'] = [sensors[i] for i,elem in enumerate(mac_channels) if elem[0]==device.macAddress]
        
        
        mac_dict[device.macAddress]['resolution'] = [4] + [12]*len(mac_channels)
        resolution[device.macAddress] = mac_dict[device.macAddress]['resolution']

    header = {'resolution': resolution, 'saveRaw': saveRaw, 'service': 'Sense'}
    
    print("# " + str(mac_dict) + '\n')
    filename.write("# " + str(mac_dict) + '\n')
    filename.write('# EndOfHeader' + '\n')
    
    return tuple(fmt), header
