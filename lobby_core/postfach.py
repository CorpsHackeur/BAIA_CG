"""Das Postfach: Hier legen Agenten ihre Ergebnisse ab und holen sie ab.

Jedes Ergebnis ist eine Markdown-Datei im Ordner postfach/,
benannt nach Agent und Uhrzeit, zum Beispiel:
    postfach/klartext_2026-11-19_10-42-07.md

Läuft im WLAN die Pinnwand, ist das Postfach automatisch gemeinsam:
- ablegen() schickt jedes Ergebnis zusätzlich an die Pinnwand.
- neueste_datei() holt neuere Ergebnisse anderer Laptops von der Pinnwand.
Ohne Pinnwand bleibt alles lokal auf diesem Rechner.
"""

from __future__ import annotations  # damit es auch mit älterem Python (ab 3.9) läuft

import json
import time
from datetime import datetime
from pathlib import Path
from urllib.error import HTTPError
from urllib.parse import quote
from urllib.request import Request

from lobby_core.netz import finde_pinnwand, oeffne

POSTFACH = Path(__file__).resolve().parent.parent / "postfach"

_pinnwand: list = []  # einmal pro Programmlauf suchen: [] = noch nicht gesucht, [None] = keine da


def pinnwand() -> str | None:
    """Adresse der Pinnwand im WLAN, oder None. Wird nur einmal pro Lauf gesucht."""
    if not _pinnwand:
        _pinnwand.append(finde_pinnwand())
    return _pinnwand[0]


def _an_pinnwand(datei: Path) -> None:
    adresse = pinnwand()
    if not adresse:
        return
    daten = json.dumps({"name": datei.name, "text": datei.read_text(encoding="utf-8")}).encode("utf-8")
    try:
        oeffne(Request(f"{adresse}/api/postfach", data=daten,
                       headers={"Content-Type": "application/json"}), 5).close()
    except Exception:
        pass  # Pinnwand gerade weg: Ergebnis liegt trotzdem lokal


def _von_pinnwand(agent: str) -> None:
    """Holt das neueste Ergebnis eines Agenten von der Pinnwand ins lokale Postfach."""
    adresse = pinnwand()
    if not adresse:
        return
    try:
        with oeffne(f"{adresse}/api/postfach/neuestes?agent={quote(agent)}", 5) as r:
            daten = json.load(r)
    except HTTPError:
        return  # 404: die Pinnwand hat nichts von diesem Agenten
    except Exception:
        return
    name = Path(str(daten.get("name", ""))).name  # nur ein Dateiname, kein Pfad
    if name.startswith(f"{agent}_") and name.endswith(".md"):
        ziel = POSTFACH / name
        if not ziel.exists():
            POSTFACH.mkdir(exist_ok=True)
            ziel.write_text(str(daten.get("text", "")), encoding="utf-8")


def ablegen(agent: str, inhalt: str) -> Path:
    """Speichert ein Ergebnis im Postfach und gibt den Dateipfad zurück."""
    POSTFACH.mkdir(exist_ok=True)
    datei = POSTFACH / f"{agent}_{datetime.now():%Y-%m-%d_%H-%M-%S}.md"
    while datei.exists():  # nie ein älteres Ergebnis überschreiben: auf die nächste Sekunde warten
        time.sleep(0.2)
        datei = POSTFACH / f"{agent}_{datetime.now():%Y-%m-%d_%H-%M-%S}.md"
    datei.write_text(inhalt, encoding="utf-8")
    _an_pinnwand(datei)
    return datei


def neueste_datei(agent: str) -> Path | None:
    """Gibt den Pfad zum jüngsten Ergebnis eines Agenten zurück, oder None.

    Mit Pinnwand im WLAN zählen auch die Ergebnisse der anderen Laptops.
    """
    _von_pinnwand(agent)
    dateien = sorted(POSTFACH.glob(f"{agent}_*.md"))
    return dateien[-1] if dateien else None


def neuestes(agent: str) -> str | None:
    """Holt das jüngste Ergebnis eines Agenten, oder None, wenn es keins gibt."""
    datei = neueste_datei(agent)
    return datei.read_text(encoding="utf-8") if datei else None
