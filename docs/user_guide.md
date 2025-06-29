# Web Scraping System User Guide

## Table of Contents

1. [Installation](#installation)
2. [Quick Start](#quick-start)
3. [Configuration](#configuration)
4. [Usage](#usage)
5. [Data Sources](#data-sources)
6. [Reports & Analytics](#reports--analytics)
7. [Troubleshooting](#troubleshooting)
8. [Advanced Features](#advanced-features)

## Installation

### Prerequisites

- Python 3.8 or higher
- pip (Python package installer)

### Step 1: Navigate to Project Directory

```bash
cd dataScrapingFinals
```

### Step 2: Create Virtual Environment

```bash
python -m venv venv

# On Windows
venv\Scripts\activate

# On macOS/Linux
source venv/bin/activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Verify Installation

```bash
python main.py --help
```

You should see the CLI help message indicating successful installation.

## Quick Start

### 1. Basic Configuration

The system comes with a default `config.json` file. You can start with the default settings or customize them:

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
  ]
}
```

### 2. Run Your First Scraping Task

```bash
# Interactive mode
python main.py

# Or run all tasks automatically
python main.py --auto

# Or run specific type
python main.py --type news
```

### 3. View Results

After scraping completes, check the `data_output/` directory for your results:

```bash
ls data_output/raw/
ls data_output/processed/
ls data_output/reports/
```

## Configuration

### Configuration File Structure

The `config.json` file controls all aspects of the scraping system:

```json
{
  "min_workers": 2,
  "max_workers": 5,
  "tasks": [
    {
      "priority": 1,
      "url": "https://www.bbc.com/",
      "type": "news"
    },
    {
      "priority": 2,
      "url": "",
      "type": "rss",
      "search_word": "technology"
    }
  ],
  "userAgents": [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36..."
  ],
  "proxies": [
    "http://proxy1:port",
    "http://proxy2:port"
  ]
}
```

### Configuration Options

#### Worker Configuration
- **min_workers**: Minimum number of worker processes (default: 2)
- **max_workers**: Maximum number of worker processes (default: 5)

#### Task Configuration
- **priority**: Task priority (1-10, higher = more important)
- **url**: Target URL to scrape
- **type**: Scraper type ("news", "rss", "blog")
- **search_word**: Search term for RSS scraping (optional)

#### Network Configuration
- **userAgents**: List of user agent strings for rotation
- **proxies**: List of HTTP proxy servers

### Adding New Tasks

You can add new scraping tasks through the CLI or by editing the config file directly:

#### Via CLI
```bash
python main.py
# Select "Configure Settings" → "Edit Tasks" → "Add new task"
```

#### Via Config File
```json
{
  "priority": 3,
  "url": "https://www.example.com/",
  "type": "news"
}
```

## Usage

### Interactive Mode

The interactive mode provides a user-friendly menu system:

```bash
python main.py
```

**Main Menu Options:**
1. 🚀 Start Scraping
2. ⚙️ Configure Settings
3. 📊 View Reports & Analytics
4. 🧪 Run Tests
5. 📁 Manage Data
6. 🔧 System Status
7. 📋 View Tasks
8. ❌ Exit

### Command Line Mode

For automation and scripting, use command line arguments:

```bash
# Run all tasks
python main.py --auto

# Run specific type
python main.py --type news
python main.py --type rss
python main.py --type blog

# Generate report
python main.py --report

# Use custom config
python main.py --config my_config.json
```

### Scraping Options

#### 1. Run All Tasks
Scrapes all configured sources simultaneously:
```bash
python main.py --auto
```

#### 2. Run by Type
Scrape specific content types:

**News Scraping:**
```bash
python main.py --type news
```
- Supports: BBC News, Fox News
- Uses: Strategy pattern for site-specific scraping
- Output: Structured article data

**RSS Scraping:**
```bash
python main.py --type rss
```
- Supports: NPR RSS feeds
- Uses: Selenium for dynamic content
- Features: Search word filtering

**Blog Scraping:**
```bash
python main.py --type blog
```
- Supports: TechCrunch
- Uses: Scrapy framework
- Output: Blog post data

#### 3. Custom Selection
Choose specific tasks to run:
```bash
python main.py
# Select "Custom Selection" and choose task numbers
```

## Data Sources

### Supported Sources

#### News Sources
- **BBC News** (`bbc.com`)
  - Content: Latest news articles
  - Categories: Politics, Technology, Sports, etc.
  - Data: Title, summary, URL, tags, publication date

- **Fox News** (`foxnews.com`)
  - Content: News articles and headlines
  - Categories: Politics, World, Technology, etc.
  - Data: Title, summary, URL, tags, author

#### RSS Sources
- **NPR** (`npr.org`)
  - Content: RSS feed articles
  - Features: Search word filtering
  - Data: Title, summary, URL, author, tags

#### Blog Sources
- **TechCrunch** (`techcrunch.com`)
  - Content: Technology blog posts
  - Data: Title, content, author, publication date, tags

### Adding Custom Sources

To add a new data source:

1. **Create Scraper Strategy** (for news sites):
```python
class CustomSiteStrategy(ScrapingStrategy):
    def scrape(self, url: str) -> list:
        # Implement scraping logic
        pass
    
    def get_site_name(self) -> str:
        return "Custom Site"
```

2. **Add to ScrapingContext**:
```python
self._strategies['customsite.com'] = CustomSiteStrategy(session)
```

3. **Update Configuration**:
```json
{
  "priority": 1,
  "url": "https://www.customsite.com/",
  "type": "news"
}
```

## Reports & Analytics

### Available Reports

#### 1. Data Overview
View summary of scraped data:
```bash
python main.py
# Select "View Reports & Analytics" → "Data Overview"
```

#### 2. Performance Analytics
Monitor scraping performance:
```bash
python main.py
# Select "View Reports & Analytics" → "Performance Analytics"
```

#### 3. Task Summary
View task configuration and status:
```bash
python main.py
# Select "View Reports & Analytics" → "Task Summary"
```

#### 4. HTML Report
Generate comprehensive HTML report:
```bash
python main.py --report
# Or via menu: "Generate HTML Report"
```

### Report Types

#### Raw Data
- **Location**: `data_output/raw/`
- **Format**: JSON files
- **Content**: Raw scraped data from each source

#### Processed Data
- **Location**: `data_output/processed/`
- **Format**: CSV, JSON, Excel
- **Content**: Cleaned and structured data

#### Reports
- **Location**: `data_output/reports/`
- **Format**: HTML, JSON, Excel
- **Content**: Analytics and visualizations

### Data Analysis Features

#### Statistical Analysis
- Article count by source
- Publication date distribution
- Author analysis
- Content length statistics

#### Trend Analysis
- Daily trends
- Source popularity
- Content type distribution
- Temporal patterns

#### Visualizations
- Source distribution charts
- Temporal distribution plots
- Author distribution graphs
- Content analysis charts

## Data Management

### File Structure

```
data_output/
├── raw/                    # Raw scraped data
│   ├── news_data.json
│   ├── rss_data.json
│   ├── blog_data.json
│   └── worker_*.json      # Individual worker outputs
├── processed/              # Processed and cleaned data
│   ├── complete_dataset_*.csv
│   ├── content_analysis_*.csv
│   ├── daily_trends_*.csv
│   └── source_summary_*.csv
└── reports/                # Generated reports
    ├── comprehensive_report_*.html
    ├── comprehensive_report_*.json
    └── comprehensive_report_*.xlsx
```

### Data Operations

#### List Data Files
```bash
python main.py
# Select "Manage Data" → "List Data Files"
```

#### Search Data
```bash
python main.py
# Select "Manage Data" → "Search Data"
# Enter search term to find specific content
```

#### Clean Old Data
```bash
python main.py
# Select "Manage Data" → "Clean Old Data"
# Confirm to delete all data files
```

#### Export Data
Data is automatically exported in multiple formats:
- **JSON**: Raw data structure
- **CSV**: Tabular format for analysis
- **Excel**: Formatted reports with charts
- **HTML**: Interactive web reports

## Configuration Management

### Worker Settings

Configure worker pool size:
```bash
python main.py
# Select "Configure Settings" → "Worker Settings"
```

**Settings:**
- **Min Workers**: Minimum number of concurrent workers
- **Max Workers**: Maximum number of concurrent workers

### Proxy Settings

Configure proxy servers for anonymous scraping:
```bash
python main.py
# Select "Configure Settings" → "Proxy Settings"
```

**Options:**
- Add new proxy
- Remove existing proxy
- Clear all proxies

### Rate Limiting

Configure request throttling:
```bash
python main.py
# Select "Configure Settings" → "Rate Limiting"
```

**Current Setting:**
- **Max Requests/Second**: 1 (configurable in Worker class)

## Troubleshooting

### Common Issues

#### 1. Import Errors
**Problem**: Module not found errors
**Solution**: Ensure you're in the correct directory and virtual environment is activated

```bash
# Check current directory
pwd

# Activate virtual environment
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate     # Windows

# Verify Python path
python -c "import sys; print(sys.path)"
```

#### 2. Permission Errors
**Problem**: Cannot write to data directories
**Solution**: Check file permissions

```bash
# Check permissions
ls -la data_output/

# Fix permissions if needed
chmod 755 data_output/
chmod 644 data_output/raw/*
```

#### 3. Network Errors
**Problem**: Connection timeouts or blocked requests
**Solution**: Check network configuration

```bash
# Test connectivity
curl -I https://www.bbc.com/

# Check proxy settings
python main.py
# Select "Configure Settings" → "Proxy Settings"
```

#### 4. Worker Failures
**Problem**: Workers not starting or failing tasks
**Solution**: Check worker configuration and logs

```bash
# Check logs
tail -f logs.log

# Verify worker settings
python main.py
# Select "Configure Settings" → "Worker Settings"
```

### Debug Mode

Enable detailed logging for troubleshooting:

```python
# In your script
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Log Files

- **Location**: `logs.log`
- **Content**: Detailed execution logs
- **Levels**: DEBUG, INFO, WARNING, ERROR

## Advanced Features

### Custom Scrapers

Create custom scrapers for new data sources:

```python
from src.scrapers.ScraperFactory import Scraper
from src.data.models import Article

class CustomScraper(Scraper):
    def scrape(self, url: str) -> List[Article]:
        # Implement your scraping logic
        articles = []
        # ... scraping code ...
        return articles
```

### Database Integration

The system includes SQLite database support:

```python
from src.data.database import Database

db = Database()
articles = db.get_articles_by_source("BBC")
```

### API Integration

Extend the system with REST API:

```python
# Example API endpoint
@app.route('/api/articles')
def get_articles():
    db = Database()
    articles = db.get_all_articles()
    return jsonify(articles)
```

### Scheduled Scraping

Set up automated scraping with cron jobs:

```bash
# Add to crontab
0 */6 * * * cd /path/to/project && python main.py --auto
```

### Custom Analysis

Extend analysis capabilities:

```python
from src.analysis.statistic import DataStatistics

stats = DataStatistics()
stats.load_data()
custom_analysis = stats.custom_analysis_method()
```

## Best Practices

### 1. Respectful Scraping
- Use rate limiting (default: 1 request/second)
- Rotate user agents
- Respect robots.txt
- Don't overwhelm target servers

### 2. Data Management
- Regularly clean old data files
- Backup important datasets
- Monitor disk space usage
- Validate data quality

### 3. Performance Optimization
- Adjust worker count based on system resources
- Use proxies for high-volume scraping
- Monitor memory usage
- Optimize database queries

### 4. Error Handling
- Monitor logs regularly
- Set up alerts for failures
- Implement retry logic
- Validate data integrity

### 5. Security
- Use secure proxy connections
- Validate input URLs
- Sanitize scraped data
- Protect sensitive configuration

## Support

### Getting Help

1. **Check Documentation**: Review this guide and architecture docs
2. **Examine Logs**: Check `logs.log` for error details
3. **Run Tests**: Execute test suite to verify functionality
4. **System Status**: Use CLI to check system health

### Testing

Run the test suite to verify system functionality:

```bash
python main.py
# Select "Run Tests"

# Or directly
python -m pytest tests/ -v
```

### System Status

Check system health and configuration:

```bash
python main.py
# Select "System Status"
```

This will show:
- Configuration status
- Data directory status
- Dependency status
- Worker configuration

## Examples

### Example 1: Basic News Scraping

```bash
# Configure news scraping
echo '{
  "min_workers": 2,
  "max_workers": 3,
  "tasks": [
    {
      "priority": 1,
      "url": "https://www.bbc.com/",
      "type": "news"
    }
  ]
}' > config.json

# Run scraping
python main.py --type news

# View results
ls data_output/raw/
cat data_output/raw/news_data.json
```

### Example 2: RSS Scraping with Search

```bash
# Configure RSS scraping
echo '{
  "tasks": [
    {
      "priority": 1,
      "url": "",
      "type": "rss",
      "search_word": "technology"
    }
  ]
}' > config.json

# Run scraping
python main.py --type rss

# Generate report
python main.py --report
```

### Example 3: Custom Analysis

```python
from src.analysis.statistic import DataStatistics
from src.analysis.trends import TrendAnalysis

# Run statistical analysis
stats = DataStatistics()
stats.load_data()
stats.export_statistics()

# Run trend analysis
trends = TrendAnalysis()
trends.load_data()
trends.export_trend_analysis()
```

This comprehensive user guide should help you get started with the web scraping system and make the most of its features! 