# Leitfaden Workshop Lobby-Maschine

19.11.2026

## Überblick

In 3 Stunden baut jede der 10 Personen einen KI-Agenten der Lobby-Maschine, und am Ende laufen alle Agenten einmal gemeinsam. Die ersten 45 Minuten führt die Leitung vor, wie ein Agent entsteht. Danach bauen alle selbst.

**Die Lobby-Maschine** ist ein Lobbyunternehmen für Klimaschutz aus 10 Agenten in 4 Bereichen: Lagebild, Steuerung und Lernen, Inhalte und Öffentlichkeit, Kontakte und Netzwerk. Die Liste aller Agenten steht im Anhang.

**Ein Agent besteht aus drei Dateien:**

| Datei | Rolle | Wer arbeitet daran |
| --- | --- | --- |
| `anweisung.md` | Der Kopf: wer der Agent ist, Regeln, Ausgabeformat | Alle |
| `agent.py` | Der Motor: Input lesen, KI fragen, Ergebnis ablegen | Wer Python kann |
| `config.yaml` | Die Einstellungen: welche KI, welches Modell, Denken an oder aus | Alle |

**Am Ende des Workshops** liegen 10 Agentenordner im Repository, jeder mit einem Testlauf, und die Kette hat einmal das Beispielthema Elektrifizierung durchgespielt.

