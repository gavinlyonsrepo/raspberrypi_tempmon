#!/usr/bin/env python3
"""
Module imported into rpi_tempmon contains
containing a class with methods to display graphs from matlib
Class : MatplotGraph
"""
import os
import re
import dateutil
import matplotlib as mpl
mpl.use('tkagg')
import matplotlib.pyplot as plt
import matplotlib.dates as md
# My modules
from . import RpiTempmonWork as Work



class MatplotGraph(object):
    """
    class with 6 methods to display graphs with matplotlib
    Methods:
    (1) init: pass
    (2) graph_log_data: Define data to draw graphs based on user choice
    (3) display_menu: Method to display a menu for
        user to select graph type
    (4) draw_graph: Draw a  graph from logdata
    (5) graph_live_data: Draw live data graphs
    (6) Plot_now: Called from method graph_live_data to draw graph
    """

    def __init__(self, name):
        """init class with name and define self.selection variable"""
        self.name = name
        self.selection = 0

    def graph_log_data(self, destlog):
        """define data to draw graphs from logdata"""
        # display menu return user selection
        self.display_menu()

        # get data from log file function data_func
        timelist, unixlist, cpulist, gpulist, cpu_uselist, ramlist, swaplist\
            = Work.data_func(destlog, True)
        if re.match('[1-4]', self.selection):
            yaxislist = timelist
        elif re.match('[5-8]', self.selection):
            yaxislist = unixlist

        if (self.selection == '1' or self.selection == '5'):
            plotlabel1 = 'CPU'
            plotlabel2 = 'GPU'
            ylabel = 'Temperature (degrees)'
            title = 'CPU & GPU temperature of RPi'
            self.draw_graph(yaxislist, cpulist, gpulist,
                            plotlabel1, plotlabel2, ylabel, title)

        elif (self.selection == '2' or self.selection == '6'):
            plotlabel1 = 'CPU temp'
            plotlabel2 = 'CPU usage'
            ylabel = 'CPU usage(%) / Temperature (degrees)'
            title = 'CPU temperature and usage RPi'
            self.draw_graph(yaxislist, cpulist, cpu_uselist,
                            plotlabel1, plotlabel2, ylabel, title)
        elif (self.selection == '3' or self.selection == '7'):
            plotlabel1 = 'RAM'
            plotlabel2 = 'SWAP'
            ylabel = 'Memory (% used)'
            title = 'RAM & Swap memory usage of RPi'
            self.draw_graph(yaxislist, ramlist, swaplist,
                            plotlabel1, plotlabel2, ylabel, title)
        elif (self.selection == '4' or self.selection == '8'):
            plotlabel1 = 'CPU'
            ylabel = 'Memory (% used)'
            title = 'CPU usage of RPi'
            self.draw_graph(yaxislist, cpu_uselist, False,
                            plotlabel1, False, ylabel, title)
        else:
            Work.msg_func("red", "Error: graph_log_data: Bad selection value")
            return

    def display_menu(self):
        """ method to display a menu for
        user to select graph"""
        os.system('clear')
        menu = []
        menu.append("CPU and GPU Temperature versus Time-date")
        menu.append("CPU Temperature and CPU usage versus Time-date")
        menu.append("RAM and Swap memory usage versus Time-date")
        menu.append("CPU usage versus Time-date")
        menu.append("CPU and GPU Temperature versus Epoch time")
        menu.append("CPU Temperature and CPU usage versus Epoch time")
        menu.append("RAM and Swap memory usage versus Epoch time")
        menu.append("CPU usage versus Epoch time")
        menu.append("CPU usage versus live Time")
        menu.append("GPU Temperature versus live Time")
        menu.append("RAM usage versus live Time")
        menu.append("Exit")
        try:
            while True:
                print("\n")
                Work.msg_func("blue", "Graph Menu Options")
                Work.msg_func("line", "")
                for number, string in enumerate(menu):
                    print(number+1, string)
                Work.msg_func("line", "")
                self.selection = (input("Please Select:"))
                if int(self.selection) <= 8:
                    return
                elif self.selection == '9':
                    self.graph_live_data("CPU")
                    break
                elif self.selection == '10':
                    self.graph_live_data("GPU")
                    break
                elif self.selection == '11':
                    self.graph_live_data("RAM")
                    break
                elif self.selection == '12':
                    quit()
                else:
                    Work.msg_func("red", "\n ** Warning : Unknown Option Selected! **")
                    Work.msg_func("anykey", "")
                    os.system('clear')
        except ValueError as error:
            print(error)
            Work.msg_func("red", "Error: Wrong menu Input: Integer only : Try Again")
            quit()

    def draw_graph(self, timelist, yaxis_list1,
                   yaxis_list2, plot_label1, plot_label2, yaxis_label, graph_title):
        """ Method to draw graphs two  modes, single and doulbe yaxis """
        # convert to ints as strings cause issue with graph in new matlib version
        yaxis_list1 = list(map(float, yaxis_list1))

        if plot_label2:  # single plot graph mode
            yaxis_list2 = list(map(float, yaxis_list2))

        plt.xticks(rotation=90)
        plt.xticks(fontsize=6)
        plt.subplots_adjust(bottom=0.2)
        axisx = plt.gca()
        # check user input for time date or unix epoch for yaxis
        if self.selection == 0:
            mydates = timelist
            plt.xlabel('TestRuns')
        elif re.match('[1-4]', self.selection):
            mydates = [dateutil.parser.parse(s) for s in timelist]
            axisx.set_xticks(mydates)
            xfmt = md.DateFormatter('%m/%d %H:%M')
            axisx.xaxis.set_major_formatter(xfmt)
            plt.xlabel('Date time stamp (DD-MM HH:MM)')
        elif re.match('[5-8]', self.selection):
            mydates = timelist
            plt.xlabel('Unix epoch time (seconds)')

        axisx.xaxis.label.set_color('red')
        axisx.yaxis.label.set_color('red')

        plt.plot(mydates, yaxis_list1,
                 label=plot_label1, color='green', marker='x')
        if plot_label2:  # single plot graph mode
            plt.plot(mydates,
                     yaxis_list2, label=plot_label2, marker='*')

        plt.ylabel(yaxis_label)
        plt.title(graph_title, color='green')
        plt.legend(loc='upper right', fancybox=True, shadow=True)
        plt.grid(True)
        plt.show()

    def graph_live_data(self, choice):
        """ Draw a live graph of pi GPU """
        try:
            time_axis = []
            yaxis_data = 0
            plt.ion()
            labels = ()
            # pre-load dummy data
            for i in range(0, 150):
                time_axis.append(.5)

            while True:

                time_axis.append(yaxis_data)
                time_axis.pop(0)
                if choice == "GPU":
                    ostemp = os.popen('vcgencmd measure_temp').readline()
                    yaxis_data = (ostemp.replace("temp=", "").replace("'C\n", ""))
                    labels = (" GPU live temp", "Temperature ('C)", "GPU")
                    yaxis_data = float(yaxis_data)
                    time_axis.append(yaxis_data)
                    time_axis.pop(0)
                    self.plot_now(time_axis, labels)
                elif choice == 'CPU':
                    yaxis_data = Work.get_cpu_use()
                    yaxis_data = float(yaxis_data)
                    labels = (" CPU live usage", "Usage (%)", "CPU")
                    time_axis.append(yaxis_data)
                    time_axis.pop(0)
                    self.plot_now(time_axis, labels)
                else:  # RAM
                    yaxis_data = Work.get_ram_info()
                    yaxis_data = float(yaxis_data)
                    labels = (" RAM live usage", "Usage (%)", "RAM")
                    time_axis.append(yaxis_data)
                    time_axis.pop(0)
                    self.plot_now(time_axis, labels)

                plt.pause(2)
        except Exception as error:
            print(error)
            Work.msg_func("bold", "Real-time matplotlib plot shutdown")
            quit()

    def plot_now(self, timeaxis, labels):
        """ Called from method graph_live_data to draw graph"""

        title, y_label, plot_label = labels
        plt.clf()

        plt.ylim([1, 100])
        plt.ylabel(y_label, color='red')

        plt.title(self.name + title, color='green')
        plt.grid(True)
        plt.xlabel("Time (last 300 seconds)", color='red')
        plt.plot(timeaxis, color='blue', marker='*', label=plot_label)
        plt.legend(loc='upper right', fancybox=True, shadow=True)
        plt.show()


def importtest(text):
    """import print test statement"""
    # print(text)
    pass

# ===================== MAIN ===============================


if __name__ == '__main__':
    importtest("main")
else:
    importtest("Imported {}".format(__name__))

# ===================== END ===============================
