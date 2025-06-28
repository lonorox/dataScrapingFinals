from abc import ABC, abstractmethod
from bs4 import BeautifulSoup
import requests
from urllib.parse import urljoin
from datetime import datetime
from src.utils.logger import log
from src.data.models import Article


class ScrapingStrategy(ABC):
    """Abstract base class for scraping strategies"""
    
    @abstractmethod
    def scrape(self, url: str) -> list:
        """Scrape data from the given URL"""
        pass
    
    @abstractmethod
    def get_site_name(self) -> str:
        """Get the name of the site this strategy handles"""
        pass


class BBCScrapingStrategy(ScrapingStrategy):
    """Strategy for scraping BBC News"""
    
    def __init__(self, session: requests.Session):
        self.session = session
        self.tag_set = set()
    
    def get_site_name(self):
        return "BBC News"
    
    def scrape(self, url):
        """Scrape BBC News articles"""
        soup = self._get_soup(url)
        data = soup.find_all('div', attrs={'data-testid': 'anchor-inner-wrapper'})
        articles = []

        for d in data:
            article = {}
            headline = d.find('h2', attrs={'data-testid': 'card-headline'})
            link = d.find('a', attrs={'data-testid': 'internal-link'})
            summary = d.find('p', attrs={'data-testid': 'card-description'})

            if headline and link and summary:
                # article['source'] = self.get_site_name()
                # article["headline"] = self._cleaner(headline.get_text())
                # article["summary"] = self._cleaner(summary.get_text())

                link_href = link['href']
                full_link = urljoin(url, link_href)
                # article["link"] = full_link

                # Extract categories from article page
                tags = []
                try:
                    article_soup = self._get_soup(full_link)
                    tags_div = article_soup.find('div', attrs={'data-component': 'tags'})
                    if tags_div:
                        tags = [t.get_text().lower() for t in tags_div.find_all('a')]
                        for t in tags:
                            self.tag_set.add(t)

                    else:
                        tags = []
                except Exception as e:
                    log.warning(f"Error extracting tags from {full_link}: {e}")
                    tags = []
                    # article['tags'] = []

                article = Article(
                    source_type= "news",
                    source=self.get_site_name(),
                    title=self._cleaner(headline.get_text()),
                    summary=self._cleaner(summary.get_text()),
                    url=full_link,
                    tags=tags,
                    scraped_at=datetime.now(),
                    metadata={
                        'scraper': 'NewsScraper',
                        'framework': 'basicScraper/bs4'
                    }
                )
                articles.append(article)

        return articles
    
    def _get_soup(self, url):
        response = self.session.get(url, timeout=10)
        response.raise_for_status()
        return BeautifulSoup(response.content, 'html.parser')
    
    def _cleaner(self, text):
        import re
        text = re.sub(r"\s+", " ", text).strip()
        text = re.sub(r"<.*?>", "", text)
        return text.lower()


class FoxNewsScrapingStrategy(ScrapingStrategy):
    """Strategy for scraping Fox News"""
    
    def __init__(self, session: requests.Session):
        self.session = session
        self.tag_set = set()
    
    def get_site_name(self):
        return "Fox News"
    
    def scrape(self, url):
        """Scrape Fox News articles"""
        soup = self._get_soup(url)
        content_div = soup.find('div', class_="content article-list small-shelf")

        if not content_div:
            return []

        data = content_div.find_all('h3', class_="title")
        articles = []

        for d in data:
            article = {}
            headline = d.get_text()
            link_elem = d.find('a')

            if not link_elem:
                continue

            link = urljoin(url, link_elem['href'])

            try:
                article_soup = self._get_soup(link)
                summary_elem = article_soup.find('h2', class_="sub-headline speakable")
                tags_div = article_soup.find('div', class_="related-topics")

                if headline and summary_elem and tags_div:
                    tags_ul = tags_div.find('ul', class_="categories")
                    if tags_ul:
                        tags = [t.get_text().lower() for t in tags_ul.find_all('li')]
                        for t in tags:
                            self.tag_set.add(t)
                        article = Article(
                            source_type="news",
                            source = self.get_site_name(),
                            title = self._cleaner(headline),
                            summary= self._cleaner(summary_elem.get_text()),
                            url = link,
                            tags = tags,
                            scraped_at = datetime.now(),
                        metadata = {
                            'scraper': 'NewsScraper',
                            'framework': 'basicScraper/bs4'
                        }
                        )
                        articles.append(article)

            except Exception as e:
                log.warning(f"Error extracting Fox article from {link}: {e}")
                continue

        return articles
    
    def _get_soup(self, url):
        response = self.session.get(url, timeout=10)
        response.raise_for_status()
        return BeautifulSoup(response.content, 'html.parser')
    
    def _cleaner(self, text):
        import re
        text = re.sub(r"\s+", " ", text).strip()
        text = re.sub(r"<.*?>", "", text)
        return text.lower()


class ScrapingContext:
    """Context class that uses different scraping strategies"""
    
    def __init__(self, session: requests.Session):
        self.session = session
        self._strategy = None
        self._strategies = {
            'bbc.com': BBCScrapingStrategy(session),
            'foxnews.com': FoxNewsScrapingStrategy(session)
        }
    
    def set_strategy(self, url: str):
        """Set the appropriate strategy based on URL"""
        for domain, strategy in self._strategies.items():
            if domain in url:
                self._strategy = strategy
                log.info(f"Using {strategy.get_site_name()} strategy for {url}")
                return
        
        # Default strategy or raise error
        raise ValueError(f"No strategy found for URL: {url}")
    
    def execute_scraping(self, url: str) -> list:
        """Execute scraping using the selected strategy"""
        if self._strategy is None:
            self.set_strategy(url)
        
        return self._strategy.scrape(url)
    
    def get_available_strategies(self) -> list:
        """Get list of available strategies"""
        return [strategy.get_site_name() for strategy in self._strategies.values()] 