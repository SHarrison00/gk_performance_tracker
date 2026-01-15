from datetime import datetime, timezone


def ts():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")
