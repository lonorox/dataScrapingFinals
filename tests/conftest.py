"""
Pytest configuration and shared fixtures for the data scraping project tests.
"""

import pytest
import tempfile
import os
import sys
import json
import shutil
from pathlib import Path

# Add project root and src to path for imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "src"))

from tests.fixtures.test_data import SAMPLE_CONFIG, SAMPLE_ARTICLES


@pytest.fixture(scope="session")
def temp_test_dir():
    """Create a temporary directory for testing."""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture(scope="function")
def test_config_file(temp_test_dir):
    """Create a temporary config file for testing."""
    config_file = os.path.join(temp_test_dir, "test_config.json")
    with open(config_file, 'w') as f:
        json.dump(SAMPLE_CONFIG, f, indent=2)
    return config_file


@pytest.fixture(scope="function")
def test_data_dir(temp_test_dir):
    """Create a temporary data directory for testing."""
    data_dir = os.path.join(temp_test_dir, "data_output", "raw")
    os.makedirs(data_dir, exist_ok=True)
    return data_dir


@pytest.fixture(scope="function")
def test_processed_dir(temp_test_dir):
    """Create a temporary processed data directory for testing."""
    processed_dir = os.path.join(temp_test_dir, "data_output", "processed")
    os.makedirs(processed_dir, exist_ok=True)
    return processed_dir


@pytest.fixture(scope="function")
def sample_articles():
    """Provide sample articles for testing."""
    return SAMPLE_ARTICLES


@pytest.fixture(scope="function")
def sample_config():
    """Provide sample configuration for testing."""
    return SAMPLE_CONFIG


@pytest.fixture(scope="function")
def mock_logger():
    """Mock logger for testing."""
    import logging
    from unittest.mock import MagicMock
    
    mock_logger = MagicMock(spec=logging.Logger)
    return mock_logger


@pytest.fixture(scope="function")
def mock_database():
    """Mock database for testing."""
    from unittest.mock import MagicMock
    
    mock_db = MagicMock()
    mock_db.save_articles.return_value = 5
    mock_db.close.return_value = None
    return mock_db


@pytest.fixture(scope="function")
def test_worker_files(test_data_dir):
    """Create test worker files."""
    worker_files = []
    for i in range(3):
        worker_file = os.path.join(test_data_dir, f"worker_{i}_data.json")
        test_data = [{"title": f"Test Article {i}", "url": f"https://example.com/{i}"}]
        with open(worker_file, 'w') as f:
            json.dump(test_data, f, indent=2)
        worker_files.append(worker_file)
    return worker_files


@pytest.fixture(scope="function")
def test_summary_file(test_data_dir):
    """Create a test summary file."""
    summary_file = os.path.join(test_data_dir, "summary.csv")
    summary_data = [
        {"task_id": 0, "worker_id": 0, "source_type": "blog", "processing_time": 1.5, "success": True},
        {"task_id": 1, "worker_id": 1, "source_type": "news", "processing_time": 2.1, "success": True},
        {"task_id": 2, "worker_id": 2, "source_type": "rss", "processing_time": 1.8, "success": False}
    ]
    
    import csv
    with open(summary_file, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=summary_data[0].keys())
        writer.writeheader()
        writer.writerows(summary_data)
    
    return summary_file


@pytest.fixture(scope="function")
def mock_multiprocessing():
    """Mock multiprocessing components for testing."""
    from unittest.mock import MagicMock
    
    mock_queue = MagicMock()
    mock_queue.put.return_value = None
    mock_queue.get.return_value = None
    mock_queue.empty.return_value = True
    mock_queue.qsize.return_value = 0
    
    mock_manager = MagicMock()
    mock_dict = MagicMock()
    mock_manager.dict.return_value = mock_dict
    
    return {
        'queue': mock_queue,
        'manager': mock_manager,
        'dict': mock_dict
    }


@pytest.fixture(scope="function")
def mock_selenium():
    """Mock Selenium components for testing."""
    from unittest.mock import MagicMock
    
    mock_driver = MagicMock()
    mock_driver.get.return_value = None
    mock_driver.find_elements.return_value = []
    mock_driver.quit.return_value = None
    
    mock_webdriver = MagicMock()
    mock_webdriver.Chrome.return_value = mock_driver
    mock_webdriver.Firefox.return_value = mock_driver
    
    return {
        'driver': mock_driver,
        'webdriver': mock_webdriver
    }


@pytest.fixture(scope="function")
def mock_requests():
    """Mock requests for testing."""
    from unittest.mock import MagicMock
    
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.text = "<html><body>Test content</body></html>"
    mock_response.content = b"<html><body>Test content</body></html>"
    
    mock_session = MagicMock()
    mock_session.get.return_value = mock_response
    mock_session.post.return_value = mock_response
    
    return {
        'response': mock_response,
        'session': mock_session
    }


@pytest.fixture(scope="function")
def mock_scrapy():
    """Mock Scrapy components for testing."""
    from unittest.mock import MagicMock
    
    mock_spider = MagicMock()
    mock_spider.start_urls = ["https://example.com"]
    mock_spider.parse.return_value = []
    
    mock_crawler = MagicMock()
    mock_crawler.crawl.return_value = None
    
    return {
        'spider': mock_spider,
        'crawler': mock_crawler
    }


@pytest.fixture(scope="function")
def test_environment_variables():
    """Set up test environment variables."""
    original_env = os.environ.copy()
    
    # Set test environment variables
    os.environ['TEST_MODE'] = 'true'
    os.environ['LOG_LEVEL'] = 'DEBUG'
    
    yield os.environ
    
    # Restore original environment
    os.environ.clear()
    os.environ.update(original_env)


@pytest.fixture(scope="function")
def mock_file_system(temp_test_dir):
    """Mock file system operations for testing."""
    from unittest.mock import patch
    
    with patch('os.path.exists') as mock_exists, \
         patch('os.makedirs') as mock_makedirs, \
         patch('builtins.open', create=True) as mock_open:
        
        mock_exists.return_value = True
        mock_makedirs.return_value = None
        mock_open.return_value.__enter__.return_value = MagicMock()
        mock_open.return_value.__exit__.return_value = None
        
        yield {
            'exists': mock_exists,
            'makedirs': mock_makedirs,
            'open': mock_open
        }


# Pytest configuration
def pytest_configure(config):
    """Configure pytest."""
    config.addinivalue_line(
        "markers", "unit: mark test as a unit test"
    )
    config.addinivalue_line(
        "markers", "integration: mark test as an integration test"
    )
    config.addinivalue_line(
        "markers", "slow: mark test as slow running"
    )


def pytest_collection_modifyitems(config, items):
    """Modify test collection to add markers based on file location."""
    for item in items:
        # Add unit marker for tests in unit directory
        if "unit" in str(item.fspath):
            item.add_marker(pytest.mark.unit)
        
        # Add integration marker for tests in integration directory
        if "integration" in str(item.fspath):
            item.add_marker(pytest.mark.integration)
        
        # Add slow marker for tests that might be slow
        if any(keyword in str(item.fspath) for keyword in ["integration", "pipeline"]):
            item.add_marker(pytest.mark.slow) 