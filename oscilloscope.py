#!/usr/bin/env python3
"""
oscilloscope_analysis.py

This script loads an oscilloscope CSV file that contains metadata in the first few rows
followed by the actual data. The data portion must start with a header row beginning with
"TIME", e.g.:
    
    TIME,CH1,CH2
    -4.97000e-05,-0.16,0.4
    -4.96990e-05,-0.08,0.4
    ...

By default, the script uses the "TIME" column for the x‑axis and "CH1" for the y‑axis.
You can change the channel to analyze using the "--channel" option.

Interactive Measurement Options:
  1: Click two points to measure the differences in x (time) and y (voltage).
  2: Click two points (defining an x‑axis region) to compute the peak‑to‑peak voltage in that region.
  q: Quit the interactive mode.
  
Usage:
    python oscilloscope_analysis.py path/to/your_file.csv [--channel CH1]

Example:
    python oscilloscope_analysis.py osc_data.csv --channel CH2
"""

import argparse
import sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import os

def load_csv(filename, channel):
    """
    Loads an oscilloscope CSV file with a metadata header.
    
    The function searches for the header row that starts with "TIME" and then uses that row
    (and all following rows) as the CSV data.
    
    Parameters:
      filename (str): Path to the CSV file.
      channel (str): Name of the channel to use (e.g., "CH1" or "CH2").
      
    Returns:
      tuple: (time, voltage) arrays.
    """
    header_index = None
    with open(filename, 'r') as f:
        lines = f.readlines()
    for i, line in enumerate(lines):
        # Look for the header line that starts with "TIME"
        if line.strip().startswith("TIME"):
            header_index = i
            break
    if header_index is None:
        print("Error: Could not find header row starting with 'TIME' in the file.")
        sys.exit(1)
        
    # Use pandas to load the CSV, skipping all rows before the header.
    try:
        df = pd.read_csv(filename, skiprows=header_index)
    except Exception as e:
        print(f"Error reading CSV data: {e}")
        sys.exit(1)
        
    # Verify that the expected columns are present.
    if "TIME" not in df.columns:
        print("Error: CSV file does not contain a 'TIME' column.")
        sys.exit(1)
    if channel not in df.columns:
        print(f"Error: CSV file does not contain channel '{channel}'. Available columns: {df.columns.tolist()}")
        sys.exit(1)
    
    # Return the TIME and selected channel data as numpy arrays.
    time = df["TIME"].values
    voltage = df[channel].values
    return time, voltage

