"""Ein Zugang zu allen Sprachmodellen.

Jeder Agent ruft nur frage_ki() auf. Welche KI dahinter arbeitet,
steht in der config.yaml des Agenten unter "anbieter".

Heute eingebaut:  lokal  (LM Studio auf diesem Rechner)
Später geplant:   claude (Anthropic API)
"""

import json
import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from pathlib import Path

import yaml

# Gemeinsame Server-Adresse für alle Agenten, steht in ki_server.yaml im Projektordner
SERVER_DATEI = Path(__file__).resolve().parent.parent / "ki_server.yaml"


def gemeinsamer_server() -> str:
    """Liest die Adresse des KI-Servers aus ki_server.yaml."""
    try:
        return yaml.safe_load(SERVER_DATEI.read_text(encoding="utf-8"))["server"]
    except (FileNotFoundError, KeyError, TypeError):
        return "http://localhost:1234"


@dataclass
class Antwort:
    text: str          # Die eigentliche Antwort
    denken: str        # Das "laute Nachdenken" des Modells (leer, wenn aus)
    sekunden: float    # Wie lange es gedauert hat
    tokens: int        # Wie viele Tokens das Modell erzeugt hat


def frage_ki(anweisung: str, text: str, einstellungen: dict) -> Antwort:
    """Schickt Anweisung und Text an die KI und gibt die Antwort zurück."""
    anbieter = einstellungen.get("anbieter", "lokal")

    if anbieter == "lokal":
        return _frage_lmstudio(anweisung, text, einstellungen)
    if anbieter == "claude":
        raise NotImplementedError("Claude ist noch nicht eingebaut. Das ergänzen wir im Workshop.")
    raise ValueError(f"Unbekannter Anbieter: {anbieter!r}. Erlaubt sind: lokal, claude")


def _frage_lmstudio(anweisung: str, text: str, einstellungen: dict) -> Antwort:
    """Fragt das Modell über die eigene Schnittstelle von LM Studio."""
    # Eigene Adresse des Agenten, sonst die gemeinsame aus ki_server.yaml
    server = (einstellungen.get("server") or gemeinsamer_server()).rstrip("/")
    anfrage = {
        "model": einstellungen["modell"],
        "system_prompt": anweisung,
        "input": text,
        "reasoning": "on" if einstellungen.get("denken") == "an" else "off",
        "temperature": einstellungen.get("temperatur", 0.3),
        "store": False,
    }

    start = time.time()
    try:
        req = urllib.request.Request(
            f"{server}/api/v1/chat",
            data=json.dumps(anfrage).encode("utf-8"),
            headers={"Content-Type": "application/json"},
        )
        with urllib.request.urlopen(req, timeout=600) as r:
            daten = json.load(r)
    except urllib.error.URLError as fehler:
        raise SystemExit(
            f"LM Studio ist nicht erreichbar ({fehler}).\n"
            "Bitte in LM Studio den Server starten oder im Terminal eingeben: lms server start"
        )

    antwort_teile = [t["content"] for t in daten["output"] if t["type"] == "message"]
    denk_teile = [t["content"] for t in daten["output"] if t["type"] == "reasoning"]

    return Antwort(
        text="\n".join(antwort_teile).strip(),
        denken="\n".join(denk_teile).strip(),
        sekunden=round(time.time() - start, 1),
        tokens=daten.get("stats", {}).get("total_output_tokens", 0),
    )
