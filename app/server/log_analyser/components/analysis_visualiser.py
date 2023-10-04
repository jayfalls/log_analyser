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
    def plot_time_series_and_matrix(frequency_over_time, matrix_profile: numpy.array, window_size: int, title: str = "") -> None:
        motif_idx = numpy.argsort(matrix_profile[:, 0])[0]
        print(motif_idx)
        nearest_neighbor_idx = matrix_profile[motif_idx, 1]
        axs = plot.subplots(2, sharex=True, gridspec_kw={'hspace': 0})[1]
        plot.suptitle(f'{title} Motif (Pattern) Discovery', fontsize='30')
        
        axs[0].plot(frequency_over_time)
        axs[0].set_ylabel('Frequency', fontsize='20')
        axs[1].set_xlabel('Time', fontsize ='20')
        axs[1].set_ylabel('Matrix Profile', fontsize='20')
        # Resample the DataFrame to match the length of matrix_profile
        num_occurrences = len(matrix_profile)
        start_date = datetime.utcfromtimestamp(frequency_over_time.index.values[0].tolist() / 1e9)
        end_date = datetime.utcfromtimestamp(frequency_over_time.index.values[-1].tolist() / 1e9)
        # Calculate the time range between start and end dates
        time_range = end_date - start_date
        # Calculate the time interval between each occurrence
        interval = time_range / (num_occurrences - 1)
        # Convert interval to a valid frequency string
        frequency_str = to_offset(interval).freqstr
        matched_datetime = pandas.date_range(start=start_date, end=end_date, freq=frequency_str)
        if len(matched_datetime) < num_occurrences:
            matched_datetime = matched_datetime.append(pandas.Index([matched_datetime[-1]]))
        elif len(matched_datetime) > num_occurrences:
            matched_datetime = matched_datetime[:-1]
        axs[1].plot(matched_datetime, matrix_profile[:, 0])
        #rect = Rectangle((matched_datetime.to_list()[motif_idx], 0), window_size, 40, facecolor='lightgrey')
        #axs[0].add_patch(rect)
        #rect = Rectangle((matched_datetime.to_list()[nearest_neighbor_idx], 0), window_size, 40, facecolor='lightgrey')
        #axs[0].add_patch(rect)
        axs[1].axvline(x=matched_datetime.to_list()[motif_idx], linestyle="dashed")
        axs[1].axvline(x=matched_datetime.to_list()[nearest_neighbor_idx], linestyle="dashed")

        plot.show()
    
    def plot_multi_time_series_matrix(self, log_type_data_frames: dict, matrix_profiles: dict) -> None:
        for log_type, frequency_over_time in log_type_data_frames.items():
            if not len(frequency_over_time) > 1:
                continue
            matrix_profile = matrix_profiles.get(log_type)[0]
            window_size: int = matrix_profiles.get(log_type)[1]
            self.plot_time_series_and_matrix(frequency_over_time, matrix_profile, window_size, log_type)
    
    def visualise_log_type_time_series(self, log_type_data_frames: dict) -> None:
        for log_type, frequency_over_time in log_type_data_frames.items():
            if not len(frequency_over_time) > 1:
                continue
            self.visualise_time_series(frequency_over_time, log_type)
        show_plot()