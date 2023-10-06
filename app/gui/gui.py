import asyncio
import json
import os
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog


# VARIABLES
## Constants
MIN_TIME_INTERVAL: int = 1
MAX_TIME_INTERVAL: int = 240
MIN_WINDOW_MODIFIER: int = 2
MAX_WINDOW_MODIFIER: int = 40
MIN_MATCH_PERCENT: int = 70
MAX_MATCH_PERCENT: int = 99
MIN_THRESHOLD_PERCENT: int = 20
MAX_THRESHOLD_PERCENT: int = 99


class GUI:
    # Variables
    ## References
    # | log_analyser_interface | Must be assigned by log_analyser
    default_time_interval: int = 1
    default_window_modifier: int = 1
    default_matching_graph_percent: int = 1
    default_anomaly_threshold_percent: int = 1

    # CREATION
    ## Default Values
    def assign_default_values(self) -> None:
        self.default_time_interval: int = self.log_analyser_interface.get_time_interval()
        self.default_window_modifier: int = self.log_analyser_interface.get_window_modifier()
        self.default_matching_graph_percent: int = self.log_analyser_interface.get_match_percent()
        self.default_anomaly_threshold_percent: int = self.log_analyser_interface.get_threshold_percent()

    ## Components
    def create_bottom_panel(self) -> None:
        # Create a frame for the bottom panel
        panel_frame = tk.Frame(self.root, height=10)
        panel_frame.pack(side=tk.BOTTOM, fill=tk.X)
        ### Panel
        self.panel = tk.Frame(panel_frame, bg='gray', height=10)
        self.panel.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
    
    def create_input_fields(self) -> None:
        # Time Interval Minutes
        self.time_interval_label = tk.Label(self.panel, text="Time Interval Minutes")
        self.time_interval_label.pack()
        self.time_interval_slider = ttk.Scale(self.panel, from_=MIN_TIME_INTERVAL, to=MAX_TIME_INTERVAL) 
        self.time_interval_slider.set(self.default_time_interval)
        self.time_interval_slider.pack(pady=5)
        self.time_interval_apply = tk.Button(self.panel, text="Apply", state=tk.DISABLED, command=self.apply_time_interval)
        self.time_interval_apply.pack(pady=5)

        # Matrix Window Modifer
        self.matrix_window_label = tk.Label(self.panel, text="Matrix Window Modifer")
        self.matrix_window_label.pack()
        self.matrix_window_slider = ttk.Scale(self.panel, from_=MIN_WINDOW_MODIFIER, to=MAX_WINDOW_MODIFIER) 
        self.matrix_window_slider.set(self.default_window_modifier)
        self.matrix_window_slider.pack(pady=5)
        self.matrix_window_apply = tk.Button(self.panel, text="Apply", state=tk.DISABLED, command=self.apply_matrix_window)
        self.matrix_window_apply.pack(pady=5)

        # Matching Graph Percent
        self.matching_graph_label = tk.Label(self.panel, text="Matching Graph Percent")
        self.matching_graph_label.pack()
        self.matching_graph_slider = ttk.Scale(self.panel, from_=MIN_MATCH_PERCENT, to=MAX_MATCH_PERCENT) 
        self.matching_graph_slider.set(self.default_matching_graph_percent)
        self.matching_graph_slider.pack(pady=5)
        self.matching_graph_apply = tk.Button(self.panel, text="Apply", state=tk.DISABLED, command=self.apply_matching_graph)
        self.matching_graph_apply.pack(pady=5)

        # Matrix Anomaly Threshold Percent
        self.matrix_anomaly_label = tk.Label(self.panel, text="Matrix Anomaly Threshold Percent")
        self.matrix_anomaly_label.pack()
        self.matrix_anomaly_slider = ttk.Scale(self.panel, from_=MIN_THRESHOLD_PERCENT, to=MAX_THRESHOLD_PERCENT) 
        self.matrix_anomaly_slider.set(self.default_anomaly_threshold_percent)
        self.matrix_anomaly_slider.pack(pady=5)
        self.matrix_anomaly_apply = tk.Button(self.panel, text="Apply", state=tk.DISABLED, command=self.apply_matrix_anomaly)
        self.matrix_anomaly_apply.pack(pady=5)

        self.update_all_labels()

        # Add trace to update buttons on input
        self.time_interval_slider.bind('<Motion>', self.update_time_interval_label)
        self.matrix_window_slider.bind('<Motion>', self.update_matrix_window_label)
        self.matching_graph_slider.bind('<Motion>', self.update_matching_graph_label)
        self.matrix_anomaly_slider.bind('<Motion>', self.update_matrix_anomaly_label)
    
    def create_import_files_button(self) -> None:
        self.select_button = tk.Button(self.panel, text="Import Files", command=self.import_files)
        self.select_button.pack(pady=10)
        
    def create_analyse_database_button(self) -> None:
        self.analyse_button = tk.Button(self.panel, text="Analyse Database", command=self.analyse)
        self.analyse_button.pack(pady=10)
    
    def create_clear_database_button(self) -> None:
        self.clear_button = tk.Button(self.panel, text="Clear Database", command=self.clear_database)
        self.clear_button.pack(pady=10)
    
    def __init__(self, interface):
        self.log_analyser_interface = interface
        self.assign_default_values()
        self.root = tk.Tk()
        self.root.title("File Selector")
        self.create_bottom_panel()
        self.create_input_fields()
        self.create_import_files_button()
        self.create_analyse_database_button()
        self.create_clear_database_button()
        self.enable_all_buttons()
        self.root.mainloop()

    # FILE IMPORTING
    def import_files(self):
        selected_files: list[str] = []
        file_paths = filedialog.askopenfilenames(filetypes=[("Log Files", "*.log")])
        for path in file_paths:
            if path.endswith(".log"):
                selected_files.append(path)
        if not selected_files:
            return
        asyncio.run(self.log_analyser_interface.import_logs(selected_files))
        self.enable_all_buttons()
    
    def analyse(self) -> None:
        self.disable_all_buttons()
        self.log_analyser_interface.analyse()
        while self.log_analyser_interface.analysing:
            pass
        self.enable_all_buttons()
        
    def clear_database(self) -> None:
        self.log_analyser_interface.clear_database()
        self.enable_all_buttons()

    # COMPONENTS
    def disable_all_buttons(self) -> None:
        self.select_button.config(state=tk.DISABLED)
        self.analyse_button.config(state=tk.DISABLED)
        self.clear_button.config(state=tk.DISABLED)
    
    def disable_database_buttons(self) -> None:
        self.analyse_button.config(state=tk.DISABLED)
        self.clear_button.config(state=tk.DISABLED)
    
    def enable_all_buttons(self) -> None:
        self.select_button.config(state=tk.NORMAL)
        self.analyse_button.config(state=tk.NORMAL)
        self.clear_button.config(state=tk.NORMAL)
        self.check_button_status()
    
    def enable_database_buttons(self) -> None:
        self.analyse_button.config(state=tk.NORMAL)
        self.clear_button.config(state=tk.NORMAL)
    
    def check_button_status(self) -> None:
        self.disable_database_buttons()
        self.hide_fields()
        if self.log_analyser_interface.does_database_exist():
            self.show_fields()
            self.enable_database_buttons()
    
    def hide_fields(self) -> None:
        self.time_interval_label.pack_forget()
        self.time_interval_slider.pack_forget()
        self.matrix_window_label.pack_forget()
        self.matrix_window_slider.pack_forget()
        self.matching_graph_label.pack_forget()
        self.matching_graph_slider.pack_forget()
        self.matrix_anomaly_label.pack_forget()
        self.matrix_anomaly_slider.pack_forget()
        self.time_interval_apply.pack_forget()
        self.matrix_window_apply.pack_forget()
        self.matching_graph_apply.pack_forget()
        self.matrix_anomaly_apply.pack_forget()
    
    def show_fields(self) -> None:
        self.time_interval_label.pack()
        self.time_interval_slider.pack()
        self.matrix_window_label.pack()
        self.matrix_window_slider.pack()
        self.matching_graph_label.pack()
        self.matching_graph_slider.pack()
        self.matrix_anomaly_label.pack()
        self.matrix_anomaly_slider.pack()
        self.time_interval_apply.pack()
        self.matrix_window_apply.pack()
        self.matching_graph_apply.pack()
        self.matrix_anomaly_apply.pack()

    def update_time_interval_label(self, event):
        self.update_time_interval_button()
        value = int(self.time_interval_slider.get())
        self.time_interval_label.config(text=f"Time Interval Minutes: {value}")
        

    def update_matrix_window_label(self, event):
        self.update_matrix_window_button()
        value = int(self.matrix_window_slider.get())
        self.matrix_window_label.config(text=f"Matrix Window Modifier: {value}")
        

    def update_matching_graph_label(self, event):
        self.update_matching_graph_button()
        value = int(self.matching_graph_slider.get())
        self.matching_graph_label.config(text=f"Matching Graph Percent: {value}%")
        

    def update_matrix_anomaly_label(self, event):
        self.update_matrix_anomaly_button()
        value = int(self.matrix_anomaly_slider.get())
        self.matrix_anomaly_label.config(text=f"Matrix Anomaly Threshold Percent: {value}%")
        
    # Update apply button status
    def update_time_interval_button(self):
        self.disable_time_interval_button()
        if self.time_interval_slider.get() != self.default_time_interval:
            self.enable_time_interval_button()
            

    def update_matrix_window_button(self):
        self.disable_time_interval_button()
        if self.matrix_window_slider.get() != self.default_window_modifier:
            self.enable_time_interval_button()            

    def update_matching_graph_button(self):
        self.disable_time_interval_button()
        if self.matching_graph_slider.get() != self.default_matching_graph_percent:
            self.enable_time_interval_button()
           
    def update_matrix_anomaly_button(self):
        self.disable_time_interval_button()
        if self.matrix_anomaly_slider.get() != self.default_anomaly_threshold_percent:
            self.enable_time_interval_button()
            
    
    def update_all_labels(self):
        # Update Time Interval label
        time_interval_value = int(self.time_interval_slider.get())
        self.time_interval_label.config(text=f"Time Interval Minutes: {time_interval_value}")

        # Update Matrix Window Modifier label
        matrix_window_value = int(self.matrix_window_slider.get())
        self.matrix_window_label.config(text=f"Matrix Window Modifier: {matrix_window_value}")

        # Update Matching Graph Percent label
        matching_graph_value = int(self.matching_graph_slider.get())
        self.matching_graph_label.config(text=f"Matching Graph Percent: {matching_graph_value}%")

        # Update Matrix Anomaly Threshold Percent label
        matrix_anomaly_value = int(self.matrix_anomaly_slider.get())
        self.matrix_anomaly_label.config(text=f"Matrix Anomaly Threshold Percent: {matrix_anomaly_value}%")

    # Enable/disable apply buttons
    def enable_time_interval_button(self):
        self.time_interval_apply.config(state=tk.NORMAL)

    def disable_time_interval_button(self):
        self.time_interval_apply.config(state=tk.DISABLED)

    def enable_matrix_window_button(self):
        self.matrix_window_apply.config(state=tk.NORMAL)

    def disable_matrix_window_button(self):
        self.matrix_window_apply.config(state=tk.DISABLED)

    def enable_matching_graph_button(self):
        self.matching_graph_apply.config(state=tk.NORMAL)

    def disable_matching_graph_button(self):
        self.matching_graph_apply.config(state=tk.DISABLED)

    def enable_matrix_anomaly_button(self):
        self.matrix_anomaly_apply.config(state=tk.NORMAL)

    def disable_matrix_anomaly_button(self):
        self.matrix_anomaly_apply.config(state=tk.DISABLED)

    # Apply functions
    def apply_time_interval(self):
        self.log_analyser_interface.update_time_interval(int(self.time_interval_slider.get()))
        self.assign_default_values()

    def apply_matrix_window(self):
        self.log_analyser_interface.update_window_modifier(int(self.matrix_window_slider.get()))
        self.assign_default_values()

    def apply_matching_graph(self):
        self.log_analyser_interface.update_match_percent(int(self.matching_graph_slider.get()))
        self.assign_default_values()

    def apply_matrix_anomaly(self):
        self.log_analyser_interface.update_threshold_percent(int(self.matrix_anomaly_slider.get()))
        self.assign_default_values()