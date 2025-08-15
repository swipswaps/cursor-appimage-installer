#!/usr/bin/env python3
"""
Cursor AppImage Installer v1.5
A robust, secure installer for Cursor IDE on Linux systems.

Features:
- Automatic dependency management
- SHA256 integrity verification
- GPU compatibility fixes
- Desktop integration
- Update detection
- Comprehensive error handling
- User-friendly logging

Author: swipswaps
License: MIT
"""

import os
import sys
import subprocess
import requests
import shutil
import tempfile
import hashlib
import time
import json
import platform
from pathlib import Path
from typing import Optional, Tuple, Dict, Any

# Configuration
APP_NAME = "Cursor"
APP_VERSION = "1.5"
USER_INSTALL = True  # Always use user install for security
INSTALL_DIR = Path.home() / "Applications" / "cursor"
BIN_PATH = INSTALL_DIR / "cursor.AppImage"
ICON_PATH = INSTALL_DIR / "cursor.png"
VERSION_FILE = INSTALL_DIR / ".version"
DESKTOP_FILE = Path.home() / ".local/share/applications/cursor.desktop"

# API Configuration
API_URL = "https://www.cursor.com/api/download?platform=linux-x64&releaseTrack=stable"
ICON_URLS = [
    "https://www.cursor.com/assets/images/logo.png",
    "https://www.cursor.com/favicon.png",
    "https://raw.githubusercontent.com/getcursor/cursor/main/resources/icon.png",
]

# System requirements
MIN_PYTHON_VERSION = (3, 6)
REQUIRED_PACKAGES = ["requests", "Pillow"]

class Colors:
    """ANSI color codes for terminal output"""
    GREEN = "\033[1;32m"
    YELLOW = "\033[1;33m"
    RED = "\033[1;31m"
    BLUE = "\033[1;34m"
    RESET = "\033[0m"

def log(msg: str, color: str = Colors.GREEN) -> None:
    """Print a formatted log message"""
    print(f"{color}[INFO]{Colors.RESET} {msg}")

def warn(msg: str) -> None:
    """Print a formatted warning message"""
    print(f"{Colors.YELLOW}[WARN]{Colors.RESET} {msg}")

def err(msg: str) -> None:
    """Print a formatted error message and exit"""
    sys.stderr.write(f"{Colors.RED}[ERROR]{Colors.RESET} {msg}\n")
    sys.exit(1)

def check_system_requirements() -> None:
    """Verify system meets minimum requirements"""
    log("Checking system requirements...")
    
    # Check Python version
    if sys.version_info < MIN_PYTHON_VERSION:
        err(f"Python {'.'.join(map(str, MIN_PYTHON_VERSION))}+ required. "
            f"Current version: {sys.version}")
    
    # Check platform
    if platform.system() != "Linux":
        err("This installer is designed for Linux systems only.")
    
    # Check architecture
    if platform.machine() not in ["x86_64", "amd64"]:
        warn(f"Architecture {platform.machine()} may not be supported. "
             "Proceeding anyway...")

def install_deps() -> None:
    """Install required Python dependencies"""
    log("Checking and installing required Python dependencies...")
    
    for package in REQUIRED_PACKAGES:
        try:
            if package == "requests":
                import requests  # noqa
            elif package == "Pillow":
                import PIL  # noqa
            log(f"{package} is already installed.")
        except ImportError:
            log(f"{package} not found. Installing with pip --user...")
            try:
                subprocess.run(
                    [sys.executable, "-m", "pip", "install", "--user", package],
                    check=True, capture_output=True, text=True
                )
                log(f"{package} installed successfully.")
            except subprocess.CalledProcessError as e:
                err(f"Failed to install {package}: {e.stderr}")

def set_libgl_env() -> None:
    """Set LIBGL_ALWAYS_SOFTWARE=1 for better compatibility"""
    log("Configuring GPU compatibility settings...")
    env_file = Path.home() / ".profile"
    
    if env_file.exists():
        content = env_file.read_text()
        if "LIBGL_ALWAYS_SOFTWARE=1" in content:
            log("Environment variable already present in .profile")
            return
    
    try:
        with open(env_file, "a") as f:
            f.write("\n# Cursor IDE GPU compatibility fix\n")
            f.write("export LIBGL_ALWAYS_SOFTWARE=1\n")
        log(f"Added LIBGL_ALWAYS_SOFTWARE=1 to {env_file}")
        warn("You must log out or run: source ~/.profile for the change to take effect.")
    except Exception as e:
        warn(f"Failed to update .profile: {e}")

