Overview
--------------------------------------------
* Name: rpi_tempmon 
* Title : Display the ARM CPU and GPU temperature of Raspberry Pi 2/3  
* Description: This python program will display the ARM CPU and 
GPU temperature of a Raspberry Pi 2/3 
features include GPIO (LED) output, logging, alarm limit, graphing and e-mailing options. 
The program is written in python 3. It is run in terminal and uses matplotlib 
plots for graph modes.
* Author: Gavin Lyons
* URL: https://github.com/gavinlyonsrepo/raspeberrypi_tempmon

Table of contents
---------------------------

  * [Overview](#overview)
  * [Table of contents](#table-of-contents)
  * [Installation](#installation)
  * [Usage](#usage)
  * [Files and setup](#files-and-setup)
  * [Output](#output)
  * [Optional dependencies](#optional-dependencies)
  * [Features](#features)
  * [See Also](#see-also)
  * [Communication](#communication)
  * [History](#history)
  * [Copyright](#copyright)

Installation
-----------------------------------------------

For Linux OS users.
Make sure that python3 and pip3 have been installed on your machine, then: 

```sh
sudo pip3 install rpi_tempmon.py
```

If you are an Arch linux OS user 
rpi_tempmon can be installed by PKGBUILD. 
The PKGBUILD file is available in the AUR - Arch user repository. 

    AUR package name :rpi_tempmon
    AUR maintainer : glyons
    AUR location: https://aur.archlinux.org/packages/rpi_tempmon/

Usage
-------------------------------------------
Program is a python 3 package. 


Run in a terminal by typing rpi_tempmon.py or python3 rpi_tempmon.py: 

rpi_tempmon.py -[options][arguments]

Options list (standalone cannot be combined):

| Option          | Description     |
| --------------- | --------------- |
| -h  | Print help information and exit |
| -v  | Print version information and exit |
| -c  | Enters continuous mode, optional number of seconds as a argument eg (-c 5)|
| -l  | Creates and/or appends to log file at output folder |
| -L  | Creates a sub-folder at output folder with date/time stamp and puts a log file in it |
| -m  | Sends the log file to an email account |
| -g  | Generate a graph of output of log file, graph mode 1 |
| -G  | Generates a graph of real time GPU data,  graph mode 2 |
| -a  | parse log file and produce a report |
| -n  | send notifications to desktop, Number argument to define behaviour |

Files and setup
-----------------------------------------
rpi_tempmon files needed are listed below:

| File Path | Description |
| ------ | ------ |
| rpi_tempmon.py | The main python script |
| RpiTempmonWork.py| python module containing work functions |
| RpiTempmonGraph.py | python module dealing with graph output by matplotlib |
| $HOME/.config/rpi_tempmon/rpi_tempmon.cfg | config file, user made, NOT installed |
| README.md | help file |


Config file: The user **MUST** create a config file at path in table above.
The config file is NOT installed by setup. A dummy config file is available in documentation folder at repositry
, used  for -m mail option, GPIO/LED feature and the alarm function. 

The sstmp setting in config file is created so the ssmtp config file can be kept 
secured from all but root account. 

The setting "RPI_AuthUser" the is email address 
destination of data from -m option. 
 
Mail_Alert(one: mail alert on with -l option, zero: off)

The other settings are ALARM_MODE which should be set to one or zero(one: alarm on, zero: off)

CPU_UPPERLIMIT is the temperature limit of CPU in Centigrade, should be a positive integer.
If alarm mode is on when CPU temperature  goes above this limit, the alarm function will activate. 

LED_MODE which should be set to one or zero(one: LED mode on, zero: off) if on 
an GPIO pin will swicth on during an alarm state in continuous and normal mode.
The RPI GPIO pin as defined by GPIO_LED number. You can connect an LED or another
electronic component to this pin.

A dummy config file is available in documentation folder.

Make sure to include the [MAIN] header and all settings just as below or from dummy file.

Settings:

[MAIN]
>
>RPI_AuthUser=examplemail@gmail.com
>
>MAIL_ALERT = 1
>
>ALARM_MODE = 1
>
>CPU_UPPERLIMIT = 60
>
>LED_MODE = 0
>
>GPIO_LED = 26
>



Output
-------------------------------------

The output folder for log files is currently fixed at: 

```sh
$HOME/.cache/rpi_tempmon/
```

Optional dependencies
-----------

1. sSMTP - Version: 2.64-8 - Simple SMTP

sSMTP is a simple MTA to deliver mail from a computer to a mail hub (SMTP server)
needed for -m mail option. This is optional. Install from OS repositories.


* Config:
To configure SSMTP, you will have to edit its configuration file 
(/etc/ssmtp/ssmtp.conf) and enter your account settings. see below link
https://wiki.archlinux.org/index.php/SSMTP
and remember to configure the rpi_tempmon.cfg as well, see files section.


2. matplotlib - Version: 2.2.2 - Python plotting package

The graph modules requires python module *matplotlib* to draw graphs,
This is for -g and -G options.
Install from OS repositories or use pip.

```sh
$ sudo pip3 install matplotlib
```

3. libnotify-bin - Version 0.7.6-2 - sends desktop notifications to a notification daemon 


```sh
sudo apt install libnotify-bin
```

This is needed if using the -n option which uses the notify-send command. 
Additional packages or steps 
**may** be required to get notify-send working,
depending on system. for example  
[Jessie](https://raspberrypi.stackexchange.com/questions/75299/how-to-get-notify-send-working-on-raspbian-jessie)


Features
----------------------

This software was tested ona rapsberry pi 3 model B, 
running Raspbian 8.0 jessie, LXDE lxpanel 0.7.2.

For a raspberry pi the official operating temperature limit is 85°C, 
and as a result the Raspberry Pi should start to thermally throttle 
performance around 82°C.

The program calculates the ARM CPU and GPU temperature of 
a Raspberry Pi and outputs them in Centigrade together with
datetime stamp.

The program has seven features
1. Normal mode - output to screen with optional GPIO output, prompt for update.
2. Continuous mode - output to screen with optional GPIO output, updates based on timer.
3. Logfile mode   - output to single logfile(also mail mode if mail alert mode on and triggered).
4. Logfolder mode - output to multiple logfile in separate folders.
5. Mail mode  - output to email.
6. Graph mode - Displays a graph of logfile created in mode 3
7. Graph mode 2 - Displays a graph of GPU data in realtime
8. Data mode - parses log file and produces a small report.
9. Notify mode - send notifications to desktop, Number argument to define behaviour 

**1. normal mode**

Normal mode is run by running program with no command line arguments.
In normal mode output, Data is sent to the terminal with prompt to repeat or quit. 
The GPIO pin in config file will be turned on 
and Data in red is displayed in screen for an Alarm state, if setup in config file.

**2. Continuous mode**

Same as 
In continuous mode entered by option -c, The program enters a delay between scan.
This delay is set by positive integer argument placed after -c. 
For example "-c 30" will wait 30 seconds between scans. 
Data is sent to terminal screen. 
The GPIO pin in config file will be turned on 
and Data in red is displayed in screen for an Alarm state, if  setup in config file. 
 
![ScreenShot cont mode](https://raw.githubusercontent.com/gavinlyonsrepo/raspberrypi_tempmon/master/screenshot/main_screen.jpg)
 
**3. & 4. Log  modes**
 
For mode 3 an email is sent using mode 5 function, 
but with warning in title.

In logfile mode the data is appended into a file log.txt at output folder. 
 With optional mail setup if alarm mode setup. Sample output of logfile:
 
```sh
Raspberry pi temperature monitor: raspberrypi
TS = 2017-08-20 14:29:21
GPU temperature = 52.6'C
CPU temperature = 53.5'C
Raspberry pi temperature monitor: raspberrypi
TS = 2017-08-20 14:48:00
GPU temperature = 56.9'C
CPU temperature = 57.5'C
Warning : cpu over the temperature limit: 55
```

The log file is appended with "Warning:" text if alarm state entered.

In logfolder mode in the output folder, a new sub-folder is created each
time it is ran and a new log-file put in here. The sub-folder has following syntax
1250-02Jul17_RPIT HHMM-DDMMMYY_XXXX. 
This folder mode does not work with mail or graph mode at present.

Logging modes are designed to be used with UNIX automation like crontab.
For example this crontab entry will run logfile mode once an hour, 
Note: The path to executable may differ on each users system.

```sh
0 * * * *  /usr/local/bin/rpi_tempmon.py -l
```

**5. Mail mode**

In mail mode an email is sent using ssmtp. 
The mail contains the data from logfile mode only it will not work with 
sub-folders from logfolder mode.
The user must install and configure the ssmtp program(see installation section)
Also the rpi_tempmon.cfg file mentioned above must be configured. 
This file allows for user to set an email without access to ssmtp
config file which should be set up just for root account.

**6. & 7. graph modes**

In graph mode one the program using matplotlib (plotting library) 
creates a plot of data of GPU and CPU versus time/date stamp
the logfile.txt created by logfile mode 3.

 
![graph mode 1](https://raw.githubusercontent.com/gavinlyonsrepo/raspberrypi_tempmon/master/screenshot/graphmode1.jpg)

In graph mode 2 the program  creates a plot of data of GPU 
versus realtime.

![graph mode 2](https://raw.githubusercontent.com/gavinlyonsrepo/raspberrypi_tempmon/master/screenshot/graphmode2.jpg)


**8. data mode**

Parses log file created by logfile mode 3 and produces a small data report.

**9. notify mode**

Send notifications to desktop, Numbered argument to define behaviour 

* -n 2 = argument 2 = If run always display CPU temperature 
* -n 3 = argument 3 = If run only display if CPU temperature exceeds limit

![notify mode](https://raw.githubusercontent.com/gavinlyonsrepo/raspberrypi_tempmon/master/screenshot/nyalarm.jpg)

See Also
-----------
README.md is at repository.
Screenshots and dummy config file are also available.

[SSMTP help](https://wiki.archlinux.org/index.php/SSMTP)

[matplotlib help](https://matplotlib.org/)

Communication
-----------
If you should find a bug or you have any other query, 
please send a report.
Pull requests, suggestions for improvements
and new features welcome.
* Contact: Upstream repo at github site below or glyons66@hotmail.com
* [Upstream repository](https://github.com/gavinlyonsrepo/raspberrypi_tempmon)

History
------------------

[Changelog is at repository in documentation section](Documentation/CHANGELOG.md)

Copyright
-------------
Copyright (C) 2017 - Gavin Lyons - GPLv3

[License is at repository in documentation section](Documentation/LICENSE.txt)


