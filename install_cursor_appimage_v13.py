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

# Always use user install
USER_INSTALL = True
INSTALL_DIR = Path.home() / "Applications" / "cursor"

BIN_PATH = INSTALL_DIR / "cursor.AppImage"
ICON_PATH = INSTALL_DIR / "cursor.png"
VERSION_FILE = INSTALL_DIR / ".version"
DESKTOP_FILE = Path.home() / ".local/share/applications/cursor.desktop"

API_URL = "https://www.cursor.com/api/download?platform=linux-x64&releaseTrack=stable"
ICON_URL = "https://raw.githubusercontent.com/getcursor/cursor/main/resources/icon.png"

def log(msg):
    print(f"\033[1;32m[INFO]\033[0m {msg}")

def warn(msg):
    print(f"\033[1;33m[WARN]\033[0m {msg}")

def err(msg):
    sys.stderr.write(f"\033[1;31m[ERROR]\033[0m {msg}\n")
    sys.exit(1)

def install_deps():
    log("User install mode: skipping dependency installation.")

def set_libgl_env():
    log("Ensuring LIBGL_ALWAYS_SOFTWARE=1 is set...")
    env_file = Path.home() / ".profile"
    added = False
    if env_file.exists():
        content = env_file.read_text()
        if "LIBGL_ALWAYS_SOFTWARE" in content:
            log("Environment variable already present in .profile")
            return
    with open(env_file, "a") as f:
        f.write("\nLIBGL_ALWAYS_SOFTWARE=1\n")
    added = True
    if added:
        log(f"Added LIBGL_ALWAYS_SOFTWARE=1 to {env_file}")
        warn("You must log out or run: source ~/.profile for the change to take effect.")

def fetch_download_info():
    log("Fetching latest AppImage info...")
    try:
        r = requests.get(API_URL, headers={"Accept": "application/json"}, timeout=15)
        r.raise_for_status()
    except Exception as e:
        err(f"Failed to fetch API data: {e}")
    data = r.json()
    dl = data.get("downloadUrl")
    ver = data.get("version") or "unknown"
    sha256 = data.get("sha256")
    if not dl:
        err("downloadUrl not found in API response.")
    return dl, ver, sha256

def sha256sum(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()

def download_with_progress(url, dest_path, desc="Downloading", retries=3):
    for attempt in range(1, retries + 1):
        try:
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
            return
        except Exception as e:
            warn(f"Download failed (attempt {attempt}/{retries}): {e}")
            if attempt == retries:
                err(f"Failed to download after {retries} attempts.")
            time.sleep(2)

def remote_sha256(url):
    log("Calculating remote checksum (temporary download)...")
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
    log("Closing running instances of Cursor owned by this user...")
    subprocess.run(
        ["pkill", "-u", os.getlogin(), "-f", str(BIN_PATH)],
        check=False
    )
    time.sleep(1)

def download_and_install(url, version, expected_sha256=None):
    with tempfile.TemporaryDirectory() as tmp:
        tmpfile = Path(tmp) / "cursor.AppImage"
        log(f"Downloading version {version} from: {url}")
        download_with_progress(url, tmpfile, desc="Downloading AppImage")

        # Verify checksum before install
        log("Verifying downloaded file integrity...")
        file_hash = sha256sum(tmpfile)
        if expected_sha256 and file_hash != expected_sha256:
            err("Checksum mismatch! Aborting installation.")
        elif not expected_sha256:
            log("No checksum from API; skipping verification.")

        INSTALL_DIR.mkdir(parents=True, exist_ok=True)
        shutil.move(str(tmpfile), BIN_PATH)
        os.chmod(BIN_PATH, 0o755)
        VERSION_FILE.write_text(version)

def install_icon():
    try:
        log("Downloading icon...")
        download_with_progress(ICON_URL, ICON_PATH, desc="Downloading icon")
    except Exception:
        warn("Could not download icon; proceeding without it.")

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
    subprocess.run(["update-desktop-database", str(DESKTOP_FILE.parent)], check=False)

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
    download_and_install(url, latest_version, expected_sha256)
    install_icon()
    create_desktop_entry()
    log(f"Installation of version {latest_version} complete.")
    launch()
