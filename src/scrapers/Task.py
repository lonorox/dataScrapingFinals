import time
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from ..data.models import ScrapingTask as ModelScrapingTask

class Task:
    def __init__(self,id,priority,url,type,search_word=None):
        self.id = id
        self.priority = priority
        self.url = url
        self.type = type
        self.search_word = search_word
        self.created_at = time.time()
    
    def to_model_task(self) -> ModelScrapingTask:
        """Convert to model ScrapingTask."""
        return ModelScrapingTask(
            id=str(self.id),
            url=self.url,
            source_type=self.type,
            priority=self.priority,
            search_word=self.search_word,
            metadata={
                'created_at': self.created_at,
                'original_id': self.id
            }
        )

@dataclass
class Result:
    task_id: int
    worker_name: str
    source_type: str
    data: List[Dict[str, Any]] = field(default_factory=list)
    success: bool = True
    error_message: Optional[str] = None
    scraped_at: Optional[float] = None
    processing_time: Optional[float] = None
    errors: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        if self.scraped_at is None:
            self.scraped_at = time.time()
    
    def add_error(self, error: str):
        """Add an error to the result."""
        self.errors.append(error)
    
    def to_scraping_result(self) -> 'ScrapingResult':
        """Convert to model ScrapingResult."""
        from ..data.models import ScrapingResult
        return ScrapingResult(
            success=self.success,
            articles=[],  # Will be populated by Master
            errors=self.errors,
            metadata={
                'task_id': self.task_id,
                'worker_name': self.worker_name,
                'source_type': self.source_type,
                'processing_time': self.processing_time,
                'scraped_at': self.scraped_at,
                **self.metadata
            }
        )