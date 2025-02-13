class CursorManager:
    def __init__(self, ax, viewer, theme_manager):
        self.ax = ax
        self.cursors = {
            'time1': {'line': None, 'label': None, 'value': None, 'active': False},
            'time2': {'line': None, 'label': None, 'value': None, 'active': False},
            'volt1': {'line': None, 'label': None, 'value': None, 'active': False},
            'volt2': {'line': None, 'label': None, 'value': None, 'active': False}
        }
        self.dragging = False
        self.active_cursor = None
        self.cursor_placement_mode = None
        self.last_cursor_click = None
        self.current_theme = None
        self.viewer = viewer
        self.theme_manager = theme_manager

    def set_theme(self, theme):
        """Set the current theme."""
        self.current_theme = theme
        self.update_cursor_positions()

    def _get_fallback_theme(self):
        return self.theme_manager.get_theme("White")['plot']

    def add_cursor(self, name, value, vertical=True, color=None):
        """Add a cursor line to the plot."""
        # Remove existing cursor if it exists
        if self.cursors[name]['line'] is not None:
            self.cursors[name]['line'].remove()
            if self.cursors[name]['label'] is not None:
                self.cursors[name]['label'].remove()
        
        # Use the helper to get fallback theme
        fallback_theme = self._get_fallback_theme()
        
        if vertical:
            line = self.ax.axvline(
                value,
                color=color or self.current_theme.get('accent', fallback_theme['accent']),
                linestyle='--',
                alpha=0.8,
                picker=True,
                label=name
            )
            label = self.ax.text(
                value, 0.02,
                f'{name}',
                rotation=90,
                verticalalignment='bottom',
                color=color or self.current_theme.get('accent', fallback_theme['accent']),
                backgroundcolor=self.current_theme.get('bg', fallback_theme['bg']),
                alpha=0.8
            )
        else:
            line = self.ax.axhline(
                value,
                color=color or self.current_theme.get('accent', fallback_theme['accent']),
                linestyle='--',
                alpha=0.8,
                picker=True,
                label=name
            )
            label = self.ax.text(
                0.02, value,
                f'{name}',
                verticalalignment='bottom',
                color=color or self.current_theme.get('accent', fallback_theme['accent']),
                backgroundcolor=self.current_theme.get('bg', fallback_theme['bg']),
                alpha=0.8
            )
        
        self.cursors[name].update({
            'line': line,
            'label': label,
            'value': value,
            'active': True
        })
        
        # Force a redraw
        self.ax.figure.canvas.draw()
        
        # Update measurements in the viewer
        if hasattr(self.viewer, 'update_measurements'):
            self.viewer.update_measurements()

    def remove_cursor(self, name):
        """Remove a cursor and its label from the plot."""
        cursor = self.cursors[name]
        try:
            if cursor['line'] is not None:
                cursor['line'].remove()
                self.ax.figure.canvas.draw()
        except (ValueError, AttributeError):
            pass
            
        try:
            if cursor['label'] is not None:
                cursor['label'].remove()
                self.ax.figure.canvas.draw()
        except (ValueError, AttributeError):
            pass
            
        cursor.update({
            'line': None,
            'label': None,
            'value': None,
            'active': False
        })

    def get_cursor_measurements(self):
        """Get measurements between cursors."""
        measurements = {}
        
        # Individual cursor values
        for name, cursor in self.cursors.items():
            if cursor['value'] is not None:
                measurements[name] = cursor['value']
        
        # Time measurements
        if all(self.cursors[c]['value'] is not None for c in ['time1', 'time2']):
            delta_t = abs(self.cursors['time2']['value'] - self.cursors['time1']['value'])
            freq = 1/delta_t if delta_t != 0 else float('inf')
            measurements['delta_t'] = delta_t
            measurements['freq'] = freq
            
        # Voltage measurements
        if all(self.cursors[c]['value'] is not None for c in ['volt1', 'volt2']):
            delta_v = abs(self.cursors['volt2']['value'] - self.cursors['volt1']['value'])
            measurements['delta_v'] = delta_v
            
        return measurements

    def update_cursor_positions(self):
        """Update cursor positions and labels."""
        # Use the helper to get fallback theme
        fallback_theme = self._get_fallback_theme()
        
        for name, cursor in self.cursors.items():
            if cursor['line'] is not None:
                try:
                    if cursor['label'] is not None:
                        cursor['label'].remove()
                        cursor['label'] = None
                except (ValueError, AttributeError):
                    pass
                    
                # Create new label
                if 'time' in name:
                    cursor['label'] = self.ax.text(
                        cursor['value'],
                        self.ax.get_ylim()[1],
                        f'{name}: {cursor["value"]:.2e}s',
                        rotation=90,
                        color=cursor['line'].get_color(),
                        va='top',
                        ha='right',
                        backgroundcolor=self.current_theme.get('bg', fallback_theme['bg']),
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
                        backgroundcolor=self.current_theme.get('bg', fallback_theme['bg']),
                        alpha=0.8
                    )
        
        # Force a redraw
        self.ax.figure.canvas.draw()
        
        # Update measurements in the viewer
        if hasattr(self.viewer, 'update_measurements'):
            self.viewer.update_measurements()

    def on_click(self, event):
        """Handle mouse click events for cursor dragging."""
        if event.inaxes != self.ax or event.button != 1:  # Only handle left clicks
            return

        # Check if click is near any cursor
        for name, cursor in self.cursors.items():
            if cursor['line'] is None:
                continue

            if 'time' in name:
                # For time cursors, check x-distance
                cursor_x = cursor['line'].get_xdata()[0]
                tolerance = 0.02 * (self.ax.get_xlim()[1] - self.ax.get_xlim()[0])
                if abs(event.xdata - cursor_x) < tolerance:
                    self.active_cursor = name
                    self.dragging = True
                    cursor['active'] = True
                    return
            else:
                # For voltage cursors, check y-distance
                cursor_y = cursor['line'].get_ydata()[0]
                tolerance = 0.02 * (self.ax.get_ylim()[1] - self.ax.get_ylim()[0])
                if abs(event.ydata - cursor_y) < tolerance:
                    self.active_cursor = name
                    self.dragging = True
                    cursor['active'] = True
                    return

    def on_motion(self, event):
        """Handle mouse motion events for cursor dragging."""
        if not self.dragging or not self.active_cursor or event.inaxes != self.ax:
            return

        plot_manager = self.ax.figure.canvas.get_tk_widget().master.master
        cursor = self.cursors[self.active_cursor]
        
        if 'time' in self.active_cursor:
            # Update time cursor position
            cursor['line'].set_xdata([event.xdata, event.xdata])
            cursor['value'] = event.xdata
            # Update stored position in plot manager
            plot_manager.cursor_positions[self.active_cursor] = event.xdata
            # Update file-specific storage
            if plot_manager.current_file:
                plot_manager.file_cursor_positions[plot_manager.current_file][self.active_cursor] = event.xdata
        else:
            # Update voltage cursor position
            cursor['line'].set_ydata([event.ydata, event.ydata])
            cursor['value'] = event.ydata
            # Update stored position in plot manager
            plot_manager.cursor_positions[self.active_cursor] = event.ydata
            # Update file-specific storage
            if plot_manager.current_file:
                plot_manager.file_cursor_positions[plot_manager.current_file][self.active_cursor] = event.ydata

        # Update cursor label
        self.update_cursor_positions()
        self.ax.figure.canvas.draw()
        
        # Update measurements in the viewer
        if hasattr(self.viewer, 'update_measurements'):
            self.viewer.update_measurements()

    def on_release(self, event):
        """Handle mouse release events for cursor dragging."""
        if self.active_cursor:
            self.cursors[self.active_cursor]['active'] = False
            self.active_cursor = None
            self.dragging = False
            self.ax.figure.canvas.draw()
            # Update measurements one final time
            if hasattr(self.viewer, 'update_measurements'):
                self.viewer.update_measurements() 