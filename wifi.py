import network
import time
import json

with open('auth.json') as f:
    wifi_config = json.load(f)
    f.close()
    ssid = wifi_config['ssid']
    password = wifi_config['password']

def connect():
    #Connect to WLAN
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(ssid, password)
    while wlan.isconnected() == False:
        print('Wifi: Waiting for connection...')
        time.sleep(1)
    print(f'Wifi: Connected')
    
def disconnect():
    #Turn off wifi module
    wlan = network.WLAN(network.STA_IF)
    wlan.deinit()
