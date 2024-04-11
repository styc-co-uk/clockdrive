import wifi
import ntptime2
from machine import RTC

def printnow():
    rtc = RTC()
    print(rtc.datetime())

def updateRTC():
    # this code can get UTC time from web and update Pi's clock
    wifi.connect()
    ntptime2.host = "uk.pool.ntp.org"
    # try four times to get time
    for i in range(5):
        try:
            t,ms = ntptime2.time()
            ntptime2.settime(t)
        except:
            print ('get time error')
            ms=-1
        else:
            break
    return ms
    #wifi.disconnect()
    #printnow()