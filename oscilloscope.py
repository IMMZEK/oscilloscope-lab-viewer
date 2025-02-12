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

        # Control panel
        self.control_frame = ttk.LabelFrame(self.main_frame, text="Controls")
        self.control_frame.pack(fill=tk.X, padx=5, pady=5)

        # File selection
        ttk.Button(self.control_frame, text="Open Data Folder", command=self.load_data_folder).pack(side=tk.LEFT, padx=5)
        
        # Channel toggles
        self.ch1_var = tk.BooleanVar(value=True)
        self.ch2_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(self.control_frame, text="CH1", variable=self.ch1_var, command=self.update_plot).pack(side=tk.LEFT, padx=5)
        ttk.Checkbutton(self.control_frame, text="CH2", variable=self.ch2_var, command=self.update_plot).pack(side=tk.LEFT, padx=5)

        # Plot controls
        self.zoom_frame = ttk.Frame(self.control_frame)
        self.zoom_frame.pack(side=tk.LEFT, padx=20)
        ttk.Label(self.zoom_frame, text="Zoom:").pack(side=tk.LEFT)
        ttk.Button(self.zoom_frame, text="Reset", command=self.reset_zoom).pack(side=tk.LEFT, padx=5)

        # File list
        self.files_frame = ttk.LabelFrame(self.main_frame, text="CSV Files")
        self.files_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Add a scrollbar to the listbox
        self.list_frame = ttk.Frame(self.files_frame)
        self.list_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.scrollbar = ttk.Scrollbar(self.list_frame)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.file_listbox = tk.Listbox(self.list_frame, height=3, yscrollcommand=self.scrollbar.set)
        self.file_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.scrollbar.config(command=self.file_listbox.yview)
        
        self.file_listbox.bind('<<ListboxSelect>>', self.on_file_select)

        # Plot
        self.fig = Figure(figsize=(10, 6))
        self.ax = self.fig.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.main_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Add toolbar
        from matplotlib.backends.backend_tkagg import NavigationToolbar2Tk
        self.toolbar = NavigationToolbar2Tk(self.canvas, self.main_frame)
        self.toolbar.update()

        # Initialize variables
        self.current_data = None
        self.data_folder = None
        self.metadata = {}

    def load_data_folder(self):
        # Start in the script's directory
        self.data_folder = filedialog.askdirectory(
            title="Select Data Folder",
            initialdir=self.script_dir
        )
        if self.data_folder:
            self.file_listbox.delete(0, tk.END)
            for root, _, files in os.walk(self.data_folder):
                for file in files:
                    if file.endswith('.CSV'):
                        rel_path = os.path.relpath(os.path.join(root, file), self.data_folder)
                        self.file_listbox.insert(tk.END, rel_path)

    def on_file_select(self, event):
        selection = self.file_listbox.curselection()
        if selection:
            filename = self.file_listbox.get(selection[0])
            self.load_data(os.path.join(self.data_folder, filename))

    def load_data(self, filepath):
        try:
            # First read metadata
            metadata = {}
            data_lines = []
            
            with open(filepath, 'r') as f:
                lines = f.readlines()
                
            # Process metadata (first 13 lines)
            for line in lines[:13]:
                if ',' in line:
                    key, value = line.strip().split(',', 1)
                    metadata[key] = value

            # Find the header line (TIME,CH1,CH2)
            header_index = next(i for i, line in enumerate(lines) if 'TIME' in line)
            
            # Convert remaining lines to DataFrame
            data = pd.read_csv(filepath, skiprows=header_index)
            
            self.current_data = data
            self.metadata = metadata
            self.update_plot()
            
            # Update window title with metadata
            self.title(f"Oscilloscope Data Viewer - {os.path.basename(filepath)} - {metadata.get('Model', 'Unknown')}")
            
        except Exception as e:
            tk.messagebox.showerror("Error", f"Failed to load file: {str(e)}")

    def update_plot(self):
        if self.current_data is None:
            return

        self.ax.clear()
        
        if self.ch1_var.get():
            self.ax.plot(self.current_data['TIME'], self.current_data['CH1'], 
                        label='CH1', color='yellow', linewidth=1)
        if self.ch2_var.get():
            self.ax.plot(self.current_data['TIME'], self.current_data['CH2'], 
                        label='CH2', color='cyan', linewidth=1)

        # Set dark theme for better visibility
        self.fig.set_facecolor('#2b2b2b')
        self.ax.set_facecolor('#2b2b2b')
        self.ax.grid(True, color='#404040')
        self.ax.tick_params(colors='white')
        for spine in self.ax.spines.values():
            spine.set_color('white')

        self.ax.set_xlabel('Time (s)', color='white')
        self.ax.set_ylabel('Voltage (V)', color='white')
        self.ax.legend(facecolor='#2b2b2b', labelcolor='white')
        
        # Show scale information from metadata
        if self.metadata:
            title = f"Time Scale: {self.metadata.get('Horizontal Scale', 'Unknown')}s/div"
            self.ax.set_title(title, color='white')
            
        self.canvas.draw()

    def reset_zoom(self):
        if self.current_data is not None:
            self.ax.autoscale(True)
            self.canvas.draw()

if __name__ == "__main__":
    app = OscilloscopeViewer()
    app.configure(bg='#2b2b2b')  # Set dark theme for main window
    app.mainloop()
