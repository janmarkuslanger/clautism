# clautism — Birthday Flow

Ein lokaler Flow, der täglich prüft, wer heute Geburtstag hat, je nach
**Beziehung** einen passenden Geburtstagstext schreibt und ihn über einen
**Kanal** verschickt. Läuft komplett lokal mit [Ollama](https://ollama.com) und
ist als kleiner DAG mit [Stagehand](https://github.com/janmarkuslanger/stagehand)
gebaut.

## Macht Stagehand hier Sinn?

Ja. Stagehand ist ein Workflow-/Agenten-Framework (DAG) mit eingebautem
**Ollama-Executor** und Template-Ausdrücken (`{{ ... }}`) – genau das, was hier
gebraucht wird. Der Flow besteht aus drei Schritten:

```
find_birthdays  ──▶  compose (Fan-out, 1 LLM-Call pro Person)  ──▶  dispatch
```

- **find_birthdays** (Python): lädt die Personen, filtert auf heute.
- **compose** (Ollama-Agent): schreibt pro Person eine beziehungs-spezifische
  Nachricht. Über Stagehands `over=` Fan-out läuft der Agent einmal je Person.
- **dispatch** (Python): verschickt jede Nachricht über ihren Kanal.

(Das andere Stagehand – die Browser-Automatisierung von Browserbase – wäre hier
*nicht* sinnvoll; Telegram hat eine Bot-API, kein Browser nötig.)

## Architektur / Erweiterbarkeit

```
birthday_flow/
  config.py        # Konfiguration aus Env-Variablen
  people.py        # Personen-Daten laden + Geburtstagslogik
  relations.py     # Beziehung -> Ton/Stil (hier erweitern)
  prompt.py        # System- und Task-Prompt
  flow.py          # der Stagehand-Workflow (Kern)
  channels/
    base.py        # Channel-Interface + Registry
    telegram.py    # erster Kanal: Telegram
    console.py     # Kanal für lokales Testen / Dry-Run
```

**Neuen Kanal hinzufügen, ohne den Kern anzufassen:** eine Datei in
`birthday_flow/channels/` anlegen, eine `Channel`-Klasse mit `name` und
`async def send(...)` definieren und mit `@register_channel` dekorieren. Die
Kanäle werden beim Start automatisch entdeckt (`load_channels()`), und
`dispatch` löst sie nur über die Registry auf – der Flow selbst ändert sich nie.

```python
from birthday_flow.channels.base import Channel, register_channel

@register_channel
class EmailChannel(Channel):
    name = "email"
    async def send(self, recipient: str, message: str) -> None:
        ...
```

In der Personen-Datei verweist dann `"channel": "email"` darauf.

## Datenformat

Minimale Daten pro Person (`data/people.json`, Beispiel siehe
`data/people.example.json`):

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

- `birthday`: `YYYY-MM-DD` (mit Alter) oder `MM-DD` (ohne Jahr).
- `relation`: einer der Schlüssel aus `relations.py` (sonst `default`).
- `recipient`: kanal-spezifische Adresse – bei Telegram die Chat-ID.

## Setup & Ausführen

```bash
pip install -r requirements.txt          # oder: pip install -e .

# Ollama lokal starten
ollama pull qwen2.5
ollama serve

# Personen anlegen (oder das Beispiel nutzen)
cp data/people.example.json data/people.json

# Telegram-Bot-Token setzen (von @BotFather)
export TELEGRAM_BOT_TOKEN="123456:ABC..."

python -m birthday_flow
```

### Lokal testen ohne Versand

```bash
BIRTHDAY_DRY_RUN=1 python -m birthday_flow      # gibt Nachrichten auf der Konsole aus
```

### Konfiguration (Env-Variablen)

| Variable | Default | Zweck |
|---|---|---|
| `OLLAMA_HOST` | `http://localhost:11434` | Ollama-Endpunkt |
| `BIRTHDAY_MODEL` | `qwen2.5` | Ollama-Modell |
| `BIRTHDAY_PEOPLE_FILE` | `data/people.json` | Pfad zur Personen-Datei |
| `BIRTHDAY_DATE` | heute | Datum überschreiben (zum Testen) |
| `BIRTHDAY_DRY_RUN` | aus | alles auf den `console`-Kanal umleiten |
| `TELEGRAM_BOT_TOKEN` | – | für den Telegram-Versand |

### Täglich ausführen (cron)

```cron
0 8 * * *  cd /pfad/zu/clautism && /usr/bin/python -m birthday_flow >> birthday.log 2>&1
```

## Tests

```bash
pytest
```
