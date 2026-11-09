from datetime import datetime, timedelta
from zoneinfo import ZoneInfo


SLOT_HOURS = (6, 10, 14, 18)
SEOUL = ZoneInfo("Asia/Seoul")


def latest_slot(now=None):
    now = (now or datetime.now(SEOUL)).astimezone(SEOUL)
    for hour in reversed(SLOT_HOURS):
        if now.hour >= hour:
            return now.replace(hour=hour, minute=0, second=0, microsecond=0)
    return (now - timedelta(days=1)).replace(
        hour=SLOT_HOURS[-1], minute=0, second=0, microsecond=0
    )


def slot_needs_update(slot, *timestamps):
    for timestamp in timestamps:
        if not timestamp:
            return True
        try:
            observed = datetime.fromisoformat(timestamp)
        except (TypeError, ValueError):
            return True
        if observed.tzinfo is None or observed < slot:
            return True
    return False
