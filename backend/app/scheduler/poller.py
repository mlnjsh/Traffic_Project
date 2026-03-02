"""APScheduler-based polling loop for data sources.

Per PLAN.md: Poll TomTom every 2 minutes for 10 key corridors.
Per REPORT.md: ASTraM 1-min refresh, TomTom 30-sec refresh.
We poll every 2 min to stay within free-tier rate limits.
"""

import logging

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from app.config import settings

logger = logging.getLogger(__name__)

scheduler = AsyncIOScheduler()


async def poll_tomtom():
    """Poll TomTom Traffic Flow + Incidents APIs."""
    from app.data_sources.tomtom import TomTomClient
    client = TomTomClient()
    try:
        flow_data = await client.fetch()
        incidents = await client.fetch_incidents()
        logger.info(f"TomTom poll: {len(flow_data)} corridors, {len(incidents)} incidents")
    except Exception as e:
        logger.error(f"TomTom poll failed: {e}")


async def poll_astram():
    """Poll ASTraM incident API."""
    from app.data_sources.astram import ASTraMClient
    client = ASTraMClient()
    try:
        data = await client.fetch()
        incidents = data.get("incidents", [])
        logger.info(f"ASTraM poll: {len(incidents)} incidents")
    except Exception as e:
        logger.error(f"ASTraM poll failed: {e}")


def start_scheduler():
    """Start the background polling scheduler."""
    interval = settings.poll_interval_seconds

    scheduler.add_job(poll_tomtom, "interval", seconds=interval, id="tomtom_poll")
    scheduler.add_job(poll_astram, "interval", seconds=interval, id="astram_poll")

    scheduler.start()
    logger.info(f"Scheduler started: polling every {interval}s")


def stop_scheduler():
    """Stop the scheduler gracefully."""
    if scheduler.running:
        scheduler.shutdown(wait=False)
        logger.info("Scheduler stopped")
