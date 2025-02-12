import pandas as pd
import numpy as np

class DataHandler:
    def __init__(self):
        self.data = None
        self.metadata = {}

    def load_data(self, filepath):
        """Load data from a CSV file."""
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
        
        # Read just the data portion efficiently
        data = pd.read_csv(filepath, skiprows=data_start)
        
        # Verify required columns exist
        required_columns = ['TIME', 'CH1', 'CH2']
        missing_columns = [col for col in required_columns if col not in data.columns]
        if missing_columns:
            raise ValueError(f"Missing required columns: {', '.join(missing_columns)}")
            
        self.data = data
        self.metadata = metadata
        return data, metadata

    def get_measurements(self, channel):
        """Calculate measurements for a given channel."""
        if self.data is None or channel not in self.data.columns:
            return None
            
        data = self.data[channel]
        time = self.data['TIME']
        
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
            
        return {
            'vpp': vpp,
            'vmax': vmax,
            'vmin': vmin,
            'freq': freq,
            'period': period,
            'rise_time': rise_time,
            'fall_time': fall_time,
            'duty': duty
        } 