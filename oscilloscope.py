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
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure
from matplotlib.widgets import Cursor
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
        
        # Initialize path variables
        self.script_dir = os.path.dirname(os.path.abspath(__file__))
        self.data_folder = None
        self.title("Oscilloscope Data Viewer")
        self.geometry("1400x900")
        
        # Configure the window
        self.configure(bg='#2b2b2b')
        
        # Set theme and style for better visibility
        style = ttk.Style()
        style.configure('Treeview', 
                       background='#2b2b2b',
                       foreground='white',
                       fieldbackground='#2b2b2b',
                       selectbackground='#404040',
                       selectforeground='white')
        style.configure('Treeview.Heading', 
                       background='#3b3b3b',
                       foreground='white')
        style.configure('TLabelframe', 
                       background='#2b2b2b',
                       foreground='white')
        style.configure('TLabelframe.Label', 
                       background='#2b2b2b',
                       foreground='white')
        
        # Create main layout
        self.create_layout()
        
        # Initialize variables
        self.initialize_variables()
        
        # Auto-load the Lab3/Data directory if it exists
        default_data_path = os.path.join(self.script_dir, "Lab3", "Data")
        if os.path.exists(default_data_path):
            self.data_folder = default_data_path
            self.after(100, self.refresh_files)  # Schedule refresh after GUI is ready
            self.set_status(f"Loading default folder: {default_data_path}")

    def create_layout(self):
        """Create the main application layout"""
        # Create main container
        self.main_frame = ttk.Frame(self)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Create central layout
        self.content_frame = ttk.Frame(self.main_frame)
        self.content_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create status bar
        self.status_bar = ttk.Label(
            self.main_frame,
            text="Ready",
            relief=tk.SUNKEN,
            anchor=tk.W,
            background='#2b2b2b',
            foreground='white'
        )
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Setup panels
        self.create_left_panel()
        self.create_right_panel()

    def initialize_variables(self):
        """Initialize all class variables"""
        self.current_data = None
        self.metadata = {}
        self.cursors = {
            'time1': {'line': None, 'value': None, 'active': False, 'label': None},
            'time2': {'line': None, 'value': None, 'active': False, 'label': None},
            'volt1': {'line': None, 'value': None, 'active': False, 'label': None},
            'volt2': {'line': None, 'value': None, 'active': False, 'label': None}
        }
        
        # Initialize icons for file tree
        self.folder_icon = tk.PhotoImage(data='''
            R0lGODlhEAAQAIABAEBNYP///yH5BAEKAAEALAAAAAAQABAAAAIijI+py+0PowwKhgC
            mXgr7bHUf42VhKJpYaqLnqq5uSmMFADs=
        ''')
        self.file_icon = tk.PhotoImage(data='''
            R0lGODlhEAAQAIABAEBNYP///yH5BAEKAAEALAAAAAAQABAAAAIdjI+py+0Po5y02ouz
            3rz7D4biSJbmiabqyrbuC4cFADs=
        ''')
        
        # Initialize cursor state variables
        self.cursor_placement_mode = None
        self.last_cursor_click = None
        
    def create_left_panel(self):
        """Create the left panel with all its components"""
        self.left_panel = ttk.Frame(self.content_frame, width=300)
        self.left_panel.pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=5)
        
        # Setup all left panel components
        self.setup_controls()
        self.setup_measurements_panel()
        self.setup_cursor_controls()
        self.setup_file_tree()
        
    def create_right_panel(self):
        """Create the right panel with plot area"""
        self.right_panel = ttk.Frame(self.content_frame)
        self.right_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Setup plot
        self.setup_plot()
        
        # Add cursor instructions overlay
        self.cursor_overlay = ttk.Label(
            self.right_panel,
            text="Double-click to place cursors\nDrag cursors to move them",
            background='#2b2b2b',
            foreground='#888888',
            justify=tk.CENTER
        )
        self.cursor_overlay.place(relx=0.98, rely=0.02, anchor='ne')

    def setup_file_tree(self):
        """Setup the file browser tree view"""
        self.files_frame = ttk.LabelFrame(self.left_panel, text="Data Files")
        self.files_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Create tree frame with scrollbars
        tree_frame = ttk.Frame(self.files_frame)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Create scrollbars
        vsb = ttk.Scrollbar(tree_frame, orient="vertical")
        vsb.pack(side=tk.RIGHT, fill=tk.Y)
        
        hsb = ttk.Scrollbar(tree_frame, orient="horizontal")
        hsb.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Create and configure the Treeview
        self.file_tree = ttk.Treeview(
            tree_frame,
            selectmode='browse',
            yscrollcommand=vsb.set,
            xscrollcommand=hsb.set,
            height=15
        )
        self.file_tree.pack(fill=tk.BOTH, expand=True)
        
        # Configure scrollbars
        vsb.config(command=self.file_tree.yview)
        hsb.config(command=self.file_tree.xview)
        
        # Configure tree columns and heading
        self.file_tree.heading('#0', text='Name', anchor=tk.W)
        
        # Configure tags for icons
        self.file_tree.tag_configure('folder', foreground='lightblue')
        self.file_tree.tag_configure('file', foreground='white')
        
        # Bind events
        self.file_tree.bind('<<TreeviewSelect>>', self.on_file_select)

    def setup_controls(self):
        """Setup control panel with file and visualization controls"""
        control_frame = ttk.LabelFrame(self.left_panel, text="Controls")
        control_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # File controls
        ttk.Button(control_frame, text="Open Data Folder", 
                  command=self.load_data_folder).pack(fill=tk.X, padx=5, pady=2)
        
        ttk.Button(control_frame, text="Refresh Files",
                  command=self.refresh_files).pack(fill=tk.X, padx=5, pady=2)
        
        # Visualization options
        viz_frame = ttk.LabelFrame(control_frame, text="Display Options")
        viz_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Channel selection
        self.ch1_var = tk.BooleanVar(value=True)
        self.ch2_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(viz_frame, text="CH1", variable=self.ch1_var,
                       command=self.update_plot).pack(fill=tk.X, padx=5, pady=2)
        ttk.Checkbutton(viz_frame, text="CH2", variable=self.ch2_var,
                       command=self.update_plot).pack(fill=tk.X, padx=5, pady=2)
                       
        # Dark mode always on for better visibility
        self.dark_mode = True

    def setup_measurements_panel(self):
        """Setup the measurements panel"""
        measurements_frame = ttk.LabelFrame(self.left_panel, text="Measurements")
        measurements_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Cursor measurements
        cursor_frame = ttk.LabelFrame(measurements_frame, text="Cursor Measurements")
        cursor_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Add cursor position readouts
        self.cursor_pos = {
            'time1': tk.StringVar(value="T1: --"),
            'time2': tk.StringVar(value="T2: --"),
            'volt1': tk.StringVar(value="V1: --"),
            'volt2': tk.StringVar(value="V2: --")
        }
        
        for var in self.cursor_pos.values():
            ttk.Label(cursor_frame, textvariable=var).pack(fill=tk.X, padx=5, pady=2)
        
        self.delta_t_var = tk.StringVar(value="ΔT: --")
        self.delta_v_var = tk.StringVar(value="ΔV: --")
        ttk.Label(cursor_frame, textvariable=self.delta_t_var).pack(fill=tk.X, padx=5, pady=2)
        ttk.Label(cursor_frame, textvariable=self.delta_v_var).pack(fill=tk.X, padx=5, pady=2)
        
        # Add frequency from cursor measurements
        self.cursor_freq_var = tk.StringVar(value="1/ΔT: --")
        ttk.Label(cursor_frame, textvariable=self.cursor_freq_var).pack(fill=tk.X, padx=5, pady=2)
        
        # Automatic measurements
        auto_frame = ttk.LabelFrame(measurements_frame, text="Automatic Measurements")
        auto_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.measurements = {
            'Vpp': tk.StringVar(value="Vpp: --"),
            'Vmax': tk.StringVar(value="Vmax: --"),
            'Vmin': tk.StringVar(value="Vmin: --"),
            'Freq': tk.StringVar(value="Freq: --"),
            'Period': tk.StringVar(value="Period: --"),
            'Rise': tk.StringVar(value="Rise: --"),
            'Fall': tk.StringVar(value="Fall: --"),
            'Duty': tk.StringVar(value="Duty: --")
        }
        
        for var in self.measurements.values():
            ttk.Label(auto_frame, textvariable=var).pack(fill=tk.X, padx=5, pady=2)

    def setup_cursor_controls(self):
        """Setup cursor control panel with enhanced visibility and interaction."""
        cursor_control_frame = ttk.LabelFrame(self.left_panel, text="Cursor Controls")
        cursor_control_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Instructions label
        ttk.Label(
            cursor_control_frame, 
            text="Double-click on plot to place cursors",
            wraplength=200
        ).pack(fill=tk.X, padx=5, pady=2)
        
        # Time cursors with better visibility options
        time_frame = ttk.Frame(cursor_control_frame)
        time_frame.pack(fill=tk.X, padx=5, pady=2)
        
        self.time_cursor_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(
            time_frame,
            text="Time Cursors",
            variable=self.time_cursor_var,
            command=self.toggle_time_cursors
        ).pack(side=tk.LEFT)
        
        # Time cursor color picker
        self.time_cursor_color = tk.StringVar(value='red')
        ttk.Combobox(
            time_frame,
            textvariable=self.time_cursor_color,
            values=['red', 'yellow', 'cyan', 'magenta'],
            width=8,
            state='readonly'
        ).pack(side=tk.LEFT, padx=5)
        
        # Voltage cursors with better visibility options
        volt_frame = ttk.Frame(cursor_control_frame)
        volt_frame.pack(fill=tk.X, padx=5, pady=2)
        
        self.volt_cursor_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(
            volt_frame,
            text="Voltage Cursors",
            variable=self.volt_cursor_var,
            command=self.toggle_voltage_cursors
        ).pack(side=tk.LEFT)
        
        # Voltage cursor color picker
        self.volt_cursor_color = tk.StringVar(value='cyan')
        ttk.Combobox(
            volt_frame,
            textvariable=self.volt_cursor_color,
            values=['red', 'yellow', 'cyan', 'magenta'],
            width=8,
            state='readonly'
        ).pack(side=tk.LEFT, padx=5)
        
        # Active cursor indicators
        self.active_cursor_label = ttk.Label(cursor_control_frame, text="")
        self.active_cursor_label.pack(fill=tk.X, padx=5, pady=2)

    def setup_plot(self):
        """Setup the matplotlib plot with enhanced cursor interaction."""
        self.fig = Figure(figsize=(10, 6))
        self.ax = self.fig.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.right_panel)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # Add navigation toolbar
        self.toolbar = NavigationToolbar2Tk(self.canvas, self.right_panel)
        self.toolbar.update()
        
        # Bind double click for cursor placement
        self.canvas.mpl_connect('button_press_event', self.on_plot_click)
        
        # Initialize cursor placement state
        self.cursor_placement_mode = None
        self.last_cursor_click = None

    def toggle_time_cursors(self):
        """Toggle time cursors with improved visibility"""
        if not self.time_cursor_var.get():
            self.remove_cursor('time1')
            self.remove_cursor('time2')
            self.cursor_placement_mode = None
            self.last_cursor_click = None
            self.active_cursor_label.config(text="")
        else:
            self.active_cursor_label.config(text="Double-click to place Time Cursor 1")
        self.canvas.draw()

    def toggle_voltage_cursors(self):
        """Toggle voltage cursors with improved visibility"""
        if not self.volt_cursor_var.get():
            self.remove_cursor('volt1')
            self.remove_cursor('volt2')
            self.cursor_placement_mode = None
            self.last_cursor_click = None
            self.active_cursor_label.config(text="")
        else:
            self.active_cursor_label.config(text="Double-click to place Voltage Cursor 1")
        self.canvas.draw()

    def add_cursor(self, name, position=0, vertical=True, color=None):
        """Add a cursor line to the plot with enhanced visibility."""
        if self.current_data is None:
            return
            
        # Remove existing cursor if any
        self.remove_cursor(name)
        
        if vertical:
            line = self.ax.axvline(
                x=position,
                color=color or self.time_cursor_color.get(),
                linestyle='--',
                alpha=0.8,
                linewidth=2,
                picker=5
            )
        else:
            line = self.ax.axhline(
                y=position,
                color=color or self.volt_cursor_color.get(),
                linestyle='--',
                alpha=0.8,
                linewidth=2,
                picker=5
            )
            
        self.cursors[name] = {
            'line': line,
            'value': position,
            'active': False
        }
        
        # Add cursor label
        if vertical:
            label = f'{name}: {position:.2e}s'
            self.ax.text(
                position,
                self.ax.get_ylim()[1],
                label,
                rotation=90,
                color=color or self.time_cursor_color.get(),
                va='top'
            )
        else:
            label = f'{name}: {position:.3f}V'
            self.ax.text(
                self.ax.get_xlim()[0],
                position,
                label,
                color=color or self.volt_cursor_color.get(),
                va='bottom',
                ha='left'
            )
        
    def remove_cursor(self, name):
        """Remove a cursor and its label from the plot"""
        cursor = self.cursors[name]
        if cursor['line'] is not None:
            cursor['line'].remove()
            if cursor.get('label'):
                cursor['label'].remove()
            cursor['line'] = None
            cursor['label'] = None
            cursor['value'] = None
            cursor['active'] = False

    def update_cursor_measurements(self):
        """Update cursor measurements with better formatting"""
        if self.current_data is None:
            return
            
        # Update cursor positions
        for name, cursor in self.cursors.items():
            if cursor['line'] is not None:
                if cursor['label'] is not None:
                    cursor['label'].remove()
                
                if 'time' in name:
                    cursor['label'] = self.ax.text(
                        cursor['value'],
                        self.ax.get_ylim()[1],
                        f'{name}: {cursor["value"]:.2e}s',
                        rotation=90,
                        color=cursor['line'].get_color(),
                        va='top',
                        ha='right',
                        backgroundcolor='#2b2b2b',
                        alpha=0.8
                    )
                else:
                    cursor['label'] = self.ax.text(
                        self.ax.get_xlim()[0],
                        cursor['value'],
                        f'{name}: {cursor["value"]:.3f}V',
                        color=cursor['line'].get_color(),
                        va='bottom',
                        ha='left',
                        backgroundcolor='#2b2b2b',
                        alpha=0.8
                    )
        
        # Update delta measurements
        if all(self.cursors[c]['value'] is not None for c in ['time1', 'time2']):
            delta_t = abs(self.cursors['time2']['value'] - self.cursors['time1']['value'])
            freq = 1/delta_t if delta_t != 0 else float('inf')
            self.delta_t_var.set(f"ΔT: {delta_t:.2e} s")
            self.cursor_freq_var.set(f"1/ΔT: {freq:.2e} Hz")
            
            # Add delta marker
            t1, t2 = sorted([self.cursors['time1']['value'], self.cursors['time2']['value']])
            y = self.ax.get_ylim()[1] * 0.9
            self.ax.annotate(
                f'ΔT: {delta_t:.2e}s',
                xy=(t1, y),
                xytext=(t2, y),
                arrowprops=dict(arrowstyle='<->'),
                color='white',
                backgroundcolor='#2b2b2b',
                alpha=0.8
            )
            
        if all(self.cursors[c]['value'] is not None for c in ['volt1', 'volt2']):
            delta_v = abs(self.cursors['volt2']['value'] - self.cursors['volt1']['value'])
            self.delta_v_var.set(f"ΔV: {delta_v:.3f} V")
            
            # Add delta marker
            v1, v2 = sorted([self.cursors['volt1']['value'], self.cursors['volt2']['value']])
            x = self.ax.get_xlim()[0] * 0.9
            self.ax.annotate(
                f'ΔV: {delta_v:.3f}V',
                xy=(x, v1),
                xytext=(x, v2),
                arrowprops=dict(arrowstyle='<->'),
                color='white',
                backgroundcolor='#2b2b2b',
                alpha=0.8
            )
        
        self.canvas.draw()

    def update_measurements(self):
        """Update automatic measurements"""
        if self.current_data is None:
            return
            
        # Update cursor measurements first
        self.update_cursor_measurements()
        
        # Update automatic measurements for the visible channels
        channels = []
        if self.ch1_var.get():
            channels.append('CH1')
        if self.ch2_var.get():
            channels.append('CH2')
            
        for ch in channels:
            data = self.current_data[ch]
            time = self.current_data['TIME']
            
            # Voltage measurements
            vmax = data.max()
            vmin = data.min()
            vpp = vmax - vmin
            
            # Timing measurements
            mean = data.mean()
            crossings = np.where(np.diff(np.signbit(data - mean)))[0]
            if len(crossings) > 1:
                periods = np.diff(time[crossings[::2]])  # Only rising or falling edges
                period = np.mean(periods) if len(periods) > 0 else 0
                freq = 1 / period if period > 0 else 0
            else:
                period = 0
                freq = 0
                
            # Rise/Fall time (10% to 90%)
            v10 = vmin + 0.1 * vpp
            v90 = vmin + 0.9 * vpp
            
            # Find all rising and falling edges
            rising_edges = []
            falling_edges = []
            
            for i in range(len(data)-1):
                if data[i] <= v10 and data[i+1] >= v90:
                    rising_edges.append((i, time[i+1] - time[i]))
                elif data[i] >= v90 and data[i+1] <= v10:
                    falling_edges.append((i, time[i+1] - time[i]))
            
            rise_time = np.mean([t for _, t in rising_edges]) if rising_edges else 0
            fall_time = np.mean([t for _, t in falling_edges]) if falling_edges else 0
            
            # Duty cycle using zero crossings
            if len(crossings) > 1:
                high_time = np.sum(np.diff(time[crossings])[::2])
                total_time = np.sum(np.diff(time[crossings]))
                duty = (high_time / total_time) * 100 if total_time > 0 else 0
            else:
                duty = 0
            
            # Update measurement display
            self.measurements['Vpp'].set(f"Vpp ({ch}): {vpp:.3f} V")
            self.measurements['Vmax'].set(f"Vmax ({ch}): {vmax:.3f} V")
            self.measurements['Vmin'].set(f"Vmin ({ch}): {vmin:.3f} V")
            self.measurements['Freq'].set(f"Freq ({ch}): {freq:.2e} Hz")
            self.measurements['Period'].set(f"Period ({ch}): {period:.2e} s")
            self.measurements['Rise'].set(f"Rise ({ch}): {rise_time:.2e} s")
            self.measurements['Fall'].set(f"Fall ({ch}): {fall_time:.2e} s")
            self.measurements['Duty'].set(f"Duty ({ch}): {duty:.1f} %")

    def on_click(self, event):
        """Handle mouse click events"""
        if event.inaxes != self.ax or self.toolbar.mode != "":
            return
            
        # Check if click is near any cursor
        for name, cursor in self.cursors.items():
            if cursor['line'] is not None:
                if isinstance(cursor['line'], plt.Line2D):  # Vertical cursor
                    if abs(event.xdata - cursor['value']) < (self.ax.get_xlim()[1] - self.ax.get_xlim()[0]) * 0.02:
                        cursor['active'] = True
                else:  # Horizontal cursor
                    if abs(event.ydata - cursor['value']) < (self.ax.get_ylim()[1] - self.ax.get_ylim()[0]) * 0.02:
                        cursor['active'] = True

    def on_motion(self, event):
        """Handle mouse motion for cursor dragging with improved feedback"""
        if event.inaxes != self.ax:
            return
            
        # Move active cursors and update their labels
        for name, cursor in self.cursors.items():
            if cursor['active'] and cursor['line'] is not None:
                if isinstance(cursor['line'], plt.Line2D):  # Vertical cursor
                    cursor['line'].set_xdata([event.xdata, event.xdata])
                    cursor['value'] = event.xdata
                else:  # Horizontal cursor
                    cursor['line'].set_ydata([event.ydata, event.ydata])
                    cursor['value'] = event.ydata
                
                # Update cursor position and measurements
                self.update_cursor_measurements()
                self.canvas.draw()

    def on_release(self, event):
        """Handle mouse release and cleanup"""
        any_active = False
        for cursor in self.cursors.values():
            if cursor['active']:
                any_active = True
            cursor['active'] = False
            
        if any_active:
            self.active_cursor_label.config(text="")
            self.update_cursor_measurements()

    def load_data_folder(self):
        """Open a folder dialog and load all CSV files from the selected directory"""
        folder = filedialog.askdirectory(
            title="Select Data Folder",
            initialdir=os.path.join(self.script_dir, "Lab3", "Data"),
            mustexist=True
        )
        if folder:
            self.data_folder = folder
            self.refresh_files()
            self.set_status(f"Loaded folder: {folder}")
            
            # Automatically expand all folders
            def expand_all(tree, item=""):
                children = tree.get_children(item)
                for child in children:
                    tree.item(child, open=True)
                    expand_all(tree, child)
            
            expand_all(self.file_tree)

    def refresh_files(self):
        """Refresh the file tree with all CSV files in the data folder."""
        if not self.data_folder:
            return
            
        def insert_path(parent, path):
            """Recursively insert a path into the tree"""
            parts = os.path.relpath(path, self.data_folder).split(os.sep)
            current_parent = parent
            current_path = self.data_folder
            
            for part in parts[:-1]:  # Process all but the last part (file)
                current_path = os.path.join(current_path, part)
                # Check if this node already exists
                found = False
                for child in self.file_tree.get_children(current_parent):
                    if self.file_tree.item(child)['text'] == part:
                        current_parent = child
                        found = True
                        break
                
                if not found:
                    current_parent = self.file_tree.insert(
                        current_parent, 'end',
                        text=part,
                        values=(current_path,),
                        tags=('folder',),
                        open=True
                    )
            
            # Insert the file
            return current_parent
            
        # Clear existing items
        for item in self.file_tree.get_children():
            self.file_tree.delete(item)
        
        # Walk through directory structure
        for root, dirs, files in os.walk(self.data_folder):
            # Sort directories and files
            dirs.sort()
            files.sort()
            
            # Get the parent node for this directory
            parent = insert_path("", root)
            
            # Add CSV files
            for file in files:
                if file.upper().endswith('.CSV'):
                    full_path = os.path.join(root, file)
                    self.file_tree.insert(
                        parent,
                        'end',
                        text=file,
                        values=(full_path,),
                        tags=('file',)
                    )
        
        # Configure tags
        self.file_tree.tag_configure('folder', foreground='lightblue')
        self.file_tree.tag_configure('file', foreground='white')
        
    def on_file_select(self, event):
        """Handle file selection from tree"""
        selection = self.file_tree.selection()
        if not selection:
            return
            
        item = selection[0]
        item_tags = self.file_tree.item(item)['tags']
        
        # Skip if a folder is selected
        if 'folder' in item_tags:
            return
            
        # Get the full file path from the tree item values
        file_path = self.file_tree.item(item)['values'][0]
        if not os.path.isfile(file_path):
            self.set_status(f"Error: File not found - {file_path}")
            return
            
        try:
            self.load_data(file_path)
            self.set_status(f"Loaded: {os.path.basename(file_path)}")
        except Exception as e:
            self.set_status(f"Error loading file: {str(e)}")
            messagebox.showerror("Error", f"Failed to load file: {str(e)}")

    def load_data(self, filepath):
        """Load data from a CSV file."""
        try:
            self.set_status(f"Loading {os.path.basename(filepath)}...")
            
            # First read metadata with optimized reading
            metadata = {}
            data_start = 0
            
            with open(filepath, 'r') as f:
                for i, line in enumerate(f):
                    if i < 13:  # Metadata section
                        if ',' in line:
                            key, value = line.strip().split(',', 1)
                            metadata[key] = value
                    else:
                        if 'TIME' in line:
                            data_start = i
                            break
            
            # Now read just the data portion efficiently
            self.current_data = pd.read_csv(filepath, skiprows=data_start)
            
            # Verify required columns exist
            required_columns = ['TIME', 'CH1', 'CH2']
            missing_columns = [col for col in required_columns if col not in self.current_data.columns]
            if missing_columns:
                raise ValueError(f"Missing required columns: {', '.join(missing_columns)}")
                
            self.metadata = metadata
            
            # Update window title with metadata
            self.title(f"Oscilloscope Data - {os.path.basename(filepath)} - {metadata.get('Model', 'Unknown')}")
            
            self.update_plot()
            self.set_status(f"Successfully loaded {os.path.basename(filepath)}")
            
        except Exception as e:
            self.set_status(f"Error: {str(e)}")
            raise
            
    def set_status(self, message):
        """Update status bar message"""
        self.status_bar.config(text=message)
        self.update_idletasks()

    def update_plot(self):
        """Update the plot with current data"""
        if self.current_data is None:
            return

        self.ax.clear()
        
        if self.ch1_var.get():
            self.ax.plot(self.current_data['TIME'], self.current_data['CH1'], 
                        label='CH1', color='yellow', linewidth=1)
        if self.ch2_var.get():
            self.ax.plot(self.current_data['TIME'], self.current_data['CH2'], 
                        label='CH2', color='cyan', linewidth=1)

        # Restore cursors
        for name, cursor in self.cursors.items():
            if cursor['value'] is not None:
                if 'time' in name:
                    cursor['line'] = self.ax.axvline(x=cursor['value'], color='r', linestyle='--', alpha=0.5)
                else:
                    cursor['line'] = self.ax.axhline(y=cursor['value'], color='g', linestyle='--', alpha=0.5)

        # Set dark theme and labels
        self.fig.set_facecolor('#2b2b2b')
        self.ax.set_facecolor('#2b2b2b')
        self.ax.grid(True, color='#404040', linestyle='--', alpha=0.5)
        self.ax.tick_params(colors='white')
        
        for spine in self.ax.spines.values():
            spine.set_color('white')

        self.ax.set_xlabel(f'Time ({self.metadata.get("Horizontal Units", "s")})', color='white')
        self.ax.set_ylabel(f'Voltage ({self.metadata.get("Vertical Units", "V")})', color='white')
        self.ax.legend(facecolor='#2b2b2b', labelcolor='white')
        
        if self.metadata:
            title = f"Time Scale: {self.metadata.get('Horizontal Scale', 'Unknown')}s/div"
            self.ax.set_title(title, color='white', pad=10)
            
        self.canvas.draw()
        self.update_measurements()

    def on_plot_click(self, event):
        """Handle mouse clicks on the plot for cursor placement."""
        if event.inaxes != self.ax or self.toolbar.mode != "":
            return
            
        if event.dblclick:  # Handle double click
            if self.time_cursor_var.get():
                # Place time cursor
                if self.cursor_placement_mode != 'time':
                    self.cursor_placement_mode = 'time'
                    self.last_cursor_click = None
                    self.active_cursor_label.config(text="Click to place Time Cursor 1")
                
                if self.last_cursor_click is None:
                    # Place first cursor
                    self.add_cursor('time1', event.xdata, color=self.time_cursor_color.get())
                    self.last_cursor_click = 'time1'
                    self.active_cursor_label.config(text="Click to place Time Cursor 2")
                else:
                    # Place second cursor
                    self.add_cursor('time2', event.xdata, color=self.time_cursor_color.get())
                    self.cursor_placement_mode = None
                    self.last_cursor_click = None
                    self.active_cursor_label.config(text="")
                    
            elif self.volt_cursor_var.get():
                # Place voltage cursor
                if self.cursor_placement_mode != 'voltage':
                    self.cursor_placement_mode = 'voltage'
                    self.last_cursor_click = None
                    self.active_cursor_label.config(text="Click to place Voltage Cursor 1")
                
                if self.last_cursor_click is None:
                    # Place first cursor
                    self.add_cursor('volt1', event.ydata, vertical=False, color=self.volt_cursor_color.get())
                    self.last_cursor_click = 'volt1'
                    self.active_cursor_label.config(text="Click to place Voltage Cursor 2")
                else:
                    # Place second cursor
                    self.add_cursor('volt2', event.ydata, vertical=False, color=self.volt_cursor_color.get())
                    self.cursor_placement_mode = None
                    self.last_cursor_click = None
                    self.active_cursor_label.config(text="")
            
            self.canvas.draw()
            self.update_cursor_measurements()
        
        elif event.button == 1:  # Left click for dragging existing cursors
            # Check if click is near any cursor
            for name, cursor in self.cursors.items():
                if cursor['line'] is not None:
                    if isinstance(cursor['line'], plt.Line2D):  # Vertical cursor
                        if abs(event.xdata - cursor['value']) < (self.ax.get_xlim()[1] - self.ax.get_xlim()[0]) * 0.02:
                            cursor['active'] = True
                            self.active_cursor_label.config(text=f"Dragging {name}")
                    else:  # Horizontal cursor
                        if abs(event.ydata - cursor['value']) < (self.ax.get_ylim()[1] - self.ax.get_ylim()[0]) * 0.02:
                            cursor['active'] = True
                            self.active_cursor_label.config(text=f"Dragging {name}")

    def on_tree_double_click(self, event):
        """Handle double click on tree items"""
        item = self.file_tree.selection()
        if not item:
            return
            
        item = item[0]
        if 'folder' in self.file_tree.item(item, 'tags'):
            # Toggle folder expansion
            if self.file_tree.item(item, 'open'):
                self.file_tree.item(item, open=False)
            else:
                self.file_tree.item(item, open=True)

if __name__ == "__main__":
    app = OscilloscopeViewer()
    app.configure(bg='#2b2b2b')
    app.mainloop()
