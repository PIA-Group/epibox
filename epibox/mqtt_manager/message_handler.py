# built-in
import ast
import subprocess

def on_message(client, userdata, message):

    message = str(message.payload.decode("utf-8"))
    message = ast.literal_eval(message)

    if message[0] == 'RESTART':
        client.loop_stop()
        #startup.main()

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