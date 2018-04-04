Overview
--------------------------------------------
* Name: rpi_tempmon 
* Title : Display the ARM CPU and GPU temperature of Raspberry Pi 
* Description: This python program will display the ARM CPU and 
GPU temperature of a Raspberry Pi 2/3 
features include command line display, GPIO (LED) output, logging, alarm limit, 
graphing,  desktop notification and e-mailing options. 
The program is written in python 3. It is run in terminal and uses matplotlib 
plots for graph modes. This software was built and tested on a raspberry pi 3 model B, 
running Linux, Raspbian 8.0 jessie, LXDE lxpanel 0.7.2, Python 3.4.2.
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
| -g  | graph mode, Generate a menu where six types of graphs can be selected |
| -a  | parse log file and produces a data report in terminal |
| -n  | send notifications to desktop, Number argument to define behaviour |
| -s  | CSV mode , parses log.txt and converts it to log.csv,  CSV file |

Files and setup
-----------------------------------------
rpi_tempmon files needed are listed below:

| File Path | Description |
| ------ | ------ |
| rpi_tempmon.py | The main python script |
| RpiTempmonWork.py| python module containing various utility functions used by main |
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

NOTE: An example config file is available in documentation folder of 
this repo.

Make sure to include the [MAIN] header and all settings just as below or 
copy from example file.

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

Dependencies
-----------

Note:
Numbers 2 and 4 should already installed by setup.py when you install rpitempmon,
You should not have to install them.
Numbers 1 and 3 are optional dependencies, 
They will have to manually installed from linux repos 
you only need them for mailing and desktop notifications respectively. 

1. sSMTP - Version: 2.64-8 - Simple SMTP

sSMTP is a simple MTA to deliver mail from a computer to a mail hub (SMTP server)
needed for -m mail option. 

```sh
$ sudo apt install ssmtp
```

* Config:
To configure SSMTP, you will have to edit its configuration file 
(/etc/ssmtp/ssmtp.conf) and enter your account settings. see below link
https://wiki.archlinux.org/index.php/SSMTP
An example sstmp config file for gmail is in documentation folder.
and configure the rpi_tempmon.cfg as well, see files section.


2. matplotlib - Version: 2.2.2 - Python plotting package 

The graph modules requires python module *matplotlib* to draw graphs,
This is for -g and -G options.

```sh
$ sudo pip3 install matplotlib
```

3. libnotify-bin - Version 0.7.6-2 - sends desktop notifications to a notification daemon 


```sh
$ sudo apt install libnotify-bin
```

This is needed if using the -n option which uses the notify-send command. 
Additional packages or steps 
**may** be required to get notify-send working,
depending on system. for example  
[Jessie](https://raspberrypi.stackexchange.com/questions/75299/how-to-get-notify-send-working-on-raspbian-jessie)


4. psutil  - Version (2.1.1) -  Library for retrieving info on PC

```sh
$ sudo pip3 install psutil

# or

$ sudo apt install python3-psutil
```

Features
----------------------



For a raspberry pi the official operating temperature limit is 85°C, 
and as a result the Raspberry Pi should start to thermally throttle 
performance around 82°C. The GPU and CPU are closely correlated
to within a degree usually.

The program calculates the ARM CPU and GPU temperature of 
a Raspberry Pi and outputs them in Centigrade together with
datetime stamp. Also shows CPU , RAM memory usage .

The program has nine features
1. Normal mode - output to screen with optional GPIO output, prompt for update.
2. Continuous mode - output to screen with optional GPIO output, updates based on timer.
3. Logfile mode   - output to single logfile(also mail mode if mail alert mode on and triggered).
4. Logfolder mode - output to multiple logfile in separate folders.
5. Mail mode  - output to email.
6. Graph mode - Displays a graph of logfile created in mode 3
7. CSV mode - parses log.txt and converts it to log.csv for external use
8. Data mode - parses log file and produces a small report.
9. Notify mode - send notifications to desktop, Number argument to define behaviour 

**1. normal mode**

Normal mode is run by running program with no command line arguments.
In normal mode output, Data is sent to the terminal with prompt to repeat or quit. 
The GPIO pin in config file will be turned on 
and Data in red is displayed in screen for an Alarm state, if setup in config file.

**2. Continuous mode**

Same as normal mode except in continuous mode. The program enters a delay between scan.
This delay is set by positive integer argument placed after -c. 
For example "-c 30" will wait 30 seconds between scans. 
Data is sent to terminal screen. 
The GPIO pin in config file will be turned on 
and Data in red is displayed in screen for an Alarm state, if  setup in config file. 
 
![ScreenShot cont mode](https://raw.githubusercontent.com/gavinlyonsrepo/raspberrypi_tempmon/master/screenshots/main_screen.jpg)
 
**3. & 4. Log  modes**


In logfile mode the data is appended into a file log.txt at output folder. 
With optional mail setup if alarm mode setup. For mode 3 an email
is sent using mode 5 function, 
but with warning in title.
 
 Sample output of logfile:
 
```sh
TS = 18-04-04 09:46:51
GPU temperature = 60.7'C
CPU temperature = 61.5'C
Cpu usage = 25.8
RAM usage = 33.9
Swap usage = 11.6
Raspberry pi temperature monitor: raspberrypi 
```

The log file is appended with "Warning:" text message if alarm state entered.

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

**6. graph mode**

In graph mode, the program using matplotlib (plotting library) 
creates a plot of various data versus time.
Note: Will not work with log files containing data older than version 2.0.
The logfile.txt created by logfile mode 3 is used for data for graph 1-4.
The graphs 5-6 are live plots sampled every two seconds for 150 points,
so five minutes of live data.

1.  CPU and GPU Temperature versus Time-date
2.  CPU Temperature and CPU usage versus Time-date
3.  RAM and Swap memory usage versus Time-date
4.  CPU usage versus Time-date
5.  CPU usage versus live Time
6.  GPU Temperature versus live Time
 
Two sample graphs of six , screenshots of all six are in screenshot folder.

![graph mode 2](https://raw.githubusercontent.com/gavinlyonsrepo/raspberrypi_tempmon/master/screenshots/graphmode2.jpg)

![graph mode 5](https://raw.githubusercontent.com/gavinlyonsrepo/raspberrypi_tempmon/master/screenshots/graphmode5.jpg)

**7. csv convert**

New in Version 2.0. Run with -s on the CLI.
Parses log.txt and creates log.csv. 
Note: Will not work with log files containing data older than version 2.0.
This csv file can be then used by user in another app.
A comma-separated values (CSV) file is a delimited text file 
that uses a comma to separate values. This file can then be loaded by libreoffice calc
for example.

sample output = time-data, CPU temp, GPU temp, CPU usage , RAM usage , swap usage 

```sh
18-04-04 09:46:51,61.5,60.7,25.8,33.9,11.6
```

**8. data mode**

Parses log file created by logfile mode 3 and produces a small data report.

**9. notify mode**

Send notifications to desktop, Numbered argument to define behaviour 

* -n 2 = argument 2 = If run always display CPU temperature , no warning.
* -n 3 = argument 3 = If run only display if CPU temperature exceeds limit

![notify mode](https://raw.githubusercontent.com/gavinlyonsrepo/raspberrypi_tempmon/master/screenshots/nyalarm.jpg)

See Also
-----------
README.md is at repository.
Screenshots and dummy config files are also available.

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


