# Contributors

This document tracks the contributions of team members to the Web Scraping System project.

## 👥 Team Members & Contributions
### Elene Baiashvili
**Role**: Selenium Scraper & Testing 


**Major Contributions**:
- **Selenium RSS Scraper**: Created the NPR RSS feed scraping system using Selenium WebDriver
- **Scrapy Blog Crawler**: Implemented TechCrunch blog scraping using Scrapy framework
- **Comprehensive Test Suite**: Built the entire testing infrastructure

**Files Created/Modified**:
- `src/scrapers/SeleniumRssScrapper.py` - NPR RSS feed scraper with Selenium
- `src/scrapers/BlogScrapy.py` - TechCrunch blog scraper using Scrapy
- `src/scrapers/scrapy_crawler/` - Complete Scrapy project structure
  - `src/scrapers/scrapy_crawler/newscrapy/spiders/techcrunch.py` - TechCrunch spider
  - `src/scrapers/scrapy_crawler/newscrapy/items.py` - Scrapy item definitions
  - `src/scrapers/scrapy_crawler/newscrapy/pipelines.py` - Data processing pipelines
  - `src/scrapers/scrapy_crawler/newscrapy/settings.py` - Scrapy configuration
- `tests/` - Complete test infrastructure
  - `tests/unit/` - Unit tests for individual components
  - `tests/integration/` - Integration tests for data processing and scraping pipeline
  - `tests/fixtures/` - Test data and mock responses
- `session_cookies.pkl` - Browser session management

**Key Features Implemented**:
- Dynamic RSS feed scraping with search word filtering
- Browser session persistence and cookie management
- Subprocess management for Scrapy integration
- Comprehensive test coverage with fixtures and mocks
- Error handling and retry logic for web scraping

---
### Saba Tchumburidze
**Role**: BeautifulSoup Scraper & Analysis 


**Major Contributions**:
- **BeautifulSoup News Scrapers**: Created BBC and Fox News scrapers using BeautifulSoup
- **Design Patterns**: Implemented Factory and Strategy patterns for extensible scraping
- **Data Analysis**: Built comprehensive analysis and reporting system

**Files Created/Modified**:
- `src/scrapers/NewsScrapper.py` - Main news scraper with BeautifulSoup
- `src/scrapers/ScrapingStrategy.py` - Strategy pattern implementation
  - BBCScrapingStrategy class
  - FoxNewsScrapingStrategy class
  - ScrapingContext class
- `src/scrapers/ScraperFactory.py` - Factory pattern for scraper creation
- `src/analysis/` - Complete analysis module
  - `src/analysis/reports.py` - HTML and Excel report generation
  - `src/analysis/statistic.py` - Statistical analysis and data quality checks
  - `src/analysis/trends.py` - Time-based trend analysis
  - `src/analysis/constants.py` - Analysis constants and templates
- Refactored project structure from `src/data/` to `src/scrapers/`

**Key Features Implemented**:
- Site-specific scraping strategies for BBC and Fox News
- Content extraction with tags and categories
- Statistical analysis of scraped data
- Trend analysis and temporal patterns
- Multi-format report generation (HTML, Excel, JSON)
- Data visualization and charts

---
### Saba Danelia
**Role**: Concurrency & System Architecture 

**Major Contributions**:
- **Master-Worker Architecture**: Implemented concurrent scraping with multiprocessing
- **Data Models & Database**: Created data structures and SQLite integration
- **CLI Interface**: Built comprehensive command-line interface
- **System Integration**: Connected all components and created main entry points

**Files Created/Modified**:
- `main.py` - Main application entry point
- `config.json` - Configuration file for tasks and workers
- `src/scrapers/Master.py` - Master node for task distribution and coordination
- `src/scrapers/Worker.py` - Worker processes for concurrent scraping
- `src/scrapers/Task.py` - Task and Result data models
- `src/data/` - Data management system
  - `src/data/models.py` - Article, ScrapingResult, ScrapingStats data models
  - `src/data/database.py` - SQLite database operations
  - `src/data/processors.py` - Data processing and consolidation
- `src/cli/` - Command-line interface
  - `src/cli/interface.py` - Main CLI interface and menu system
  - `src/cli/commands.py` - All CLI commands implementation
- `src/utils/` - Utility modules
  - `src/utils/configs.py` - Configuration management
  - `src/utils/logger.py` - Logging system
  - `src/utils/RateLimiter.py` - Rate limiting implementation
- `data_output/` - Output directory structure
- `logs.log` - Application logging
- Integration with analysis modules and test suite

**Key Features Implemented**:
- Multiprocessing worker pool with configurable size
- Task queue management and result collection
- SQLite database for data persistence
- Interactive CLI with menu system
- Command-line automation support
- Configuration management system
- Rate limiting and error handling
- Data consolidation and cleanup
- Performance monitoring and statistics

---

## 📊 Contribution Summary by Component

