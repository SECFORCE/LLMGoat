import os
import sys
import datetime
from llmgoat.utils import definitions


class Logger:
    COLORS = {
        "DEBUG": "\033[94m",   # Blue
        "INFO": "\033[92m",    # Green
        "WARNING": "\033[38;5;214m",  # Orange (256-color escape)
        "ERROR": "\033[91m",   # Red
        "RESET": "\033[0m",
        "BOLD": "\033[1m"
    }

    LEVELS = ["DEBUG", "INFO", "WARNING", "ERROR"]
    # compute padding to align levels
    _max_len = max(len(level) for level in LEVELS)

    def _log(self, level: str, message: str):
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        color = self.COLORS[level]
        reset = self.COLORS["RESET"]
        bold = self.COLORS["BOLD"]
        # Align type with spaces inside brackets
        padded_level = f"{level:<{self._max_len}}"
        log_line = f"{now} [{color}{padded_level}{reset}] {bold}{message}{reset}"
        print(log_line, file=sys.stdout)

    def debug(self, message: str):
        verbose_env_value = os.environ.get(definitions.LLMGOAT_VERBOSE, str(int(False)))
        is_verbose = True if verbose_env_value == "1" else False
        if is_verbose:
            self._log("DEBUG", message)

    def info(self, message: str):
        self._log("INFO", message)

    def warning(self, message: str):
        self._log("WARNING", message)

    def error(self, message: str):
        self._log("ERROR", message)


# Create a single shared instance
goatlog = Logger()
