/* Google-Ads-Conversion-Messung, nur nach Einwilligung.
   Inaktiv, solange ADS_ID leer ist: dann lädt nichts und es erscheint kein Hinweis.
   Aktivieren: ADS_ID ("AW-…") und LEAD_LABEL (Conversion-Label der Aktion „Anfrage“) aus Google Ads eintragen
   und den Abschnitt zu Google Ads in der Datenschutzerklärung ergänzen. */
(function () {
  var ADS_ID = "";      // z. B. "AW-123456789"
  var LEAD_LABEL = "";  // z. B. "AbCdEfGhIjK12" (Google Ads > Ziele > Conversions > Tag einrichten)
  if (!ADS_ID) return;

  var de = (document.documentElement.lang || "de").slice(0, 2) === "de";
  var KEY = "ads-consent", loaded = false;
  var t = de
    ? { text: "Wir möchten messen, welche Anzeigen zu Anfragen führen (Google Ads). Dafür setzen wir Cookies, aber nur mit Ihrer Einwilligung.", yes: "Einverstanden", no: "Ablehnen", more: "Datenschutz", link: "Cookie-Einstellungen", privacy: "datenschutz.html" }
    : { text: "We would like to measure which ads lead to enquiries (Google Ads). This sets cookies, but only with your consent.", yes: "Accept", no: "Decline", more: "Privacy", link: "Cookie settings", privacy: "privacy.html" };
  var get = function () { try { return localStorage.getItem(KEY); } catch (e) { return null; } };
  var set = function (v) { try { localStorage.setItem(KEY, v); } catch (e) {} };

  function load() {
    if (loaded) return; loaded = true;
    window.dataLayer = window.dataLayer || [];
    window.gtag = function () { window.dataLayer.push(arguments); };
    window.gtag("consent", "default", { ad_storage: "granted", ad_user_data: "granted", ad_personalization: "denied", analytics_storage: "denied" });
    window.gtag("js", new Date());
    window.gtag("config", ADS_ID);
    var s = document.createElement("script"); s.async = true;
    s.src = "https://www.googletagmanager.com/gtag/js?id=" + encodeURIComponent(ADS_ID);
    document.head.appendChild(s);
  }
  function lead(kind) {
    if (loaded && LEAD_LABEL) window.gtag("event", "conversion", { send_to: ADS_ID + "/" + LEAD_LABEL, event_label: kind });
  }
  // Anfragen: Formular gesendet (main.js meldet "site:lead"), Klick auf Telefon, E-Mail, WhatsApp oder Terminbuchung
  document.addEventListener("site:lead", function (ev) { lead(ev.detail || "form"); });
  document.addEventListener("click", function (ev) {
    var a = ev.target.closest && ev.target.closest("a[href]");
    if (!a) return;
    var h = a.getAttribute("href") || "";
    if (/^(tel:|mailto:)|wa\.me\/|calendar\.google\.com|calendar\.app\.google|#termin$/.test(h)) lead("contact-click");
  });

  function banner() {
    if (document.getElementById("ads-consent")) return;
    var b = document.createElement("div");
    b.id = "ads-consent"; b.setAttribute("role", "dialog"); b.setAttribute("aria-live", "polite");
    b.style.cssText = "position:fixed;left:16px;right:16px;bottom:16px;z-index:9999;max-width:520px;margin:0 auto;background:var(--card,#fff);color:var(--fg,#141417);border:1px solid var(--line,#d9d9e1);border-radius:20px;padding:18px 20px;box-shadow:0 24px 60px -20px rgba(0,0,0,.35);font:400 .95rem/1.5 inherit";
    var pl = document.querySelector('footer a[href*="datenschutz"], footer a[href*="privacy"]');
    var priv = pl ? pl.getAttribute("href") : t.privacy;
    b.innerHTML = '<p style="margin:0 0 12px">' + t.text + ' <a href="' + priv + '" style="color:inherit">' + t.more + '</a></p>' +
      '<div style="display:flex;gap:10px;flex-wrap:wrap"><button type="button" data-v="1" class="btn btn-o" style="cursor:pointer">' + t.yes + '</button>' +
      '<button type="button" data-v="0" class="btn btn-line" style="cursor:pointer">' + t.no + '</button></div>';
    b.addEventListener("click", function (ev) {
      var v = ev.target.getAttribute && ev.target.getAttribute("data-v");
      if (v === null) return;
      set(v === "1" ? "yes" : "no");
      b.remove();
      if (v === "1") load();
    });
    document.body.appendChild(b);
  }

  // Einstellungen jederzeit änderbar: Link im Footer
  function footerLink() {
    var base = document.querySelector(".f-base div") || document.querySelector(".foot-base span:last-child") || document.querySelector("footer");
    if (!base) return;
    var a = document.createElement("a");
    a.href = "#"; a.textContent = t.link; if (base.matches && base.matches(".foot-base span:last-child")) base.appendChild(document.createTextNode(" · "));
    a.addEventListener("click", function (ev) { ev.preventDefault(); banner(); });
    base.appendChild(a);
  }

  var start = function () {
    footerLink();
    var v = get();
    if (v === "yes") load(); else if (v !== "no") banner();
  };
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", start); else start();
})();
