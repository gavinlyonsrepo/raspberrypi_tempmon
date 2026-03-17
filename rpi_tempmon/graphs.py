#!/usr/bin/env python3
"""
Module imported into rpi_tempmon containing a class
with methods to display graphs from matplotlib.
Class : MatplotGraph
"""

from dataclasses import dataclass
import os
import sys
import re
import dateutil
import matplotlib.pyplot as plt
import matplotlib.dates as md
import matplotlib as mpl
from rpi_tempmon import display
from rpi_tempmon import log_writer
from rpi_tempmon import sensors

mpl.use('tkagg')

@dataclass
class GraphSpec:
    """Metadata for a single graph — groups labels and title to reduce argument count."""
    plot_label1: str
    yaxis_label: str
    title: str
    plot_label2: str | None = None


class MatplotGraph:
    """
    Class with methods to display graphs with matplotlib.
    Methods:
    (1) __init__: initialise with name
    (2) graph_log_data: define data to draw graphs based on user choice
    (3) display_menu: display a menu for user to select graph type
    (4) draw_graph: draw a graph from log data
    (5) graph_live_data: draw live data graphs
    (6) plot_now: called from graph_live_data to draw graph
    (7) graph_all_live_data: draw live graph of GPU/CPU/RAM
    (8) plot_all_now: called from graph_all_live_data to draw graph
    """

    def __init__(self, name):
        """Initialise class with name and define self.selection variable."""
        self.name = name
        self.selection = 0

    def graph_log_data(self, destlog):
        """Define data to draw graphs from log data."""
        self.display_menu()

        data = log_writer.parse_log(destlog)
        timelist    = data["timelist"]
        unixlist    = data["unixlist"]
        cpulist     = data["cpulist"]
        gpulist     = data["gpulist"]
        cpu_uselist = data["cpu_uselist"]
        ramlist     = data["ramlist"]
        swaplist    = data["swaplist"]

        # Assign yaxislist based on selection range — default to timelist
        if re.match('[5-8]', self.selection):
            yaxislist = unixlist
        else:
            yaxislist = timelist

        if self.selection in ('1', '5'):
            self.draw_graph(yaxislist, cpulist, gpulist,
                            GraphSpec('CPU', 'Temperature (degrees)',
                                      'CPU & GPU temperature of RPi', 'GPU'))
        elif self.selection in ('2', '6'):
            self.draw_graph(yaxislist, cpulist, cpu_uselist,
                            GraphSpec('CPU temp', 'CPU usage(%) / Temperature (degrees)',
                                      'CPU temperature and usage RPi', 'CPU usage'))
        elif self.selection in ('3', '7'):
            self.draw_graph(yaxislist, ramlist, swaplist,
                            GraphSpec('RAM', 'Memory (% used)',
                                      'RAM & Swap memory usage of RPi', 'SWAP'))
        elif self.selection in ('4', '8'):
            self.draw_graph(yaxislist, cpu_uselist, None,
                            GraphSpec('CPU', 'CPU (% used)', 'CPU usage of RPi'))
        else:
            display.red("Error: graph_log_data: Bad selection value")

    def display_menu(self):
        """Display a menu for user to select graph type."""
        os.system('clear')
        menu = [
            "CPU and GPU Temperature versus Time-date",
            "CPU Temperature and CPU usage versus Time-date",
            "RAM and Swap memory usage versus Time-date",
            "CPU usage versus Time-date",
            "CPU and GPU Temperature versus Epoch time",
            "CPU Temperature and CPU usage versus Epoch time",
            "RAM and Swap memory usage versus Epoch time",
            "CPU usage versus Epoch time",
            "CPU usage versus live Time",
            "GPU Temperature versus live Time",
            "RAM usage versus live Time",
            "CPU GPU & RAM usage versus live time",
            "Exit",
        ]
        try:
            while True:
                print("\n")
                display.blue("RPI_tempmon :: Graph Menu Options")
                display.line()
                for number, string in enumerate(menu):
                    print(number + 1, string)
                display.line()
                self.selection = input("Please Select:")
                if int(self.selection) <= 8:
                    return
                if self.selection == '9':
                    self.graph_live_data("CPU")
                    break
                if self.selection == '10':
                    self.graph_live_data("GPU")
                    break
                if self.selection == '11':
                    self.graph_live_data("RAM")
                    break
                if self.selection == '12':
                    self.graph_all_live_data()
                    break
                if self.selection == '13':
                    sys.exit()
                else:
                    display.red("\n ** Warning : Unknown Option Selected! **")
                    display.anykey("")
                    os.system('clear')
        except ValueError as error:
            print(error)
            display.red("Error: Wrong menu Input: Integer only : Try Again")
            sys.exit()

    def draw_graph(self, timelist, yaxis_list1, yaxis_list2, spec: GraphSpec):
        """Draw graphs in two modes: single and double y-axis.

        Pass spec.plot_label2=None for single-series graphs.
        """
        yaxis_list1 = list(map(float, yaxis_list1))

        if spec.plot_label2 is not None:
            yaxis_list2 = list(map(float, yaxis_list2))

        plt.xticks(rotation=90)
        plt.xticks(fontsize=6)
        plt.subplots_adjust(bottom=0.2)
        axisx = plt.gca()

        if self.selection == 0:
            mydates = timelist
            plt.xlabel('TestRuns')
        elif re.match('[1-4]', self.selection):
            mydates = [dateutil.parser.parse(s) for s in timelist]
            axisx.set_xticks(mydates)
            xfmt = md.DateFormatter('%m/%d %H:%M')
            axisx.xaxis.set_major_formatter(xfmt)
            plt.xlabel('Date time stamp (DD-MM HH:MM)')
        else:
            mydates = timelist
            plt.xlabel('Unix epoch time (seconds)')

        axisx.xaxis.label.set_color('red')
        axisx.yaxis.label.set_color('red')

        plt.plot(mydates, yaxis_list1, label=spec.plot_label1, color='green', marker='x')
        if spec.plot_label2 is not None:
            plt.plot(mydates, yaxis_list2, label=spec.plot_label2, marker='*')

        plt.ylabel(spec.yaxis_label)
        plt.title(spec.title, color='green')
        plt.legend(loc='upper right', fancybox=True, shadow=True)
        plt.grid(True)
        plt.show()

    def graph_all_live_data(self):
        """Draw a live graph of Pi GPU/CPU/RAM."""
        print("Drawing graph of all data usage versus live time")
        print("Press CTRL+c to quit.")
        try:
            time_cpu_axis = [0.5] * 150
            time_ram_axis = [0.5] * 150
            time_gpu_axis = [0.5] * 150
            plt.ion()

            while True:
                yaxis_cpu_data = float(sensors.get_cpu_usage())
                yaxis_ram_data = float(sensors.get_ram_usage())
                yaxis_gpu_data = float(sensors.get_gpu_temp())

                labels = (
                    "GPU Temp + CPU & RAM usage",
                    "CPU-% RAM-% GPU-'C",
                    "CPU-%", "RAM-%", "GPU-'C",
                )
                time_cpu_axis.append(yaxis_cpu_data)
                time_ram_axis.append(yaxis_ram_data)
                time_gpu_axis.append(yaxis_gpu_data)
                time_cpu_axis.pop(0)
                time_ram_axis.pop(0)
                time_gpu_axis.pop(0)
                self.plot_all_now(time_cpu_axis, time_ram_axis, time_gpu_axis, labels)
                plt.pause(2)

        except KeyboardInterrupt:
            display.bold("Real-time matplotlib plot shutdown")
            sys.exit()

    def plot_all_now(self, time_cpu_axis, time_ram_axis, time_gpu_axis, labels):
        """Called from graph_all_live_data to render the graph frame."""
        title, y_label, plot_cpu_label, plot_ram_label, plot_gpu_label = labels
        plt.clf()
        plt.ylim([1, 100])
        plt.ylabel(y_label, color='red')
        plt.title(self.name + title, color='green')
        plt.grid(True)
        plt.xlabel("Time (last 300 seconds)", color='red')
        plt.plot(time_cpu_axis, color='blue',  marker='', label=plot_cpu_label)
        plt.plot(time_ram_axis, color='red',   marker='', label=plot_ram_label)
        plt.plot(time_gpu_axis, color='green', marker='', label=plot_gpu_label)
        plt.legend(loc='upper right', fancybox=True, shadow=True)
        plt.show()

    def graph_live_data(self, choice):
        """Draw a live graph of Pi GPU, CPU, or RAM."""
        print("Press CTRL+c to quit.")
        try:
            time_axis = [0.5] * 150
            plt.ion()

            while True:
                if choice == "GPU":
                    yaxis_data = float(sensors.get_gpu_temp())
                    labels = (" GPU live temp", "Temperature ('C)", "GPU")
                elif choice == 'CPU':
                    yaxis_data = float(sensors.get_cpu_usage())
                    labels = (" CPU live usage", "Usage (%)", "CPU")
                else:
                    yaxis_data = float(sensors.get_ram_usage())
                    labels = (" RAM live usage", "Usage (%)", "RAM")

                time_axis.append(yaxis_data)
                time_axis.pop(0)
                self.plot_now(time_axis, labels)
                plt.pause(2)

        except KeyboardInterrupt:
            display.bold("Real-time matplotlib plot shutdown")
            sys.exit()

    def plot_now(self, timeaxis, labels):
        """Called from graph_live_data to render the graph frame."""
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
