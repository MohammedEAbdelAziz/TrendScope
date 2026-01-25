"""
Database models and setup for historical sentiment data
Uses SQLite for simplicity
"""
import sqlite3
from datetime import datetime, timedelta
from typing import Optional
import os
import logging

logger = logging.getLogger(__name__)

DATABASE_PATH = os.path.join(os.path.dirname(__file__), "sentiment_history.db")


def get_db_connection():
    """Get database connection"""
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Initialize the database with required tables"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Create sentiment history table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sentiment_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            region_id TEXT NOT NULL,
            sentiment_score REAL NOT NULL,
            sentiment_label TEXT NOT NULL,
            headline_count INTEGER NOT NULL,
            recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(region_id, recorded_at)
        )
    """)
    
    # Create index for faster queries
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_region_time 
        ON sentiment_history(region_id, recorded_at DESC)
    """)
    
    # Create headlines history table for AI insights
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS headlines_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            region_id TEXT NOT NULL,
            title TEXT NOT NULL,
            source TEXT NOT NULL,
            url TEXT,
            sentiment_score REAL NOT NULL,
            sentiment_label TEXT NOT NULL,
            recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_headlines_region_time 
        ON headlines_history(region_id, recorded_at DESC)
    """)
    
    conn.commit()
    conn.close()
    logger.info("Database initialized successfully")


def save_sentiment_snapshot(region_id: str, score: float, label: str, headline_count: int):
    """Save a sentiment snapshot to history"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            INSERT INTO sentiment_history (region_id, sentiment_score, sentiment_label, headline_count)
            VALUES (?, ?, ?, ?)
        """, (region_id, score, label, headline_count))
        conn.commit()
        logger.info(f"Saved sentiment snapshot for {region_id}: {score:.1f}%")
    except sqlite3.IntegrityError:
        logger.warning(f"Duplicate snapshot for {region_id}, skipping")
    finally:
        conn.close()


def save_headlines_batch(region_id: str, headlines: list[dict]):
    """Save headlines to history for AI analysis"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    for h in headlines:
        cursor.execute("""
            INSERT INTO headlines_history (region_id, title, source, url, sentiment_score, sentiment_label)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (region_id, h.get('title', ''), h.get('source', ''), h.get('url', ''), 
              h.get('sentiment_score', 0), h.get('sentiment_label', 'neutral')))
    
    conn.commit()
    conn.close()
    logger.info(f"Saved {len(headlines)} headlines for {region_id}")


def get_trend_data(region_id: str, hours: int = 24) -> list[dict]:
    """Get sentiment trend data for the last N hours"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cutoff_time = datetime.now() - timedelta(hours=hours)
    # Use strftime to match SQLite's CURRENT_TIMESTAMP format (YYYY-MM-DD HH:MM:SS)
    cutoff_str = cutoff_time.strftime('%Y-%m-%d %H:%M:%S')
    
    cursor.execute("""
        SELECT sentiment_score, sentiment_label, headline_count, recorded_at
        FROM sentiment_history
        WHERE region_id = ? AND recorded_at >= ?
        ORDER BY recorded_at ASC
    """, (region_id, cutoff_str))
    
    rows = cursor.fetchall()
    conn.close()
    
    return [
        {
            "score": row["sentiment_score"],
            "label": row["sentiment_label"],
            "headline_count": row["headline_count"],
            "timestamp": row["recorded_at"]
        }
        for row in rows
    ]


def get_latest_sentiment(region_id: str) -> Optional[dict]:
    """Get the most recent sentiment for a region"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT sentiment_score, sentiment_label, headline_count, recorded_at
        FROM sentiment_history
        WHERE region_id = ?
        ORDER BY recorded_at DESC
        LIMIT 1
    """, (region_id,))
    
    row = cursor.fetchone()
    conn.close()
    
    if row:
        return {
            "score": row["sentiment_score"],
            "label": row["sentiment_label"],
            "headline_count": row["headline_count"],
            "timestamp": row["recorded_at"]
        }
    return None


def get_sentiment_change(region_id: str, hours: int = 24) -> dict:
    """Calculate sentiment change over the past N hours"""
    trend_data = get_trend_data(region_id, hours)
    
    if len(trend_data) < 2:
        return {"change": 0, "trend": "stable", "data_points": len(trend_data)}
    
    first_score = trend_data[0]["score"]
    last_score = trend_data[-1]["score"]
    change = last_score - first_score
    
    if change > 2:
        trend = "rising"
    elif change < -2:
        trend = "falling"
    else:
        trend = "stable"
    
    return {
        "change": round(change, 1),
        "trend": trend,
        "first_score": first_score,
        "last_score": last_score,
        "data_points": len(trend_data)
    }


def get_top_keywords(region_id: str, hours: int = 24, limit: int = 10) -> list[dict]:
    """Extract top keywords from recent headlines for AI insights"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cutoff_time = datetime.now() - timedelta(hours=hours)
    cutoff_str = cutoff_time.strftime('%Y-%m-%d %H:%M:%S')
    
    cursor.execute("""
        SELECT title, sentiment_label
        FROM headlines_history
        WHERE region_id = ? AND recorded_at >= ?
    """, (region_id, cutoff_str))
    
    rows = cursor.fetchall()
    conn.close()
    
    # Simple keyword extraction
    keywords = {}
    for row in rows:
        words = row["title"].lower().split()
        for word in words:
            if len(word) > 4:  # Skip short words
                if word not in keywords:
                    keywords[word] = {"count": 0, "positive": 0, "negative": 0, "neutral": 0}
                keywords[word]["count"] += 1
                keywords[word][row["sentiment_label"]] += 1
    
    # Sort by frequency
    sorted_keywords = sorted(keywords.items(), key=lambda x: x[1]["count"], reverse=True)
    
    return [{"word": k, **v} for k, v in sorted_keywords[:limit]]


# Initialize database on module load
init_db()