### Architecture & Core System
- **Saba Danelia**: Master-Worker architecture, multiprocessing, task management
- **Saba Tchumburidze**: Factory and Strategy design patterns
- **Elene Baiashvili**: Testing infrastructure for all components

### Scraping Components
- **Saba Tchumburidze**: BBC News, Fox News (BeautifulSoup + Strategy pattern)
- **Elene Baiashvili**: NPR RSS (Selenium), TechCrunch (Scrapy)
- **Saba Danelia**: Worker integration and task processing

### Data Management
- **Saba Danelia**: Data models, database operations, data processing
- **Saba Tchumburidze**: Data analysis and reporting
- **Elene Baiashvili**: Test data and fixtures

### User Interface
- **Saba Danelia**: Complete CLI interface and commands
- **Saba Tchumburidze**: Report generation and data visualization
- **Elene Baiashvili**: Test coverage for CLI functionality

### Analysis & Reporting
- **Saba Tchumburidze**: Statistical analysis, trend analysis, report generation
- **Saba Danelia**: Integration with CLI and database
- **Elene Baiashvili**: Test coverage for analysis modules

### Testing & Quality Assurance
- **Elene Baiashvili**: Complete test suite (unit, integration, fixtures)
- **Saba Danelia**: Integration with CLI testing
- **Saba Tchumburidze**: Analysis module testing

## 🔄 Development Workflow

### Branch Strategy
The project used feature branches for development:
- `features/concurrency` - Master-Worker architecture
- `features/utils` - Utility modules and configuration
- `features/completeDatabase` - Data models and database
- `features/commandLineInterface` - CLI implementation
- `features/analysisCliIntegration` - Analysis integration
- `features/CliTestsIntegration` - Testing integration

### Integration Points
- **Saba Danelia** integrated all components into a cohesive system
- **Saba Tchumburidze** provided analysis capabilities for scraped data
- **Elene Baiashvili** ensured quality through comprehensive testing

## 🏆 Key Achievements

### Technical Excellence
- **Scalable Architecture**: Master-Worker pattern with configurable worker pools
- **Design Patterns**: Factory and Strategy patterns for extensible scraping
- **Comprehensive Testing**: Full test coverage with unit and integration tests
- **Data Analysis**: Statistical analysis and trend detection
- **User Experience**: Intuitive CLI with both interactive and command-line modes

### Code Quality
- **Type Hints**: Comprehensive type annotations throughout
- **Error Handling**: Robust exception management and retry logic
- **Documentation**: Inline code documentation and comprehensive guides
- **Modular Design**: Clear separation of concerns and extensible architecture

### Performance & Reliability
- **Concurrent Processing**: Multiprocessing for efficient scraping
- **Rate Limiting**: Respectful scraping with configurable limits
- **Data Integrity**: Validation and error recovery mechanisms
- **Resource Management**: Proper cleanup and memory management

---

# Contributors: Real Commits with Branch Mapping

