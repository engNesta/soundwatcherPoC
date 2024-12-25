import os
import json
from tkinter import filedialog


class LogManager:
    def __init__(self, default_log_file="logs.json", config_file="config.json"):
        self.config_file = config_file
        self.log_file_path = default_log_file
        self.load_config()

    def load_config(self):
        """
        Load the log file path from the config file or set a default path.
        """
        if os.path.exists(self.config_file):
            with open(self.config_file, "r") as f:
                config = json.load(f)
                self.log_file_path = config.get("log_file_path", self.log_file_path)
        else:
            # Default to the user's Documents folder if no config exists
            default_directory = os.path.join(os.path.expanduser("~"), "Documents", "Soundwatcher")
            os.makedirs(default_directory, exist_ok=True)
            self.log_file_path = os.path.join(default_directory, "logs.json")
            self.save_config()

    def save_config(self):
        """
        Save the log file path to the config file.
        """
        config = {"log_file_path": self.log_file_path}
        with open(self.config_file, "w") as f:
            json.dump(config, f, indent=4)

    def prompt_for_log_file(self):
        """
        Prompt the user to select or confirm a directory for storing logs.
        """
        directory = filedialog.askdirectory(title="Select Directory for Logs")
        if directory:
            self.log_file_path = os.path.join(directory, "logs.json")
            self.save_config()

    def initialize_log_file(self):
        """
        Create the log file if it doesn't exist.
        """
        if not os.path.exists(self.log_file_path):
            with open(self.log_file_path, "w") as f:
                json.dump([], f, indent=4)

    def save_log(self, log_entry):
        """
        Save a single log entry to the log file.
        """
        try:
            self.initialize_log_file()
            with open(self.log_file_path, "r") as f:
                logs = json.load(f)

            logs.append(log_entry)

            with open(self.log_file_path, "w") as f:
                json.dump(logs, f, indent=4)
        except Exception as e:
            print(f"Error saving log: {e}")

    def fetch_logs(self):
        """
        Fetch all logs from the log file.
        """
        try:
            self.initialize_log_file()
            with open(self.log_file_path, "r") as f:
                return json.load(f)
        except Exception as e:
            print(f"Error fetching logs: {e}")
            return []
