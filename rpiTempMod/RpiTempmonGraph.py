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
from rpiTempMod import RpiTempmonWork as Work  # for data log func


class MatplotGraph(object):
    """class with 2 methods to display graphs with matplotlib"""
    def __init__(self, name):
        """docstring"""
        self.name = name

    def graph_log_data(self, destlog):
        """draw a  graph of pi GPU CPU from logdata"""
        # display menu return user selection
        selection = self.display_menu()

        # get data from log file function data_func
        timelist, cpulist, gpulist, cpu_uselist, ramlist, swaplist\
            = Work.data_func(destlog, True)

        # based on selection define y axis , title and call graph function
        # passing in data
        if selection == '1':
            plotlabel1 = 'CPU'
            plotlabel2 = 'GPU'
            ylabel = 'Temperature (degrees)'
            title = 'CPU & GPU temperature of RPi'
            self.draw_graph(timelist, cpulist, gpulist,
                            plotlabel1, plotlabel2, ylabel, title)
        elif selection == '2':
            plotlabel1 = 'CPU temp'
            plotlabel2 = 'CPU usage'
            ylabel = 'CPU usage(%) / Temperature (degrees)'
            title = 'CPU temperature and usage RPi'
            self.draw_graph(timelist, cpulist, cpu_uselist,
                            plotlabel1, plotlabel2, ylabel, title)
        elif selection == '3':
            plotlabel1 = 'RAM'
            plotlabel2 = 'SWAP'
            ylabel = 'Memory (% used)'
            title = 'RAM & Swap memory usage of RPi'
            self.draw_graph(timelist, ramlist, swaplist,
                            plotlabel1, plotlabel2, ylabel, title)
        elif selection == '4':
            plotlabel1 = 'CPU'
            ylabel = 'Memory (% used)'
            title = 'CPU usage of RPi'
            self.draw_graph(timelist, cpu_uselist, False,
                            plotlabel1, False, ylabel, title)
        else:
            print("Error Bad selection value")
            quit()

    def display_menu(self):
        """ method to display a menu for
        user to select graph"""
        menu = []
        menu.append("CPU and GPU Temperature versus Time-date")
        menu.append("CPU Temperature and CPU usage versus Time-date")
        menu.append("RAM and Swap memory usage versus Time-date")
        menu.append("CPU usage versus Time-date")
        menu.append("CPU usage versus live Time")
        menu.append("GPU Temperature versus live Time")
        menu.append("Exit")
        while True:
            print("\n")
            print(23 * "-", "GRAPH MENU OPTIONS", 23 * "-")
            for number, string in enumerate(menu):
                print(number+1, string)
            print(67 * "-")
            print("\n")
            selection = input("Please Select:")
            if selection == '1':
                return selection
            elif selection == '2':
                return selection
            elif selection == '3':
                return selection
            elif selection == '4':
                return selection
            elif selection == '5':
                self.graph_live_data("CPU")
                break
            elif selection == '6':
                self.graph_live_data("GPU")
                break
            elif selection == '7':
                break
            else:
                print("\n\t ** Warning : Unknown Option Selected! **")
        quit()

    def draw_graph(self, timelist, yaxis_list1,
                   yaxis_list2, plot_label1, plot_label2, yaxis_label, graph_title):
        """ Method to draw graphs two  modes, single and doulbe yaxis """

        # parse dates format
        mydates = [dateutil.parser.parse(s) for s in timelist]
        # convert to ints as strings cause issue with graph in new matlib version
        yaxis_list1 = list(map(float, yaxis_list1))

        if plot_label2:  # single plot graph mode
            yaxis_list2 = list(map(float, yaxis_list2))

        plt.xticks(rotation=90)
        plt.xticks(fontsize=5)
        plt.subplots_adjust(bottom=0.2)
        axisx = plt.gca()
        axisx.set_xticks(mydates)
        xfmt = md.DateFormatter('%m/%d %H:%M')
        axisx.xaxis.set_major_formatter(xfmt)
        axisx.xaxis.label.set_color('red')
        axisx.yaxis.label.set_color('red')

        plt.plot(mydates, yaxis_list1,
                 label=plot_label1, color='green', marker='x')
        if plot_label2:  # single plot graph mode
            plt.plot(mydates,
                     yaxis_list2, label=plot_label2, marker='*')
        plt.xlabel('Date time stamp (DD-MM HH:MM)')
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
                # GPU
                time_axis.append(yaxis_data)
                time_axis.pop(0)
                if choice == "GPU":
                    ostemp = os.popen('vcgencmd measure_temp').readline()
                    yaxis_data = (ostemp.replace("temp=", "").replace("'C\n", ""))
                    labels = ("RPi GPU temp", "Temperature ('C)", "GPU")
                    yaxis_data = float(yaxis_data)
                    time_axis.append(yaxis_data)
                    time_axis.pop(0)
                    self.plot_now(time_axis, labels)
                else:
                    yaxis_data = Work.get_cpu_use()
                    yaxis_data = float(yaxis_data)
                    labels = ("RPi CPU usage", "Usage (%)", "CPU")
                    time_axis.append(yaxis_data)
                    time_axis.pop(0)
                    self.plot_now(time_axis, labels)

                plt.pause(2)
        except Exception as error:
            print(error)
            print("Real-time matplotlib plot shutdown")

    def plot_now(self, timeaxis, labels):
        """ Called from method graph_live_data to draw graph"""

        title, y_label, plot_label = labels
        plt.clf()

        plt.ylim([1, 100])
        plt.ylabel(y_label, color='red')

        plt.title(title, color='green')
        plt.grid(True)
        plt.xlabel("Time (last 300 seconds)", color='red')
        plt.plot(timeaxis, color='blue', marker='*', label=plot_label)
        plt.legend(loc='upper right', fancybox=True, shadow=True)
        plt.show()


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
