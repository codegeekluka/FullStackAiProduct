#!/usr/bin/env python3
"""
Test runner script for the Recipe App backend
"""
import sys
import subprocess
import os
from pathlib import Path


def run_command(command, description):
    """Run a command and handle errors"""
    print(f"\n{'='*60}")
    print(f"Running: {description}")
    print(f"Command: {command}")
    print(f"{'='*60}")
    
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error running {description}:")
        print(f"Exit code: {e.returncode}")
        print(f"Error output: {e.stderr}")
        return False


def main():
    """Main test runner"""
    # Change to the backend directory
    backend_dir = Path(__file__).parent
    os.chdir(backend_dir)
    
    print("Recipe App Backend Test Runner")
    print("=" * 40)
    
    # Check if we're in the right directory
    if not (backend_dir / "tests").exists():
        print("Error: tests directory not found. Make sure you're in the backend directory.")
        sys.exit(1)
    
    # Install test dependencies if needed
    if not run_command("pip install -r requirements-test.txt", "Installing test dependencies"):
        print("Failed to install test dependencies")
        sys.exit(1)
    
    # Run different types of tests
    test_commands = [
        ("pytest tests/unit/ -v --tb=short", "Unit Tests"),
        ("pytest tests/integration/ -v --tb=short", "Integration Tests"),
        ("pytest tests/ -v --cov=backend --cov-report=term-missing", "All Tests with Coverage"),
        ("pytest tests/ -v --cov=backend --cov-report=html:htmlcov", "Generate HTML Coverage Report"),
    ]
    
    success_count = 0
    total_tests = len(test_commands)
    
    for command, description in test_commands:
        if run_command(command, description):
            success_count += 1
        else:
            print(f"\n❌ {description} failed!")
    
    # Summary
    print(f"\n{'='*60}")
    print("TEST SUMMARY")
    print(f"{'='*60}")
    print(f"Tests run: {total_tests}")
    print(f"Successful: {success_count}")
    print(f"Failed: {total_tests - success_count}")
    
    if success_count == total_tests:
        print("\n🎉 All tests completed successfully!")
        sys.exit(0)
    else:
        print(f"\n❌ {total_tests - success_count} test suite(s) failed!")
        sys.exit(1)


if __name__ == "__main__":
    main()
