# devunoxAI Website

Zweisprachige Website (DE/EN) für KI-Automatisierung, Websites, Web-Apps und Dashboards, mit klickbaren Demos. devunoxAI ist eine Marke der DEVUNOX SOLUTIONS Sp. z o.o.

## Struktur

- `site/` – die fertige Website, genau so, wie sie ausgeliefert wird
  - `site/de/`, `site/en/` – Seiten auf Deutsch und Englisch
  - `site/demos/` – die Demos zum Ausprobieren
  - `site/assets/` – Styles, Script, Schriften, Bilder und Video
- `build.py` – kopiert `site/` nach `dist/` (für Cloudflare Pages)

## Demos

| Demo | Datei | Quell-Repository |
| --- | --- | --- |
| Workflow und Reklamationen in einer App | `site/demos/suite.html` | `devunox-apps` |
| Arbeitsschutz-App | `site/demos/arbeitsschutz.html` | `arbeitsschutz-app` |
| GeoAuftrag (Feldaufträge mit GPS-Nachweis) | `site/demos/geoauftrag.html` | `geoauftrag` |
| Geschäftsführungs-Cockpit | `site/demos/cockpit.html` | `management-cockpit` |
| Website für eine Spedition | `site/demos/spedition.html` | – |

Neue Version einer App: deren `index.html` aus dem Quell-Repository hierher kopieren und unter dem Dateinamen oben speichern.

## Veröffentlichen auf Cloudflare

Das Repository ist mit Cloudflare Pages verbunden.

- Build command: `python3 build.py`
- Build output directory: `dist`

Jede Änderung auf `main` (auch direkt auf github.com bearbeitet) wird automatisch gebaut und ist nach etwa einer Minute live.

## Texte ändern

Die Texte stehen direkt in den HTML-Dateien unter `site/de/` und `site/en/`. Auf github.com die Datei öffnen, Stift-Symbol, Text ändern, „Commit changes“. Dabei nur den Text zwischen den spitzen Klammern ändern, nicht die Tags selbst.
