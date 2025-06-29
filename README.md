# Web Scraping System

A powerful, scalable web scraping system built with Python that supports multiple data sources including news sites, RSS feeds, and blogs. The system uses a Master-Worker architecture with multiprocessing for efficient concurrent scraping operations.

## 🌟 Features

- **Multi-Source Scraping**: Support for news sites, RSS feeds, and blogs
- **Scalable Architecture**: Master-Worker pattern with configurable worker pools
- **Design Patterns**: Factory and Strategy patterns for extensible scraping
- **Rate Limiting**: Respectful scraping with configurable request throttling
- **Proxy Support**: Anonymous scraping with proxy rotation
- **Data Analysis**: Comprehensive reporting and analytics
- **Interactive CLI**: User-friendly command-line interface
- **Database Integration**: SQLite storage with efficient data management
- **Error Handling**: Robust retry logic and graceful error recovery

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- pip (Python package installer)

### Installation

1. **Navigate to project directory**
   ```bash
   cd dataScrapingFinals
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   
   # On Windows
   venv\Scripts\activate
   
   # On macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Verify installation**
   ```bash
   python main.py --help
   ```

### Basic Usage

1. **Run interactive mode**
   ```bash
   python main.py
   ```

2. **Run all tasks automatically**
   ```bash
   python main.py --auto
   ```

3. **Run specific content type**
   ```bash
   python main.py --type news
   python main.py --type rss
   python main.py --type blog
   ```

4. **Generate reports**
   ```bash
   python main.py --report
   ```

## 📊 Supported Data Sources

### News Sources
- **BBC News** (`bbc.com`) - Latest news articles with categories
- **Fox News** (`foxnews.com`) - News articles and headlines

### RSS Sources
- **NPR** (`npr.org`) - RSS feed articles with search filtering

### Blog Sources
- **TechCrunch** (`techcrunch.com`) - Technology blog posts

## 🏗️ Architecture

The system follows a **Master-Worker pattern** with **multiprocessing** for concurrent scraping operations:

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

### Design Patterns

- **Factory Pattern**: Dynamic scraper creation based on task type
- **Strategy Pattern**: Site-specific scraping strategies
- **Master-Worker Pattern**: Distributed task processing
- **Observer Pattern**: Real-time monitoring and status tracking

## 📁 Project Structure

```
dataScrapingFinals/
├── main.py                 # Main entry point
├── config.json            # Configuration file
├── requirements.txt       # Python dependencies
├── docs/                  # Documentation
│   ├── architecture.md    # System architecture
│   └── user_guide.md      # User guide
├── src/                   # Source code
│   ├── cli/              # Command-line interface
│   ├── scrapers/         # Scraping components
│   ├── data/             # Data models and processing
│   ├── analysis/         # Data analysis and reporting
│   └── utils/            # Utilities and helpers
├── data_output/          # Output data
│   ├── raw/              # Raw scraped data
│   ├── processed/        # Processed data
│   └── reports/          # Generated reports
└── tests/                # Test suite
```

## ⚙️ Configuration

The system is configured via `config.json`:

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

- **Worker Pool**: Configure min/max worker processes
- **Tasks**: Define scraping tasks with priority and type
- **Network**: User agent rotation and proxy support
- **Rate Limiting**: Request throttling settings

## 📈 Usage Examples

### Interactive Mode
```bash
python main.py
# Navigate through the menu system
```

### Command Line Mode
```bash
# Run all configured tasks
python main.py --auto

# Run specific content type
python main.py --type news

# Generate comprehensive report
python main.py --report

# Use custom configuration
python main.py --config my_config.json
```

### Custom Configuration
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
```

## 📊 Reports & Analytics

The system generates comprehensive reports:

### Available Reports
- **Data Overview**: Summary of scraped data
- **Performance Analytics**: Scraping performance metrics
- **Task Summary**: Task configuration and status
- **HTML Reports**: Interactive web-based reports

### Output Formats
- **JSON**: Raw data structure
- **CSV**: Tabular format for analysis
- **Excel**: Formatted reports with charts
- **HTML**: Interactive web reports

### Analysis Features
- Statistical analysis of scraped content
- Trend analysis and temporal patterns
- Source distribution and popularity metrics
- Content classification and categorization

## 🔧 Advanced Features

### Custom Scrapers
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
```python
from src.data.database import Database

db = Database()
articles = db.get_articles_by_source("BBC")
```

### Scheduled Scraping
```bash
# Add to crontab for automated scraping
0 */6 * * * cd /path/to/project && python main.py --auto
```

## 🧪 Testing

Run the comprehensive test suite:

```bash
# Run all tests
python main.py
# Select "Run Tests"

# Or directly with pytest
python -m pytest tests/ -v

# Or with unittest
python -m unittest discover tests/
```

## 📚 Documentation

- **[Architecture Guide](docs/architecture.md)**: Detailed system architecture and design patterns
- **[User Guide](docs/user_guide.md)**: Comprehensive usage instructions and examples

## 🛠️ Troubleshooting

### Common Issues

1. **Import Errors**
   ```bash
   # Ensure virtual environment is activated
   source venv/bin/activate  # Linux/Mac
   venv\Scripts\activate     # Windows
   ```

2. **Permission Errors**
   ```bash
   # Check and fix permissions
   chmod 755 data_output/
   chmod 644 data_output/raw/*
   ```

3. **Network Errors**
   ```bash
   # Test connectivity
   curl -I https://www.bbc.com/
   
   # Check proxy settings
   python main.py
   # Select "Configure Settings" → "Proxy Settings"
   ```

4. **Worker Failures**
   ```bash
   # Check logs
   tail -f logs.log
   
   # Verify worker settings
   python main.py
   # Select "Configure Settings" → "Worker Settings"
   ```

### Debug Mode
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

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

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built with Python 3.8+
- Uses BeautifulSoup for HTML parsing
- Selenium for dynamic content scraping
- Scrapy framework for blog scraping
- SQLite for data storage
- Matplotlib and Seaborn for visualizations

## 📞 Support

- **Documentation**: Check the [docs/](docs/) directory
- **Issues**: Report bugs and feature requests
- **Logs**: Check `logs.log` for detailed error information
- **System Status**: Use CLI to check system health

---

**Happy Scraping! 🕷️📊** 