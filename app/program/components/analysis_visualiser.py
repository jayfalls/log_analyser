from datetime import datetime, timedelta
import matplotlib.pyplot as plot
from matplotlib.pyplot import Axes
import matplotlib.dates
from matplotlib.patches import Rectangle
import pandas
from pandas import DataFrame
from pandas.tseries.frequencies import to_offset
from pandas import date_range
import numpy
from numpy import array
import random


# VARIABLES
## Constants
LINE_STYLES: tuple = ("-", "--", "-.", ":")
TEXT_ABOVE_DISTANCE: float = 0.2
TEXT_ABOVE_SIZE: int = 6
## States
available_lines: list = list(LINE_STYLES)


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
def get_matching_datetime_range(frequency_over_time, matrix_profile) -> date_range:
    # Calculate new parameters
    start_date, end_date, time_range = get_formated_datetime_range(frequency_over_time)
    num_occurrences, interval = get_new_interval(matrix_profile, time_range)
    frequency_str: str = get_freq_str(interval)
    # Generate new list with matching times
    matched_datetime = date_range(start=start_date, end=end_date, freq=frequency_str)
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
    global available_lines
    available_lines = list(LINE_STYLES)

def get_unique_random_line() -> str:
    if len(available_lines) == 0:
        reset_chosen_lines()
    chosen_line_style: str = random.choice(available_lines)
    available_lines.remove(chosen_line_style)
    return chosen_line_style

    
