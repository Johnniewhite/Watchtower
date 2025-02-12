# System Monitor

A comprehensive system monitoring tool built with Python and the `rich` library, providing real-time insights into system performance, including CPU usage, memory statistics, network details, disk I/O, and temperature monitoring.

## Features

- **Real-time Monitoring**: Displays live updates of system metrics.
- **Customizable Display**: Toggle visibility of different sections like CPU, memory, network, disk I/O, and temperature.
- **User-friendly Interface**: Uses the `rich` library for a visually appealing console interface.
- **Cross-platform Support**: Works on Windows, macOS, and Linux (with some features dependent on platform support).

## Installation

1. **Clone the Repository**:

   ```bash
   git clone https://github.com/johnniewhite/watchtower.git
   cd watchtower
   ```

2. **Install Dependencies**:
   Ensure you have Python 3.6 or later installed. Then, install the required packages:

   ```bash
   pip install -r requirements.txt
   ```

   The `requirements.txt` should include:

   ```
   rich
   psutil
   speedtest-cli
   pynput
   ```

## Usage

Run the system monitor using the following command:

```bash
python system_monitor.py
```

### Keyboard Commands

- **q**: Quit the application
- **s**: Toggle Speed Test display
- **p**: Toggle Process List
- **n**: Toggle Network Details
- **d**: Toggle Disk I/O Statistics
- **t**: Toggle Temperature Monitor
- **h**: Show help message

## Configuration

- **Update Intervals**: Adjust the refresh rate by modifying the `refresh_per_second` parameter in the `Live` context.
- **Speed Test Interval**: Change the `SPEED_TEST_INTERVAL` variable to set how often speed tests are conducted.

## Troubleshooting

- **Temperature Monitoring Not Supported**: If you receive an error about temperature monitoring, ensure your system supports it and that `psutil` is up-to-date.
- **Command Not Responding**: Ensure the terminal window is focused and that you are pressing the correct keys.
- **Dependencies Issues**: Verify that all dependencies are installed correctly using `pip list`.

## Contributing

Contributions are welcome! Please fork the repository and submit a pull request with your changes. Ensure your code follows the existing style and includes appropriate documentation.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Contact

For questions or support, please contact [your-email@example.com](mailto:your-email@example.com).

```

### Explanation:

- **Features**: Lists the main capabilities of the application.
- **Installation**: Provides step-by-step instructions to set up the project.
- **Usage**: Explains how to run the application and use its features.
- **Configuration**: Offers guidance on customizing the application.
- **Troubleshooting**: Addresses common issues users might encounter.
- **Contributing**: Encourages community contributions.
- **License**: States the licensing terms.
- **Contact**: Provides a way for users to reach out for support.
