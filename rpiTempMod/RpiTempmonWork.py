
"""
module imported into rpi_tempmon contains functions related to mail option
logging options, toggling GPIO LED and getting Rpi CPU and GPU information.
"""
import os
import datetime
import csv
import time
import RPi.GPIO as GPIO
import psutil


def csv_convert(destlog):
    """ Function to convert log to csv"""
    try:
        os.chdir(destlog)
        # Read in log.txt file
        cputemp = ""
        time = ""
        gputemp = ""
        cpu = ""
        ram = ""
        swap = ""

        # csv file
        mycsvpath = destlog + "/" + "log.csv"
        output_file = open(mycsvpath, 'w', newline='')
        output_writer = csv.writer(output_file)

        # get data from file and put into csv file
        mylogpath = destlog + "/" + "log.txt"
        if os.path.isfile(mylogpath):
            with open(mylogpath, 'r') as myfile:
                for line in myfile:
                    if "TS" in line:
                        time = line[5:-1]
                    if "CPU" in line:
                        cputemp = line[18:22]
                    if "GPU" in line:
                        gputemp = line[18:22]
                    if "Cpu" in line:
                        cpu = line[12:16]
                    if "RAM" in line:
                        ram = line[12:16]
                    if "Swap" in line:
                        swap = line[13:17]
                    if "Raspberry" in line:
                        output_writer.writerow([time, cputemp, gputemp, cpu, ram, swap])
            output_file.close()
        else:
            print("Error: Log file not found at {}".format(mylogpath))

    except Exception as error:
        print("Problem with csv convert function {}".format(error))
        print("Check that log file exists, is not corrupt")
        print("or created by a version pre-2.0-1 - {}".format(mylogpath))


def notify_func(cli_arg_2, cpu_limit):
    """ function to control notify-send alerts, passed in second command line argument"""
    title = "rpi_tempmon"
    message = ""

    if cli_arg_2 == "2":
        # send notify always
        message = "CPU temperature => " + get_cpu_tempfunc() + "'C"
        os.system('notify-send "{}" "{}"'.format(title, message))
    elif cli_arg_2 == "3":
        # send notify if cpulimit exceed)
        if get_cpu_tempfunc() > cpu_limit:
            message = "ALARM : CPU temp  => {}'C : Limit at {}'C"\
                .format(get_cpu_tempfunc(), cpu_limit)
            os.system('notify-send "{}" "{}"'.format(title, message))
    else:
        print("Error invalid argument to -n option 2 or 3 only")


def get_cpu_tempfunc():
    """ Return CPU temperature """
    result = 0
    mypath = "/sys/class/thermal/thermal_zone0/temp"
    with open(mypath, 'r') as mytmpfile:
        for line in mytmpfile:
            result = line
    
    result = float(result)/1000
    result = round(result, 1)
    return str(result)


def get_gpu_tempfunc():
    """ Return GPU temperature as a character string"""
    res = os.popen('/opt/vc/bin/vcgencmd measure_temp').readline()
    return res.replace("temp=", "")


def get_cpu_use():
    """ Return CPU usage using psutil"""
    cpu_cent = psutil.cpu_percent()
    return str(cpu_cent)


def get_ram_info():
    """ Return RAM usage using psutil """
    ram_cent = psutil.virtual_memory()[2]
    return str(ram_cent)


def get_swap_info():
    """ Return swap memory  usage using psutil """
    swap_cent = psutil.swap_memory()[3]
    return str(swap_cent)


def led_toggle_func(mode, led):
    """ led_toggle_func , function
    to toggle a GPIO LED, passed mode on/off
    and GPIO pin of LED"""
    led = int(led)
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    GPIO.setup(led, GPIO.OUT)
    time.sleep(.05)  # gpio init
    if mode == "off":
        GPIO.output(led, False)
    else:
        GPIO.output(led, True)


