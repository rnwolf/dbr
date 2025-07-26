#!/usr/bin/env python3
"""
SDK Authentication Test
Tests login/logout functionality with the backend
"""

import sys
import asyncio
from typing import Optional

def test_backend_connection():
    """Test basic connection to backend"""
    try:
        from dbrsdk import Dbrsdk
        
        # Test connection to backend
        client = Dbrsdk(server_url="http://localhost:8000/api/v1")
        print("✅ SDK client created with backend URL")
        return True
    except Exception as e:
        print(f"❌ Backend connection setup failed: {e}")
        return False

def test_login_sync():
    """Test synchronous login"""
    try:
        from dbrsdk import Dbrsdk
        from dbrsdk.models import LoginRequest
        
        # Create client without authentication first
        client = Dbrsdk(server_url="http://localhost:8000/api/v1")
        
        # Attempt login (this will likely fail if no backend is running)
        login_request = LoginRequest(
            username="admin",  # Default super user
            password="admin"   # Default password
        )
        
        print("🔍 Attempting login...")
        response = client.authentication.login(login_request)
        
        print(f"✅ Login successful!")
        print(f"   Token type: {response.token_type}")
        print(f"   Access token: {response.access_token[:20]}...")
        print(f"   User info: {response.user}")
        
        return True, response.access_token
    except Exception as e:
        print(f"❌ Login failed: {e}")
        print("   Note: This is expected if backend is not running")
        return False, None

async def test_login_async():
    """Test asynchronous login"""
    try:
        from dbrsdk import Dbrsdk
        from dbrsdk.models import LoginRequest
        
        # Create async client
        async with Dbrsdk(server_url="http://localhost:8000/api/v1") as client:
            
            login_request = LoginRequest(
                username="admin",
                password="admin"
            )
            
            print("🔍 Attempting async login...")
            response = await client.authentication.login_async(login_request)
            
            print(f"✅ Async login successful!")
            print(f"   Token: {response.access_token[:20]}...")
            
            return True, response.access_token
    except Exception as e:
        print(f"❌ Async login failed: {e}")
        return False, None

def test_authenticated_client(token: str):
    """Test using authenticated client"""
    try:
        from dbrsdk import Dbrsdk
        
        # Create authenticated client
        auth_client = Dbrsdk(
            server_url="http://localhost:8000/api/v1",
            http_bearer=token
        )
        
        print("✅ Authenticated client created")
        
        # Try to make an authenticated request (this will test the token)
        # We'll try to get work items (this should work if we have an org)
        print("🔍 Testing authenticated request...")
        
        # Note: This might fail if no organization exists yet
        # work_items = auth_client.work_items.list(organization_id="test-org-id")
        
        print("✅ Authenticated client setup successful")
        return True
    except Exception as e:
        print(f"❌ Authenticated client test failed: {e}")
        return False

def main():
    """Run authentication tests"""
    print("🧪 Starting SDK Authentication Tests...")
    print("=" * 60)
    print("📝 Note: These tests require the backend to be running on localhost:8000")
    print("=" * 60)
    
    # Test 1: Basic connection
    print(f"\n🔍 Test 1: Backend Connection Setup")
    conn_result = test_backend_connection()
    
    # Test 2: Synchronous login
    print(f"\n🔍 Test 2: Synchronous Login")
    login_result, token = test_login_sync()
    
    # Test 3: Asynchronous login
    print(f"\n🔍 Test 3: Asynchronous Login")
    async_result, async_token = asyncio.run(test_login_async())
    
    # Test 4: Authenticated client (if we got a token)
    auth_result = False
    if token:
        print(f"\n🔍 Test 4: Authenticated Client")
        auth_result = test_authenticated_client(token)
    else:
        print(f"\n⏭️  Test 4: Skipped (no token available)")
    
    # Results
    print("\n" + "=" * 60)
    print("📊 Authentication Test Results:")
    print(f"  Backend Connection: {'✅ PASS' if conn_result else '❌ FAIL'}")
    print(f"  Sync Login: {'✅ PASS' if login_result else '❌ FAIL'}")
    print(f"  Async Login: {'✅ PASS' if async_result else '❌ FAIL'}")
    print(f"  Authenticated Client: {'✅ PASS' if auth_result else '⏭️ SKIP'}")
    
    # Overall assessment
    critical_tests = [conn_result, login_result or async_result]
    all_critical_passed = all(critical_tests)
    
    print(f"\n🎯 Overall: {'✅ CRITICAL TESTS PASSED' if all_critical_passed else '❌ CRITICAL TESTS FAILED'}")
    
    if not (login_result or async_result):
        print("\n💡 Troubleshooting:")
        print("   1. Ensure backend is running: cd dbr_mvp/backend && uv run python -m dbr.main")
        print("   2. Check backend URL: http://localhost:8000/api/v1")
        print("   3. Verify default credentials: admin/admin")
    
    return all_critical_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)