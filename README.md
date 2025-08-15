# Cursor AppImage Installer

A robust, secure, and user-friendly installer for [Cursor IDE](https://cursor.com) on Linux systems. This installer automatically downloads, verifies, and installs the latest version of Cursor as an AppImage with proper desktop integration.

## 🚀 Features

- **Automatic Updates**: Checks for and installs the latest version
- **Integrity Verification**: SHA256 checksum validation for security
- **GPU Compatibility**: Automatic configuration for better graphics support
- **Desktop Integration**: Creates proper desktop entries and icons
- **User-Friendly**: Colored output and progress indicators
- **Error Handling**: Comprehensive error handling and recovery
- **Dependency Management**: Automatic installation of required Python packages
- **Security**: User-level installation (no root required)

## 📋 Requirements

- **OS**: Linux (x86_64/amd64 architecture)
- **Python**: 3.6 or higher
- **Internet**: Active internet connection for download
- **Disk Space**: ~200MB for the AppImage

## 🛠️ Installation

### Quick Install

```bash
# Download and run the installer
curl -sSL https://raw.githubusercontent.com/swipswaps/cursor-appimage-installer/main/install_cursor_appimage_v15.py | python3 -
```

### Manual Install

```bash
# Clone the repository
git clone https://github.com/swipswaps/cursor-appimage-installer.git
cd cursor-appimage-installer

# Run the installer
python3 install_cursor_appimage_v15.py
```

## 📖 How It Works

### 1. System Requirements Check
The installer first verifies your system meets the minimum requirements:
- Python version (3.6+)
- Linux operating system
- x86_64 architecture

### 2. Dependency Management
Automatically installs required Python packages:
- `requests`: For HTTP downloads
- `Pillow`: For icon creation (fallback)

### 3. GPU Compatibility Configuration
Sets `LIBGL_ALWAYS_SOFTWARE=1` in your `~/.profile` to ensure compatibility with various graphics drivers and virtual environments.

### 4. API Communication
Fetches the latest version information from Cursor's official API:
```json
{
  "downloadUrl": "https://downloads.cursor.com/.../Cursor-1.4.5-x86_64.AppImage",
  "version": "1.4.5",
  "commitSha": "af58d92614edb1f72bdd756615d131bf8dfa5299"
}
```

### 5. Download and Verification
- Downloads the AppImage with progress indication
- Calculates SHA256 checksum for integrity verification
- Compares with expected checksum (when available)

### 6. Installation
- Creates installation directory: `~/Applications/cursor/`
- Installs the AppImage with proper permissions (755)
- Records version information for future updates

### 7. Icon Installation
Attempts to download the official Cursor icon from multiple sources:
1. `https://www.cursor.com/assets/images/logo.png`
2. `https://www.cursor.com/favicon.png`
3. `https://raw.githubusercontent.com/getcursor/cursor/main/resources/icon.png`

If all downloads fail, creates a custom placeholder icon.

### 8. Desktop Integration
Creates a desktop entry at `~/.local/share/applications/cursor.desktop` with:
- Proper application metadata
- MIME type associations
- Desktop categories
- Launch flags for compatibility

### 9. Launch Configuration
Launches Cursor with compatibility flags:
- `--no-sandbox`: Disables Chrome sandbox (common on Linux)
- `--disable-gpu`: Uses software rendering for stability

## 🔧 Technical Details

### File Structure
```
~/Applications/cursor/
├── cursor.AppImage    # Main executable
├── cursor.png         # Application icon
└── .version          # Version tracking file

~/.local/share/applications/
└── cursor.desktop    # Desktop entry
```

### Security Features
- **User-level installation**: No root privileges required
- **Checksum verification**: SHA256 integrity checking
- **Safe process termination**: Uses `pkill` with user filter
- **Temporary file handling**: Secure cleanup of download files
- **Error isolation**: Comprehensive exception handling

### Compatibility Flags
The installer uses several flags to ensure compatibility:
- `--no-sandbox`: Required on many Linux distributions
- `--disable-gpu`: Prevents graphics driver issues
- `LIBGL_ALWAYS_SOFTWARE=1`: Forces software rendering

## 🐛 Troubleshooting

### Common Issues

#### 1. Permission Denied
```bash
# Make sure the script is executable
chmod +x install_cursor_appimage_v15.py
```

#### 2. Python Dependencies
```bash
# Install dependencies manually if needed
pip3 install --user requests Pillow
```

#### 3. Network Issues
```bash
# Check internet connectivity
curl -I https://www.cursor.com/api/download?platform=linux-x64&releaseTrack=stable
```

#### 4. Graphics Issues
```bash
# Apply GPU compatibility fix manually
echo 'export LIBGL_ALWAYS_SOFTWARE=1' >> ~/.profile
source ~/.profile
```

#### 5. Desktop Entry Not Working
```bash
# Update desktop database
update-desktop-database ~/.local/share/applications
```

### Debug Mode
For detailed debugging, you can modify the script to enable verbose logging:
```python
# Add this line after the imports
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 🔄 Updating

The installer automatically checks for updates. To force a reinstall:

```bash
# Remove version file to force update check
rm ~/Applications/cursor/.version

# Run installer again
python3 install_cursor_appimage_v15.py
```

## 🗑️ Uninstallation

To completely remove Cursor:

```bash
# Remove application files
rm -rf ~/Applications/cursor

# Remove desktop entry
rm ~/.local/share/applications/cursor.desktop

# Update desktop database
update-desktop-database ~/.local/share/applications

# Remove GPU compatibility setting (optional)
# Edit ~/.profile and remove the LIBGL_ALWAYS_SOFTWARE=1 line
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

### Development Setup
```bash
git clone https://github.com/swipswaps/cursor-appimage-installer.git
cd cursor-appimage-installer
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [Cursor Team](https://cursor.com) for the excellent IDE
- [AppImage](https://appimage.org/) for the portable format
- Linux community for compatibility insights

## 📞 Support

If you encounter any issues:

1. Check the [troubleshooting section](#-troubleshooting)
2. Search [existing issues](https://github.com/swipswaps/cursor-appimage-installer/issues)
3. Create a new issue with detailed information

## 🔗 Related Links

- [Cursor Official Website](https://cursor.com)
- [Cursor GitHub Repository](https://github.com/getcursor/cursor)
- [AppImage Documentation](https://docs.appimage.org/)
- [Linux Desktop Entry Specification](https://specifications.freedesktop.org/desktop-entry-spec/desktop-entry-spec-latest.html)

---

**Note**: This installer is not officially affiliated with Cursor. It's a community-maintained tool to simplify the installation process on Linux systems.