**Beispielthema:** eine Elektrifizierungsstrategie für Deutschland. Grundlage ist das [Briefing von Germanwatch](https://www.germanwatch.org/de/93538) „Elektrifizierung als Schlüssel für Resilienz und Wettbewerbsfähigkeit“ vom Juli 2026. Es fordert von der Bundesregierung eine eigene Elektrifizierungsstrategie, zum Beispiel eine Stromsteuer unter dem Niveau der Gassteuer, schnellere Netzanschlüsse und mehr flexible Stromnutzung.

**Rollen der Leitung:** Eine Person führt vor und tippt die Prompts in Claude Code am Beamer. Eine zweite Person geht herum, hilft bei Technikfragen und achtet auf die Zeit.

**So sind die Prompts gedacht:** Alle Texte in grauen Kästen tippt ihr wörtlich in Claude Code ein. Wörter in eckigen Klammern wie [Name] ersetzt ihr durch eure eigenen Angaben.

## Zeitplan

Der Workshop dauert 180 Minuten: 45 für die Vorführung, 60 für das eigene Bauen, dazwischen Verteilen und Pause, am Ende Probelauf und Rückblick.

| Uhr | Dauer | Block | Wer |
| --- | --- | --- | --- |
| 0:00 | 10 Min. | Einstieg: Idee, Schaubild, Ablauf | Leitung |
| 0:10 | 10 Min. | Technik-Check bei allen | Alle |
| 0:20 | 45 Min. | Teil 1: Vorführung, Agent Klartext entsteht | Leitung am Beamer |
| 1:05 | 15 Min. | Teil 2: Agenten verteilen, Schnittstellen klären | Alle |
| 1:20 | 10 Min. | Pause | |
| 1:30 | 60 Min. | Teil 3: Jede Person baut ihren Agenten | Alle, Leitung hilft |
| 2:30 | 20 Min. | Teil 4: Probelauf der ganzen Kette | Leitung am Beamer |
| 2:50 | 10 Min. | Rückblick und nächste Schritte | Alle |

**Puffer:** Wenn die Vorführung länger dauert, kürzt ihr Schritt 7 in Teil 1 (Denken einschalten). Die Bauzeit sollte nicht unter 50 Minuten fallen.

## Vorbereitung vor Beginn

Die Leitung erledigt diese Punkte vor dem Workshop, damit die 3 Stunden für das Bauen bleiben.

### Am Vortag

- [ ] **Repository bereit machen:** Die Lobby-Maschine liegt im Team-Repository [AGENTS_PARASITE-](https://github.com/CorpsHackeur/AGENTS_PARASITE-), lokal unter `~/Documents/GitHub/AGENTS_PARASITE-`. Claude Code dort in einer neuen Sitzung öffnen, damit der Befehl `/klartext` geladen wird, und eingeben:

```text
Hol den neuesten Stand von GitHub, richte die Python-Umgebung ein und starte Klartext einmal mit tests/klartext/elektrifizierung.txt.
```

- [ ] **Team freischalten** (nur wenn die Teilnehmenden nicht schon über den Team-Account Zugriff haben):

```text
Gib dem Team [Team-Name] in unserem GitHub-Account Schreibrechte für das Repository AGENTS_PARASITE-.
```

- [ ] **Schnittstellen vorbereiten** mit diesem Prompt in Claude Code:

```text
Erstelle die Datei schnittstellen.md für die Lobby-Maschine. Sie hat zehn Agenten: Politikmonitoring, Recherche, Akteursanalyse, Strategie, Freigabeprüfung, Positionspapiere, Öffentlichkeitsarbeit, Gesprächsvorbereitung, Bündnisarbeit, Wirkungsanalyse. Lege für jeden Agenten fest, von wem er Input bekommt und welches Ausgabeformat er liefert. Das Format ist immer Markdown mit festen Überschriften. Halte es kurz: eine Tabelle und pro Agent ein Formatbeispiel. Committe die Datei danach auf main und lade sie auf GitHub hoch.
```

- [ ] **Startskript für den Probelauf bauen** mit diesem Prompt:

```text
Baue lobby_core/start.py. Es soll alle Agenten in agents/ in der Reihenfolge des Schaubilds starten: Politikmonitoring, Recherche, Akteursanalyse, Strategie, Positionspapiere, Öffentlichkeitsarbeit, Gesprächsvorbereitung, Bündnisarbeit, Freigabeprüfung, Wirkungsanalyse. Jeder Agent bekommt als Input die neuesten Ergebnisse seiner Zulieferer aus dem Postfach, laut schnittstellen.md. Fehlt ein Agent noch, überspringe ihn mit einem Hinweis. Teste es mit Klartext.
```

- [ ] **Entscheiden, wie die Laptops der Teilnehmenden an ein Modell kommen.** Nur der Leitungsrechner hat LM Studio. Zwei Wege:
  - **Gemeinsamer Server:** LM Studio nimmt Anfragen aus dem lokalen Netzwerk an. Die Adresse des Leitungsrechners steht für alle Agenten in der Datei `ki_server.yaml` im Projektordner, zum Beispiel `http://192.168.1.182:1234`. Zehn Personen teilen sich ein Modell, Anfragen warten also kurz aufeinander.
  - **Claude über die API:** Dazu muss `lobby_core/ki.py` vorher um Claude erweitert werden, und ihr braucht einen Workshop-Schlüssel mit Ausgabelimit.
- [ ] **Ausprobieren:** Einen Laptop aus der Gruppe einmal komplett durchspielen, vom Holen des Repositorys bis zum Testlauf.
- [ ] **Freigaben einrichten,** damit Claude die üblichen Befehle ohne Rückfrage ausführt. Sonst klicken zehn Personen ständig auf „Erlauben“:

```text
Richte für dieses Repository Freigaben ein, damit du ohne Rückfrage git-Befehle, die Befehle von LM Studio (lms) und das Starten der Agenten mit .venv/bin/python ausführen darfst. Lege dazu die Einstellungsdatei im Ordner .claude an und lade sie auf GitHub hoch, damit alle sie bekommen.
```

### 30 Minuten vor Beginn

- [ ] LM Studio auf dem Leitungsrechner öffnen. Dann Claude Code im Repository-Ordner öffnen und eingeben:

```text
Starte den Server von LM Studio und lade das Modell qwen/qwen3.6-27b mit 32.768 Tokens Kontext. Prüfe danach, ob es bereit ist.
```

- [ ] Die Server-Adresse für das Workshop-WLAN eintragen:

```text
Finde die IP-Adresse dieses Rechners im aktuellen WLAN. Trage sie in ki_server.yaml als http://[IP-Adresse]:1234 ein, committe die Änderung auf main und lade sie auf GitHub hoch.
```

- [ ] Claude Code im Repository-Ordner öffnen und mit `/klartext tests/klartext/elektrifizierung.txt` einen Testlauf machen.
- [ ] Beamer anschließen, Schrift in Claude Code und im Terminal groß stellen.
- [ ] Das Schaubild der Lobby-Maschine bereitlegen.

## Teil 1: Vorführung, Agent Klartext entsteht (0:20, 45 Min.)

Die Gruppe sieht am Beamer in 8 Schritten, wie ein Agent vom Steckbrief bis zum Pull Request entsteht. Klartext ist schon fertig vorbereitet. Ihr zeigt den Bauweg an den echten Dateien und verbessert den Agenten live.

**Vorher prüfen:** Claude Code ist im Repository-Ordner geöffnet, und zwar in einer neuen Sitzung, sonst kennt Claude den Befehl `/klartext` nicht.

### Schritt 1: Was läuft hier? (3 Min.)

```text
Zeig uns kurz, was auf diesem Rechner für unsere Agenten bereitsteht: Läuft LM Studio, welches Modell ist geladen, wie groß ist der Kontext? Antworte in 4 kurzen Punkten.
```

**Botschaft an die Gruppe:** Das Modell läuft hier auf dem Laptop. Claude ist nur unser Assistent beim Bauen.

### Schritt 2: Steckbrief (7 Min.)

Fragt zuerst die Gruppe: Was soll ein Agent für Leichte Sprache können? Dann:

```text
Wir bauen einen Agenten namens Klartext. Er übersetzt Texte aus Politik und Verwaltung in Leichte Sprache. Schreib uns einen Steckbrief mit Name, Aufgabe, Input, Output und Grenzen. Nur hier im Chat, lege noch keine Datei an.
```

### Schritt 3: Vom Steckbrief zur Anweisung (8 Min.)

```text
Öffne agents/00-klartext/anweisung.md. Erkläre in 5 Punkten, wie aus dem Steckbrief diese Anweisung geworden ist. Zeig dabei die Regeln für Leichte Sprache und das feste Ausgabeformat.
```

**Botschaft:** Die Anweisung ist der wichtigste Teil. Hier entscheidet sich, wie gut der Agent arbeitet.

### Schritt 4: Der Motor (7 Min.)

```text
Erkläre agent.py und config.yaml im Ordner agents/00-klartext so, dass auch Menschen ohne Programmierkenntnisse es verstehen. Gehe agent.py in 4 Schritten durch: Einstellungen laden, Input holen, KI fragen, Ergebnis ablegen.
```

### Schritt 5: Erster Lauf (5 Min.)

```text
/klartext tests/klartext/elektrifizierung.txt
```

Danach einmal ohne Datei, mit einem Text, den jemand aus der Gruppe vorschlägt:

```text
/klartext
```

Claude fragt dann nach dem Text. Den Text einfügen und abschicken.

**Hinweis zum Datenschutz:** Was ihr in Claude Code einfügt, liest Claude mit. Übersetzt wird lokal. Soll ein Text den Rechner gar nicht verlassen, startet ihr den Agenten im Terminal (siehe Anhang).

### Schritt 6: Verbessern (8 Min.)

Die Gruppe sucht Schwächen im Ergebnis. Typisch sind: Prozentzahlen trotz Verbot, Aufzählungen, die in Satzstücke zerfallen, und Sätze, die den Ausgangstext falsch wiedergeben. Dann:

```text
Im Ergebnis von Klartext sind diese Schwächen: [Schwächen aus der Gruppe]. Schärfe die Anweisung so nach, dass das nicht mehr passiert. Ändere nur agents/00-klartext/anweisung.md und zeig mir, was du geändert hast.
```

Danach Schritt 5 wiederholen und beide Ergebnisse vergleichen.

**Botschaft:** Agenten baut man in Runden. Testen, Schwächen benennen, Anweisung nachschärfen.

### Schritt 7: Denken einschalten (5 Min., kürzbar)

```text
Stelle in agents/00-klartext/config.yaml das Denken auf an und starte Klartext noch einmal mit derselben Datei. Vergleiche danach Dauer und Ergebnis mit dem letzten Lauf in 3 Punkten.
```

Am Ende das Denken wieder ausschalten, sonst sind alle weiteren Läufe deutlich langsamer.

### Schritt 8: Sichern (2 Min.)

```text
Leg einen Branch agent/klartext an, committe die Änderungen an agents/00-klartext und stell einen Pull Request mit einer kurzen Beschreibung.
```

## Teil 2: Agenten verteilen, Schnittstellen klären (1:05, 15 Min.)

Nach 15 Minuten hat jede Person genau einen Agenten und weiß, was sie liefert und was sie bekommt.

1. **Verteilen (5 Min.):** Jede Person wählt oder zieht einen der 10 Agenten aus dem Anhang. Namen auf dem Schaubild notieren.
2. **Nachbarn sprechen sich ab (7 Min.):** Wer im Schaubild verbunden ist, klärt gemeinsam: Was genau liefere ich dir? Welche Überschriften hat mein Ergebnis? Grundlage ist die vorbereitete Datei `schnittstellen.md`.
3. **Änderungen festhalten (3 Min.):** Die Leitung trägt Änderungen am Beamer ein:

```text
Ändere in schnittstellen.md Folgendes: [Absprachen der Gruppen]. Behalte den restlichen Inhalt bei und committe die Änderung direkt auf main, damit alle sie gleich haben.
```

Danach holen alle den neuen Stand, mit diesem Prompt in ihrem Claude Code:

```text
Hol den neuesten Stand von GitHub.
```

**Warum das wichtig ist:** Die Agenten lesen gegenseitig ihre Ergebnisse. Passt ein Format nicht, bricht im Probelauf die Kette.

## Teil 3: Jede Person baut ihren Agenten (1:30, 60 Min.)

In 60 Minuten baut jede Person ihren Agenten nach dem Vorbild von Klartext, testet ihn und stellt einen Pull Request. Diese Seite könnt ihr für die Teilnehmenden einzeln ausdrucken.

### B1: Startklar machen (5 Min.)

Claude Code im Repository-Ordner öffnen und eingeben:

```text
Hol den neuesten Stand von GitHub. Richte die Python-Umgebung für dieses Projekt ein, falls es sie noch nicht gibt. Prüfe dann, ob du das Modell unter der Adresse in ki_server.yaml erreichst. Antworte in 3 kurzen Punkten.
```

Meldet Claude, dass das Modell nicht erreichbar ist, gebt der Leitung Bescheid.

### B2: Agentenordner anlegen (10 Min.)

Nummer und Namen eures Agenten findet ihr im Anhang, zum Beispiel `01-politikmonitoring`.

```text
Ich baue den Agenten [Name] der Lobby-Maschine. Seine Aufgabe: [Aufgabe]. Sein Input: [Input]. Sein Output: [Output]. Lege nach dem Vorbild von agents/00-klartext einen Ordner agents/[Nummer-name]/ an mit anweisung.md, agent.py und config.yaml. Übernimm das Ausgabeformat für meinen Agenten aus schnittstellen.md. Zeig mir danach die Anweisung.
```

Lest die Anweisung in Ruhe. Passt sie zu eurem Agenten? Wenn nicht, sagt Claude, was fehlt.

### B3: Testeingabe erstellen (5 Min.)

```text
Erstelle eine kurze Testeingabe für meinen Agenten zum Thema Elektrifizierungsstrategie für Deutschland in tests/[name]/eingabe.md. Sie soll so aussehen wie das, was mein Agent laut schnittstellen.md von seinen Zulieferern bekommt. Kennzeichne sie oben als erfundenes Beispiel.
```

### B4: Testen und verbessern (25 Min.)

```text
Starte meinen Agenten mit tests/[name]/eingabe.md und zeig mir das Ergebnis unverändert.
```

Prüft das Ergebnis mit drei Fragen: Macht der Agent seine Aufgabe? Hält er das Ausgabeformat ein? Erfindet er etwas? Dann:

```text
Das Ergebnis hat diese Schwächen: [Schwächen]. Ändere nur meine anweisung.md, damit das nicht mehr passiert, und starte den Agenten erneut.
```

Diese Runde zwei- bis dreimal wiederholen.

**Nur für Python-Kundige, wenn Zeit bleibt:**

```text
Erweitere meine agent.py so, dass sie [zum Beispiel: den Inhalt einer Webseite liest / mehrere Eingabedateien zusammenführt]. Erkläre mir danach jede geänderte Zeile.
```

### B5: Pull Request stellen (10 Min.)

```text
Leg einen Branch agent/[name] an, committe nur meinen Agentenordner und meine Testdaten und stell einen Pull Request mit einer kurzen Beschreibung, was mein Agent kann.
```

Dann prüft eine Nachbarin oder ein Nachbar euren Pull Request auf GitHub und gibt ihn frei.

**Regel:** Jede Person ändert nur ihren eigenen Agentenordner. So gibt es keine Konflikte.

## Teil 4: Probelauf und Rückblick (2:30, 30 Min.)

Im Probelauf spielen alle fertigen Agenten das Thema Elektrifizierungsstrategie für Deutschland einmal nacheinander durch. Danach schaut die Gruppe gemeinsam, wo die Kette hakt.

### Probelauf (20 Min.)

1. **Pull Requests übernehmen.** Die Leitung am Beamer:

```text
Zeig mir alle offenen Pull Requests in diesem Repository. Übernimm alle, die nur einen eigenen Agentenordner und Testdaten ändern, nach main. Nenne mir die, bei denen das nicht so ist.
```

2. **Kette starten:**

```text
Hol den neuesten Stand von main und starte lobby_core/start.py zum Thema Elektrifizierungsstrategie für Deutschland. Zeig nach jedem Agenten eine Zeile: wer lief, wie lange, welche Datei im Postfach landete.
```

3. **Gemeinsam anschauen:** Die Gruppe öffnet einzelne Ergebnisse im Ordner `postfach`. Jede Person schaut, ob ihr Agent bekommen hat, was er brauchte.
4. **Schwachstellen sammeln:**

```text
Prüfe die Ergebnisse im Postfach von diesem Lauf. Wo passt ein Output nicht zum Format, das der nächste Agent laut schnittstellen.md erwartet? Antworte als Tabelle mit Agent, Problem und Vorschlag.
```

### Rückblick (10 Min.)

Drei Fragen an die Runde:

1. Was hat überrascht, positiv wie negativ?
2. Wo hat das lokale Modell an seine Grenzen gestoßen?
3. Welcher Agent sollte als Nächstes besser werden?

**Ausblick für das nächste Treffen:** Claude als zweite KI einbauen und vergleichen, Agenten nach Zeitplan selbst starten lassen, das Politikmonitoring echte Nachrichtenquellen lesen lassen. Die Tabelle mit den Schwachstellen ist die Aufgabenliste bis dahin.

## Anhang

### Die zehn Agenten

| Ordner | Name | Bereich | Aufgabe | Input | Output |
| --- | --- | --- | --- | --- | --- |
| `01-politikmonitoring` | Politikmonitoring | Lagebild | Beobachtet Politik und Gesetzgebung | Parlamentsseiten, Tagesordnungen, Nachrichten | Lagebericht mit Fristen und Chancen |
| `02-recherche` | Recherche | Lagebild | Liefert belastbare Zahlen und Belege | Studien, Statistiken, Fragen der anderen | Faktenblätter mit Quellen |
| `03-akteursanalyse` | Akteursanalyse | Lagebild | Ermittelt Entscheider und ihre Positionen | Abstimmungen, Reden, Lagebericht | Akteursliste mit Haltung und Einfluss |
| `04-strategie` | Strategie | Steuerung und Lernen | Wählt Themen, setzt Ziele, verteilt Aufträge | Lagebild, Wirkungsbericht | Strategieplan |
| `05-freigabepruefung` | Freigabeprüfung | Steuerung und Lernen | Prüft alles auf Fakten und Regeln, bevor es nach außen geht | Texte, Gesprächsunterlagen, Kampagnen | Freigabe oder Korrekturauftrag |
| `06-positionspapiere` | Positionspapiere | Inhalte und Öffentlichkeit | Schreibt Positionen und Gesetzesvorschläge | Strategieplan, Faktenblätter | Positionspapier, Argumentationshilfen |
| `07-oeffentlichkeitsarbeit` | Öffentlichkeitsarbeit | Inhalte und Öffentlichkeit | Bringt das Thema in Medien und soziale Netzwerke | Positionspapier, Kernbotschaften | Pressemitteilung, Social-Media-Beiträge |
| `08-gespraechsvorbereitung` | Gesprächsvorbereitung | Kontakte und Netzwerk | Bereitet Gespräche mit Entscheidern vor | Akteursliste, Positionspapier | Gesprächsleitfäden, Briefings |
| `09-buendnisarbeit` | Bündnisarbeit | Kontakte und Netzwerk | Gewinnt Verbündete, plant Veranstaltungen | Akteursliste, Strategieplan | Bündnisliste, gemeinsame Erklärung |
| `10-wirkungsanalyse` | Wirkungsanalyse | Steuerung und Lernen | Misst, was die Arbeit bewirkt hat | Rückmeldungen aus Politik und Medien | Wirkungsbericht |

### Nur für Notfall und Datenschutz: Befehle im Terminal

Alle Schritte im Workshop erledigt Claude über die Prompts. Diese Befehle braucht ihr nur, wenn Claude Code nicht weiterkommt oder wenn ein vertraulicher Text den Rechner nicht verlassen darf. Dann verarbeitet das lokale Modell den Text, ohne dass Claude ihn liest.

| Was | Befehl |
| --- | --- |
| Umgebung aktivieren (in jedem neuen Fenster) | `source .venv/bin/activate` |
| Agent mit einer Datei starten | `python agents/00-klartext/agent.py tests/klartext/elektrifizierung.txt` |
| Agent mit eingefügtem Text starten, Ende mit Ctrl+D | `python agents/00-klartext/agent.py` |
| Server von LM Studio starten | `lms server start` |
| Modell mit großem Kontext laden | `lms load qwen/qwen3.6-27b --context-length 32768 -y` |

### Hilfe bei Problemen

| Meldung oder Problem | Lösung |
| --- | --- |
| Claude fragt ständig, ob es einen Befehl ausführen darf | Freigaben aus der Vorbereitung fehlen. Neuesten Stand holen lassen oder einmal „Immer erlauben“ wählen. |
| „LM Studio ist nicht erreichbar“ | Prompt: „Starte den Server von LM Studio.“ Bei einem gemeinsamen Server die Adresse in `ki_server.yaml` prüfen. |
| Antwort dauert sehr lange | In `config.yaml` steht `denken: an`. Auf `aus` stellen lassen. |
| Claude kennt `/klartext` nicht | Neue Sitzung in Claude Code im Repository-Ordner starten |
| Ergebnis hält das Format nicht ein | Format in der Anweisung als festes Beispiel zeigen, Temperatur in `config.yaml` senken |
| Konflikt beim Pull Request | Prüfen, ob Dateien außerhalb des eigenen Ordners geändert wurden. Die Leitung hilft. |
| Text zu lang für das Modell | Modell mit größerem Kontext laden lassen oder Text teilen |
| Im Terminal: `command not found: python` | Umgebung aktivieren: `source .venv/bin/activate` |

**Sicherheitsregel:** API-Schlüssel kommen nie ins Repository. Sie stehen nur in der lokalen Datei `.env`, die Git ignoriert.
