#gavin lyons 120817: called from rpi_tempmon.sh
#turns led on and off, Passed LED GPIO pin number and on/off option.

import sys
import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
LED = int(sys.argv[1])
GPIO.setup(LED, GPIO.OUT)

if sys.argv[2] == "off":
    GPIO.output(LED, False)
else:
    GPIO.output(LED, True)
