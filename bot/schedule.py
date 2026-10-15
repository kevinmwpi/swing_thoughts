"""Decide what to post next and keep the post log."""

from __future__ import annotations

import json
import os
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

from .content import REPO_ROOT, Thought

STATE_PATH = REPO_ROOT / "state" / "posted.json"
DEFAULT_TIMEZONE = "America/New_York"


def load_history(path: Path | None = None) -> list[dict]:
    path = path or STATE_PATH
    if not path.exists():
        return []
    return json.loads(path.read_text(encoding="utf-8")).get("posts", [])


def save_history(history: list[dict], path: Path | None = None) -> None:
    path = path or STATE_PATH
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({"posts": history}, indent=2) + "\n", encoding="utf-8")


def today_local() -> date:
    tz = ZoneInfo(os.environ.get("POST_TIMEZONE") or DEFAULT_TIMEZONE)
    return datetime.now(tz).date()


def posted_on(history: list[dict], day: date) -> bool:
    return any(p.get("date") == day.isoformat() for p in history)


def pick_next(thoughts: list[Thought], history: list[dict]) -> Thought | None:
    """The first approved thought never posted, in file order.

    Once every approved thought has gone out, recycle the one posted longest
    ago: new followers haven't seen it, and the post number keeps the text
    unique so X doesn't reject it as a duplicate.
    """
    approved = [t for t in thoughts if t.status == "approved"]
    last_posted = {p["id"]: i for i, p in enumerate(history)}
    for t in approved:
        if t.id not in last_posted:
            return t
    if not approved:
        return None
    return min(approved, key=lambda t: last_posted[t.id])


def unposted_count(thoughts: list[Thought], history: list[dict]) -> int:
    posted = {p["id"] for p in history}
    return sum(1 for t in thoughts if t.status == "approved" and t.id not in posted)


def upcoming(thoughts: list[Thought], history: list[dict], days: int, start: date) -> list[tuple[date, int, Thought]]:
    """Simulate the next `days` posts as (date, post number, thought)."""
    simulated = list(history)
    if posted_on(simulated, start):
        start += timedelta(days=1)
    plan = []
    for offset in range(days):
        thought = pick_next(thoughts, simulated)
        if thought is None:
            break
        day = start + timedelta(days=offset)
        plan.append((day, len(simulated) + 1, thought))
        simulated.append({"id": thought.id, "date": day.isoformat()})
    return plan


def log_entry(thought: Thought, number: int, day: date, post_id: str) -> dict:
    return {
        "number": number,
        "id": thought.id,
        "date": day.isoformat(),
        "post_id": post_id,
        "posted_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    }
