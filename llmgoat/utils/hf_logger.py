import logging
# The following import is needed in order to setup the logging and then override it
from transformers import BlipProcessor, BlipForConditionalGeneration

LABEL = "HF"
PAD = 7
YELLOW = "\033[93m"   # bright yellow
BOLD = "\033[1m"
RESET = "\033[0m"

formatter = logging.Formatter(
    fmt=f"%(asctime)s [{YELLOW}{LABEL:<{PAD}}{RESET}] {BOLD}%(message)s{RESET}",
    datefmt="%Y-%m-%d %H:%M:%S",
)


def setup_hf_logging():
    # 1) Timestamp only HF loggers; keep same verbosity as your root
    root_level = logging.getLogger().getEffectiveLevel()

    for name in ("transformers", "huggingface_hub"):
        lg = logging.getLogger(name)
        lg.handlers.clear()
        lg.setLevel(root_level)   # WARNING by default, same as before
        lg.propagate = False
#
        h = logging.StreamHandler()
        h.setLevel(logging.NOTSET)
        h.setFormatter(formatter)
        lg.addHandler(h)
