import ntpsync
import mindrive
import time
from machine import Pin, Timer

# This code runs the clock

# define minute advance function
def moveMin(dMin):
    for i in range(dMin):
        Timer().init(mode=Timer.ONE_SHOT, period=0, callback=minWorker)
    print(f'Minute hand +{dMin}')

def minWorker(timer):
    mindrive.move_min()

# setup timers
preTick = Timer()
minTick = Timer()
#corrMin = Timer()
minSince = None

# wait until second is aligned and start timer
def alignSec():
    global minSince
    from timeconvert import minsFrom12
    print ('I am correcting clock...')
    #lasthor,lastmin,lastsec = rtc.datetime()[4:7]

    # update NTP time to RTC, get current ms
    synMSe, second, microSec = ntpsync.updateRTC()

    # delay in ms to the next minute
    msWait = 60000-(second*1000+microSec)

    #!!!! make sure code elegant!
    if minSince == None:
        preTick.init(mode=Timer.ONE_SHOT, period=msWait, callback=initPulse)
        print('Initialise pulse')
    else:
        delMSe = synMSe-minSince # check 720 case
        if delMSe >= 0:
            if (delMSe > 0 & delMSe < 5):
                # clock runs slow, add the missed minute
                moveMin(delMSe)
                #corrMin.init(mode=Timer.ONE_SHOT, period=0, callback=lambda i: moveMin(delMSe))
                print(f'Adding {delMSe} correction mins')
            # fire initial run
            preTick.init(mode=Timer.ONE_SHOT, period=msWait, callback=initPulse)
            print('Initialise clock')
        elif delMSe > -5:
            # clock run fast
            preTick.init(mode=Timer.ONE_SHOT, period=(msWait+60000*delMSe), callback=initPulse)
            print(f'Initialise with {-delMSe} mins wait')
        else:
            preTick.init(mode=Timer.ONE_SHOT, period=msWait, callback=initPulse)
            print(f'Initialise not/ Time off {-delMSe} mins, ignore correction')
    minSince = synMSe

def minTimer(addition):
    global minSince
    minSince += addition
    #12th o'clock
    if minSince >= 720:
        minSince = addition
    return minSince

    # while True:
    #     # waiting for the second to jump
    #     hour,minute,second = rtc.datetime()[4:7]
    #     if second != lastsec:
    #         # activate timer at the next full minute
    #         preTick.init(mode=Timer.ONE_SHOT, period=1000*(60-second), callback=initPulse)
    #         # update time from 12 counter
    #         minSince = minsFrom12(hour,minute)
    #         print(minSince,'alignSec')
    #         break

# initilise minute pulse
def initPulse(timer):
    timer.deinit()
    # fire the periodic 60sec pulse (starting after 60s)
    minTick.init(mode=Timer.PERIODIC, period=60000, callback=minPulse)
    minSince = minTimer(1)
    print(minSince,'initPulse')
    # initiate the 1st pulse
    moveMin(1)

# minute pulse duty cycle
def minPulse(timer):
    minSince = minTimer(1)
    print(minSince,'minPulse')
    moveMin(1)
    # if at reset state stop timer
    if pulseReset(minSince):
        pulseCal(timer)
        print('Time realign')

# check pulse reset condition
def pulseReset(minSince):
    if minSince>=719:
        return True
    return False

# disable timer and realign second
def pulseCal(timer):
    timer.deinit()
    print('Minute pulse disabled')
    alignSec()

if __name__ == "__main__":
    # set first run to forward
    mindrive.setFwd(True)

    # reset all outputs
    mindrive.off_min()

    # turn on machine LED when all setup is done
    Pin("LED", Pin.OUT).on()

    alignSec()



#%%%%%% THE RESET BUTTON %%%%%%

resIrqCount = 0
# debounce button
# reset button
resQueue = Timer()
def resIrq(pin):
    global resIrqCount
    if resIrqCount == 0:
        resIrqCount=-1
        #reset all ticks but don't touch minute counter, thic only moves hand
        preTick.deinit()
        minTick.deinit()
        print('Time reset button pressed')
        resQueue.init(mode=Timer.ONE_SHOT, period=1000, callback=lambda i: alignSec())
        resetIrqT.init(mode=Timer.ONE_SHOT, period=400, callback=resetIrqCount)

resetIrqT = Timer()
def resetIrqCount(timer=None):
    global resIrqCount, advIrqCount
    print('Button state reset')
    advIrqCount = 0
    resIrqCount = 0


advIrqCount = 0
# advance button
def advIrq(pin):
    global advIrqCount
    if advIrqCount == 0:
        advIrqCount=-1
        print('Time advance button pressed')
        # timer won't work if it's activated during bouncing
        resQueue.init(mode=Timer.ONE_SHOT, period=300, callback=lambda i: moveMin(1))
        resetIrqT.init(mode=Timer.ONE_SHOT, period=400, callback=resetIrqCount)
        
resetBut = Pin(0, mode=Pin.IN, pull=Pin.PULL_UP)
resetBut.irq(trigger=Pin.IRQ_FALLING,handler=resIrq)
advanceBut = Pin(1, mode=Pin.IN, pull=Pin.PULL_UP)
advanceBut.irq(trigger=Pin.IRQ_FALLING,handler=advIrq)