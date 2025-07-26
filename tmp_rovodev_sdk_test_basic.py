#!/usr/bin/env python3
"""
Basic SDK Import and Initialization Test
Tests that we can import and create SDK client
"""

import sys
import os

def test_sdk_import():
    """Test basic SDK import"""
    try:
        from dbrsdk import Dbrsdk
        from dbrsdk.models import LoginRequest, LoginResponse
        print("✅ SDK import successful")
        return True
    except ImportError as e:
        print(f"❌ SDK import failed: {e}")
        return False

def test_sdk_initialization():
    """Test SDK client initialization"""
    try:
        from dbrsdk import Dbrsdk
        
        # Test with default settings
        client = Dbrsdk()
        print("✅ SDK client initialization successful")
        
        # Test with custom server URL
        client_custom = Dbrsdk(server_url="http://localhost:8000/api/v1")
        print("✅ SDK client with custom URL successful")
        
        return True
    except Exception as e:
        print(f"❌ SDK initialization failed: {e}")
        return False

def test_sdk_models():
    """Test SDK model creation"""
    try:
        from dbrsdk.models import LoginRequest
        
        # Create a login request
        login_req = LoginRequest(
            username="test_user",
            password="test_password"
        )
        
        print(f"✅ LoginRequest model created: {login_req.username}")
        print(f"✅ Model validation working")
        return True
    except Exception as e:
        print(f"❌ SDK model creation failed: {e}")
        return False

def main():
    """Run all basic tests"""
    print("🧪 Starting Basic SDK Tests...")
    print("=" * 50)
    
    tests = [
        ("SDK Import", test_sdk_import),
        ("SDK Initialization", test_sdk_initialization),
        ("SDK Models", test_sdk_models),
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n🔍 Testing: {test_name}")
        result = test_func()
        results.append((test_name, result))
    
    print("\n" + "=" * 50)
    print("📊 Test Results:")
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {test_name}: {status}")
    
    all_passed = all(result for _, result in results)
    print(f"\n🎯 Overall: {'✅ ALL TESTS PASSED' if all_passed else '❌ SOME TESTS FAILED'}")
    
    return all_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)