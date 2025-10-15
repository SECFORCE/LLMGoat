import os
import requests
import hashlib
from tqdm import tqdm

def banner():
    print("""
      ░█░░░█░░░█▄█
      ░█░░░█░░░█░█
      ░▀▀▀░▀▀▀░▀░▀
    ░█▀▀░█▀█░█▀█░▀█▀
    ░█░█░█░█░█▀█░░█░
    ░▀▀▀░▀▀▀░▀░▀░░▀░

""")

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