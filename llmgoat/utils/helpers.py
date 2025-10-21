"""
This module contains multiple helper function used throughout the codebase.
"""
import os
import stat
import shutil
import requests
import hashlib
from tqdm import tqdm
from .definitions import LLMGOAT_FOLDER, DEFAULT_MODELS_FOLDER, DEFAULT_CACHE_FOLDER, DEFAULT_CHALLENGES_FOLDER, LLMGOAT_VERBOSE
from .logger import goatlog

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

def create_read_only_file(filename: str, content: str) -> None:
    """
    Creates a read-only file with the specified content if it doesn't already exist.
    """
    if not file_exists(filename):
        # Create and write content to the file
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(content)
        
        # Make the file read-only
        os.chmod(filename, stat.S_IREAD)
        goatlog.info(f"Created read-only file: {filename}")
    else:
        goatlog.info(f"File already exists: {filename}")


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

    # Create the models, cache and challenges folders within the above one if missing
    create_folder_if_missing(DEFAULT_MODELS_FOLDER)
    create_folder_if_missing(DEFAULT_CACHE_FOLDER)
    create_folder_if_missing(DEFAULT_CHALLENGES_FOLDER)


def set_env_if_empty(env_var, env_value):
    """Set an ENV variable if empty, otherwise don't change it (ENV vars take precedence!)"""
    os.environ[env_var] = os.environ.get(env_var, env_value)


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


def is_running_in_container() -> bool:
    """
    Detect if the current process is running inside a container.
    Works for Docker, Podman, Kubernetes, etc.
    """
    try:
        # Common indicator: existence of /.dockerenv file
        if os.path.exists("/.dockerenv"):
            return True

        # Check cgroup info for container-specific markers
        with open("/proc/1/cgroup", "rt") as f:
            content = f.read()
            if any(keyword in content for keyword in ("docker", "kubepods", "containerd", "podman")):
                return True
    except Exception:
        pass

    return False


def is_verbose_mode():
    """Check whether verbose mode is enabled (environment takes precedence)."""
    verbose_env_value = os.environ.get(LLMGOAT_VERBOSE, "0")
    return verbose_env_value == "1"


def challenge_response(response, solved, prompt=None):
    """
    Construct a JSON-safe dictionary for all goat challenges.
    Includes debug_prompt only if verbose mode is enabled.
    """
    data = {
        "response": response,
        "solved": solved,
    }

    if is_verbose_mode() and prompt:
        data["debug_prompt"] = prompt

    return data


def disclaimer():
    """
    Print a big visual disclaimer warning the user that this app is intentionally vulnerable.
    """
    RED = "\033[91m"
    YELLOW = "\033[93m"
    RESET = "\033[0m"
    BOLD = "\033[1m"

    message = f"""
{RED}{'=' * 90}
{BOLD}{' ' * 26}⚠️ WARNING: RUNNING ON HOST SYSTEM! ⚠️{RESET}{RED}
{'=' * 90}{RESET}

{YELLOW}{BOLD}This application is intentionally vulnerable and should not be run on a host system!
It is designed for testing and educational use only. 
Run it inside a secure, disposable container.{RESET}

{RED}You are solely responsible for any damage, data loss or security issues
caused by running this software on your machine.{RESET}

{RED}{'=' * 90}{RESET}
"""

    print(message)
    input(f"{BOLD}Press Enter to acknowledge and continue...{RESET}\n")
