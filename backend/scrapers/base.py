"""
Base scraper class with common functionality
"""
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Optional
import logging
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models import Headline, SentimentLabel

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class BaseScraper(ABC):
    """Abstract base class for all news scrapers"""
    
    def __init__(self, region_id: str, region_name: str):
        self.region_id = region_id
        self.region_name = region_name
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
        }
    
    @abstractmethod
    def fetch_headlines(self) -> list[dict]:
        """
        Fetch raw headlines from the source.
        Returns list of dicts with: title, source, url, published_at (optional)
        """
        pass
    
    def create_headline(
        self, 
        title: str, 
        source: str, 
        url: str, 
        published_at: Optional[datetime] = None,
        sentiment_score: float = 0.0,
        sentiment_label: SentimentLabel = SentimentLabel.NEUTRAL
    ) -> Headline:
        """Create a Headline object"""
        return Headline(
            title=title,
            source=source,
            url=url,
            published_at=published_at,
            sentiment_score=sentiment_score,
            sentiment_label=sentiment_label
        )
    
    def safe_request(self, url: str, timeout: int = 10) -> Optional[str]:
        """Make a safe HTTP request with error handling"""
        import requests
        try:
            response = requests.get(url, headers=self.headers, timeout=timeout)
            response.raise_for_status()
            return response.text
        except Exception as e:
            logger.error(f"Error fetching {url}: {e}")
            return None
