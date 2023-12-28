
"""
Module imported into rpi_tempmon contains various utility functions
Functions in this module
(1) csv convert : converts log.txt into log.csv
(2) notify_func : function to control notify-send alerts
(3) get_cpu_tempfunc: Return CPU temperature
(4) get_gpu_tempfunc: Return GPU temperature as a character string
(5) get_cpu_use: Return CPU usage using psutil
(6) get_ram_info: Return RAM usage using psutil
(7) get_swap_info: Return swap memory  usage using psutil
(8) led_toggle_func: functionto toggle a GPIO
(9) logging_func: sents log data to file
(10) mail_func: Sends mail via msmpt
(11) data_func: Function to parse log file also produce a Data report
(12) stress_func: Carry out stress test
(13) msg_func: Writes to console
"""
import os
import datetime
import csv
import time
import RPi.GPIO as GPIO
import psutil


def csv_convert(destlog):
    """ Function to convert log.txt to log.csv"""
    try:
        os.chdir(destlog)
        # Read in log.txt file
        cputemp = ""
        time_stamp = ""
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
                        time_stamp = line[5:-1]
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
                        output_writer.writerow([time_stamp, cputemp, gputemp, cpu, ram, swap])
            output_file.close()
        else:
            msg_func("red", "Error: Log file not found at {}".format(mylogpath))

    except Exception as error:
        msg_func("red", "Problem with csv convert function {}".format(error))
        msg_func("red", "Check that log file exists, is not corrupt")
        msg_func("red", "or created by a version pre-2.0-1 - {}".format(mylogpath))
    else:
        msg_func("bold", "Log File conversion from text to csv completed")


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
        msg_func("red", "Error invalid argument to -n option 2 or 3 only")


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
    res = os.popen('vcgencmd measure_temp').readline()
    return (res.replace("\n", "").replace("temp=", ""))


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
            mylogfile.write("EP = " + str(round(time.time(), 0)) + '\n')
            mylogfile.write("GPU temperature = " + get_gpu_tempfunc() + '\n')
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
        msg_func("red", "Problem with data logging convert function {}".format(error))
        msg_func("red", "Check that log file exists and is not corrupt ")
    else:
        msg_func("bold", "Logging function run completed")


def mail_func(sub, mailu, destlog):
    """Function sends mail via ssmpt ,
    passed subject line and mail account name and logfile"""
    try:
        os.chdir(destlog)
        if os.path.exists("log.txt"):
            # Command to send mail from bash
            os.system('echo "Datafile log.txt attached" > body.txt')
            os.system('mpack -s "raspberry-PI-temperature {}" -d body.txt log.txt {}'.format(sub, mailu))
        else:
            msg_func("red", "Error: log file is not there {}".format(destlog))
    except Exception as error:
        msg_func("red", "Error with mail send function {}".format(error))
        msg_func("red", "Check that log file exists {}".format(destlog))
        msg_func("red", "Check that network is up")
        msg_func("red", "ssmtp and the user is configured properly {}".format(mailu))
    else:
        msg_func("bold", "Mail send function completed")


def data_func(destlog, flag):
    """ Function to parse log file and produce a Data report
    also called from rpiTempmonGraph module when called
    from there exits before report build"""
    # parse logfile section
    # define lists to hold data from logfile
    timelist = []
    unixlist = []
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
                    if "EP" in line:
                        unixlist.append(line[5:-1])
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
            msg_func("red", "Error: Log file not found at {}".format(mypath))

        if flag:  # if called from graph module go back with data
            return timelist, unixlist, cpulist, gpulist, cpu_uselist, ramlist, swaplist
        # Report code section
        msg_func("bold", "\nRaspberry pi CPU GPU temperature monitor program")
        print("Data report on {} \n".format(mypath))
        print("Start temperature: {} Time: {}".format(cpulist[0], timelist[0]))
        length = len(cpulist)
        print("End temperature: {} Time: {}".format(cpulist[length-1], timelist[length-1]))
        print("Number of data points: {} \n".format(length))
        cpulist = list(map(int, cpulist))
        average_temp = sum(cpulist) / float(length)
        print("Average Temperature: {:.2f}".format(average_temp))
        print("Max Tempertaure: {}".format(max(cpulist)))
        print("Min Tempertaure: {}".format(min(cpulist)))
        print("Number of temperature warnings: {}\n".format(my_warning_count))

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
        msg_func("red", error)
        msg_func("red", "Error in data_func function")
    return


