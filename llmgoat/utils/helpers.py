"""
This module contains multiple helper function used throughout the codebase.
"""
import os
import requests
import shutil
import hashlib
from tqdm import tqdm
from .definitions import LLMGOAT_FOLDER, DEFAULT_MODELS_FOLDER, DEFAULT_CACHE_FOLDER

def banner(version):
    print(f"""
      ░█░░░█░░░█▄█
      ░█░░░█░░░█░█
      ░▀▀▀░▀▀▀░▀░▀
    ░█▀▀░█▀█░█▀█░▀█▀
    ░█░█░█░█░█▀█░░█░
    ░▀▀▀░▀▀▀░▀░▀░░▀░
    LLMGoat v{version}

""")

def file_exists(filepath: str) -> bool:
  """Check if a file exists at the given filepath and return a boolean."""
  return os.path.exists(filepath)

def create_folder_if_missing(path: str) -> None:
  """Utility function to create a folder if missing"""

  if not os.path.isdir(path):
    os.makedirs(path)

def delete_folder_if_exists(path: str) -> None:
  """Utility function to delete a folder if exists"""

  if os.path.isdir(path):
    shutil.rmtree(path)

def ensure_folders():
  # Create the .LLMGoat folder in $HOME if missing
  create_folder_if_missing(LLMGOAT_FOLDER)
  # Create the models and cache folders within the above one if missing
  create_folder_if_missing(DEFAULT_MODELS_FOLDER)
  create_folder_if_missing(DEFAULT_CACHE_FOLDER)


def sha256_of_file(filepath):
    """Calculate the SHA-256 hash of a file."""
    sha256_hash = hashlib.sha256()
    with open(filepath, "rb") as f:
        # Read file in chunks to handle large files efficiently
        for chunk in iter(lambda: f.read(8192), b""):
            sha256_hash.update(chunk)
    return sha256_hash.hexdigest()

def download_file(url, output_folder, filename=None, show_progress=True):
    """Download a file from a URL and save it to the specified output folder."""
    os.makedirs(output_folder, exist_ok=True)
    
    # Determine filename
    if filename is None:
        filename = os.path.basename(url.split("?")[0]) or "downloaded_file"
    
    output_path = os.path.join(output_folder, filename)

    # Stream download
    with requests.get(url, stream=True) as r:
        r.raise_for_status()
        total_size = int(r.headers.get('content-length', 0))
        chunk_size = 8192

        progress = tqdm(
            total=total_size,
            unit='B',
            unit_scale=True,
            desc=filename,
            disable=not show_progress
        )

        with open(output_path, "wb") as f:
            for chunk in r.iter_content(chunk_size=chunk_size):
                if chunk:
                    f.write(chunk)
                    progress.update(len(chunk))

        progress.close()
    
    return output_path