from machine import Timer, Pin
import json

# this file imports buttton, button pin defined in pinout.json

with open('pinout.json') as f:
    but0 = json.load(f)['but0']
    f.close()

# debounce button
def buttonIrq(pin):
    global butIrqCount
    if butIrqCount == 0:
        print('button pressed')
        Timer(mode=Timer.ONE_SHOT, period=300, callback=resetIrqCount)
        butIrqCount=-1
        
def resetIrqCount(timer=None):
    global butIrqCount
    butIrqCount = 0
           
resetIrqCount()

pin_button = Pin(but0, mode=Pin.IN, pull=Pin.PULL_UP)

pin_button.irq(trigger=Pin.IRQ_FALLING,handler=buttonIrq)