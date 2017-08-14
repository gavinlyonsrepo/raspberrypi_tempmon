Overview
--------------------------------------------
* Name: rpi_tempmon
* Title : Display the ARM CPU and GPU temperature of Raspberry Pi 2/3  
* Description: This bash script will display the ARM CPU and 
GPU temperature of Raspberry Pi 2/3 
includes GPIO LED output, logging, alarm limit, graph and e-mailing options. 
The main script is written in bash but it uses 
two python module for the GPIO LED function and for the graph function.
* Author: Gavin Lyons

Table of contents
---------------------------

  * [Overview](#overview)
  * [Table of contents](#table-of-contents)
  * [Installation](#installation)
  * [Usage](#usage)
  * [Files and setup](#files-and-setup)
  * [Output](#output)
  * [Dependencies](#dependencies)
  * [Features](#features)
  * [See Also](#see-also)
  * [Communication](#communication)
  * [History](#history)
  * [Copyright](#copyright)

Installation
-----------------------------------------------
rpi_tempmon is installed by copying script to an executable 
path at $PATH and making it executable.
 
If the user wants to use the optional GPIO LED function
they also must install a python script file for this.

If the user wants to use the optional log file graph function
they also must install a python script file for this. 

* Download and extract files from repository latest version released to downloads folder

* Copy the script file to an executable path for example 

```sh 
$ sudo cp $HOME/Downloads/raspberrypi_tempmon-1.3-4/src /usr/local/bin
```

* Give it executable permissions 

```sh
$ sudo chmod u+x /usr/local/bin/rpi_tempmon.sh
```

* Copy the python library files to following location if you wish to 
use LED and graph function. See file section for details.


```sh
$ sudo cp $HOME/Downloads/raspberrypi_tempmon-1.3-4/modules /usr/lib/rpi_tempmon
```

```sh
$ sudo cp $HOME/Downloads/raspberrypi_tempmon-1.3-4/modules  /usr/lib/rpi_tempmon
```

These may need executable permissions depending on your system.

```sh
$ sudo chmod u+x /usr/lib/rpi_tempmon/*
```

Usage
-------------------------------------------
Program is a bash terminal application which calls python modules 
for some functions.

Run in a terminal by typing rpi_tempmon.sh: 

rpi_tempmon.sh -[options][arguments]

Options list (standalone cannot be combined):

| Option          | Description     |
| --------------- | --------------- |
| -h  | Print help information and exit |
| -v  | Print version information and exit |
| -c  | Enters continuous mode, optional number of seconds as a argument eg (-c 2)|
| -l  | Creates and/or appends to log-file at output folder |
| -L  | Creates a sub-folder at output folder with date/time stamp and puts a log file in it |
| -m  | Sends the output of -l to an email account |
| -g  | Generate a graph of output of -l mode |

Files and setup
-----------------------------------------
rpi_tempmon files needed are listed below:

| File Path | Description |
| ------ | ------ |
| /usr/bin/local/rpi_tempmon.sh | The main shell script |
| /usr/lib/rpi_tempmon/rpi_tempmon_lib.py | python module LED_GPIO |
| /usr/lib/rpi_tempmon/rpi_tempmon_2_lib.py | python module graph generator |
| $HOME/.config/rpi_tempmon/rpi_tempmon.cfg | config file, optional, user made, not installed |

Config file: The user can create a  config file, used  
for -m mail option, LED feature and the alarm function. 
The sstmp setting in config file is created so the ssmtp config file can be kept 
secured from all but root account. The setting "RPI_AuthUser" the is email address 
 destination of data from -m option.
The other settings are ALARM_MODE which should be set to one or zero(one: alarm on, zero: off)
CPU_UPPERLIMIT is the temperature limit of CPU in Centigrade, should be a positive integer.
If alarm mode is on when CPU temperature  goes above this limit, the alarm function will activate. 
LED_MODE which should be set to one or zero(one: LED mode on, zero: off) if on 
an LED will light during an alarm state in continuous and normal mode.
The LED must be connected to a RPI GPIO pin as defined by GPIO_LED number.
At startup file is read by program, if it does not exist it creates a blank one.

A dummy config file is available in documentation folder.

Settings:

>
>RPI_AuthUser=examplemail@gmail.com
>
>ALARM_MODE=1
>
>CPU_UPPERLIMIT=60
>
>LED_MODE=0
>
>GPIO_LED=26
>


Output
-------------------------------------

The output folder for log files is fixed at 

```sh
$HOME/.cache/rpi_tempmon/
```

Dependencies
-----------
sSMTP - Simple SMTP

sSMTP is a simple MTA to deliver mail from a computer to a mail hub (SMTP server)
needed for -m mail option. This is optional. Install from repositories.

* Install:
```sh
$ sudo apt-get install ssmtp
```

* Config:
To configure SSMTP, you will have to edit its configuration file 
(/etc/ssmtp/ssmtp.conf) and enter your account settings. see below link
https://wiki.archlinux.org/index.php/SSMTP
and remember to configure the rpi_tempmon.cfg as well, see files section.

If user is using the python modules you must have python 3 installed.
Furthermore the graph modules requires matplotlib to draw graph
install as follows:

matplotlib -plotting library 

```sh
$ sudo apt-get install python-matplotlib
```


Features
----------------------

The program calculates the ARM CPU and GPU temperature of 
a Raspberry Pi 2/3 and outputs them in Centigrade together with
datetime stamp.

The program has six features
1. Normal mode - output to screen with optional LED output.
2. Continuous mode - output to screen with optional LED output.
3. Logfile mode   - output to single logfile(also mail mode if alarm mode on and triggered).
4. Logfolder mode - output to multiple logfile in separate folders.
5. Mail mode  - output to email.
6. Graph mode - Displays a graph of logfile created in mode 3


In normal mode output, Data is sent to the terminal with option to repeat or quit. 
A LED will light and Data in red is displayed in screen for an on Alarm state if setup.

In continuous mode entered by option -c, The program enters a delay between 
each display as a default this is set to 5 seconds by entered a number argument after -c 
this can be adjusted for example "-c 60" will wait 60 seconds between scans. 
Data is sent to terminal screen. A LED will light if for an on Alarm state if set.
If an alarm limit is on and triggered by CPU going above limit, 
data in red is displayed in screen.
 
For mode 3 an email is sent using mode 5 function, 
but with warning in title and the log file is appended with error text.

> "Warning : CPU over the temperature limit 10 "

In logfile mode the data is appended into a file log.txt at output folder. 
 With optional mail setup if alarm mode setup. Sample output of logfile:
 
```sh
Raspberry pi temperature monitor at  @hostname
TS = 2017-08-14-00:09:51 
EPOCH = 1502665791
GPU temperature = 56.9'C
CPU temperature = 56'C
```

In logfolder mode in the output folder, a new sub-folder is created each
time it is ran and a new log-file put in here. The sub-folder has following syntax
1250-02Jul17_RPIT HHMM-DDMMMYY_XXXX. 
This folder mode does not work with mail or graph mode at present.

Logging modes are designed to be used with UNIX automation like crontab.

In mail mode an email is sent using ssmtp. 
The mail contains the data from logfile mode only it will not work with 
sub-folders from logfolder mode.
The user must install and configure the ssmtp program(see installation section)
Also the rpi_tempmon.cfg file mentioned above must be configured. 
This file allows for user to set an email without access to ssmtp
config file which should be set up just for root account.

In graph mode the program calls a python function
and using matplotlib (plotting library) creates a plot of data of GPU and CPU verus time
from output of mode 3 the logfile.txt.

See Also
-----------
README.md is at repository.
Screenshots and dummy config file are also available.

Communication
-----------
If you should find a bug or you have any other query, 
please send a report.
Pull requests, suggestions for improvements
and new features welcome.
* Contact: Upstream repo at github site below or glyons66@hotmail.com
* Upstream repository: https://github.com/gavinlyonsrepo/raspberrypi_tempmon

History
------------------
CHANGELOG.md is at repository

Copyright
-------------
Copyright (C) 2017 Gavin Lyons 
This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public license published by
the Free Software Foundation, see LICENSE.md in documentation section 
for more details
