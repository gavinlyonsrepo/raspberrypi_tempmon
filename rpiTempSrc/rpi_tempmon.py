#!/usr/bin/env python3
"""python script to display the ARM CPU and GPU temperature of Raspberry Pi 3"""
#=========================HEADER=======================================
# title             :rpi_tempmon.py
# description       :python script to display the ARM CPU and GPU temperature of Raspberry Pi 3
# author            :Gavin Lyons
# date              :17/08/2017
# version           :1.4-5
# web               :https://github.com/gavinlyonsrepo/raspeberrypi_tempmon
# mail              :glyons66@hotmail.com
# python_version    :3.6.0

#==========================IMPORTS======================
# Import the system modules needed to run rpi_tempmon.py.
import sys
import os
import datetime
import argparse
import configparser
import time
import socket #hostname

#my modules
from rpiTempMod import RpiTempmonWork as Work
from rpiTempMod import RpiTempmonGraph


#=======================GLOBALS=========================

#colours for printf
BLUE = '\033[94m'
GREEN = '\033[92m'
YELLOW = '\033[93m'
RED = '\033[91m'
BOLD = '\033[1m'
UNDERLINE = '\033[4m'
END = '\033[0m'

#set the path for logfile
DESTLOG = os.environ['HOME'] + "/.cache/rpi_tempmon"
if not os.path.exists(DESTLOG):
    os.makedirs(DESTLOG)

#set the path for config file
DESTCONFIG = os.environ['HOME'] + "/.config/rpi_tempmon"
if not os.path.exists(DESTCONFIG):
    os.makedirs(DESTCONFIG)
DESTCONFIG = DESTCONFIG + "/" + "rpi_tempmon.cfg"
if os.path.isfile(DESTCONFIG):
    pass
else:
    print("Config file is missing at {}".format(DESTCONFIG))
    print("See https://github.com/gavinlyonsrepo/raspeberrypi_tempmon or readme.md")
    quit()

#version
VERSION = "1.4"

#====================FUNCTION SECTION===============================


def msg_func(myprocess, mytext):
    """NAME : msg_func
    DESCRIPTION :prints to screen
    prints line, text and anykey prompts, yesno prompt
    INPUTS : $1 process name $2 text input
    PROCESS :[1]  print line [2] anykey prompt
    [3] print text  "green , red ,blue , norm yellow and highlight" [4] yn prompt,
    OUTPUT yesno prompt return 1 or 0"""

    mychoice = ""

    if myprocess == "line": #print blue horizontal line of =
        print(BLUE + "="*80 + END)

    if myprocess == "anykey":
        input("Press <Enter> to continue" + " " + mytext)

    if myprocess == "green": #print green text
        print(GREEN + mytext + END)

    if myprocess == "red": #print red text
        print(RED + mytext + END)

    if myprocess == "blue": #print blue text
        print(BLUE + mytext + END)

    if myprocess == "yellow": #print yellow text
        print(YELLOW + mytext + END)

    if myprocess == "bold": #print yellow text
        print(BOLD + mytext + END)

    if myprocess == "underline": #print yellow text
        print(UNDERLINE + mytext + END)

    if myprocess == "yesno": #yes no prompt loop
        while True:
            mychoice = input("Repeat ? [y/n]")
            if mychoice == "y":
                return  1
            elif mychoice == "n":
                return  0
            else:
                print(YELLOW +  "Please answer: y for yes OR n for no!" + END)


def exit_handler_func():
    """handle the program exit"""
    #print goodbye message
    msg_func("bold", "Goodbye")
    msg_func("anykey", " and exit.")
    #code to switch off the LED before shutdown
    myconfigfile1 = configparser.ConfigParser()
    myconfigfile1.read(DESTCONFIG)
    led_num1 = myconfigfile1.get("MAIN", "GPIO_LED")
    Work.led_toggle_func("off", led_num1)
    quit()

