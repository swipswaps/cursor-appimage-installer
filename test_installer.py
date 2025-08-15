#!/usr/bin/env python3
"""
Test script for Cursor AppImage Installer
This script tests the installer functionality without actually installing.
"""

import sys
import os
import tempfile
import json
from pathlib import Path

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_api_connection():
    """Test API connection and response parsing"""
    print("Testing API connection...")
    
    try:
        import requests
        from install_cursor_appimage_v15 import fetch_download_info
        
        url, version, checksum = fetch_download_info()
        print(f"✓ API connection successful")
        print(f"  Download URL: {url}")
        print(f"  Version: {version}")
        print(f"  Checksum: {checksum}")
        return True
    except Exception as e:
        print(f"✗ API connection failed: {e}")
        return False

def test_dependency_check():
    """Test dependency checking"""
    print("\nTesting dependency checking...")
    
    try:
        from install_cursor_appimage_v15 import install_deps
        install_deps()
        print("✓ Dependency check successful")
        return True
    except Exception as e:
        print(f"✗ Dependency check failed: {e}")
        return False

def test_system_requirements():
    """Test system requirements checking"""
    print("\nTesting system requirements...")
    
    try:
        from install_cursor_appimage_v15 import check_system_requirements
        check_system_requirements()
        print("✓ System requirements check successful")
        return True
    except Exception as e:
        print(f"✗ System requirements check failed: {e}")
        return False

def test_sha256_function():
    """Test SHA256 calculation"""
    print("\nTesting SHA256 calculation...")
    
    try:
        from install_cursor_appimage_v15 import sha256sum
        
        # Create a test file
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            tmp.write(b"test content")
            tmp_path = Path(tmp.name)
        
        # Calculate checksum
        checksum = sha256sum(tmp_path)
        expected = "6ae8a75555209fd6c44157c0aed8016e763ff435a19cf186f76863140143ff72"
        
        if checksum == expected:
            print("✓ SHA256 calculation successful")
            result = True
        else:
            print(f"✗ SHA256 calculation failed: expected {expected}, got {checksum}")
            result = False
        
        # Cleanup
        tmp_path.unlink()
        return result
    except Exception as e:
        print(f"✗ SHA256 calculation failed: {e}")
        return False

def test_download_function():
    """Test download functionality with a small file"""
    print("\nTesting download functionality...")
    
    try:
        from install_cursor_appimage_v15 import download_with_progress
        
        # Download a small test file
        test_url = "https://httpbin.org/bytes/1024"
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            tmp_path = Path(tmp.name)
        
        success = download_with_progress(test_url, tmp_path, "Test download", fatal=False)
        
        if success and tmp_path.exists() and tmp_path.stat().st_size == 1024:
            print("✓ Download functionality successful")
            result = True
        else:
            print("✗ Download functionality failed")
            result = False
        
        # Cleanup
        tmp_path.unlink()
        return result
    except Exception as e:
        print(f"✗ Download functionality failed: {e}")
        return False

def main():
    """Run all tests"""
    print("Cursor AppImage Installer - Test Suite")
    print("=" * 50)
    
    tests = [
        test_system_requirements,
        test_dependency_check,
        test_api_connection,
        test_sha256_function,
        test_download_function,
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"✗ Test {test.__name__} crashed: {e}")
    
    print("\n" + "=" * 50)
    print(f"Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("✓ All tests passed! The installer should work correctly.")
        return 0
    else:
        print("✗ Some tests failed. Please check the issues above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
