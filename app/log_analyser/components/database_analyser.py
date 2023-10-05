import matplotlib.pyplot as plot
import numpy
from numpy import array
import pandas
from pandas import DataFrame
from stumpy import stump


# VARIABLES
## Constants
ALL_KEY: str = "ALL"


# HELPER FUNCTIONS
def seperate_all_from_dict(contains_all_key: dict) -> tuple:
    all_dict = {}
    cleaned_dict = {}
    for key, value in contains_all_key.items():
        if key == ALL_KEY:
            all_dict[ALL_KEY] = value
            continue
        cleaned_dict[key] = value
    return (all_dict, cleaned_dict)
    

# LOG DATABASE ANALYSER
class LogDatabaseAnalyser():
    # VARIABLES
    ## References
    # | log_analyser | Must be assigned by log_analyser interface
    ## States
    time_interval_minutes: int = 2
    matrix_window_modifier: int = 20

    # TIME SERIES
    ## Frequency Over Time
    def process_frequency_over_time(self, data_frame: DataFrame):
        data_frame["datetime"] = pandas.to_datetime(data_frame["date"] + " " + data_frame["time"])
        data_frame.drop(["date", "time"], axis=1, inplace=True)
        data_frame.set_index("datetime", inplace=True)
        frequency_over_time = data_frame.groupby("datetime").count()
        frequency_over_time.columns = ["frequency"]
        # Resample the data to the specified time interval and count the occurrences
        frequency_over_time = frequency_over_time.resample(str(self.time_interval_minutes) + "T").sum()
        return frequency_over_time
    
    ## Freq/Time Matrix Profile
    def calculate_matrix_profile(self, data_frame: DataFrame) -> tuple:
        data = data_frame["frequency"].values.astype(numpy.float64)
        window_size: int = int(len(data_frame) / self.matrix_window_modifier)
        if not window_size > 3:
            return None
        matrix_profile = stump(data, m=window_size)
        return (matrix_profile, window_size)
    
    ## Freq/Time & Matrix Merged
    def get_frequency_time_matrix(self, results: list) -> tuple:
        frequency_time_matrix: list = []
        data_frame: DataFrame = pandas.DataFrame(columns=["log_message", "date", "time"])
        for result in results:
            data_frame = pandas.concat([data_frame, pandas.DataFrame({"log_message": [result[0]], "date": [result[1]], "time": [result[2]]})], ignore_index=True)      
        frequency_over_time = self.process_frequency_over_time(data_frame)
        matrix_profile: tuple = self.calculate_matrix_profile(frequency_over_time)
        if matrix_profile is None:
            return None
        frequency_time_matrix.append(frequency_over_time)
        frequency_time_matrix.append(matrix_profile)
        return tuple(frequency_time_matrix)

    ## Dictionary Sorting
    def plot_message_frequencies_matrix(self, sorted_messages: dict) -> tuple:
        data_frames: dict = {}
        matrix_profiles: dict = {}
        all_results: list = [result for results in sorted_messages.values() for result in results]
        sorted_messages[ALL_KEY] = all_results
        for key, results in sorted_messages.items():
            frequency_time_matrix: tuple = self.get_frequency_time_matrix(results)
            if frequency_time_matrix is None:
                continue
            frequency_over_time, matrix_profile = frequency_time_matrix
            data_frames[key] = frequency_over_time
            if key == ALL_KEY:
                continue
            matrix_profiles[key] = matrix_profile
        return (data_frames, matrix_profiles)
    
    # ANOMALY DETECTION
    @staticmethod
    def get_mismatched_frequencies(data_frame1: DataFrame, data_frame2: DataFrame) -> DataFrame:
        data_frame1 = data_frame1.reset_index()
        data_frame2 = data_frame2.reset_index()
        merged_data_frame: DataFrame = pandas.merge(data_frame1, data_frame2, on="datetime", how="outer", suffixes=("_1", "_2"))
        merged_data_frame["mismatch"] = (merged_data_frame["frequency_1"] != merged_data_frame["frequency_2"])
        mismatch_data_frame: DataFrame = merged_data_frame[merged_data_frame["mismatch"]][["datetime", "mismatch"]] # Only returns collums where the collum "mismatch" contains true
        mismatch_data_frame = mismatch_data_frame.set_index("datetime")
        return mismatch_data_frame

    # ANALYSIS
    ## Bar Graphs
    def plot_log_type_frequencies(self) -> None:
        log_type_frequencies: tuple = self.log_analyser.get_log_type_frequencies()
        graph_details: tuple = ("Log Type Frequency", "LOG TYPE", "OCCURENCES")
        self.log_analyser.visualise_bar_graph(graph_details, log_type_frequencies, True)
    
    def plot_source_frequencies(self) -> None:
        source_frequencies: tuple = self.log_analyser.get_source_frequencies()
        graph_details: tuple = ("Source Frequency", "SOURCE", "OCCURENCES")
        self.log_analyser.visualise_bar_graph(graph_details, source_frequencies, True)

    ## Time Series Graphs
    def plot_frequency_matrix(self, sorted_messages: dict, ignore_all: bool = False) -> None:
        data_frames, matrix_profiles = self.plot_message_frequencies_matrix(sorted_messages)
        all_frame, seperated_frames = seperate_all_from_dict(data_frames)
        all_matrixes, seperated_matrixes = seperate_all_from_dict(matrix_profiles)
        if not ignore_all:
            self.log_analyser.visualise_time_series(all_frame[ALL_KEY], f"{ALL_KEY} Log Messages")
        self.log_analyser.plot_multi_time_series_matrix(seperated_frames, seperated_matrixes)
        
        if "ERROR" in seperated_frames.keys():
            self.get_mismatched_frequencies(seperated_frames["ERROR"], seperated_frames["STACKTRACE"])
    
    def plot_log_types_over_time(self) -> None:
        sorted_log_type_messages: dict = self.log_analyser.get_sorted_log_types()
        self.plot_frequency_matrix(sorted_log_type_messages)

    def plot_sources_over_time(self) -> None:
        sorted_source_messages: dict = self.log_analyser.get_sorted_sources()
        self.plot_frequency_matrix(sorted_source_messages, ignore_all=True)
    
    # OUTER FUNCTION
    def analyse(self) -> None:
        self.plot_log_type_frequencies()
        self.plot_source_frequencies()
        self.plot_log_types_over_time()
        self.plot_sources_over_time()