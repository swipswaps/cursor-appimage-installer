# Installation Guide

This guide provides detailed instructions for installing Cursor IDE using the AppImage installer.

## Quick Start

### One-liner Installation
```bash
curl -sSL https://raw.githubusercontent.com/swipswaps/cursor-appimage-installer/main/install_cursor_appimage_v15.py | python3 -
```

### Manual Installation
```bash
# Clone the repository
git clone https://github.com/swipswaps/cursor-appimage-installer.git
cd cursor-appimage-installer

# Run the installer
python3 install_cursor_appimage_v15.py
```

## What the Installer Does

### 1. System Verification
The installer first checks your system:
- ✅ Python version (3.6+)
- ✅ Linux operating system
- ✅ x86_64 architecture
- ⚠️ Warns if architecture might not be supported

### 2. Dependency Installation
Automatically installs required Python packages:
- `requests`: For downloading files
- `Pillow`: For creating placeholder icons

### 3. GPU Compatibility Setup
Adds `LIBGL_ALWAYS_SOFTWARE=1` to your `~/.profile`:
```bash
# Cursor IDE GPU compatibility fix
export LIBGL_ALWAYS_SOFTWARE=1
```

This ensures compatibility with:
- Virtual machines
- Older graphics drivers
- Wayland sessions
- Remote desktop environments

### 4. API Communication
Fetches the latest version from Cursor's API:
```json
{
  "downloadUrl": "https://downloads.cursor.com/.../Cursor-1.4.5-x86_64.AppImage",
  "version": "1.4.5",
  "commitSha": "af58d92614edb1f72bdd756615d131bf8dfa5299"
}
```

### 5. Download and Verification
- Downloads the AppImage (~200MB)
- Shows progress bar
- Calculates SHA256 checksum
- Verifies file integrity

### 6. Installation
Creates the following structure:
```
~/Applications/cursor/
├── cursor.AppImage    # Main executable (755 permissions)
├── cursor.png         # Application icon
└── .version          # Version tracking file
```

### 7. Desktop Integration
Creates a desktop entry at `~/.local/share/applications/cursor.desktop`:
```ini
[Desktop Entry]
Name=Cursor
Comment=AI-first code editor
Exec=/home/user/Applications/cursor/cursor.AppImage --no-sandbox --disable-gpu
Icon=/home/user/Applications/cursor/cursor.png
Type=Application
Categories=Development;IDE;TextEditor;
Keywords=code;editor;IDE;AI;
StartupWMClass=cursor
Terminal=false
MimeType=text/plain;inode/directory;application/x-code-workspace;
```

### 8. Launch Configuration
Launches Cursor with compatibility flags:
- `--no-sandbox`: Disables Chrome sandbox (required on many Linux distros)
- `--disable-gpu`: Uses software rendering for stability

## File Locations

### Application Files
- **Executable**: `~/Applications/cursor/cursor.AppImage`
- **Icon**: `~/Applications/cursor/cursor.png`
- **Version File**: `~/Applications/cursor/.version`

### Desktop Integration
- **Desktop Entry**: `~/.local/share/applications/cursor.desktop`
- **Environment Variable**: `~/.profile` (LIBGL_ALWAYS_SOFTWARE=1)

## Troubleshooting

### Common Issues

#### 1. Permission Denied
```bash
# Make the script executable
chmod +x install_cursor_appimage_v15.py
```

#### 2. Python Not Found
```bash
# Install Python 3
sudo dnf install python3  # Fedora/RHEL
sudo apt install python3  # Ubuntu/Debian
```

#### 3. Network Issues
```bash
# Test connectivity
curl -I https://www.cursor.com/api/download?platform=linux-x64&releaseTrack=stable
```

#### 4. Graphics Issues
```bash
# Apply GPU fix manually
echo 'export LIBGL_ALWAYS_SOFTWARE=1' >> ~/.profile
source ~/.profile
```

#### 5. Desktop Entry Not Working
```bash
# Update desktop database
update-desktop-database ~/.local/share/applications
```

### Debug Mode
For detailed debugging, add this to the script:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Updating

The installer automatically checks for updates. To force a reinstall:

```bash
# Remove version file
rm ~/Applications/cursor/.version

# Run installer again
python3 install_cursor_appimage_v15.py
```

## Uninstallation

To completely remove Cursor:

```bash
# Remove application files
rm -rf ~/Applications/cursor

# Remove desktop entry
rm ~/.local/share/applications/cursor.desktop

# Update desktop database
update-desktop-database ~/.local/share/applications

# Remove GPU setting (optional)
# Edit ~/.profile and remove the LIBGL_ALWAYS_SOFTWARE=1 line
```

## Security Features

- **User-level installation**: No root privileges required
- **Checksum verification**: SHA256 integrity checking
- **Safe process termination**: Uses `pkill` with user filter
- **Temporary file handling**: Secure cleanup of download files
- **Error isolation**: Comprehensive exception handling

## Compatibility

### Supported Systems
- **OS**: Linux (x86_64/amd64)
- **Python**: 3.6+
- **Desktop Environments**: GNOME, KDE, XFCE, etc.

### Graphics Compatibility
- **OpenGL**: Software rendering via LIBGL_ALWAYS_SOFTWARE=1
- **Wayland**: Compatible with software rendering
- **X11**: Full compatibility
- **Virtual Machines**: Optimized for VM environments

## Performance Notes

- **First Launch**: May take longer due to AppImage extraction
- **Subsequent Launches**: Faster as files are cached
- **Memory Usage**: ~200-500MB depending on workspace size
- **Disk Space**: ~200MB for AppImage + workspace files

## Support

If you encounter issues:

1. Check the troubleshooting section above
2. Run the test suite: `python3 test_installer.py`
3. Check system logs: `journalctl --user -f`
4. Create an issue on GitHub with detailed information

## Advanced Usage

### Custom Installation Directory
Edit the script to change the installation path:
```python
INSTALL_DIR = Path.home() / "custom" / "path" / "cursor"
```

### Custom Launch Flags
Modify the desktop entry to add custom flags:
```bash
# Edit the desktop file
nano ~/.local/share/applications/cursor.desktop

# Add custom flags to the Exec line
Exec=/home/user/Applications/cursor/cursor.AppImage --no-sandbox --disable-gpu --custom-flag
```

### Silent Installation
For automated installations, you can modify the script to suppress output:
```python
# Redirect output to /dev/null
import os
import sys
sys.stdout = open(os.devnull, 'w')
sys.stderr = open(os.devnull, 'w')
```
