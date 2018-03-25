
"""
module imported into rpi_tempmon contains functions related to mail option
logging options, toggling GPIO LED and getting Rpi CPU and GPU information.
"""
import os
import socket # hostname
import datetime
import RPi.GPIO as GPIO

def notify_func(cli_arg_2, cpu_limit):
    """ function to control notify-send alerts, passed in second command line argument"""
    print(cli_arg_2)
    title = "rpi_tempmon"
    message = ""
    
    if cli_arg_2 == "2":
        # send notify always
        message = "CPU temperature => " + get_cpu_tempfunc() + "'C"
        os.system('notify-send "{}" "{}"'.format(title, message))
    elif cli_arg_2 == "3":
        # send notify if cpulimit exceed)
        if get_cpu_tempfunc() > cpu_limit:
            message = "ALARM : CPU temp  => {}'C : Limit at {}'C".format(get_cpu_tempfunc(), cpu_limit)
            os.system('notify-send "{}" "{}"'.format(title, message))
    else:
        print("Error invalid argument to -n option 1 or 2 only")
   
    
def get_cpu_tempfunc():
    """ Return CPU temperature """
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


def logging_func(choice, mail_alert, cpu_limit, mailuser, destlog, alarm_mode):
    """Function to log temps data to file, passed choice(args parameter which called it
    and 3 options from config file and path to log file"""
    if choice == "l":
        os.chdir(destlog)
    else:
        #m akes a directory with time/date stamp and enters it
        os.chdir(destlog)
        dirvar = datetime.datetime.now().strftime("%H:%M:%S%a%b%d")
        dirvar = destlog + "/" + dirvar + "_RPIT"
        if not os.path.exists(dirvar):
            os.makedirs(dirvar)
        os.chdir(dirvar)
        
    # making time string
    today = datetime.datetime.now().strftime("%y-%m-%d %H:%M:%S")
    # write to file
    with open("log.txt", "a+") as mylogfile:
        mylogfile.write("Raspberry pi temperature monitor: " + socket.gethostname() + '\n')
        mylogfile.write("TS = " + str(today) + '\n')
        mylogfile.write("GPU temperature = " + get_gpu_tempfunc())
        mylogfile.write("CPU temperature = " + get_cpu_tempfunc() + ".5'C" + '\n')
        # Add alarm message to log 
        if (alarm_mode == "1") and  get_cpu_tempfunc() > cpu_limit:
            mylogfile.write("Warning : cpu over the temperature limit: " +  cpu_limit + '\n')
        
    
    # Send log by mail 
    if (choice == "l") and (mail_alert == "1"):
        if get_cpu_tempfunc() > cpu_limit:
            mail_func(" Warning ", mailuser, destlog)


def mail_func(sub, mailu, destlog):
    """Function sends mail via ssmpt , passed subject line and mail account name and logfile"""
    os.chdir(destlog)
    if os.path.exists("log.txt"):
        # Command to send mail by ssmpt from bash
        os.system('cat "log.txt" | mail -s "raspberry-PI-temperature {}  " {}'.format(sub, mailu))

def data_func(destlog):
    """function to parse log file and produce a Data report"""
    # define lists to hold data from logfile
    timelist = []
    cpulist = []
    my_warning_count = 0

    # get data from file and put into lists
    mypath = destlog + "/" + "log.txt"
    if os.path.isfile(mypath):
        with open(mypath, 'r') as myfile:
            for line in myfile:
                if "TS" in line:
                    timelist.append(line[5:-1])
                if "CPU" in line:
                    cpulist.append(line[18:20])
                if "Warning" in line:
                    my_warning_count += 1
    else:
        print("Error: Log file not found at {}".format(mypath))
        return 1

    print("\nRaspberry pi CPU GPU temperature monitor program")
    print("Data report on {} \n".format(mypath))
    print("Start temperature: {} Time: {}".format(cpulist[0], timelist[0]))
    length = len(cpulist)
    print("End temperature: {} Time: {}".format(cpulist[length-1], timelist[length-1]))
    cpulist = list(map(int, cpulist))
    myaverage = sum(cpulist) / float(length)
    print("Average Temperature: {:.2f}".format(myaverage))
    print("Max Tempertaure: {}".format(max(cpulist)))
    print("Min Tempertaure: {}".format(min(cpulist)))
    print("Number of temperature warnings: {}".format(my_warning_count))
    print("Number of data points: {}\n".format(length))

def importtest(text):
    """import print test statement"""
    pass
    # print(text)

# ===================== MAIN ===============================

if __name__ == '__main__':
    importtest("main")
else:
    importtest("Imported {}".format(__name__))

# ===================== END ===============================
