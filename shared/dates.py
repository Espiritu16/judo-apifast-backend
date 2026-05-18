from datetime import datetime, timezone
def ahora_utc() -> datetime:
    return datetime.now(timezone.utc)
