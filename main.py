#!/usr/bin/env python3
"""
Main entry point for the data scraping application.
Runs the CLI interface.
"""

import sys
import os
from src.cli.interface import main
# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

if __name__ == '__main__':
    # Import and run the CLI
    main()