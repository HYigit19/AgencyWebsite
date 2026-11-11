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

# Demos nie indexieren: zusätzlich zum Header X-Robots-Tag (site/_headers) einen
# robots-Meta-Tag in jede Demo-Seite setzen. So greift noindex auch für neue Demos
# und für Prüfwerkzeuge, die nur das HTML lesen.
import re as _re_robots
for p in sorted((OUT / "demos").glob("*.html")):
    html = p.read_text(encoding="utf-8")
    if _re_robots.search(r'<meta[^>]*name=["\']robots["\']', html, _re_robots.I):
        html = _re_robots.sub(r'<meta[^>]*name=["\']robots["\'][^>]*>', '<meta name="robots" content="noindex, follow">', html, flags=_re_robots.I)
    else:
        html = _re_robots.sub(r'(<head[^>]*>)', r'\1\n<meta name="robots" content="noindex, follow">', html, count=1, flags=_re_robots.I)
    p.write_text(html, encoding="utf-8")

# Eigene JS-/CSS-Dateien mit Inhalts-Version verlinken (style.css?v=1a2b3c4d5e).
# Cloudflare gibt statischen Dateien einen Browser-Cache von mehreren Stunden; ohne Version
# laufen geänderte Seiten sonst mit veralteten Skripten (z. B. dem Demo-Kit).
import hashlib, re as _re_v

_ASSET_REF = _re_v.compile(r'\b(src|href)="(?!https?:|//|data:|#)([^"?#]+\.(?:js|css))"')
_hash_cache = {}

def _version(path):
    if path not in _hash_cache:
        _hash_cache[path] = hashlib.sha1(path.read_bytes()).hexdigest()[:10]
    return _hash_cache[path]

def version_assets(page):
    html = page.read_text(encoding="utf-8")
    def rep(m):
        target = (page.parent / m.group(2)).resolve()
        if not target.is_file() or OUT.resolve() not in target.parents:
            return m.group(0)
        return f'{m.group(1)}="{m.group(2)}?v={_version(target)}"'
    new = _ASSET_REF.sub(rep, html)
    if new != html:
        page.write_text(new, encoding="utf-8")

for p in sorted(OUT.rglob("*.html")):
    version_assets(p)

# Interne Links auf die sauberen Adressen umstellen (/de/websites statt websites.html,
# /de/ statt index.html). Cloudflare Pages leitet .html-Adressen per 308 um; mit sauberen
# Links spart jeder Klick und jeder Crawler-Besuch diese Weiterleitung, und die Links
# entsprechen genau den Canonical-Adressen. In site/ bleiben die Links relativ, damit die
# Seiten auch lokal als Datei funktionieren.
import posixpath, re as _re

def clean_href(href, page_dir):
    if _re.match(r'^(?:[a-z][a-z0-9+.-]*:|//|#)', href, _re.I):
        return href
    m = _re.match(r'^([^?#]*)(.*)$', href)
    path, rest = m.group(1), m.group(2)
    if not path.endswith(".html"):
        return href
    full = path if path.startswith("/") else posixpath.normpath(posixpath.join("/" + page_dir, path))
    if full.endswith("/index.html"):
        full = full[: -len("index.html")]
    else:
        full = full[: -len(".html")]
    return full + rest

for p in sorted(OUT.rglob("*.html")):
    page_dir = p.parent.relative_to(OUT).as_posix()
    page_dir = "" if page_dir == "." else page_dir
    s = p.read_text(encoding="utf-8")
    s2 = _re.sub(r'(<a\b[^>]*?\bhref=")([^"]+)(")', lambda m: m.group(1) + clean_href(m.group(2), page_dir) + m.group(3), s)
    if s2 != s:
        p.write_text(s2, encoding="utf-8")

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
        yield loc, alts, "site/" + p.relative_to(OUT).as_posix()

import subprocess

def lastmod(rel):
    """Datum der letzten Änderung der Quelldatei laut Git (leer, wenn keine Historie da ist)."""
    try:
        out = subprocess.run(["git", "log", "-1", "--format=%cs", "--", rel], cwd=ROOT,
                             capture_output=True, text=True, timeout=20).stdout.strip()
        return out
    except Exception:
        return ""

urls = []
for loc, alts, rel in sitemap_entries():
    links = "".join(f'\n    <xhtml:link rel="alternate" hreflang="{escape(h)}" href="{escape(u)}"/>' for h, u in alts)
    lm = lastmod(rel)
    lm = f"\n    <lastmod>{lm}</lastmod>" if lm else ""
    urls.append(f"  <url>\n    <loc>{escape(loc)}</loc>{lm}{links}\n  </url>")
(OUT / "sitemap.xml").write_text(
    '<?xml version="1.0" encoding="UTF-8"?>\n'
    '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">\n'
    + "\n".join(urls) + "\n</urlset>\n", encoding="utf-8")
print(f"sitemap.xml mit {len(urls)} Seiten erzeugt")

print(f"{sum(1 for p in OUT.rglob('*') if p.is_file())} Dateien nach {OUT} kopiert")
