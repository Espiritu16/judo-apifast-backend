from datetime import date, datetime, timezone
from zoneinfo import ZoneInfo

LIMA_TZ = ZoneInfo("America/Lima")


def ahora_utc() -> datetime:
    return datetime.now(timezone.utc)


def now_lima() -> datetime:
    return datetime.now(LIMA_TZ)


def now_lima_naive() -> datetime:
    return now_lima().replace(tzinfo=None)


def today_lima() -> date:
    return now_lima().date()
