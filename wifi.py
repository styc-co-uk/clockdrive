# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
# % This code connects pico to wifi with stored info %
# % info stored in auth.json at the pico root folder %
# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
import network
import time
import rp2
import json

rp2.country('GB')
wlan = network.WLAN(network.STA_IF)

with open('auth.json') as f:
    wifi_config = json.load(f)
    f.close()
    ssid = wifi_config['ssid']
    password = wifi_config['password']

def connect():
    #Connect to WLAN
    wlan.active(True)
    wlan.connect(ssid, password)
    counter = 0
    resetcounter = 0
    while wlan.isconnected() == False:
        print('Wifi: Waiting for connection...')
        counter+=1
        if counter >= 10:
            wlan.deinit()
            wlan.active(True)
            wlan.connect(ssid, password)
            counter = 0
            resetcounter += 1
            print(r'Resetting wifi')
        if resetcounter >= 5:
           raise RuntimeError('network connection failed')
        time.sleep(1)
    resetcounter = 0
    ip = wlan.ifconfig()[0]
    print(f'Wifi: Connected, IP: {ip}')
    
def disconnect():
    #Turn off wifi module
    wlan.deinit()