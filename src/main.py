#!/usr/bin/env python3

from src.ui.oscilloscope_viewer import OscilloscopeViewer

def main():
    app = OscilloscopeViewer()
    app.configure(bg='#2b2b2b')
    app.mainloop()

if __name__ == "__main__":
    main()