"""
Unit tests for the configs module.
Tests configuration loading and task generation.
"""

import unittest
import json
import tempfile
import os
import sys
from pathlib import Path
from unittest.mock import patch, mock_open

# Add project root and src to path for imports
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "src"))

from src.utils.configs import generate_tasks
from tests.fixtures.test_data import SAMPLE_CONFIG


class TestConfigs(unittest.TestCase):
    """Test cases for the configs module."""

    def setUp(self):
        """Set up test fixtures."""
        self.sample_config = SAMPLE_CONFIG

    @patch('builtins.open', new_callable=mock_open)
    @patch('json.load')
    def test_generate_tasks_with_search_word(self, mock_json_load, mock_file):
        """Test task generation with search words."""
        mock_json_load.return_value = self.sample_config
        
        tasks = generate_tasks()
        
        # Find RSS task with search word
        rss_task = next(task for task in tasks if task["type"] == "rss")
        self.assertEqual(rss_task["search_word"], "technology")

    @patch('builtins.open')
    def test_generate_tasks_file_not_found(self, mock_open):
        """Test task generation when config file is not found."""
        mock_open.side_effect = FileNotFoundError("Config file not found")
        
        with self.assertRaises(FileNotFoundError):
            generate_tasks()

    @patch('builtins.open', new_callable=mock_open)
    @patch('json.load')
    def test_generate_tasks_invalid_json(self, mock_json_load, mock_file):
        """Test task generation with invalid JSON."""
        mock_json_load.side_effect = json.JSONDecodeError("Invalid JSON", "", 0)
        
        with self.assertRaises(json.JSONDecodeError):
            generate_tasks()

    @patch('builtins.open', new_callable=mock_open)
    @patch('json.load')
    def test_generate_tasks_missing_tasks_key(self, mock_json_load, mock_file):
        """Test task generation with missing tasks key."""
        config_without_tasks = {
            "min_workers": 2,
            "max_workers": 5,
            "userAgents": ["test"],
            "proxies": ["test"]
        }
        mock_json_load.return_value = config_without_tasks
        
        with self.assertRaises(KeyError):
            generate_tasks()

    @patch('builtins.open', new_callable=mock_open)
    @patch('json.load')
    def test_generate_tasks_empty_tasks(self, mock_json_load, mock_file):
        """Test task generation with empty tasks list."""
        config_with_empty_tasks = self.sample_config.copy()
        config_with_empty_tasks["tasks"] = []
        mock_json_load.return_value = config_with_empty_tasks
        
        tasks = generate_tasks()
        
        self.assertIsInstance(tasks, list)
        self.assertEqual(len(tasks), 0)

    def test_generate_tasks_with_temp_file(self):
        """Test task generation using a temporary config file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as temp_file:
            json.dump(self.sample_config, temp_file)
            temp_file_path = temp_file.name

        try:
            # Change to the directory with the temp file and patch the open function
            original_cwd = os.getcwd()
            temp_dir = os.path.dirname(temp_file_path)
            os.chdir(temp_dir)
            
            with patch('builtins.open', new_callable=mock_open) as mock_file:
                mock_file.return_value.__enter__.return_value.read.return_value = json.dumps(self.sample_config)
                mock_file.return_value.__enter__.return_value.close.return_value = None
                
                tasks = generate_tasks()
                
                self.assertIsInstance(tasks, list)
                self.assertEqual(len(tasks), len(self.sample_config["tasks"]))
                
                # Verify task structure
                for task in tasks:
                    self.assertIn("priority", task)
                    self.assertIn("url", task)
                    self.assertIn("type", task)
                    self.assertIsInstance(task["priority"], int)
                    self.assertIsInstance(task["url"], str)
                    self.assertIsInstance(task["type"], str)
        finally:
            os.chdir(original_cwd)
            os.unlink(temp_file_path)

    @patch('builtins.open', new_callable=mock_open)
    @patch('json.load')
    def test_generate_tasks_task_validation(self, mock_json_load, mock_file):
        """Test that generated tasks have required fields."""
        mock_json_load.return_value = self.sample_config
        
        tasks = generate_tasks()
        
        for task in tasks:
            # Check required fields
            self.assertIn("priority", task)
            self.assertIn("url", task)
            self.assertIn("type", task)
            
            # Check data types
            self.assertIsInstance(task["priority"], int)
            self.assertIsInstance(task["url"], str)
            self.assertIsInstance(task["type"], str)
            
            # Check value ranges
            self.assertGreaterEqual(task["priority"], 1)
            self.assertLessEqual(task["priority"], 10)
            self.assertIn(task["type"], ["news", "rss", "blog"])

    @patch('builtins.open', new_callable=mock_open)
    @patch('json.load')
    def test_generate_tasks_preserves_original_data(self, mock_json_load, mock_file):
        """Test that task generation preserves original task data."""
        mock_json_load.return_value = self.sample_config
        
        tasks = generate_tasks()
        
        # Check that all original task data is preserved
        for i, task in enumerate(tasks):
            original_task = self.sample_config["tasks"][i]
            self.assertEqual(task["priority"], original_task["priority"])
            self.assertEqual(task["url"], original_task["url"])
            self.assertEqual(task["type"], original_task["type"])
            
            if "search_word" in original_task:
                self.assertEqual(task["search_word"], original_task["search_word"])


if __name__ == '__main__':
    unittest.main() 