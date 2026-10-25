# Nexvio Website

Zweisprachige Website (DE/EN) für KI-Automatisierung, Websites, Web-Apps und Dashboards. Nexvio ist ein Arbeitsname und eine Marke der DEVUNOX SOLUTIONS Sp. z o.o.

## Struktur

- `content.py` – alle Texte der Seiten (DE und EN)
- `legal.py` – Impressum und Datenschutzerklärung
- `src/` – Styles, Script und lokal eingebundene Schriften
- `build.py` – erzeugt die fertige Website
- `dist/` – fertige Website; wird bei jedem Build automatisch erzeugt und liegt nicht im Repository

## Bauen

```
python3 build.py
```

## Veröffentlichen auf Cloudflare

Workers & Pages → Create → Pages → Connect to Git → dieses Repository wählen.

- Build command: `python3 build.py`
- Build output directory: `dist`

Jede Änderung auf `main` (auch direkt auf github.com bearbeitet) wird automatisch gebaut und ist nach etwa einer Minute live. Andere Branches bekommen einen Vorschau-Link.

## Texte ändern

Alle Seitentexte stehen in `content.py`, Impressum und Datenschutz in `legal.py`. Auf github.com die Datei öffnen, Stift-Symbol, Text zwischen den Anführungszeichen ändern, „Commit changes“. Anführungszeichen und Kommas dabei nicht löschen.
