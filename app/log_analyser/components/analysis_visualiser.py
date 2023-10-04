from datetime import datetime, timedelta
import matplotlib.pyplot as plot
import matplotlib.dates
from matplotlib.patches import Rectangle
import pandas
from pandas.tseries.frequencies import to_offset
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

    @staticmethod
    def visualise_time_series_matrix(frequency_over_time, matrix_profile: numpy.array, window_size: int, title: str = "") -> None:
        motif_idx = numpy.argsort(matrix_profile[:, 0])[0]
        print(motif_idx)
        nearest_neighbor_idx = matrix_profile[motif_idx, 1]
        axs = plot.subplots(2, sharex=True, gridspec_kw={'hspace': 0})[1]
        plot.suptitle(f'{title} Motif (Pattern) Discovery', fontsize='30')
        
        axs[0].plot(frequency_over_time)
        axs[0].set_ylabel('Frequency', fontsize='20')
        axs[1].set_xlabel('Time', fontsize ='20')
        axs[1].set_ylabel('Matrix Profile', fontsize='20')
        matched_datetime = get_matching_datetime_range(frequency_over_time, matrix_profile)
        axs[1].plot(matched_datetime, matrix_profile[:, 0])
        #rect = Rectangle((matched_datetime.to_list()[motif_idx], 0), window_size, 40, facecolor='lightgrey')
        #axs[0].add_patch(rect)
        #rect = Rectangle((matched_datetime.to_list()[nearest_neighbor_idx], 0), window_size, 40, facecolor='lightgrey')
        #axs[0].add_patch(rect)
        axs[1].axvline(x=matched_datetime.to_list()[motif_idx], linestyle="dashed")
        axs[1].axvline(x=matched_datetime.to_list()[nearest_neighbor_idx], linestyle="dashed")
    
    def plot_multi_time_series_matrix(self, log_type_data_frames: dict, matrix_profiles: dict) -> None:
        for log_type, frequency_over_time in log_type_data_frames.items():
            if not len(frequency_over_time) > 1:
                continue
            matrix_profile = matrix_profiles.get(log_type)[0]
            window_size: int = matrix_profiles.get(log_type)[1]
            self.visualise_time_series_matrix(frequency_over_time, matrix_profile, window_size, log_type)
        show_plot()
    
    def visualise_log_type_time_series(self, log_type_data_frames: dict) -> None:
        for log_type, frequency_over_time in log_type_data_frames.items():
            if not len(frequency_over_time) > 1:
                continue
            self.visualise_time_series(frequency_over_time, log_type)
        show_plot()