"""
This modules contains the all the static definitions
"""

from os import path
from pathlib import Path

FILE_PATH = Path(__file__)
ROOT_DIR = FILE_PATH.parent.parent.parent.absolute() # The path of the root folder
MAIN_DIR = FILE_PATH.parent.parent.absolute() # The path of the 'llmgoat' folder within the project

# Common definitions
DEFAULT_BASE_PATH = ".LLMGoat" 
LLMGOAT_FOLDER = path.join(Path.home(), DEFAULT_BASE_PATH)

# Definitions for the folders
LLMGOAT_MODELS_FOLDER = "models"
LLMGOAT_CACHE_FOLDER = "cache"

# Default paths
DEFAULT_MODELS_FOLDER = path.join(LLMGOAT_FOLDER, LLMGOAT_MODELS_FOLDER)
DEFAULT_CACHE_FOLDER = path.join(LLMGOAT_FOLDER, LLMGOAT_CACHE_FOLDER)

# Env variables
LLMGOAT_SERVER_HOST="LLMGOAT_SERVER_HOST"
LLMGOAT_SERVER_PORT="LLMGOAT_SERVER_PORT"
LLMGOAT_DEFAULT_MODEL="LLMGOAT_DEFAULT_MODEL"
LLMGOAT_N_THREADS="LLMGOAT_N_THREADS"
LLMGOAT_N_GPU_LAYERS="LLMGOAT_N_GPU_LAYERS"
LLMGOAT_VERBOSE="LLMGOAT_VERBOSE"