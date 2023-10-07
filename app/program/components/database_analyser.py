import matplotlib.pyplot as plot
import numpy
from numpy import array
import pandas
from pandas import DataFrame
from stumpy import stump
import sys


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
    # | log_analyser_interface | Must be assigned by log_analyser_interface
    ## Tuning
    time_interval_minutes: int = 2 # How long time series should be measured in
    matrix_window_modifier: int = 15 # What fraction the matrix profile segments should be split into
    ## Results
    all_type_frame: DataFrame
    seperated_type_frames: dict = {}
    seperated_matrixes: dict = {}
    all_matrix_profile: array
    ## Analysis
    ### Patterns
    matching_graph_percent: int = 100 # The percent that two graphs need to be the same to be considered matching
    ### Anomalies
    matrix_anomaly_threshold_percent: int = 98
    matrix_anomaly_threshold: float = 0

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
    def get_frequency_time(self, results: list) -> DataFrame:
        data_frame: DataFrame = pandas.DataFrame(columns=["log_message", "date", "time"])
        for result in results:
            data_frame = pandas.concat([data_frame, pandas.DataFrame({"log_message": [result[0]], "date": [result[1]], "time": [result[2]]})], ignore_index=True)      
        frequency_over_time = self.process_frequency_over_time(data_frame)
        return frequency_over_time

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
    def plot_message_frequencies(self, sorted_messages: dict) -> dict:
        data_frames: dict = {}
        for key, results in sorted_messages.items():
            frequency_over_time: DataFrame = self.get_frequency_time(results)
            data_frames[key] = frequency_over_time
        return data_frames
    
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
            matrix_profiles[key] = matrix_profile
        return (data_frames, matrix_profiles)
    
    ## Hourly Freq
    def get_hourly_frequencies(self) -> DataFrame:
        hourly_avg: DataFrame = self.all_type_frame.resample("H").sum()
        return hourly_avg
    
    # ANALYSIS
    ## Patterns
    def get_matching_graphs(self) -> list[tuple]:
        matching_names: list[tuple] = []
        # Get the list of dataframe names
        graph_names: list[str] = list(self.seperated_type_frames.keys())
        print(self.seperated_type_frames)
        already_matched_names: list = []
        # Perform two-way comparison for each pair of dataframes
        for index in range(len(graph_names)):
            for secondary_index in range(len(graph_names)):
                if index == secondary_index:
                    continue
                graph1_name = graph_names[index]
                graph2_name = graph_names[secondary_index]
                graph1 = self.seperated_type_frames[graph1_name]
                graph2 = self.seperated_type_frames[graph2_name]
                # Calculate the number of matching values
                matching_values = (graph1['frequency'] == graph2['frequency']).sum()
                # Calculate the percentage of matching values
                percentage_matched: float = matching_values / len(graph1) * 100
                # Check if the percentage exceeds the threshold
                if percentage_matched > self.matching_graph_percent:
                    combined_names: str = graph1_name + graph2_name
                    reverse_combined_names: str = graph2_name + graph1_name
                    if combined_names in already_matched_names:
                        continue
                    already_matched_names.append(combined_names)
                    already_matched_names.append(reverse_combined_names)
                    matching_names.append((graph1_name, graph2_name, percentage_matched))
        return matching_names

    def get_matching_motif_indices(self) -> None:
        matrix_profile = self.all_matrix_profile[:, 0]
        motif: float = numpy.argmin(matrix_profile)
        matching_indices = numpy.where(matrix_profile == motif)
        #print(matching_indices)

    ## Anomalies
    @staticmethod
    def get_mismatched_ocurrences(data_frame1: DataFrame, data_frame2: DataFrame) -> DataFrame:
        data_frame1 = data_frame1.reset_index()
        data_frame2 = data_frame2.reset_index()
        merged_data_frame: DataFrame = pandas.merge(data_frame1, data_frame2, on="datetime", how="outer", suffixes=("_1", "_2"))
        merged_data_frame["mismatch"] = (merged_data_frame["frequency_1"] != merged_data_frame["frequency_2"])
        mismatch_data_frame: DataFrame = merged_data_frame[merged_data_frame["mismatch"]][["datetime", "mismatch"]] # Only returns collums where the collum "mismatch" contains true
        mismatch_data_frame = mismatch_data_frame.set_index("datetime")
        return mismatch_data_frame
    
    def calculate_threshold(self, matrix_profile) -> None:
        first_column = matrix_profile[:, 0]
        highest_value: float = numpy.max(first_column)
        threshold: float = highest_value * self.matrix_anomaly_threshold_percent  / 100
        self.matrix_anomaly_threshold = threshold

    def get_anomaly_indexes_above_threshold(self, matrix_profile) -> array:
        self.calculate_threshold(matrix_profile)
        first_column = matrix_profile[:, 0]
        above_threshold_indices: array = numpy.where(first_column > self.matrix_anomaly_threshold)
        return above_threshold_indices[0]
    
    ## Temporal Trends
    

    # VISUALISATION
    ## Bar Graphs
    def plot_log_type_frequencies(self) -> None:
        log_type_frequencies: tuple = self.log_analyser_interface.get_log_type_frequencies()
        graph_details: tuple = ("Log Type Frequency", "LOG TYPE", "OCCURENCES")
        self.log_analyser_interface.visualise_bar_graph(graph_details, log_type_frequencies, True)
    
    def plot_source_frequencies(self) -> None:
        source_frequencies: tuple = self.log_analyser_interface.get_source_frequencies()
        graph_details: tuple = ("Source Frequency", "SOURCE", "OCCURENCES")
        self.log_analyser_interface.visualise_bar_graph(graph_details, source_frequencies, True)

    ## Histogram
    def plot_log_type_histo(self) -> None:
        log_type_frequencies: tuple = self.log_analyser_interface.get_log_type_frequencies()
        self.log_analyser_interface.visualise_histogram(log_type_frequencies[1])

    ## Time Series Graphs
    def plot_frequency_matrix(self, sorted_type_messages: dict, sorted_source_messages: dict, ignore_all: bool = False) -> None:
        frequency_data_frames, matrix_profiles = self.plot_message_frequencies_matrix(sorted_type_messages)
        all_type_frame, self.seperated_type_frames = seperate_all_from_dict(frequency_data_frames)
        self.all_type_frame = all_type_frame[ALL_KEY]
        all_matrixes, self.seperated_matrixes = seperate_all_from_dict(matrix_profiles)
        self.all_matrix_profile = all_matrixes[ALL_KEY][0]
        source_data_frames: dict = self.plot_message_frequencies(sorted_source_messages)
        hourly_frequencies: DataFrame = self.get_hourly_frequencies()
        graphs: dict = {
            "Types Frequency": self.seperated_type_frames,
            "Sources Frequency": source_data_frames,
            "Matrix Profile": self.seperated_matrixes,
            "Hourly Frequency": hourly_frequencies
        }
        if not ignore_all:
            self.log_analyser_interface.visualise_time_series(self.all_type_frame, f"{ALL_KEY} Log Messages")
        self.log_analyser_interface.visualise_multi_time_series_matrix(graphs)
            
    def plot_log_types_sources_over_time(self) -> None:
        sorted_log_type_messages: dict = self.log_analyser_interface.get_sorted_log_types()
        sorted_source_messages: dict = self.log_analyser_interface.get_sorted_sources()
        self.plot_frequency_matrix(sorted_log_type_messages, sorted_source_messages)
    
    def plot_insights(self) -> None:
        insights: dict = {}
        matching_graphs: list[tuple] = self.get_matching_graphs()
        if matching_graphs != []:
            insights["PERCENT_MATCHED"] = matching_graphs
            non_match_anomalies: list = []
            for name1, name2, _ in matching_graphs:
                non_match_anomalies.append(self.get_mismatched_ocurrences(self.seperated_type_frames[name1], self.seperated_type_frames[name2]))
            insights["NON_MATCH_ANOMALIES"] = non_match_anomalies
        threshold_anomaly_indexes: array = self.get_anomaly_indexes_above_threshold(self.seperated_matrixes["ERROR"][0])
        threshold_anomalies: tuple = (self.matrix_anomaly_threshold, threshold_anomaly_indexes)
        insights["THRESHOLD_ANOMALIES"] = threshold_anomalies
        self.log_analyser_interface.add_analysis_insights(insights)
        self.get_matching_motif_indices()
    
    # OUTER FUNCTIONS
    def analyse(self) -> None:
        print("thinking...")
        sys.stdout.flush()
        self.plot_log_type_frequencies()
        self.log_analyser_interface.show_plot()
        #self.plot_log_type_histo()
        self.log_analyser_interface.show_plot()
        self.plot_source_frequencies()
        self.plot_log_types_sources_over_time()
        self.plot_insights()
        self.log_analyser_interface.show_plot()
        print("done thinking")
        self.log_analyser_interface.done_analysing()