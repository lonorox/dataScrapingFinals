"""
Unit tests for the CLI commands.
Tests command functionality and user interactions.
"""

import unittest
import json
import tempfile
import os
import sys
from pathlib import Path
from unittest.mock import patch, mock_open, MagicMock
from io import StringIO

# Add project root and src to path for imports
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "src"))

from src.cli.commands import WebScrapingCommands
from tests.fixtures.test_data import SAMPLE_CONFIG, SAMPLE_ARTICLES


class TestWebScrapingCommands(unittest.TestCase):
    """Test cases for the WebScrapingCommands class."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.config_file = os.path.join(self.temp_dir, "test_config.json")
        self.results_dir = os.path.join(self.temp_dir, "data_output", "raw")
        os.makedirs(self.results_dir, exist_ok=True)
        
        # Create test config file
        with open(self.config_file, 'w') as f:
            json.dump(SAMPLE_CONFIG, f, indent=2)
        
        self.commands = WebScrapingCommands(self.config_file, self.results_dir)

    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    @patch('src.cli.commands.Master')
    @patch('src.cli.commands.generate_tasks')
    def test_run_all_tasks_success(self, mock_generate_tasks, mock_master_class):
        """Test successful execution of all tasks."""
        # Mock generate_tasks
        mock_generate_tasks.return_value = SAMPLE_CONFIG["tasks"]
        
        # Mock Master instance
        mock_master = MagicMock()
        mock_master_class.return_value = mock_master
        
        # Capture print output
        with patch('sys.stdout', new=StringIO()) as fake_output:
            self.commands.run_all_tasks()
        
        # Verify Master was called
        mock_master_class.assert_called_once()
        mock_master.run.assert_called_once()
        
        # Check output contains expected messages
        output = fake_output.getvalue()
        self.assertIn("Starting all scraping tasks", output)
        self.assertIn("Scraping completed successfully", output)

    @patch('src.cli.commands.Master')
    @patch('src.cli.commands.generate_tasks')
    def test_run_all_tasks_exception(self, mock_generate_tasks, mock_master_class):
        """Test handling of exceptions during task execution."""
        mock_generate_tasks.side_effect = Exception("Test error")
        
        with patch('sys.stdout', new=StringIO()) as fake_output:
            self.commands.run_all_tasks()
        
        output = fake_output.getvalue()
        self.assertIn("Error during scraping", output)
        self.assertIn("Test error", output)

    @patch('src.cli.commands.Master')
    @patch('src.cli.commands.generate_tasks')
    def test_run_filtered_tasks_news(self, mock_generate_tasks, mock_master_class):
        """Test running filtered news tasks."""
        mock_generate_tasks.return_value = SAMPLE_CONFIG["tasks"]
        mock_master = MagicMock()
        mock_master_class.return_value = mock_master
        
        with patch('sys.stdout', new=StringIO()) as fake_output:
            self.commands.run_news_only()
        
        mock_master.run.assert_called_once()
        output = fake_output.getvalue()
        self.assertIn("Starting news scraping", output)
        self.assertIn("News scraping completed", output)

    @patch('src.cli.commands.Master')
    @patch('src.cli.commands.generate_tasks')
    def test_run_filtered_tasks_no_tasks_found(self, mock_generate_tasks, mock_master_class):
        """Test running filtered tasks when no tasks of that type are found."""
        # Create config with no RSS tasks
        config_without_rss = SAMPLE_CONFIG.copy()
        config_without_rss["tasks"] = [task for task in SAMPLE_CONFIG["tasks"] if task["type"] != "rss"]
        mock_generate_tasks.return_value = config_without_rss["tasks"]
        
        with patch('sys.stdout', new=StringIO()) as fake_output:
            self.commands.run_rss_only()
        
        output = fake_output.getvalue()
        self.assertIn("No rss tasks found", output)

    @patch('builtins.input', return_value='1,3')
    @patch('src.cli.commands.Master')
    @patch('src.cli.commands.generate_tasks')
    def test_run_custom_selection_success(self, mock_generate_tasks, mock_master_class, mock_input):
        """Test successful custom task selection."""
        mock_generate_tasks.return_value = SAMPLE_CONFIG["tasks"]
        mock_master = MagicMock()
        mock_master_class.return_value = mock_master
        
        with patch('sys.stdout', new=StringIO()) as fake_output:
            self.commands.run_custom_selection()
        
        mock_master.run.assert_called_once()
        output = fake_output.getvalue()
        self.assertIn("Custom Task Selection", output)
        self.assertIn("Custom scraping completed", output)

    @patch('builtins.input', return_value='invalid')
    def test_run_custom_selection_invalid_input(self, mock_input):
        """Test custom task selection with invalid input."""
        with patch('sys.stdout', new=StringIO()) as fake_output:
            self.commands.run_custom_selection()
        
        output = fake_output.getvalue()
        self.assertIn("Invalid selection", output)

    @patch('builtins.input', side_effect=['1', 'blog', 'https://newblog.com', '5', '4'])
    @patch('builtins.open', new_callable=mock_open, read_data='{"tasks": []}')
    @patch('json.load')
    @patch('json.dump')
    def test_edit_tasks_add_task(self, mock_json_dump, mock_json_load, mock_file, mock_input):
        """Test adding a new task."""
        mock_json_load.return_value = SAMPLE_CONFIG
        
        with patch('sys.stdout', new=StringIO()) as fake_output:
            self.commands.edit_tasks()
        
        # Verify that json.dump was called at least once
        self.assertGreater(mock_json_dump.call_count, 0)
        output = fake_output.getvalue()
        self.assertIn("Task added successfully", output)

    @patch('builtins.input', side_effect=['2', '1', 'https://updated.com', '', '4'])
    @patch('builtins.open', new_callable=mock_open)
    @patch('json.load')
    @patch('json.dump')
    def test_edit_tasks_edit_existing_task(self, mock_json_dump, mock_json_load, mock_file, mock_input):
        """Test editing an existing task."""
        mock_json_load.return_value = SAMPLE_CONFIG
        
        with patch('sys.stdout', new=StringIO()) as fake_output:
            self.commands.edit_tasks()
        
        mock_json_dump.assert_called()
        output = fake_output.getvalue()
        self.assertIn("Task updated successfully", output)

    @patch('builtins.input', side_effect=['3', '1', 'y', '4'])
    @patch('builtins.open', new_callable=mock_open)
    @patch('json.load')
    @patch('json.dump')
    def test_edit_tasks_delete_task(self, mock_json_dump, mock_json_load, mock_file, mock_input):
        """Test deleting a task."""
        mock_json_load.return_value = SAMPLE_CONFIG
        
        with patch('sys.stdout', new=StringIO()) as fake_output:
            self.commands.edit_tasks()
        
        mock_json_dump.assert_called()
        output = fake_output.getvalue()
        self.assertIn("Task deleted successfully", output)

    def test_task_summary(self):
        """Test task summary display."""
        with patch('sys.stdout', new=StringIO()) as fake_output:
            self.commands.task_summary()
        
        output = fake_output.getvalue()
        self.assertIn("Task Summary", output)
        self.assertIn("Total tasks configured", output)
        self.assertIn("Worker settings", output)

    def test_data_overview_no_data(self):
        """Test data overview when no data files exist."""
        with patch('sys.stdout', new=StringIO()) as fake_output:
            self.commands.data_overview()
        
        output = fake_output.getvalue()
        self.assertIn("No data files found", output)

    def test_data_overview_with_data(self):
        """Test data overview with existing data files."""
        # Create test data files
        test_data = [{"title": "Test Article"}]
        blog_file = os.path.join(self.results_dir, "blog_data.json")
        with open(blog_file, 'w') as f:
            json.dump(test_data, f)
        
        with patch('sys.stdout', new=StringIO()) as fake_output:
            self.commands.data_overview()
        
        output = fake_output.getvalue()
        self.assertIn("Data files in", output)
        self.assertIn("blog_data.json", output)
        self.assertIn("1 items", output)

    def test_system_status(self):
        """Test system status display."""
        with patch('sys.stdout', new=StringIO()) as fake_output:
            self.commands.system_status()
        
        output = fake_output.getvalue()
        self.assertIn("System Status", output)
        self.assertIn("Configuration", output)
        self.assertIn("Data Directory", output)
        self.assertIn("Dependencies", output)

    @patch('builtins.input', return_value='test')
    def test_search_data_no_files(self, mock_input):
        """Test search functionality when no data files exist."""
        with patch('sys.stdout', new=StringIO()) as fake_output:
            self.commands.search_data()
        
        output = fake_output.getvalue()
        self.assertIn("No data files found", output)

    def test_search_data_with_files(self):
        """Test search functionality with existing data files."""
        # Create test data file
        test_data = [
            {"title": "Test Article", "summary": "This is a test article about technology"}
        ]
        blog_file = os.path.join(self.results_dir, "blog_data.json")
        with open(blog_file, 'w') as f:
            json.dump(test_data, f)
        
        with patch('builtins.input', return_value='technology'):
            with patch('sys.stdout', new=StringIO()) as fake_output:
                self.commands.search_data()
        
        output = fake_output.getvalue()
        self.assertIn("Found 1 items", output)
        self.assertIn("Test Article", output)

    def test_clean_old_data_no_files(self):
        """Test cleaning old data when no files exist."""
        with patch('sys.stdout', new=StringIO()) as fake_output:
            self.commands.clean_old_data()
        
        output = fake_output.getvalue()
        self.assertIn("No data files to clean", output)

    @patch('builtins.input', return_value='y')
    def test_clean_old_data_with_files(self, mock_input):
        """Test cleaning old data with existing files."""
        # Create test data file
        test_file = os.path.join(self.results_dir, "test_data.json")
        with open(test_file, 'w') as f:
            json.dump([{"test": "data"}], f)
        
        with patch('sys.stdout', new=StringIO()) as fake_output:
            self.commands.clean_old_data()
        
        output = fake_output.getvalue()
        self.assertIn("All data files deleted", output)
        self.assertFalse(os.path.exists(test_file))

    def test_worker_settings(self):
        """Test worker settings configuration."""
        with patch('builtins.input', side_effect=['3', '7']):
            with patch('sys.stdout', new=StringIO()) as fake_output:
                self.commands.worker_settings()
        
        output = fake_output.getvalue()
        self.assertIn("Worker Settings", output)
        self.assertIn("Worker settings updated", output)

    def test_proxy_settings(self):
        """Test proxy settings configuration."""
        with patch('builtins.input', side_effect=['1', 'http://newproxy:8080', '4']):
            with patch('sys.stdout', new=StringIO()) as fake_output:
                self.commands.proxy_settings()
        
        output = fake_output.getvalue()
        self.assertIn("Proxy Settings", output)
        self.assertIn("Proxy added", output)

    def test_rate_limiting_settings(self):
        """Test rate limiting settings display."""
        with patch('sys.stdout', new=StringIO()) as fake_output:
            self.commands.rate_limiting_settings()
        
        output = fake_output.getvalue()
        self.assertIn("Rate Limiting Settings", output)
        self.assertIn("hardcoded", output)

    def test_export_data(self):
        """Test export data functionality."""
        with patch('sys.stdout', new=StringIO()) as fake_output:
            self.commands.export_data()
        
        output = fake_output.getvalue()
        self.assertIn("Export Data", output)
        self.assertIn("JSON format", output)

    def test_schedule_scraping(self):
        """Test schedule scraping functionality."""
        with patch('sys.stdout', new=StringIO()) as fake_output:
            self.commands.schedule_scraping()
        
        output = fake_output.getvalue()
        self.assertIn("Schedule Scraping", output)
        self.assertIn("not yet implemented", output)

    def test_view_tasks(self):
        """Test viewing current tasks."""
        with patch('sys.stdout', new=StringIO()) as fake_output:
            self.commands.view_tasks()
        
        output = fake_output.getvalue()
        self.assertIn("Current Tasks", output)
        self.assertIn("Total tasks", output)

    def test_performance_analytics_no_summary(self):
        """Test performance analytics when no summary file exists."""
        with patch('sys.stdout', new=StringIO()) as fake_output:
            self.commands.performance_analytics()
        
        output = fake_output.getvalue()
        self.assertIn("No summary file found", output)

    def test_list_data_files_no_files(self):
        """Test listing data files when none exist."""
        # Create a commands instance with a non-existent directory
        temp_dir = tempfile.mkdtemp()
        non_existent_dir = os.path.join(temp_dir, "non_existent")
        commands_without_dir = WebScrapingCommands(self.config_file, non_existent_dir)
        
        try:
            with patch('sys.stdout', new=StringIO()) as fake_output:
                commands_without_dir.list_data_files()
            
            output = fake_output.getvalue()
            self.assertIn("No data directory found", output)
        finally:
            import shutil
            shutil.rmtree(temp_dir, ignore_errors=True)

    def test_list_data_files_with_files(self):
        """Test listing data files with existing files."""
        # Create test files
        json_file = os.path.join(self.results_dir, "test.json")
        csv_file = os.path.join(self.results_dir, "test.csv")
        
        with open(json_file, 'w') as f:
            json.dump([{"test": "data"}], f)
        with open(csv_file, 'w') as f:
            f.write("test,data\n")
        
        with patch('sys.stdout', new=StringIO()) as fake_output:
            self.commands.list_data_files()
        
        output = fake_output.getvalue()
        self.assertIn("JSON Files", output)
        self.assertIn("CSV Files", output)
        self.assertIn("test.json", output)
        self.assertIn("test.csv", output)


if __name__ == '__main__':
    unittest.main() 