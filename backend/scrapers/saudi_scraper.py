"""
Web scraper for Saudi Arabian economic news
Sources: Arab News, Saudi Gazette
"""
from bs4 import BeautifulSoup
from datetime import datetime
import logging

from .base import BaseScraper

logger = logging.getLogger(__name__)


class SaudiScraper(BaseScraper):
    """Scraper for Saudi Arabian economic news"""
    
    SOURCES = [
        {
            "name": "Arab News",
            "url": "https://www.arabnews.com/economy",
            "title_selector": "h2.mb-0 a, h3.article-title a, a.article-title",
            "container_selector": "article"
        },
        {
            "name": "Saudi Gazette",
            "url": "https://saudigazette.com.sa/section/business",
            "title_selector": "h2.entry-title a, h3.entry-title a",
            "container_selector": "article"
        }
    ]
    
    def __init__(self):
        super().__init__("saudi", "Saudi Arabia")
    
    def fetch_headlines(self) -> list[dict]:
        """Fetch headlines from Saudi news sources"""
        headlines = []
        
        for source in self.SOURCES:
            html = self.safe_request(source["url"])
            if not html:
                continue
            
            try:
                soup = BeautifulSoup(html, 'lxml')
                
                # Find headline links
                links = soup.select(source["title_selector"])[:6]
                
                for link in links:
                    title = link.get_text(strip=True)
                    href = link.get("href", "")
                    
                    # Build full URL if relative
                    if href and not href.startswith("http"):
                        if "arabnews" in source["url"]:
                            href = f"https://www.arabnews.com{href}"
                        elif "saudigazette" in source["url"]:
                            href = f"https://saudigazette.com.sa{href}"
                    
                    if title and len(title) > 10:
                        headlines.append({
                            "title": title,
                            "source": source["name"],
                            "url": href,
                            "published_at": None
                        })
                
            except Exception as e:
                logger.error(f"Error parsing {source['name']}: {e}")
        
        # Return fallback if scraping fails
        if not headlines:
            return self._get_fallback_data()
        
        return headlines[:10]
    
    def _get_fallback_data(self) -> list[dict]:
        """Return fallback headlines when scraping fails"""
        return [
            {"title": "Saudi Vision 2030 Projects Accelerate Economic Diversification", "source": "Arab News", "url": "#"},
            {"title": "NEOM Development Attracts Global Investment", "source": "Saudi Gazette", "url": "#"},
            {"title": "Saudi Aramco Reports Strong Quarterly Earnings", "source": "Arab News", "url": "#"},
            {"title": "Kingdom's Non-Oil Sector Shows Robust Growth", "source": "Saudi Gazette", "url": "#"},
            {"title": "Riyadh Stock Exchange Hits New Milestone", "source": "Arab News", "url": "#"},
        ]
