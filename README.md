# Nexvio Website

Zweisprachige Website (DE/EN) für KI-Automatisierung, Websites, Web-Apps und Dashboards. Nexvio ist ein Arbeitsname und eine Marke der DEVUNOX SOLUTIONS Sp. z o.o.

## Struktur

- `content.py` – alle Texte der Seiten (DE und EN)
- `legal.py` – Impressum und Datenschutzerklärung
- `src/` – Styles, Script und lokal eingebundene Schriften
- `build.py` – erzeugt die fertige Website
- `dist/` – fertige Website zum Veröffentlichen

## Bauen

```
python3 build.py
```

## Veröffentlichen auf Cloudflare

Workers & Pages → Create → Pages → Connect to Git → dieses Repository wählen.

- Build command: leer lassen
- Build output directory: `dist`

Jeder Push auf `main` geht automatisch live, andere Branches bekommen einen Vorschau-Link.
