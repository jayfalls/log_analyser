import matplotlib.pyplot as plot
import numpy
from numpy import array
import pandas
from pandas import DataFrame
from stumpy import stump


# LOG TO DATABASE
class LogDatabaseAnalyser():
    # VARIABLES
    ## References
    # | log_analyser | Must be assigned by log_analyser interface

    def get_log_type_frequencies(self) -> tuple:
        try:
            frequencies: tuple = self.log_analyser.get_log_type_frequencies()
            if frequencies is None:
                raise Exception("Error: Unable to retrieve log type frequencies.")
            return frequencies
        except Exception as error:
            raise Exception("An error occurred during analysis:", str(error))

    def get_sorted_log_types(self) -> dict:
        try:
            sorted_log_types: dict = self.log_analyser.get_sorted_log_types()
            if sorted_log_types is None:
                raise Exception("Error: Unable to retrieve log type frequencies.")
            return sorted_log_types
        except Exception as error:
            raise Exception("An error occurred during analysis:", str(error))

    @staticmethod
    def process_frequency_over_time(data_frame: DataFrame, time_interval_minutes: int):
        data_frame['datetime'] = pandas.to_datetime(data_frame['date'] + ' ' + data_frame['time'])
        # Remove the 'date' and 'time' columns
        data_frame.drop(['date', 'time'], axis=1, inplace=True)
        # Set the datetime column as the index
        data_frame.set_index('datetime', inplace=True)
        # Resample the data to the specified time interval and count the occurrences
        frequency_over_time = data_frame.groupby('datetime').count()
        frequency_over_time.columns = ['frequency']
        #frequency_over_time = data_frame.resample(str(time_interval_minutes) + 'T').size()
        frequency_over_time = frequency_over_time.resample(str(time_interval_minutes) + 'T').sum()
        # Remove frequencies of 0
        #frequency_over_time = frequency_over_time[frequency_over_time['frequency'] != 0]
        return frequency_over_time
    
    @staticmethod
    def join_dataframes(dataframes: list):
        # Concatenate the dataframes in the list vertically
        merged_data_frame: DataFrame = pandas.concat(dataframes)
        # Sort the dataframe by datetime
        merged_data_frame.sort_values(by='datetime', inplace=True)
        # Reset the index of the merged dataframe
        #merged_data_frame.reset_index(drop=True, inplace=True)
        return merged_data_frame
    
    @staticmethod
    def calculate_matrix_profile(data_frame: DataFrame) -> list[array]:
        # Convert the "frequency" column to float64 dtype
        data = data_frame["frequency"].values.astype(numpy.float64)
        window_size: int = int(len(data) / 2)
        print(f"Window size is {window_size}")
        if not window_size > 3:
            return array
        # Calculate the matrix profiles
        matrix_profile = stump(data, m=window_size)  # You can modify the parameter 'm' as per your requirement
        return [matrix_profile, window_size]

    def plot_log_message_frequencies(self, sorted_log_messages: dict, time_interval_minutes: int):
        # Iterate over log types and append results to the DataFrame
        log_type_data_frames: dict = {}
        matrix_profiles: dict = {}
        for log_type, results in sorted_log_messages.items():
            data_frame: DataFrame = pandas.DataFrame(columns=['log_message', 'date', 'time'])
            for result in results:
                data_frame = pandas.concat([data_frame, pandas.DataFrame({'log_message': [result[0]], 'date': [result[1]], 'time': [result[2]]})], ignore_index=True)      
            log_type_data_frames[log_type] = data_frame
        # Combine date and time columns into a single datetime column
        for log_type, data_frame in log_type_data_frames.items():
            frequency_over_time = self.process_frequency_over_time(data_frame, time_interval_minutes)
            print(frequency_over_time.describe())
            log_type_data_frames[log_type] = frequency_over_time
            matrix_profiles[log_type] = self.calculate_matrix_profile(frequency_over_time)
        log_type_data_frames["ALL"] = self.join_dataframes(log_type_data_frames.values())
        matrix_profiles["ALL"] = self.calculate_matrix_profile(log_type_data_frames["ALL"])

        self.log_analyser.plot_multi_time_series_matrix(log_type_data_frames, matrix_profiles)
        #self.log_analyser.visualise_log_type_time_series(log_type_data_frames)
        #self.log_analyser.visualise_log_type_time_series(matrix_profiles)

    def analyse(self, filters: tuple = ()) -> None:
        log_frequencies: tuple = self.get_log_type_frequencies()
        graph_details: tuple = ("Log Type Frequency", "LOG TYPE", "OCCURENCES")
        self.log_analyser.visualise_bar_graph(graph_details, log_frequencies, True)
        sorted_log_messages: dict = self.get_sorted_log_types()
        self.plot_log_message_frequencies(sorted_log_messages, 15)