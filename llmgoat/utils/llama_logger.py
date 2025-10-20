import ctypes
import logging
import sys
import contextlib

# =========================
# 1) Styling / shared handler
# =========================
LLAMA_LABEL = "LLAMA"
PAD = 7  # align with [WARNING] length
PURPLE = "\033[95m"
BOLD = "\033[1m"
RESET = "\033[0m"

_formatter = logging.Formatter(
    fmt=f"%(asctime)s [{PURPLE}{LLAMA_LABEL:<{PAD}}{RESET}] {BOLD}%(message)s{RESET}",
    datefmt="%Y-%m-%d %H:%M:%S",
)

_llama_handler = logging.StreamHandler()
_llama_handler.setFormatter(_formatter)
# mark so we don't add duplicates if this module is imported multiple times
setattr(_llama_handler, "_is_llama_handler", True)

# Our named logger for everything LLAMA
llama_logger = logging.getLogger("LLAMA")
llama_logger.propagate = False  # keep output under our format only

# Add our handler exactly once
if not any(getattr(h, "_is_llama_handler", False) for h in llama_logger.handlers):
    llama_logger.addHandler(_llama_handler)

# =========================
# 2) Verbosity control (global min level for native + wrapper)
# =========================
# Default to INFO+ (i.e., verbose=True); you can switch at runtime with setup_llama_logging()
_MIN_LEVEL = logging.INFO


def _py_level_from_verbose(verbose: bool) -> int:
    # verbose=True  -> INFO+
    # verbose=False -> WARNING+
    return logging.INFO if verbose else logging.WARNING


def set_llama_min_level(level: int):
    """
    Raise/lower the minimum level for *native* llama.cpp logs and the Python
    wrapper/logger so they stay consistent with your verbosity preference.
    """
    global _MIN_LEVEL
    _MIN_LEVEL = level
    # Align both our custom logger and the wrapper's logger
    llama_logger.setLevel(level)
    logging.getLogger("llama_cpp").setLevel(level)


def setup_llama_logging(verbose: bool = True):
    """
    Convenience API to match Llama(verbose=...):
      - verbose=True  -> INFO+
      - verbose=False -> WARNING+
    Call this once before creating your Llama(...) instance(s).
    """
    set_llama_min_level(_py_level_from_verbose(verbose))


# Initialize logger levels to current min
set_llama_min_level(_MIN_LEVEL)

# =========================
# 3) Native llama.cpp callback -> our logger (filtered by _MIN_LEVEL)
# =========================
try:
    from llama_cpp import llama_log_callback, llama_log_set  # type: ignore
except Exception:
    llama_log_callback = llama_log_set = None  # noqa: E305


def _to_py_level(level: int) -> int:
    # llama.cpp convention: 0=DEBUG, 1=INFO, 2=WARNING, 3+=ERROR
    if level <= 0:
        return logging.DEBUG
    if level == 1:
        return logging.INFO
    if level == 2:
        return logging.WARNING
    return logging.ERROR


if llama_log_callback and llama_log_set:
    @llama_log_callback
    def _llama_cb(level: int, text: ctypes.c_char_p, user_data):
        # Convert C string -> str and trim trailing newline(s)
        msg = ctypes.cast(text, ctypes.c_char_p).value
        if not msg:
            return
        try:
            s = msg.decode("utf-8", "ignore").rstrip()
        except Exception:
            s = str(msg).rstrip()
        if not s:
            return

        py_level = _to_py_level(level)
        # Drop messages below our chosen minimum level (honors verbose)
        if py_level < _MIN_LEVEL:
            return

        llama_logger.log(py_level, s)

    # Register once (must be done before creating Llama instances)
    llama_log_set(_llama_cb, None)

# =========================
# 4) Route Python wrapper logs ("llama_cpp") into our handler/format
# =========================
_py_wrap_logger = logging.getLogger("llama_cpp")
_py_wrap_logger.propagate = False
# Remove any existing handlers to avoid double-printing, then add ours (once)
_py_wrap_logger.handlers = [h for h in _py_wrap_logger.handlers if getattr(h, "_is_llama_handler", False)]
if not any(getattr(h, "_is_llama_handler", False) for h in _py_wrap_logger.handlers):
    _py_wrap_logger.addHandler(_llama_handler)
# Keep wrapper logger level aligned with our min level
_py_wrap_logger.setLevel(_MIN_LEVEL)


# =========================
# 5) Optional: capture stray print() during sensitive phases
# =========================
class _WriteToLogger:
    def __init__(self, level: int):
        self.level = level
        self._buffer = ""

    def write(self, s: str):
        if not isinstance(s, str):
            s = str(s)
        self._buffer += s
        # flush on newlines to avoid chopping lines mid-message
        while "\n" in self._buffer:
            line, self._buffer = self._buffer.split("\n", 1)
            if line.strip():
                llama_logger.log(self.level, line)

    def flush(self):
        if self._buffer.strip():
            llama_logger.log(self.level, self._buffer.strip())
        self._buffer = ""


@contextlib.contextmanager
def capture_llama_prints(level: int = logging.INFO):
    """
    Temporarily redirect stdout/stderr to the LLAMA logger.
    Use this around model loading if you still see bare prints.
    """
    old_out, old_err = sys.stdout, sys.stderr
    sys.stdout = _WriteToLogger(level)
    sys.stderr = _WriteToLogger(level)
    try:
        yield
    finally:
        try:
            sys.stdout.flush()
            sys.stderr.flush()
        finally:
            sys.stdout, sys.stderr = old_out, old_err