def stresstest(destlog, scancount):
    """ function to carry out stress test, creates a data csv file and
    optional graph"""
    # if not a positive int print message and ask for input again
    if int(scancount) < 2 or int(scancount) > 50:
        msg_func("red", "Error: input to -ST must be a positive integer 2-50")
        quit()

    try:
        yaxislist = []
        cpu_uselist = []
        cpulist = []

        # csv file
        os.chdir(destlog)
        mycsvpath = destlog + "/" + "stresslog.csv"
        output_file = open(mycsvpath, 'w', newline='')
        output_writer = csv.writer(output_file)
        print("RPi tempmon, CPU Stress Test:")
        # loop thru data for scancount carrying out cpu stress test
        if os.path.isfile(mycsvpath):
            for i in range(0, int(scancount)):
                yaxislist.append(i+1)
                cpu_temp = get_cpu_tempfunc()
                cpu_use = get_cpu_use()
                cpu_uselist.append(cpu_use)
                cpulist.append(cpu_temp)
                msg_func("bold", "Testrun: {}".format(i+1))
                # Sysbench stress test
                os.system('sysbench --test=cpu --cpu-max-prime=20000 --num-threads=4 run >/dev/null 2>&1')
                msg_func("bold", "CPU temp => {}'C".format(cpu_temp))
                msg_func("bold", "CPU usage => {}%".format(cpu_use))
                output_writer.writerow([i+1, cpu_temp, cpu_use])
            output_file.close()
            print("\ncsv file, stresslog.csv, created at {}".format(destlog))
        else:
            msg_func("red", "Error: Log file not found at {}".format(mycsvpath))
    except Exception as error:
        print("Problem with stress test function {}".format(error))
        quit()
    else:
        plotlabel1 = 'CPU temp'
        plotlabel2 = 'CPU usage'
        ylabel = 'CPU usage(%) / Temperature (degrees)'
        title = 'CPU temperature and usage , Stress Test results'
        return yaxislist, cpulist, cpu_uselist, plotlabel1, plotlabel2, ylabel, title


def msg_func(myprocess, mytext):
    """NAME : msg_func
    DESCRIPTION :prints to screen
    prints line, text and anykey prompts, yesno prompt
    INPUTS : $1 process name $2 text input
    PROCESS :[1]  print line [2] anykey prompt
    [3] print text  "green , red ,blue , norm yellow and highlight"
     [4] yn prompt,
    OUTPUT yesno prompt return 1 or 0"""

    # colours for printf
    blue = '\033[96m'
    green = '\033[92m'
    yellow = '\033[93m'
    red = '\033[91m'
    bold = '\033[1m'
    end = '\033[0m'
    mychoice = ""

    if myprocess == "line":  # print blue horizontal line of =
        print(blue + "="*80 + end)

    if myprocess == "anykey":
        input("Press <Enter> to continue" + " " + mytext)

    if myprocess == "green":  # print green text
        print(green + mytext + end)

    if myprocess == "red":  # print red text
        print(red + mytext + end)

    if myprocess == "blue":  # print blue text
        print(blue + mytext + end)

    if myprocess == "yellow":  # print yellow text
        print(yellow + mytext + end)

    if myprocess == "bold":  # print bold text
        print(bold + mytext + end)

    if myprocess == "yesno":  # yes no prompt loop
        while True:
            mychoice = input("Repeat ? [y/n]")
            if mychoice == "y":
                choice = 1
                return choice
            elif mychoice == "n":
                choice = 0
                return choice
            else:
                print(yellow + "Please answer: y for yes OR n for no!" + end)

    return 2


def importtest(text):
    """import print test statement"""
    # print(text)
    pass
# ===================== MAIN ===============================


if __name__ == '__main__':
    importtest("main")
else:
    importtest("Imported {}".format(__name__))

# ===================== END ===============================
