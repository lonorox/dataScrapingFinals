import sys
import subprocess

if __name__ == "__main__":
    try:
        import pytest
        print("Running all tests with pytest...\n")
        sys.exit(pytest.main(["-v", "tests/"]))
    except ImportError:
        print("pytest not installed, falling back to unittest discovery...\n")
        import unittest
        loader = unittest.TestLoader()
        suite = loader.discover('tests')
        runner = unittest.TextTestRunner(verbosity=2)
        result = runner.run(suite)
        sys.exit(not result.wasSuccessful()) 