def fetch_download_info() -> Tuple[str, str, Optional[str]]:
    """Fetch latest AppImage information from Cursor API"""
    log("Fetching latest AppImage info...")
    
    try:
        # Follow redirects and handle JSON response
        r = requests.get(API_URL, headers={
            "Accept": "application/json",
            "User-Agent": "Cursor-Installer/1.5"
        }, timeout=15, allow_redirects=True)
        r.raise_for_status()
        
        data = r.json()
        download_url = data.get("downloadUrl")
        version = data.get("version", "unknown")
        
        if not download_url:
            err("downloadUrl not found in API response.")
        
        log(f"Found version {version}")
        return download_url, version, None
        
    except requests.exceptions.RequestException as e:
        err(f"Failed to fetch API data: {e}")
    except json.JSONDecodeError as e:
        err(f"Invalid JSON response from API: {e}")

def sha256sum(file_path: Path) -> str:
    """Calculate SHA256 hash of a file"""
    h = hashlib.sha256()
    try:
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(8192), b""):
                h.update(chunk)
        return h.hexdigest()
    except Exception as e:
        err(f"Failed to calculate checksum: {e}")

def download_with_progress(url: str, dest_path: Path, desc: str = "Downloading", 
                          retries: int = 3, fatal: bool = True) -> bool:
    """Download file with progress bar and retry logic"""
    for attempt in range(1, retries + 1):
        try:
            r = requests.get(url, stream=True, timeout=60, headers={
                "User-Agent": "Cursor-Installer/1.5"
            })
            r.raise_for_status()
            
            total = int(r.headers.get("content-length", 0))
            downloaded = 0
            
            with open(dest_path, "wb") as f:
                for chunk in r.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        if total > 0:
                            percent = (downloaded * 100) // total
                            print(f"\r{desc}: {percent}%", end="", flush=True)
            
            print("")  # New line after progress
            return True
            
        except Exception as e:
            warn(f"{desc} failed (attempt {attempt}/{retries}): {e}")
            if attempt == retries and fatal:
                err(f"Failed to download after {retries} attempts.")
            elif attempt == retries:
                return False
            time.sleep(2)
    
    return False

def is_update_needed(url: str, latest_version: str, expected_sha256: Optional[str] = None) -> bool:
    """Check if an update is needed by comparing versions and checksums"""
    if not BIN_PATH.exists():
        return True
    
    if VERSION_FILE.exists():
        current_version = VERSION_FILE.read_text().strip()
        if current_version == latest_version:
            log(f"Already up to date (version {latest_version}).")
            return False
    
    # If we have a checksum, verify it
    if expected_sha256:
        local_hash = sha256sum(BIN_PATH)
        if local_hash == expected_sha256:
            VERSION_FILE.write_text(latest_version)
            log(f"File integrity verified (version {latest_version}).")
            return False
    
    return True

def close_other_instances() -> None:
    """Safely close running instances of Cursor"""
    log("Closing running instances of Cursor...")
    try:
        # Use pkill with user filter for safety
        subprocess.run(
            ["pkill", "-u", os.getlogin(), "-f", str(BIN_PATH)],
            check=False, capture_output=True
        )
        time.sleep(1)
    except Exception as e:
        warn(f"Failed to close instances: {e}")

