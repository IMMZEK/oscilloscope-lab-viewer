import os
import tkinter as tk
from tkinter import ttk, messagebox
from src.core.data_handler import DataHandler
from src.ui.file_browser import FileBrowser
from src.ui.plot_manager import PlotManager
from src.themes.theme_manager import ThemeManager

class OscilloscopeViewer(tk.Tk):
    def __init__(self):
        super().__init__()
        
        # Initialize variables
        self.script_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        self.data_handler = DataHandler()
        self.theme_manager = ThemeManager()
        
        # Configure the window
        self.title("Oscilloscope Data Viewer")
        self.geometry("1400x900")
        
        # Set theme and style
        self.setup_theme()
        
        # Create main layout
        self.create_layout()
        
        # Auto-load the Lab3/Data directory if it exists
        default_data_path = os.path.join(self.script_dir, "Lab3", "Data")
        if os.path.exists(default_data_path):
            self.file_browser.data_folder = default_data_path
            self.after(100, self.file_browser.refresh_files)
            self.set_status(f"Loading default folder: {default_data_path}")

    def setup_theme(self):
        """Configure the application theme and styles."""
        # Set initial theme
        self.theme_manager.set_current_theme("White")
        self.apply_current_theme()

    def apply_current_theme(self):
        """Apply the current theme to all widgets with comprehensive color settings."""
        theme = self.theme_manager.get_current_theme()
        if not theme:
            return
    
        ui_theme = theme["ui"]
        style = ttk.Style()
    
        # Set default style options
        style.configure('.',
                        background=ui_theme['bg'],
                        foreground=ui_theme['fg'],
                        fieldbackground=ui_theme['bg'],
                        selectbackground=ui_theme['select_bg'],
                        selectforeground=ui_theme['fg'])
        
        # Configure Treeview including heading and alternate row colors
        style.configure('Treeview',
                        background=ui_theme['bg'],
                        foreground=ui_theme['fg'],
                        fieldbackground=ui_theme['bg'],
                        selectbackground=ui_theme['select_bg'],
                        selectforeground=ui_theme['fg'])
        style.map('Treeview',
                  background=[('selected', ui_theme['select_bg']),
                              ('!selected', ui_theme['bg']),
                              ('disabled', ui_theme.get('disabled_bg', ui_theme['bg']))],
                  foreground=[('selected', ui_theme['fg']),
                              ('!selected', ui_theme['fg']),
                              ('disabled', ui_theme.get('disabled_fg', ui_theme['fg']))])
        # Configure Treeview heading (header) styling
        style.configure('Treeview.Heading',
                        background=ui_theme.get('header_bg', ui_theme['frame_bg']),
                        foreground=ui_theme.get('header_fg', ui_theme['fg']),
                        relief='raised')
        # Configure alternate row colors for Treeview
        style.configure('Treeview.EvenRow',
                        background=ui_theme.get('even_row_bg', ui_theme['bg']))
        style.configure('Treeview.OddRow',
                        background=ui_theme.get('odd_row_bg', ui_theme['bg']))
    
        # Configure frames and labelframes
        style.configure('TFrame', background=ui_theme['bg'])
        style.configure('TLabelframe',
                        background=ui_theme['bg'],
                        foreground=ui_theme['fg'])
        style.map('TLabelframe',
                  background=[('disabled', ui_theme.get('disabled_bg', ui_theme['bg']))],
                  foreground=[('disabled', ui_theme.get('disabled_fg', ui_theme['fg']))])
        style.configure('TLabelframe.Label',
                        background=ui_theme['bg'],
                        foreground=ui_theme['fg'])
        style.map('TLabelframe.Label',
                  background=[('disabled', ui_theme.get('disabled_bg', ui_theme['bg']))],
                  foreground=[('disabled', ui_theme.get('disabled_fg', ui_theme['fg']))])
    
        # Configure labels
        style.configure('TLabel',
                        background=ui_theme['bg'],
                        foreground=ui_theme['fg'])
        style.map('TLabel',
                  background=[('disabled', ui_theme.get('disabled_bg', ui_theme['bg']))],
                  foreground=[('disabled', ui_theme.get('disabled_fg', ui_theme['fg']))])
    
        # Configure buttons with additional states
        style.configure('TButton',
                        background=ui_theme['frame_bg'],
                        foreground=ui_theme['fg'])
        style.map('TButton',
                  background=[('active', ui_theme.get('hover_bg', ui_theme['select_bg'])),
                              ('pressed', ui_theme.get('pressed_bg', ui_theme['select_bg'])),
                              ('disabled', ui_theme.get('disabled_bg', ui_theme['frame_bg']))],
                  foreground=[('active', ui_theme['fg']),
                              ('pressed', ui_theme['fg']),
                              ('disabled', ui_theme.get('disabled_fg', ui_theme['fg']))])
    
        # Configure comboboxes with additional states
        style.configure('TCombobox',
                        background=ui_theme['frame_bg'],
                        foreground=ui_theme['fg'],
                        fieldbackground=ui_theme['bg'],
                        selectbackground=ui_theme['select_bg'],
                        selectforeground=ui_theme['fg'],
                        arrowcolor=ui_theme['fg'])
        style.map('TCombobox',
                  background=[('readonly', ui_theme['frame_bg']),
                              ('disabled', ui_theme.get('disabled_bg', ui_theme['frame_bg']))],
                  fieldbackground=[('readonly', ui_theme['bg']),
                                   ('disabled', ui_theme.get('disabled_bg', ui_theme['bg']))],
                  selectbackground=[('readonly', ui_theme['select_bg'])],
                  selectforeground=[('readonly', ui_theme['fg'])])
    
        # Configure checkbuttons with additional states
        style.configure('TCheckbutton',
                        background=ui_theme['bg'],
                        foreground=ui_theme['fg'],
                        indicatorcolor=ui_theme['fg'],
                        indicatorbackground=ui_theme['bg'])
        style.map('TCheckbutton',
                  background=[('active', ui_theme['bg']),
                              ('disabled', ui_theme.get('disabled_bg', ui_theme['bg']))],
                  foreground=[('active', ui_theme['fg']),
                              ('disabled', ui_theme.get('disabled_fg', ui_theme['fg']))])
    
        # Configure entry widgets (if used)
        style.configure('TEntry',
                        fieldbackground=ui_theme['bg'],
                        foreground=ui_theme['fg'],
                        bordercolor=ui_theme.get('border_color', ui_theme['fg']),
                        lightcolor=ui_theme.get('light_color', ui_theme['select_bg']),
                        insertcolor=ui_theme.get('cursor_color', ui_theme['fg']))
        style.map('TEntry',
                  fieldbackground=[('disabled', ui_theme.get('disabled_bg', ui_theme['bg']))],
                  foreground=[('disabled', ui_theme.get('disabled_fg', ui_theme['fg']))],
                  focus=[('focus', ui_theme.get('focus_bg', ui_theme['select_bg']))])
    
        # Configure separators
        style.configure('TSeparator',
                        background=ui_theme['fg'])
    
        # Configure status bar
        style.configure('Status.TLabel',
                        background=ui_theme['frame_bg'],
                        foreground=ui_theme['fg'],
                        relief='sunken')
    
        # Update window background
        self.configure(bg=ui_theme['bg'])
    
        # Update status bar widget if available
        if hasattr(self, 'status_bar'):
            self.status_bar.configure(style='Status.TLabel')
    
        # Recursively update all child widgets
        self._update_widget_colors(self, ui_theme)
    
        # Update plot colors if a plot manager exists
        if hasattr(self, 'plot_manager'):
            self.plot_manager.apply_theme(theme['plot'])
    
        # Force redraw of all widgets
        self.update_idletasks()

    def _update_widget_colors(self, widget, theme):
        """Recursively update colors of all widgets."""
        try:
            # Update ttk widget style
            if isinstance(widget, ttk.Widget):
                if isinstance(widget, ttk.Button):
                    widget.configure(style='TButton')
                elif isinstance(widget, ttk.Combobox):
                    widget.configure(style='TCombobox')
                elif isinstance(widget, ttk.Separator):
                    widget.configure(style='Toolbar.TSeparator')
                else:
                    widget.configure(style=widget.winfo_class())
            # Update tk widget colors
            elif isinstance(widget, (tk.Label, tk.Frame, tk.LabelFrame)):
                widget.configure(
                    background=theme['bg'],
                    foreground=theme['fg']
                )
            elif isinstance(widget, tk.Entry):
                widget.configure(
                    background=theme['bg'],
                    foreground=theme['fg'],
                    insertbackground=theme['fg'],
                    selectbackground=theme['select_bg'],
                    selectforeground=theme['fg']
                )
            elif isinstance(widget, (tk.Listbox, tk.Text)):
                widget.configure(
                    background=theme['bg'],
                    foreground=theme['fg'],
                    selectbackground=theme['select_bg'],
                    selectforeground=theme['fg']
                )
            elif isinstance(widget, tk.Button):
                widget.configure(
                    background=theme['frame_bg'],
                    foreground=theme['fg'],
                    activebackground=theme['select_bg'],
                    activeforeground=theme['fg'],
                    highlightbackground=theme['bg'],
                    highlightcolor=theme['fg']
                )
        except tk.TclError:
            # Some widgets might not support all configurations
            pass
        
        # Recursively update all children
        for child in widget.winfo_children():
            self._update_widget_colors(child, theme)

    def create_layout(self):
        """Create the main application layout."""
        # Create main container
        self.main_frame = ttk.Frame(self)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Create theme selector
        theme_frame = ttk.Frame(self.main_frame)
        theme_frame.pack(side=tk.TOP, anchor=tk.NE, padx=5, pady=5)
        
        ttk.Label(theme_frame, text="Theme:").pack(side=tk.LEFT, padx=5)
        
        self.theme_var = tk.StringVar(value=self.theme_manager.current_theme)
        theme_combo = ttk.Combobox(
            theme_frame,
            textvariable=self.theme_var,
            values=self.theme_manager.get_theme_names(),
            state='readonly',
            style='Theme.TCombobox'
        )
        theme_combo.pack(side=tk.LEFT, padx=5)
        theme_combo.bind('<<ComboboxSelected>>', lambda e: self.change_theme())
        
        # Create central layout
        self.content_frame = ttk.Frame(self.main_frame)
        self.content_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create status bar
        self.status_bar = ttk.Label(
            self.main_frame,
            text="Ready",
            relief=tk.SUNKEN,
            anchor=tk.W
        )
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Setup panels
        self.create_left_panel()
        self.create_right_panel()

    def create_left_panel(self):
        """Create the left panel with file browser and measurements."""
        self.left_panel = ttk.Frame(self.content_frame, width=300)
        self.left_panel.pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=5)
        
        # Add file browser
        self.file_browser = FileBrowser(
            self.left_panel,
            initial_dir=os.path.join(self.script_dir, "Lab3", "Data"),
            on_file_select=self.load_data
        )
        self.file_browser.pack(fill=tk.BOTH, expand=True)
        
        # Add measurements panel
        self.setup_measurements_panel()

    def create_right_panel(self):
        """Create the right panel with plot area."""
        self.right_panel = ttk.Frame(self.content_frame)
        self.right_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Add plot manager
        self.plot_manager = PlotManager(self.right_panel, self)
        self.plot_manager.pack(fill=tk.BOTH, expand=True)
        
        # Apply current theme to plot manager
        theme = self.theme_manager.get_current_theme()
        if theme:
            self.plot_manager.apply_theme(theme['plot'])

    def setup_measurements_panel(self):
        """Setup the measurements panel."""
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
        self.auto_frame = ttk.LabelFrame(measurements_frame, text="Automatic Measurements")
        self.auto_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Initialize empty measurements dictionary
        self.measurements = {}

    def load_data(self, filepath):
        """Load data from a CSV file."""
        try:
            self.set_status(f"Loading {os.path.basename(filepath)}...")
            
            # Load data using data handler
            data, metadata = self.data_handler.load_data(filepath)
            
            # Update window title
            self.title(f"Oscilloscope Data - {os.path.basename(filepath)} - {metadata.get('Model', 'Unknown')}")
            
            # Update plot with filepath
            self.plot_manager.update_plot(data, metadata, filepath)
            
            # Update measurements
            self.update_measurements()
            
            self.set_status(f"Successfully loaded {os.path.basename(filepath)}")
            
        except Exception as e:
            self.set_status(f"Error: {str(e)}")
            messagebox.showerror("Error", f"Failed to load file: {str(e)}")

    def update_measurements(self):
        """Update all measurements."""
        # Update cursor measurements
        cursor_measurements = self.plot_manager.cursor_manager.get_cursor_measurements()
        
        # Update cursor positions
        for name in ['time1', 'time2', 'volt1', 'volt2']:
            if name in cursor_measurements:
                if 'time' in name:
                    self.cursor_pos[name].set(f"TIME{name[-1]}: {cursor_measurements[name]:.2e} s")
                else:
                    self.cursor_pos[name].set(f"VOLT{name[-1]}: {cursor_measurements[name]:.3f} V")
            else:
                self.cursor_pos[name].set(f"{'TIME' if 'time' in name else 'VOLT'}{name[-1]}: --")
        
        # Update delta measurements
        if 'delta_t' in cursor_measurements:
            self.delta_t_var.set(f"ΔT: {cursor_measurements['delta_t']:.2e} s")
            self.cursor_freq_var.set(f"1/ΔT: {cursor_measurements['freq']:.2e} Hz")
        else:
            self.delta_t_var.set("ΔT: --")
            self.cursor_freq_var.set("1/ΔT: --")
            
        if 'delta_v' in cursor_measurements:
            self.delta_v_var.set(f"ΔV: {cursor_measurements['delta_v']:.3f} V")
        else:
            self.delta_v_var.set("ΔV: --")
        
        # Clear existing measurements
        for widget in self.auto_frame.winfo_children():
            widget.destroy()
        self.measurements.clear()
        
        # Update automatic measurements for each enabled channel
        for channel in self.plot_manager.channel_vars:
            if self.plot_manager.channel_vars[channel].get():
                # Create a new frame for this channel's measurements
                channel_frame = ttk.LabelFrame(self.auto_frame, text=channel)
                channel_frame.pack(fill=tk.X, padx=5, pady=5)
                
                # Initialize measurements for this channel
                self.measurements[channel] = {
                    'Vpp': tk.StringVar(value="Vpp: --"),
                    'Vmax': tk.StringVar(value="Vmax: --"),
                    'Vmin': tk.StringVar(value="Vmin: --"),
                    'Freq': tk.StringVar(value="Freq: --"),
                    'Period': tk.StringVar(value="Period: --"),
                    'Rise': tk.StringVar(value="Rise: --"),
                    'Fall': tk.StringVar(value="Fall: --"),
                    'Duty': tk.StringVar(value="Duty: --")
                }
                
                # Get measurements for this channel
                measurements = self.data_handler.get_measurements(channel)
                if measurements:
                    self.measurements[channel]['Vpp'].set(f"Vpp: {measurements['vpp']:.3f} V")
                    self.measurements[channel]['Vmax'].set(f"Vmax: {measurements['vmax']:.3f} V")
                    self.measurements[channel]['Vmin'].set(f"Vmin: {measurements['vmin']:.3f} V")
                    self.measurements[channel]['Freq'].set(f"Freq: {measurements['freq']:.2e} Hz")
                    self.measurements[channel]['Period'].set(f"Period: {measurements['period']:.2e} s")
                    self.measurements[channel]['Rise'].set(f"Rise: {measurements['rise_time']:.2e} s")
                    self.measurements[channel]['Fall'].set(f"Fall: {measurements['fall_time']:.2e} s")
                    self.measurements[channel]['Duty'].set(f"Duty: {measurements['duty']:.1f} %")
                
                # Add labels for this channel's measurements
                for var in self.measurements[channel].values():
                    ttk.Label(channel_frame, textvariable=var).pack(fill=tk.X, padx=5, pady=2)

    def set_status(self, message):
        """Update status bar message."""
        self.status_bar.config(text=message)
        self.update_idletasks()

    def change_theme(self):
        """Change the current theme."""
        self.theme_manager.set_current_theme(self.theme_var.get())
        self.apply_current_theme()
        
        # Refresh file browser and measurements panel
        if hasattr(self, 'file_browser'):
            self.file_browser.refresh_files()
        if hasattr(self, 'plot_manager'):
            self.plot_manager.update_plot()
            
        # Update measurements if they exist
        if hasattr(self, 'update_measurements'):
            self.update_measurements() 