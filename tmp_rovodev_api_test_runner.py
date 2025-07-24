#!/usr/bin/env python3
"""Test runner for API client tests"""

import subprocess
import sys
import os

def run_api_tests():
    """Run API client tests and capture output"""
    os.chdir("dbr_mvp/frontend")
    
    try:
        result = subprocess.run([
            "uv", "run", "pytest", "tests/test_api_client.py", "-v", "--tb=short"
        ], capture_output=True, text=True, timeout=60)
        
        print("STDOUT:")
        print(result.stdout)
        print("\nSTDERR:")
        print(result.stderr)
        print(f"\nReturn code: {result.returncode}")
        
    except subprocess.TimeoutExpired:
        print("Test timed out after 60 seconds")
    except Exception as e:
        print(f"Error running tests: {e}")

if __name__ == "__main__":
    run_api_tests()