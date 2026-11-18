# Lobby-Maschine

Die Lobby-Maschine ist ein beispielhaftes Lobbyunternehmen für Klimaschutz, das aus zehn KI-Agenten besteht.
Jede teilnehmende Person des Workshops baut einen Agenten. Die Agenten laufen mit einem lokalen Sprachmodell in LM Studio und geben ihre Ergebnisse über ein gemeinsames Postfach weiter.

Der Ablauf des Workshops mit allen Prompts steht im [Leitfaden](Leitfaden%20Workshop%20Lobby-Maschine.md).

## Aufbau

```
agents/00-klartext/   Demo-Agent: übersetzt schwierige Texte in Leichte Sprache
├── anweisung.md      Der Kopf: wer der Agent ist, Regeln, Ausgabeformat
├── agent.py          Der Motor: Input lesen, KI fragen, Ergebnis ablegen
└── config.yaml       Die Einstellungen: welche KI, welches Modell, Denken an/aus
lobby_core/
├── ki.py             frage_ki(): ein Zugang für alle Sprachmodelle
└── postfach.py       ablegen() und neuestes(): Übergabe zwischen Agenten
ki_server.yaml        Adresse des LM-Studio-Servers, gilt für alle Agenten
postfach/             Hier landen die Ergebnisse (werden nicht hochgeladen)
tests/klartext/       Beispieltext zum Thema Elektrifizierung
```

## Einrichten

In Claude Code im Projektordner:

```text
Richte die Python-Umgebung für dieses Projekt ein und starte Klartext einmal mit tests/klartext/elektrifizierung.txt.
```

Oder von Hand im Terminal:

```bash
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
```

## Agent starten

In Claude Code: `/klartext tests/klartext/elektrifizierung.txt`

Im Terminal:

```bash
.venv/bin/python agents/00-klartext/agent.py tests/klartext/elektrifizierung.txt
```

## LM Studio vorbereiten

Auf dem Rechner mit LM Studio den Server starten und das Modell mit großem Kontext laden:

```bash
lms server start
```

```bash
lms load qwen/qwen3.6-27b --context-length 32768 -y
```

Die Adresse des Servers steht in `ki_server.yaml`. Auf anderen Laptops dort die IP-Adresse des LM-Studio-Rechners eintragen.
