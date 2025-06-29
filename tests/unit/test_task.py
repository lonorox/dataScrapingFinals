"""
Unit tests for the Task class.
Tests task creation, validation, and conversion methods.
"""

import unittest
import time
from unittest.mock import patch
import sys
import os
from pathlib import Path

# Add project root and src to path for imports
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "src"))

from src.scrapers.Task import Task, Result
from tests.fixtures.test_data import SAMPLE_TASKS


class TestTask(unittest.TestCase):
    """Test cases for the Task class."""

    def setUp(self):
        """Set up test fixtures."""
        self.sample_task_data = SAMPLE_TASKS[0]

    def test_task_creation(self):
        """Test basic task creation."""
        task = Task(
            id=self.sample_task_data["id"],
            priority=self.sample_task_data["priority"],
            url=self.sample_task_data["url"],
            type=self.sample_task_data["type"],
            search_word=self.sample_task_data["search_word"]
        )

        self.assertEqual(task.id, self.sample_task_data["id"])
        self.assertEqual(task.priority, self.sample_task_data["priority"])
        self.assertEqual(task.url, self.sample_task_data["url"])
        self.assertEqual(task.type, self.sample_task_data["type"])
        self.assertEqual(task.search_word, self.sample_task_data["search_word"])
        self.assertIsInstance(task.created_at, float)

    def test_task_with_search_word(self):
        """Test task creation with search word."""
        task_data = SAMPLE_TASKS[1]  # RSS task with search word
        task = Task(
            id=task_data["id"],
            priority=task_data["priority"],
            url=task_data["url"],
            type=task_data["type"],
            search_word=task_data["search_word"]
        )

        self.assertEqual(task.search_word, "technology")

    def test_task_without_search_word(self):
        """Test task creation without search word."""
        task = Task(
            id=0,
            priority=1,
            url="https://example.com",
            type="blog"
        )

        self.assertIsNone(task.search_word)

    def test_to_model_task(self):
        """Test conversion to model task."""
        task = Task(
            id=self.sample_task_data["id"],
            priority=self.sample_task_data["priority"],
            url=self.sample_task_data["url"],
            type=self.sample_task_data["type"],
            search_word=self.sample_task_data["search_word"]
        )

        model_task = task.to_model_task()

        self.assertEqual(model_task.id, str(self.sample_task_data["id"]))
        self.assertEqual(model_task.url, self.sample_task_data["url"])
        self.assertEqual(model_task.source_type, self.sample_task_data["type"])
        self.assertEqual(model_task.priority, self.sample_task_data["priority"])
        self.assertEqual(model_task.search_word, self.sample_task_data["search_word"])
        self.assertIn('created_at', model_task.metadata)
        self.assertIn('original_id', model_task.metadata)

    def test_task_attributes_immutability(self):
        """Test that task attributes are properly set and immutable."""
        task = Task(
            id=0,
            priority=1,
            url="https://example.com",
            type="blog"
        )

        # Test that attributes are set correctly
        self.assertEqual(task.id, 0)
        self.assertEqual(task.priority, 1)
        self.assertEqual(task.url, "https://example.com")
        self.assertEqual(task.type, "blog")

        # Test that created_at is a timestamp
        self.assertGreater(task.created_at, 0)
        self.assertIsInstance(task.created_at, float)


class TestResult(unittest.TestCase):
    """Test cases for the Result class."""

    def setUp(self):
        """Set up test fixtures."""
        self.sample_result_data = {
            "task_id": 0,
            "worker_name": "worker_0",
            "source_type": "blog",
            "data": [{"title": "Test Article"}],
            "success": True,
            "error_message": None,
            "processing_time": 1.5,
            "errors": [],
            "metadata": {"worker_id": 0}
        }

    def test_result_creation(self):
        """Test basic result creation."""
        result = Result(**self.sample_result_data)

        self.assertEqual(result.task_id, self.sample_result_data["task_id"])
        self.assertEqual(result.worker_name, self.sample_result_data["worker_name"])
        self.assertEqual(result.source_type, self.sample_result_data["source_type"])
        self.assertEqual(result.data, self.sample_result_data["data"])
        self.assertEqual(result.success, self.sample_result_data["success"])
        self.assertEqual(result.error_message, self.sample_result_data["error_message"])
        self.assertEqual(result.processing_time, self.sample_result_data["processing_time"])
        self.assertEqual(result.errors, self.sample_result_data["errors"])
        self.assertEqual(result.metadata, self.sample_result_data["metadata"])
        self.assertIsInstance(result.scraped_at, float)

    def test_result_creation_with_defaults(self):
        """Test result creation with default values."""
        result = Result(
            task_id=0,
            worker_name="worker_0",
            source_type="blog"
        )

        self.assertEqual(result.task_id, 0)
        self.assertEqual(result.worker_name, "worker_0")
        self.assertEqual(result.source_type, "blog")
        self.assertEqual(result.data, [])
        self.assertTrue(result.success)
        self.assertIsNone(result.error_message)
        self.assertIsInstance(result.scraped_at, float)
        self.assertEqual(result.errors, [])
        self.assertEqual(result.metadata, {})

    def test_add_error(self):
        """Test adding errors to result."""
        result = Result(
            task_id=0,
            worker_name="worker_0",
            source_type="blog"
        )

        result.add_error("Test error 1")
        result.add_error("Test error 2")

        self.assertEqual(len(result.errors), 2)
        self.assertIn("Test error 1", result.errors)
        self.assertIn("Test error 2", result.errors)

    def test_to_scraping_result(self):
        """Test conversion to model ScrapingResult."""
        result = Result(**self.sample_result_data)

        scraping_result = result.to_scraping_result()

        self.assertEqual(scraping_result.success, self.sample_result_data["success"])
        self.assertEqual(scraping_result.errors, self.sample_result_data["errors"])
        self.assertIn('task_id', scraping_result.metadata)
        self.assertIn('worker_name', scraping_result.metadata)
        self.assertIn('source_type', scraping_result.metadata)
        self.assertIn('processing_time', scraping_result.metadata)
        self.assertIn('scraped_at', scraping_result.metadata)

    def test_failed_result(self):
        """Test failed result creation."""
        failed_result = Result(
            task_id=0,
            worker_name="worker_0",
            source_type="blog",
            data=[],
            success=False,
            error_message="Connection failed",
            processing_time=5.0,
            errors=["Connection failed", "Timeout"]
        )

        self.assertFalse(failed_result.success)
        self.assertEqual(failed_result.error_message, "Connection failed")
        self.assertEqual(len(failed_result.errors), 2)
        self.assertEqual(failed_result.data, [])


if __name__ == '__main__':
    unittest.main() 