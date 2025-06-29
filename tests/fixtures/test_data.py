"""
Test data fixtures for the data scraping project.
Contains sample data for testing various components.
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Any

# Sample configuration for testing
SAMPLE_CONFIG = {
    "min_workers": 2,
    "max_workers": 5,
    "tasks": [
        {
            "priority": 1,
            "url": "",
            "type": "blog"
        },
        {
            "priority": 2,
            "url": "",
            "type": "rss",
            "search_word": "technology"
        },
        {
            "priority": 3,
            "url": "https://www.bbc.com/",
            "type": "news"
        }
    ],
    "userAgents": [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    ],
    "proxies": [
        "http://test-proxy:8080"
    ]
}

# Sample task data
SAMPLE_TASKS = [
    {
        "id": 0,
        "priority": 1,
        "url": "https://example.com/blog",
        "type": "blog",
        "search_word": None
    },
    {
        "id": 1,
        "priority": 2,
        "url": "https://example.com/rss",
        "type": "rss",
        "search_word": "technology"
    },
    {
        "id": 2,
        "priority": 3,
        "url": "https://example.com/news",
        "type": "news",
        "search_word": None
    }
]

# Sample scraped articles
SAMPLE_ARTICLES = [
    {
        "title": "Test Article 1",
        "url": "https://example.com/article1",
        "author": "John Doe",
        "publication_date_datetime": datetime.now().isoformat(),
        "publication_date_readable": "2024-01-01",
        "summary": "This is a test article summary",
        "content": "This is the full content of the test article",
        "tags": ["test", "technology"],
        "source_type": "blog",
        "source": "Example Blog",
        "headline": "Test Article 1",
        "link": "https://example.com/article1",
        "href": "https://example.com/article1",
        "scraped_at": datetime.now().isoformat(),
        "metadata": {"test": True}
    },
    {
        "title": "Test Article 2",
        "url": "https://example.com/article2",
        "author": "Jane Smith",
        "publication_date_datetime": datetime.now().isoformat(),
        "publication_date_readable": "2024-01-02",
        "summary": "Another test article summary",
        "content": "Another test article content",
        "tags": ["test", "news"],
        "source_type": "news",
        "source": "Example News",
        "headline": "Test Article 2",
        "link": "https://example.com/article2",
        "href": "https://example.com/article2",
        "scraped_at": datetime.now().isoformat(),
        "metadata": {"test": True}
    }
]

# Sample scraping results
SAMPLE_SCRAPING_RESULTS = [
    {
        "task_id": 0,
        "worker_name": "worker_0",
        "source_type": "blog",
        "data": SAMPLE_ARTICLES[:1],
        "success": True,
        "error_message": None,
        "scraped_at": datetime.now().timestamp(),
        "processing_time": 1.5,
        "errors": [],
        "metadata": {"worker_id": 0}
    },
    {
        "task_id": 1,
        "worker_name": "worker_1",
        "source_type": "rss",
        "data": SAMPLE_ARTICLES[1:],
        "success": True,
        "error_message": None,
        "scraped_at": datetime.now().timestamp(),
        "processing_time": 2.1,
        "errors": [],
        "metadata": {"worker_id": 1}
    }
]

# Sample failed scraping result
SAMPLE_FAILED_RESULT = {
    "task_id": 2,
    "worker_name": "worker_2",
    "source_type": "news",
    "data": [],
    "success": False,
    "error_message": "Connection timeout",
    "scraped_at": datetime.now().timestamp(),
    "processing_time": 5.0,
    "errors": ["Connection timeout", "Failed to parse content"],
    "metadata": {"worker_id": 2}
}

# Sample HTML content for testing scrapers
SAMPLE_HTML_CONTENT = """
<!DOCTYPE html>
<html>
<head>
    <title>Test News Site</title>
</head>
<body>
    <article>
        <h1>Test Article Title</h1>
        <p class="summary">This is a test article summary</p>
        <p class="content">This is the full content of the test article</p>
        <span class="author">John Doe</span>
        <time datetime="2024-01-01">January 1, 2024</time>
        <a href="https://example.com/article">Read more</a>
    </article>
    <article>
        <h1>Another Test Article</h1>
        <p class="summary">Another test article summary</p>
        <p class="content">Another test article content</p>
        <span class="author">Jane Smith</span>
        <time datetime="2024-01-02">January 2, 2024</time>
        <a href="https://example.com/article2">Read more</a>
    </article>
</body>
</html>
"""

# Sample RSS feed content
SAMPLE_RSS_CONTENT = """<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
    <channel>
        <title>Test RSS Feed</title>
        <link>https://example.com/rss</link>
        <description>Test RSS feed for testing</description>
        <item>
            <title>Test RSS Article 1</title>
            <link>https://example.com/rss/article1</link>
            <description>This is a test RSS article description</description>
            <pubDate>Mon, 01 Jan 2024 12:00:00 GMT</pubDate>
            <author>John Doe</author>
        </item>
        <item>
            <title>Test RSS Article 2</title>
            <link>https://example.com/rss/article2</link>
            <description>Another test RSS article description</description>
            <pubDate>Tue, 02 Jan 2024 12:00:00 GMT</pubDate>
            <author>Jane Smith</author>
        </item>
    </channel>
</rss>
"""

def create_temp_config_file(temp_dir: str) -> str:
    """Create a temporary config file for testing."""
    config_path = os.path.join(temp_dir, "test_config.json")
    with open(config_path, 'w') as f:
        json.dump(SAMPLE_CONFIG, f, indent=2)
    return config_path

def create_temp_data_files(temp_dir: str) -> List[str]:
    """Create temporary data files for testing."""
    files = []
    
    # Create blog data file
    blog_file = os.path.join(temp_dir, "blog_data.json")
    with open(blog_file, 'w') as f:
        json.dump(SAMPLE_ARTICLES[:1], f, indent=2)
    files.append(blog_file)
    
    # Create news data file
    news_file = os.path.join(temp_dir, "news_data.json")
    with open(news_file, 'w') as f:
        json.dump(SAMPLE_ARTICLES[1:], f, indent=2)
    files.append(news_file)
    
    # Create RSS data file
    rss_file = os.path.join(temp_dir, "rss_data.json")
    with open(rss_file, 'w') as f:
        json.dump(SAMPLE_ARTICLES, f, indent=2)
    files.append(rss_file)
    
    return files

def cleanup_temp_files(file_paths: List[str]):
    """Clean up temporary test files."""
    for file_path in file_paths:
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
        except Exception:
            pass 