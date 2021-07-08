def sync_bitalino(value, device):
    print ('')
    print ('Synchronizing...')

    try:
        if value == 0:
            value = 1
            device.trigger([1,1])
            #print (str(value))
        else:
            value = 0
            device.trigger([0,0])
            #print (str(value))
            
    except Exception as e:
        print('error in sync_bitalino')
        print(e)
        pass
 
    return value
