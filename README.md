# devunoxAI Website

Live: **[www.devunox.ai](https://www.devunox.ai)**

Zweisprachige Website (DE/EN) für KI-Automatisierung, Websites, Web-Apps und Dashboards, mit klickbaren Demos. devunoxAI ist eine Marke der DEVUNOX SOLUTIONS Sp. z o.o.

## Struktur

- `site/` – die fertige Website, genau so, wie sie ausgeliefert wird
  - `site/de/`, `site/en/` – Seiten auf Deutsch und Englisch
  - `site/demos/` – die Demos zum Ausprobieren
  - `site/assets/` – Styles, Script, Schriften, Bilder und Video
- `build.py` – kopiert `site/` nach `dist/` (für Cloudflare Pages) und erzeugt dabei `sitemap.xml` aus allen Seiten mit Canonical und ohne noindex
  - stellt in `dist/` alle internen Links auf saubere Adressen um (`/de/websites` statt `websites.html`), passend zu den Canonicals; in `site/` bleiben die Links relativ
  - trägt in der Sitemap `lastmod` aus der Git-Historie ein
- `site/assets/brand/` – Logo (Zeichen und Schriftzug), LinkedIn-Titelbild und Vorschaubilder für Social Media (`og-de.jpg`, `og-en.jpg`)
- `site/robots.txt`, `site/404.html`, `site/_headers` (pages.dev-Adressen und `/demos/*` auf noindex), Favicons im Wurzelordner

Hauptadresse ist https://www.devunox.ai (alle Canonicals zeigen dorthin). devunox.ai ohne www wird per Cloudflare-Weiterleitungsregel dorthin umgeleitet.

## Demos

| Demo | Datei | Quell-Repository |
| --- | --- | --- |
| Workflow und Reklamationen in einer App | `site/demos/suite.html` | `devunox-apps` |
| Arbeitsschutz-App | `site/demos/arbeitsschutz.html` | `arbeitsschutz-app` |
| GeoAuftrag (Feldaufträge mit GPS-Nachweis) | `site/demos/geoauftrag.html` | `geoauftrag` |
| Geschäftsführungs-Cockpit | `site/demos/cockpit.html` | `management-cockpit` |
| QM-App: Qualitätsmanagement für KMU (DE/EN, `#de`/`#en`) | `site/demos/qm.html` | – (Quelle: Claude-Artifact „QM Modul – devunoxAI Demo“) |
| Website für eine Spedition | `site/demos/spedition.html` | – |
| Makler-Suite mit KI: KI-Posteingang, CRM, Workflows, DMS (DE/EN) | `site/demos/makler.html` | – (Quelle: Claude-Artifact „Makler-Suite – Muster Immobilien“) |

Weitere App-Demos: `pod.html` (Proof of Delivery), `anlagencheck.html` (Prüfungen per QR-Code), `wissen.html` (Wissensdatenbank), `cockpit-produktion.html` (Produktions-Cockpit).

**Achtung:** Seit November 2026 sind die Demos hier weiterentwickelt (neues Design, Englisch, geführte Tour). Die Fassung in `site/demos/` ist maßgeblich; eine ältere `index.html` aus einem Quell-Repository würde diese Änderungen überschreiben.

### Demo-Kit (`site/demos/shared-files/demo-kit.js` + `.css`)

Gemeinsam für alle App-Demos:
- **Sprache:** `?lang=de|en` (sonst gespeicherte Wahl, sonst Deutsch), DE|EN-Umschalter in jeder App. Die Website verlinkt deutsche Seiten mit `?lang=de`, englische mit `?lang=en`.
- **Geführte Tour:** Willkommenskarte bei jedem neuen Besuch (neuer Tab), bis die Tour einmal abgeschlossen wurde; Schritte mit Markierung und Mitmach-Klicks, jederzeit überspringbar, Neustart über „Geführte Tour“. `?tour=1` startet die Tour sofort, `?tour=0` zeigt keine Willkommenskarte. Abschlusskarte mit Link zur Terminbuchung.
- **Diagramme:** Balken, Tacho, Ring, Sparkline, Donut (SVG).
- GeoAuftrag mit `embed=1` (eingebettete Handy-Vorschau auf /demos): ohne Tour und Umschalter, eigener Speicherstand.

## Veröffentlichen auf Cloudflare

Das Repository ist mit Cloudflare Pages verbunden.

- Build command: `python3 build.py`
- Build output directory: `dist`

Jede Änderung auf `main` (auch direkt auf github.com bearbeitet) wird automatisch gebaut und ist nach etwa einer Minute live.

## Texte ändern

Die Texte stehen direkt in den HTML-Dateien unter `site/de/` und `site/en/`. Auf github.com die Datei öffnen, Stift-Symbol, Text ändern, „Commit changes“. Dabei nur den Text zwischen den spitzen Klammern ändern, nicht die Tags selbst.

## Kontaktformular

- `functions/api/contact.js` – Cloudflare Pages Function, nimmt das Formular entgegen (Spam-Schutz, Prüfung)
- `workers/kontakt-mailer/` – eigener Worker `devunox-kontakt-mailer`, verschickt die Mail kostenlos über Cloudflare Email Routing an yigit@devunox-consulting.com (Absender kontakt@devunox.ai)
- `wrangler.toml` – verbindet beides (Service-Binding `MAILER`)

Voraussetzungen in Cloudflare: Email Routing auf devunox.ai aktiv (DNS-Einträge gesetzt) und yigit@devunox-consulting.com als bestätigte Zieladresse.

## SEO-Regeln

- Titel höchstens 60 Zeichen, Beschreibung höchstens 160 Zeichen; `og:title`/`og:description` gleich lauten lassen
- Jede Seite: Canonical auf https://www.devunox.ai/…, hreflang de/en/x-default (x-default = deutsche Seite)
- Bilder mit Alt-Text (Demo-Screenshots: „Screenshot: <Name der Demo>“)
- Demos unter `/demos/` werden nicht indexiert; gefunden werden sollen `/de/demos` und `/en/demos`
- Impressum und Datenschutz stehen auf noindex
