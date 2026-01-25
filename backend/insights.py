"""
AI Insights generator using historical data and keyword analysis
"""
from database import get_trend_data, get_sentiment_change, get_top_keywords
from models import REGIONS
import logging

logger = logging.getLogger(__name__)


def generate_insights(region_id: str, current_score: float, current_label: str, headline_count: int) -> list[dict]:
    """Generate AI insights based on historical data and current sentiment"""
    insights = []
    
    # Get trend data
    trend_info = get_sentiment_change(region_id, hours=24)
    keywords = get_top_keywords(region_id, hours=24, limit=5)
    
    # Insight 1: Market Sentiment Overview
    if current_score > 60:
        insights.append({
            "title": "POSITIVE MOMENTUM",
            "text": f"Markets show strong optimism at {current_score:.1f}%. Positive sentiment is driving investor confidence across {region_id.upper()} markets.",
            "color": "emerald",
            "icon": "trending-up"
        })
    elif current_score < 40:
        insights.append({
            "title": "CAUTION ADVISED",
            "text": f"Sentiment at {current_score:.1f}% suggests market concerns. Economic headwinds may be affecting investor confidence.",
            "color": "rose",
            "icon": "trending-down"
        })
    else:
        insights.append({
            "title": "MARKET NEUTRALITY",
            "text": f"Markets show balanced sentiment at {current_score:.1f}%. Mixed signals from economic indicators are keeping sentiment stable.",
            "color": "amber",
            "icon": "minus"
        })
    
    # Insight 2: Trend Analysis
    if trend_info["data_points"] > 1:
        change = trend_info["change"]
        if trend_info["trend"] == "rising":
            insights.append({
                "title": "UPWARD TREND",
                "text": f"Sentiment has improved by {abs(change):.1f}% over the last 24 hours. Optimistic momentum is building.",
                "color": "emerald",
                "icon": "chevron-up"
            })
        elif trend_info["trend"] == "falling":
            insights.append({
                "title": "DOWNWARD PRESSURE",
                "text": f"Sentiment declined by {abs(change):.1f}% in the past 24 hours. Watch for potential further corrections.",
                "color": "rose",
                "icon": "chevron-down"
            })
        else:
            insights.append({
                "title": "STABLE OUTLOOK",
                "text": f"Sentiment remains stable with minimal change ({change:+.1f}%). Markets consolidating around current levels.",
                "color": "blue",
                "icon": "minus"
            })
    
    # Insight 3: Volume Analysis
    if headline_count > 50:
        insights.append({
            "title": "HIGH NEWS VOLUME",
            "text": f"Unusually high activity with {headline_count} headlines. Major economic events may be driving increased coverage.",
            "color": "purple",
            "icon": "file-text"
        })
    elif headline_count > 20:
        insights.append({
            "title": "ACTIVE NEWS CYCLE",
            "text": f"{headline_count} headlines analyzed. Normal market activity with steady information flow.",
            "color": "blue",
            "icon": "bar-chart"
        })
    else:
        insights.append({
            "title": "LIGHT NEWS DAY",
            "text": f"Only {headline_count} headlines found. Lower news volume may indicate quieter market conditions.",
            "color": "slate",
            "icon": "clipboard"
        })
    
    # Insight 4: Keyword-based insight (if we have keywords)
    if keywords:
        top_keyword = keywords[0]
        keyword_sentiment = "optimistic" if top_keyword.get("positive", 0) > top_keyword.get("negative", 0) else "pessimistic" if top_keyword.get("negative", 0) > top_keyword.get("positive", 0) else "neutral"
        
        insights.append({
            "title": "TOP TOPIC",
            "text": f"'{top_keyword['word'].title()}' is the most discussed topic with {top_keyword['count']} mentions. Sentiment around this topic is {keyword_sentiment}.",
            "color": "cyan",
            "icon": "search"
        })
    
    # Insight 5: Regional context
    region_name = REGIONS.get(region_id, region_id)
    regional_insights = {
        "global": "Global markets interconnected - watch for spillover effects from major economies.",
        "us": "Fed policy and employment data remain key drivers for American market sentiment.",
        "eu": "ECB decisions and energy prices continue to shape European economic outlook.",
        "africa": "Infrastructure investment and commodity prices driving African development narrative.",
        "egypt": "Currency stability and Suez Canal revenues crucial for Egyptian economic health.",
        "saudi": "Vision 2030 progress and oil diversification efforts shaping Saudi market narrative.",
        "middleeast": "Regional cooperation and energy transition policies impacting Gulf economies."
    }
    
    insights.append({
        "title": "REGIONAL CONTEXT",
        "text": regional_insights.get(region_id, f"Monitoring key economic indicators for {region_name}."),
        "color": "indigo",
        "icon": "globe"
    })
    
    return insights[:5]  # Return top 5 insights


def get_summary_insight(regions_data: list) -> dict:
    """Generate a summary insight across all regions"""
    if not regions_data:
        return {"title": "NO DATA", "text": "No sentiment data available", "color": "slate"}
    
    avg_score = sum(r.get("sentiment_score", 50) for r in regions_data) / len(regions_data)
    positive_regions = sum(1 for r in regions_data if r.get("sentiment_label") == "positive")
    negative_regions = sum(1 for r in regions_data if r.get("sentiment_label") == "negative")
    
    if positive_regions > negative_regions:
        return {
            "title": "GLOBAL OUTLOOK: OPTIMISTIC",
            "text": f"Majority of regions ({positive_regions}/{len(regions_data)}) showing positive sentiment. Average global score: {avg_score:.1f}%",
            "color": "emerald"
        }
    elif negative_regions > positive_regions:
        return {
            "title": "GLOBAL OUTLOOK: CAUTIOUS",
            "text": f"{negative_regions}/{len(regions_data)} regions showing pessimistic sentiment. Monitor risk exposure.",
            "color": "rose"
        }
    else:
        return {
            "title": "GLOBAL OUTLOOK: MIXED",
            "text": f"Balanced sentiment across regions. Average score: {avg_score:.1f}%",
            "color": "amber"
        }
