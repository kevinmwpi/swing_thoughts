from datetime import date

import pytest

from bot import __main__ as cli
from bot import schedule
from bot.content import Thought, format_post, load_thoughts, validate, weighted_length


def thought(id, status="approved", drill=None):
    return Thought(id=id, cue="Turn.", audience="Slicers.", feel="Feel it.", drill=drill,
                   phase="backswing", source="test", status=status)


def test_bank_is_valid():
    thoughts = load_thoughts()
    assert validate(thoughts) == []
    assert sum(t.status == "approved" for t in thoughts) >= 30


def test_weighted_length_counts_like_x():
    assert weighted_length("abc") == 3
    assert weighted_length("—") == 1  # em dash is in a 1-weight range
    assert weighted_length("⛳") == 2  # emoji count double
    assert weighted_length("日") == 2  # CJK counts double


def test_format_post_omits_missing_drill():
    assert "Try it" not in format_post(thought("a"), 1)
    post = format_post(thought("a", drill="Hit 10."), 7)
    assert post.startswith('Swing Thought #7: "Turn."')
    assert post.endswith("Try it: Hit 10.")


def test_pick_next_goes_in_order_and_skips_unapproved():
    thoughts = [thought("a", "draft"), thought("b"), thought("c", "retired"), thought("d")]
    assert schedule.pick_next(thoughts, []).id == "b"
    assert schedule.pick_next(thoughts, [{"id": "b"}]).id == "d"


def test_pick_next_recycles_oldest_when_exhausted():
    thoughts = [thought("a"), thought("b")]
    history = [{"id": "a"}, {"id": "b"}, {"id": "a"}]
    assert schedule.pick_next(thoughts, history).id == "b"


def test_upcoming_skips_today_if_already_posted():
    thoughts = [thought("a"), thought("b")]
    plan = schedule.upcoming(thoughts, [{"id": "a", "date": "2026-10-15"}], 1, date(2026, 10, 15))
    assert plan == [(date(2026, 10, 16), 2, thoughts[1])]


@pytest.fixture
def sandbox(tmp_path, monkeypatch):
    """Point the CLI at a temporary post log and a fixed 'today'."""
    state = tmp_path / "posted.json"
    monkeypatch.setattr(schedule, "STATE_PATH", state)
    monkeypatch.setattr(schedule, "today_local", lambda: date(2026, 10, 15))
    return state


class FakeClient:
    posts = []

    @classmethod
    def from_env(cls):
        return cls()

    def create_post(self, text):
        self.posts.append(text)
        return str(1000 + len(self.posts))


def test_post_live_logs_once_per_day(sandbox, monkeypatch):
    FakeClient.posts = []
    monkeypatch.setattr(cli, "XClient", FakeClient)

    assert cli.main(["post", "--live"]) == 0
    assert cli.main(["post", "--live"]) == 0  # second run the same day is a no-op

    history = schedule.load_history()
    assert len(FakeClient.posts) == 1
    assert history[0]["number"] == 1
    assert history[0]["id"] == load_thoughts()[0].id
    assert history[0]["date"] == "2026-10-15"
    assert history[0]["post_id"] == "1001"


def test_dry_run_posts_and_logs_nothing(sandbox, monkeypatch):
    FakeClient.posts = []
    monkeypatch.setattr(cli, "XClient", FakeClient)

    assert cli.main(["post"]) == 0
    assert FakeClient.posts == []
    assert not sandbox.exists()


class FakeResponse:
    def __init__(self, status, body):
        self.status_code, self._body = status, body
        self.ok = 200 <= status < 300
        self.text = str(body)

    def json(self):
        return self._body


def test_x_client_posts_text_and_explains_failures(monkeypatch):
    from bot.x_client import PostError, XClient

    calls = []
    client = XClient("k", "s", "t", "ts")
    monkeypatch.setattr(client._session, "post",
                        lambda url, **kw: calls.append((url, kw)) or FakeResponse(201, {"data": {"id": "42"}}))
    assert client.create_post("hello") == "42"
    assert calls[0][0] == "https://api.x.com/2/tweets"
    assert calls[0][1]["json"] == {"text": "hello"}

    monkeypatch.setattr(client._session, "post", lambda url, **kw: FakeResponse(403, {"title": "Forbidden"}))
    with pytest.raises(PostError, match="Read and write"):
        client.create_post("hello")


def test_x_client_names_missing_secrets(monkeypatch):
    from bot.x_client import ENV_VARS, PostError, XClient

    for name in ENV_VARS:
        monkeypatch.delenv(name, raising=False)
    with pytest.raises(PostError, match="X_API_KEY, X_API_SECRET"):
        XClient.from_env()


def test_x_client_whoami_reads_username(monkeypatch):
    from bot.x_client import XClient

    client = XClient("k", "s", "t", "ts")
    calls = []
    monkeypatch.setattr(client._session, "get",
                        lambda url, **kw: calls.append(url) or FakeResponse(200, {"data": {"username": "SwingBot"}}))
    assert client.whoami() == "SwingBot"
    assert calls == ["https://api.x.com/2/users/me"]
