# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
# % This code is forked from                          %
# % https://github.com/micropython/micropython-lib/blob/master/micropython/net/ntptime/ntptime.py %
# % with additional feature to support millisecond    %
# % NTP protocal supports accuracy up to 2^-32 second %
# % but exceeds the machine accuracy                  %
# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
try:
    import utime
except:
    import time as utime
try:
    import usocket as socket
except:
    import socket
try:
    import ustruct as struct
except:
    import struct

# The NTP host can be configured at runtime by doing: ntptime.host = 'myhost.org'
host = "pool.ntp.org"
# The NTP socket timeout can be configured at runtime by doing: ntptime.timeout = 2
timeout = 1


def time():
    NTP_QUERY = bytearray(48)
    NTP_QUERY[0] = 0x1B
    addr = socket.getaddrinfo(host, 123)[0][-1]
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # addr = socket.getaddrinfo(host, 123)[0][-1]
        s.settimeout(timeout)
        res = s.sendto(NTP_QUERY, addr)
        msg = s.recv(48)
    finally:
        s.close()
    # Date and time accurate to second
    val = struct.unpack("!I", msg[40:44])[0]
    # Time in milisecond
    val_ms = round(struct.unpack("!I", msg[44:48])[0]*2**-32*1000)

    EPOCH_YEAR = utime.gmtime(0)[0]
    if EPOCH_YEAR == 2000:
        # (date(2000, 1, 1) - date(1900, 1, 1)).days * 24*60*60
        NTP_DELTA = 3155673600
    elif EPOCH_YEAR == 1970:
        # (date(1970, 1, 1) - date(1900, 1, 1)).days * 24*60*60
        NTP_DELTA = 2208988800
    else:
        raise Exception("Unsupported epoch: {}".format(EPOCH_YEAR))

    return val - NTP_DELTA, val_ms

# There's currently no timezone support in MicroPython, and the RTC is set in UTC time.
def settime(t=None):
    if t==None:
        t,_= time()

    from machine import RTC

    tm = utime.gmtime(t)
    # RTC not supporting millisecond
    # see https://www.raspberrypi.com/documentation/pico-sdk/hardware.html#rpipc382390bd58f4f14aadf
    # note: the RTC second tick can not be changed using 'utime.sleep_ms'
    RTC().datetime((tm[0], tm[1], tm[2], tm[6] + 1, tm[3], tm[4], tm[5], 0))
    print('Machine RTC set: %04d-%02d-%02d, %02d:%02d:%02d' % tuple(tm[0:6]))