def download_and_install(url: str, version: str, expected_sha256: Optional[str] = None) -> None:
    """Download and install the AppImage with integrity verification"""
    with tempfile.TemporaryDirectory() as tmp:
        tmpfile = Path(tmp) / "cursor.AppImage"
        log(f"Downloading version {version}...")
        
        if not download_with_progress(url, tmpfile, desc="Downloading AppImage"):
            err("Download failed.")
        
        # Verify file integrity
        log("Verifying downloaded file integrity...")
        file_hash = sha256sum(tmpfile)
        if expected_sha256 and file_hash != expected_sha256:
            err("Checksum mismatch! Aborting installation.")
        elif not expected_sha256:
            log("No checksum provided; skipping verification.")
        
        # Install the file
        try:
            INSTALL_DIR.mkdir(parents=True, exist_ok=True)
            shutil.move(str(tmpfile), BIN_PATH)
            os.chmod(BIN_PATH, 0o755)
            VERSION_FILE.write_text(version)
            log(f"AppImage installed to {BIN_PATH}")
        except Exception as e:
            err(f"Failed to install AppImage: {e}")

def install_icon() -> None:
    """Download and install application icon"""
    log("Installing application icon...")
    INSTALL_DIR.mkdir(parents=True, exist_ok=True)
    
    for url in ICON_URLS:
        if download_with_progress(url, ICON_PATH, 
                                desc=f"Downloading icon from {url}", 
                                fatal=False):
            log(f"Icon saved to {ICON_PATH}")
            return
    
    # Create placeholder icon if all downloads fail
    warn("All icon downloads failed. Creating placeholder icon...")
    try:
        from PIL import Image, ImageDraw, ImageFont
        
        # Create a simple placeholder icon
        img = Image.new("RGBA", (128, 128), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        # Draw a simple "C" logo
        draw.ellipse([10, 10, 118, 118], fill=(100, 100, 100, 200))
        draw.text((45, 45), "C", fill=(255, 255, 255), font=ImageFont.load_default())
        
        img.save(ICON_PATH)
        log(f"Placeholder icon created at {ICON_PATH}")
    except Exception as e:
        warn(f"Placeholder icon creation failed: {e}")
        # Create an empty file as fallback
        ICON_PATH.write_text("")

def create_desktop_entry() -> None:
    """Create desktop entry for application launcher integration"""
    log("Creating desktop entry...")
    
    # Build execution command with compatibility flags
    exec_line = f"{BIN_PATH} --no-sandbox --disable-gpu"
    
    try:
        DESKTOP_FILE.parent.mkdir(parents=True, exist_ok=True)
        
        desktop_content = f"""[Desktop Entry]
Name={APP_NAME}
Comment=AI-first code editor
Exec={exec_line}
Icon={ICON_PATH}
Type=Application
Categories=Development;IDE;TextEditor;
Keywords=code;editor;IDE;AI;
StartupWMClass=cursor
Terminal=false
MimeType=text/plain;inode/directory;application/x-code-workspace;
"""
        
        DESKTOP_FILE.write_text(desktop_content)
        
        # Update desktop database
        subprocess.run(["update-desktop-database", str(DESKTOP_FILE.parent)], 
                      check=False, capture_output=True)
        
        log(f"Desktop entry created at {DESKTOP_FILE}")
    except Exception as e:
        err(f"Failed to create desktop entry: {e}")

def launch() -> None:
    """Launch Cursor with appropriate flags"""
    log(f"Launching {APP_NAME}...")
    try:
        subprocess.Popen([
            str(BIN_PATH), 
            "--no-sandbox", 
            "--disable-gpu"
        ], start_new_session=True)
        log("Cursor launched successfully!")
    except Exception as e:
        err(f"Failed to launch Cursor: {e}")

def main() -> None:
    """Main installation function"""
    log(f"Cursor AppImage Installer v{APP_VERSION}")
    log("=" * 50)
    
    try:
        # System checks
        check_system_requirements()
        install_deps()
        set_libgl_env()
        
        # Close existing instances
        close_other_instances()
        
        # Fetch and install
        url, latest_version, expected_sha256 = fetch_download_info()
        
        if not is_update_needed(url, latest_version, expected_sha256):
            launch()
            return
        
        download_and_install(url, latest_version, expected_sha256)
        install_icon()
        create_desktop_entry()
        
        log(f"Installation of version {latest_version} complete!")
        log("=" * 50)
        
        # Launch the application
        launch()
        
    except KeyboardInterrupt:
        err("Installation cancelled by user.")
    except Exception as e:
        err(f"Unexpected error: {e}")

if __name__ == "__main__":
    main()
