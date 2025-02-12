# ESET355 Lab Viewer

This project is an oscilloscope data viewer that allows users to load and visualize oscilloscope data from CSV files. The application provides interactive measurement options and a user-friendly interface.

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
   conda create --name eset355-lab-viewer python=3.9
   conda activate eset355-lab-viewer
   ```

4. Install the required packages:
   ```
   pip install -r requirements.txt
   ```

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