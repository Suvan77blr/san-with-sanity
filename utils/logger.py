"""
Logging utilities for the erasure coding simulator.

Provides console and optional file logging capabilities.
"""

import datetime
import os

class Logger:
    """
    Handles logging for the simulation.
    """

    def __init__(self, log_to_file=False, log_file="simulation.log"):
        """
        Initialize the logger.

        Args:
            log_to_file: Whether to also log to a file
            log_file: Name of the log file
        """
        self.log_to_file = log_to_file
        self.log_file = log_file
        if log_to_file:
            # Clear previous log file
            with open(self.log_file, 'w') as f:
                f.write(f"Simulation Log - {datetime.datetime.now()}\n")
                f.write("=" * 50 + "\n")

    def _write_to_file(self, message):
        """
        Write message to log file if enabled.

        Args:
            message: Message to write
        """
        if self.log_to_file:
            with open(self.log_file, 'a') as f:
                timestamp = datetime.datetime.now().strftime("%H:%M:%S")
                f.write(f"[{timestamp}] {message}\n")

    def log(self, message):
        """
        Log a general message to console and optionally file.

        Args:
            message: Message to log
        """
        print(message)
        self._write_to_file(message)

    def log_info(self, message):
        """
        Log an informational message.

        Args:
            message: Info message to log
        """
        formatted = f"[INFO] {message}"
        print(formatted)
        self._write_to_file(formatted)

    def log_error(self, message):
        """
        Log an error message.

        Args:
            message: Error message to log
        """
        formatted = f"[ERROR] {message}"
        print(formatted)
        self._write_to_file(formatted)

    def log_success(self, message):
        """
        Log a success message.

        Args:
            message: Success message to log
        """
        formatted = f"[SUCCESS] {message}"
        print(formatted)
        self._write_to_file(formatted)

    def log_header(self, title):
        """
        Log a section header.

        Args:
            title: Header title
        """
        header = f"\n=== {title.upper()} ==="
        print(header)
        self._write_to_file(header)

    def log_data_summary(self, data_type, data):
        """
        Log a summary of data (truncated for readability).

        Args:
            data_type: Type of data being logged
            data: The data to summarize
        """
        if isinstance(data, str):
            summary = data[:200] + "..." if len(data) > 50 else data
        elif isinstance(data, bytes):
            summary = data[:20].hex() + "..." if len(data) > 20 else data.hex()
        elif isinstance(data, list):
            summary = f"List of {len(data)} items"
        else:
            summary = str(data)

        self.log_info(f"{data_type}: {summary}")

    def log_simulation_results(self, rs_stats, lrc_stats):
        """
        Log final simulation results comparison.

        Args:
            rs_stats: Dict with RS simulation statistics
            lrc_stats: Dict with LRC simulation statistics
        """
        self.log_header("FINAL RESULTS")
        self.log_info("Reed-Solomon (RS) Results:")
        self.log_info(f"  - Nodes contacted: {rs_stats.get('nodes_contacted', 'N/A')}")
        self.log_info(f"  - Recovery: {'SUCCESS' if rs_stats.get('success') else 'FAILED'}")

        self.log_info("Local Reconstruction Code (LRC) Results:")
        self.log_info(f"  - Nodes contacted: {lrc_stats.get('nodes_contacted', 'N/A')}")
        self.log_info(f"  - Recovery: {'SUCCESS' if lrc_stats.get('success') else 'FAILED'}")

        rs_contacted = rs_stats.get('nodes_contacted', 0)
        lrc_contacted = lrc_stats.get('nodes_contacted', 0)

        if rs_contacted > lrc_contacted:
            savings = rs_contacted - lrc_contacted
            self.log_success(f"LRC contacted {savings} fewer nodes than RS - demonstrating local repair advantage!")
        elif rs_contacted == lrc_contacted:
            self.log_info("RS and LRC contacted the same number of nodes in this simulation")
        else:
            self.log_info("RS contacted fewer nodes than LRC in this simulation")
