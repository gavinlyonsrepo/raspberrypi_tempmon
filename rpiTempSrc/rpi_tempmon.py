#!/usr/bin/env python3
"""python script to display the CPU &  GPU temperature of Raspberry Pi """
# ========================HEADER=======================================
# title             :rpi_tempmon.py
# description       :python script to display the CPU & GPU temp of RPi
# author            :Gavin Lyons
# intial date       :17/08/2017
# version           :2.0-1
# web               :https://github.com/gavinlyonsrepo/raspeberrypi_tempmon
# mail              :glyons66@hotmail.com
# python version    :3.4.2

# =========================IMPORTS======================
# Import the system modules needed to run rpi_tempmon.py.
import sys
import os
import datetime
import argparse
import configparser
import time
import socket  # For hostname

# my modules
from rpiTempMod import RpiTempmonWork as Work
from rpiTempMod import RpiTempmonGraph


# =======================GLOBALS=========================

# set the path for logfile
DESTLOG = os.environ['HOME'] + "/.cache/rpi_tempmon"
if not os.path.exists(DESTLOG):
    os.makedirs(DESTLOG)

# set the path for config file
DESTCONFIG = os.environ['HOME'] + "/.config/rpi_tempmon"
if not os.path.exists(DESTCONFIG):
    os.makedirs(DESTCONFIG)
DESTCONFIG = DESTCONFIG + "/" + "rpi_tempmon.cfg"
if os.path.isfile(DESTCONFIG):
    pass
else:
    print("Config file is missing at {}".format(DESTCONFIG))
    print("User must create a config file see url:-")
    print("https://github.com/gavinlyonsrepo/raspeberrypi_tempmon")
    quit()

# Version
VERSION = "2.0"

# ===================FUNCTION SECTION===============================


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
    blue = '\033[94m'
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


def exit_handler_func(led_num):
    """Handle the program exit"""
    msg_func("bold", "\nGoodbye " + os.environ['USER'])
    msg_func("anykey", " and exit.")
    # code to switch off the LED before shutdown
    Work.led_toggle_func("off", led_num)
    quit()


def process_cmd_arguments():
    """Function for processing CL arguments
    return tuple of 4 values to main"""
    str_desc = 'Display the CPU & GPU temps of Raspberry Pi'
    parser = argparse.ArgumentParser(description=str_desc)
    parser.add_argument(
        '-v', help='Print rpi_tempmon version and quit',
        default=False, dest='version', action='store_true')

    parser.add_argument(
        '-l', help='Log file mode',
        default=False, dest='logfile', action='store_true')

    parser.add_argument(
        '-s', help=' convert Log file to csv',
        default=False, dest='csv_convert', action='store_true')

    parser.add_argument(
        '-L', help='Log folder mode',
        default=False, dest='logfolder', action='store_true')

    parser.add_argument(
        '-m', help='Send email mode with ssmtp',
        default=False, dest='mail', action='store_true')

    parser.add_argument(
        '-g', help='Draw a graph from log file data',
        default=False, dest='graphlog', action='store_true')

    parser.add_argument(
        '-c', help='Continuous mode, + integer arg in secs for delay time',
        type=int, dest='cont')

    parser.add_argument(
        '-a', help='Analysis the log file and report',
        default=False, dest='data', action='store_true')

    parser.add_argument('-n', help='notify mode +int arg, 2=notify always ,\
    3=notify only on Cpu limit exceed', type=int, dest='notify')

    args = parser.parse_args()

    # read config file
    config_file_data = read_configfile_func()
    # unpack tuple with values
    mailuser, mail_alert, alarm_mode, cpu_limit, led_mode, led_num = config_file_data
    # pack a new tuple for main
    config_file_data_main = config_file_data[2:6]

    # check the args
    if not len(sys.argv) > 1:
        # no argument > back to main
        return config_file_data_main

    if args.cont:
        # cont mode > back to main
        return config_file_data_main

    if args.version:
        msg_func("bold", "rpi_tempmon " + VERSION)

    if args.csv_convert:
        Work.csv_convert(DESTLOG)

    if args.logfolder:
        # call log function pass L for folder
        Work.logging_func("L", "0", "100", "X", DESTLOG, False)

    if args.data:
        # call the data analysis function
        Work.data_func(DESTLOG, False)

    if args.logfile:
        # call log function pass l for file
        Work.logging_func("l", mail_alert, cpu_limit, mailuser, DESTLOG, alarm_mode)

    if args.notify:
        Work.notify_func(sys.argv[2], cpu_limit)

    if args.mail:
        # mail mode
        Work.mail_func(" Mail mode ", mailuser, DESTLOG)

    if args.graphlog:
        mygraph = RpiTempmonGraph.MatplotGraph("graphlog")
        mygraph.graph_log_data(DESTLOG)

    quit()


