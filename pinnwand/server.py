"""Pinnwand der Lobby-Maschine: Texte im Workshop-WLAN teilen.

Start auf dem Leitungsrechner (im Projektordner):
    python3 pinnwand/server.py

Danach öffnen alle im selben WLAN die Adresse, die beim Start angezeigt wird,
zum Beispiel http://192.168.1.182:8080

Die Pinnwand braucht nur Python (ab 3.9), keine zusätzlichen Pakete.
Beiträge werden in pinnwand/daten/beitraege.json gespeichert.

Die Pinnwand ist auch das gemeinsame Postfach der Agenten:
- Agenten im WLAN finden sie von selbst (Rundruf auf UDP-Port 47800).
- Sie erfahren von ihr auch die Adresse von LM Studio, wenn LM Studio
  auf demselben Rechner läuft.
- Ergebnisse aller Laptops landen im Ordner postfach/ dieses Rechners.
"""

from __future__ import annotations

import argparse
import json
import re
import socket
import sys
import threading
import uuid
from datetime import datetime
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, unquote, urlparse

HIER = Path(__file__).resolve().parent
PROJEKT = HIER.parent
sys.path.insert(0, str(PROJEKT))

from lobby_core import netz  # noqa: E402

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


POSTFACH_NAME = re.compile(r"^[A-Za-z0-9-]{1,60}_[0-9_-]{1,40}\.md$")
PORT = netz.PINNWAND_PORTS[0]  # wird beim Start auf den tatsächlich genutzten Port gesetzt


def ki_server_hier() -> bool:
    """Läuft LM Studio auf diesem Rechner?"""
    return netz.ist_lmstudio(f"http://localhost:{netz.KI_PORT}")


def info(fuer_ip: str | None = None) -> dict:
    """Adressen von Pinnwand und LM Studio, so wie ein Gerät im WLAN sie erreicht."""
    ip = netz.ip_fuer(fuer_ip) if fuer_ip else (netz.eigene_ip() or "127.0.0.1")
    return {
        "dienst": netz.DIENST,
        "pinnwand": f"http://{ip}:{PORT}",
        "ki_server": f"http://{ip}:{netz.KI_PORT}" if ki_server_hier() else None,
    }


def neuestes_im_postfach(agent: str) -> Path | None:
    dateien = sorted(POSTFACH.glob(f"{agent}_*.md"))
    return dateien[-1] if dateien else None


def beantworte_rundrufe() -> None:
    """Antwortet Agenten, die per Rundruf im WLAN nach der Pinnwand fragen."""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    try:
        s.bind(("", netz.SUCH_PORT))
    except OSError as fehler:
        print(f"Hinweis: Rundruf-Port {netz.SUCH_PORT} nicht nutzbar ({fehler}). "
              "Agenten finden die Pinnwand dann über die langsamere Suche.")
        return
    while True:
        try:
            daten, absender = s.recvfrom(1024)
            if daten.strip() == netz.SUCH_FRAGE:
                antwort = json.dumps(info(absender[0])).encode("utf-8")
                s.sendto(antwort, absender)
        except OSError:
            continue


class Server(ThreadingHTTPServer):
    daemon_threads = True
    # Unter Windows würde SO_REUSEADDR erlauben, einen belegten Port doppelt zu nutzen
    allow_reuse_address = sys.platform != "win32"


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

    def _lies_json(self):
        """Liest einen JSON-Körper. Gibt ein dict zurück oder None (Fehler ist dann schon gesendet)."""
        try:
            laenge = int(self.headers.get("Content-Length", 0))
        except ValueError:
            laenge = 0
        if laenge <= 0 or laenge > MAX_TEXT * 4 + 10_000:
            self._fehler(413, "Leer oder zu groß")
            return None
        try:
            daten = json.loads(self.rfile.read(laenge).decode("utf-8"))
        except (ValueError, UnicodeDecodeError):
            daten = None
        if not isinstance(daten, dict):
            self._fehler(400, "Ungültige Daten")
            return None
        return daten

    def do_GET(self):
        url = urlparse(self.path)
        pfad = url.path
        if pfad == "/api/info":
            return self._json(info(self.client_address[0]))
        if pfad == "/api/postfach/neuestes":
            agent = parse_qs(url.query).get("agent", [""])[0]
            if not re.fullmatch(r"[A-Za-z0-9-]{1,60}", agent):
                return self._fehler(400, "Ungültiger Agentenname")
            datei = neuestes_im_postfach(agent)
            if datei is None:
                return self._fehler(404, "Kein Ergebnis von diesem Agenten")
            return self._json({"name": datei.name, "text": datei.read_text(encoding="utf-8", errors="replace")})
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
        pfad = urlparse(self.path).path
        if pfad == "/api/postfach":
            return self._postfach_ablegen()
        if pfad != "/api/beitraege":
            return self._fehler(404, "Nicht gefunden")
        daten = self._lies_json()
        if daten is None:
            return

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

    def _postfach_ablegen(self):
        """Ein Agent von einem anderen Laptop legt sein Ergebnis ins gemeinsame Postfach."""
        daten = self._lies_json()
        if daten is None:
            return
        name = str(daten.get("name", ""))
        text = str(daten.get("text", ""))
        if not POSTFACH_NAME.fullmatch(name):
            return self._fehler(400, "Ungültiger Dateiname")
        if not text.strip():
            return self._fehler(400, "Leeres Ergebnis")
        POSTFACH.mkdir(exist_ok=True)
        ziel = POSTFACH / name
        with _sperre:
            if not ziel.exists():  # nie ein vorhandenes Ergebnis überschreiben
                ziel.write_text(text[:MAX_TEXT], encoding="utf-8")
        self._json({"abgelegt": name}, 201)

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
    parser.add_argument("--port", type=int, help="fester Port (Standard: erster freie von 8080–8082)")
    args = parser.parse_args()

    global PORT
    server = None
    for port in ([args.port] if args.port else netz.PINNWAND_PORTS):
        try:
            server = Server(("0.0.0.0", port), Handler)
            PORT = port
            break
        except OSError:
            print(f"Port {port} ist belegt.")
    if server is None:
        raise SystemExit("Kein freier Port gefunden. Läuft die Pinnwand vielleicht schon?")

    threading.Thread(target=beantworte_rundrufe, daemon=True).start()

    ip = netz.eigene_ip()
    print("Pinnwand läuft.")
    print(f"  Auf diesem Rechner:   http://localhost:{PORT}")
    if ip:
        print(f"  Für alle im WLAN:     http://{ip}:{PORT}")
    else:
        print("  Kein WLAN gefunden: nur auf diesem Rechner erreichbar.")
    if ki_server_hier():
        print(f"  LM Studio läuft hier: Agenten im WLAN finden ihn automatisch ({ip or 'localhost'}:{netz.KI_PORT}).")
    else:
        print("  LM Studio läuft nicht auf diesem Rechner. Agenten suchen ihn selbst im WLAN.")
    print("Agenten finden die Pinnwand automatisch. Beenden mit Strg+C.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nPinnwand beendet.")
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
