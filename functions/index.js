/**
 * Startadresse https://www.devunox.ai/ (Cloudflare Pages Function)
 *
 * Leitet serverseitig per 302 auf die passende Sprachversion weiter, statt eine leere
 * noindex-Seite mit JavaScript-Weiterleitung auszuliefern. Suchmaschinen (ohne
 * Accept-Language) landen auf der deutschen Seite, wie es x-default vorgibt.
 *
 * Reihenfolge: gespeicherte Wahl (Cookie devunox-lang, gesetzt beim Sprachwechsel)
 * -> Browsersprache (Accept-Language) -> Deutsch.
 * site/index.html bleibt als Rückfall bestehen, falls die Function einmal nicht läuft.
 */
export function onRequestGet({ request }) {
  const url = new URL(request.url);
  const cookie = request.headers.get("Cookie") || "";
  const saved = (cookie.match(/(?:^|;\s*)devunox-lang=(de|en)\b/) || [])[1];
  const accept = (request.headers.get("Accept-Language") || "").toLowerCase();
  const first = accept.split(",")[0].trim().slice(0, 2);
  const lang = saved || (first && first !== "de" ? "en" : "de");
  const target = new URL(`/${lang}/`, url.origin);
  target.search = url.search;
  return new Response(null, {
    status: 302,
    headers: {
      Location: target.toString(),
      Vary: "Accept-Language, Cookie",
      "Cache-Control": "private, no-store",
    },
  });
}
