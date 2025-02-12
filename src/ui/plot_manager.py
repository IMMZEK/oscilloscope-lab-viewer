import tkinter as tk
from tkinter import ttk
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from src.ui.cursor_manager import CursorManager

class PlotManager(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        # Store cursor positions per file
        self.file_cursor_positions = {}
        self.current_file = None
        self.cursor_positions = {
            'time1': None,
            'time2': None,
            'volt1': None,
            'volt2': None
        }
        self.channel_vars = {}  # Dictionary to store channel variables
        self.current_data = None  # Store current data
        self.current_metadata = None  # Store current metadata
        self.setup_plot()
        self.setup_controls()

    def setup_plot(self):
        """Setup the matplotlib plot with enhanced cursor interaction."""
        self.fig = Figure(figsize=(10, 6))
        self.ax = self.fig.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.fig, master=self)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # Add navigation toolbar
        self.toolbar = NavigationToolbar2Tk(self.canvas, self)
        self.toolbar.update()
        
        # Initialize cursor manager
        self.cursor_manager = CursorManager(self.ax)
        
        # Set dark theme
        self.fig.set_facecolor('#2b2b2b')
        self.ax.set_facecolor('#2b2b2b')
        self.ax.grid(True, color='#404040', linestyle='--', alpha=0.5)
        self.ax.tick_params(colors='white')
        
        for spine in self.ax.spines.values():
            spine.set_color('white')
            
        # Add cursor instructions overlay
        self.cursor_overlay = ttk.Label(
            self,
            text="Double-click to place cursors\nDrag cursors to move them",
            background='#2b2b2b',
            foreground='#888888',
            justify=tk.CENTER
        )
        self.cursor_overlay.place(relx=0.98, rely=0.02, anchor='ne')
        
        # Bind events
        self.canvas.mpl_connect('button_press_event', self.on_plot_click)
        self.canvas.mpl_connect('motion_notify_event', self.on_motion)
        self.canvas.mpl_connect('button_release_event', self.on_release)

    def setup_controls(self):
        """Setup plot control panel."""
        control_frame = ttk.LabelFrame(self, text="Display Options")
        control_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Channel selection frame
        self.channel_frame = ttk.Frame(control_frame)
        self.channel_frame.pack(side=tk.LEFT, padx=5)
        
        # Cursor controls
        cursor_frame = ttk.LabelFrame(control_frame, text="Cursors")
        cursor_frame.pack(side=tk.LEFT, fill=tk.X, padx=5)
        
        # Time cursors
        time_frame = ttk.Frame(cursor_frame)
        time_frame.pack(side=tk.LEFT, padx=5)
        
        self.time_cursor_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(
            time_frame,
            text="Time",
            variable=self.time_cursor_var,
            command=self.toggle_time_cursors
        ).pack(side=tk.LEFT)
        
        self.time_cursor_color = tk.StringVar(value='red')
        ttk.Combobox(
            time_frame,
            textvariable=self.time_cursor_color,
            values=['red', 'yellow', 'cyan', 'magenta'],
            width=8,
            state='readonly'
        ).pack(side=tk.LEFT, padx=5)
        
        # Voltage cursors
        volt_frame = ttk.Frame(cursor_frame)
        volt_frame.pack(side=tk.LEFT, padx=5)
        
        self.volt_cursor_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(
            volt_frame,
            text="Voltage",
            variable=self.volt_cursor_var,
            command=self.toggle_voltage_cursors
        ).pack(side=tk.LEFT)
        
        self.volt_cursor_color = tk.StringVar(value='cyan')
        ttk.Combobox(
            volt_frame,
            textvariable=self.volt_cursor_color,
            values=['red', 'yellow', 'cyan', 'magenta'],
            width=8,
            state='readonly'
        ).pack(side=tk.LEFT, padx=5)

    def update_plot(self, data=None, metadata=None, filepath=None):
        """Update the plot with new data."""
        if data is not None:
            self.current_data = data
            self.current_metadata = metadata
        elif self.current_data is None:
            return

        # If loading a new file, store current cursor positions for the old file
        if self.current_file is not None and self.current_file != filepath:
            self.file_cursor_positions[self.current_file] = self.cursor_positions.copy()

        # Update current file and load its cursor positions if they exist
        if filepath is not None:
            self.current_file = filepath
            if filepath in self.file_cursor_positions:
                self.cursor_positions = self.file_cursor_positions[filepath].copy()
            else:
                self.cursor_positions = {
                    'time1': None,
                    'time2': None,
                    'volt1': None,
                    'volt2': None
                }

            # Update channel controls based on available channels in the data
            self.update_channel_controls(self.current_data)

        # Clear all cursors before clearing the plot
        for name in ['time1', 'time2', 'volt1', 'volt2']:
            cursor = self.cursor_manager.cursors[name]
            cursor.update({
                'line': None,
                'label': None,
                'value': None,
                'active': False
            })

        self.ax.clear()
        
        # Plot each available channel if enabled
        colors = ['yellow', 'cyan', 'magenta', 'lime', 'red', 'orange', 'white', 'purple']
        for i, channel in enumerate([col for col in self.current_data.columns if col.startswith('CH')]):
            if channel in self.channel_vars and self.channel_vars[channel].get():
                color = colors[i % len(colors)]  # Cycle through colors if more than 8 channels
                self.ax.plot(self.current_data['TIME'], self.current_data[channel], 
                           label=channel, color=color, linewidth=1)

        # Restore dark theme
        self.ax.set_facecolor('#2b2b2b')
        self.ax.grid(True, color='#404040', linestyle='--', alpha=0.5)
        self.ax.tick_params(colors='white')
        
        for spine in self.ax.spines.values():
            spine.set_color('white')

        self.ax.set_xlabel(f'Time ({self.current_metadata.get("Horizontal Units", "s")})', color='white')
        self.ax.set_ylabel(f'Voltage ({self.current_metadata.get("Vertical Units", "V")})', color='white')
        self.ax.legend(facecolor='#2b2b2b', labelcolor='white')
        
        if self.current_metadata:
            title = f"Time Scale: {self.current_metadata.get('Horizontal Scale', 'Unknown')}s/div"
            self.ax.set_title(title, color='white', pad=10)

        # Restore cursors if they were enabled
        if self.time_cursor_var.get():
            if self.cursor_positions['time1'] is not None:
                self.cursor_manager.add_cursor('time1', self.cursor_positions['time1'], color=self.time_cursor_color.get())
                if self.cursor_positions['time2'] is not None:
                    self.cursor_manager.add_cursor('time2', self.cursor_positions['time2'], color=self.time_cursor_color.get())

        if self.volt_cursor_var.get():
            if self.cursor_positions['volt1'] is not None:
                self.cursor_manager.add_cursor('volt1', self.cursor_positions['volt1'], vertical=False, color=self.volt_cursor_color.get())
                if self.cursor_positions['volt2'] is not None:
                    self.cursor_manager.add_cursor('volt2', self.cursor_positions['volt2'], vertical=False, color=self.volt_cursor_color.get())
            
        # After restoring cursors, update measurements
        if hasattr(self.parent.master, 'update_measurements'):
            self.parent.master.update_measurements()
        self.canvas.draw()

    def toggle_time_cursors(self):
        """Toggle time cursors."""
        if not self.time_cursor_var.get():
            # Store cursor positions before removing
            for name in ['time1', 'time2']:
                cursor = self.cursor_manager.cursors[name]
                if cursor['line'] is not None:
                    self.cursor_positions[name] = cursor['value']
            # Disable time cursors
            self.cursor_manager.remove_cursor('time1')
            self.cursor_manager.remove_cursor('time2')
            if self.cursor_manager.cursor_placement_mode == 'time':
                # Switch to voltage mode if voltage cursors are enabled
                if self.volt_cursor_var.get():
                    self.cursor_manager.cursor_placement_mode = 'voltage'
                    self.cursor_overlay.config(text="Double-click to place Voltage Cursor 1")
                else:
                    self.cursor_manager.cursor_placement_mode = None
                    self.cursor_manager.last_cursor_click = None
                    self.cursor_overlay.config(text="Double-click to place cursors")
        else:
            # Enable time cursors and restore positions if they exist
            if self.cursor_positions['time1'] is not None:
                self.cursor_manager.add_cursor('time1', self.cursor_positions['time1'], color=self.time_cursor_color.get())
                if self.cursor_positions['time2'] is not None:
                    self.cursor_manager.add_cursor('time2', self.cursor_positions['time2'], color=self.time_cursor_color.get())
                    self.cursor_manager.cursor_placement_mode = None
                    self.cursor_overlay.config(text="Double-click to place cursors")
                else:
                    self.cursor_manager.cursor_placement_mode = 'time'
                    self.cursor_manager.last_cursor_click = 'time1'
                    self.cursor_overlay.config(text="Double-click to place Time Cursor 2")
            else:
                self.cursor_manager.cursor_placement_mode = 'time'
                self.cursor_manager.last_cursor_click = None
                self.cursor_overlay.config(text="Double-click to place Time Cursor 1")
        if hasattr(self.parent.master, 'update_measurements'):
            self.parent.master.update_measurements()
        self.canvas.draw()

    def toggle_voltage_cursors(self):
        """Toggle voltage cursors."""
        if not self.volt_cursor_var.get():
            # Store cursor positions before removing
            for name in ['volt1', 'volt2']:
                cursor = self.cursor_manager.cursors[name]
                if cursor['line'] is not None:
                    self.cursor_positions[name] = cursor['value']
            # Disable voltage cursors
            self.cursor_manager.remove_cursor('volt1')
            self.cursor_manager.remove_cursor('volt2')
            if self.cursor_manager.cursor_placement_mode == 'voltage':
                # Switch to time mode if time cursors are enabled
                if self.time_cursor_var.get():
                    self.cursor_manager.cursor_placement_mode = 'time'
                    self.cursor_overlay.config(text="Double-click to place Time Cursor 1")
                else:
                    self.cursor_manager.cursor_placement_mode = None
                    self.cursor_manager.last_cursor_click = None
                    self.cursor_overlay.config(text="Double-click to place cursors")
        else:
            # Enable voltage cursors and restore positions if they exist
            if self.cursor_positions['volt1'] is not None:
                self.cursor_manager.add_cursor('volt1', self.cursor_positions['volt1'], vertical=False, color=self.volt_cursor_color.get())
                if self.cursor_positions['volt2'] is not None:
                    self.cursor_manager.add_cursor('volt2', self.cursor_positions['volt2'], vertical=False, color=self.volt_cursor_color.get())
                    self.cursor_manager.cursor_placement_mode = None
                    self.cursor_overlay.config(text="Double-click to place cursors")
                else:
                    self.cursor_manager.cursor_placement_mode = 'voltage'
                    self.cursor_manager.last_cursor_click = 'volt1'
                    self.cursor_overlay.config(text="Double-click to place Voltage Cursor 2")
            else:
                self.cursor_manager.cursor_placement_mode = 'voltage'
                self.cursor_manager.last_cursor_click = None
                self.cursor_overlay.config(text="Double-click to place Voltage Cursor 1")
        if hasattr(self.parent.master, 'update_measurements'):
            self.parent.master.update_measurements()
        self.canvas.draw()

    def on_plot_click(self, event):
        """Handle mouse clicks on the plot."""
        if event.inaxes != self.ax or self.toolbar.mode != "":
            return
            
        if event.button == 1 and event.dblclick:  # Check for left double-click
            if self.time_cursor_var.get() and self.cursor_manager.cursor_placement_mode == 'time':
                self._handle_time_cursor_placement(event)
            elif self.volt_cursor_var.get() and self.cursor_manager.cursor_placement_mode == 'voltage':
                self._handle_voltage_cursor_placement(event)
            elif self.time_cursor_var.get():
                self.cursor_manager.cursor_placement_mode = 'time'
                self._handle_time_cursor_placement(event)
            elif self.volt_cursor_var.get():
                self.cursor_manager.cursor_placement_mode = 'voltage'
                self._handle_voltage_cursor_placement(event)
        elif event.button == 1:  # Single left-click
            self.cursor_manager.on_click(event)

    def _handle_time_cursor_placement(self, event):
        """Handle time cursor placement."""
        if self.cursor_manager.cursor_placement_mode != 'time':
            self.cursor_manager.cursor_placement_mode = 'time'
            self.cursor_manager.last_cursor_click = None
            
        if self.cursor_manager.last_cursor_click is None:
            self.cursor_manager.add_cursor('time1', event.xdata, color=self.time_cursor_color.get())
            self.cursor_positions['time1'] = event.xdata
            self.cursor_manager.last_cursor_click = 'time1'
            self.cursor_overlay.config(text="Double-click to place Time Cursor 2")
        else:
            self.cursor_manager.add_cursor('time2', event.xdata, color=self.time_cursor_color.get())
            self.cursor_positions['time2'] = event.xdata
            self.cursor_manager.cursor_placement_mode = None
            self.cursor_manager.last_cursor_click = None
            self.cursor_overlay.config(text="Double-click to place cursors")
        
        # Force update measurements
        if hasattr(self.parent.master, 'update_measurements'):
            self.parent.master.update_measurements()
        self.canvas.draw()

    def _handle_voltage_cursor_placement(self, event):
        """Handle voltage cursor placement."""
        if self.cursor_manager.cursor_placement_mode != 'voltage':
            self.cursor_manager.cursor_placement_mode = 'voltage'
            self.cursor_manager.last_cursor_click = None
            
        if self.cursor_manager.last_cursor_click is None:
            self.cursor_manager.add_cursor('volt1', event.ydata, vertical=False, color=self.volt_cursor_color.get())
            self.cursor_positions['volt1'] = event.ydata
            self.cursor_manager.last_cursor_click = 'volt1'
            self.cursor_overlay.config(text="Double-click to place Voltage Cursor 2")
        else:
            self.cursor_manager.add_cursor('volt2', event.ydata, vertical=False, color=self.volt_cursor_color.get())
            self.cursor_positions['volt2'] = event.ydata
            self.cursor_manager.cursor_placement_mode = None
            self.cursor_manager.last_cursor_click = None
            self.cursor_overlay.config(text="Double-click to place cursors")
        
        # Force update measurements
        if hasattr(self.parent.master, 'update_measurements'):
            self.parent.master.update_measurements()
        self.canvas.draw()

    def on_motion(self, event):
        """Handle mouse motion for cursor dragging."""
        self.cursor_manager.on_motion(event)
        if self.cursor_manager.dragging and hasattr(self.parent.master, 'update_measurements'):  # Only update measurements if actually dragging
            self.parent.master.update_measurements()

    def on_release(self, event):
        """Handle mouse release."""
        was_dragging = self.cursor_manager.dragging
        self.cursor_manager.on_release(event)
        if was_dragging and hasattr(self.parent.master, 'update_measurements'):  # Update measurements after drag ends
            self.parent.master.update_measurements()

    def update_channel_controls(self, data):
        """Update channel controls based on available channels in the data."""
        # Clear existing channel controls
        for widget in self.channel_frame.winfo_children():
            widget.destroy()
        
        # Clear existing channel variables
        self.channel_vars.clear()
        
        # Create new channel controls for each channel in the data
        for channel in [col for col in data.columns if col.startswith('CH')]:
            self.channel_vars[channel] = tk.BooleanVar(value=True)
            # Create a closure to capture the current channel
            ttk.Checkbutton(
                self.channel_frame,
                text=channel,
                variable=self.channel_vars[channel],
                command=lambda ch=channel: self.update_plot()  # No need to pass data/metadata here
            ).pack(side=tk.LEFT, padx=2) 