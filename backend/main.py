"""
Global Economic Mood Monitor - FastAPI Backend
Serves sentiment analysis data for 7 regions with historical trends and AI insights
"""
import os
import sys
from datetime import datetime
from typing import Optional, List
from cachetools import TTLCache
import logging
from pydantic import BaseModel

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from models import (
    Headline, RegionSentiment, APIResponse, 
    SentimentLabel, REGIONS
)
from sentiment.analyzer import analyzer
from scrapers.google_news_scraper import GoogleNewsRSSScraper
from database import (
    get_trend_data, get_sentiment_change, save_sentiment_snapshot, 
    save_headlines_batch, init_db
)
from insights import generate_insights

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize database
init_db()

# Initialize FastAPI app
app = FastAPI(
    title="Econ-Mood Monitor API",
    description="Tracks the emotional temperature of economic news across 7 regions",
    version="2.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Cache for API responses (15 minutes TTL)
cache: TTLCache = TTLCache(maxsize=100, ttl=900)

# Initialize scrapers - all using Google News RSS
SCRAPERS = {
    "global": GoogleNewsRSSScraper("global", "Global"),
    "us": GoogleNewsRSSScraper("us", "United States"),
    "eu": GoogleNewsRSSScraper("eu", "European Union"),
    "africa": GoogleNewsRSSScraper("africa", "Africa"),
    "egypt": GoogleNewsRSSScraper("egypt", "Egypt"),
    "saudi": GoogleNewsRSSScraper("saudi", "Saudi Arabia"),
    "middleeast": GoogleNewsRSSScraper("middleeast", "Middle East"),
}


# New Pydantic models for additional endpoints
class TrendDataPoint(BaseModel):
    score: float
    label: str
    headline_count: int
    timestamp: str

class TrendResponse(BaseModel):
    success: bool
    region_id: str
    trend: str  # rising, falling, stable
    change: float
    data_points: int
    data: List[TrendDataPoint]

class InsightItem(BaseModel):
    title: str
    text: str
    color: str
    icon: str

class InsightsResponse(BaseModel):
    success: bool
    region_id: str
    insights: List[InsightItem]


def process_region(region_id: str, save_to_db: bool = True) -> RegionSentiment:
    """Process a single region and return sentiment data with Bull/Bear polarity"""
    
    # Check cache first
    cache_key = f"region_{region_id}"
    if cache_key in cache:
        return cache[cache_key]
    
    scraper = SCRAPERS.get(region_id)
    if not scraper:
        raise ValueError(f"Unknown region: {region_id}")
    
    # Fetch headlines
    raw_headlines = scraper.fetch_headlines()
    
    # Analyze sentiment for each headline with noise filtering
    headlines = []
    scores = []
    headlines_for_db = []
    filtered_count = 0
    
    for raw in raw_headlines:
        title = raw["title"]
        
        # Skip noise/fluff headlines
        if analyzer.is_noise(title):
            filtered_count += 1
            logger.debug(f"Filtered noise headline: {title[:50]}...")
            continue
        
        score, label = analyzer.analyze(title)
        scores.append(score)
        
        headline = Headline(
            title=title,
            source=raw.get("source", "Unknown"),
            url=raw.get("url", "#"),
            published_at=raw.get("published_at"),
            sentiment_score=round(score, 3),
            sentiment_label=label
        )
        headlines.append(headline)
        
        # Prepare for DB
        headlines_for_db.append({
            "title": title,
            "source": raw.get("source", "Unknown"),
            "url": raw.get("url", "#"),
            "sentiment_score": round(score, 3),
            "sentiment_label": label.value
        })
    
    # Calculate aggregate sentiment using polarity counting
    avg_score, overall_label, polarity_counts = analyzer.aggregate_sentiment(scores)
    
    # Use polarity score (Bull/Bear ratio) instead of average
    polarity_score = analyzer.calculate_polarity_score(
        polarity_counts.bull_count, 
        polarity_counts.bear_count
    )
    
    # Create region sentiment object with Bull/Bear counts
    region_sentiment = RegionSentiment(
        region_id=region_id,
        region_name=REGIONS.get(region_id, region_id),
        sentiment_score=polarity_score,
        sentiment_label=overall_label,
        headline_count=len(headlines),
        bull_count=polarity_counts.bull_count,
        bear_count=polarity_counts.bear_count,
        neutral_count=polarity_counts.neutral_count,
        filtered_count=filtered_count,
        top_headlines=headlines[:10],  # Top 10 headlines
        last_updated=datetime.now()
    )
    
    # Save to database for historical tracking
    if save_to_db and len(headlines) > 0:
        try:
            save_sentiment_snapshot(region_id, polarity_score, overall_label.value, len(headlines))
            save_headlines_batch(region_id, headlines_for_db)
        except Exception as e:
            logger.warning(f"Failed to save to database: {e}")
    
    # Store in cache
    cache[cache_key] = region_sentiment
    
    return region_sentiment


@app.get("/")
async def root():
    """API root endpoint"""
    return {
        "name": "Econ-Mood Monitor API",
        "version": "2.0.0",
        "regions": list(REGIONS.keys()),
        "endpoints": {
            "regions": "/api/regions",
            "trend": "/api/regions/{region_id}/trend",
            "insights": "/api/regions/{region_id}/insights",
            "collect": "/api/collect"
        },
        "documentation": "/docs"
    }


@app.get("/health")
async def health_check():
    """Basic health check for Docker"""
    return {"status": "healthy"}


@app.get("/api/health")
async def api_health():
    """Detailed health check with database and scraper status"""
    try:
        # Check database connection
        from database import get_db_connection
        conn = get_db_connection()
        conn.execute("SELECT 1")
        conn.close()
        db_status = "healthy"
    except Exception as e:
        db_status = f"error: {str(e)}"
    
    return {
        "status": "healthy" if db_status == "healthy" else "degraded",
        "database": db_status,
        "regions": len(SCRAPERS),
        "cache_size": len(cache)
    }


@app.get("/api/regions", response_model=APIResponse)
async def get_all_regions():
    """Get sentiment data for all regions"""
    try:
        regions_data = []
        
        for region_id in REGIONS.keys():
            try:
                region_data = process_region(region_id)
                regions_data.append(region_data)
            except Exception as e:
                logger.error(f"Error processing region {region_id}: {e}")
                # Continue with other regions even if one fails
                continue
        
        return APIResponse(
            success=True,
            data=regions_data,
            timestamp=datetime.now()
        )
    
    except Exception as e:
        logger.error(f"Error getting all regions: {e}")
        return APIResponse(
            success=False,
            error=str(e),
            timestamp=datetime.now()
        )


@app.get("/api/regions/{region_id}", response_model=APIResponse)
async def get_region(region_id: str):
    """Get sentiment data for a specific region"""
    if region_id not in REGIONS:
        raise HTTPException(
            status_code=404, 
            detail=f"Region not found. Valid regions: {list(REGIONS.keys())}"
        )
    
    try:
        region_data = process_region(region_id)
        
        return APIResponse(
            success=True,
            data=[region_data],
            timestamp=datetime.now()
        )
    
    except Exception as e:
        logger.error(f"Error getting region {region_id}: {e}")
        return APIResponse(
            success=False,
            error=str(e),
            timestamp=datetime.now()
        )


@app.get("/api/regions/{region_id}/trend", response_model=TrendResponse)
async def get_region_trend(region_id: str, hours: int = 24):
    """Get historical trend data for a region"""
    if region_id not in REGIONS:
        raise HTTPException(
            status_code=404, 
            detail=f"Region not found. Valid regions: {list(REGIONS.keys())}"
        )
    
    try:
        # Get trend data from database
        trend_data = get_trend_data(region_id, hours=hours)
        trend_info = get_sentiment_change(region_id, hours=hours)
        
        return TrendResponse(
            success=True,
            region_id=region_id,
            trend=trend_info.get("trend", "stable"),
            change=trend_info.get("change", 0),
            data_points=len(trend_data),
            data=[TrendDataPoint(**d) for d in trend_data]
        )
    
    except Exception as e:
        logger.error(f"Error getting trend for {region_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/regions/{region_id}/insights", response_model=InsightsResponse)
async def get_region_insights(region_id: str):
    """Get AI-generated insights for a region"""
    if region_id not in REGIONS:
        raise HTTPException(
            status_code=404, 
            detail=f"Region not found. Valid regions: {list(REGIONS.keys())}"
        )
    
    try:
        # Get current sentiment data
        region_data = process_region(region_id, save_to_db=False)
        
        # Generate insights
        insights = generate_insights(
            region_id=region_id,
            current_score=region_data.sentiment_score,
            current_label=region_data.sentiment_label.value,
            headline_count=region_data.headline_count
        )
        
        return InsightsResponse(
            success=True,
            region_id=region_id,
            insights=[InsightItem(**i) for i in insights]
        )
    
    except Exception as e:
        logger.error(f"Error getting insights for {region_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/collect")
async def trigger_collection(background_tasks: BackgroundTasks):
    """Manually trigger data collection for all regions (saves to database)"""
    def collect_all():
        for region_id in REGIONS.keys():
            try:
                process_region(region_id, save_to_db=True)
                logger.info(f"Collected data for {region_id}")
            except Exception as e:
                logger.error(f"Error collecting {region_id}: {e}")
    
    background_tasks.add_task(collect_all)
    return {"success": True, "message": "Data collection started in background"}


@app.post("/api/refresh")
async def refresh_cache():
    """Clear the cache to force fresh data on next request"""
    cache.clear()
    return {"success": True, "message": "Cache cleared"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
