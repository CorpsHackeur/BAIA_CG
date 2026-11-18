# Schnittstellen der Lobby-Maschine

Diese Datei legt fest, wer wem was liefert. Jeder Agent hält sich genau an das Format seines Abschnitts, denn der nächste Agent liest das Ergebnis.
Änderungen nur nach Absprache mit den Agenten, die das Ergebnis lesen.

## Regeln für alle Agenten

1. **Ablage:** Jedes Ergebnis landet als Markdown-Datei im Postfach: `postfach/<name>_<Datum>_<Uhrzeit>.md`. `<name>` ist der Wert `name` aus der `config.yaml` des Agenten, zum Beispiel `recherche`.
2. **Input:** Ein Agent liest immer das **neueste** Ergebnis seiner Zulieferer aus dem Postfach.
3. **Kopf:** Jedes Ergebnis beginnt mit diesen vier Zeilen:

```markdown
# [Name des Agenten]: [kurzer Titel]
Thema: [Thema des Durchlaufs]
Erstellt von: Lobby-Maschine, Agent [Name]
Grundlage: [Dateinamen der gelesenen Postfach-Ergebnisse oder „Thema“]
```

4. **Überschriften genau übernehmen.** Die `##`-Überschriften unten sind fest. Keine weglassen, keine umbenennen. Gibt es zu einer Überschrift nichts, steht darunter: „Keine Angaben.“
5. **Nichts erfinden.** Jede Zahl und jedes Zitat braucht eine Quelle. Was nicht belegt ist, wird mit **[unbelegt]** markiert.
6. **Keine Privatpersonen.** Personen nur in ihrer öffentlichen Rolle und Funktion.

## Wer liefert wem?

Reihenfolge eines Durchlaufs von oben nach unten.

| Nr. | Agent | Bekommt Input von | Liefert an |
| --- | --- | --- | --- |
| 01 | Politikmonitoring | Thema des Durchlaufs | Recherche, Akteursanalyse, Strategie |
| 02 | Recherche | Politikmonitoring | Strategie, Positionspapiere |
| 03 | Akteursanalyse | Politikmonitoring | Strategie, Gesprächsvorbereitung, Bündnisarbeit |
| 04 | Strategie | Politikmonitoring, Recherche, Akteursanalyse, Wirkungsanalyse (vom letzten Durchlauf) | Positionspapiere, Öffentlichkeitsarbeit, Bündnisarbeit |
| 06 | Positionspapiere | Strategie, Recherche | Öffentlichkeitsarbeit, Gesprächsvorbereitung, Freigabeprüfung |
| 07 | Öffentlichkeitsarbeit | Positionspapiere, Strategie | Freigabeprüfung |
| 08 | Gesprächsvorbereitung | Akteursanalyse, Positionspapiere | Freigabeprüfung |
| 09 | Bündnisarbeit | Akteursanalyse, Strategie | Freigabeprüfung |
| 05 | Freigabeprüfung | Positionspapiere, Öffentlichkeitsarbeit, Gesprächsvorbereitung, Bündnisarbeit | Wirkungsanalyse |
| 10 | Wirkungsanalyse | Freigabeprüfung, alle Ergebnisse des Durchlaufs | Strategie (nächster Durchlauf) |

**Klartext (00)** gehört nicht zur Kette. Er kann jedes Ergebnis zusätzlich in Leichte Sprache übertragen.

## Ausgabeformate

### 01 Politikmonitoring: `politikmonitoring`

```markdown
## Lage in drei Sätzen
## Laufende Verfahren
| Verfahren | Gremium | Stand | Nächster Termin |
## Fristen und Chancen
## Quellen
```

### 02 Recherche: `recherche`

```markdown
## Kernaussagen
## Zahlen und Belege
| Aussage | Zahl | Quelle |
## Gegenargumente und Antworten
## Offene Fragen
## Quellen
```

### 03 Akteursanalyse: `akteursanalyse`

```markdown
## Wer entscheidet
## Akteursliste
| Akteur (Funktion) | Haltung: dafür / dagegen / offen | Einfluss: hoch / mittel / gering | Beleg |
## Mögliche Verbündete
## Quellen
```

### 04 Strategie: `strategie`

```markdown
## Ziel
## Kernbotschaft
## Zielgruppen
## Aufträge an die Agenten
| Agent | Auftrag | Bis wann |
## Risiken
```

### 05 Freigabeprüfung: `freigabepruefung`

```markdown
## Ergebnis
Freigegeben / Freigegeben mit Korrekturen / Nicht freigegeben
## Geprüfte Ergebnisse
| Datei | Ergebnis | Begründung |
## Korrekturaufträge
| Agent | Was zu ändern ist |
## Prüfpunkte
Fakten belegt · Keine erfundenen Personen · Absender genannt · Keine Privatpersonen
```

### 06 Positionspapiere: `positionspapiere`

```markdown
## Unsere Forderung
## Begründung
## Vorschlag für den Gesetzestext
## Antworten auf Einwände
## Quellen
```

### 07 Öffentlichkeitsarbeit: `oeffentlichkeitsarbeit`

```markdown
## Pressemitteilung
## Beiträge für soziale Netzwerke
## Schlagzeilen-Vorschläge
## Hinweis zum Absender
```

### 08 Gesprächsvorbereitung: `gespraechsvorbereitung`

```markdown
## Gesprächspartner (Funktion)
## Ziel des Gesprächs
## Gesprächsleitfaden
## Erwartete Einwände und Antworten
## Unterlagen zum Mitnehmen
```

### 09 Bündnisarbeit: `buendnisarbeit`

```markdown
## Mögliche Bündnispartner
| Organisation | Gemeinsames Interesse | Ansprache |
## Entwurf einer gemeinsamen Erklärung
## Vorschlag für eine Veranstaltung
```

### 10 Wirkungsanalyse: `wirkungsanalyse`

```markdown
## Was hat gewirkt
## Was hat nicht gewirkt
## Schwachstellen in der Kette
| Agent | Problem | Vorschlag |
## Empfehlung für den nächsten Durchlauf
```
