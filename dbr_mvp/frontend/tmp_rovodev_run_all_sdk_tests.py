#!/usr/bin/env python3
"""
SDK Test Runner
Runs all SDK tests in sequence and provides summary
"""

import sys
import subprocess
import os
from pathlib import Path

def run_test_script(script_name: str, description: str):
    """Run a test script and capture results"""
    print(f"\n{'='*60}")
    print(f"🧪 Running: {description}")
    print(f"📄 Script: {script_name}")
    print('='*60)
    
    try:
        # Run the test script
        result = subprocess.run(
            [sys.executable, script_name],
            capture_output=False,  # Show output in real-time
            text=True,
            cwd=os.getcwd()
        )
        
        success = result.returncode == 0
        print(f"\n📊 Result: {'✅ PASSED' if success else '❌ FAILED'}")
        return success
        
    except Exception as e:
        print(f"💥 Test runner error: {e}")
        return False

def check_backend_status():
    """Check if backend is running"""
    print("🔍 Checking backend status...")
    try:
        import requests
        response = requests.get("http://localhost:8000/api/v1/docs", timeout=5)
        if response.status_code == 200:
            print("✅ Backend is running on localhost:8000")
            return True
        else:
            print(f"⚠️  Backend responded with status {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Backend is not running on localhost:8000")
        return False
    except ImportError:
        print("⚠️  requests not available, skipping backend check")
        return None
    except Exception as e:
        print(f"⚠️  Backend check failed: {e}")
        return None

def main():
    """Run all SDK tests"""
    print("🚀 DBR SDK Test Suite")
    print("=" * 60)
    print("📋 This will test the DBR SDK installation and functionality")
    print("=" * 60)
    
    # Check if we're in the right directory
    current_dir = Path.cwd()
    print(f"📁 Current directory: {current_dir}")
    
    # Check for test files
    test_files = [
        "tmp_rovodev_sdk_test_basic.py",
        "tmp_rovodev_sdk_test_auth.py", 
        "tmp_rovodev_sdk_test_org.py"
    ]
    
    missing_files = [f for f in test_files if not Path(f).exists()]
    if missing_files:
        print(f"❌ Missing test files: {missing_files}")
        return False
    
    print("✅ All test files found")
    
    # Check backend status
    backend_running = check_backend_status()
    
    if backend_running is False:
        print("\n⚠️  WARNING: Backend is not running!")
        print("   Authentication and organization tests will fail")
        print("   To start backend: cd dbr_mvp/backend && uv run python -m dbr.main")
        print("\n   Continue anyway? (y/n): ", end="")
        
        try:
            response = input().lower().strip()
            if response != 'y':
                print("❌ Tests cancelled by user")
                return False
        except KeyboardInterrupt:
            print("\n❌ Tests cancelled by user")
            return False
    
    # Define tests to run
    tests = [
        ("tmp_rovodev_sdk_test_basic.py", "Basic SDK Import & Initialization"),
        ("tmp_rovodev_sdk_test_auth.py", "Authentication & Login"),
        ("tmp_rovodev_sdk_test_org.py", "Organization Management"),
    ]
    
    # Run tests
    results = []
    for script, description in tests:
        success = run_test_script(script, description)
        results.append((description, success))
    
    # Final summary
    print("\n" + "=" * 60)
    print("📊 FINAL TEST SUMMARY")
    print("=" * 60)
    
    for test_name, success in results:
        status = "✅ PASSED" if success else "❌ FAILED"
        print(f"  {test_name:<35} {status}")
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    print(f"\n🎯 Overall Results: {passed}/{total} test suites passed")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED! SDK is ready for use.")
        print("\n✅ Next steps:")
        print("   1. Update Phase 5 plan to use SDK")
        print("   2. Add SDK as dependency to frontend")
        print("   3. Start implementing DBR frontend with SDK")
    elif passed > 0:
        print("⚠️  PARTIAL SUCCESS - Some tests passed")
        print("\n💡 Recommendations:")
        print("   1. Fix failing tests before proceeding")
        print("   2. Ensure backend is running for auth tests")
        print("   3. Check SDK installation if basic tests failed")
    else:
        print("❌ ALL TESTS FAILED")
        print("\n🔧 Troubleshooting:")
        print("   1. Check SDK installation: pip list | grep dbrsdk")
        print("   2. Verify Python environment")
        print("   3. Check for import errors")
    
    return passed == total

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n⏹️  Test suite interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Test suite crashed: {e}")
        sys.exit(1)