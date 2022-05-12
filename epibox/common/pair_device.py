# bult-in
import subprocess
import bluetooth

passkey = "1234"
addr = '98:D3:91:FD:3F:5C'

#subprocess.call("kill -9 `pidof bluetooth-agent`",shell=True)
status = subprocess.call("bluetooth-agent " + passkey + " &",shell=True)

try:
    s = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
    s.connect((addr, 1))
except bluetooth.btcommon.BluetoothError as err:
    # Error handler
    pass