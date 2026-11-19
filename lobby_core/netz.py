"""Findet LM Studio und die Pinnwand automatisch im aktuellen WLAN.

So müssen die Agenten keine IP-Adresse kennen. Die Suche läuft so:

1. Zuletzt gefundene Adresse (gemerkt in .netz.json) – wenn sie noch antwortet
2. Dieser Rechner selbst (localhost)
3. Rundruf ins WLAN: Läuft die Pinnwand, antwortet sie mit ihrer Adresse
   und der Adresse von LM Studio
4. Suche im WLAN: alle Geräte im eigenen Netz auf Port 1234 (LM Studio)
   bzw. 8080–8082 (Pinnwand) abklopfen

Zum Ausprobieren (im Projektordner):
    python -m lobby_core.netz
"""

from __future__ import annotations  # damit es auch mit älterem Python (ab 3.9) läuft

import ipaddress
import json
import socket
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from urllib.request import ProxyHandler, Request, build_opener

PROJEKT = Path(__file__).resolve().parent.parent
MERKZETTEL = PROJEKT / ".netz.json"

KI_PORT = 1234                       # Standard-Port von LM Studio
PINNWAND_PORTS = (8080, 8081, 8082)  # die Pinnwand weicht aus, wenn 8080 belegt ist
PAUSE_OHNE_PINNWAND = 120            # Sekunden: so lange nach erfolgloser Suche nicht neu suchen
SUCH_PORT = 47800                    # UDP-Port für den Rundruf
SUCH_FRAGE = b"LOBBY-MASCHINE?"
DIENST = "lobby-pinnwand"


# ---------- kleine Helfer ----------

# Geräte im WLAN immer direkt ansprechen, nie über einen eingestellten Proxy
_direkt = build_opener(ProxyHandler({}))


def oeffne(anfrage, sekunden: float):
    """Öffnet eine Adresse direkt, ohne Proxy."""
    return _direkt.open(anfrage, timeout=sekunden)


def eigene_ip() -> str | None:
    """IP-Adresse dieses Rechners im aktuellen WLAN (oder None ohne Netz)."""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("10.255.255.255", 1))  # es wird nichts gesendet
        ip = s.getsockname()[0]
        return None if ip.startswith("127.") else ip
    except OSError:
        return None
    finally:
        s.close()


def ip_fuer(ziel: str) -> str:
    """Eigene IP-Adresse, unter der ein bestimmtes Gerät diesen Rechner erreicht."""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect((ziel, 1))
        return s.getsockname()[0]
    except OSError:
        return eigene_ip() or "127.0.0.1"
    finally:
        s.close()


def _hole_json(url: str, sekunden: float = 1.5):
    with oeffne(Request(url, headers={"Accept": "application/json"}), sekunden) as r:
        return json.load(r)


def ist_lmstudio(adresse: str | None) -> bool:
    if not adresse:
        return False
    try:
        return isinstance(_hole_json(adresse.rstrip("/") + "/v1/models").get("data"), list)
    except Exception:
        return False


def ist_pinnwand(adresse: str | None) -> bool:
    if not adresse:
        return False
    try:
        return _hole_json(adresse.rstrip("/") + "/api/info").get("dienst") == DIENST
    except Exception:
        return False


def _port_offen(ip: str, port: int, sekunden: float = 0.4) -> bool:
    try:
        with socket.create_connection((ip, port), timeout=sekunden):
            return True
    except OSError:
        return False


def _lies_merkzettel() -> dict:
    try:
        return json.loads(MERKZETTEL.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}


def _merke(schluessel: str, wert) -> None:
    daten = _lies_merkzettel()
    if daten.get(schluessel) != wert:
        daten[schluessel] = wert
        try:
            MERKZETTEL.write_text(json.dumps(daten, indent=1), encoding="utf-8")
        except OSError:
            pass


# ---------- Rundruf und Suche ----------

