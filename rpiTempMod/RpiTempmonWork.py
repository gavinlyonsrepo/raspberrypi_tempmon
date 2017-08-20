
"""
module imported into rpi_tempmon contains functions related to mail option
logging options, toggling GPIOLED and getting R pi CPU and GPU information.
"""
import os
import socket #hostname
import datetime
import RPi.GPIO as GPIO


def get_cpu_tempfunc():
    """ Return CPU temperature as a character string"""
    result = 0
    mypath = "/sys/class/thermal/thermal_zone0/temp"
    with open(mypath, 'r') as mytmpfile:
        for line in mytmpfile:
            result = line
    result = result[0:2]
    return result


def get_gpu_tempfunc():
    """Return GPU temperature as a character string"""
    res = os.popen('/opt/vc/bin/vcgencmd measure_temp').readline()
    return res.replace("temp=", "")


def led_toggle_func(mode, led):
    """led_toggle_func , function to toggle a GPIO LED, passed mode on/off
    and GPIO pin of LED"""
    led = int(led)
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    GPIO.setup(led, GPIO.OUT)

    if mode == "off":
        GPIO.output(led, False)
    else:
        GPIO.output(led, True)


def logging_func(choice, mail_alert, cpu_limit, mailuser, destlog):
    """Function to log temps data to file, passed choice(args parameter which called it
    and 3 options from config file and path to log file"""
    if choice == "l":
        os.chdir(destlog)
    else:
        #makes a directory with time/date stamp and enters it
        os.chdir(destlog)
        myformat = "%H:%M:%S%a%b%d"
        today = datetime.datetime.today()
        dirvar = today.strftime(myformat)
        dirvar = destlog + "/" + dirvar + "_RPIT"
        if not os.path.exists(dirvar):
            os.makedirs(dirvar)
        os.chdir(dirvar)
    #making time
    today = datetime.datetime.today()
    #write to file
    with open("log.txt", "a+") as mylogfile:
        mylogfile.write("Raspberry pi temperature monitor: " + socket.gethostname() + '\n')
        mylogfile.write("TS = " + str(today) + '\n')
        mylogfile.write("GPU temperature = " + get_gpu_tempfunc())
        mylogfile.write("CPU temperature = " + get_cpu_tempfunc() + ".5'C" + '\n')
        if (choice == "l") and (mail_alert == "1"):
            if get_cpu_tempfunc() > cpu_limit:
                mylogfile.write("Warning : cpu over the temperature limit: " +  cpu_limit + '\n')
                mail_func(" Warning ", mailuser, destlog)


def mail_func(sub, mailu, destlog):
    """Function sends mail via ssmpt , passed subject line and mail account name and logfile"""
    os.chdir(destlog)
    if os.path.exists("log.txt"):
        #Command to send mail by ssmpt from bash
        os.system('cat "log.txt" | mail -s "raspberry-PI-temperature {}  " {}'.format(sub, mailu))


def test():
    """import code"""
    pass

if __name__ == '__main__':
    test()
