# built-in
import json

# local
from epibox import config_debug
from epibox.exceptions.system_exceptions import MQTTConnectionError


def get_battery(client, devices, service):

    if service != "Mini":
        try:
            battery = {}
            for device in devices:
                state = device.state()
                if state["battery"] > 63:
                    battery_volts = 2 * ((state["battery"] * 3.3) / (2**10 - 1))
                else:
                    battery_volts = 2 * ((state["battery"] * 3.3) / (2**6 - 1))

                battery[device.macAddress] = battery_volts

            battery_json = json.dumps(["BATTERY", battery])
            message_info = client.publish("rpi", battery_json)
            if message_info.rc == 4:  # MQTT_ERR_NO_CONN
                raise MQTTConnectionError

        except Exception as e:  # TODO which errors arise here?
            config_debug.log(e)
            pass
