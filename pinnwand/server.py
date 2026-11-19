"""Pinnwand der Lobby-Maschine: Texte im Workshop-WLAN teilen.

Start auf dem Leitungsrechner (im Projektordner):
    python3 pinnwand/server.py

Danach öffnen alle im selben WLAN die Adresse, die beim Start angezeigt wird,
zum Beispiel http://192.168.1.182:8080

Die Pinnwand braucht nur Python (ab 3.9), keine zusätzlichen Pakete.
Beiträge werden in pinnwand/daten/beitraege.json gespeichert.
Zusätzlich zeigt sie die Ergebnisse aus dem Ordner postfach/ dieses Rechners an.
"""

from __future__ import annotations

import argparse
import json
import socket
import threading
import uuid
from datetime import datetime
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import unquote, urlparse

HIER = Path(__file__).resolve().parent
PROJEKT = HIER.parent
DATEN = HIER / "daten" / "beitraege.json"
POSTFACH = PROJEKT / "postfach"
SEITE = HIER / "index.html"

MAX_TEXT = 200_000  # Zeichen pro Beitrag
MAX_KURZ = 200  # Zeichen für Name und Titel

_sperre = threading.Lock()


def lade_beitraege() -> list[dict]:
    if not DATEN.exists():
        return []
    try:
        return json.loads(DATEN.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return []


def speichere_beitraege(beitraege: list[dict]) -> None:
    DATEN.parent.mkdir(parents=True, exist_ok=True)
    tmp = DATEN.with_suffix(".tmp")
    tmp.write_text(json.dumps(beitraege, ensure_ascii=False, indent=1), encoding="utf-8")
    tmp.replace(DATEN)


def postfach_liste() -> list[dict]:
    if not POSTFACH.is_dir():
        return []
    eintraege = []
    for datei in POSTFACH.glob("*.md"):
        try:
            stat = datei.stat()
            eintraege.append({
                "name": datei.name,
                "agent": datei.stem.split("_", 1)[0],
                "zeit": datetime.fromtimestamp(stat.st_mtime).isoformat(timespec="seconds"),
                "text": datei.read_text(encoding="utf-8", errors="replace")[:MAX_TEXT],
            })
        except OSError:
            continue
    eintraege.sort(key=lambda e: e["zeit"], reverse=True)
    return eintraege


def lokale_ip() -> str:
    """Ermittelt die IP-Adresse dieses Rechners im lokalen Netz."""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("10.255.255.255", 1))  # es wird nichts gesendet
        return s.getsockname()[0]
    except OSError:
        return "127.0.0.1"
    finally:
        s.close()


class Handler(BaseHTTPRequestHandler):
    server_version = "Pinnwand/1.0"

    def log_message(self, fmt, *args):  # ruhigere Ausgabe im Terminal
        pass

    def _json(self, daten, status: int = 200) -> None:
        body = json.dumps(daten, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def _fehler(self, status: int, meldung: str) -> None:
        self._json({"fehler": meldung}, status)

    def do_GET(self):
        pfad = urlparse(self.path).path
        if pfad in ("/", "/index.html"):
            body = SEITE.read_bytes()
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        elif pfad == "/api/beitraege":
            with _sperre:
                self._json(lade_beitraege())
        elif pfad == "/api/postfach":
            self._json(postfach_liste())
        else:
            self._fehler(404, "Nicht gefunden")

    def do_POST(self):
        if urlparse(self.path).path != "/api/beitraege":
            return self._fehler(404, "Nicht gefunden")
        try:
            laenge = int(self.headers.get("Content-Length", 0))
        except ValueError:
            laenge = 0
        if laenge <= 0 or laenge > MAX_TEXT * 4 + 10_000:
            return self._fehler(413, "Beitrag ist leer oder zu groß")
        try:
            daten = json.loads(self.rfile.read(laenge).decode("utf-8"))
        except (ValueError, UnicodeDecodeError):
            return self._fehler(400, "Ungültige Daten")
        if not isinstance(daten, dict):
            return self._fehler(400, "Ungültige Daten")

        text = str(daten.get("text", "")).strip()
        if not text:
            return self._fehler(400, "Bitte einen Text eingeben")
        beitrag = {
            "id": uuid.uuid4().hex[:12],
            "autor": str(daten.get("autor", "")).strip()[:MAX_KURZ] or "Unbekannt",
            "titel": str(daten.get("titel", "")).strip()[:MAX_KURZ],
            "text": text[:MAX_TEXT],
            "zeit": datetime.now().isoformat(timespec="seconds"),
        }
        with _sperre:
            beitraege = lade_beitraege()
            beitraege.insert(0, beitrag)
            speichere_beitraege(beitraege)
        self._json(beitrag, 201)

    def do_DELETE(self):
        pfad = urlparse(self.path).path
        if not pfad.startswith("/api/beitraege/"):
            return self._fehler(404, "Nicht gefunden")
        bid = unquote(pfad.rsplit("/", 1)[-1])
        with _sperre:
            beitraege = lade_beitraege()
            rest = [b for b in beitraege if b.get("id") != bid]
            if len(rest) == len(beitraege):
                return self._fehler(404, "Beitrag nicht gefunden")
            speichere_beitraege(rest)
        self._json({"geloescht": bid})


def main() -> None:
    parser = argparse.ArgumentParser(description="Pinnwand der Lobby-Maschine")
    parser.add_argument("--port", type=int, default=8080, help="Port (Standard: 8080)")
    args = parser.parse_args()

    server = ThreadingHTTPServer(("0.0.0.0", args.port), Handler)
    ip = lokale_ip()
    print("Pinnwand läuft.")
    print(f"  Auf diesem Rechner:   http://localhost:{args.port}")
    print(f"  Für alle im WLAN:     http://{ip}:{args.port}")
    print("Beenden mit Strg+C.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nPinnwand beendet.")
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
