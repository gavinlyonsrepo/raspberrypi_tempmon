#!/usr/bin/env python3
"""
# ========================HEADER=======================================
# title             :rpi_tempmon.py
# description       :python script to display the CPU & GPU temp of RPi
# author            :Gavin Lyons
# intial date       :17/08/2017
# web url           :https://github.com/gavinlyonsrepo/raspberrypi_tempmon
# mail              :glyons66@hotmail.com
# python version    :3.4.2
# Functions:
(1) exit_handler_func: exit handler function
(2) stresstest_func: stresstest function
(3) process_cmd_arguments: process command line arguments
(4) print_title_func: prints title to console
(5) read_configfile_func: read in config file
(6) alarm_mode_check: checks for alarm condition
(7) cont_mode_check: checks for continuous mode
(8) main: main program loop
"""
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
# metadata
__VERSION__ = "2.1"
__URL__ = "https://github.com/gavinlyonsrepo/raspberrypi_tempmon"

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
    print("User must create a config file, See url:-")
    print("Example config file and info can be found at")
    print(__URL__)
    quit()


# ===================FUNCTION SECTION===============================


def exit_handler_func(led_num):
    """Handle the program exit"""
    # code to switch off the LED before shutdown
    if not led_num == 0:
        Work.led_toggle_func("off", led_num)
    # Print exit message
    print("\nGoodbye " + os.environ['USER'])
    Work.msg_func("bold", "Endex")
    quit()


def stresstest_func(testrun_count):
    """Call stresstest  function and display stress test graph choice"""
    print(DESTLOG)
    yaxislist, cpulist, cpu_uselist, plotlabel1, \
        plotlabel2, ylabel, title = Work.stresstest(DESTLOG, testrun_count)
    mychoice = input("\nDo you want to view graph of stress test? [y/N]")
    if (mychoice == "y") or (mychoice == "Y"):
        mygraph = RpiTempmonGraph.MatplotGraph("RPi Tempmon :")
        mygraph.draw_graph(yaxislist, cpulist, cpu_uselist,
                           plotlabel1, plotlabel2, ylabel, title)


def process_cmd_arguments():
    """Function for processing CL arguments
    return tuple of 4 values to main"""
    str_desc = "URL help at: {}".format(__URL__)
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

    parser.add_argument(
        '-ST', help='Stress test mode, + integer arg for number of runs',
        type=int, dest='stresstest')

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

    if args.stresstest:
        stresstest_func(sys.argv[2])

    if args.version:
        Work.msg_func("bold", "\nVersion : rpi_tempmon " + __VERSION__)

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
        mygraph = RpiTempmonGraph.MatplotGraph("RPi Tempmon :")
        mygraph.graph_log_data(DESTLOG)

    exit_handler_func(0)


def print_title_func():
    """Function to print title in normal and cont mode"""
    os.system('clear')
    print()
    Work.msg_func("line", "")
    today = datetime.datetime.now().strftime("%y-%m-%d %H:%M:%S")
    Work.msg_func("bold", "Raspberry pi CPU GPU temperature monitor program")
    print(today)
    print(socket.gethostname())
    Work.msg_func("line", "")
    Work.msg_func("green", "CPU temp => {}'C".format(Work.get_cpu_tempfunc()))
    Work.msg_func("green", "GPU temp => {}".format(Work.get_gpu_tempfunc()))
    Work.msg_func("green", "CPU usage => {}%".format(Work.get_cpu_use()))
    Work.msg_func("green", "RAM usage => {}%".format(Work.get_ram_info()))
    Work.msg_func("green", "Swap usage => {}% \n".format(Work.get_swap_info()))


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
            Work.msg_func("red", "  ERROR : ")
            print("CPU_UPPERLIMIT must be between 1 and 99")
            quit()
        config_file_data = (mailuser, mail_alert, alarm_mode, cpu_limit, led_mode, led_num)
    except Exception as error:
        Work.msg_func("red", "  ERROR : ")
        print("Problem with config file: {}".format(error))
        print("Must have section header of [MAIN] and six parameters")
        print("Help and exmaple file at url")
        print(__URL__)
        exit_handler_func(0)

    return config_file_data


def alarm_mode_check(config_file_data_main):
    """function to check alarm mode """
    alarm_mode, cpu_limit, led_mode, led_num = config_file_data_main
    if alarm_mode == "1":
        Work.msg_func("bold", "Alarm mode is on: " + cpu_limit)
        if Work.get_cpu_tempfunc() > cpu_limit:
            # display led mode
            Work.msg_func("red", "Warning : cpu over the temperature limit: " + cpu_limit)
            if led_mode == "1":
                Work.msg_func("bold", "LED mode is on, GPIO pin selected: " + led_num)
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
            Work.msg_func("bold", "Continuous mode is on.")
            Work.msg_func("bold", "Sleep delay set to seconds: " + str(delay))
            Work.msg_func("bold", "Press CTRL+c to quit.")
            time.sleep(float(delay))
            os.system('clear')
    else:  # normal mode prompt
        if Work.msg_func("yesno", ""):
            pass
        else:
            exit_handler_func(led_num)


def main(config_file_data_main):
    """Function to hold main program loop, config file data tuple"""

    # unpack config file data main tuple
    alarm_mode, cpu_limit, led_mode, led_num = config_file_data_main

    scan_count = 0
    # main loop
    try:
        while True:
            print_title_func()
            scan_count += 1
            Work.msg_func("bold", "Number of scans: " + str(scan_count))
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
        print("\nRPi temperature monitor:")
        exit(main(process_cmd_arguments()))
    except (KeyboardInterrupt, SystemExit):
        pass
# ====================END===============================
