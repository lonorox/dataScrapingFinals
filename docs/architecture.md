# Web Scraping System Architecture

## Overview

This document describes the architecture of the web scraping system, which is designed to efficiently scrape, process, and analyze data from various web sources including news sites, RSS feeds, and blogs.

## System Architecture

### High-Level Architecture

The system follows a **Master-Worker pattern** with **multiprocessing** for concurrent scraping operations. The architecture is modular and extensible, supporting multiple scraping strategies and data sources.

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   CLI Interface │    │   Configuration │    │   Data Storage  │
│                 │    │                 │    │                 │
│ • Interactive   │    │ • Task Config   │    │ • SQLite DB     │
│ • Command Line  │    │ • Worker Config │    │ • JSON Files    │
│ • Batch Mode    │    │ • Proxy Config  │    │ • CSV Reports   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
                    ┌─────────────────┐
                    │   Master Node   │
                    │                 │
                    │ • Task Queue    │
                    │ • Result Queue  │
                    │ • Worker Mgmt   │
                    │ • Stats Tracking│
                    └─────────────────┘
                                 │
                    ┌─────────────────┐
                    │   Worker Pool   │
                    │                 │
                    │ • Worker 1      │
                    │ • Worker 2      │
                    │ • Worker N      │
                    └─────────────────┘
                                 │
                    ┌─────────────────┐
                    │  Scraper Types  │
                    │                 │
                    │ • News Scraper  │
                    │ • RSS Scraper   │
                    │ • Blog Scraper  │
                    └─────────────────┘
```

## Core Components

### 1. Master Node (`src/scrapers/Master.py`)

The Master node orchestrates the entire scraping operation:

- **Task Management**: Distributes tasks to workers via a multiprocessing Queue
- **Worker Coordination**: Manages worker processes and monitors their status
- **Result Collection**: Aggregates results from all workers
- **Statistics Tracking**: Monitors performance metrics and success rates
- **Database Integration**: Manages data persistence

**Key Features:**
- Configurable worker pool (min/max workers)
- Automatic task distribution
- Result consolidation
- Performance monitoring
- Graceful shutdown handling

### 2. Worker Processes (`src/scrapers/Worker.py`)

Individual worker processes handle the actual scraping tasks:

- **Task Processing**: Executes assigned scraping tasks
- **Scraper Factory**: Creates appropriate scraper instances
- **Rate Limiting**: Implements request throttling
- **Error Handling**: Retry logic and error reporting
- **Data Output**: Saves scraped data to temporary files

**Key Features:**
- Automatic retry mechanism (3 attempts)
- Rate limiting (1 request/second)
- Dynamic scraper creation
- Worker status reporting
- Graceful error handling

### 3. Scraper Factory (`src/scrapers/ScraperFactory.py`)

Implements the **Factory Pattern** to create appropriate scraper instances:

```python
class ScraperFactory:
    @staticmethod
    def create_scraper(task_type: str, rate_limiter: RateLimiter = None, search_word: str = None) -> Scraper:
        if task_type == "news":
            return NewsScraper(rate_limiter)
        elif task_type == "rss":
            return seleniumRssScrapper(rate_limiter, headers, search_word)
        elif task_type == "blog":
            return BlogScrapy()
```

**Supported Scraper Types:**
- **News Scraper**: BBC, Fox News using Strategy pattern
- **RSS Scraper**: NPR RSS feeds using Selenium
- **Blog Scraper**: TechCrunch using Scrapy framework

### 4. Scraping Strategies (`src/scrapers/ScrapingStrategy.py`)

Implements the **Strategy Pattern** for different news sites:

```python
class ScrapingContext:
    def __init__(self, session: requests.Session):
        self._strategies = {
            'bbc.com': BBCScrapingStrategy(session),
            'foxnews.com': FoxNewsScrapingStrategy(session)
        }
```

**Benefits:**
- Easy to add new news sites
- Site-specific scraping logic
- Reusable scraping components
- Maintainable code structure

## Data Flow

### 1. Task Creation
```
Config File → Task Objects → Master Queue → Worker Assignment
```

### 2. Scraping Process
```
Worker → Scraper Factory → Strategy Selection → Data Extraction → Article Objects
```

### 3. Data Processing
```
Article Objects → JSON Serialization → File Storage → Database Persistence
```

### 4. Result Aggregation
```
Worker Results → Master Collection → Data Consolidation → Final Output
```

## Design Patterns Used

### 1. Factory Pattern
- **Purpose**: Create appropriate scraper instances based on task type
- **Implementation**: `ScraperFactory.create_scraper()`
- **Benefits**: Encapsulation, extensibility, type safety

### 2. Strategy Pattern
- **Purpose**: Handle different scraping strategies for various news sites
- **Implementation**: `ScrapingContext` with site-specific strategies
- **Benefits**: Easy to add new sites, maintainable code

### 3. Master-Worker Pattern
- **Purpose**: Distribute work across multiple processes
- **Implementation**: Master coordinates workers via queues
- **Benefits**: Scalability, fault tolerance, load balancing

### 4. Observer Pattern (Implicit)
- **Purpose**: Monitor worker status and progress
- **Implementation**: Worker status reporting via shared dictionaries
- **Benefits**: Real-time monitoring, error detection

## Data Models

### Core Data Structures

#### Article Model (`src/data/models.py`)
```python
@dataclass
class Article:
    title: str
    url: str
    author: Optional[str] = None
    publication_date_datetime: Optional[datetime] = None
    publication_date_readable: Optional[str] = None
    summary: Optional[str] = None
    content: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    source_type: str = "unknown"
    source: Optional[str] = None
    scraped_at: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
