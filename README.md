# Swing Thoughts

An X account that posts one golf swing thought every morning. Each post says
**who it's for** (the miss it fixes), so a reader can skip the ones that aren't
theirs and spot the one that is. Then they take it to the range.

```
content/thoughts.yaml ──> GitHub Actions (daily, 7:17am ET) ──> X API ──> @account
         ▲                         │
   you approve entries             └──> state/posted.json (log, committed back)
```

- **Content** lives in [`content/thoughts.yaml`](content/thoughts.yaml): 60
  thoughts to start, about two months of posts. The bot goes top to bottom and
  only posts entries marked `status: approved`. After the last one it reruns
  the oldest.
- **Posting** is [`bot/`](bot/), about 350 lines of Python. It posts once per
  day at most, even if the job runs twice.
- **Scheduling** is [`.github/workflows/daily-post.yml`](.github/workflows/daily-post.yml).
  Every run is a dry run until you set `X_POSTING_ENABLED` to `true`.

A post looks like this:

```text
Swing Thought #1: "Turn your back to the target."

For: Short, armsy backswings and over-the-top slices.

At the top your back faces the target and the arms just ride along. Turn first. Lift never.

Try it: 5 slow turns with a club across your chest, then hit 10 balls.
```

## Going live: owner checklist

### 1. Create the X account

| Field | Value |
| --- | --- |
| Display name | `Swing Thought of the Day` |
| Handle | Your pick. Ideas: `@SwingThoughtDay`, `@DailySwingThought`, `@SwingThoughtAM` |
| Avatar | [`brand/avatar.png`](brand/avatar.png) (400x400) |
| Header | [`brand/banner.png`](brand/banner.png) (1500x500) |
| Bio | `One swing thought every morning, and who it is for. Take it to the range. Keep the one that clicks.` |

Use a separate email (a `+swing` alias on your existing one works).

Then turn on the **Automated** label. X's developer rules require it for
API-driven accounts: Settings → Your account → Account information →
Automation, and pick your personal account as the managing account.

Post this yourself from the app and pin it (manual posts cost nothing):

```text
New here? Every morning this account posts one swing thought.

Each one says who it's for. Skip the ones that aren't you.

Take today's to the range, hit 10 balls with it, and keep the one that clicks.

Lead side = closer to the target. Trail side = the other one.
```

### 2. Get API keys (while logged in as the new account)

1. Sign in to the X Developer Console as the **bot account**, not your
   personal one. That way the tokens post as the bot.
2. Create an app. Under **User authentication settings**, set permissions to
   **Read and write**. Choose app type "Web App, Automated App or Bot". Any
   URL works for the callback and website, for example this repo's URL.
3. **After** saving Read and write, generate the **Access Token and Secret**
   on the app's Keys and tokens page. Tokens made before the permission change
   can only read, and posting fails with a 403. Creating the app gives you
   only the consumer key, consumer secret, and bearer token. The bearer token
   can't post, so the bot doesn't use it.
4. Buy a small amount of credits. X is pay-per-use: about **$0.015 per text
   post**, so $5 covers most of a year. A post with a link costs $0.20, which
   is why the bot refuses links. Turn off auto-recharge if you want a hard cap.

### 3. Give the keys to GitHub (never paste them into chat)

Repo → Settings → Secrets and variables → Actions:

- **Secrets** tab, add four:

  | GitHub secret | X calls it |
  | --- | --- |
  | `X_API_KEY` | Consumer Key (API Key) |
  | `X_API_SECRET` | Consumer Secret (API Key Secret) |
  | `X_ACCESS_TOKEN` | Access Token |
  | `X_ACCESS_TOKEN_SECRET` | Access Token Secret |
- **Variables** tab, add `X_POSTING_ENABLED` = `true` when you're ready to go
  live. Optional: `POST_TIMEZONE` (default `America/New_York`). It decides what
  counts as "today."

### 4. Test, then go live

Actions → **Daily swing thought** → Run workflow. With the variable unset you
get a dry run: it checks your keys against X without posting, shows which
`@account` they will post as, and the job summary shows the coming week of
posts. Once it's
`true`, a manual run posts for real and commits the log.

Scheduled workflows only run from the repository's **default branch**.

## Editing content

Edit `content/thoughts.yaml` (the GitHub web editor is fine). Rules:

- `for` is the most important line. Name the miss, not the body part.
- Original wording only. Don't paste other people's tips.
- Set `status: draft` on anything you're unsure about. Drafts are never posted.
- Never rename an `id` after it has been posted. The log uses it.

The **Checks** workflow fails if any post is over 280 characters, has a link,
or is missing a field.

## Commands

```bash
pip install -r requirements.txt
python -m bot check          # validate the bank
python -m bot preview 14     # the next two weeks of posts, exactly as they'll go out
python -m bot post           # dry run of today's post
python -m bot whoami         # check X keys (from env vars) without posting
python -m pytest -q
```

## Known limits

- **GitHub cron drifts.** Scheduled runs can start 5 to 30 minutes late. The
  time also moves an hour with daylight saving (cron is UTC).
- **Public repo auto-disable.** GitHub disables schedules in public repos after
  60 days without activity. The daily log commit should count as activity. If
  the schedule is ever disabled, GitHub emails you, and one click in the Actions
  tab turns it back on.
- **Posting is automated. Growth isn't.** The bot can't reply, like, or
  follow: X restricts automated replies and moved like/follow automation to
  its Enterprise tier. Reach on a new account comes from a person replying in
  golf conversations.
