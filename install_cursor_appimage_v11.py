#!/usr/bin/env python3
import os
import sys
import subprocess
import requests
import shutil
import tempfile
import hashlib
import time
from pathlib import Path

APP_NAME = "Cursor"

# Always use user install for this version
USER_INSTALL = True
INSTALL_DIR = Path.home() / "Applications" / "cursor"

BIN_PATH = INSTALL_DIR / "cursor.AppImage"
ICON_PATH = INSTALL_DIR / "cursor.png"
VERSION_FILE = INSTALL_DIR / ".version"
DESKTOP_FILE = Path.home() / ".local/share/applications/cursor.desktop"

API_URL = "https://www.cursor.com/api/download?platform=linux-x64&releaseTrack=stable"
DEPENDENCIES = ["fuse-libs", "curl", "jq", "desktop-file-utils"]

def log(msg): print(f"\033[1;32m[INFO]\033[0m {msg}")
def err(msg): sys.stderr.write(f"\033[1;31m[ERROR]\033[0m {msg}\n") or sys.exit(1)
def run(cmd): subprocess.run(cmd, check=True)

def install_deps():
    if USER_INSTALL:
        log("User install mode: skipping dependency installation.")
        return
    log("Checking dependencies...")
    missing = []
    for dep in DEPENDENCIES:
        if subprocess.run(["rpm", "-q", dep], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL).returncode != 0:
            missing.append(dep)
    if not missing:
        log("All dependencies already installed.")
        return
    log(f"Installing missing dependencies: {', '.join(missing)}")
    run(["dnf", "install", "-y"] + missing)

def set_libgl_env():
    log("Ensuring LIBGL_ALWAYS_SOFTWARE=1 is set...")
    env_file = Path.home() / ".profile" if USER_INSTALL else Path("/etc/environment")
    line = "LIBGL_ALWAYS_SOFTWARE=1\n"
    if env_file.exists() and "LIBGL_ALWAYS_SOFTWARE" in env_file.read_text():
        return
    with open(env_file, "a") as f: f.write(line)
    log(f"Added LIBGL_ALWAYS_SOFTWARE=1 to {env_file}")

def fetch_download_info():
    log("Fetching latest AppImage info...")
    r = requests.get(API_URL, headers={"Accept": "application/json"}, timeout=15)
    r.raise_for_status()
    data = r.json()
    dl = data.get("downloadUrl")
    ver = data.get("version") or "unknown"
    sha256 = data.get("sha256")
    if not dl: err("downloadUrl not found in API response.")
    return dl, ver, sha256

def sha256sum(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()

def download_with_progress(url, dest_path, desc="Downloading"):
    r = requests.get(url, stream=True, timeout=60)
    r.raise_for_status()
    total = int(r.headers.get("content-length", 0))
    downloaded = 0
    chunk_size = 8192
    with open(dest_path, "wb") as f:
        for chunk in r.iter_content(chunk_size=chunk_size):
            if chunk:
                f.write(chunk)
                downloaded += len(chunk)
                if total > 0:
                    percent = downloaded * 100 // total
                    print(f"\r{desc}: {percent}%", end="", flush=True)
    print("")

def remote_sha256(url):
    log("Calculating remote checksum...")
    with tempfile.NamedTemporaryFile(delete=False) as tmp:
        tmp_path = Path(tmp.name)
    download_with_progress(url, tmp_path, desc="Downloading for checksum")
    checksum = sha256sum(tmp_path)
    tmp_path.unlink(missing_ok=True)
    return checksum

def is_update_needed(url, latest_version, expected_sha256=None):
    if BIN_PATH.exists():
        local_hash = sha256sum(BIN_PATH)
        if not expected_sha256:
            expected_sha256 = remote_sha256(url)
        if local_hash == expected_sha256:
            VERSION_FILE.write_text(latest_version)
            return False
    return True

def close_other_instances():
    log("Closing any running instances of Cursor...")
    subprocess.run(["pkill", "-f", str(BIN_PATH)], check=False)
    subprocess.run(["pkill", "-f", "cursor"], check=False)
    time.sleep(1)

def download_and_install(url, version):
    with tempfile.TemporaryDirectory() as tmp:
        tmpfile = Path(tmp) / "cursor.AppImage"
        log(f"Downloading version {version} from: {url}")
        download_with_progress(url, tmpfile, desc="Downloading AppImage")
        INSTALL_DIR.mkdir(parents=True, exist_ok=True)
        shutil.move(str(tmpfile), BIN_PATH)
        os.chmod(BIN_PATH, 0o755)
        VERSION_FILE.write_text(version)

def install_icon():
    try:
        url = "https://raw.githubusercontent.com/getcursor/cursor/main/resources/icon.png"
        log("Downloading icon...")
        download_with_progress(url, ICON_PATH, desc="Downloading icon")
    except Exception:
        log("Warning: Could not download icon.")

def create_desktop_entry():
    log("Creating desktop entry...")
    exec_line = f"{BIN_PATH} --no-sandbox --disable-gpu"
    DESKTOP_FILE.parent.mkdir(parents=True, exist_ok=True)
    DESKTOP_FILE.write_text(f"""[Desktop Entry]
Name={APP_NAME}
Exec={exec_line}
Icon={ICON_PATH}
Type=Application
Categories=Development;IDE;
""")

def launch():
    log(f"Launching {APP_NAME} with GPU disabled...")
    subprocess.Popen([str(BIN_PATH), "--no-sandbox", "--disable-gpu"])

if __name__ == "__main__":
    install_deps()
    set_libgl_env()
    close_other_instances()
    url, latest_version, expected_sha256 = fetch_download_info()
    if not is_update_needed(url, latest_version, expected_sha256):
        log(f"Already up to date (version {latest_version}).")
        launch()
        sys.exit(0)
    download_and_install(url, latest_version)
    install_icon()
    create_desktop_entry()
    log(f"Installation of version {latest_version} complete.")
    launch()