def rundruf(sekunden: float = 1.0) -> dict:
    """Fragt per Rundruf im WLAN nach der Pinnwand. Gibt deren Antwort zurück oder {}."""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        s.settimeout(sekunden)
        ziele = ["255.255.255.255"]
        ip = eigene_ip()
        if ip:
            ziele.append(str(ipaddress.ip_network(f"{ip}/24", strict=False).broadcast_address))
        for ziel in ziele:
            try:
                s.sendto(SUCH_FRAGE, (ziel, SUCH_PORT))
            except OSError:
                pass
        while True:
            daten, _ = s.recvfrom(4096)
            try:
                antwort = json.loads(daten.decode("utf-8"))
            except ValueError:
                continue
            if antwort.get("dienst") == DIENST:
                return antwort
    except OSError:  # auch Zeitüberschreitung: niemand hat geantwortet
        return {}
    finally:
        s.close()


def durchsuche_wlan(ports: tuple[int, ...], pruefe) -> str | None:
    """Klopft alle Geräte im eigenen /24-Netz auf den Ports ab. Gibt die erste passende Adresse zurück."""
    ip = eigene_ip()
    if not ip:
        return None
    netz = ipaddress.ip_network(f"{ip}/24", strict=False)
    kandidaten = [(str(h), p) for p in ports for h in netz.hosts()]
    with ThreadPoolExecutor(max_workers=64) as pool:
        offen = [k for k, ok in zip(kandidaten, pool.map(lambda k: _port_offen(*k), kandidaten)) if ok]
    for host, port in offen:
        adresse = f"http://{host}:{port}"
        if pruefe(adresse):
            return adresse
    return None


# ---------- das, was die Agenten benutzen ----------

def finde_ki_server(ausgabe: bool = True) -> str | None:
    """Sucht LM Studio. Gibt z. B. 'http://192.168.1.20:1234' zurück oder None."""
    gemerkt = _lies_merkzettel().get("ki_server")
    if ist_lmstudio(gemerkt):
        return gemerkt

    if ausgabe:
        print("Suche LM Studio im WLAN ...", flush=True)
    kandidaten = [f"http://localhost:{KI_PORT}", rundruf().get("ki_server")]
    adresse = next((k for k in kandidaten if ist_lmstudio(k)), None)
    adresse = adresse or durchsuche_wlan((KI_PORT,), ist_lmstudio)
    if adresse:
        _merke("ki_server", adresse)
        if ausgabe:
            print(f"LM Studio gefunden: {adresse}", flush=True)
    return adresse


def finde_pinnwand(ausgabe: bool = False) -> str | None:
    """Sucht die Pinnwand. Gibt z. B. 'http://192.168.1.20:8080' zurück oder None."""
    merkzettel = _lies_merkzettel()
    gemerkt = merkzettel.get("pinnwand")
    if ist_pinnwand(gemerkt):
        return gemerkt
    if time.time() - merkzettel.get("pinnwand_gesucht", 0) < PAUSE_OHNE_PINNWAND:
        return None  # eben erst vergeblich gesucht: Agent nicht unnötig aufhalten

    if ausgabe:
        print("Suche Pinnwand im WLAN ...", flush=True)
    kandidaten = [rundruf().get("pinnwand")] + [f"http://localhost:{p}" for p in PINNWAND_PORTS]
    adresse = next((k for k in kandidaten if ist_pinnwand(k)), None)
    adresse = adresse or durchsuche_wlan(PINNWAND_PORTS, ist_pinnwand)
    _merke("pinnwand_gesucht", 0 if adresse else int(time.time()))
    if adresse:
        _merke("pinnwand", adresse)
        if ausgabe:
            print(f"Pinnwand gefunden: {adresse}", flush=True)
    return adresse


if __name__ == "__main__":
    print(f"Dieser Rechner: {eigene_ip() or 'kein Netz'}")
    ki = finde_ki_server()
    print(f"LM Studio:      {ki or 'nicht gefunden'}")
    pw = finde_pinnwand(ausgabe=True)
    print(f"Pinnwand:       {pw or 'nicht gefunden'}")
