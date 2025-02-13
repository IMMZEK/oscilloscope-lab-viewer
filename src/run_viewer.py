#!/usr/bin/env python3
import os
import sys
import tkinter as tk

# Verify tkinter is available
try:
    root = tk.Tk()
    root.withdraw()
except:
    print("Error: tkinter is not available. Please ensure Python is installed with tkinter support.")
    sys.exit(1)

# Add the workspace root to PYTHONPATH
workspace_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, workspace_root)

# Import and run the main application
from src.ui.oscilloscope_viewer import OscilloscopeViewer

if __name__ == "__main__":
    app = OscilloscopeViewer()
    app.mainloop()  # Changed from run() to mainloop()