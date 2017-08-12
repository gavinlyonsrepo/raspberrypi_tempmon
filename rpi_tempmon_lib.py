'''gavin lyons 120817 called from 
tunrs led on and off rp_tempmon passed LED GPIO and on/off option '''

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





