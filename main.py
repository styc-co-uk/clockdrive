import ntpsync
import mindrive
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

def realignNTC():
    #reset all ticks but don't touch minute counter, thic only moves hand
    preTick.deinit()
    minTick.deinit()
    resQueue.init(mode=Timer.ONE_SHOT, period=1000, callback=lambda i: alignSec())
    print('Realigning to NTP')


# %%%%%% THE WEBPAGE %%%%%%
# Import necessary modules
import socket
import re

# HTML template for the webpage
def webpage(hour,minute,hourDST,advMineq):
    html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Master clock control</title>
            <meta name="viewport" content="width=device-width, initial-scale=1">
        </head>
        <body>
            <h1>Master clock control</h1>
            <h2><span id='gmt'>GMT</span> {hour:d}&#183;{minute:02d} / <span id='bst'>BST</span> {hourDST:d}&#183;{minute:02d}</h2>
            <form action="./syncNTP">
                <input type="submit" value="Sync with NTP" />
            </form>
            <h2>Manual adjust</h2>
            <form action="./advance" method="set">
                <label for="msg">Advance</label>
                <input type="int" size=3 maxlength=3 name="advMin" />
                <input type="submit" value="Submit"/>
            </form>
            <h2>Daylight saving</h2>
            <form action="./DSTon">
                <input type="submit" value="GMT&rarr;BST" />
            </form>
            <br>
            <form action="./DSToff">
                <input type="submit" value="GMT&larr;BST" />
            </form>
            <h2>Apply change</h2>
            <p>The clock will advance {advMineq} minutes.
            <form action="./applyCh">
                <input type="submit" value="Move!" />
            </form>
            <br>
            <form action="./clrCh">
                <input type="submit" value="Clear" />
            </form>
        </body>
        </html>
        """
    return str(html)

# Set up socket and start listening
addr = socket.getaddrinfo('0.0.0.0', 80)[0][-1]
s = socket.socket()
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind(addr)
s.listen()
print('Listening on', addr)


#%%%%%% THE RESET BUTTON %%%%%%

resIrqCount = 0
# debounce button
# reset button
resQueue = Timer()
def resIrq(pin):
    global resIrqCount
    if resIrqCount == 0:
        resIrqCount=-1
        realignNTC()
        print('Time reset button pressed')
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


# %%%%%% MAIN LOOP %%%%%

if __name__ == "__main__":
    # set first run to forward
    mindrive.setFwd(True)

    # reset all outputs
    mindrive.off_min()

    # turn on machine LED when all setup is done
    Pin("LED", Pin.OUT).on()

    alignSec()

    advMin = 0
    advHor = 0

    while True:
        try:
            conn, addr = s.accept()
            print('Got a connection from', addr)
            
            # Receive and parse the request
            request = conn.recv(1024)
            request = str(request)
            #print('Request content = %s' % request)

            try:
                request = request.split()[1]
                print('Request:', request)
            except IndexError:
                pass

            # Process the request and update variables
            advMnReX = re.search(r'/advance\?advMin=(\d+)',request)
            if advMnReX:
                advMin = int(advMnReX.group(1))
                print(f'Request advance {advMin}')
            elif request == '/DSTon?':
                print("DST on")
                advHor = 1
            elif request == '/DSToff?':
                print("DST off")
                advHor = 11
            elif request =='/clrCh?':
                print("reseted changes")
                advMin = 0
                advHor = 0
            elif request =='/applyCh?':
                resQueue.init(mode=Timer.ONE_SHOT, period=0, callback=lambda i: moveMin(advMineq))
                advMin = 0
                advHor = 0
                print("applied changes")
            elif request =='/syncNTP?':
                realignNTC()
                
            # convert minsince to hour:min
            def convertMSe(mSe):
                hour = mSe//60
                hourDST = hour+1
                if hour == 0:
                    hour=12
                minute = mSe%60
                return hour,minute,hourDST
            hour,minute,hourDST = convertMSe(minSince)

            advMineq = advHor*60 + advMin

            # Generate HTML response
            response = webpage(hour,minute,hourDST,advMineq)  

            # Send the HTTP response and close the connection
            conn.send('HTTP/1.0 200 OK\r\nContent-type: text/html\r\n\r\n')
            conn.send(response)
            conn.close()

        except OSError as e:
            conn.close()
            print('Connection closed')