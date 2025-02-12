#!/usr/bin/env python3

import os
import sys

# Add the parent directory to Python path so we can import from src
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.ui.oscilloscope_viewer import OscilloscopeViewer

def main():
    app = OscilloscopeViewer()
    app.configure(bg='#2b2b2b')
    app.mainloop()

if __name__ == "__main__":
    main() 