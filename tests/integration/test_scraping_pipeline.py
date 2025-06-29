"""
Integration tests for the complete scraping pipeline.
Tests end-to-end functionality of the scraping system.
"""

import unittest
import json
import tempfile
import os
import sys
import time
from pathlib import Path
from unittest.mock import patch, MagicMock
from multiprocessing import Queue, Manager
import queue

# Add project root and src to path for imports
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "src"))

from src.scrapers.Master import Master
from src.scrapers.Task import Task, Result
from src.utils.configs import generate_tasks
from tests.fixtures.test_data import SAMPLE_CONFIG, SAMPLE_ARTICLES


class TestScrapingPipeline(unittest.TestCase):
    """Integration tests for the complete scraping pipeline."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.config_file = os.path.join(self.temp_dir, "test_config.json")
        self.data_dir = os.path.join(self.temp_dir, "data_output", "raw")
        os.makedirs(self.data_dir, exist_ok=True)
        
        # Create test config file
        with open(self.config_file, 'w') as f:
            json.dump(SAMPLE_CONFIG, f, indent=2)

    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    @patch('builtins.open')
    def test_config_to_tasks_pipeline(self, mock_open):
        """Test the complete pipeline from config to task generation."""
        # Patch open to return the test config file
        mock_open.return_value.__enter__.return_value.read.return_value = json.dumps(SAMPLE_CONFIG)
        
        # Test task generation
        tasks = generate_tasks()
        
        self.assertIsInstance(tasks, list)
        self.assertEqual(len(tasks), len(SAMPLE_CONFIG["tasks"]))
        
        # Verify task structure
        for task in tasks:
            self.assertIn("priority", task)
            self.assertIn("url", task)
            self.assertIn("type", task)
            self.assertIsInstance(task["priority"], int)
            self.assertIsInstance(task["url"], str)
            self.assertIsInstance(task["type"], str)

    def test_task_to_result_pipeline(self):
        """Test the pipeline from Task objects to Result objects."""
        # Create tasks from config
        tasks = []
        for i, task_data in enumerate(SAMPLE_CONFIG["tasks"]):
            task = Task(
                id=i,
                priority=task_data["priority"],
                url=task_data["url"],
                type=task_data["type"],
                search_word=task_data.get("search_word")
            )
            tasks.append(task)
        
        # Verify task creation
        self.assertEqual(len(tasks), len(SAMPLE_CONFIG["tasks"]))
        
        # Create results from tasks
        results = []
        for task in tasks:
            result = Result(
                task_id=task.id,
                worker_name=f"worker_{task.id}",
                source_type=task.type,
                data=SAMPLE_ARTICLES[:1] if task.type == "blog" else SAMPLE_ARTICLES[1:],
                success=True,
                processing_time=1.5,
                metadata={"worker_id": task.id}
            )
            results.append(result)
        
        # Verify result creation
        self.assertEqual(len(results), len(tasks))
        for result in results:
            self.assertTrue(result.success)
            self.assertIsInstance(result.data, list)
            self.assertIsInstance(result.processing_time, float)

    @patch('src.scrapers.Master.Database')
    def test_master_initialization(self, mock_database_class):
        """Test Master class initialization and setup."""
        # Mock database
        mock_db = MagicMock()
        mock_database_class.return_value = mock_db
        
        # Create queues
        task_queue = Queue()
        result_queue = Queue()
        manager = Manager()
        worker_status = manager.dict()
        
        # Initialize Master
        master = Master(
            task_queue=task_queue,
            result_queue=result_queue,
            worker_status=worker_status,
            n=3
        )
        
        # Verify initialization
        self.assertEqual(master.workers, 3)
        self.assertEqual(master.number_of_Tasks, 0)
        self.assertEqual(master.completed_tasks, 0)
        self.assertEqual(master.stop, 0)
        self.assertIsInstance(master.results, list)
        self.assertIsInstance(master.worker_list, list)

    def test_task_queue_operations(self):
        """Test task queue operations in the pipeline."""
        task_queue = queue.Queue()
        result_queue = queue.Queue()
        manager = Manager()
        worker_status = manager.dict()
        
        # Create tasks
        tasks = []
        for i, task_data in enumerate(SAMPLE_CONFIG["tasks"]):
            task = Task(
                id=i,
                priority=task_data["priority"],
                url=task_data["url"],
                type=task_data["type"],
                search_word=task_data.get("search_word")
            )
            tasks.append(task)
        
        # Add tasks to queue
        for task in tasks:
            task_queue.put(task)
        
        # Instead of qsize, drain the queue and count
        retrieved_tasks = []
        while not task_queue.empty():
            retrieved_tasks.append(task_queue.get())
        self.assertEqual(len(retrieved_tasks), len(tasks))
        for i, task in enumerate(retrieved_tasks):
            self.assertEqual(task.id, i)
            self.assertEqual(task.type, SAMPLE_CONFIG["tasks"][i]["type"])

    def test_result_queue_operations(self):
        """Test result queue operations in the pipeline."""
        task_queue = queue.Queue()
        result_queue = queue.Queue()
        manager = Manager()
        worker_status = manager.dict()
        
        # Create results
        results = []
        for i, task_data in enumerate(SAMPLE_CONFIG["tasks"]):
            result = Result(
                task_id=i,
                worker_name=f"worker_{i}",
                source_type=task_data["type"],
                data=SAMPLE_ARTICLES[:1],
                success=True,
                processing_time=1.5,
                metadata={"worker_id": i}
            )
            results.append(result)
        
        # Add results to queue
        for result in results:
            result_queue.put(result)
        
        # Instead of qsize, drain the queue and count
        retrieved_results = []
        while not result_queue.empty():
            retrieved_results.append(result_queue.get())
        self.assertEqual(len(retrieved_results), len(results))
        for i, result in enumerate(retrieved_results):
            self.assertEqual(result.task_id, i)
            self.assertTrue(result.success)
            self.assertIsInstance(result.data, list)
            self.assertIsInstance(result.processing_time, float)

    @patch('src.scrapers.Master.Database')
    def test_master_task_management(self, mock_database_class):
        """Test Master task management functionality."""
        # Mock database
        mock_db = MagicMock()
        mock_database_class.return_value = mock_db
        
        # Create Master instance
        task_queue = Queue()
        result_queue = Queue()
        manager = Manager()
        worker_status = manager.dict()
        
        master = Master(
            task_queue=task_queue,
            result_queue=result_queue,
            worker_status=worker_status
        )
        
        # Create tasks
        tasks = []
        for i, task_data in enumerate(SAMPLE_CONFIG["tasks"]):
            task = Task(
                id=i,
                priority=task_data["priority"],
                url=task_data["url"],
                type=task_data["type"],
                search_word=task_data.get("search_word")
            )
            tasks.append(task)
        
        # Add tasks to master
        master.add_tasks(tasks)
        
        # Instead of qsize, drain the queue and count
        retrieved_tasks = []
        while not task_queue.empty():
            retrieved_tasks.append(task_queue.get())
        self.assertEqual(master.number_of_Tasks, len(tasks))
        self.assertEqual(len(retrieved_tasks), len(tasks))

    def test_data_consolidation_pipeline(self):
        """Test data consolidation pipeline."""
        # Create sample results with different data types
        results = []
        
        # Blog result
        blog_result = Result(
            task_id=0,
            worker_name="worker_0",
            source_type="blog",
            data=SAMPLE_ARTICLES[:1],
            success=True,
            processing_time=1.5
        )
        results.append(blog_result)
        
        # News result
        news_result = Result(
            task_id=1,
            worker_name="worker_1",
            source_type="news",
            data=SAMPLE_ARTICLES[1:],
            success=True,
            processing_time=2.1
        )
        results.append(news_result)
        
        # RSS result
        rss_result = Result(
            task_id=2,
            worker_name="worker_2",
            source_type="rss",
            data=SAMPLE_ARTICLES,
            success=True,
            processing_time=1.8
        )
        results.append(rss_result)
        
        # Verify results
        self.assertEqual(len(results), 3)
        
        # Check data distribution
        total_articles = sum(len(result.data) for result in results)
        self.assertEqual(total_articles, 4)  # 1 + 1 + 2
        
        # Check success rates
        successful_results = [r for r in results if r.success]
        self.assertEqual(len(successful_results), 3)
        
        # Check processing times
        total_time = sum(r.processing_time for r in results)
        self.assertGreater(total_time, 0)

    def test_error_handling_pipeline(self):
        """Test error handling in the pipeline."""
        # Create results with mixed success/failure
        results = []
        
        # Successful result
        success_result = Result(
            task_id=0,
            worker_name="worker_0",
            source_type="blog",
            data=SAMPLE_ARTICLES[:1],
            success=True,
            processing_time=1.5
        )
        results.append(success_result)
        
        # Failed result
        failed_result = Result(
            task_id=1,
            worker_name="worker_1",
            source_type="news",
            data=[],
            success=False,
            error_message="Connection timeout",
            processing_time=5.0,
            errors=["Connection timeout", "Failed to parse content"]
        )
        results.append(failed_result)
        
        # Verify error handling
        successful_results = [r for r in results if r.success]
        failed_results = [r for r in results if not r.success]
        
        self.assertEqual(len(successful_results), 1)
        self.assertEqual(len(failed_results), 1)
        
        # Check error details
        failed_result = failed_results[0]
        self.assertFalse(failed_result.success)
        self.assertEqual(len(failed_result.errors), 2)
        self.assertIn("Connection timeout", failed_result.errors)

    def test_worker_status_management(self):
        """Test worker status management in the pipeline."""
        manager = Manager()
        worker_status = manager.dict()
        
        # Simulate worker status updates
        worker_status["worker_0"] = "running"
        worker_status["worker_1"] = "idle"
        worker_status["worker_2"] = "completed"
        
        # Verify worker status
        self.assertEqual(worker_status["worker_0"], "running")
        self.assertEqual(worker_status["worker_1"], "idle")
        self.assertEqual(worker_status["worker_2"], "completed")
        
        # Update worker status
        worker_status["worker_0"] = "completed"
        worker_status["worker_1"] = "running"
        
        # Verify updated status
        self.assertEqual(worker_status["worker_0"], "completed")
        self.assertEqual(worker_status["worker_1"], "running")

    def test_data_export_pipeline(self):
        """Test data export functionality in the pipeline."""
        # Create sample results
        results = []
        for i, task_data in enumerate(SAMPLE_CONFIG["tasks"]):
            result = Result(
                task_id=i,
                worker_name=f"worker_{i}",
                source_type=task_data["type"],
                data=SAMPLE_ARTICLES[:1],
                success=True,
                processing_time=1.5 + i * 0.1,
                metadata={"worker_id": i}
            )
            results.append(result)
        
        # Calculate summary statistics
        total_results = len(results)
        successful_results = sum(1 for r in results if r.success)
        failed_results = total_results - successful_results
        success_rate = (successful_results / total_results) * 100 if total_results > 0 else 0
        avg_time = sum(r.processing_time for r in results) / total_results if total_results > 0 else 0
        
        # Verify summary calculations
        self.assertEqual(total_results, len(SAMPLE_CONFIG["tasks"]))
        self.assertEqual(successful_results, len(SAMPLE_CONFIG["tasks"]))
        self.assertEqual(failed_results, 0)
        self.assertEqual(success_rate, 100.0)
        self.assertGreater(avg_time, 0)

    def test_configuration_validation_pipeline(self):
        """Test configuration validation throughout the pipeline."""
        # Test valid configuration
        valid_config = SAMPLE_CONFIG.copy()
        
        # Validate required fields
        self.assertIn("min_workers", valid_config)
        self.assertIn("max_workers", valid_config)
        self.assertIn("tasks", valid_config)
        self.assertIn("userAgents", valid_config)
        self.assertIn("proxies", valid_config)
        
        # Validate worker configuration
        self.assertGreater(valid_config["min_workers"], 0)
        self.assertGreaterEqual(valid_config["max_workers"], valid_config["min_workers"])
        
        # Validate tasks
        for task in valid_config["tasks"]:
            self.assertIn("priority", task)
            self.assertIn("url", task)
            self.assertIn("type", task)
            self.assertGreaterEqual(task["priority"], 1)
            self.assertLessEqual(task["priority"], 10)
            self.assertIn(task["type"], ["news", "rss", "blog"])

    def test_performance_monitoring_pipeline(self):
        """Test performance monitoring in the pipeline."""
        # Create results with different performance characteristics
        results = []
        
        # Fast result
        fast_result = Result(
            task_id=0,
            worker_name="worker_0",
            source_type="blog",
            data=SAMPLE_ARTICLES[:1],
            success=True,
            processing_time=0.5
        )
        results.append(fast_result)
        
        # Medium result
        medium_result = Result(
            task_id=1,
            worker_name="worker_1",
            source_type="news",
            data=SAMPLE_ARTICLES[1:],
            success=True,
            processing_time=2.0
        )
        results.append(medium_result)
        
        # Slow result
        slow_result = Result(
            task_id=2,
            worker_name="worker_2",
            source_type="rss",
            data=SAMPLE_ARTICLES,
            success=True,
            processing_time=5.0
        )
        results.append(slow_result)
        
        # Calculate performance metrics
        total_time = sum(r.processing_time for r in results)
        avg_time = total_time / len(results)
        min_time = min(r.processing_time for r in results)
        max_time = max(r.processing_time for r in results)
        
        # Verify performance metrics
        self.assertEqual(total_time, 7.5)
        self.assertEqual(avg_time, 2.5)
        self.assertEqual(min_time, 0.5)
        self.assertEqual(max_time, 5.0)


if __name__ == '__main__':
    unittest.main() 