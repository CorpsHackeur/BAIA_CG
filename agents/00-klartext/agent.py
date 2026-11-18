"""Agent "Klartext": übersetzt schwierige Texte in Leichte Sprache.

So startest du ihn (im Projektordner, mit aktiver Umgebung):

    python agents/00-klartext/agent.py tests/klartext/solarpflicht.txt   Text aus einer Datei
    python agents/00-klartext/agent.py                                  Text einfügen, dann Ctrl+D
"""

import sys
from pathlib import Path

import yaml

# Damit der Agent den gemeinsamen Kern (lobby_core) findet
ORDNER = Path(__file__).resolve().parent
sys.path.insert(0, str(ORDNER.parent.parent))

from lobby_core.ki import frage_ki          # noqa: E402
from lobby_core.postfach import ablegen     # noqa: E402

# Farben nur im Terminal, nicht wenn ein anderes Programm (z. B. Claude Code) die Ausgabe liest
if sys.stdout.isatty():
    GRAU, FETT, ENDE = "\033[90m", "\033[1m", "\033[0m"
else:
    GRAU = FETT = ENDE = ""


def main() -> None:
    # 1. Einstellungen und Anweisung laden
    einstellungen = yaml.safe_load((ORDNER / "config.yaml").read_text(encoding="utf-8"))
    anweisung = (ORDNER / "anweisung.md").read_text(encoding="utf-8")

    # 2. Input holen: aus einer Datei oder direkt eingefügt
    if len(sys.argv) > 1:
        text = Path(sys.argv[1]).read_text(encoding="utf-8")
    else:
        print("Text einfügen und mit Ctrl+D abschließen:\n")
        text = sys.stdin.read()
    if not text.strip():
        raise SystemExit("Kein Text bekommen.")

    # 3. KI fragen
    print(f"\n{FETT}Klartext arbeitet{ENDE} mit {einstellungen['modell']} "
          f"(Denken: {einstellungen.get('denken', 'aus')}) ...\n")
    antwort = frage_ki(anweisung, text, einstellungen)

    if antwort.denken:
        print(f"{GRAU}{antwort.denken}{ENDE}\n")
    print(antwort.text)

    # 4. Ergebnis ins Postfach legen
    datei = ablegen(einstellungen["name"], antwort.text + "\n")
    print(f"\n{GRAU}Fertig in {antwort.sekunden} s, {antwort.tokens} Tokens. "
          f"Gespeichert: {datei.relative_to(ORDNER.parent.parent)}{ENDE}")


if __name__ == "__main__":
    main()
