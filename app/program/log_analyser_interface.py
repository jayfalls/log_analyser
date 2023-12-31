import asyncio
import sqlite3
import sys
import os
from .components.log_database import LogDatabase
from .components.file_to_database import LogToDatabase
from .components.database_analyser import LogDatabaseAnalyser
from .components.analysis_visualiser import AnalysisVisualiser


class LogAnalyserInterface():
    # VARIABLES
    ## References
    log_database: LogDatabase
    extractor: LogToDatabase
    analyser: LogDatabaseAnalyser
    visualiser: AnalysisVisualiser
    ## States
    analysing: bool = False
    _debug_mode: bool = False
    ### State Changes
    @property
    def debug_mode(self):
        return self._debug_mode
    @debug_mode.setter
    def debug_mode(self, value):
        self._debug_mode = value
        self.log_database.debug_mode = self.debug_mode
    
    # OBJECT CREATION & DELETION
    def __init__(self):
        self.log_database = LogDatabase()
        self.extractor = LogToDatabase()
        self.analyser = LogDatabaseAnalyser()
        self.analyser.log_analyser_interface = self
        self.visualiser = AnalysisVisualiser()
        
    def __del__(self):
        self.log_database.close_database()
    
    def close_database(self) -> None:
        self.log_database.close_database()

    # INNER FUNCTIONS
    def done_analysing(self) -> None:
        self.analysing = False

    ## Database
    def does_database_exist(self) -> bool:
        return self.log_database.does_database_exist()

    ### Variables
    def set_filters(filters: tuple) -> None:
        self.log_database.filters = filters

    ### Read/Write
    async def add_log_to_database(self, log_path: str) -> None:
        await self.extractor.log_to_database(self.log_database, log_path)

    def commit_to_database(self) -> None:
        self.log_database.commit_to_database()

    def write_line_to_database(self, log_line: dict) -> None:
        self.log_database.write_line_to_database(log_line)
    
    ### Querying
    def get_logs(self) -> tuple:
        return self.log_database.get_logs()

    def get_log_type_frequencies(self) -> tuple:
        return self.log_database.get_log_type_frequencies()

    def get_source_frequencies(self) -> tuple:
        return self.log_database.get_source_frequencies()

    def get_sorted_log_types(self) -> dict:
        return self.log_database.get_sorted_log_types()
    
    def get_sorted_sources(self) -> dict:
        return self.log_database.get_sorted_sources()
    
    ## Log To Database
    async def log_to_database(self, path_to_log: str) -> None:
        await self.extractor.log_to_database(self, path_to_log)

    ## Analysis Visualisation
    def visualise_bar_graph(self, graph_details: tuple, xy_array: tuple, shuffle: bool = False) -> None:
        self.visualiser.visualise_bar_graph(graph_details, xy_array, shuffle)
    
    def visualise_histogram(self, values: tuple) -> None:
        self.visualiser.visualise_histogram(values)
    
    def visualise_time_series(self, data_frame, title: str) -> None:
        self.visualiser.visualise_time_series(data_frame, title)
    
    def visualise_multi_time_series_matrix(self, graphs: dict) -> None:
        self.visualiser.visualise_multi_time_series_matrix(graphs)
    
    def add_analysis_insights(self, insights: dict) -> None:
        self.visualiser.add_analysis_insights(insights)

    def show_plot(self) -> None:
        self.visualiser.show_plot()
    
    # OUTER FUNCTIONS
    async def import_logs(self, log_paths: set) -> None:
        self.log_database.initialise_database()
        if not log_paths:
            return
        if len(log_paths) == 1:
            await self.log_to_database(log_paths.pop())
        else:
            load_tasks: list = []
            for log_path in log_paths:
                task: asyncio.Task = asyncio.create_task(self.log_to_database(log_path))
                load_tasks.append(task)
            await load_tasks[-1]

    def analyse(self) -> None:
        self.log_database.initialise_database()
        self.analysing = True
        self.analyser.analyse()

    def clear_database(self) -> None:
        self.log_database.initialise_database()
        self.log_database.clear_database()
    
    def get_time_interval(self) -> int:
        return self.analyser.time_interval_minutes
    
    def get_window_modifier(self) -> int:
        return self.analyser.matrix_window_modifier
    
    def get_match_percent(self) -> int:
        return self.analyser.matching_graph_percent
    
    def get_threshold_percent(self) -> int:
        return self.analyser.matrix_anomaly_threshold_percent

    def update_time_interval(self, time_interval: int) -> None:
        self.analyser.time_interval_minutes = time_interval
    
    def update_window_modifier(self, window_modifier: int) -> None:
        self.analyser.matrix_window_modifier = window_modifier
    
    def update_match_percent(self, match_percent: int) -> None:
        self.analyser.matching_graph_percent = match_percent
    
    def update_threshold_percent(self, threshold_percent: int) -> None:
        self.analyser.matrix_anomaly_threshold_percent = threshold_percent