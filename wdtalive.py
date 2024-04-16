from machine import Timer, WDT
import wifi

def setWDT():
    global wdt
    wdt = WDT(timeout=8388)

wdtKicker = Timer()

def reactivateWDT():
    global wdtCount
    wdtCount = 11
    kickWDT()
    wdtKicker.init(mode=Timer.PERIODIC, period=6000, callback=kickWDT)
    wifi.lazyconnect()

def kickWDT(timer=None):
    global wdtCount
    global wdt
    print(f'Feeding WDT, {wdtCount} autofeeds left')
    # deactivate if there's no renew for 6000s
    if wdtCount <= 0:
        wdtKicker.deinit()
    else:
        try:
            wdt.feed()
        except:
            print('WDT feed failed')
            pass
    wdtCount -= 1