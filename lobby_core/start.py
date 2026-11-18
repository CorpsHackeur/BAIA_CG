"""Startet die ganze Lobby-Maschine einmal von vorne bis hinten.

Die Agenten laufen in der Reihenfolge des Schaubilds. Jeder bekommt als Input
das Thema und die neuesten Ergebnisse seiner Zulieferer aus dem Postfach,
so wie es in schnittstellen.md steht. Fehlt ein Agent noch, wird er mit einem
Hinweis übersprungen.

So startest du die Kette (im Projektordner, mit aktiver Umgebung):

    python lobby_core/start.py "Elektrifizierungsstrategie für Deutschland"
    python lobby_core/start.py "Elektrifizierungsstrategie für Deutschland" --material tests/klartext/elektrifizierung.txt

--material gibt dem Politikmonitoring zusätzlich einen Text als Ausgangsmaterial.
Was jeder Agent als Input bekommen hat, liegt danach in postfach/eingaben/.
"""

from __future__ import annotations  # damit es auch mit älterem Python (ab 3.9) läuft

import argparse
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

import yaml

PROJEKT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJEKT))

from lobby_core.postfach import POSTFACH, neueste_datei  # noqa: E402

AGENTEN_ORDNER = PROJEKT / "agents"
STANDARD_THEMA = "Elektrifizierungsstrategie für Deutschland"

# Reihenfolge und Zulieferer laut schnittstellen.md ("Wer liefert wem?").
# Links der Name aus der config.yaml, rechts die Zulieferer.
KETTE: list[tuple[str, list[str]]] = [
    ("politikmonitoring", []),
    ("recherche", ["politikmonitoring"]),
    ("akteursanalyse", ["politikmonitoring"]),
    ("strategie", ["politikmonitoring", "recherche", "akteursanalyse",
                   "wirkungsanalyse"]),  # Wirkungsanalyse stammt aus dem letzten Durchlauf
    ("positionspapiere", ["strategie", "recherche"]),
    ("oeffentlichkeitsarbeit", ["positionspapiere", "strategie"]),
    ("gespraechsvorbereitung", ["akteursanalyse", "positionspapiere"]),
    ("buendnisarbeit", ["akteursanalyse", "strategie"]),
    ("freigabepruefung", ["positionspapiere", "oeffentlichkeitsarbeit",
                          "gespraechsvorbereitung", "buendnisarbeit"]),
    ("wirkungsanalyse", ["freigabepruefung"]),  # plus alle Ergebnisse des Durchlaufs, siehe unten
]

# Farben nur im Terminal, nicht wenn ein anderes Programm (z. B. Claude Code) die Ausgabe liest
if sys.stdout.isatty():
    GRAU, FETT, GELB, ROT, ENDE = "\033[90m", "\033[1m", "\033[33m", "\033[31m", "\033[0m"
else:
    GRAU = FETT = GELB = ROT = ENDE = ""


def finde_agenten() -> dict[str, Path]:
    """Sucht alle Agentenordner und ordnet sie dem Namen aus ihrer config.yaml zu."""
    gefunden = {}
    for ordner in sorted(AGENTEN_ORDNER.iterdir()):
        if not (ordner / "agent.py").is_file():
            continue
        name = None
        try:
            name = yaml.safe_load((ordner / "config.yaml").read_text(encoding="utf-8"))["name"]
        except (FileNotFoundError, KeyError, TypeError, yaml.YAMLError):
            pass
        # Ohne Namen in der config.yaml: Ordnername ohne Nummer, z. B. 02-recherche -> recherche
        gefunden[name or ordner.name.split("-", 1)[-1]] = ordner
    return gefunden


def relativ(pfad: Path) -> str:
    return str(pfad.relative_to(PROJEKT))


