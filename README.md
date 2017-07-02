Overview
--------------------------------------------
* Name: rpi_tempmon
* Title : Display the ARM CPU and GPU temperature of Raspberry Pi 2/3  
* Description: This bash script will display the ARM CPU and 
GPU temperature of Raspberry Pi 2/3 
includes logging and mailing options. 
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

* Download and extract files from repository.
* Copy the script file to an executable path for example 

```sh 
sudo cp /home/pi/Downloads/rpi_tempmon.sh /usr/local/bin
```

* Give it permission to run as script 

```sh
sudo chmod u+x /usr/local/bin/raspberrypi_tempmon
```

Usage
-------------------------------------------
Program is a terminal application.

Run in a terminal by typing rpi_tempmon.sh: 

rpi_tempmon.sh -[options][arguments]

Options list (standalone cannot be combined):

| Option          | Description     |
| --------------- | --------------- |
| -h  | Print help information and exit |
| -v  | Print version information and exit |
| -c  | enters continuous mode, optional number of seconds as a argument|
| -l  | creates and/or appends to log-file at output folder |
| -L  | creates a sub-folder at output folder with date/time stamp and puts a log file in it |
| -m  | sends the output of -l to an email account |

Files and setup
-----------------------------------------
rpi_tempmon files needed are listed below:

| File Path | Description |
| ------ | ------ |
| /usr/bin/local/rpi_tempmon.sh | The  shell script |
| $HOME/.config/rpi_tempmon/rpi_tempmon.cfg | config file, optional, user made, not installed |

Config file: The user can create an optional config file, used  
for -m option. The config file is created so the ssmtp config file can be kept 
secured from all but root account. it contains one setting the email address for 
which is the destination of -m option.

>
>RPI_AuthUser=examplemail@gmail.com
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
needed for -m mail option. This is optional.

Features
----------------------

The program calculates the ARM CPU and GPU temperature of 
a Raspberry Pi 2/3 and outputs them in Centigrade together with
datetime stamp.

The program has five features
1. Normal mode - output to screen
2. Continous mode - output to screen
3. logfile mode   - outut to logfile
4. logfolder mode - output to logfile
5. mail mode  - output to email

In normal mode output, Data is sent to the terminal with option to repeat or quit

In continues mode entered by option -c, The program enters a delay between 
each display as a default this is set to 5 seconds by entered a number argument after -c 
this can be adjusted for example "-c 60" will wait 60 seconds between scans. 
Data is sent to terminal screen.
 
In logfile mode the data is appended into a file log.txt at output folder

In logfolder mode in the output folder, a new sub-folder is created each
time it is ran and the log-file put in here. The sub-folder has following syntax
1250-02Jul17_RPIT HHMM-DDMMMYY_XXXX

In mail mode a email is sent using ssmtp
The mail contains the data from logfile mode only it will not work with 
sub-folders from logfolder mode.
The user most install and configure the ssmtp program. 
Also the rpi_tempmon.cfg file mentioned above must be configured
this file allows for user to set an email without access to ssmtp
config file which should be set up just for root account 

* Install:
```sh
sudo apt-get install ssmtp
```

* Config:
To configure SSMTP, you will have to edit its configuration file 
(/etc/ssmtp/ssmtp.conf) and enter your account settings. see below link
https://wiki.archlinux.org/index.php/SSMTP
and remember to config the rpi_tempmon.cfg  as well

See Also
-----------
README.md is at repository.

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