# ANALYSIS VISUALISER
class AnalysisVisualiser():
    # VARIABLES
    ## XY-Axis
    all_frequency_over_time: DataFrame
    ## X-Axis
    matched_datetime: date_range
    ## Graphs
    frequency_matrix_axes: Axes
    
    # INNER FUNCTIONS
    ## Helper Functions
    def get_highest_frequency(self) -> int:
        return self.all_frequency_over_time["frequency"].max()

    def get_frequency_at_datetime(self, time) -> int:
        closest_time = self.all_frequency_over_time.index.asof(time)
        frequency = self.all_frequency_over_time.loc[closest_time, 'frequency']
        if frequency == 0:
            return self.get_highest_frequency()
        return frequency
    
    ### Rectangle Widths
    def get_times_and_widths(self, insight: array) -> list[list]:
        times_widths: list[list] = []
        previous_index: int = insight[0]
        start_index: int = insight[0]
        end_index: int = 0
        for insight_index, time_index in enumerate(insight):
            if insight_index == 0:
                continue
            if time_index == previous_index + 1:
                end_index = time_index
                previous_index = time_index
                continue
            if end_index != 0:
                start_time = self.matched_datetime[start_index]
                width_range = self.matched_datetime[end_index] - start_time
                times_widths.append([start_time, width_range])
            else:
                time = self.matched_datetime[time_index]
                if time == self.matched_datetime[-1]:
                    continue
                width_range = self.matched_datetime[time_index + 1] - time
                times_widths.append([time, width_range])
            start_index = time_index
            previous_index = insight[0]
            end_index = 0
        return times_widths

    ## Visualisation
    def add_graph_to_visualisation(self, plot_index: int, key: str, data_frame: DataFrame) -> None:
        chosen_line_style: str = get_unique_random_line()
        self.frequency_matrix_axes[plot_index].plot(data_frame, label=key, linestyle=chosen_line_style)

    ## Patterns
    @staticmethod
    def print_pattern_percent(matching_graphs: tuple) -> None:
        name1, name2, percent_matched = matching_graphs
        print(f"Graphs {name1} and {name2} are {int(percent_matched)}% identical")

    ## Anomalies
    def add_non_matching_anomalies(self, insight: DataFrame) -> None:
        for x_time in insight.index:
            frequency: int = self.get_frequency_at_datetime(x_time)
            self.frequency_matrix_axes[0].plot(x_time, frequency, marker="v", markersize=8, color="r")
            self.frequency_matrix_axes[0].text(x_time, frequency + TEXT_ABOVE_DISTANCE, "Unique Occurence", color="r", fontsize=TEXT_ABOVE_SIZE)
    
    def add_threshold_line(self, threshold: float) -> None:
        self.frequency_matrix_axes[-1   ].axhline(y=threshold, color='r', linestyle='--')
        self.frequency_matrix_axes[-1   ].text(self.matched_datetime[0], threshold + TEXT_ABOVE_DISTANCE,"Threshold", color="red", fontsize=TEXT_ABOVE_SIZE)
    
    def add_threshold_anomalies(self, insight: array) -> None:
        if len(insight) == 0:
            return
        times_widths: list[list] = self.get_times_and_widths(insight)
        for time, width_range in times_widths:
            if time == self.matched_datetime[-1]:
                continue
            frequency: int = self.get_frequency_at_datetime(time)
            rect = Rectangle((time, 0), width_range, frequency)
            rect.set_facecolor('red')  # Set fill color
            rect.set_alpha(0.5)  # Set transparency
            self.frequency_matrix_axes[0].add_patch(rect)
            self.frequency_matrix_axes[0].text(time, frequency + TEXT_ABOVE_DISTANCE, "Threshold Anomaly", color="red", fontsize=TEXT_ABOVE_SIZE)

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
    
    ## Time Series  
    def visualise_time_series(self, frequency_over_time, title) -> None:
        self.all_frequency_over_time = frequency_over_time
        ax = frequency_over_time.plot()
        ax.set_title(title)
        ax.label = ""
        ax.set_xlabel("Time")
        ax.set_ylabel("Frequency")

    def visualise_time_series_matrix(self, label_name: str, frequency_over_time, matrix_profile) -> None:
        chosen_line_style: str = get_unique_random_line()
        self.frequency_matrix_axes[0].plot(frequency_over_time, label=label_name, linestyle=chosen_line_style)
        self.matched_datetime = get_matching_datetime_range(frequency_over_time, matrix_profile)
        self.frequency_matrix_axes[3].plot(self.matched_datetime, matrix_profile[:, 0], label=label_name, linestyle=chosen_line_style)

    ### Multi Graph
    def setup_multiple_graph_axes(self, title: str, graphs: dict) -> None:
        reset_chosen_lines()
        num_graphs: int = len(graphs)
        self.frequency_matrix_axes = plot.subplots(num_graphs, sharex=True, gridspec_kw={"hspace": 0})[1]
        plot.suptitle(title, fontsize="30")
        for index, key in enumerate(graphs.keys()):
            self.frequency_matrix_axes[index].set_ylabel(key, fontsize="12")
        self.frequency_matrix_axes[-1].set_xlabel("Time", fontsize ="20")

    def plot_graphs(self, graphs: dict) -> None:
        frequency_data_frames, source_data_frames, matrix_profiles, hourly_averages = graphs.values()
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
        self.add_graph_to_visualisation(2, "All", hourly_averages)
        for axes in self.frequency_matrix_axes:
            axes.legend(loc="center left", bbox_to_anchor=(1, 0.5))
    
    def visualise_multi_time_series_matrix(self, graphs: dict) -> None:
        self.setup_multiple_graph_axes("Log Message Analysis", graphs)
        self.plot_graphs(graphs)
    
    ## Analysis
    def add_analysis_insights(self, insights: dict) -> None:
        for key, insight in insights.items():
            if key == "PERCENT_MATCHED":
                for matching_graphs in insight:
                    self.print_pattern_percent(matching_graphs)
            if key == "NON_MATCH_ANOMALIES":
                for non_match_anomalies in insight: 
                    self.add_non_matching_anomalies(non_match_anomalies)
            if key == "THRESHOLD_ANOMALIES":
                threshold, anomalies = insight
                self.add_threshold_line(threshold)
                self.add_threshold_anomalies(anomalies)
    
    ## Control
    @staticmethod
    def show_plot() -> None:
        plot.show()