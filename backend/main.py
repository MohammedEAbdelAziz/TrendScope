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
from database import (
    get_trend_data, get_sentiment_change, save_sentiment_snapshot, 
    save_headlines_batch, init_db, get_latest_sentiment, get_latest_headlines
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

# Scrapers and Analyzer are now isolated in workers to save RAM


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


def process_region(region_id: str, save_to_db: bool = False) -> RegionSentiment:
    """Get region sentiment from cache or database"""
    
    # Check cache first
    cache_key = f"region_{region_id}"
    if cache_key in cache:
        return cache[cache_key]
    
    # Fetch latest snapshot from DB
    latest = get_latest_sentiment(region_id)
    
    if latest:
        # Get headlines associated with this snapshot
        raw_headlines = get_latest_headlines(region_id, limit=10)
        
        headlines = [
            Headline(
                title=h["title"],
                source=h["source"],
                url=h["url"],
                published_at=h["published_at"] if isinstance(h["published_at"], datetime) else None,
                sentiment_score=h["sentiment_score"],
                sentiment_label=SentimentLabel(h["sentiment_label"])
            ) for h in raw_headlines
        ]
        
        region_sentiment = RegionSentiment(
            region_id=region_id,
            region_name=REGIONS.get(region_id, region_id),
            sentiment_score=latest["score"],
            sentiment_label=SentimentLabel(latest["label"]),
            headline_count=latest["headline_count"],
            bull_count=latest.get("bull_count", 0),
            bear_count=latest.get("bear_count", 0),
            neutral_count=latest.get("neutral_count", 0),
            filtered_count=0, # No longer tracked live in API
            top_headlines=headlines,
            last_updated=latest["timestamp"] if isinstance(latest["timestamp"], datetime) else datetime.now()
        )
        
        # Store in cache
        cache[cache_key] = region_sentiment
        return region_sentiment
    else:
        # Fallback if DB is empty - triggering a live collection is too heavy for main process RAM
        # Return a "pending" state or empty data
        return RegionSentiment(
            region_id=region_id,
            region_name=REGIONS.get(region_id, region_id),
            sentiment_score=50.0,
            sentiment_label=SentimentLabel.NEUTRAL,
            headline_count=0,
            top_headlines=[],
            last_updated=datetime.now()
        )


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
                region_data = process_region(region_id, save_to_db=False)
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
        region_data = process_region(region_id, save_to_db=False)
        
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
async def trigger_collection():
    """Clear internal cache to show latest DB data (triggered by frontend Refresh)"""
    cache.clear()
    return {"success": True, "message": "Cache cleared, will fetch latest data from DB"}


@app.post("/api/refresh")
async def refresh_cache():
    """Clear the cache to force fresh data on next request"""
    cache.clear()
    return {"success": True, "message": "Cache cleared"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
