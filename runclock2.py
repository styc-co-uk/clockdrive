import ntpsync
import mindrive
import time
from machine import RTC, Pin, Timer

# This code runs the clock

# setup timers
preTick = Timer()
minTick = Timer()

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
            preTick.init(mode=Timer.ONE_SHOT, period=1000*(60-second), callback=initPulse)
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
    minTick.init(mode=Timer.PERIODIC, period=60000, callback=minPulse)
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



#%%%%%% THE RESET BUTTON %%%%%%

alignRequest = Timer()

def alignRequestFun(timer):
    ntpsync.updateRTC()
    alignSec()
    
# debounce button
def buttonIrq(pin):
    global butIrqCount
    if butIrqCount == 0:
        butIrqCount=-1
        #reset all ticks but don't touch minute counter, thic only moves hand
        preTick.deinit()
        minTick.deinit()
        alignRequest.deinit()
        print('button pressed')
        mindrive.move_min()
        alignRequest.init(mode=Timer.ONE_SHOT, period=500, callback=alignRequestFun)
        Timer(mode=Timer.ONE_SHOT, period=300, callback=resetIrqCount)
        
        
def resetIrqCount(timer=None):
    global butIrqCount
    butIrqCount = 0
           
resetIrqCount()
resetBut = Pin(0, mode=Pin.IN, pull=Pin.PULL_UP)
resetBut.irq(trigger=Pin.IRQ_FALLING,handler=buttonIrq)