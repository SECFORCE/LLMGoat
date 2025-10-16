"""
Name: LLMGoat
Description: A deliberately vulnerable environment to learn about LLM-specific risks based on the OWASP Top 10 for LLM Applications.
"""

import os
from llmgoat.utils.definitions import DEFAULT_CACHE_FOLDER

# Project Info
__title__ = "llmgoat"
__version__ = "0.1.0"
__description__ = (
    "A deliberately vulnerable environment to learn about LLM-specific risks based on the OWASP Top 10 for LLM Applications."
)

# Set some env variables
os.environ["TOKENIZERS_PARALLELISM"] = "false"  # Avoid issues when running tokenizers in WSGI servers
os.environ["HF_HOME"] = DEFAULT_CACHE_FOLDER    # Set the cache folder for HuggingFace