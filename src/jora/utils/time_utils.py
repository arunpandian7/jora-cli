"""Time parsing and formatting utilities. Ported from JoraManager."""

from __future__ import annotations

from datetime import datetime
from typing import Optional

import pytz


def parse_time_input(time_str: str) -> Optional[int]:
    """Parse time strings to seconds.

    Supports: '2h 30m', '2h30m', '90m', '1.5h', plain numbers (treated as hours).
    Returns None for 'none', 'null', or empty input.
    Raises ValueError with a descriptive message on invalid format.
    """
    if not time_str or time_str.lower().strip() in ("none", "null", ""):
        return None

    try:
        s = time_str.lower().strip()
        total_seconds = 0.0

        if "h" in s:
            parts = s.split("h")
            total_seconds += float(parts[0].strip()) * 3600
            if len(parts) > 1 and parts[1].strip():
                minutes_part = parts[1].replace("m", "").strip()
                if minutes_part:
                    total_seconds += float(minutes_part) * 60
        elif "m" in s:
            total_seconds += float(s.replace("m", "").strip()) * 60
        else:
            total_seconds += float(s) * 3600

        return int(total_seconds)

    except (ValueError, IndexError):
        raise ValueError(
            f"Invalid time format: '{time_str}'. Use formats like '2h 30m', '90m', or '1.5h'."
        )


def format_time_estimate(seconds: Optional[int]) -> str:
    """Convert seconds to human-readable format. Returns 'Not set' for None/0."""
    if not seconds:
        return "Not set"
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    if hours > 0:
        return f"{hours}h {minutes}m"
    return f"{minutes}m"


def seconds_to_jira_format(seconds: int) -> str:
    """Convert seconds to Jira time format string for API calls ('2h', '30m', '2h 30m')."""
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    if hours > 0 and minutes > 0:
        return f"{hours}h {minutes}m"
    elif hours > 0:
        return f"{hours}h"
    return f"{minutes}m"


def parse_datetime(
    date_str: Optional[str],
    time_str: Optional[str],
    timezone: str = "UTC",
) -> datetime:
    """Parse date/time strings and localize to the given timezone, then convert to UTC.

    Args:
        date_str: ISO date string (YYYY-MM-DD), or None to use today.
        time_str: Time string (HH:MM), or None to default to 09:00.
        timezone: Timezone name (e.g. 'Asia/Tokyo', 'UTC').

    Returns:
        UTC-aware datetime object.
    """
    local_tz = pytz.timezone(timezone)

    if date_str:
        try:
            if time_str:
                dt = datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M")
            else:
                dt = datetime.strptime(date_str, "%Y-%m-%d").replace(hour=9, minute=0)
        except ValueError:
            dt = datetime.now()
    else:
        dt = datetime.now()

    if dt.tzinfo is None:
        dt = local_tz.localize(dt)

    return dt.astimezone(pytz.UTC)
