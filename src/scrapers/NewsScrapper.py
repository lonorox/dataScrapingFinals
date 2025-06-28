from datetime import datetime
import requests
from src.utils.RateLimiter import RateLimiter
from src.utils.logger import log
from src.scrapers.ScrapingStrategy import ScrapingContext
from src.scrapers.ScraperFactory import Scraper
from src.data.models import Article
from typing import List, Dict, Any


class NewsScraper(Scraper):
    """Scraper for news articles using Strategy pattern - supports BBC, Fox News"""
    
    def __init__(self, rate_limiter: RateLimiter):
        self.rate_limiter = rate_limiter
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        # Use Strategy pattern for different news sites
        self.scraping_context = ScrapingContext(self.session)
        self.tag_set = set()  # Store all discovered categories

    def scrape(self, url: str) -> List[Article]:
        """Scrape news articles using appropriate strategy"""
        if not self.validate_url(url):
            raise ValueError(f"Invalid URL: {url}")
            
        self.rate_limiter.wait_if_needed()
        try:
            # Use Strategy pattern to select appropriate scraping strategy
            raw_data = self.scraping_context.execute_scraping(url)
            
            # Preprocess the data and convert to Article objects
            articles = self.preprocess_data(raw_data)
            
            # Add source type metadata
            for article in articles:
                article.source_type = 'news'
                if not article.scraped_at:
                    article.scraped_at = datetime.now()
            
            log.info(f"Successfully scraped {len(articles)} news articles from {url}")
            return articles
            
        except Exception as e:
            log.error(f"Error scraping news URL {url}: {str(e)}")
            raise

    def get_discovered_tags(self) -> set:
        """Return all discovered tags/categories"""
        # Combine tags from all strategies
        all_tags = set()
        for strategy in self.scraping_context._strategies.values():
            all_tags.update(strategy.tag_set)
        return all_tags

    def filter_by_category(self, articles, category_filter: str):
        """Filter articles by category"""
        filtered_articles = []
        similar_filters = []

        # Find similar tags
        for tag in self.get_discovered_tags():
            if category_filter.lower() in tag:
                similar_filters.append(tag)

        # Filter articles
        for filter_tag in similar_filters:
            filtered_articles.extend([
                article for article in articles
                if filter_tag in article.get('tags', [])
            ])

        return filtered_articles

    def search_by_keyword(self, articles, keyword):
        """Search articles by keyword in headline and summary"""
        keyword = keyword.lower()
        return [
            article for article in articles
            if keyword in article.get('headline', '').lower() or
               keyword in article.get('summary', '').lower()
        ]

    def close(self):
        """Clean up resources"""
        if hasattr(self, 'selenium_driver') and self.selenium_driver:
            self.selenium_driver.close()