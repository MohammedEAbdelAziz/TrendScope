"""
Celery configuration and tasks for scheduled data collection
Runs hourly to collect and store sentiment data
"""
from celery import Celery
from celery.schedules import crontab
import os
import sys
import logging

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database import save_sentiment_snapshot, save_headlines_batch, init_db
from scrapers.google_news_scraper import GoogleNewsRSSScraper
from sentiment.analyzer import analyzer
from models import REGIONS

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Celery configuration
# Using Redis as broker - install: pip install redis
# Or use RabbitMQ, or even filesystem for testing
BROKER_URL = os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0")
RESULT_BACKEND = os.getenv("CELERY_RESULT_BACKEND", "redis://localhost:6379/0")

app = Celery("econ_mood", broker=BROKER_URL, backend=RESULT_BACKEND)

# Celery configuration
app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    # Beat schedule for hourly data collection
    beat_schedule={
        "collect-sentiment-hourly": {
            "task": "celery_tasks.collect_all_regions",
            "schedule": crontab(minute=0),  # Every hour at :00
        },
    },
)


@app.task(name="celery_tasks.collect_region_data")
def collect_region_data(region_id: str, region_name: str) -> dict:
    """Collect and store sentiment data for a single region"""
    logger.info(f"Collecting data for region: {region_id}")
    
    try:
        # Initialize scraper
        scraper = GoogleNewsRSSScraper(region_id, region_name)
        
        # Fetch headlines
        raw_headlines = scraper.fetch_headlines()
        
        if not raw_headlines:
            logger.warning(f"No headlines found for {region_id}")
            return {"success": False, "region": region_id, "error": "No headlines"}
        
        # Analyze sentiment for each headline
        headlines = []
        scores = []
        
        for raw in raw_headlines:
            score, label = analyzer.analyze(raw["title"])
            scores.append(score)
            
            headlines.append({
                "title": raw["title"],
                "source": raw.get("source", "Unknown"),
                "url": raw.get("url", "#"),
                "sentiment_score": round(score, 3),
                "sentiment_label": label.value  # Convert enum to string
            })
        
        # Calculate aggregate sentiment using polarity counting
        avg_score, overall_label, polarity_counts = analyzer.aggregate_sentiment(scores)
        percentage_score = analyzer.calculate_polarity_score(
            polarity_counts.bull_count, 
            polarity_counts.bear_count
        )
        
        # Save to database
        save_sentiment_snapshot(
            region_id=region_id,
            score=percentage_score,
            label=overall_label.value,
            headline_count=len(headlines)
        )
        
        # Save headlines for keyword analysis
        save_headlines_batch(region_id, headlines)
        
        logger.info(f"Successfully collected {len(headlines)} headlines for {region_id}, score: {percentage_score:.1f}%")
        
        return {
            "success": True,
            "region": region_id,
            "score": percentage_score,
            "label": overall_label.value,
            "headline_count": len(headlines)
        }
        
    except Exception as e:
        logger.error(f"Error collecting data for {region_id}: {e}")
        return {"success": False, "region": region_id, "error": str(e)}


@app.task(name="celery_tasks.collect_all_regions")
def collect_all_regions() -> dict:
    """Collect data for all regions - called hourly by Celery Beat"""
    logger.info("Starting hourly data collection for all regions")
    
    results = {}
    for region_id, region_name in REGIONS.items():
        result = collect_region_data(region_id, region_name)
        results[region_id] = result
    
    success_count = sum(1 for r in results.values() if r.get("success"))
    logger.info(f"Completed hourly collection: {success_count}/{len(REGIONS)} regions successful")
    
    return {
        "success": success_count == len(REGIONS),
        "total": len(REGIONS),
        "successful": success_count,
        "results": results
    }


@app.task(name="celery_tasks.manual_collect")
def manual_collect() -> dict:
    """Manual trigger for data collection (can be called from API)"""
    return collect_all_regions()


# Standalone script for manual data collection without Celery
def run_collection_now():
    """Run data collection immediately (without Celery)"""
    init_db()
    logger.info("Running immediate data collection...")
    
    for region_id, region_name in REGIONS.items():
        try:
            scraper = GoogleNewsRSSScraper(region_id, region_name)
            raw_headlines = scraper.fetch_headlines()
            
            if not raw_headlines:
                logger.warning(f"No headlines for {region_id}")
                continue
            
            headlines = []
            scores = []
            
            for raw in raw_headlines:
                score, label = analyzer.analyze(raw["title"])
                scores.append(score)
                headlines.append({
                    "title": raw["title"],
                    "source": raw.get("source", "Unknown"),
                    "url": raw.get("url", "#"),
                    "sentiment_score": round(score, 3),
                    "sentiment_label": label.value
                })
            
            avg_score, overall_label, polarity_counts = analyzer.aggregate_sentiment(scores)
            percentage_score = analyzer.calculate_polarity_score(
                polarity_counts.bull_count, 
                polarity_counts.bear_count
            )
            
            save_sentiment_snapshot(region_id, percentage_score, overall_label.value, len(headlines))
            save_headlines_batch(region_id, headlines)
            
            logger.info(f"Collected {len(headlines)} headlines for {region_id}: {percentage_score:.1f}%")
            
        except Exception as e:
            logger.error(f"Error collecting {region_id}: {e}")
    
    logger.info("Data collection complete!")


if __name__ == "__main__":
    # Run collection immediately when script is run directly
    run_collection_now()
