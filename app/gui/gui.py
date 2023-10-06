import asyncio
import json
import os
import tkinter as tk
from tkinter import filedialog


class GUI:
    # Variables
    ## References
    # | log_analyser_interface | Must be assigned by log_analyser
    
    ## Components
    def create_bottom_panel(self) -> None:
        # Create a frame for the bottom panel
        panel_frame = tk.Frame(self.root, height=10)
        panel_frame.pack(side=tk.BOTTOM, fill=tk.X)
        ### Panel
        self.panel = tk.Frame(panel_frame, bg='gray', height=10)
        self.panel.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
    
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
        self.root = tk.Tk()
        self.root.title("File Selector")
        self.create_bottom_panel()
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
        if not self.log_analyser_interface.does_database_exist():
            self.disable_database_buttons()
            return
        self.enable_database_buttons()