class OscilloscopeViewer(tk.Tk):
    def __init__(self):
        super().__init__()

        # Get the directory where the script is located
        self.script_dir = os.path.dirname(os.path.abspath(__file__))

        self.title("Oscilloscope Data Viewer")
        self.geometry("1200x800")

        # Create main container
        self.main_frame = ttk.Frame(self)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Control panel with better organization
        self.control_frame = ttk.LabelFrame(self.main_frame, text="Controls")
        self.control_frame.pack(fill=tk.X, padx=5, pady=5)

        # File controls
        self.file_controls = ttk.Frame(self.control_frame)
        self.file_controls.pack(side=tk.LEFT, padx=5)
        
        ttk.Button(self.file_controls, text="Open Root Folder", command=self.load_data_folder).pack(side=tk.LEFT, padx=5)
        ttk.Button(self.file_controls, text="Refresh Files", command=self.refresh_files).pack(side=tk.LEFT, padx=5)
        
        # Channel toggles
        self.ch1_var = tk.BooleanVar(value=True)
        self.ch2_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(self.control_frame, text="CH1", variable=self.ch1_var, command=self.update_plot).pack(side=tk.LEFT, padx=5)
        ttk.Checkbutton(self.control_frame, text="CH2", variable=self.ch2_var, command=self.update_plot).pack(side=tk.LEFT, padx=5)

        # File browser with tree view for better navigation
        self.files_frame = ttk.LabelFrame(self.main_frame, text="Data Files")
        self.files_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Create tree view with scrollbars
        self.tree_frame = ttk.Frame(self.files_frame)
        self.tree_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.tree_scroll_y = ttk.Scrollbar(self.tree_frame)
        self.tree_scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.tree_scroll_x = ttk.Scrollbar(self.tree_frame, orient='horizontal')
        self.tree_scroll_x.pack(side=tk.BOTTOM, fill=tk.X)
        
        self.file_tree = ttk.Treeview(self.tree_frame, 
                                     yscrollcommand=self.tree_scroll_y.set,
                                     xscrollcommand=self.tree_scroll_x.set,
                                     selectmode='browse')
        self.file_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        self.tree_scroll_y.config(command=self.file_tree.yview)
        self.tree_scroll_x.config(command=self.file_tree.xview)
        
        # Configure tree columns
        self.file_tree["columns"] = ("path",)
        self.file_tree.column("#0", width=200)
        self.file_tree.column("path", width=400)
        self.file_tree.heading("#0", text="File Name")
        self.file_tree.heading("path", text="Path")
        
        self.file_tree.bind('<<TreeviewSelect>>', self.on_file_select)

        # Plot area
        self.fig = Figure(figsize=(10, 6))
        self.ax = self.fig.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.main_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Add navigation toolbar
        from matplotlib.backends.backend_tkagg import NavigationToolbar2Tk
        self.toolbar = NavigationToolbar2Tk(self.canvas, self.main_frame)
        self.toolbar.update()

        # Initialize variables
        self.current_data = None
        self.data_folder = None
        self.metadata = {}

    def load_data_folder(self):
        """Open a folder dialog and load all CSV files from the selected directory and its subdirectories."""
        self.data_folder = filedialog.askdirectory(
            title="Select Root Data Folder",
            initialdir=self.script_dir
        )
        if self.data_folder:
            self.refresh_files()
    
    def refresh_files(self):
        """Refresh the file tree with all CSV files in the data folder."""
        if not self.data_folder:
            return
            
        # Clear existing items
        for item in self.file_tree.get_children():
            self.file_tree.delete(item)
            
        # Cache for parent nodes
        parent_nodes = {"": ""}
        
        # Walk through directory and add files to tree
        for root, dirs, files in os.walk(self.data_folder):
            # Sort directories and files for consistent display
            dirs.sort()
            files.sort()
            
            # Get relative path from data folder
            rel_path = os.path.relpath(root, self.data_folder)
            if rel_path == ".":
                parent = ""
            else:
                # Create parent folders in tree
                parts = rel_path.split(os.sep)
                current_path = ""
                for part in parts:
                    next_path = os.path.join(current_path, part) if current_path else part
                    if next_path not in parent_nodes:
                        parent_nodes[next_path] = self.file_tree.insert(
                            parent_nodes[current_path], 
                            'end',
                            text=part,
                            values=(next_path,),
                            open=True
                        )
                    current_path = next_path
                parent = parent_nodes[rel_path]
            
            # Add CSV files to tree
            for file in files:
                if file.upper().endswith('.CSV'):
                    file_rel_path = os.path.join(rel_path, file) if rel_path != "." else file
                    self.file_tree.insert(
                        parent, 
                        'end',
                        text=file,
                        values=(file_rel_path,),
                        tags=('csv_file',)
                    )

    def on_file_select(self, event):
        selection = self.file_tree.selection()
        if selection:
            item = selection[0]
            if 'csv_file' in self.file_tree.item(item)['tags']:
                file_path = self.file_tree.item(item)['values'][0]
                full_path = os.path.join(self.data_folder, file_path)
                self.load_data(full_path)

    def load_data(self, filepath):
        try:
            # First read metadata with optimized reading
            metadata = {}
            header_lines = []
            data_start = 0
            
            with open(filepath, 'r') as f:
                for i, line in enumerate(f):
                    if i < 13:  # Metadata section
                        if ',' in line:
                            key, value = line.strip().split(',', 1)
                            metadata[key] = value
                        header_lines.append(line)
                    else:
                        if 'TIME' in line:
                            data_start = i
                            break
            
            # Now read just the data portion efficiently
            self.current_data = pd.read_csv(filepath, skiprows=data_start)
            self.metadata = metadata
            
            # Update window title with metadata
            self.title(f"Oscilloscope Data - {os.path.basename(filepath)} - {metadata.get('Model', 'Unknown')}")
            
            self.update_plot()
            
        except Exception as e:
            tk.messagebox.showerror("Error", f"Failed to load file: {str(e)}")

    def update_plot(self):
        if self.current_data is None:
            return

        self.ax.clear()
        
        # Plot visible channels
        if self.ch1_var.get():
            self.ax.plot(self.current_data['TIME'], self.current_data['CH1'], 
                        label=f'CH1 ({self.metadata.get("Vertical Scale", "?")}V/div)', 
                        color='yellow', linewidth=1)
        if self.ch2_var.get():
            self.ax.plot(self.current_data['TIME'], self.current_data['CH2'], 
                        label=f'CH2 ({self.metadata.get("Vertical Scale", "?")}V/div)', 
                        color='cyan', linewidth=1)

        # Set dark theme for better visibility
        self.fig.set_facecolor('#2b2b2b')
        self.ax.set_facecolor('#2b2b2b')
        self.ax.grid(True, color='#404040', linestyle='--', alpha=0.5)
        self.ax.tick_params(colors='white')
        
        for spine in self.ax.spines.values():
            spine.set_color('white')

        # Add labels with units from metadata
        self.ax.set_xlabel(f'Time ({self.metadata.get("Horizontal Units", "s")})', color='white')
        self.ax.set_ylabel(f'Voltage ({self.metadata.get("Vertical Units", "V")})', color='white')
        
        # Add legend with metadata info
        self.ax.legend(facecolor='#2b2b2b', labelcolor='white')
        
        # Show time scale from metadata
        if self.metadata:
            title = f"Time Scale: {self.metadata.get('Horizontal Scale', 'Unknown')}s/div"
            self.ax.set_title(title, color='white', pad=10)
            
        self.canvas.draw()

    def reset_zoom(self):
        if self.current_data is not None:
            self.ax.autoscale(True)
            self.canvas.draw()

if __name__ == "__main__":
    app = OscilloscopeViewer()
    app.configure(bg='#2b2b2b')  # Set dark theme for main window
    app.mainloop()
