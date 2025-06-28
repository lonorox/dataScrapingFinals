"""
Data models for scraped articles and content.
"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional, Dict, Any
import json

@dataclass
class Article:
    """Data model for a scraped article."""
    
    # Core article information
    title: str
    url: str
    author: Optional[str] = None
    publication_date_datetime: Optional[datetime] = None
    publication_date_readable: Optional[str] = None
    summary: Optional[str] = None

    # Metadata
    tags: List[str] = field(default_factory=list)
    source_type: str = "unknown"  # blog, rss, news
    source: Optional[str] = None
    # Scraping metadata
    scraped_at: Optional[datetime] = None
    
    # Additional metadata
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        """Post-initialization processing."""
        # Convert tags from string representation if needed
        if isinstance(self.tags, str):
            try:
                self.tags = json.loads(self.tags.replace("'", '"'))
            except (json.JSONDecodeError, AttributeError):
                self.tags = [self.tags] if self.tags else []
        
        # Ensure tags is always a list
        if not isinstance(self.tags, list):
            self.tags = [self.tags] if self.tags else []
        
        # Convert datetime strings to datetime objects
        if isinstance(self.publication_date_datetime, str):
            try:
                self.publication_date_datetime = datetime.fromisoformat(
                    self.publication_date_datetime.replace('Z', '+00:00')
                )
            except ValueError:
                self.publication_date_datetime = None
        
        if isinstance(self.scraped_at, str):
            try:
                self.scraped_at = datetime.fromisoformat(
                    self.scraped_at.replace('Z', '+00:00')
                )
            except ValueError:
                self.scraped_at = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert article to dictionary."""
        return {
            'title': self.title,
            'url': self.url,
            'author': self.author,
            'publication_date_datetime': self.publication_date_datetime.isoformat() if self.publication_date_datetime else None,
            'publication_date_readable': self.publication_date_readable,
            'summary': self.summary,
            'tags': self.tags,
            'source_type': self.source_type,
            'source': self.source,
            'scraped_at': self.scraped_at.isoformat() if self.scraped_at else None,
            'metadata': self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Article':
        """Create article from dictionary."""
        return cls(**data)

@dataclass
class ScrapingResult:
    """Result of a scraping operation."""
    
    success: bool
    articles: List[Article] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def add_article(self, article: Article):
        """Add an article to the result."""
        self.articles.append(article)
    
    def add_error(self, error: str):
        """Add an error to the result."""
        self.errors.append(error)
    
    def get_article_count(self) -> int:
        """Get the number of articles scraped."""
        return len(self.articles)
    
    def get_error_count(self) -> int:
        """Get the number of errors encountered."""
        return len(self.errors)


@dataclass
class ScrapingTask:
    """Represents a scraping task."""
    
    id: str
    url: str
    source_type: str
    priority: int = 1
    search_word: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """Post-initialization processing."""
        if not self.id:
            import uuid
            self.id = str(uuid.uuid4())


@dataclass
class ScrapingStats:
    """Statistics for scraping operations."""
    
    total_articles: int = 0
    successful_scrapes: int = 0
    failed_scrapes: int = 0
    total_errors: int = 0
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    
    def start_timer(self):
        """Start the timer."""
        self.start_time = datetime.now()
    
    def end_timer(self):
        """End the timer."""
        self.end_time = datetime.now()
    
    def get_duration(self) -> Optional[float]:
        """Get duration in seconds."""
        if self.start_time and self.end_time:
            return (self.end_time - self.start_time).total_seconds()
        return None
    
    def get_success_rate(self) -> float:
        """Get success rate as percentage."""
        total = self.successful_scrapes + self.failed_scrapes
        if total == 0:
            return 0.0
        return (self.successful_scrapes / total) * 100 