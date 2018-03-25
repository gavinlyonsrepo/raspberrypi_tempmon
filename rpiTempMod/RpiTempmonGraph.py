#!/usr/bin/env python3
"""
module imported into rpi_tempmon contains functions related
containg a class with methods to display graphs from matlib
"""
import os
import matplotlib as mpl
mpl.use('tkagg')
import matplotlib.pyplot as plt
import matplotlib.dates as md
import dateutil



def plot_now_func(tempg):
    """called from method graph_live_data to draw graph"""
    plt.clf()
    # plt.ylim(15,90) # had to comment out after matplotlib upgrade
    plt.title('Raspberry Pi core temperture', color='green')
    plt.grid(True)
    plt.ylabel("Temperature ('C)", color='red')
    plt.xlabel("Time (last 25 seconds)", color='red')
    plt.plot(tempg, color='blue', marker='*', label="GPU")
    plt.legend(loc='upper right', fancybox=True, shadow=True)
    plt.show()

class MatplotGraph(object):
    """class with 2 methods to display graphs of pi CPU data with matplotlib"""
    def __init__(self, name):
        """docstring"""
        self.name = name


    def graph_log_data(self, destlog):
        """draw a  graph of pi GPU CPU from logdata"""
        #define lists to hold data from logfile
        timelist = []
        cpulist = []
        gpulist = []

        #get data from file and put into lists
        mypath = destlog + "/" + "log.txt"
        if os.path.isfile(mypath):
            with open(mypath, 'r') as myfile:
                for line in myfile:
                    if "TS" in line:
                        timelist.append(line[5:-1])
                    if "CPU" in line:
                        cpulist.append(line[18:20])
                    if "GPU" in line:
                        gpulist.append(line[18:20])
        else:
            print("Log file not found at {}".format(mypath))
            return 1
        # convert to ints as strings cause issue with graph in new matlib version
        cpulist = list(map(float, cpulist))
        gpulist = list(map(float, gpulist))
        # parse dates format
        mydates = [dateutil.parser.parse(s) for s in timelist]
        # make graph matplotlib from logfile
        cpulist = list(map(int, cpulist))
        gpulist = list(map(int, gpulist))
        plt.xticks(rotation=25)
        plt.subplots_adjust(bottom=0.2)
        axisx = plt.gca()
        axisx.set_xticks(mydates)
        xfmt = md.DateFormatter('%m/%d %H:%M')
        axisx.xaxis.set_major_formatter(xfmt)
        axisx.xaxis.label.set_color('red')
        axisx.yaxis.label.set_color('red')
        plt.plot(mydates, cpulist, label='CPU', color='green', marker='x')
        plt.plot(mydates, gpulist, label='GPU', marker='*')
        plt.xlabel('Date time stamp (DD-MM HH:MM)')
        plt.ylabel('Temperature (degrees)')
        plt.title('ARM CPU and GPU temperature of Raspberry Pi 3', color='green')
        plt.legend(loc='upper right',
                   fancybox=True, shadow=True)
        plt.grid(True)
        plt.show()

    def graph_live_data(self):
        """draw a live graph of pi GPU """
        tempg = []
        plt.ion()

        #pre-load dummy data
        for i in range(0, 26):
            tempg.append(35)

        while True:
            #GPU
            ostemp = os.popen('vcgencmd measure_temp').readline()
            temp = (ostemp.replace("temp=", "").replace("'C\n", ""))
            tempg.append(temp)
            tempg.pop(0)
            #plot graph pass function temp
            plot_now_func(tempg)
            plt.pause(1)

def importtest(text):
    """import print test statement"""
    pass
    # print(text)

# ===================== MAIN ===============================

if __name__ == '__main__':
    importtest("main")
else:
    importtest("Imported {}".format(__name__))

# ===================== END ===============================
