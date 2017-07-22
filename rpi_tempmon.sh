#!/bin/bash
#=========================HEADER=======================================
# Script: rpi_tempmon.sh
# Purpose: Display the ARM CPU and GPU temperature of Raspberry Pi 3 
# logging and email output also.
# Author:Gavin Lyons under GPL v3.x+
# Date: 020317
# Repository: https://github.com/gavinlyonsrepo/raspeberrypi_tempmon

#=======================GLOBAL VARIABLES SETUP=========================
#Syntax: Global: UPPERCASE XXX , local: XXXVar. local Array: XXXArr

#colours for printf
RED=$(printf "\033[31;1m")
GREEN=$(printf "\033[32;1m")
BLUE=$(printf "\033[36;1m")
YELLOW=$(printf "\033[33;1m")
HL=$(printf "\033[42;1m")
NORMAL=$(printf "\033[0m") 

#set the path for optional logfile 
DESTLOG="$HOME/.cache/rpi_tempmon"
mkdir -p "$DESTLOG"

#set the path for optional configfile  
DESTCONFIG="$HOME/.config/rpi_tempmon"
mkdir -p "$DESTCONFIG"

#delay value default 5
DELAY="5"
declare -i COUNT=1

#====================FUNCTION SECTION===============================

#FUNCTION HEADER
# NAME : msgFunc
# DESCRIPTION :   prints to screen
#prints line, text and anykey prompts, yesno prompt
# INPUTS : $1 process name $2 text input
# PROCESS :[1]  print line [2] anykey prompt
# [3] print text  "green , red ,blue , norm yellow and highlight" [4] yn prompt, 
# OUTPUT yesno prompt return 1 or 0                       
function msgFunc
{
	case "$1" in 
	
		line) #print blue horizontal line of =
			printf '\033[36;1m%*s\n' "${COLUMNS:-$(tput cols)}" '' | tr ' ' =
			printf '%s' "${NORMAL}"
		;;
		anykey) #any key prompt, appends second text input to prompt
		    printf '%s' "${GREEN}" 
			read -n 1 -r -s -p "Press any key to continue $2"
			printf '%s\n' "${NORMAL}"
		;;
		
		#print passed text string
		green) printf '%s\n' "${GREEN}$2${NORMAL}" ;;
		red) printf '%s\n' "${RED}$2${NORMAL}" ;;
		blue) printf '%s\n' "${BLUE}$2${NORMAL}" ;;
		yellow)printf '%s\n' "${YELLOW}$2${NORMAL}" ;;
		highlight)printf '%s\n' "${HL}$2${NORMAL}" ;;
		norm) printf '%s\n' "${NORMAL}$2" ;;			
			
		yesno) #print yes no quit prompt
			local yesnoVar=""
			while true; do
				read -r yesnoVar
				case $yesnoVar in
					[Yy]*) return 0;;
					[Nn]*) return 1;;
					[Qq]*) exitHandlerFunc EXITOUT;;
					*) printf '%s\n' "${YELLOW}Please answer: (y/Y for yes) OR (n/N for no) OR (q/Q to quit)!${NORMAL}";;
				esac
			done
		;;
		*) printf '%s\n' "ERROR unknown input to msgFunc" ;;
	esac
}

#FUNCTION HEADER
# NAME : makeDirFunc
# DESCRIPTION :  makes a directory with time/date stamp and enters it
function makeDirFunc
{			cd "$DESTLOG" || exitHandlerFunc DESTLOG
			dirVar=$(date +%H%M-%d%b%y)"$1"
			mkdir -p "$dirVar"
			cd "$dirVar" || exitHandlerFunc DESTLOG2 "$dirVar"
}

#FUNCTION HEADER
# NAME :  exitHandlerFunc 
# DESCRIPTION: error handler deal with user 
#exits and paths not found errors 
function exitHandlerFunc
{
	#double square brackets without use of quotes on matching pattern 
	#for glob support
	if [[ "$1" = DEST* ]]
	then
		msgFunc red "Path not found to Destination directory"
	fi
	case "$1" in
			EXITOUT) 
				msgFunc norm "Goodbye $USER!"
				msgFunc anykey "and exit."
				exit 0;;
			DESTLOG) msgFunc red "$DESTLOG" ;;
			DESTLOG2) msgFunc red "$2" ;;
			DESTCONFIG) msgFunc red "$DESTCONFIG";;
			NONINT) msgFunc red "Integer expected, user entered non-integer, program exiting";;
			FILEERROR) msgFunc red "$2";;
			*) msgFunc yellow "Unknown input to error handler";;
	 esac
	msgFunc norm "Goodbye $USER!"
	msgFunc anykey "and exit."
	exit 1
}

