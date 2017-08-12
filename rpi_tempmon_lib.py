'''gavin lyons 120817: called from rpi_tempmon.sh
tunrs led on and off, Passed LED GPIO pin number and on/off option '''

import RPi.GPIO as GPIO
import sys
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
led = int(sys.argv[1])
GPIO.setup(led,GPIO.OUT)

if sys.argv[2] == "off" :
	GPIO.output(led,False)
else:
	GPIO.output(led,True)