def process_cmd_arguments():
    """Function for processing command line arguments."""
    parser = argparse.ArgumentParser(description='Display the CPU & GPU temps of Raspberry Pi')
    parser.add_argument(
        '-v', help='Print rpi_tempmon version and quit',
        default=False, dest='version', action='store_true')

    parser.add_argument(
        '-l', help='Log file mode',
        default=False, dest='logfile', action='store_true')

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
        '-G', help='Draw a graph from realtime data',
        default=False, dest='graphlive', action='store_true')

    parser.add_argument(
        '-c', help='Continuous mode, + integer arg in secs for delay time',
        type=int, dest='cont')

    args = parser.parse_args()

    #check the args that don't need config file
    #display version
    if args.version:
        msg_func("bold", "rpi_tempmon " + VERSION)
        quit()
    if args.logfolder:
        #call log function pass L
        Work.logging_func("L", "0", "100", "X", DESTLOG)
        quit()

    return args

def main(args):
    """Function to hold main program loop, passed command line arguments"""
    scan_count = 0
    mygraph = RpiTempmonGraph.MatplotGraph("gavin")
    #read in configfile
    myconfigfile = configparser.ConfigParser()
    myconfigfile.read(DESTCONFIG)
    mailuser = myconfigfile.get("MAIN", "RPI_AuthUser")
    mail_alert = myconfigfile.get("MAIN", "MAIL_ALERT")
    alarm_mode = myconfigfile.get("MAIN", "ALARM_MODE")
    cpu_limit = myconfigfile.get("MAIN", "CPU_UPPERLIMIT")
    led_mode = myconfigfile.get("MAIN", "LED_MODE")
    led_num = myconfigfile.get("MAIN", "GPIO_LED")
    
    #check arguments list
    if args.logfile:
        #call log function pass l
        Work.logging_func("l", mail_alert, cpu_limit, mailuser, DESTLOG)
        return 0

    if args.mail:
        #mail mode
        Work.mail_func(" Mail mode ", mailuser, DESTLOG)
        return 0

    if args.graphlog:
        mygraph.graph_log_data(DESTLOG)
        return 0
    if args.graphlive:
        mygraph.graph_live_data()
        return 0
    #main loop
    try:
        while True:
        #clear screen
            os.system('clear')
            print()
            msg_func("line", "")
            today = datetime.datetime.today()
            print(today)
            print(socket.gethostname())
            msg_func("line", "")
            msg_func("green", "CPU temperature => " + Work.get_cpu_tempfunc() + ".0'C")
            msg_func("green", "GPU temperature => " + Work.get_gpu_tempfunc())
        
            delay = 5
            scan_count += 1
            msg_func("bold", "Number of scans: " + str(scan_count))
            #display alarm mode
            if alarm_mode == "1":
                msg_func("bold", "Alarm mode is on: " + cpu_limit)
                if Work.get_cpu_tempfunc() > cpu_limit:
                    #display led mode
                    msg_func("red", "Warning : cpu over the temperature limit:  " + cpu_limit)
                    if led_mode == "1":
                        msg_func("bold", "LED mode is on, GPIO pin selected: " + led_num)
                        Work.led_toggle_func("on", led_num)
            #check for continuous mode
            if args.cont:
                val = int(sys.argv[2])
                if val < 0:  # if not a positive int print message and ask for input again
                    print("Sorry, input must be a positive integer, try again")
                    quit()
                delay = sys.argv[2]
                msg_func("bold", "Continuous mode is on")
                msg_func("bold", "Sleep delay set to seconds: " + str(delay) + " Press CTRL+c to quit.")
                time.sleep(float(delay))
                os.system('clear')
            else:
                if msg_func("yesno", ""):
                    pass
                else:
                    Work.led_toggle_func("off", led_num)
                    exit_handler_func()
        
            #call led function off
            Work.led_toggle_func("off", led_num)
    except (KeyboardInterrupt):
        Work.led_toggle_func("off", led_num)
#=====================MAIN===============================
if __name__ == "__main__":
    try:
        exit(main(process_cmd_arguments()))
    except (KeyboardInterrupt, SystemExit):
        pass
#=====================END===============================