def print_title_func():
    """Function to print title in normal and cont mode"""
    os.system('clear')
    print()
    msg_func("line", "")
    today = datetime.datetime.now().strftime("%y-%m-%d %H:%M:%S")
    msg_func("bold", "Raspberry pi CPU GPU temperature monitor program")
    print(today)
    print(socket.gethostname())
    msg_func("line", "")
    msg_func("green", "CPU temp => {}'C".format(Work.get_cpu_tempfunc()))
    msg_func("green", "GPU temp => {}".format(Work.get_gpu_tempfunc()))
    msg_func("green", "CPU usage => {}%".format(Work.get_cpu_use()))
    msg_func("green", "RAM usage => {}%".format(Work.get_ram_info()))
    msg_func("green", "Swap usage => {}% \n".format(Work.get_swap_info()))


def read_configfile_func():
    """Read in configfile, return 6 values in a tuple"""
    try:
        myconfigfile = configparser.ConfigParser()
        myconfigfile.read(DESTCONFIG)
        mailuser = myconfigfile.get("MAIN", "RPI_AuthUser")
        mail_alert = myconfigfile.get("MAIN", "MAIL_ALERT")
        alarm_mode = myconfigfile.get("MAIN", "ALARM_MODE")
        cpu_limit = myconfigfile.get("MAIN", "CPU_UPPERLIMIT")
        led_mode = myconfigfile.get("MAIN", "LED_MODE")
        led_num = myconfigfile.get("MAIN", "GPIO_LED")
        if (int(cpu_limit) < 1) or (int(cpu_limit) > 99):
            msg_func("red", "  ERROR : ")
            print("CPU_UPPERLIMIT must be between 1 and 99")
            quit()
        config_file_data = (mailuser, mail_alert, alarm_mode, cpu_limit, led_mode, led_num)
    except Exception as error:
        msg_func("red", "  ERROR : ")
        print("Problem with config file: {}".format(error))
        print("\nhttps://github.com/gavinlyonsrepo/raspeberrypi_tempmon")
        print("Must have section header of [MAIN] and six parameters")
        quit()

    return config_file_data


def alarm_mode_check(config_file_data_main):
    """function to check alarm mode """
    alarm_mode, cpu_limit, led_mode, led_num = config_file_data_main
    if alarm_mode == "1":
        msg_func("bold", "Alarm mode is on: " + cpu_limit)
        if Work.get_cpu_tempfunc() > cpu_limit:
            # display led mode
            msg_func("red", "Warning : cpu over the temperature limit: " + cpu_limit)
            if led_mode == "1":
                msg_func("bold", "LED mode is on, GPIO pin selected: " + led_num)
                Work.led_toggle_func("on", led_num)


def cont_mode_check(led_num):
    """check for continuous mode """
    delay = 5
    # is their an argument?
    if len(sys.argv) > 1:
        # Was it -c?
        if sys.argv[1] == "-c":
            val = int(sys.argv[2])
            # if not a positive int print message and ask for input again
            if val < 0:
                print("Sorry, input to -c  must be a positive integer.")
                quit()
            delay = sys.argv[2]
            msg_func("bold", "Continuous mode is on.")
            msg_func("bold", "Sleep delay set to seconds: " + str(delay))
            msg_func("bold", "Press CTRL+c to quit.")
            time.sleep(float(delay))
            os.system('clear')
    else:  # normal mode prompt
        if msg_func("yesno", ""):
            pass
        else:
            exit_handler_func(led_num)


def main(config_file_data_main):
    """Function to hold main program loop, config file data tuple"""

    # unpack config file data main tuple
    # led_num = config_file_data_main[3]
    alarm_mode, cpu_limit, led_mode, led_num = config_file_data_main

    scan_count = 0
    # main loop
    try:
        while True:
            print_title_func()
            scan_count += 1
            msg_func("bold", "Number of scans: " + str(scan_count))
            # check for  alarm mode
            alarm_mode_check(config_file_data_main)
            # check for continuous mode
            cont_mode_check(led_num)
            # call led function off
            Work.led_toggle_func("off", led_num)
    except KeyboardInterrupt:
        exit_handler_func(led_num)


# =====================MAIN===============================
if __name__ == "__main__":
    try:
        exit(main(process_cmd_arguments()))
    except (KeyboardInterrupt, SystemExit):
        pass
# ====================END===============================
