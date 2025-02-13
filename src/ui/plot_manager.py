import tkinter as tk
from tkinter import ttk
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from src.ui.cursor_manager import CursorManager
from src.themes.theme_manager import ThemeManager

class PlotManager(ttk.Frame):
    def __init__(self, parent, viewer):
        super().__init__(parent)
        self.parent = parent
        self.viewer = viewer
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
        self.current_theme = None  # Store current theme
        
        # Get initial theme from parent's theme manager
        if hasattr(self.parent.master, 'theme_manager'):
            self.theme_manager = self.parent.master.theme_manager
            initial_theme = self.theme_manager.get_current_theme()
            if initial_theme:
                self.current_theme = initial_theme['plot']
        else:
            # Use Gruvbox Dark as fallback
            self.theme_manager = ThemeManager()
            initial_theme = self.theme_manager.get_theme("White")
            if initial_theme:
                self.current_theme = initial_theme['plot']
        
        self.setup_plot()
        self.setup_controls()

    def apply_theme(self, theme):
        """Apply theme to plot and related widgets."""
        self.current_theme = theme
        
        # Update figure and axes colors
        self.fig.set_facecolor(theme['bg'])
        self.ax.set_facecolor(theme['bg'])
        self.ax.grid(True, color=theme['grid'], linestyle='--', alpha=0.5)
        self.ax.tick_params(colors=theme['text'])
        
        # Update spines
        for spine in self.ax.spines.values():
            spine.set_color(theme['text'])
        
        # Update labels
        self.ax.xaxis.label.set_color(theme['text'])
        self.ax.yaxis.label.set_color(theme['text'])
        if self.ax.get_title():
            self.ax.title.set_color(theme['text'])
        
        # Update legend if it exists
        if self.ax.get_legend():
            self.ax.legend(facecolor=theme['bg'], labelcolor=theme['text'])
        
        # Update cursor overlay
        self.cursor_overlay.configure(
            fg=theme['text'],
            bg=theme['bg']
        )
        
        # Store channel colors for use in update_plot
        self.channel_colors = theme['channel_colors']
        
        # Update toolbar appearance
        if hasattr(self, 'toolbar'):
            # Configure the toolbar's background
            self.toolbar.configure(background=theme['bg'])
            
            # Update the main toolbar frame and all its children
            for widget in self.toolbar.winfo_children():
                if isinstance(widget, tk.Frame):
                    widget.configure(background=theme['bg'])
                    for child in widget.winfo_children():
                        if isinstance(child, (tk.Button, tk.Label)):
                            child.configure(
                                background=theme['bg'],
                                foreground=theme['text'],
                                activebackground=theme['select_bg'],
                                activeforeground=theme['text']
                            )
                        elif isinstance(child, ttk.Separator):
                            style = ttk.Style()
                            style.configure('Toolbar.TSeparator',
                                          background=theme['text'])
                            child.configure(style='Toolbar.TSeparator')
                elif isinstance(widget, tk.Label):  # This handles the coordinate display
                    widget.configure(
                        background=theme['bg'],
                        foreground=theme['text']
                    )
        
        # Update all ttk widgets in the control panel
        self._update_control_panel(theme)
        
        # Configure the frame itself
        style = ttk.Style()
        style.configure('Plot.TFrame',
                       background=theme['bg'])
        self.configure(style='Plot.TFrame')
        
        # Redraw canvas
        self.canvas.draw()

    def _update_control_panel(self, theme):
        """Update the control panel widgets with the current theme."""
        # Update channel checkbuttons
        for widget in self.channel_frame.winfo_children():
            if isinstance(widget, ttk.Checkbutton):
                widget.configure(style='TCheckbutton')
        
        # Update cursor controls
        for frame in self.winfo_children():
            if isinstance(frame, ttk.LabelFrame):
                frame.configure(style='TLabelframe')
                for child in frame.winfo_children():
                    if isinstance(child, ttk.Frame):
                        child.configure(style='TFrame')
                    elif isinstance(child, ttk.Label):
                        child.configure(style='TLabel')
                    elif isinstance(child, ttk.Checkbutton):
                        child.configure(style='TCheckbutton')
                    elif isinstance(child, ttk.Combobox):
                        child.configure(style='Theme.TCombobox')

    def setup_plot(self):
        """Setup the matplotlib plot with enhanced cursor interaction."""
        self.fig = Figure(figsize=(10, 6))
        self.ax = self.fig.add_subplot(111)
        
        # Set initial colors from theme if available
        if self.current_theme:
            self.fig.set_facecolor(self.current_theme['bg'])
            self.ax.set_facecolor(self.current_theme['bg'])
            self.ax.grid(True, color=self.current_theme['grid'], linestyle='--', alpha=0.5)
            self.ax.tick_params(colors=self.current_theme['text'])
            
            # Update spines
            for spine in self.ax.spines.values():
                spine.set_color(self.current_theme['text'])
                
            # Update labels
            self.ax.xaxis.label.set_color(self.current_theme['text'])
            self.ax.yaxis.label.set_color(self.current_theme['text'])
        
        self.canvas = FigureCanvasTkAgg(self.fig, master=self)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # Add navigation toolbar
        self.toolbar = NavigationToolbar2Tk(self.canvas, self)
        self.toolbar.update()
        
        # Initialize cursor manager
        self.cursor_manager = CursorManager(self.ax, self.viewer, self.theme_manager)
        
        # Defer theme setting to after initialization
        self.after(0, lambda: self.cursor_manager.set_theme(self.current_theme) if self.current_theme else None)
        
        # Add cursor instructions overlay
        fallback_theme = self.theme_manager.get_theme("White")['plot']
        self.cursor_overlay = tk.Label(
            self,
            text="Double-click to place cursors\nDrag cursors to move them",
            justify=tk.CENTER,
            fg=self.current_theme['text'] if self.current_theme else fallback_theme['text'],
            bg=self.current_theme['bg'] if self.current_theme else fallback_theme['bg']
        )
        self.cursor_overlay.place(relx=0.98, rely=0.02, anchor='ne')
        
        # Bind events
        self.canvas.mpl_connect('button_press_event', self.on_plot_click)
        self.canvas.mpl_connect('motion_notify_event', self.on_motion)
        self.canvas.mpl_connect('button_release_event', self.on_release)

    def setup_controls(self):
        """Setup plot control panel."""
        control_frame = ttk.LabelFrame(self, text="Display Options", style='TLabelframe')
        control_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Channel selection frame
        self.channel_frame = ttk.Frame(control_frame, style='TFrame')
        self.channel_frame.pack(side=tk.LEFT, padx=5)
        
        # Cursor controls
        cursor_frame = ttk.LabelFrame(control_frame, text="Cursors", style='TLabelframe')
        cursor_frame.pack(side=tk.LEFT, fill=tk.X, padx=5)
        
        # Time cursors
        time_frame = ttk.Frame(cursor_frame, style='TFrame')
        time_frame.pack(side=tk.LEFT, padx=5)
        
        self.time_cursor_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(
            time_frame,
            text="Time",
            variable=self.time_cursor_var,
            command=self.toggle_time_cursors,
            style='TCheckbutton'
        ).pack(side=tk.LEFT)
        
        # Use theme accent color for cursors or fallback to Gruvbox Dark
        fallback_theme = self.theme_manager.get_theme("White")['plot']
        default_color = self.current_theme.get('accent', fallback_theme['accent']) if self.current_theme else fallback_theme['accent']
        
        self.time_cursor_color = tk.StringVar(value=default_color)
        time_color_combo = ttk.Combobox(
            time_frame,
            textvariable=self.time_cursor_color,
            values=[default_color],  # Only use theme color
            width=8,
            state='readonly',
            style='TCombobox'
        )
        time_color_combo.pack(side=tk.LEFT, padx=5)
        
        # Voltage cursors
        volt_frame = ttk.Frame(cursor_frame, style='TFrame')
        volt_frame.pack(side=tk.LEFT, padx=5)
        
        self.volt_cursor_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(
            volt_frame,
            text="Voltage",
            variable=self.volt_cursor_var,
            command=self.toggle_voltage_cursors,
            style='TCheckbutton'
        ).pack(side=tk.LEFT)
        
        self.volt_cursor_color = tk.StringVar(value=default_color)
        volt_color_combo = ttk.Combobox(
            volt_frame,
            textvariable=self.volt_cursor_color,
            values=[default_color],  # Only use theme color
            width=8,
            state='readonly',
            style='TCombobox'
        )
        volt_color_combo.pack(side=tk.LEFT, padx=5)

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
        if self.current_theme:
            colors = self.current_theme['channel_colors']
        else:
            theme = self.theme_manager.get_theme("White")
            colors = theme['plot']['channel_colors'] if theme else ['#FFFFFF']
            
        for i, channel in enumerate([col for col in self.current_data.columns if col.startswith('CH')]):
            if channel in self.channel_vars and self.channel_vars[channel].get():
                color = colors[i % len(colors)]
                self.ax.plot(self.current_data['TIME'], self.current_data[channel], 
                           label=channel, color=color, linewidth=1)

        # Apply current theme if it exists
        if self.current_theme:
            self.fig.set_facecolor(self.current_theme['bg'])
            self.ax.set_facecolor(self.current_theme['bg'])
            self.ax.grid(True, color=self.current_theme['grid'], linestyle='--', alpha=0.5)
            self.ax.tick_params(colors=self.current_theme['text'])
            
            for spine in self.ax.spines.values():
                spine.set_color(self.current_theme['text'])

            self.ax.set_xlabel(
                'Time (s)',
                color=self.current_theme['text']
            )
            self.ax.set_ylabel(
                'Voltage (V)',
                color=self.current_theme['text']
            )
            self.ax.legend(
                facecolor=self.current_theme['bg'],
                labelcolor=self.current_theme['text']
            )
            
            if self.current_metadata:
                title = f"Time Scale: {self.current_metadata.get('Horizontal Scale', 'Unknown')}s/div"
                self.ax.set_title(title, color=self.current_theme['text'], pad=10)

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
            ttk.Checkbutton(
                self.channel_frame,
                text=channel,
                variable=self.channel_vars[channel],
                command=lambda ch=channel: self.update_plot(),
                style='TCheckbutton'
            ).pack(side=tk.LEFT, padx=2) 