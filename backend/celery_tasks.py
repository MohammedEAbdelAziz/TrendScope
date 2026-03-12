"""
Celery configuration and tasks for scheduled data collection
Runs hourly to collect and store sentiment data
"""
from celery import Celery
from celery.schedules import crontab
import json
import os
import sys
import logging
import gc
import subprocess

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

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
    # Worker memory management
    worker_concurrency=1,
    worker_max_tasks_per_child=1,
    worker_max_memory_per_child=200000, # Kill worker if memory exceeds ~200MB during a task
    worker_prefetch_multiplier=1,  # Process one task at a time
    task_acks_late=True,  # Acknowledge task after completion
    # Beat schedule for hourly data collection
    beat_schedule={
        "collect-sentiment-15min": {
            "task": "celery_tasks.collect_all_regions",
            "schedule": crontab(minute="*/15"),  # Every 15 minutes
        },
        "cleanup-db-daily": {
            "task": "celery_tasks.cleanup_db",
            "schedule": crontab(hour=0, minute=0),  # Every day at midnight
        },
    },
)


def _extract_json_payload(stdout: str) -> dict:
    """Extract the last JSON object emitted by the collection subprocess."""
    for line in reversed(stdout.splitlines()):
        line = line.strip()
        if not line:
            continue
        try:
            return json.loads(line)
        except json.JSONDecodeError:
            continue
    raise ValueError("Collection subprocess did not emit JSON output")


def _run_collection_subprocess(region_id: str | None = None) -> dict:
    """Run the heavy collection code in a short-lived subprocess."""
    script_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "collection_runner.py")
    command = [sys.executable, script_path]
    if region_id is not None:
        command.extend(["--region", region_id])

    env = os.environ.copy()
    env.setdefault("TOKENIZERS_PARALLELISM", "false")
    env.setdefault("OMP_NUM_THREADS", "1")
    env.setdefault("OMP_WAIT_POLICY", "PASSIVE")

    completed = subprocess.run(
        command,
        capture_output=True,
        text=True,
        env=env,
        timeout=1800,
        check=False,
    )

    if completed.stderr:
        logger.info("Collection subprocess stderr:\n%s", completed.stderr.strip())

    try:
        payload = _extract_json_payload(completed.stdout)
    except ValueError as exc:
        raise RuntimeError(
            f"Collection subprocess failed with exit code {completed.returncode}"
        ) from exc

    if completed.returncode != 0 and payload.get("success") is True:
        logger.warning("Collection subprocess exited non-zero despite success payload")

    return payload


@app.task(name="celery_tasks.collect_region_data")
def collect_region_data(region_id: str, region_name: str) -> dict:
    """Collect and store sentiment data for a single region"""
    logger.info("Dispatching collection subprocess for region: %s (%s)", region_id, region_name)

    try:
        result = _run_collection_subprocess(region_id=region_id)
        gc.collect()
        return result
    except Exception as exc:
        logger.error("Error collecting data for %s: %s", region_id, exc)
        gc.collect()
        return {"success": False, "region": region_id, "error": str(exc)}


@app.task(name="celery_tasks.collect_all_regions")
def collect_all_regions() -> dict:
    """Collect data for all regions - called hourly by Celery Beat"""
    logger.info("Starting hourly data collection for all regions")

    try:
        result = _run_collection_subprocess()
        gc.collect()
        logger.info(
            "Completed hourly collection: %s/%s regions successful",
            result.get("successful", 0),
            result.get("total", len(REGIONS)),
        )
        return result
    except Exception as exc:
        logger.error("Error during hourly collection: %s", exc)
        gc.collect()
        return {
            "success": False,
            "total": len(REGIONS),
            "successful": 0,
            "results": {},
            "error": str(exc),
        }


@app.task(name="celery_tasks.manual_collect")
def manual_collect() -> dict:
    """Manual trigger for data collection (can be called from API)"""
    return collect_all_regions()


# Standalone script for manual data collection without Celery
def run_collection_now():
    """Run data collection immediately (without Celery)"""
    logger.info("Running immediate data collection in subprocess...")
    result = _run_collection_subprocess()
    logger.info(
        "Immediate collection complete: %s/%s regions successful",
        result.get("successful", 0),
        result.get("total", len(REGIONS)),
    )
    return result


@app.task(name="celery_tasks.cleanup_db")
def cleanup_db() -> dict:
    """Daily database cleanup task"""
    from database import cleanup_old_data
    logger.info("Starting daily database cleanup")
    return cleanup_old_data(days=7)  # Keep 7 days of history


if __name__ == "__main__":
    # Run collection immediately when script is run directly
    run_collection_now()
