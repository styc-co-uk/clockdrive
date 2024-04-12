import wifi
import ntptime2
import utime
from machine import RTC
from timeconvert import minsFrom12

def printnow():
    rtc = RTC()
    print(rtc.datetime())

def updateRTC():
    # this code can get UTC time from web and update Pi's clock
    wifi.connect()
    ntptime2.host = "uk.pool.ntp.org"
    # try four times to get time
    for i in range(10):
        try:
            t,ms = ntptime2.time()
            # ~10ms delay, do this to save memory
            ntptime2.settime(t)
            tm = utime.gmtime(t)
            # mins since 12
            mSe = minsFrom12(tm[3],tm[4])
            sec = tm[5]
        except:
            print ('get time error')
            ms  = -1
            mSe = -1
            sec = -1
            if i == 5:
                ntptime2.host = "pool.ntp.org"
        else:
            break
    return mSe, sec, ms
    #wifi.disconnect()
    #printnow()