#FUNCTION HEADER
# NAME :  checkinputFunc
# DESCRIPTION:CHECK INPUT OPTIONS from linux command line arguments passed to program on call
# INPUTS :  $1 user input option $2 from -c (number of seconds) to sleep between checks
function checkinputFunc
{
case "$1" in
	"");;
	-v)
		msgFunc norm " "
		msgFunc norm "*** rpi_tempmon ***"
		msgFunc norm "*** Version 1.0 ***" 
		exitHandlerFunc EXITOUT
	;;
	-h)
		msgFunc norm " "
		msgFunc norm "Usage: -l, -L, -v, -h, -c (number of seconds)"
		msgFunc norm "See README.md for details at webpage:"
		msgFunc norm "https://github.com/gavinlyonsrepo/raspberrypi_tempmon"
		exitHandlerFunc EXITOUT
	;;
	-l|-L)
		#L for DIR , l for a file
		if [ "$1" = "-L" ] 
		then
			makeDirFunc  _RPIT
		else
			cd "$DESTLOG" || exitHandlerFunc DESTLOG
		fi
		CPU=$(</sys/class/thermal/thermal_zone0/temp)
	    echo  "Raspberry pi temperature monitor" >> log.txt
		echo  "$(date) at  $(hostname)" >>log.txt
		echo  "GPU temperature => $(/opt/vc/bin/vcgencmd measure_temp | cut -d "=" -f 2)" >> log.txt
		echo  "CPU temperature => $((CPU/1000))'C" >> log.txt
		if [ "$ALARM_MODE" = "1" ] &&  [ "$1" = "-l" ] 
		then
			if ! AlarmFunc #if returns more than 0
			then
				echo "Warning : CPU over the temperature limit $CPU_UPPERLIMIT" >> log.txt
				mailFunc "Warning"
			fi 
		fi
		exit 0
	;;
	-c)
		#Continous mode delay set to $DELAY: press ctrl+c to quit" 
		#is there a number?
		if [ -n "$2" ] 
		then
			#check valid integer value
			if [[ "$2" = *[!0-9]* ]]; 
			then
				#not an integer
				exitHandlerFunc NONINT
			fi
			#Set to DELAY to it 
			DELAY="$2"
		fi
	;;	
	-m)
		mailFunc
		exit 0
	;;
	
	*)	
		msgFunc red  "Invalid option!"
		msgFunc norm "Usage: -l, -L, -v, -h, -c (number of seconds)"
		msgFunc norm "See README.md for details at webpage:"
		msgFunc norm "https://github.com/gavinlyonsrepo/raspberrypi_tempmon"
		exitHandlerFunc EXITOUT
	;;
esac	
}

#FUNCTION HEADER
# NAME : mailFunc
# DESCRIPTION : send mail
function 	mailFunc
{
	cd "$DESTLOG" || exitHandlerFunc DESTLOG
	if [ -e log.txt ] #log file exist?
	then
		 {
			echo Subject: raspberry-PI-temperature-"$1"
			find . -maxdepth 1  -type f -name "log.txt" -exec cat {} \;
			#alternative code# mpack -s raspberry_PI_temperature log.txt "$RPI_AuthUser" 
		 } | ssmtp "$RPI_AuthUser" 
	else
		exitHandlerFunc FILEERROR  "No log file available"
	fi
}

#FUNCTION HEADER
# NAME : mailFunc
# DESCRIPTION : check alarm limits CPU mail
function AlarmFunc
{
#check cpu
if [ "$((CPU/1000))" -lt "$CPU_UPPERLIMIT" ]
then 

	return 0 #alarm off
else
	return 1 #alarm on
fi 
}

#==================MAIN CODE====================================
#get config file
source "$DESTCONFIG/rpi_tempmon.cfg" || touch "$DESTCONFIG/rpi_tempmon.cfg"
#if a user input deal with user input options for user input options
if [ -n "$1" ] 
then
    checkinputFunc "$1" "$2"
fi
clear
#main loop
while true; do
	msgFunc norm " "
	CPU=$(</sys/class/thermal/thermal_zone0/temp)
	msgFunc green "$(date) @ $(hostname)"
	msgFunc line
	msgFunc norm "GPU temperature => $(/opt/vc/bin/vcgencmd measure_temp | cut -d "=" -f 2)"
	msgFunc norm "CPU temperature => $((CPU/1000))'C"
	msgFunc line
	msgFunc norm " "
	msgFunc norm "Number of scans $COUNT"
	((COUNT++))
	#check alarm function on?
	if [ "$ALARM_MODE" = "1" ]
	then
		if ! AlarmFunc #if returns more than 0
		then
			msgFunc red "Warning : CPU over the temperature limit $CPU_UPPERLIMIT"
		fi
	fi
	
	if [  -n "$1" ] #check for -c mode
	then
		msgFunc norm "Continuous mode is on"
		msgFunc norm "Sleep delay set to $DELAY seconds : Press CTRL+c to quit."
		sleep "$DELAY"
		clear
	else
		msgFunc norm " "
		printf "%s\n" "Repeat? [y/n/q]"
		if ! msgFunc yesno #if no then exit
		then
			exitHandlerFunc EXITOUT
		fi
		clear
	fi
	
done
#======================END==============================
