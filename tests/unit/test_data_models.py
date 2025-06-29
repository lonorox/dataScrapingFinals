"""
Unit tests for the data models.
Tests Article, ScrapingResult, ScrapingStats, and ScrapingTask models.
"""

import unittest
import sys
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, Any

# Add project root and src to path for imports
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "src"))

from src.data.models import Article, ScrapingResult, ScrapingStats, ScrapingTask
from tests.fixtures.test_data import SAMPLE_ARTICLES


class TestArticle(unittest.TestCase):
    """Test cases for the Article model."""

    def setUp(self):
        """Set up test fixtures."""
        self.sample_article_data = SAMPLE_ARTICLES[0]

    def test_article_with_minimal_data(self):
        """Test article creation with minimal required data."""
        article = Article(
            title="Test Article",
            url="https://example.com/article",
            source_type="blog"
        )

        self.assertEqual(article.title, "Test Article")
        self.assertEqual(article.url, "https://example.com/article")
        self.assertEqual(article.source_type, "blog")
        self.assertIsNone(article.author)
        self.assertIsNone(article.publication_date_datetime)
        self.assertIsNone(article.publication_date_readable)
        self.assertIsNone(article.summary)
        self.assertIsNone(article.content)
        self.assertEqual(article.tags, [])
        self.assertIsNone(article.source)
        self.assertIsNone(article.headline)
        self.assertIsNone(article.link)
        self.assertIsNone(article.href)
        self.assertIsNone(article.scraped_at)
        self.assertEqual(article.metadata, {})

    def test_article_to_dict(self):
        """Test converting article to dictionary."""
        article = Article(
            title="Test Article",
            url="https://example.com/article",
            author="John Doe",
            summary="Test summary",
            content="Test content",
            tags=["test", "technology"],
            source_type="blog",
            source="Test Blog",
            metadata={"test": True}
        )

        article_dict = article.to_dict()

        self.assertIsInstance(article_dict, dict)
        self.assertEqual(article_dict["title"], "Test Article")
        self.assertEqual(article_dict["url"], "https://example.com/article")
        self.assertEqual(article_dict["author"], "John Doe")
        self.assertEqual(article_dict["summary"], "Test summary")
        self.assertEqual(article_dict["content"], "Test content")
        self.assertEqual(article_dict["tags"], ["test", "technology"])
        self.assertEqual(article_dict["source_type"], "blog")
        self.assertEqual(article_dict["source"], "Test Blog")
        self.assertEqual(article_dict["metadata"], {"test": True})

    def test_article_from_dict(self):
        """Test creating article from dictionary."""
        article_data = {
            "title": "Test Article",
            "url": "https://example.com/article",
            "author": "John Doe",
            "summary": "Test summary",
            "content": "Test content",
            "tags": ["test", "technology"],
            "source_type": "blog",
            "source": "Test Blog",
            "metadata": {"test": True}
        }

        article = Article.from_dict(article_data)

        self.assertEqual(article.title, article_data["title"])
        self.assertEqual(article.url, article_data["url"])
        self.assertEqual(article.author, article_data["author"])
        self.assertEqual(article.summary, article_data["summary"])
        self.assertEqual(article.content, article_data["content"])
        self.assertEqual(article.tags, article_data["tags"])
        self.assertEqual(article.source_type, article_data["source_type"])
        self.assertEqual(article.source, article_data["source"])
        self.assertEqual(article.metadata, article_data["metadata"])


class TestScrapingResult(unittest.TestCase):
    """Test cases for the ScrapingResult model."""

    def test_scraping_result_creation(self):
        """Test basic scraping result creation."""
        result = ScrapingResult(
            success=True,
            articles=[Article(title="Test", url="https://example.com", source_type="blog")],
            errors=[],
            metadata={"worker_id": 1, "processing_time": 2.5}
        )

        self.assertTrue(result.success)
        self.assertEqual(len(result.articles), 1)
        self.assertEqual(result.errors, [])
        self.assertEqual(result.metadata["worker_id"], 1)
        self.assertEqual(result.metadata["processing_time"], 2.5)

    def test_failed_scraping_result(self):
        """Test failed scraping result creation."""
        result = ScrapingResult(
            success=False,
            articles=[],
            errors=["Connection timeout", "Failed to parse content"],
            metadata={"worker_id": 1, "error_message": "Connection timeout"}
        )

        self.assertFalse(result.success)
        self.assertEqual(len(result.articles), 0)
        self.assertEqual(len(result.errors), 2)
        self.assertIn("Connection timeout", result.errors)
        self.assertIn("Failed to parse content", result.errors)


class TestScrapingStats(unittest.TestCase):
    """Test cases for the ScrapingStats model."""

    def test_scraping_task_to_dict(self):
        """Test converting scraping task to dictionary."""
        task = ScrapingTask(
            id="task_1",
            url="https://example.com",
            source_type="blog",
            priority=2,
            search_word="technology",
            metadata={"created_at": "2024-01-01"}
        )

        task_dict = task.to_dict()

        self.assertIsInstance(task_dict, dict)
        self.assertEqual(task_dict["id"], "task_1")
        self.assertEqual(task_dict["url"], "https://example.com")
        self.assertEqual(task_dict["source_type"], "blog")
        self.assertEqual(task_dict["priority"], 2)
        self.assertEqual(task_dict["search_word"], "technology")
        self.assertEqual(task_dict["metadata"]["created_at"], "2024-01-01")


class TestScrapingTask(unittest.TestCase):
    """Test cases for the ScrapingTask model."""

    def test_scraping_task_creation(self):
        """Test basic scraping task creation."""
        task = ScrapingTask(
            id="task_1",
            url="https://example.com",
            source_type="blog",
            priority=1,
            search_word="technology",
            metadata={"created_at": "2024-01-01"}
        )

        self.assertEqual(task.id, "task_1")
        self.assertEqual(task.url, "https://example.com")
        self.assertEqual(task.source_type, "blog")
        self.assertEqual(task.priority, 1)
        self.assertEqual(task.search_word, "technology")
        self.assertEqual(task.metadata["created_at"], "2024-01-01")

    def test_scraping_task_with_minimal_data(self):
        """Test scraping task creation with minimal data."""
        task = ScrapingTask(
            id="task_1",
            url="https://example.com",
            source_type="blog"
        )

        self.assertEqual(task.id, "task_1")
        self.assertEqual(task.url, "https://example.com")
        self.assertEqual(task.source_type, "blog")
        self.assertEqual(task.priority, 1)  # Default priority
        self.assertIsNone(task.search_word)
        self.assertEqual(task.metadata, {})

    def test_scraping_task_to_dict(self):
        """Test converting scraping task to dictionary."""
        task = ScrapingTask(
            id="task_1",
            url="https://example.com",
            source_type="blog",
            priority=2,
            search_word="technology",
            metadata={"created_at": "2024-01-01"}
        )

        task_dict = task.to_dict()

        self.assertIsInstance(task_dict, dict)
        self.assertEqual(task_dict["id"], "task_1")
        self.assertEqual(task_dict["url"], "https://example.com")
        self.assertEqual(task_dict["source_type"], "blog")
        self.assertEqual(task_dict["priority"], 2)
        self.assertEqual(task_dict["search_word"], "technology")
        self.assertEqual(task_dict["metadata"]["created_at"], "2024-01-01")


if __name__ == '__main__':
    unittest.main() 