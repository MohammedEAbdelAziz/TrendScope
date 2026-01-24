"""Quick test of Google News RSS scraper"""
from scrapers.google_news_scraper import GoogleNewsRSSScraper

# Test Saudi Arabia
scraper = GoogleNewsRSSScraper("saudi", "Saudi Arabia")
headlines = scraper.fetch_headlines()

print(f"Found {len(headlines)} headlines for Saudi Arabia:")
for h in headlines[:5]:
    print(f"  - {h['title'][:70]}...")
    print(f"    Source: {h['source']}")
    print()
