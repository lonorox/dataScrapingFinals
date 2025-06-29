#!/usr/bin/env python3
"""
Test runner script for the data scraping project.
Provides options to run different types of tests.
"""

import sys
import os
import subprocess
import argparse
import unittest
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "src"))


def run_unit_tests():
    """Run all unit tests."""
    print("🧪 Running unit tests...")
    
    # Discover and run unit tests
    loader = unittest.TestLoader()
    start_dir = project_root / "tests" / "unit"
    suite = loader.discover(start_dir, pattern="test_*.py")
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()


def run_integration_tests():
    """Run all integration tests."""
    print("🔗 Running integration tests...")
    
    # Discover and run integration tests
    loader = unittest.TestLoader()
    start_dir = project_root / "tests" / "integration"
    suite = loader.discover(start_dir, pattern="test_*.py")
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()


def run_all_tests():
    """Run all tests (unit and integration)."""
    print("🚀 Running all tests...")
    
    # Discover and run all tests
    loader = unittest.TestLoader()
    start_dir = project_root / "tests"
    suite = loader.discover(start_dir, pattern="test_*.py")
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()


def run_pytest_tests(test_type=None, verbose=False):
    """Run tests using pytest."""
    print(f"🧪 Running tests with pytest...")
    
    cmd = ["python", "-m", "pytest"]
    
    if test_type == "unit":
        cmd.extend(["--markers", "unit"])
    elif test_type == "integration":
        cmd.extend(["--markers", "integration"])
    
    if verbose:
        cmd.append("-v")
    
    cmd.extend(["-s", "--tb=short"])
    
    try:
        result = subprocess.run(cmd, cwd=project_root, check=True)
        return result.returncode == 0
    except subprocess.CalledProcessError as e:
        print(f"❌ Pytest failed with return code: {e.returncode}")
        return False
    except FileNotFoundError:
        print("❌ Pytest not found. Please install pytest: pip install pytest")
        return False


def run_coverage_tests():
    """Run tests with coverage reporting."""
    print("📊 Running tests with coverage...")
    
    try:
        # Run tests with coverage
        cmd = [
            "python", "-m", "coverage", "run", "--source=src",
            "-m", "pytest", "tests/", "-v"
        ]
        
        result = subprocess.run(cmd, cwd=project_root, check=True)
        
        if result.returncode == 0:
            # Generate coverage report
            subprocess.run(["python", "-m", "coverage", "report"], cwd=project_root, check=True)
            subprocess.run(["python", "-m", "coverage", "html"], cwd=project_root, check=True)
            print("📊 Coverage report generated in htmlcov/")
            return True
        else:
            return False
            
    except subprocess.CalledProcessError as e:
        print(f"❌ Coverage test failed with return code: {e.returncode}")
        return False
    except FileNotFoundError:
        print("❌ Coverage not found. Please install coverage: pip install coverage")
        return False


def run_specific_test(test_file):
    """Run a specific test file."""
    print(f"🎯 Running specific test: {test_file}")
    
    test_path = project_root / "tests" / test_file
    
    if not test_path.exists():
        print(f"❌ Test file not found: {test_path}")
        return False
    
    loader = unittest.TestLoader()
    suite = loader.discover(str(test_path.parent), pattern=test_path.name)
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()


def check_test_dependencies():
    """Check if required test dependencies are installed."""
    required_packages = [
        "pytest",
        "pytest-cov",
        "pandas",
        "matplotlib",
        "seaborn"
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace("-", "_"))
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print("❌ Missing test dependencies:")
        for package in missing_packages:
            print(f"   - {package}")
        print("\nInstall with: pip install " + " ".join(missing_packages))
        return False
    
    print("✅ All test dependencies are installed")
    return True


def main():
    """Main function to run tests based on command line arguments."""
    parser = argparse.ArgumentParser(description="Run tests for the data scraping project")
    parser.add_argument(
        "--type", 
        choices=["unit", "integration", "all"], 
        default="all",
        help="Type of tests to run"
    )
    parser.add_argument(
        "--runner", 
        choices=["unittest", "pytest"], 
        default="unittest",
        help="Test runner to use"
    )
    parser.add_argument(
        "--coverage", 
        action="store_true",
        help="Run tests with coverage reporting"
    )
    parser.add_argument(
        "--verbose", "-v", 
        action="store_true",
        help="Verbose output"
    )
    parser.add_argument(
        "--file", 
        help="Run a specific test file"
    )
    parser.add_argument(
        "--check-deps", 
        action="store_true",
        help="Check test dependencies"
    )
    
    args = parser.parse_args()
    
    # Check dependencies if requested
    if args.check_deps:
        return 0 if check_test_dependencies() else 1
    
    # Run specific test file if provided
    if args.file:
        success = run_specific_test(args.file)
        return 0 if success else 1
    
    # Run coverage tests if requested
    if args.coverage:
        success = run_coverage_tests()
        return 0 if success else 1
    
    # Run tests based on type and runner
    if args.runner == "pytest":
        success = run_pytest_tests(args.type, args.verbose)
    else:
        if args.type == "unit":
            success = run_unit_tests()
        elif args.type == "integration":
            success = run_integration_tests()
        else:  # all
            success = run_all_tests()
    
    if success:
        print("✅ All tests passed!")
        return 0
    else:
        print("❌ Some tests failed!")
        return 1


if __name__ == "__main__":
    sys.exit(main()) 