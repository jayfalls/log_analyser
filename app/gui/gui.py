import asyncio
import tkinter as tk
from tkinter import filedialog

class GUI:
    # Variables
    ## References
    # | log_analyser_interface | Must be assigned by log_analyser
    ## Save/Load
    log_files = ['log_file1.log', 'log_file2.log', 'log_file3.log', 'log_file2.log', 'log_file2.log', 'log_file2.log', 'log_file2.log', 'log_file2.log', 'log_file2.log']  # Example list of log file names
    log_file_vars = []  # To store the Tkinter IntVar objects for checkboxes

    # INITIALISATION
    ## Creation
    def create_bottom_panel(self) -> None:
        # Create a frame for the bottom panel
        panel_frame = tk.Frame(self.root, height=10)
        panel_frame.pack(side=tk.BOTTOM, fill=tk.X)
        ### Panel
        self.panel = tk.Frame(panel_frame, bg='gray', height=10)
        self.panel.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
    
    def create_import_files_button(self) -> None:
        self.select_button = tk.Button(self.panel, text="Import Files", command=self.select_files)
        self.select_button.pack(pady=10)
    
    def populate_checkboxes(self) -> None:
        self.checkbox_frame = tk.Frame(self.panel)
        self.checkbox_frame.pack(pady=10)
        # Set the number of columns for the checkbox frame based on the number of log files
        num_files = len(self.log_files)
        num_columns = 4  # You can adjust the number of columns as per your requirement
        num_rows = (num_files + num_columns - 1) // num_columns

        # Create a list to hold the checkboxes for each row
        checkbox_rows = []

        # Create a new row for each row index
        for row_index in range(num_rows):
            # Create a new frame for each row
            row_frame = tk.Frame(self.checkbox_frame)
            row_frame.pack(side=tk.TOP, anchor=tk.W)

            # Add the checkboxes to the current row
            for column_index in range(num_columns):
                # Calculate the index of the current log file
                file_index = row_index * num_columns + column_index

                if file_index < num_files:
                    var = tk.IntVar()
                    checkbox = tk.Checkbutton(row_frame, text=self.log_files[file_index], variable=var)
                    checkbox.pack(side=tk.LEFT, anchor=tk.W)
                    self.log_file_vars.append(var)

                    # Add the checkbox to the current row
                    checkbox.pack(side=tk.LEFT, anchor=tk.W)

            # Add the current row to the list of checkbox rows
            checkbox_rows.append(row_frame)
    
    def __init__(self, interface):
        self.log_analyser_interface = interface
        self.root = tk.Tk()
        self.root.title("File Selector")
        self.create_bottom_panel()
        self.create_import_files_button()
        self.populate_checkboxes()
        self.root.mainloop()

    # FILE IMPORTING
    def select_files(self):
        selected_files = []
        for i, var in enumerate(self.log_file_vars):
            if var.get() == 1:
                selected_files.append(self.log_files[i])

        if len(selected_files) == 0:
            return

        asyncio.run(self.log_analyser_interface.import_logs(selected_files))