#!/usr/bin/env python3
"""Simple test runner to check if our structure works"""

import subprocess
import sys
import os

def run_tests():
    """Run tests and capture output"""
    os.chdir("dbr_mvp/frontend")
    
    try:
        result = subprocess.run([
            "uv", "run", "pytest", "tests/test_app.py", "-v", "--tb=short"
        ], capture_output=True, text=True, timeout=30)
        
        print("STDOUT:")
        print(result.stdout)
        print("\nSTDERR:")
        print(result.stderr)
        print(f"\nReturn code: {result.returncode}")
        
    except subprocess.TimeoutExpired:
        print("Test timed out after 30 seconds")
    except Exception as e:
        print(f"Error running tests: {e}")

if __name__ == "__main__":
    run_tests()