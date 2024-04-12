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
            # Note. settime() causes ~10ms delay
            ntptime2.settime(t)
            tm = utime.gmtime(t)
            # convert to standartised timescale minute
            mSe = minsFrom12(tm[3],tm[4])
            sec = tm[5]
            print (f'Minute since UTC 12 am/pm %03d:%02d.%03d'%(mSe,sec,ms))
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
    ## uncomment to discconnect WiFi after obtaining time 
    # wifi.disconnect()