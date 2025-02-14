#!/usr/bin/env python3

import os
import sys

# Add the parent directory to Python path so we can import from src
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.ui.oscilloscope_viewer import OscilloscopeViewer

if __name__ == "__main__":
    app = OscilloscopeViewer()
    app.mainloop() 