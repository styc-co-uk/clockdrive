# Raspberry Pi Pico W NTP Master Clock Project
![headphoto](/images/head.jpg)

This project is built with a Raspberry Pi Pico W with Wi-Fi, inspired by [a similar project from veeb.ch](https://github.com/veebch/clock). In this code, time is syncd from NTP and accurate to milisecond. Impulse is provided by the pi built-in ``Timer`` function. It provides an simple web interface to adjust clock, and the equivalent GPIO inputs.

The current code is designed for alternating minute impulse clocks (this include most central & eastern european influenced mechanisms). It uses two output channels to drive two inputs on a H-bridge that switches a 12V DC that feeds the slave clocks. The code can be easily modified to support 30 s impulse. It supports a website to manage the clock.

![webpage](/images/page.png)

## Configuration
### auth.json
``` json
{
    "ssid":"<--YOUR SSID HERE-->",
    "password":"<--YOUR PASSWORD HERE-->"
}
```
### pinout.json
``` json
{
    "min0":<--FORWARD TO H-BRIDGE-->,
    "min1":<--BACKWARD TO H-BRIDGE-->,
    "led0":<--LED-->,
    "led1":<--LED-->,
    "but0":<--RESET BUTTON-->, // not used yet
    "but1":<--ADVANCE BUTTON--> // not used yet
}
```

### ntphosts.json
You should choose the best [ntp server pools](https://www.ntppool.org/en/).
``` json
{
    "hosts": ["uk.pool.ntp.org","0.uk.pool.ntp.org","1.uk.pool.ntp.org","2.uk.pool.ntp.org","3.uk.pool.ntp.org","pool.ntp.org"]
}
```

### clockstate.json
This file is intentionally left blank but need to present in the pi.
```
```
