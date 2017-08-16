'''Script to display graph of data produced in log.txt
by rpi_tempmon.sh'''

import os
import matplotlib.pyplot as plt
import matplotlib.dates as md
import dateutil


__author__ = "Gavin Lyons"
__copyright__ = "Copyright 2017, Gavin Lyons"
__credits__ = ["Gavin Lyons"]
__licence__ = "GPL"
__version__ = "1.3"
__maintainer__ = "Gavin Lyons"
__status__ = "Production"

TIMELIST = []
CPULIST = []
GPULIST = []

#get data from file and put into lists
MYPATH = os.environ['HOME'] + "/.cache/rpi_tempmon/log.txt"
with open(MYPATH, 'r') as f:
    for line in f:
        if "TS" in line:
            TIMELIST.append(line[5:-1])
        if "CPU" in line:
            CPULIST.append(line[18:20])
        if "GPU" in line:
            GPULIST.append(line[18:20])


#parse dates format
DATES = [dateutil.parser.parse(s) for s in TIMELIST]

#make graph matplotlib
plt.xticks(rotation=25)
plt.subplots_adjust(bottom=0.2)
AX = plt.gca()
AX.set_xticks(DATES)
XFMT = md.DateFormatter('%m/%d %H:%M')
AX.xaxis.set_major_formatter(XFMT)
AX.xaxis.label.set_color('red')
AX.yaxis.label.set_color('red')
plt.plot(DATES, CPULIST, label='CPU', color='green', marker='x')
plt.plot(DATES, GPULIST, label='GPU', marker='*')
plt.xlabel('Date time stamp (DD-MM HH:MM)')
plt.ylabel('Temperature (degrees)')
plt.title('ARM CPU and GPU temperature of Raspberry Pi 3', color='green')
plt.legend(loc='upper center', bbox_to_anchor=(0.5, 1),
           fancybox=True, shadow=True, ncol=5)
plt.grid(True)
plt.show()
