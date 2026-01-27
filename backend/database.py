"""
Database models and setup for historical sentiment data
Uses SQLite for simplicity
"""
import sqlite3
from datetime import datetime, timedelta
from typing import Optional
import os
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

# Use env var for Docker, fallback to local path for development
DATABASE_PATH = os.getenv("DATABASE_PATH", os.path.join(os.path.dirname(__file__), "sentiment_history.db"))


def get_db_connection():
    """Get database connection"""
    # Ensure the directory exists
    db_dir = os.path.dirname(DATABASE_PATH)
    if db_dir:
        Path(db_dir).mkdir(parents=True, exist_ok=True)
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
            bull_count INTEGER DEFAULT 0,
            bear_count INTEGER DEFAULT 0,
            neutral_count INTEGER DEFAULT 0,
            recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(region_id, recorded_at)
        )
    """)
    
    # Check for missing columns (migration for existing databases)
    cursor.execute("PRAGMA table_info(sentiment_history)")
    columns = [row[1] for row in cursor.fetchall()]
    
    if "bull_count" not in columns:
        logger.info("Migrating database: Adding bull_count column")
        cursor.execute("ALTER TABLE sentiment_history ADD COLUMN bull_count INTEGER DEFAULT 0")
        
    if "bear_count" not in columns:
        logger.info("Migrating database: Adding bear_count column")
        cursor.execute("ALTER TABLE sentiment_history ADD COLUMN bear_count INTEGER DEFAULT 0")
        
    if "neutral_count" not in columns:
        logger.info("Migrating database: Adding neutral_count column")
        cursor.execute("ALTER TABLE sentiment_history ADD COLUMN neutral_count INTEGER DEFAULT 0")
    
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


def save_sentiment_snapshot(region_id: str, score: float, label: str, headline_count: int, 
                            bull_count: int = 0, bear_count: int = 0, neutral_count: int = 0):
    """Save a sentiment snapshot to history"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            INSERT INTO sentiment_history (
                region_id, sentiment_score, sentiment_label, headline_count,
                bull_count, bear_count, neutral_count
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (region_id, score, label, headline_count, bull_count, bear_count, neutral_count))
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
        SELECT sentiment_score, sentiment_label, headline_count, recorded_at,
               bull_count, bear_count, neutral_count
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
            "bull_count": row["bull_count"],
            "bear_count": row["bear_count"],
            "neutral_count": row["neutral_count"],
            # Convert to ISO format with Z suffix for UTC (SQLite stores in UTC)
            "timestamp": row["recorded_at"].replace(" ", "T") + "Z" if row["recorded_at"] else None
        }
        for row in rows
    ]


def get_latest_sentiment(region_id: str) -> Optional[dict]:
    """Get the most recent sentiment for a region"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT sentiment_score, sentiment_label, headline_count, recorded_at,
               bull_count, bear_count, neutral_count
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
            "bull_count": row["bull_count"],
            "bear_count": row["bear_count"],
            "neutral_count": row["neutral_count"],
            "timestamp": row["recorded_at"]
        }
    return None


def get_latest_headlines(region_id: str, limit: int = 10) -> list[dict]:
    """Get the most recent headlines for a region"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT title, source, url, sentiment_score, sentiment_label, recorded_at
        FROM headlines_history
        WHERE region_id = ?
        ORDER BY recorded_at DESC
        LIMIT ?
    """, (region_id, limit))
    
    rows = cursor.fetchall()
    conn.close()
    
    return [
        {
            "title": row["title"],
            "source": row["source"],
            "url": row["url"],
            "sentiment_score": row["sentiment_score"],
            "sentiment_label": row["sentiment_label"],
            "published_at": row["recorded_at"]
        }
        for row in rows
    ]


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



def cleanup_old_data(days: int = 7):
    """Delete data older than N days to keep database size manageable"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cutoff_date = datetime.now() - timedelta(days=days)
    cutoff_str = cutoff_date.strftime('%Y-%m-%d %H:%M:%S')
    
    try:
        # Cleanup headlines history
        cursor.execute("DELETE FROM headlines_history WHERE recorded_at < ?", (cutoff_str,))
        headlines_deleted = cursor.rowcount
        
        # Cleanup sentiment history 
        cursor.execute("DELETE FROM sentiment_history WHERE recorded_at < ?", (cutoff_str,))
        sentiment_deleted = cursor.rowcount
        
        conn.commit()
        logger.info(f"Database cleanup: Deleted {headlines_deleted} old headlines and {sentiment_deleted} sentiment records")
        return {"headlines_deleted": headlines_deleted, "sentiment_deleted": sentiment_deleted}
        
    except Exception as e:
        logger.error(f"Error cleaning up database: {e}")
        return {"error": str(e)}
    finally:
        conn.close()


# Initialize database on module load
init_db()
