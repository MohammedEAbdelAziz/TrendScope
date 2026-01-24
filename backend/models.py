"""
Data models for the Economic Mood Monitor
"""
from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from enum import Enum


class SentimentLabel(str, Enum):
    POSITIVE = "positive"
    NEUTRAL = "neutral"
    NEGATIVE = "negative"


class Headline(BaseModel):
    """A single news headline with sentiment"""
    title: str
    source: str
    url: str
    published_at: Optional[datetime] = None
    sentiment_score: float  # -1 to 1
    sentiment_label: SentimentLabel
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }


class RegionSentiment(BaseModel):
    """Sentiment data for a single region with Bull/Bear polarity"""
    region_id: str
    region_name: str
    sentiment_score: float  # 0 to 100 (Bull/Bear ratio)
    sentiment_label: SentimentLabel
    headline_count: int
    # New: Bull/Bear/Neutral counts
    bull_count: int = 0
    bear_count: int = 0
    neutral_count: int = 0
    filtered_count: int = 0  # Headlines removed by noise filter
    top_headlines: list[Headline]
    last_updated: datetime
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class APIResponse(BaseModel):
    """API response wrapper"""
    success: bool
    data: Optional[list[RegionSentiment]] = None
    error: Optional[str] = None
    timestamp: datetime
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


# Region definitions
REGIONS = {
    "global": "Global",
    "us": "United States",
    "eu": "European Union",
    "africa": "Africa",
    "egypt": "Egypt",
    "saudi": "Saudi Arabia",
    "middleeast": "Middle East"
}