def baue_input(thema: str, zulieferer: list[str], dieser_lauf: list[Path],
               material: str | None, alle_des_laufs: bool) -> tuple[str, list[str]]:
    """Setzt den Input für einen Agenten zusammen. Gibt Text und Hinweise zurück."""
    teile = [f"Thema: {thema}"]
    hinweise = []

    if not zulieferer and material:
        teile.append(f"## Ausgangsmaterial\n\n{material.strip()}")

    dateien = []
    for z in zulieferer:
        datei = neueste_datei(z)
        if datei is None:
            hinweise.append(f"kein Ergebnis von {z}")
            teile.append(f"## Input von {z}\n\nKein Ergebnis im Postfach.")
            continue
        if datei not in dieser_lauf and z != "wirkungsanalyse":
            hinweise.append(f"{z} aus früherem Lauf")
        dateien.append(datei)

    # Wirkungsanalyse bekommt zusätzlich alle übrigen Ergebnisse dieses Durchlaufs
    if alle_des_laufs:
        dateien += [d for d in dieser_lauf if d not in dateien]

    for datei in dateien:
        agent = datei.name.split("_", 1)[0]
        inhalt = datei.read_text(encoding="utf-8").strip()
        teile.append(f"## Input von {agent}\nDatei: {datei.name}\n\n{inhalt}")

    teile[0] += "\nGrundlage: " + (", ".join(d.name for d in dateien) or "Thema")
    return "\n\n---\n\n".join(teile) + "\n", hinweise


def starte_agent(ordner: Path, eingabe: Path) -> tuple[int, str]:
    """Startet agent.py mit der Eingabedatei. Gibt Rückgabecode und Ausgabe zurück."""
    lauf = subprocess.run(
        [sys.executable, str(ordner / "agent.py"), str(eingabe)],
        cwd=PROJEKT, capture_output=True, text=True, encoding="utf-8",
    )
    return lauf.returncode, (lauf.stdout + lauf.stderr).strip()


def main() -> None:
    parser = argparse.ArgumentParser(description="Startet alle Agenten der Lobby-Maschine nacheinander.")
    parser.add_argument("thema", nargs="?", default=STANDARD_THEMA, help="Thema des Durchlaufs")
    parser.add_argument("--material", type=Path, help="Text als Ausgangsmaterial für das Politikmonitoring")
    parser.add_argument("--zeigen", action="store_true", help="Ausgabe jedes Agenten vollständig anzeigen")
    args = parser.parse_args()

    material = args.material.read_text(encoding="utf-8") if args.material else None
    agenten = finde_agenten()
    eingaben = POSTFACH / "eingaben"
    eingaben.mkdir(parents=True, exist_ok=True)

    print(f"\n{FETT}Lobby-Maschine startet{ENDE} zum Thema: {args.thema}\n")
    dieser_lauf: list[Path] = []
    start_gesamt = time.time()

    for nr, (name, zulieferer) in enumerate(KETTE, start=1):
        kopf = f"{nr:>2}. {name:<23}"
        ordner = agenten.get(name)
        if ordner is None:
            zeile = f"{kopf} {GELB}übersprungen{ENDE} – noch kein Agent in agents/"
            print(zeile)
            continue

        text, hinweise = baue_input(args.thema, zulieferer, dieser_lauf, material,
                                    alle_des_laufs=(name == "wirkungsanalyse"))
        zeit = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        eingabe = eingaben / f"{name}_{zeit}.md"
        eingabe.write_text(text, encoding="utf-8")

        print(f"{kopf} {GRAU}läuft ({relativ(ordner)}) ...{ENDE}", flush=True)
        vorher = {d: d.stat().st_mtime for d in POSTFACH.glob("*.md")}
        start = time.time()
        code, ausgabe = starte_agent(ordner, eingabe)
        dauer = time.time() - start
        neu = sorted(d for d in POSTFACH.glob("*.md") if vorher.get(d) != d.stat().st_mtime)

        if args.zeigen and ausgabe:
            print(f"{GRAU}{ausgabe}{ENDE}\n")

        if code != 0 or not neu:
            grund = ausgabe.splitlines()[-1] if ausgabe else f"Rückgabecode {code}"
            zeile = f"{kopf} {ROT}Fehler{ENDE} nach {dauer:.0f} s – {grund}"
        else:
            dieser_lauf += neu
            zeile = f"{kopf} fertig in {dauer:.0f} s -> {', '.join(relativ(d) for d in neu)}"
        if hinweise:
            zeile += f" {GRAU}(Hinweis: {'; '.join(hinweise)}){ENDE}"
        print(zeile)

    gelaufen = len(dieser_lauf)
    print(f"\n{FETT}Fertig{ENDE} in {time.time() - start_gesamt:.0f} s. "
          f"{gelaufen} neue Ergebnisse im Postfach, Eingaben in {relativ(eingaben)}/")


if __name__ == "__main__":
    main()
