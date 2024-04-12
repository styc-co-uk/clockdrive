import ntpsync
import mindrive
import time
from machine import RTC, Pin

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

while True:
    # obtain current time
    hour,minute,second = rtc.datetime()[4:7]
    if second == 00:
        if hour==lasthor:
            minmove = minute-lastmin
        else:
            minmove = 60+minute-lastmin
        if minmove > 0:
            print(f'UTC{hour}:{minute}:{second}, hand +{minmove} min')
            for i in range(minmove):
                mindrive.move_min()
                time.sleep(0.5)
            lastmin = minute
            lasthor = hour
    #
    # obtain button input
    buv = but.value()
    if buv == 0:
        if not bup:
            mindrive.move_min()
            ntpsync.updateRTC()
            # button pressed to prevent sticky key
            bup = True
            print(f'UTC{hour}:{minute}:{second}, manual hand move')
    else:
        bup = False
        
    time.sleep(0.1)