import urllib.request
import zipfile
import os
import sys

URL = "https://zenodo.org/api/records/2867216/files/26_29_09_2017_KCL.zip/content"
DEST_DIR = "raw_data/mdvr_kcl"
ZIP_PATH = os.path.join(DEST_DIR, "MDVR_KCL.zip")

os.makedirs(DEST_DIR, exist_ok=True)

def reporthook(count, block_size, total_size):
    if count % 2000 == 0 or (count * block_size >= total_size):
        percent = min(100, int(count * block_size * 100 / total_size))
        mb = int(count * block_size / (1024 * 1024))
        total_mb = int(total_size / (1024 * 1024))
        print(f"Downloading MDVR-KCL: {mb}MB / {total_mb}MB ({percent}%)", flush=True)

print(">>> Starting direct download from Zenodo...", flush=True)
urllib.request.urlretrieve(URL, ZIP_PATH, reporthook)
print(">>> Download complete! Unzipping dataset...", flush=True)

with zipfile.ZipFile(ZIP_PATH, 'r') as zip_ref:
    zip_ref.extractall(DEST_DIR)

print(">>> Extraction complete!", flush=True)
print(">>> Folder contents:", os.listdir(DEST_DIR), flush=True)
