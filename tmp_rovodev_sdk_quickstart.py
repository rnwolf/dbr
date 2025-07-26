#!/usr/bin/env python3
"""
SDK Quick Start Script
Simplified workflow for SDK installation and testing with UV
"""

import subprocess
import sys
import os
from pathlib import Path

def run_command(cmd, description, cwd=None, check=True):
    """Run a command and handle errors"""
    print(f"🔍 {description}")
    print(f"   Command: {' '.join(cmd) if isinstance(cmd, list) else cmd}")
    
    try:
        if isinstance(cmd, str):
            result = subprocess.run(cmd, shell=True, cwd=cwd, check=check, capture_output=True, text=True)
        else:
            result = subprocess.run(cmd, cwd=cwd, check=check, capture_output=True, text=True)
        
        if result.stdout:
            print(f"   Output: {result.stdout.strip()}")
        
        print("   ✅ Success")
        return True
    except subprocess.CalledProcessError as e:
        print(f"   ❌ Failed: {e}")
        if e.stdout:
            print(f"   Stdout: {e.stdout}")
        if e.stderr:
            print(f"   Stderr: {e.stderr}")
        return False
    except Exception as e:
        print(f"   💥 Error: {e}")
        return False

def check_prerequisites():
    """Check if required tools are available"""
    print("🔍 Checking prerequisites...")
    
    # Check UV
    uv_available = run_command(["uv", "--version"], "Check UV availability", check=False)
    
    # Check directories
    sdk_dir = Path("dbrsdk-python")
    frontend_dir = Path("dbr_mvp/frontend")
    
    sdk_exists = sdk_dir.exists()
    frontend_exists = frontend_dir.exists()
    
    print(f"   SDK directory: {'✅' if sdk_exists else '❌'} {sdk_dir}")
    print(f"   Frontend directory: {'✅' if frontend_exists else '❌'} {frontend_dir}")
    
    return uv_available and sdk_exists and frontend_exists

def install_sdk():
    """Install SDK in frontend environment"""
    print("\n📦 Installing SDK in frontend environment...")
    
    frontend_dir = Path("dbr_mvp/frontend")
    sdk_path = "../../dbrsdk-python"
    
    # Try direct UV add first
    success = run_command(
        ["uv", "add", sdk_path],
        "Install SDK with UV add",
        cwd=frontend_dir,
        check=False
    )
    
    if not success:
        print("   Trying alternative installation method...")
        success = run_command(
            ["uv", "pip", "install", "-e", sdk_path],
            "Install SDK with UV pip",
            cwd=frontend_dir,
            check=False
        )
    
    return success

def verify_installation():
    """Verify SDK installation"""
    print("\n🔍 Verifying SDK installation...")
    
    frontend_dir = Path("dbr_mvp/frontend")
    
    # Test import
    test_cmd = ["uv", "run", "python", "-c", "import dbrsdk; print(f'SDK version: {dbrsdk.__version__}')"]
    
    return run_command(
        test_cmd,
        "Test SDK import",
        cwd=frontend_dir,
        check=False
    )

def copy_test_files():
    """Copy test files to frontend directory for easier execution"""
    print("\n📋 Copying test files to frontend directory...")
    
    test_files = [
        "tmp_rovodev_sdk_test_basic.py",
        "tmp_rovodev_sdk_test_auth.py", 
        "tmp_rovodev_sdk_test_org.py",
        "tmp_rovodev_run_all_sdk_tests.py"
    ]
    
    frontend_dir = Path("dbr_mvp/frontend")
    
    for test_file in test_files:
        src = Path(test_file)
        dst = frontend_dir / test_file
        
        if src.exists():
            try:
                import shutil
                shutil.copy2(src, dst)
                print(f"   ✅ Copied {test_file}")
            except Exception as e:
                print(f"   ❌ Failed to copy {test_file}: {e}")
                return False
        else:
            print(f"   ⚠️  Test file not found: {test_file}")
    
    return True

def run_tests():
    """Run the test suite"""
    print("\n🧪 Running SDK tests...")
    
    frontend_dir = Path("dbr_mvp/frontend")
    test_runner = "tmp_rovodev_run_all_sdk_tests.py"
    
    if not (frontend_dir / test_runner).exists():
        print(f"   ❌ Test runner not found: {test_runner}")
        return False
    
    return run_command(
        ["uv", "run", "python", test_runner],
        "Run complete test suite",
        cwd=frontend_dir,
        check=False
    )

def main():
    """Main workflow"""
    print("🚀 DBR SDK Quick Start")
    print("=" * 50)
    print("This script will:")
    print("1. Check prerequisites")
    print("2. Install SDK in frontend environment")
    print("3. Verify installation")
    print("4. Copy test files")
    print("5. Run tests")
    print("=" * 50)
    
    # Step 1: Prerequisites
    if not check_prerequisites():
        print("\n❌ Prerequisites not met. Please check:")
        print("   - UV is installed and available")
        print("   - dbrsdk-python directory exists")
        print("   - dbr_mvp/frontend directory exists")
        return False
    
    # Step 2: Install SDK
    if not install_sdk():
        print("\n❌ SDK installation failed")
        return False
    
    # Step 3: Verify installation
    if not verify_installation():
        print("\n❌ SDK installation verification failed")
        return False
    
    # Step 4: Copy test files
    if not copy_test_files():
        print("\n❌ Failed to copy test files")
        return False
    
    # Step 5: Run tests
    print("\n" + "=" * 50)
    print("🎯 SDK installation complete! Running tests...")
    print("=" * 50)
    
    test_success = run_tests()
    
    # Final summary
    print("\n" + "=" * 50)
    if test_success:
        print("🎉 SUCCESS! SDK is installed and working")
        print("\n✅ Next steps:")
        print("   1. Review test results above")
        print("   2. Update Phase 5 plan to use SDK")
        print("   3. Start implementing DBR frontend")
    else:
        print("⚠️  SDK installed but tests had issues")
        print("\n💡 Troubleshooting:")
        print("   1. Check if backend is running for auth tests")
        print("   2. Review test output above")
        print("   3. Run individual tests manually if needed")
    
    return test_success

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n⏹️  Quick start interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Quick start failed: {e}")
        sys.exit(1)