```

#### Task Model (`src/scrapers/Task.py`)
```python
@dataclass
class Task:
    id: int
    priority: int
    url: str
    type: str
    search_word: Optional[str] = None
```

#### Result Model (`src/scrapers/Task.py`)
```python
@dataclass
class Result:
    task_id: int
    worker_name: str
    source_type: str
    data: List[Dict[str, Any]] = field(default_factory=list)
    success: bool = True
    error_message: Optional[str] = None
    processing_time: Optional[float] = None
```

## Configuration Management

### Configuration File (`config.json`)
```json
{
  "min_workers": 2,
  "max_workers": 5,
  "tasks": [
    {
      "priority": 1,
      "url": "https://www.bbc.com/",
      "type": "news"
    }
  ],
  "userAgents": [...],
  "proxies": [...]
}
```

### Configuration Features
- **Worker Pool Configuration**: Min/max worker limits
- **Task Definition**: URL, type, priority, search terms
- **User Agent Rotation**: Multiple browser identities
- **Proxy Support**: HTTP proxy configuration
- **Rate Limiting**: Request throttling settings

## Error Handling & Resilience

### 1. Worker-Level Error Handling
- **Retry Logic**: 3 attempts per task
- **Graceful Degradation**: Continue processing other tasks
- **Error Reporting**: Detailed error messages and stack traces

### 2. Master-Level Error Handling
- **Worker Monitoring**: Detect and handle worker failures
- **Task Recovery**: Re-queue failed tasks
- **Resource Cleanup**: Proper cleanup of worker processes

### 3. Data Integrity
- **Transaction Safety**: Atomic database operations
- **File Locking**: Prevent concurrent file access issues
- **Data Validation**: Validate scraped data before storage

## Performance Considerations

### 1. Concurrency
- **Multiprocessing**: True parallel execution
- **Queue-based Communication**: Efficient inter-process communication
- **Worker Pool**: Configurable concurrency levels

### 2. Rate Limiting
- **Request Throttling**: Prevent overwhelming target sites
- **Configurable Limits**: Adjustable requests per second
- **Respectful Scraping**: Follow robots.txt and site policies

### 3. Resource Management
- **Memory Efficiency**: Stream data processing
- **File Management**: Automatic cleanup of temporary files
- **Database Optimization**: Efficient queries and indexing

## Security & Ethics

### 1. Respectful Scraping
- **Rate Limiting**: Prevent server overload
- **User Agent Rotation**: Avoid detection
- **Robots.txt Compliance**: Respect site policies

### 2. Data Privacy
- **Minimal Data Collection**: Only necessary information
- **Secure Storage**: Encrypted data storage
- **Access Control**: Proper file permissions

### 3. Legal Compliance
- **Terms of Service**: Respect website terms
- **Copyright**: Proper attribution and usage
- **Data Protection**: GDPR and privacy law compliance

## Extensibility

### Adding New Scrapers
1. Create new scraper class implementing `Scraper` interface
2. Add to `ScraperFactory.create_scraper()` method
3. Update configuration schema if needed
4. Add tests for new scraper

### Adding New Data Sources
1. Implement site-specific strategy
2. Add to `ScrapingContext` strategies
3. Update URL validation logic
4. Test with sample data

### Adding New Analysis Features
1. Extend analysis modules in `src/analysis/`
2. Add new report types
3. Update CLI commands
4. Add visualization options

## Monitoring & Observability

### 1. Logging
- **Structured Logging**: JSON-formatted logs
- **Log Levels**: DEBUG, INFO, WARNING, ERROR
- **Log Rotation**: Automatic log file management

### 2. Metrics
- **Performance Metrics**: Processing time, success rates
- **Resource Usage**: Memory, CPU utilization
- **Error Rates**: Failure tracking and analysis

### 3. Health Checks
- **Worker Status**: Real-time worker monitoring
- **Queue Status**: Task queue monitoring
- **Database Health**: Connection and query monitoring

## Deployment Considerations

### 1. Environment Setup
- **Python Environment**: Virtual environment management
- **Dependencies**: Requirements.txt and dependency management
- **Configuration**: Environment-specific configs

### 2. Resource Requirements
- **CPU**: Multi-core for parallel processing
- **Memory**: Sufficient RAM for data processing
- **Storage**: Adequate disk space for data and logs

### 3. Scalability
- **Horizontal Scaling**: Multiple master instances
- **Load Balancing**: Distribute tasks across instances
- **Data Partitioning**: Split data across multiple databases

## Future Enhancements

### 1. Advanced Features
- **Machine Learning**: Content classification and sentiment analysis
- **Real-time Processing**: Stream processing capabilities
- **API Integration**: RESTful API for external access

### 2. Performance Optimizations
- **Caching**: Redis-based caching layer
- **Async Processing**: Async/await for I/O operations
- **Database Optimization**: Advanced indexing and query optimization

### 3. Monitoring Enhancements
- **Dashboard**: Web-based monitoring interface
- **Alerting**: Automated alert system
- **Analytics**: Advanced performance analytics 