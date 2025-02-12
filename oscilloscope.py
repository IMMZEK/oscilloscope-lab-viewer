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

def main():
    # Parse command-line arguments.
    parser = argparse.ArgumentParser(description="Oscilloscope CSV Data Analysis")
    parser.add_argument("csv_file", help="Path to the oscilloscope CSV file")
    parser.add_argument("--channel", default="CH1", help="Channel to analyze (default: CH1)")
    args = parser.parse_args()
    
    # Load data from CSV.
    time, voltage = load_csv(args.csv_file, args.channel)
    
    # Create the initial plot.
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot(time, voltage, label=f"Signal ({args.channel})")
    ax.set_xlabel("Time")
    ax.set_ylabel("Voltage")
    ax.set_title("Oscilloscope Data")
    ax.grid(True)
    ax.legend()
    plt.draw()  # Ensure the plot is drawn before entering interactive mode.
    
    print("\nInteractive Measurement Options:")
    print("  1: Select two points to measure delta x (time difference) and delta y (voltage difference)")
    print("  2: Select two points (defining an x-axis region) to compute the peak-to-peak voltage")
    print("  q: Quit the program")
    print("Note: After selecting an option, click on the plot window to pick points.\n")
    
    # Main interactive loop.
    while True:
        choice = input("Enter option (1: delta measurement, 2: peak-to-peak, q: quit): ").strip().lower()
        
        if choice == 'q':
            print("Exiting interactive mode.")
            break
        
        elif choice == '1':
            print("Please click two points on the plot for delta measurement.")
            pts = plt.ginput(2, timeout=-1)
            if len(pts) < 2:
                print("Not enough points were selected. Please try again.")
                continue
            (x1, y1), (x2, y2) = pts
            dx = x2 - x1
            dy = y2 - y1
            print(f"Delta x (time difference): {dx}")
            print(f"Delta y (voltage difference): {dy}")
            # Mark the selected points and draw a connecting line.
            ax.plot([x1, x2], [y1, y2], 'ro-', label="Delta Measurement")
            ax.text((x1+x2)/2, (y1+y2)/2,
                    f"dx={dx:.3g}\ndy={dy:.3g}",
                    fontsize=9, color='red',
                    bbox=dict(facecolor='white', alpha=0.5))
            fig.canvas.draw()
        
        elif choice == '2':
            print("Please click two points on the plot to define the x-range for peak-to-peak measurement.")
            pts = plt.ginput(2, timeout=-1)
            if len(pts) < 2:
                print("Not enough points were selected. Please try again.")
                continue
            (x1, _), (x2, _) = pts
            xmin, xmax = sorted([x1, x2])
            # Select indices corresponding to the chosen x-range.
            indices = np.where((time >= xmin) & (time <= xmax))[0]
            if len(indices) == 0:
                print("No data found in the selected region. Try a different region.")
                continue
            region_voltage = voltage[indices]
            v_peak = np.max(region_voltage)
            v_min = np.min(region_voltage)
            peak_to_peak = v_peak - v_min
            print(f"Peak-to-peak voltage in region ({xmin} to {xmax}): {peak_to_peak}")
            # Highlight the region with vertical dashed lines.
            ax.axvline(x=xmin, color='green', linestyle='--', label="Region Start")
            ax.axvline(x=xmax, color='green', linestyle='--', label="Region End")
            ax.text((xmin+xmax)/2, v_min,
                    f"Peak-to-Peak:\n{peak_to_peak:.3g}",
                    fontsize=9, color='green', ha='center', va='bottom',
                    bbox=dict(facecolor='white', alpha=0.5))
            fig.canvas.draw()
        
        else:
            print("Invalid option. Please enter 1, 2, or q.")
    
    # Keep the plot window open until the user closes it.
    plt.show()

if __name__ == '__main__':
    main()
