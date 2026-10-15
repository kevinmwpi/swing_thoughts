"""Load, validate, and format the swing thought bank."""

from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent
THOUGHTS_PATH = REPO_ROOT / "content" / "thoughts.yaml"

MAX_POST_LENGTH = 280
STATUSES = {"approved", "draft", "retired"}
REQUIRED_FIELDS = ("id", "cue", "for", "feel", "phase", "source", "status")

# A post with a link costs ~13x more on X's pay-per-use API ($0.20 vs $0.015)
# and gets less reach, so links are rejected outright.
URL_RE = re.compile(r"https?://|www\.|\b[\w-]+\.(?:com|net|org|io|co|ly|gg|me|app)\b", re.I)

# X counts these code point ranges as 1 character and everything else
# (emoji, CJK, ...) as 2. Mirrors twitter-text's v3 config.
_LIGHT_RANGES = ((0, 4351), (8192, 8205), (8208, 8223), (8242, 8247))


@dataclass(frozen=True)
class Thought:
    id: str
    cue: str
    audience: str
    feel: str
    drill: str | None
    phase: str
    source: str
    status: str


def load_thoughts(path: Path = THOUGHTS_PATH) -> list[Thought]:
    raw = yaml.safe_load(path.read_text(encoding="utf-8")) or []
    return [
        Thought(
            id=str(entry.get("id", "")),
            cue=str(entry.get("cue", "")).strip(),
            audience=str(entry.get("for", "")).strip(),
            feel=str(entry.get("feel", "")).strip(),
            drill=(str(entry["drill"]).strip() if entry.get("drill") else None),
            phase=str(entry.get("phase", "")),
            source=str(entry.get("source", "")),
            status=str(entry.get("status", "")),
        )
        for entry in raw
    ]


def weighted_length(text: str) -> int:
    """Length of `text` the way X counts it against the 280 limit."""
    total = 0
    for ch in unicodedata.normalize("NFC", text):
        cp = ord(ch)
        total += 1 if any(lo <= cp <= hi for lo, hi in _LIGHT_RANGES) else 2
    return total


def format_post(thought: Thought, number: int) -> str:
    parts = [
        f'Swing Thought #{number}: "{thought.cue}"',
        f"For: {thought.audience}",
        thought.feel,
    ]
    if thought.drill:
        parts.append(f"Try it: {thought.drill}")
    return "\n\n".join(parts)


def validate(thoughts: list[Thought], path: Path = THOUGHTS_PATH) -> list[str]:
    """Return a list of human-readable problems; empty means the bank is good."""
    raw = yaml.safe_load(path.read_text(encoding="utf-8")) or []
    errors = []
    for i, entry in enumerate(raw):
        missing = [f for f in REQUIRED_FIELDS if not entry.get(f)]
        if missing:
            errors.append(f"entry {i} ({entry.get('id', '?')}): missing {', '.join(missing)}")

    seen = set()
    for t in thoughts:
        if t.id in seen:
            errors.append(f"{t.id}: duplicate id")
        seen.add(t.id)
        if t.status not in STATUSES:
            errors.append(f"{t.id}: status must be one of {sorted(STATUSES)}, got {t.status!r}")
        # Check against a 4-digit post number so the bank stays valid for years.
        post = format_post(t, 9999)
        length = weighted_length(post)
        if length > MAX_POST_LENGTH:
            errors.append(f"{t.id}: post is {length} chars, over by {length - MAX_POST_LENGTH}")
        if URL_RE.search(post):
            errors.append(f"{t.id}: contains a link (links cost 13x more per post on X)")
    return errors
