from datetime import datetime
from abc import ABC, abstractmethod
from src.utils.RateLimiter import RateLimiter
import src.utils.configs as con
from src.utils.logger import log
from src.data.models import ScrapingTask, Article
from typing import List, Dict, Any


class Scraper(ABC):
    """Abstract base class for all scrapers"""
    
    @abstractmethod
    def scrape(self, url: str) -> List[Article]:
        """Scrape data from the given URL and return Article objects"""
        pass
    
    def validate_url(self, url: str) -> bool:
        """Validate if the URL is valid for this scraper"""
        return url and isinstance(url, str) and url.startswith(('http://', 'https://'))
    
    def preprocess_data(self, data: List[Dict[str, Any]]) -> List[Article]:
        return data


class ScraperFactory:
    """Factory class for creating different types of scrapers"""
    
    @staticmethod
    def create_scraper(task_type: str, rate_limiter: RateLimiter = None, search_word: str = None) -> Scraper:
        """
        Factory method to create appropriate scraper based on task type
        
        Args:
            task_type: Type of scraper to create ('news', 'rss', 'blog')
            rate_limiter: Rate limiter instance for the scraper
            search_word: Search word for RSS scraper (optional)
            
        Returns:
            Scraper instance of the appropriate type
            
        Raises:
            ValueError: If task_type is not supported
        """
        if rate_limiter is None:
            rate_limiter = RateLimiter(max_requests_per_second=1)
            
        if task_type == "news":
            # Import here to avoid circular imports
            log.info(f"Creating NewsScraper instance")
            from src.scrapers.NewsScrapper import NewsScraper
            return NewsScraper(rate_limiter)
        elif task_type == "rss":
            # Import here to avoid circular imports
            from src.scrapers.SeleniumRssScrapper import seleniumRssScrapper
            log.info(f"Creating SeleniumRssScrapper instance with search word: {search_word}")
            return seleniumRssScrapper(rate_limiter, con.generate_header(), search_word)
        elif task_type == "blog":
            # Import here to avoid circular imports
            from src.scrapers.BlogScrapy import BlogScrapy
            log.info(f"Creating BlogScrapy instance")
            return BlogScrapy()
        else:
            raise ValueError(f"Unsupported scraper type: {task_type}")
    
    @staticmethod
    def get_supported_types() -> list:
        """Get list of supported scraper types"""
        return ["news", "rss", "blog"]
    
    @staticmethod
    def validate_task_type(task_type: str) -> bool:
        """Validate if the task type is supported"""
        return task_type in ScraperFactory.get_supported_types() 