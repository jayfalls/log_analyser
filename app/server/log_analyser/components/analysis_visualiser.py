import matplotlib.pyplot as plot
import matplotlib.dates
from matplotlib.patches import Rectangle
import pandas
import numpy



# CONTROL FUNCTIONS
def show_plot() -> None:
        plot.show()

# HELPER FUNCTIONS
def organise_two_dimensional_list(two_dimensional_list: list) -> tuple:
    x_list: list = []
    y_list: list[int] = []
    for line in two_dimensional_list:
        x_list.append(line[0])
        y_list.append(line[1])
    return (x_list, y_list)
    

class AnalysisVisualiser():
    @staticmethod
    def visualise_bar_graph(graph_details: tuple, xy_list: tuple, shuffle: bool = False) -> None:
        working_list: tuple
        if shuffle:
            working_list = organise_two_dimensional_list(xy_list)
        else:
            working_list = xy_list[:]
        plot.bar(working_list[0], working_list[1])
        plot.title(graph_details[0])
        plot.xlabel(graph_details[1])
        plot.ylabel(graph_details[2])
        show_plot()
    
    @staticmethod
    def visualise_time_series(frequency_over_time, title) -> None:
        ax = frequency_over_time.plot()
        ax.set_title(title)
        ax.set_xlabel('Time')
        ax.set_ylabel('Frequency')
    
    def visualise_log_type_time_series(self, log_type_data_frames: dict) -> None:
        for log_type, frequency_over_time in log_type_data_frames.items():
            self.visualise_time_series(frequency_over_time, log_type)
        show_plot()