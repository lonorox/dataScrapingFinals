"""
Smoke test to verify the test infrastructure is working correctly.
This test should always pass and can be used to verify the test setup.
"""

import unittest
import sys
import os
from pathlib import Path

# Add project root and src to path for imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "src"))


class TestSmoke(unittest.TestCase):
    """Smoke tests to verify test infrastructure."""

    def test_imports_work(self):
        """Test that basic imports work."""
        try:
            # Test importing main modules
            from src.scrapers.Task import Task, Result
            from src.data.models import Article, ScrapingResult, ScrapingStats
            from tests.fixtures.test_data import SAMPLE_CONFIG, SAMPLE_ARTICLES
            
            self.assertTrue(True)  # If we get here, imports worked
        except ImportError as e:
            self.fail(f"Import failed: {e}")

    def test_basic_functionality(self):
        """Test basic functionality of core classes."""
        from src.scrapers.Task import Task, Result
        
        # Test Task creation
        task = Task(id=0, priority=1, url="https://example.com", type="blog")
        self.assertEqual(task.id, 0)
        self.assertEqual(task.priority, 1)
        self.assertEqual(task.url, "https://example.com")
        self.assertEqual(task.type, "blog")
        
        # Test Result creation
        result = Result(
            task_id=0,
            worker_name="worker_0",
            source_type="blog",
            data=[{"title": "Test"}],
            success=True
        )
        self.assertEqual(result.task_id, 0)
        self.assertEqual(result.worker_name, "worker_0")
        self.assertTrue(result.success)

    def test_test_data_available(self):
        """Test that test data is available."""
        from tests.fixtures.test_data import SAMPLE_CONFIG, SAMPLE_ARTICLES
        
        # Test config data
        self.assertIsInstance(SAMPLE_CONFIG, dict)
        self.assertIn("tasks", SAMPLE_CONFIG)
        self.assertIn("min_workers", SAMPLE_CONFIG)
        self.assertIn("max_workers", SAMPLE_CONFIG)
        
        # Test articles data
        self.assertIsInstance(SAMPLE_ARTICLES, list)
        self.assertGreater(len(SAMPLE_ARTICLES), 0)
        
        # Test first article structure
        first_article = SAMPLE_ARTICLES[0]
        self.assertIn("title", first_article)
        self.assertIn("url", first_article)
        self.assertIn("source_type", first_article)

    def test_path_setup(self):
        """Test that path setup is working correctly."""
        # Test that we can access the project structure
        project_root = Path(__file__).parent.parent
        src_path = project_root / 'src'
        
        self.assertTrue(project_root.exists())
        self.assertTrue(src_path.exists())
        self.assertTrue((src_path / 'scrapers').exists())
        self.assertTrue((src_path / 'data').exists())

    def test_unittest_framework(self):
        """Test that unittest framework is working."""
        # This test should always pass
        self.assertTrue(True)
        self.assertEqual(1 + 1, 2)
        self.assertIn("test", "this is a test")

    def test_mock_imports(self):
        """Test that mock imports work."""
        try:
            from unittest.mock import patch, MagicMock, mock_open
            self.assertTrue(True)  # If we get here, imports worked
        except ImportError as e:
            self.fail(f"Mock import failed: {e}")

    def test_temp_file_creation(self):
        """Test temporary file creation."""
        import tempfile
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as temp_file:
            temp_file.write("test content")
            temp_file_path = temp_file.name
        
        try:
            # Verify file was created
            self.assertTrue(os.path.exists(temp_file_path))
            
            # Verify content
            with open(temp_file_path, 'r') as f:
                content = f.read()
                self.assertEqual(content, "test content")
        finally:
            # Clean up
            if os.path.exists(temp_file_path):
                os.unlink(temp_file_path)


if __name__ == '__main__':
    unittest.main() 