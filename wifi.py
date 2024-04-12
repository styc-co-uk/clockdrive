# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
# % This code connects pico to wifi with stored info %
# % info stored in auth.json at the pico root folder %
# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
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
    ip = wlan.ifconfig()[0]
    print(f'Wifi: Connected, IP: {ip}')
    
def disconnect():
    #Turn off wifi module
    wlan = network.WLAN(network.STA_IF)
    wlan.deinit()