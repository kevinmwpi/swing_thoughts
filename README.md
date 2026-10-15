# Swing Thought of the Day

**One golf swing thought every morning on X.** Take it to the range. Keep the
one that clicks.

There are hundreds of ways to think about a golf swing, and most of them won't
do anything for you. Every so often one does, and it changes how you hit the
ball. This account posts one a day so you can keep trying them until you find
yours.

**Follow [@thinking_golf](https://x.com/thinking_golf) on X** · [see the first post](https://x.com/thinking_golf/status/2110828548982259983)

## What you get each morning

```text
Swing Thought #1: "Turn your back to the target."

For: Short, armsy backswings and over-the-top slices.

At the top your back faces the target and the arms just ride along. Turn first. Lift never.

Try it: 5 slow turns with a club across your chest, then hit 10 balls.
```

- **The cue.** Short enough to remember on the tee.
- **For.** The miss it fixes. If it isn't your miss, skip it.
- **The feel.** What it should feel like, in plain words.
- **Try it.** One drill for the range, when there is one.

## How to use them

1. **Read the "For" line first.** Swing thoughts are personal. One that cures
   a slice can make a hook worse.
2. **Give it 10 balls.** On the range, hit 10 shots thinking only about
   today's cue. A new feel takes a few swings to show up.
3. **Write down the ones that click.** Keep a note on your phone. Your own
   short list beats anyone's list of tips.
4. **Take one to the course, not five.** Pick a single cue for the round and
   leave the rest in the car.

New to the terms? **Lead** is the side of your body closer to the target (the
left side for a right-handed golfer). **Trail** is the other side.

## Browse them all

Every swing thought, past and upcoming, is in
[`content/thoughts.yaml`](content/thoughts.yaml). Search the page for your
miss (slice, hook, fat, thin, putts) to find the ones meant for you.

## Where the ideas come from

Most are classic teaching images coaches have used for decades. Some come from
specific teachers and books, and the post names them: Ernest Jones, Harvey
Penick, Ben Hogan, Jack Nicklaus, Dave Pelz, John Novosel, and Gabriele Wulf's
research on attention and learning. All of them are written in our own words.

These are ideas to try, not a lesson. A teaching pro who can watch you swing
will beat any tip. If something hurts, stop.

## Suggest a swing thought

Have a cue that changed your game?
[Open an issue](https://github.com/kevinmwpi/swing_thoughts/issues/new) with:

- the cue itself,
- who it's for (the miss it fixes),
- what it should feel like.

Good ones join the rotation.

## How it works

The account is labeled **Automated** on X because a script does the posting.
A person picks every swing thought that goes into the rotation.

- The swing thoughts live in [`content/thoughts.yaml`](content/thoughts.yaml).
- Each morning around 7am Eastern, a GitHub Action posts the next one through
  the X API ([`bot/`](bot/)).
- Every post is logged in [`state/posted.json`](state/posted.json).

Want to run your own? See [docs/SETUP.md](docs/SETUP.md).
