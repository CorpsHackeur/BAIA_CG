"""Das Postfach: Hier legen Agenten ihre Ergebnisse ab und holen sie ab.

Jedes Ergebnis ist eine Markdown-Datei im Ordner postfach/,
benannt nach Agent und Uhrzeit, zum Beispiel:
    postfach/klartext_2026-11-19_10-42.md
"""

from __future__ import annotations  # damit es auch mit älterem Python (ab 3.9) läuft

from datetime import datetime
from pathlib import Path

POSTFACH = Path(__file__).resolve().parent.parent / "postfach"


def ablegen(agent: str, inhalt: str) -> Path:
    """Speichert ein Ergebnis im Postfach und gibt den Dateipfad zurück."""
    POSTFACH.mkdir(exist_ok=True)
    zeit = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    datei = POSTFACH / f"{agent}_{zeit}.md"
    datei.write_text(inhalt, encoding="utf-8")
    return datei


def neuestes(agent: str) -> str | None:
    """Holt das jüngste Ergebnis eines Agenten, oder None, wenn es keins gibt."""
    dateien = sorted(POSTFACH.glob(f"{agent}_*.md"))
    return dateien[-1].read_text(encoding="utf-8") if dateien else None
