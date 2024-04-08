import wifi
import ntptime
from machine import RTC

def printnow():
    rtc = RTC()
    print(rtc.datetime())

def updateRTC():
    # this code can get UTC time from web and update Pi's clock
    wifi.connect()
    ntptime.host = "sntp.cam.ac.uk"
    # try four times to get time
    for i in range(5):
        try:
            ntptime.time()
            ntptime.settime()
        except:
            print ('get time error')
        else:
            break
    #wifi.disconnect()
    printnow()