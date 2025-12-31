from datetime import datetime, timezone, timedelta 


def is_stale(scrape_item, now_dt = None, max_days = 6):
    """Return True if scrape item, or scraped more than `max_days` ago."""
    if now_dt is None:
        now_dt = datetime.now(timezone.utc)
    
    last_scraped = scrape_item.get("last_scraped_date")

    if not last_scraped:
        return True

    last_dt = datetime.fromisoformat(last_scraped)
    return (now_dt - last_dt) >= timedelta(days = max_days)
