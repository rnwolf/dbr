#!/usr/bin/env python3
"""
BDD Test Runner for DBR Frontend
Demonstrates the new BDD testing approach with SDK-level validation
"""

import subprocess
import sys
import os
from pathlib import Path

def run_command(cmd, cwd=None):
    """Run a command and return success status"""
    print(f"Running: {' '.join(cmd)}")
    try:
        result = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Success")
            if result.stdout:
                print(result.stdout)
            return True
        else:
            print("❌ Failed")
            if result.stderr:
                print(result.stderr)
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    """Main test runner function"""
    print("🚀 DBR BDD Testing Strategy Demo")
    print("=" * 50)
    
    # Get the frontend directory
    frontend_dir = Path(__file__).parent / "dbr_mvp" / "frontend"
    if not frontend_dir.exists():
        print(f"❌ Frontend directory not found: {frontend_dir}")
        return False
    
    print(f"📁 Working directory: {frontend_dir}")
    
    # Check if BDD tests exist
    bdd_dir = frontend_dir / "tests_bdd"
    if not bdd_dir.exists():
        print(f"❌ BDD tests directory not found: {bdd_dir}")
        return False
    
    print("\n📋 Available BDD Test Features:")
    feature_files = list((bdd_dir / "features").glob("*.feature"))
    for feature_file in feature_files:
        print(f"  • {feature_file.name}")
    
    print("\n🔧 Test Setup:")
    print("1. Checking dependencies...")
    
    # Check if uv is available
    if not run_command(["uv", "--version"]):
        print("❌ UV package manager not found. Please install UV first.")
        return False
    
    print("\n2. Installing dependencies...")
    if not run_command(["uv", "sync"], cwd=frontend_dir):
        print("❌ Failed to install dependencies")
        return False
    
    print("\n🧪 Running BDD Tests:")
    print("Note: These tests require a running backend server")
    print("The tests will automatically start the backend server")
    
    # Test scenarios to run
    test_scenarios = [
        {
            "name": "Authentication Workflow",
            "command": ["uv", "run", "pytest", "tests_bdd/", "-k", "authentication", "-v"],
            "description": "Tests user login and token management"
        },
        {
            "name": "User Management",
            "command": ["uv", "run", "pytest", "tests_bdd/", "-k", "user_management", "-v"],
            "description": "Tests user CRUD operations and role management"
        },
        {
            "name": "Work Item Management",
            "command": ["uv", "run", "pytest", "tests_bdd/", "-k", "work_item", "-v"],
            "description": "Tests work item lifecycle and operations"
        },
        {
            "name": "DBR Scheduling",
            "command": ["uv", "run", "pytest", "tests_bdd/", "-k", "scheduling", "-v"],
            "description": "Tests core DBR scheduling and time progression"
        }
    ]
    
    print("\n📊 Test Execution Summary:")
    results = {}
    
    for scenario in test_scenarios:
        print(f"\n🔍 {scenario['name']}")
        print(f"   {scenario['description']}")
        print("   " + "-" * 40)
        
        success = run_command(scenario["command"], cwd=frontend_dir)
        results[scenario["name"]] = success
        
        if success:
            print(f"   ✅ {scenario['name']} - PASSED")
        else:
            print(f"   ❌ {scenario['name']} - FAILED")
    
    print("\n" + "=" * 50)
    print("📈 Final Results:")
    
    passed = sum(1 for success in results.values() if success)
    total = len(results)
    
    for name, success in results.items():
        status = "✅ PASSED" if success else "❌ FAILED"
        print(f"  {name}: {status}")
    
    print(f"\nOverall: {passed}/{total} test suites passed")
    
    if passed == total:
        print("🎉 All BDD test suites passed!")
        print("\n💡 Key Benefits Demonstrated:")
        print("  • SDK-level testing without GUI complexity")
        print("  • Clear business-focused test scenarios")
        print("  • Reliable backend API validation")
        print("  • Fast feedback on core functionality")
    else:
        print("⚠️  Some test suites failed.")
        print("This is expected if the backend is not fully implemented")
        print("or if there are API contract mismatches.")
    
    print("\n📚 Next Steps:")
    print("1. Review the BDD_TESTING_STRATEGY.md for detailed information")
    print("2. Examine the feature files in tests_bdd/features/")
    print("3. Check step definitions in tests_bdd/step_definitions/")
    print("4. Consider migrating existing GUI tests to this approach")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)