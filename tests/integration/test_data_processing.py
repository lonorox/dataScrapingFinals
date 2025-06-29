"""
Integration tests for data processing and analysis components.
Tests data flow, transformations, and analysis pipeline.
"""

import unittest
import json
import tempfile
import os
import sys
import pandas as pd
from pathlib import Path
from unittest.mock import patch, MagicMock
from datetime import datetime

# Add project root and src to path for imports
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "src"))

from src.data.processors import data_output_manager, consolidate_worker_data, save_consolidated_data, cleanup_worker_files
from src.data.models import Article, ScrapingResult, ScrapingStats
from tests.fixtures.test_data import SAMPLE_ARTICLES, SAMPLE_SCRAPING_RESULTS


class TestDataProcessingPipeline(unittest.TestCase):
    """Integration tests for data processing pipeline."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.data_dir = os.path.join(self.temp_dir, "data_output", "raw")
        self.processed_dir = os.path.join(self.temp_dir, "data_output", "processed")
        os.makedirs(self.data_dir, exist_ok=True)
        os.makedirs(self.processed_dir, exist_ok=True)

    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_data_output_manager_initialization(self):
        """Test data output manager initialization."""
        # Test that data output manager can be accessed
        self.assertIsNotNone(data_output_manager)
        
        # Test basic functionality
        self.assertTrue(hasattr(data_output_manager, 'save_summary_csv'))
        self.assertTrue(hasattr(data_output_manager, 'save_articles_json'))

    def test_article_creation_and_serialization(self):
        """Test article creation and serialization pipeline."""
        # Create articles from sample data
        articles = []
        for article_data in SAMPLE_ARTICLES:
            article = Article(
                title=article_data["title"],
                url=article_data["url"],
                author=article_data["author"],
                publication_date_datetime=article_data["publication_date_datetime"],
                publication_date_readable=article_data["publication_date_readable"],
                summary=article_data["summary"],
                tags=article_data["tags"],
                source_type=article_data["source_type"],
                source=article_data["source"],
                scraped_at=article_data["scraped_at"],
                metadata=article_data["metadata"]
            )
            articles.append(article)
        
        # Verify article creation
        self.assertEqual(len(articles), len(SAMPLE_ARTICLES))
        
        # Test serialization
        for article in articles:
            article_dict = article.to_dict()
            self.assertIsInstance(article_dict, dict)
            self.assertEqual(article_dict["title"], article.title)
            self.assertEqual(article_dict["url"], article.url)
            self.assertEqual(article_dict["source_type"], article.source_type)

    def test_scraping_result_creation_and_processing(self):
        """Test scraping result creation and processing pipeline."""
        # Create scraping results
        results = []
        for result_data in SAMPLE_SCRAPING_RESULTS:
            result = ScrapingResult(
                success=result_data["success"],
                articles=[Article.from_dict(article) for article in result_data["data"]],
                errors=result_data["errors"],
                metadata=result_data["metadata"]
            )
            results.append(result)
        
        # Verify result creation
        self.assertEqual(len(results), len(SAMPLE_SCRAPING_RESULTS))
        
        # Test result processing
        for result in results:
            self.assertTrue(result.success)
            self.assertIsInstance(result.articles, list)
            self.assertIsInstance(result.errors, list)
            self.assertIsInstance(result.metadata, dict)

    def test_data_consolidation_pipeline(self):
        """Test data consolidation pipeline."""
        # Create test worker files
        worker_files = []
        for i, result_data in enumerate(SAMPLE_SCRAPING_RESULTS):
            worker_file = os.path.join(self.data_dir, f"worker_{i}_data.json")
            with open(worker_file, 'w') as f:
                json.dump(result_data["data"], f, indent=2)
            worker_files.append(worker_file)
        
        # Test consolidation
        consolidated_data = consolidate_worker_data(self.data_dir)
        
        # Verify consolidation
        self.assertIsInstance(consolidated_data, dict)
        self.assertIn("blog", consolidated_data)
        self.assertIn("news", consolidated_data)
        self.assertIn("rss", consolidated_data)
        
        # Check data counts
        total_articles = sum(len(articles) for articles in consolidated_data.values())
        expected_total = sum(len(result_data["data"]) for result_data in SAMPLE_SCRAPING_RESULTS)
        self.assertEqual(total_articles, expected_total)

    def test_data_saving_pipeline(self):
        """Test data saving pipeline."""
        # Create test data
        test_data = {
            "blog": SAMPLE_ARTICLES[:1],
            "news": SAMPLE_ARTICLES[1:],
            "rss": SAMPLE_ARTICLES
        }
        
        # Save consolidated data
        success = save_consolidated_data(test_data, self.data_dir)
        
        # Verify success
        self.assertTrue(success)

    def test_worker_file_cleanup(self):
        """Test worker file cleanup pipeline."""
        # Create test worker files
        worker_files = []
        for i in range(3):
            worker_file = os.path.join(self.data_dir, f"worker_{i}_data.json")
            with open(worker_file, 'w') as f:
                json.dump([{"test": f"data_{i}"}], f)
            worker_files.append(worker_file)
        
        # Verify files exist
        for file_path in worker_files:
            self.assertTrue(os.path.exists(file_path))
        
        # Test cleanup
        success = cleanup_worker_files(self.data_dir)
        
        # Verify cleanup
        self.assertTrue(success)
        for file_path in worker_files:
            self.assertFalse(os.path.exists(file_path))

    def test_data_analysis_pipeline(self):
        """Test data analysis pipeline."""
        # Create test data for analysis
        articles = []
        for article_data in SAMPLE_ARTICLES:
            article = Article.from_dict(article_data)
            articles.append(article)
        
        # Create DataFrame for analysis
        df_data = []
        for article in articles:
            df_data.append({
                'title': article.title,
                'url': article.url,
                'author': article.author,
                'source_type': article.source_type,
                'source': article.source,
                'tags': ','.join(article.tags) if article.tags else '',
                'scraped_at': article.scraped_at
            })
        
        df = pd.DataFrame(df_data)
        
        # Perform basic analysis
        source_counts = df['source_type'].value_counts()
        author_counts = df['author'].value_counts()
        total_articles = len(df)
        
        # Verify analysis results
        self.assertEqual(total_articles, len(SAMPLE_ARTICLES))
        self.assertIn('blog', source_counts.index)
        self.assertIn('news', source_counts.index)
        self.assertGreater(len(author_counts), 0)

    def test_error_handling_in_data_processing(self):
        """Test error handling in data processing pipeline."""
        # Test with invalid data
        invalid_data = {
            "blog": [{"invalid": "data"}],
            "news": None,
            "rss": []
        }
        
        # Test data validation
        for source_type, data in invalid_data.items():
            if data is None:
                continue
            
            # Test article creation with invalid data
            for item in data:
                try:
                    article = Article.from_dict(item)
                    # If no exception, verify basic fields
                    self.assertIsInstance(article.title, str)
                    self.assertIsInstance(article.url, str)
                except Exception as e:
                    # Expected for invalid data
                    self.assertIsInstance(e, (ValueError, TypeError, KeyError))

    def test_data_transformation_pipeline(self):
        """Test data transformation pipeline."""
        # Create articles with different formats
        articles = []
        for article_data in SAMPLE_ARTICLES:
            article = Article.from_dict(article_data)
            articles.append(article)
        
        # Transform to different formats
        json_data = [article.to_dict() for article in articles]
        csv_data = []
        for article in articles:
            csv_data.append({
                'title': article.title,
                'url': article.url,
                'author': article.author or '',
                'source_type': article.source_type,
                'summary': article.summary or '',
                'tags': ','.join(article.tags) if article.tags else ''
            })
        
        # Verify transformations
        self.assertEqual(len(json_data), len(articles))
        self.assertEqual(len(csv_data), len(articles))
        
        # Check data integrity
        for i, article in enumerate(articles):
            self.assertEqual(json_data[i]["title"], article.title)
            self.assertEqual(csv_data[i]["title"], article.title)

    def test_performance_metrics_calculation(self):
        """Test performance metrics calculation pipeline."""
        # Create scraping results with performance data
        results = []
        for i, result_data in enumerate(SAMPLE_SCRAPING_RESULTS):
            result = ScrapingResult(
                success=result_data["success"],
                articles=[Article.from_dict(article) for article in result_data["data"]],
                errors=result_data["errors"],
                metadata={
                    **result_data["metadata"],
                    "processing_time": 1.5 + i * 0.5,
                    "worker_id": i
                }
            )
            results.append(result)
        
        # Calculate performance metrics
        total_results = len(results)
        successful_results = sum(1 for r in results if r.success)
        failed_results = total_results - successful_results
        success_rate = (successful_results / total_results) * 100 if total_results > 0 else 0
        
        processing_times = [r.metadata.get("processing_time", 0) for r in results]
        avg_processing_time = sum(processing_times) / len(processing_times) if processing_times else 0
        total_processing_time = sum(processing_times)
        
        # Verify metrics
        self.assertEqual(total_results, len(SAMPLE_SCRAPING_RESULTS))
        self.assertEqual(successful_results, len(SAMPLE_SCRAPING_RESULTS))
        self.assertEqual(failed_results, 0)
        self.assertEqual(success_rate, 100.0)
        self.assertGreater(avg_processing_time, 0)
        self.assertGreater(total_processing_time, 0)

    def test_data_quality_validation(self):
        """Test data quality validation pipeline."""
        # Create articles with varying quality
        articles = []
        for article_data in SAMPLE_ARTICLES:
            article = Article.from_dict(article_data)
            articles.append(article)
        
        # Validate data quality
        quality_metrics = {
            'total_articles': len(articles),
            'articles_with_title': sum(1 for a in articles if a.title and a.title.strip()),
            'articles_with_url': sum(1 for a in articles if a.url and a.url.startswith('http')),
            'articles_with_author': sum(1 for a in articles if a.author),
            'articles_with_summary': sum(1 for a in articles if a.summary),
            'articles_with_tags': sum(1 for a in articles if a.tags)
        }
        
        # Calculate quality scores
        title_quality = quality_metrics['articles_with_title'] / quality_metrics['total_articles']
        url_quality = quality_metrics['articles_with_url'] / quality_metrics['total_articles']
        author_quality = quality_metrics['articles_with_author'] / quality_metrics['total_articles']
        
        # Verify quality metrics
        self.assertEqual(quality_metrics['total_articles'], len(SAMPLE_ARTICLES))
        self.assertGreaterEqual(title_quality, 0.0)
        self.assertLessEqual(title_quality, 1.0)
        self.assertGreaterEqual(url_quality, 0.0)
        self.assertLessEqual(url_quality, 1.0)
        self.assertGreaterEqual(author_quality, 0.0)
        self.assertLessEqual(author_quality, 1.0)

    def test_data_export_formats(self):
        """Test data export in different formats."""
        # Create test data
        articles = [Article.from_dict(article_data) for article_data in SAMPLE_ARTICLES]
        
        # Export to JSON
        json_file = os.path.join(self.temp_dir, "test_export.json")
        with open(json_file, 'w') as f:
            json.dump([article.to_dict() for article in articles], f, indent=2)
        
        # Export to CSV
        csv_file = os.path.join(self.temp_dir, "test_export.csv")
        df_data = []
        for article in articles:
            df_data.append({
                'title': article.title,
                'url': article.url,
                'author': article.author or '',
                'source_type': article.source_type,
                'summary': article.summary or '',
                'tags': ','.join(article.tags) if article.tags else ''
            })
        df = pd.DataFrame(df_data)
        df.to_csv(csv_file, index=False)
        
        # Verify exports
        self.assertTrue(os.path.exists(json_file))
        self.assertTrue(os.path.exists(csv_file))
        
        # Verify JSON content
        with open(json_file, 'r') as f:
            json_data = json.load(f)
            self.assertEqual(len(json_data), len(articles))
        
        # Verify CSV content
        csv_df = pd.read_csv(csv_file)
        self.assertEqual(len(csv_df), len(articles))


if __name__ == '__main__':
    unittest.main() 