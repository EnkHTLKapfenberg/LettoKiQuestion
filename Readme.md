# 1. Projektbeschreibung

Das Projekt hat das Ziel, eine Grundlage für eine KI-basierte Beantwortung von Freitextfragen für LETTO zu legen.

# 2. Grundsätzlicher Ablauf

Im Rahmen eines Tests wird den Schülern eine Freitextfrage gestellt. Die Schülerantworten können von LETTO in einen JSON-String [exportiert](https://doc.letto.at/wiki/FreitextExport/) werden. Dieser ist zu kopieren und in das Eingabetextfeld einzufügen. Wenn man den Button `Test beurteilen` klickt, werden die Schülerantworten zusammen mit einer Musterlösung und einer Bewertungsvorschrift anonymisiert an ChatGPT gesendet. ChatGPT liefert:

- Feedback für den Schüler
- Einen Bewertungsvorschlag

Diese Informationen werden auf einer GUI angezeigt.

# 3. Anleitung

## 3.1 Voraussetzungen

Vorab wird Folgendes benötigt:

- API-Key von OpenAI (siehe auch [Readme_API_Token.md](Readme_API_Token.md))
- Prompt für OpenAI (siehe [Prompt.txt](Prompt.txt))
- Freitextfrage in LETTO

## 3.2 OpenAI API Token

Den Token von OpenAI beziehen (siehe [Readme_API_Token.md](Readme_API_Token.md)). Den Token in den [LETTO Bibliotheks-Einstellungen](https://doc.letto.at/wiki/FreitextExport/) eintragen.

## 3.3 Vorbereitung der Fragen

Jede Freitextfrage benötigt folgende Informationen:

- Aufgabenstellung für den Schüler
- Musterlösung
- Bewertungsvorschrift

## 3.4 Aufgabenstellung

Die Frage sollte so formuliert werden, dass die Bewertung einfach und nachvollziehbar möglich ist.

## 3.5 Musterlösung

Hier wird die zu erwartende Lösung beschrieben. Die Musterlösung muss in LETTO im [Feedback](https://doc.letto.at/wiki/Feedback/) hinterlegt werden.&#x20;

Tagbeispiel: [Q0]

## 3.6 Bewertungsvorschrift

Hier wird beschrieben, wie und nach welchen Kriterien die Bewertung durchzuführen ist. Die Bewertungsvorschrift muss in LETTO im [Feedback](https://doc.letto.at/wiki/Feedback/) hinterlegt werden.

Tagbeispiel: [Q0, ai]

Beispiel:

```
Maximal erreichbare Punkte: 100%
Bewertungskriterien und Gewichtungen:

1. Geringerer Durchmesser und leichtere Verlegbarkeit (20%)
   - Vollständige Erläuterung: 20%
   - Teilpunkte (z.B. Durchmesser oder Verlegbarkeit genannt, aber nicht beides): 10%

2. Geringere mechanische Kräfte im Kurzschlussfall durch größere Abstände (15%)
   - Vollständige Erläuterung: 15%
   - Teilpunkte (z.B. nur die Erwähnung der Kräfte, ohne auf den Kurzschlussfall einzugehen): 7,5%

3. Geringere kapazitive Verluste (15%)
   - Vollständige Erläuterung (Einleiterkabel haben eine geringere Kapazität als mehradrige Kabel): 15%
   - Teilpunkte (z.B. nur die Erwähnung geringerer Verluste ohne Erklärung der Kapazität): 7,5%

4. Niedrigere induktive Spannungsabfälle (15%)
   - Vollständige Erläuterung: 15%
   - Teilpunkte (z.B. nur die Erwähnung des Spannungsabfalls ohne Bezug zur Induktivität): 7,5%

5. Bessere Wärmeableitung (20%)
   - Vollständige Erläuterung (Größere Oberfläche im Verhältnis zum Querschnitt): 20%
   - Teilpunkte (z.B. nur die Erwähnung der besseren Wärmeableitung ohne Angabe des Verhältnisses): 10%

6. Reduzierung von induzierten Spannungen und Störungen (15%)
   - Vollständige Erläuterung (Bezug auf parallele Verlegung und mögliche Störungen): 15%
   - Teilpunkte (z.B. nur die Erwähnung der induzierten Spannungen ohne Bezug zur parallelen Verlegung): 7,5%

Gesamtbewertung:

- Die Punkte für jede richtige oder teilweise richtige Antwort werden addiert.
- Teilpunkte sind möglich, falls ein Schüler eine Begründung nur teilweise korrekt darstellt.

```


# 4. Prompting

In der Datei [Prompt.txt](Prompt.txt) befindet sich das Template für den Prompt, der an ChatGPT gesendet wird. Das Prompt kann natürlich angepasst werden, dabei ist auf Folgendes zu achten:

- Die Beschreibungen der Ein- und Ausgabeformate sollten nicht geändert werden, sonst funktioniert das Python-Skript nicht mehr.
- Der Platzhalter `{INPUT_JSON}` wird für den Eingabe-JSON-String verwendet.
- Alle Schülerangaben, alle Musterlösungen und alle Bewertungsvorschriften befinden sich im Eingangs-JSON-String.
- Im Prompt kann beschrieben werden, wie z.B. das Feedback aussehen soll: an den Schüler gerichtet, nachvollziehbare Bewertung, etc.
- [Prompting Tipps](https://www.iqesonline.net/bildung-digital/ki-unterricht-lernen/prompting-tipps/)

# 5. Dateien

- **BuildEXE.bat** - Erstellt aus der Python-Datei eine EXE-Datei
- **CheckLettoQuestion.py** - Das Python-Skript
- **Prompt.txt** - Das Prompt-Template
- **Readme_API_Token.md** - Beschreibt, wie man zum API-Token kommt
