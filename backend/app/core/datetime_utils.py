from datetime import datetime, timezone, timedelta

IST = timezone(timedelta(hours=5, minutes=30), name="Asia/Kolkata")

def to_ist(dt: datetime) -> datetime:
    """Convert any datetime to IST. If naive, assume UTC."""
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(IST)

def to_utc(dt: datetime) -> datetime:
    """Convert any datetime to UTC. If naive, assume IST."""
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=IST)
    return dt.astimezone(timezone.utc)

def parse_essl_datetime(dt_str: str) -> datetime:
    """
    Parse a naive string like '2026-05-02 09:48:43' from eSSL.
    eSSL logs are in local time (IST).
    Returns an IST-aware datetime.
    """
    dt = datetime.strptime(dt_str, "%Y-%m-%d %H:%M:%S")
    return dt.replace(tzinfo=IST)

def compare_time_with_policy(actual: datetime, policy_time_str: str) -> float:
    """
    Compare an actual datetime (converted to IST internally) against a policy time 'HH:MM:SS' or 'HH:MM'.
    Returns the difference in minutes.
    Positive means actual is AFTER policy time (e.g., late).
    Negative means actual is BEFORE policy time.
    """
    actual_ist = to_ist(actual)
    
    # parse policy time (handle HH:MM and HH:MM:SS)
    parts = policy_time_str.split(':')
    h = int(parts[0])
    m = int(parts[1])
    s = int(parts[2]) if len(parts) > 2 else 0
    
    policy_dt = actual_ist.replace(hour=h, minute=m, second=s, microsecond=0)
    
    diff = (actual_ist - policy_dt).total_seconds() / 60.0
    return diff

def get_current_ist() -> datetime:
    return datetime.now(IST)

def is_same_day_ist(dt1: datetime, dt2: datetime) -> bool:
    return to_ist(dt1).date() == to_ist(dt2).date()
