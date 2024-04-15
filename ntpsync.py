import wifi
import ntptime2
import utime
from machine import RTC, reset
from timeconvert import minsFrom12
import json

with open('ntphosts.json') as f:
    ntphosts = json.load(f)['hosts']
    f.close()

def printnow():
    rtc = RTC()
    print(rtc.datetime())

def updateRTC():
    # this code can get UTC time from web and update Pi's clock
    try:
        wifi.connect()
    except:
        reset()
    #ntphosts = ("uk.pool.ntp.org","0.uk.pool.ntp.org","1.uk.pool.ntp.org","2.uk.pool.ntp.org","3.uk.pool.ntp.org","pool.ntp.org")
    # ntptime2.host = ntphosts[0]
    # try four times to get time
    for i in range(len(ntphosts)*5):
        j = i//5
        ntptime2.host = ntphosts[j]
        try:
            print ('Syncing time from %s' % ntphosts[j])
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
            mSe = None
            ms  = None
            sec = None
        else:
            break
    if mSe == None:
        raise Exception("Get time error!")
    return mSe, sec, ms
    ## uncomment to discconnect WiFi after obtaining time 
    # wifi.disconnect()