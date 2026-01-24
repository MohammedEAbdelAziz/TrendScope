"""
NewsAPI-based scraper for Global, US, and EU regions
Uses the free tier (100 requests/day)
"""
import os
import requests
from datetime import datetime
from typing import Optional
import logging

from .base import BaseScraper

logger = logging.getLogger(__name__)


class NewsAPIScraper(BaseScraper):
    """Scraper using NewsAPI for Global, US, EU news"""
    
    BASE_URL = "https://newsapi.org/v2/top-headlines"
    EVERYTHING_URL = "https://newsapi.org/v2/everything"
    
    # Country mappings for regions
    REGION_CONFIG = {
        "global": {
            "endpoint": "everything",
            "params": {
                "q": "global economy OR world economy OR international trade",
                "language": "en",
                "sortBy": "publishedAt"
            }
        },
        "us": {
            "endpoint": "top-headlines",
            "params": {
                "country": "us",
                "category": "business"
            }
        },
        "eu": {
            "endpoint": "everything",
            "params": {
                "q": "economy OR business OR trade",
                "language": "en",
                "domains": "reuters.com,ft.com,euronews.com,dw.com,theguardian.com"
            }
        }
    }
    
    def __init__(self, region_id: str, region_name: str, api_key: Optional[str] = None):
        super().__init__(region_id, region_name)
        self.api_key = api_key or os.getenv("NEWSAPI_KEY", "")
        
        if not self.api_key:
            logger.warning(f"No NewsAPI key provided for {region_id}. Will use fallback data.")
    
    def fetch_headlines(self) -> list[dict]:
        """Fetch headlines from NewsAPI"""
        if not self.api_key:
            return self._get_fallback_data()
        
        config = self.REGION_CONFIG.get(self.region_id)
        if not config:
            logger.error(f"No config for region: {self.region_id}")
            return self._get_fallback_data()
        
        # Choose endpoint
        url = self.EVERYTHING_URL if config["endpoint"] == "everything" else self.BASE_URL
        
        # Build params
        params = {**config["params"], "apiKey": self.api_key, "pageSize": 10}
        
        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if data.get("status") != "ok":
                logger.error(f"NewsAPI error: {data.get('message', 'Unknown error')}")
                return self._get_fallback_data()
            
            headlines = []
            for article in data.get("articles", [])[:10]:
                published_at = None
                if article.get("publishedAt"):
                    try:
                        published_at = datetime.fromisoformat(
                            article["publishedAt"].replace("Z", "+00:00")
                        )
                    except:
                        pass
                
                headlines.append({
                    "title": article.get("title", "").split(" - ")[0],  # Remove source suffix
                    "source": article.get("source", {}).get("name", "Unknown"),
                    "url": article.get("url", ""),
                    "published_at": published_at
                })
            
            return headlines
            
        except Exception as e:
            logger.error(f"Error fetching from NewsAPI: {e}")
            return self._get_fallback_data()
    
    def _get_fallback_data(self) -> list[dict]:
        """Return fallback headlines when API is unavailable"""
        fallbacks = {
            "global": [
                {"title": "Global Markets Rally on Strong Economic Data", "source": "Reuters", "url": "#"},
                {"title": "World Trade Organization Reports Growth in International Commerce", "source": "Bloomberg", "url": "#"},
                {"title": "Central Banks Signal Cautious Approach to Interest Rates", "source": "Financial Times", "url": "#"},
                {"title": "Emerging Markets Show Resilience Amid Global Uncertainty", "source": "CNBC", "url": "#"},
                {"title": "Global Supply Chains Continue to Stabilize", "source": "The Economist", "url": "#"},
            ],
            "us": [
                {"title": "US Jobs Report Exceeds Expectations, Unemployment Falls", "source": "CNBC", "url": "#"},
                {"title": "Federal Reserve Maintains Interest Rate Policy", "source": "Wall Street Journal", "url": "#"},
                {"title": "Tech Sector Leads Stock Market Gains", "source": "Fox Business", "url": "#"},
                {"title": "Consumer Spending Shows Robust Growth in Retail Sector", "source": "Bloomberg", "url": "#"},
                {"title": "US Manufacturing Index Signals Expansion", "source": "Reuters", "url": "#"},
            ],
            "eu": [
                {"title": "European Central Bank Holds Rates Steady", "source": "Financial Times", "url": "#"},
                {"title": "German Economy Shows Signs of Recovery", "source": "Deutsche Welle", "url": "#"},
                {"title": "EU Trade Deal Boosts Business Confidence", "source": "Euronews", "url": "#"},
                {"title": "France Reports Strong Industrial Output", "source": "Reuters", "url": "#"},
                {"title": "European Markets Close Higher on Positive Data", "source": "Bloomberg", "url": "#"},
            ]
        }
        
        return fallbacks.get(self.region_id, fallbacks["global"])
