from datetime import datetime, timedelta
import matplotlib.pyplot as plot
from matplotlib.pyplot import Axes
import matplotlib.dates
from matplotlib.patches import Rectangle
import pandas
from pandas.tseries.frequencies import to_offset
import numpy
import random


# VARIABLES
## Constants
LINE_STYLES: tuple = ("-", "--", "-.", ":")
## States
chosen_lines: list = []


# HELPER FUNCTIONS
## List Organisation
def organise_two_dimensional_list(two_dimensional_list: list) -> tuple:
    x_list: list = []
    y_list: list[int] = []
    for line in two_dimensional_list:
        x_list.append(line[0])
        y_list.append(line[1])
    return (x_list, y_list)

## DateTime Lists
def get_formated_datetime_range(frequency_over_time) -> tuple:
    unformatted_start_date = frequency_over_time.index.values[0].tolist()
    unformatted_end_date = frequency_over_time.index.values[-1].tolist()
    start_date: datetime = datetime.utcfromtimestamp(unformatted_start_date / 1e9)
    end_date: datetime = datetime.utcfromtimestamp(unformatted_end_date / 1e9)
    time_range: float = end_date - start_date
    return (start_date, end_date, time_range)

def get_new_interval(matrix_profile, time_range: float) -> tuple:
    num_occurrences: int = len(matrix_profile)
    num_occurrences_fixed: int = num_occurrences - 1 # Yields results with less adjustments needed, but either way is fine
    interval: float = time_range / num_occurrences_fixed
    return (num_occurrences, interval)

### Convert a time interval to a valid frequency string
def get_freq_str(interval: float) -> str:
    return to_offset(interval).freqstr
    
### Resample a datetime list to match the occurences in a matrix_profile
def get_matching_datetime_range(frequency_over_time, matrix_profile):
    # Calculate new parameters
    start_date, end_date, time_range = get_formated_datetime_range(frequency_over_time)
    num_occurrences, interval = get_new_interval(matrix_profile, time_range)
    frequency_str: str = get_freq_str(interval)
    # Generate new list with matching times
    matched_datetime = pandas.date_range(start=start_date, end=end_date, freq=frequency_str)
    matched_occurences: int = len(matched_datetime)
    # Error Handling
    if matched_occurences == num_occurrences:
        return matched_datetime
    if matched_occurences < num_occurrences:
        return matched_datetime.append(pandas.Index([matched_datetime[-1]])) # Duplicate last index
    if matched_occurences > num_occurrences:
        return matched_datetime[:-1] # Remove last index

## Random Line Styles
def reset_chosen_lines() -> None:
    chosen_lines = []

def get_unique_random_line() -> str:
    chosen_line_style: str = ""
    while not chosen_line_style in chosen_lines:
        chosen_line_style = random.choice(LINE_STYLES)
        if not chosen_line_style in chosen_lines:
            chosen_lines.append(chosen_line_style)
    return chosen_line_style
    

# ANALYSIS VISUALISER
class AnalysisVisualiser():
    # VARIABLES
    frequency_matrix_axes: Axes
    
    # OUTER FUNCTIONS
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
    
    @staticmethod
    def visualise_time_series(frequency_over_time, title) -> None:
        ax = frequency_over_time.plot()
        ax.set_title(title)
        ax.label = ""
        ax.set_xlabel("Time")
        ax.set_ylabel("Frequency")
        
    def add_graph_to_visualisation(self, plot_index: int, key: str, data_frame) -> None:
        chosen_line_style: str = get_unique_random_line()
        self.frequency_matrix_axes[plot_index].plot(data_frame, label=key, linestyle=chosen_line_style)

    def visualise_time_series_matrix(self, label_name: str, frequency_over_time, matrix_profile) -> None:
        chosen_line_style: str = get_unique_random_line()
        self.frequency_matrix_axes[0].plot(frequency_over_time, label=label_name, linestyle=chosen_line_style)
        matched_datetime = get_matching_datetime_range(frequency_over_time, matrix_profile)
        self.frequency_matrix_axes[2].plot(matched_datetime, matrix_profile[:, 0], label=label_name, linestyle=chosen_line_style)
        
        #motif_idx = numpy.argsort(matrix_profile[:, 0])[0]
        #nearest_neighbor_idx = matrix_profile[motif_idx, 1]
        #rect = Rectangle((matched_datetime.to_list()[motif_idx], 0), window_size, 40, facecolor="lightgrey")
        #self.frequency_matrix_axes[0].add_patch(rect)
        #rect = Rectangle((matched_datetime.to_list()[nearest_neighbor_idx], 0), window_size, 40, facecolor="lightgrey")
        #self.frequency_matrix_axes[0].add_patch(rect)
        #self.frequency_matrix_axes[2].axvline(x=matched_datetime.to_list()[motif_idx], linestyle="dashed")
        #self.frequency_matrix_axes[2].axvline(x=matched_datetime.to_list()[nearest_neighbor_idx], linestyle="dashed")

    def visualise_multi_time_series_matrix(self, graphs: dict) -> None:
        reset_chosen_lines()
        num_graphs: int = len(graphs)
        self.frequency_matrix_axes = plot.subplots(num_graphs, sharex=True, gridspec_kw={"hspace": 0})[1]
        plot.suptitle(f"Log Message Analysis", fontsize="30")
        for index, key in enumerate(graphs.keys()):
            self.frequency_matrix_axes[index].set_ylabel(key, fontsize="12")
        self.frequency_matrix_axes[-1].set_xlabel("Time", fontsize ="20")
        
        frequency_data_frames, source_data_frames, matrix_profiles = graphs.values()
        
        for key, frequency_over_time in frequency_data_frames.items():
            if not len(frequency_over_time) > 1:
                continue
            matrix_profile, _ = matrix_profiles.get(key)
            self.visualise_time_series_matrix(key, frequency_over_time, matrix_profile)
        reset_chosen_lines()
        for key, source_over_time in source_data_frames.items():
            if not len(source_over_time) > 1:
                continue
            self.add_graph_to_visualisation(1, key, source_over_time)  
        
        for axes in self.frequency_matrix_axes:
            axes.legend(loc='center left', bbox_to_anchor=(1, 0.5))
    
    ## Control
    @staticmethod
    def show_plot() -> None:
        plot.show()