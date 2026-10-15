"""Command line entry point.

    python -m bot check              validate content/thoughts.yaml
    python -m bot preview [DAYS]     show the next posts exactly as they'll go out
    python -m bot post               dry run: show what today's post would be
    python -m bot post --live        post it to X and log it in state/posted.json
    python -m bot whoami             check the X credentials and show which account they post as
"""

from __future__ import annotations

import argparse
import sys
from collections import Counter

from . import schedule
from .content import MAX_POST_LENGTH, format_post, load_thoughts, validate, weighted_length
from .x_client import PostError, XClient

LOW_RUNWAY = 10


def cmd_check(_args) -> int:
    thoughts = load_thoughts()
    errors = validate(thoughts)
    for e in errors:
        print(f"ERROR {e}")
    statuses = Counter(t.status for t in thoughts)
    left = schedule.unposted_count(thoughts, schedule.load_history())
    print(f"{len(thoughts)} thoughts: " + ", ".join(f"{n} {s}" for s, n in sorted(statuses.items())))
    print(f"{left} approved thoughts not yet posted")
    return 1 if errors else 0


def cmd_preview(args) -> int:
    thoughts = load_thoughts()
    plan = schedule.upcoming(thoughts, schedule.load_history(), args.days, schedule.today_local())
    for day, number, thought in plan:
        text = format_post(thought, number)
        header = f"{day:%a %b %d} | #{number} | {thought.id} | {weighted_length(text)}/{MAX_POST_LENGTH}"
        if args.markdown:
            print(f"**{header}**\n\n```text\n{text}\n```\n")
        else:
            print(f"--- {header}\n{text}\n")
    return 0


def cmd_post(args) -> int:
    thoughts = load_thoughts()
    errors = validate(thoughts)
    if errors:
        print("Refusing to post; content/thoughts.yaml has problems:")
        for e in errors:
            print(f"  {e}")
        return 1

    history = schedule.load_history()
    today = schedule.today_local()
    if schedule.posted_on(history, today):
        print(f"Already posted for {today}; nothing to do.")
        return 0

    thought = schedule.pick_next(thoughts, history)
    if thought is None:
        print("No approved thoughts in content/thoughts.yaml.")
        return 1

    number = len(history) + 1
    text = format_post(thought, number)
    print(text)
    print(f"\n[{thought.id}, {weighted_length(text)}/{MAX_POST_LENGTH} chars]")

    if not args.live:
        print("Dry run: nothing posted. Pass --live to post.")
        return 0

    try:
        post_id = XClient.from_env().create_post(text)
    except PostError as e:
        print(f"::error::{e}")
        return 1

    history.append(schedule.log_entry(thought, number, today, post_id))
    schedule.save_history(history)
    print(f"Posted: https://x.com/i/status/{post_id}")

    left = schedule.unposted_count(thoughts, history)
    if left < LOW_RUNWAY:
        print(f"::warning::Only {left} new swing thoughts left before reruns start. Add more to content/thoughts.yaml.")
    return 0


def cmd_whoami(_args) -> int:
    try:
        username = XClient.from_env().whoami()
    except PostError as e:
        print(f"::error::{e}")
        return 1
    print(f"::notice::X credentials work. Posts will go to @{username}.")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="python -m bot")
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("check", help="validate the swing thought bank").set_defaults(func=cmd_check)

    preview = sub.add_parser("preview", help="show upcoming posts")
    preview.add_argument("days", nargs="?", type=int, default=7)
    preview.add_argument("--markdown", action="store_true", help="format for a GitHub job summary")
    preview.set_defaults(func=cmd_preview)

    post = sub.add_parser("post", help="post today's swing thought")
    post.add_argument("--live", action="store_true", help="actually post (default is a dry run)")
    post.set_defaults(func=cmd_post)

    sub.add_parser("whoami", help="check X credentials without posting").set_defaults(func=cmd_whoami)

    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
