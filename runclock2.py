import ntpsync
import mindrive
import time
from machine import RTC, Pin, Timer

# This code runs the clock

# wait until second is aligned and start timer
def alignSec():
    from timeconvert import minsFrom12
    print ('Waiting for second to align')
    lasthor,lastmin,lastsec = rtc.datetime()[4:7]
    while True:
        global minSince
        # waiting for the second to jump
        hour,minute,second = rtc.datetime()[4:7]
        if second != lastsec:
            # activate timer at the next full minute
            preTick = Timer(mode=Timer.ONE_SHOT, period=1000*(60-second), callback=initPulse)
            # update time from 12 counter
            minSince = minsFrom12(hour,minute)
            print(minSince,'alignSec')
            break

# initilise minute pulse
def initPulse(timer):
    global minSince
    timer.deinit()
    minSince+=1
    # if reset on 11:59
    if minSince >=720: minSince = 0
    # fire the periodic 60sec pulse (starting after 60s)
    minTick = Timer(mode=Timer.PERIODIC, period=60000, callback=minPulse)
    print(minSince,'initPulse')
    # initiate the 1st pulse
    mindrive.move_min()

# minute pulse duty cycle
def minPulse(timer):
    global minSince
    minSince+=1
    print(minSince,'minPulse')
    mindrive.move_min()
    # if at reset state stop timer
    if pulseReset(minSince):
        pulseCal(timer)
        print('12hr reset')

# check pulse reset condition
def pulseReset(minSince):
    if minSince>=720:
        return True
    return False

# disable timer and realign second
def pulseCal(timer):
    global minSince
    timer.deinit()
    minSince = 0
    alignSec()

# update NTP time to RTC
rtc = RTC()
ntpsync.updateRTC()

# set first run to forward
mindrive.setFwd(True)

# reset all outputs
mindrive.off_min()

# turn on machine LED when all setup is done
Pin("LED", Pin.OUT).on()

alignSec()