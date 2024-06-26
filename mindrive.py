from machine import Pin
import time
import json

# this script moves minute

with open('pinout.json') as f:
    pinout = json.load(f)
    f.close()

try:
    with open('clockstate.json') as f:
        forward = bool(json.load(f)['forward'])
        f.close()
    print(r'Forward set as %s.'%forward)
except:
    forward = True
    print(r'No data for forward, initialise as %s'%forward)

# setup pins
min0 = Pin(pinout['min0'], Pin.OUT)
min1 = Pin(pinout['min1'], Pin.OUT)
led0 = Pin(pinout['led0'], Pin.OUT)
led1 = Pin(pinout['led1'], Pin.OUT)
led = Pin('LED', Pin.OUT)

# input variable forward
#def setFwd(ifFwd=True):
#    global forward
#    forward = ifFwd

# direction 1
def Min0(val):
    assert type(val) == bool
    min0.value(val)
    led0.value(val)

# direction 2
def Min1(val):
    assert type(val) == bool
    min1.value(val)
    led1.value(val)

# both off
def off_min():
    Min0(False)
    Min1(False)

# move minute hand
def move_min(minSince):
    global forward
    Min0(forward)
    Min1(not forward)
    led.off()
    #print(forward)
    forward = not forward
    time.sleep(0.25)
    off_min()
    led.on()
    time.sleep(0.25)
    print(f'Moving +1, at {minSince}')
    with open('clockstate.json', 'w') as f:
        json.dump({'minSince':minSince, 'forward':int(forward)}, f)
        f.close()