def logging_func(choice, mail_alert, cpu_limit, mailuser, destlog, alarm_mode):
    """ Function to log temps data to file,
     passed choice(args parameter which called it
    and 3 options from config file and path to log file"""
    try:
        if choice == "l":
            os.chdir(destlog)
        else:
            # Makes a directory with time/date stamp and enters it
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
            mylogfile.write("TS = " + str(today) + '\n')
            mylogfile.write("GPU temperature = " + get_gpu_tempfunc())
            mylogfile.write("CPU temperature = " + get_cpu_tempfunc() + '\n')
            mylogfile.write("Cpu usage = " + get_cpu_use() + '\n')
            mylogfile.write("RAM usage = " + get_ram_info() + '\n')
            mylogfile.write("Swap usage = " + get_swap_info() + '\n')
            mylogfile.write("Raspberry pi temperature monitor: raspberrypi \n")
            # Add alarm message to log
            if (alarm_mode == "1") and get_cpu_tempfunc() > cpu_limit:
                mylogfile.write("Warning : cpu over the temperature limit: "
                                + cpu_limit + '\n')
        # Send log by mail
        if (choice == "l") and (mail_alert == "1"):
            if (alarm_mode == "1") and get_cpu_tempfunc() > cpu_limit:
                mail_func(" Warning ", mailuser, destlog)
    except Exception as error:
        print("Problem with data logging convert function {}".format(error))
        print("Check that log file exists and is not corrupt ")


def mail_func(sub, mailu, destlog):
    """Function sends mail via ssmpt ,
    passed subject line and mail account name and logfile"""
    try:
        os.chdir(destlog)
        if os.path.exists("log.txt"):
            # Command to send mail by ssmpt from bash
            os.system('echo "Datafile log.txt attached" | mail -s "raspberry-PI-temperature {}  " -a {} {}'.format(sub, "log.txt", mailu))
    except Exception as error:
        print("Problem with mail send function {}".format(error))
        print("Check that log file exists {}".format(destlog))
        print("Check that network is up")
        print("ssmtp and the user is configured properly {}".format(mailu))


def data_func(destlog, flag):
    """ Function to parse log file and produce a Data report
    also called from rpiTempmonGraph module when called
    from there exits before report build"""
    # parse logfile section
    # define lists to hold data from logfile
    timelist = []
    cpulist = []
    gpulist = []
    cpu_uselist = []
    ramlist = []
    swaplist = []
    my_warning_count = 0

    try:
        # get data from file and put into lists
        mypath = destlog + "/" + "log.txt"
        if os.path.isfile(mypath):
            with open(mypath, 'r') as myfile:
                for line in myfile:
                    if "TS" in line:
                        timelist.append(line[5:-1])
                    if "CPU" in line:
                        cpulist.append(line[18:20])
                    if "GPU" in line:
                        gpulist.append(line[18:20])
                    if "Cpu" in line:
                        cpu_uselist.append(line[12:16])
                    if "RAM" in line:
                        ramlist.append(line[12:16])
                    if "Swap" in line:
                        swaplist.append(line[13:17])
                    if "Warning" in line:
                        my_warning_count += 1
        else:
            print("Error: Log file not found at {}".format(mypath))

        if flag:  # if called from graph module go back with data
            return timelist, cpulist, gpulist, cpu_uselist, ramlist, swaplist

        # Report code section
        print("\nRaspberry pi CPU GPU temperature monitor program")
        print("Data report on {} \n".format(mypath))
        print("Start temperature: {} Time: {}".format(cpulist[0], timelist[0]))
        length = len(cpulist)
        print("End temperature: {} Time: {}".format(cpulist[length-1], timelist[length-1]))
        cpulist = list(map(int, cpulist))
        average_temp = sum(cpulist) / float(length)
        print("Average Temperature: {:.2f}".format(average_temp))
        print("Max Tempertaure: {}".format(max(cpulist)))
        print("Min Tempertaure: {}".format(min(cpulist)))
        print("Number of temperature warnings: {}".format(my_warning_count))
        print("Number of data points: {} \n".format(length))
        cpu_uselist = list(map(float, cpu_uselist))
        average_use = sum(cpu_uselist) / float(length)
        print("Average Cpu usage: {:.2f}".format(average_use))
        print("Max Cpu usage: {}".format(max(cpu_uselist)))
        print("Min Cpu usage: {} \n".format(min(cpu_uselist)))
        ramlist = list(map(float, ramlist))
        average_use = sum(ramlist) / float(length)
        print("Average RAM usage: {:.2f}".format(average_use))
        print("Max RAM usage: {}".format(max(ramlist)))
        print("Min RAM usage: {}".format(min(ramlist)))
    except Exception as error:
        print(error)
    return


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
