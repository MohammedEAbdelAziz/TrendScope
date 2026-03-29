"""
Health check utilities for backend services
"""
import sys
import os
import logging
from typing import Dict, Any, Tuple

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)

def check_database() -> Tuple[bool, str]:
    """Check database connectivity"""
    try:
        from database import get_db_connection
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        cursor.close()
        conn.close()
        return True, "healthy"
    except Exception as e:
        return False, str(e)

def check_redis() -> Tuple[bool, str]:
    """Check Redis connectivity"""
    try:
        import redis
        redis_url = os.environ.get("CELERY_BROKER_URL", "redis://localhost:6379/0")
        r = redis.from_url(redis_url, socket_connect_timeout=2, socket_keepalive=True, decode_responses=False)
        r.ping()
        r.close()
        return True, "healthy"
    except Exception as e:
        return False, str(e)

def full_health_check() -> Dict[str, Any]:
    """Perform full health check"""
    db_status, db_msg = check_database()
    redis_status, redis_msg = check_redis()
    
    all_healthy = db_status and redis_status
    
    return {
        "status": "healthy" if all_healthy else "degraded",
        "database": {"status": "healthy" if db_status else "error", "message": db_msg},
        "redis": {"status": "healthy" if redis_status else "error", "message": redis_msg},
        "overall": "healthy" if all_healthy else "degraded"
    }

if __name__ == "__main__":
    try:
        result = full_health_check()
        
        # Exit with 0 if healthy, 1 if degraded or error
        if result["overall"] == "healthy" and result["database"]["status"] == "healthy" and result["redis"]["status"] == "healthy":
            sys.exit(0)
        else:
            logger.error(f"Health check failed: {result}")
            sys.exit(1)
    except Exception as e:
        logger.error(f"Health check exception: {e}")
        sys.exit(1)
