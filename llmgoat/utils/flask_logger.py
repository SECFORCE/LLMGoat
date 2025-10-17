import logging
import sys

LABEL = "FLASK"
PAD = 7
DARK_GREEN = "\033[96m"
BOLD = "\033[1m"
RESET = "\033[0m"

formatter = logging.Formatter(
    fmt=f"%(asctime)s [{DARK_GREEN}{LABEL:<{PAD}}{RESET}] {BOLD}%(message)s{RESET}",
    datefmt="%Y-%m-%d %H:%M:%S",
)

def setup_flask_logging(app, verbose=False, level=logging.INFO):
    """
    Configure isolated logging for a Flask app.
    
    :param app: The Flask app instance.
    :param level: Logging level (default: INFO).
    """

    # If not verbose just return, nothing to do here
    if not verbose:
        return

    # Use Flask's own logger
    flask_logger = app.logger
    flask_logger.setLevel(level)

    # Remove default handlers (Flask may add one if debug mode was enabled)
    flask_logger.handlers.clear()

    # Choose handler type
    #if log_file:
    #    handler = logging.FileHandler(log_file)
    #else:
    handler = logging.StreamHandler(sys.stdout)

    handler.setFormatter(formatter)

    flask_logger.addHandler(handler)

    flask_logger.propagate = False  # prevent duplication into root logger
