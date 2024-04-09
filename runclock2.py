import ntpsync
import mindrive
import time
from machine import RTC, Pin, Timer

# This code runs the clock

# update NTP time to RTC
ntpsync.updateRTC()

# set first run to forward
mindrive.setFwd(True)

# reset all outputs
mindrive.off_min()

# correction input from button
but = Pin(0, Pin.IN, Pin.PULL_UP)
#sticky key prevention
bup = False

#timezone = 1
rtc = RTC()
lasthor,lastmin = rtc.datetime()[4:6]

# turn on machine LED when all setup is done
Pin("LED", Pin.OUT).on()



led0 = Pin(14, Pin.OUT)
led1 = Pin(13, Pin.OUT)

counter = 1

def pulse(timer):
    global mincounter
    # reset a full hour
    print(mincounter)
    if mincounter == 0:
        pulseReset(timer)
    else:
        mincounter-=1
        led0.on()
        time.sleep(0.1)
        led0.off()

def pulseReset(timer):
    global mincounter
    mincounter = 60
    timer.deinit()
    alignSec()
    
    
#blue = Timer(mode=Timer.PERIODIC, period=966, callback=pulse)

#red = Timer(mode=Timer.PERIODIC, period=800, callback=intrp2)

#but = Pin(0, Pin.IN, Pin.PULL_UP)

#butval = 0

#def butpush(but):
#    global butval
#    butval += 1

#but.irq(handler=butpush, trigger=Pin.IRQ_RISING)


def lag_timer(timer):
    global mincounter
    # fire the periodic 60sec pulse (starting after 60s)
    tick = Timer(mode=Timer.PERIODIC, period=60000, callback=pulse)
    # initiate the 1st pulse
    print(mincounter)
    mincounter-=1
    led0.on()
    time.sleep(0.1)
    led0.off()

def alignSec():
    print ('Waiting to align second')
    lasthor,lastmin,lastsec = rtc.datetime()[4:7]
    while True:
        global mincounter
        # waiting for the second to jump
        hour,minute,second = rtc.datetime()[4:7]
        if second != lastsec:
            # wait until the next full minute to fire shot
            pretick = Timer(mode=Timer.ONE_SHOT, period=1000*(60-second), callback=lag_timer)
            mincounter = 59-minute
            # at 59 mins always reset
            if mincounter == 0: mincounter+=60
            break

alignSec()

