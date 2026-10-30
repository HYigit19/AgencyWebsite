"""Baut die devunoxAI-Website: kopiert den Ordner site/ nach dist/.

Cloudflare Pages ruft dieses Skript bei jedem Push auf (Build command: python3 build.py,
Build output directory: dist). Es gibt keinen weiteren Build-Schritt.
"""
import shutil
from pathlib import Path

ROOT = Path(__file__).parent
SRC, OUT = ROOT / "site", ROOT / "dist"

if OUT.exists():
    shutil.rmtree(OUT)
shutil.copytree(SRC, OUT)

# Demo-Apps ohne fremde Server ausliefern (Schriften und Bibliotheken lokal)
import sys
sys.path.insert(0, str(ROOT / "tools"))
from localize_demos import localize
for p in sorted((OUT / "demos").glob("*.html")):
    localize(p)

# sitemap.xml aus den Seiten erzeugen: jede Seite mit Canonical und ohne noindex,
# mit ihren hreflang-Alternativen. Neue Seiten landen so automatisch in der Sitemap.
import re
from html import escape

def sitemap_entries():
    for p in sorted(OUT.rglob("*.html")):
        s = p.read_text(encoding="utf-8", errors="ignore")
        head = s.split("</head>", 1)[0]
        if re.search(r'<meta[^>]*noindex', head):
            continue
        m = re.search(r'<link[^>]*rel="canonical"[^>]*>', head)
        if not m:
            continue
        loc = re.search(r'href="([^"]+)"', m.group(0)).group(1)
        alts = []
        for tag in re.findall(r'<link[^>]*hreflang="[^"]+"[^>]*>', head):
            if 'rel="alternate"' in tag:
                alts.append((re.search(r'hreflang="([^"]+)"', tag).group(1), re.search(r'href="([^"]+)"', tag).group(1)))
        yield loc, alts

urls = []
for loc, alts in sitemap_entries():
    links = "".join(f'\n    <xhtml:link rel="alternate" hreflang="{escape(h)}" href="{escape(u)}"/>' for h, u in alts)
    urls.append(f"  <url>\n    <loc>{escape(loc)}</loc>{links}\n  </url>")
(OUT / "sitemap.xml").write_text(
    '<?xml version="1.0" encoding="UTF-8"?>\n'
    '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">\n'
    + "\n".join(urls) + "\n</urlset>\n", encoding="utf-8")
print(f"sitemap.xml mit {len(urls)} Seiten erzeugt")

print(f"{sum(1 for p in OUT.rglob('*') if p.is_file())} Dateien nach {OUT} kopiert")
