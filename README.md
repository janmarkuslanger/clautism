# 🎉 Birthday Flow™ — Disrupting Human Affection Since Right Now

> *"What if love... but as a cron job?"*

Welcome to the future. You used to be the kind of person who **forgot** their own
grandmother's birthday. A monster. A disgrace to the family WhatsApp group.

Not anymore. Now an AI does the loving for you. Runs **100% locally** on
[Ollama](https://ollama.com), orchestrated as a tiny DAG with
[Stagehand](https://github.com/janmarkuslanger/stagehand). **Next level.** 🚀🧠✨

## The Problem We Heroically Solved

Remembering that people exist is *hard*. Caring about them on a specific calendar
day? Practically a full-time job. Birthday Flow™ leverages cutting-edge
**artificial intelligence** to outsource both. Connection, automated. Sincerity,
generated locally at 8 AM by a 7-billion-parameter model that has never met your
mom.

## How It Bringst People Together™

```
find_birthdays ─▶ compose ─▶ tone_check ─▶ dispatch ─▶ ❤️ (allegedly)
```

1. **find_birthdays** (plain Python) — a robot checks if anyone you "love" was
   born today.
2. **compose** (Ollama agent, one call per person via fan-out) — a robot writes
   them something heartfelt, in a tone that matches the relationship.
3. **tone_check** (Ollama agent, one call per person) — *another* robot
   double-checks the first robot's feelings and rewrites them if the vibe is off.
   One layer of simulated affection simply wasn't enough.
4. **dispatch** (plain Python) — a third, deeply judgmental robot hits send.
5. Your grandmother cries. She thinks you wrote it. You were asleep.

(No, the *other* Stagehand — the browser-automation one — would not help here.
Telegram has a Bot API. No browser, no problem.)

## Quick Start (For Visionaries)

```bash
# 1. Install the feelings dependencies
pip install -r requirements.txt          # or: pip install -e .

# 2. Summon the local feelings engine
ollama pull qwen2.5
ollama serve

# 3. List everyone you'd otherwise forget
cp data/people.example.json data/people.json
#   ...then edit data/people.json (see "The Data" below)

# 4. Acquire a robot mouthpiece (token from @BotFather on Telegram)
export TELEGRAM_BOT_TOKEN="123456:ABC..."

# 5. Become a wonderful person, instantly
python -m birthday_flow
```

### Too scared to unleash it on real humans?

Disrupt yourself first — feelings, but only to your terminal:

```bash
BIRTHDAY_DRY_RUN=1 python -m birthday_flow      # routes everything to the console channel
```

### Test a specific day (because waiting for a birthday is so analog)

```bash
BIRTHDAY_DATE=2026-06-23 BIRTHDAY_DRY_RUN=1 python -m birthday_flow
```

## The Data (a.k.a. the people you keep forgetting)

There is no database. There is no cloud. Just a flat **JSON file on disk**,
`data/people.json` (template: `data/people.example.json`). It's `.gitignore`d, so
your loved ones won't end up on GitHub.

```json
[
  {
    "name": "Oma Erna",
    "birthday": "1948-06-23",
    "relation": "grandparent",
    "channel": "telegram",
    "recipient": "111111111",
    "language": "de"
  }
]
```

- `birthday` — `YYYY-MM-DD` (we'll smugly mention the age) or `MM-DD` (we won't).
- `relation` — drives the tone. One of the keys in `relations.py`
  (`grandparent`, `parent`, `sibling`, `partner`, `friend`, `colleague`),
  otherwise `default`.
- `channel` — which delivery channel to use (today: `telegram` or `console`).
- `recipient` — channel-specific address. For Telegram, the chat id.

Loading and the birthday math live in `birthday_flow/people.py`. Data is read into
memory at runtime and never written back. Stagehand does persist per-run state
(including generated messages) under `.stagehand/runs/` — also `.gitignore`d, and
relocatable via `BIRTHDAY_STATE_DIR`.

## Configuration (Env Variables)

| Variable | Default | Purpose |
|---|---|---|
| `OLLAMA_HOST` | `http://localhost:11434` | Ollama endpoint |
| `BIRTHDAY_MODEL` | `qwen2.5` | Ollama model |
| `BIRTHDAY_PEOPLE_FILE` | `data/people.json` | Path to the people file |
| `BIRTHDAY_DATE` | today | Override the date (for testing) |
| `BIRTHDAY_DRY_RUN` | off | Route everything to the `console` channel |
| `BIRTHDAY_STATE_DIR` | `.stagehand/runs` | Where Stagehand stores run state |
| `TELEGRAM_BOT_TOKEN` | – | Required for actually sending via Telegram |

## Omnichannel Disruption 📡 (currently disrupting one (1) channel)

Channels are pluggable and auto-discovered, so adding one requires **zero changes
to the core flow**. Drop a file in `birthday_flow/channels/`, define a `Channel`
subclass with a `name` and an `async send(...)`, decorate it with
`@register_channel`, and you're done:

```python
from birthday_flow.channels.base import Channel, register_channel

@register_channel
class EmailChannel(Channel):
    name = "email"
    async def send(self, recipient: str, message: str) -> None:
        ...
```

Then point a person at it: `"channel": "email"`. The registry finds it on its own.

## Project Layout

```
birthday_flow/
  config.py        # configuration from env variables
  people.py        # load people data + birthday logic
  relations.py     # relation -> tone/style (extend here)
  prompt.py        # system + task prompts (compose & tone_check)
  flow.py          # the Stagehand workflow (the core DAG)
  channels/
    base.py        # Channel interface + registry
    telegram.py    # first channel: Telegram
    console.py     # channel for local testing / dry-run
```

## Run It Daily (cron, for set-and-forget affection)

```cron
0 8 * * *  cd /path/to/clautism && /usr/bin/python -m birthday_flow >> birthday.log 2>&1
```

## Tests

```bash
pytest
```

---

*Birthday Flow™ is not responsible for the slow, dawning realization that the
warmest message your loved ones received this year was statistically
autocompleted by a machine that ran offline while you slept. Bringing people
together. Never forget again. Bla.* ✨
