"""
Run sentiment collection in a short-lived process.

This isolates the heavy ONNX Runtime model from the Celery worker so native
memory is returned to the OS when the subprocess exits.
"""
import argparse
import gc
import json
import logging
import os
import sys

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database import init_db, save_headlines_batch, save_sentiment_snapshot
from models import REGIONS

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def collect_region_data(region_id: str, region_name: str) -> dict:
    """Collect and store sentiment data for a single region."""
    logger.info("Collecting data for region: %s", region_id)

    try:
        from scrapers.google_news_scraper import GoogleNewsRSSScraper
        from sentiment.analyzer import analyzer

        scraper = GoogleNewsRSSScraper(region_id, region_name)
        raw_headlines = scraper.fetch_headlines()

        if not raw_headlines:
            logger.warning("No headlines found for %s", region_id)
            return {"success": False, "region": region_id, "error": "No headlines"}

        headlines = []
        scores = []

        # Iterate by popping from raw_headlines to immediately free up space
        while raw_headlines:
            raw = raw_headlines.pop(0)
            score, label = analyzer.analyze(raw["title"])
            scores.append(score)
            headlines.append(
                {
                    "title": raw["title"],
                    "source": raw.get("source", "Unknown"),
                    "url": raw.get("url", "#"),
                    "sentiment_score": round(score, 3),
                    "sentiment_label": label.value,
                }
            )
            
        # raw_headlines is now empty and can be freed safely
        del raw_headlines
        
        _, overall_label, polarity_counts = analyzer.aggregate_sentiment(scores)
        percentage_score = analyzer.calculate_polarity_score(
            polarity_counts.bull_count,
            polarity_counts.bear_count,
        )
        
        # Free scores early
        del scores

        headline_count = len(headlines)
        
        save_sentiment_snapshot(
            region_id=region_id,
            score=percentage_score,
            label=overall_label.value,
            headline_count=headline_count,
            bull_count=polarity_counts.bull_count,
            bear_count=polarity_counts.bear_count,
            neutral_count=polarity_counts.neutral_count,
        )
        
        # Batch inserting large numbers of headlines might consume memory, but sqlite cursor executes it fast enough.
        # Once save is complete, release it.
        save_headlines_batch(region_id, headlines)

        logger.info(
            "Successfully collected %s headlines for %s, score: %.1f%%",
            headline_count,
            region_id,
            percentage_score,
        )

        del scraper, headlines
        gc.collect()

        return {
            "success": True,
            "region": region_id,
            "score": percentage_score,
            "label": overall_label.value,
            "headline_count": headline_count,
        }
    except Exception as exc:
        logger.error("Error collecting data for %s: %s", region_id, exc)
        gc.collect()
        return {"success": False, "region": region_id, "error": str(exc)}


def collect_all_regions() -> dict:
    """Collect data for all regions within the short-lived subprocess."""
    logger.info("Starting data collection subprocess for all regions")

    results = {}
    for region_id, region_name in REGIONS.items():
        results[region_id] = collect_region_data(region_id, region_name)

    success_count = sum(1 for result in results.values() if result.get("success"))

    try:
        from sentiment.analyzer import analyzer

        analyzer.unload_model()
    except Exception as exc:
        logger.warning("Failed to unload model before subprocess exit: %s", exc)

    gc.collect()

    return {
        "success": success_count == len(REGIONS),
        "total": len(REGIONS),
        "successful": success_count,
        "results": results,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Run TrendScope collection")
    parser.add_argument("--region", choices=sorted(REGIONS.keys()))
    args = parser.parse_args()

    init_db()

    try:
        if args.region:
            result = collect_region_data(args.region, REGIONS[args.region])
            print(json.dumps(result), flush=True)
            return 0 if result.get("success") else 1

        result = collect_all_regions()
        print(json.dumps(result), flush=True)
        return 0 if result.get("successful", 0) > 0 else 1
    finally:
        try:
            from sentiment.analyzer import analyzer
            analyzer.unload_model()
        except Exception as exc:
            logger.warning("Failed to unload model in main before subprocess exit: %s", exc)
        gc.collect()


if __name__ == "__main__":
    raise SystemExit(main())