'''script to display graph of data produced in log.txt by rpi_tempmon.sh'''

import matplotlib.pyplot as plt
import matplotlib.dates as md
import dateutil
import os


__author__ = "Gavin Lyons"
__copyright__ = "Copyright 2017, Gavin Lyons"
__credits__ = ["Gavin Lyons"]
__licence__ = "GPL"
__version__ = "1.3"
__maintainer__ = "Gavin Lyons"
__status__ = "Production"

timelist = []
cpulist =[]
gpulist = []

#get data from file and put into lists 
mypath = os.environ['HOME'] + "/.cache/rpi_tempmon/log.txt"
with open(mypath, 'r') as f:
	for line in f:
		#if "EPOCH" in line:
		#	timelist.append(line[8:-1])
		if "TS" in line:
			timelist.append(line[5:-1])
		if "CPU" in line:
			cpulist.append(line[18:20])
		if "GPU" in line:
			gpulist.append(line[18:20])
			

#parse dates format
dates = [dateutil.parser.parse(s) for s in timelist]

#make graph matplotlib
plt.xticks( rotation=25 )
plt.subplots_adjust(bottom=0.2)
ax=plt.gca()
ax.set_xticks(dates)
xfmt = md.DateFormatter('%m/%d %H:%M')
ax.xaxis.set_major_formatter(xfmt)
ax.xaxis.label.set_color('red')
ax.yaxis.label.set_color('red')
plt.plot(dates,cpulist, label = 'CPU', color = 'green', marker = 'x')
plt.plot(dates, gpulist, label = 'GPU', marker = '*')
plt.xlabel('Date time stamp (DD-MM HH:MM)')
plt.ylabel('Temperature (degrees)')
plt.title('ARM CPU and GPU temperature of Raspberry Pi 3', color = 'green')
plt.legend(loc='upper center', bbox_to_anchor=(0.5, 1),
          fancybox=True, shadow=True, ncol=5)
plt.grid(True)
plt.show()



				
