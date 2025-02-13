# ESET 355 Lab Viewer

A Python-based oscilloscope viewer for ESET 355 lab data.

## Features

- Load oscilloscope data from CSV files.
- Visualize data with customizable plots.
- Interactive measurement tools for analyzing voltage and time differences.
- Support for multiple channels.
- Cursor controls for precise measurements with real-time readouts.

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/eset355-lab-viewer.git
   cd eset355-lab-viewer
   ```

2. Install Miniconda:
   - Download Miniconda from the official website: [https://docs.conda.io/en/latest/miniconda.html](https://docs.conda.io/en/latest/miniconda.html)
   - Follow the installation instructions for your operating system.

3. Create a conda environment:
   ```
   conda create --name eset355-lab-viewer python=3.11.11
   conda activate eset355-lab-viewer
   ```

4. Install the required packages:
   ```
   pip install -r requirements.txt
   ```

## Building and Running

You can build and run the application using any of these methods:

### 1. Combined Build and Run (Recommended)

This method ensures proper Bazel dependency management with system Python execution:

```bash
# Make the script executable (first time only)
chmod +x build_and_run.sh

# Build and run the application
./build_and_run.sh
```

### 2. Using Bazel

1. Build and run the project:
   ```bash
   # Clean build (recommended for first run)
   bazel clean

   # Build the project
   bazel build //src:viewer

   # Run with Bazel
   bazel run //src:viewer
   ```

2. For development, you can update dependencies:
   ```bash
   # Update dependencies
   bazel run //:requirements.update

   # Clean and rebuild
   bazel clean && bazel build //src:viewer
   ```

### 3. Using Python Directly

The recommended way to run the application is using the provided run script:

```bash
# Make the script executable (first time only)
chmod +x run.sh

# Run the application
./run.sh
```

The run script ensures proper integration with system dependencies while using Bazel-managed Python packages.

## Development

When adding new Python dependencies:

1. Add them to `requirements.txt`
2. Update the Bazel dependencies:
   ```bash
   bazel run //:requirements.update
   ```
3. Rebuild the project:
   ```bash
   bazel build //src:viewer
   ```

## Project Structure

- `src/`: Main application source code
  - `core/`: Core data handling functionality
  - `ui/`: User interface components
- `Lab3/`: Lab data files
  - `Data/`: CSV data files

## Dependencies

- Python 3.9+
- matplotlib
- numpy
- pandas
- tkinter (system Python)

## Usage

To run the application, execute the following command:
```
python oscilloscope.py
```

You can open a CSV file containing oscilloscope data through the GUI and start analyzing the data.

## Contributing

Contributions are welcome! Please open an issue or submit a pull request for any improvements or bug fixes.

## License

This project is licensed under the MIT License.