- b9f1d02dde78bcf037891b70c34641c719081707 SabaDanelia (2025-06-29): Update README.md [branches: dev
features/CliTestsIntegration
features/analysisCliIntegration
features/commandLineInterface
features/completeDatabase
features/concurrency
features/utils
main]
- df8311328644e529381a6616e09e8c6640440daa SabaDanelia (2025-06-29): Enhance configuration and documentation for web scraping system [branches: dev
features/CliTestsIntegration
features/analysisCliIntegration
features/commandLineInterface
features/completeDatabase
features/concurrency
features/utils
main]
- 556b8cb409a00ceb2307b12c860842a744286837 SabaDanelia (2025-06-29): Add run_all_tests method and update CLI options [branches: dev
features/CliTestsIntegration
features/analysisCliIntegration
features/commandLineInterface
features/completeDatabase
features/concurrency
features/utils
main]
- 5fec6e4c238c260355184418424ae411fdfd6387 SabaDanelia (2025-06-29): Refactor data paths and streamline report generation [branches: dev
features/CliTestsIntegration
features/analysisCliIntegration
features/commandLineInterface
features/completeDatabase
features/concurrency
features/utils
main]
- 3c79215500c96e51bbe0016f6c9f76231f060226 EleneBaiashvili (2025-06-29): Add test infrastructure and smoke tests for data scraping project [branches: dev
features/CliTestsIntegration
features/analysisCliIntegration
features/commandLineInterface
features/completeDatabase
features/concurrency
features/utils
main]
- 7133de9c16cd8f5f896ea82099a4b4e26b73c0dc EleneBaiashvili (2025-06-29): Add test fixtures for data scraping project [branches: dev
features/CliTestsIntegration
features/analysisCliIntegration
features/commandLineInterface
features/completeDatabase
features/concurrency
features/utils
main]
- 7bb13f9667e4c4873eb686544803c4afd81e4d06 EleneBaiashvili (2025-06-29): Add integration tests for data processing and scraping pipeline [branches: dev
features/CliTestsIntegration
features/analysisCliIntegration
features/commandLineInterface
features/completeDatabase
features/concurrency
features/utils
main]
- 4da326ec0d57535c01e2c50ef8340f4d71deba5c EleneBaiashvili (2025-06-29): Add unit tests for data scraping project [branches: dev
features/CliTestsIntegration
features/analysisCliIntegration
features/commandLineInterface
features/completeDatabase
features/concurrency
features/utils
main]
- 66bee80c1dc16ad8bcff7712ad924fb84b35f8a5 SabaDanelia (2025-06-28): Add analysis modules and refactor report generation [branches: dev
features/CliTestsIntegration
features/analysisCliIntegration
features/commandLineInterface
features/completeDatabase
features/concurrency
features/utils
main]
- 46c8e1d7f371ee455fb65f606200f098084f2083 SabaDanelia (2025-06-28): Refactor results directory and improve code formatting [branches: dev
features/CliTestsIntegration
features/analysisCliIntegration
features/commandLineInterface
features/completeDatabase
features/concurrency
features/utils
main]
- 6256c2f56fcac4e0d54af81cd3b71c8fc1802889 SabaTchumburidze (2025-06-28): Add constants and templates for the analysis module [branches: dev
features/CliTestsIntegration
features/analysisCliIntegration
features/commandLineInterface
features/completeDatabase
features/concurrency
features/utils
main]
- 56db1a8e4473a9fef021dec084c6aebfa19823dc SabaDanelia (2025-06-28): Add main entry point for the data scraping application [branches: dev
features/CliTestsIntegration
features/analysisCliIntegration
features/commandLineInterface
features/completeDatabase
features/concurrency
features/utils
main]
- edd24f26cd90f1d21b0d382ad4b189117ad571e4 SabaDanelia (2025-06-28): Add CLI interface and command structure for web scraping [branches: dev
features/CliTestsIntegration
features/analysisCliIntegration
features/commandLineInterface
features/completeDatabase
features/concurrency
features/utils
main]
- c6f207b460af2fea24a83223bdb783f9efbe93d1 SabaTchumburidze (2025-06-28): Add analysis modules for comprehensive data reporting - Introduced `reports.py` for generating automated reports with insights and data exports in multiple formats. - Added `statistics.py` for performing data quality checks, statistical summaries, and distributions. - Created `trends.py` for analyzing time-based trends and comparative analysis across sources. - Each module includes functionality for loading data, generating insights, and exporting results in various formats. [branches: dev
features/CliTestsIntegration
features/analysisCliIntegration
features/commandLineInterface
features/completeDatabase
features/concurrency
features/utils
main]
- d0043332fcb8537f4c4bf3d5d5a102fafeec4319 SabaDanelia (2025-06-28): moved configuration file for task management and worker settings from src to root [branches: dev
features/CliTestsIntegration
features/analysisCliIntegration
features/commandLineInterface
features/completeDatabase
features/concurrency
features/utils
main]
- 172ba28efc9c320fa3a4a8dbaf4be4883d57a356 SabaDanelia (2025-06-28): Add core scraping functionality with Master, Task, and Worker classes [branches: dev
features/CliTestsIntegration
features/analysisCliIntegration
features/commandLineInterface
features/completeDatabase
features/concurrency
features/utils
main]
- 3b9eddf729ec3dd7a2d12790e00c948b7f2cb0f2 SabaDanelia (2025-06-28): Add configuration and utility modules for task management [branches: dev
features/CliTestsIntegration
features/analysisCliIntegration
features/commandLineInterface
features/completeDatabase
features/concurrency
features/utils
main]
- 42ee9dfe660bb6e139e84f281325d5c194067d8c SabaTchumburidze (2025-06-28): added Factory and Strategy patters for better code organization added added NewsScrapper for BBC and Fox News scrapping [branches: dev
features/CliTestsIntegration
features/analysisCliIntegration
features/commandLineInterface
features/completeDatabase
features/concurrency
features/utils
main]
- 98a058fee5e910c89dd01d005bb487f5eaf74c8c SabaTchumburidze (2025-06-28): refactored src file moved scrapper from src/data to src [branches: dev
features/CliTestsIntegration
features/analysisCliIntegration
features/commandLineInterface
features/completeDatabase
features/concurrency
features/utils
main]
- 8c0f042ac6658522cd4bf298fded3e1a294d695c EleneBaiashvili (2025-06-28): Refactor data processing modules for improved efficiency [branches: dev
features/CliTestsIntegration
features/analysisCliIntegration
features/commandLineInterface
features/completeDatabase
features/concurrency
features/utils
main]
- facc263470c71babed368256deedda764ddbb65a SabaDanelia (2025-06-28): Add data management and processing modules [branches: dev
features/CliTestsIntegration
features/analysisCliIntegration
features/commandLineInterface
features/completeDatabase
features/concurrency
features/utils
main]

