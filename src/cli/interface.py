#!/usr/bin/env python3
"""
Web Scraping CLI Interface
Main interface and menu system for the web scraping project
"""

import argparse
import json
import os
import sys
import time
from datetime import datetime
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
from pathlib import Path

# Add src to path for imports
sys.path.append('src')

from src.scrapers.Master import Master
from src.scrapers.Task import Task
from src.utils.logger import log
from src.utils.configs import generate_tasks
from multiprocessing import Queue, Manager

from .commands import WebScrapingCommands


class WebScrapingCLI:
    def __init__(self):
        self.config_file = "config.json"
        self.results_dir = "data_output/raw"
        self.commands = WebScrapingCommands(self.config_file, self.results_dir)

    def main_menu(self):
        """Main interactive menu"""
        while True:
            print("\n" + "=" * 50)
            print("🌐 WEB SCRAPING CLI INTERFACE")
            print("=" * 50)
            print("1. 🚀 Start Scraping")
            print("2. ⚙️  Configure Settings")
            print("3. 📊 View Reports & Analytics")
            print("4. 📁 Run tests")
            print("5. 📁 Manage Data")
            print("6. 🔧 System Status")
            print("7. 📋 View Tasks")
            print("8. ❌ Exit")
            print("=" * 50)

            choice = input("Select an option (1-8): ").strip()

            if choice == '1':
                self.start_scraping_menu()
            elif choice == '2':
                self.configure_settings()
            elif choice == '3':
                self.view_reports_menu()
            elif choice == '4':
                self.commands.run_all_tests()
            elif choice == '5':
                self.manage_data_menu()
            elif choice == '6':
                self.commands.system_status()
            elif choice == '7':
                self.commands.view_tasks()
            elif choice == '8':
                print("👋 Goodbye!")
                sys.exit(0)
            else:
                print("❌ Invalid option. Please try again.")

    def start_scraping_menu(self):
        """Menu for starting scraping operations"""
        print("\n" + "=" * 40)
        print("🚀 START SCRAPING")
        print("=" * 40)
        print("1. 🔄 Run All Tasks")
        print("2. 📰 News Only")
        print("3. 📻 RSS Only")
        print("4. 📝 Blog Only")
        print("5. 🎯 Custom Selection")
        print("6. ⬅️  Back to Main Menu")

        choice = input("Select scraping type (1-6): ").strip()

        if choice == '1':
            self.commands.run_all_tasks()
        elif choice == '2':
            self.commands.run_news_only()
        elif choice == '3':
            self.commands.run_rss_only()
        elif choice == '4':
            self.commands.run_blog_only()
        elif choice == '5':
            self.commands.run_custom_selection()
        elif choice == '6':
            return
        else:
            print("❌ Invalid option.")

    def configure_settings(self):
        """Configure scraping settings"""
        print("\n" + "=" * 40)
        print("⚙️  CONFIGURE SETTINGS")
        print("=" * 40)
        print("1. 📝 Edit Tasks")
        print("2. 🔧 Worker Settings")
        print("3. 🌐 Proxy Settings")
        print("4. 📊 Rate Limiting")
        print("5. ⬅️  Back to Main Menu")

        choice = input("Select option (1-5): ").strip()

        if choice == '1':
            self.commands.edit_tasks()
        elif choice == '2':
            self.commands.worker_settings()
        elif choice == '3':
            self.commands.proxy_settings()
        elif choice == '4':
            self.commands.rate_limiting_settings()
        elif choice == '5':
            return
        else:
            print("❌ Invalid option.")

    def view_reports_menu(self):
        """Menu for viewing reports and analytics"""
        print("\n" + "=" * 40)
        print("📊 REPORTS & ANALYTICS")
        print("=" * 40)
        print("1. 📈 Data Overview")
        print("2. 📊 Performance Analytics")
        print("3. 📋 Task Summary")
        print("4. 📄 Generate HTML Report")
        print("5. ⬅️  Back to Main Menu")

        choice = input("Select option (1-5): ").strip()

        if choice == '1':
            self.commands.data_overview()
        elif choice == '2':
            self.commands.performance_analytics()
        elif choice == '3':
            self.commands.task_summary()
        elif choice == '4':
            self.commands.generate_html_report()
        elif choice == '5':
            return
        else:
            print("❌ Invalid option.")

    def manage_data_menu(self):
        """Menu for managing data"""
        print("\n" + "=" * 40)
        print("📁 MANAGE DATA")
        print("=" * 40)
        print("1. 📂 List Data Files")
        print("2. 🗑️  Clean Old Data")
        print("3. 🔍 Search Data")
        print("4. ⬅️  Back to Main Menu")

        choice = input("Select option (1-4): ").strip()

        if choice == '1':
            self.commands.list_data_files()
        elif choice == '2':
            self.commands.clean_old_data()
        elif choice == '3':
            self.commands.search_data()
        elif choice == '4':
            return
        else:
            print("❌ Invalid option.")


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description='Web Scraping CLI Interface')
    parser.add_argument('--config', default='config.json', help='Configuration file path')
    parser.add_argument('--auto', action='store_true', help='Run all tasks automatically')
    parser.add_argument('--type', choices=['news', 'rss', 'blog'], help='Run specific type only')
    parser.add_argument('--report', action='store_true', help='Generate HTML report')

    args = parser.parse_args()

    cli = WebScrapingCLI()
    cli.config_file = args.config
    cli.commands.config_file = args.config

    if args.auto:
        print("🚀 Running all tasks automatically...")
        cli.commands.run_all_tasks()
    elif args.type:
        print(f"🚀 Running {args.type} tasks...")
        if args.type == 'news':
            cli.commands.run_news_only()
        elif args.type == 'rss':
            cli.commands.run_rss_only()
        elif args.type == 'blog':
            cli.commands.run_blog_only()
    elif args.report:
        print("📄 Generating HTML report...")
        cli.commands.generate_html_report()
    else:
        # Interactive mode
        cli.main_menu()


if __name__ == "__main__":
    main() 