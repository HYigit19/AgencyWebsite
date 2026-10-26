/**
 * Kontaktformular der devunoxAI-Website (Cloudflare Pages Function)
 * POST /api/contact  ->  E-Mail an CONTACT_TO (Standard: yigit@devunox-consulting.com)
 *
 * Versand, in dieser Reihenfolge:
 *   1. Service-Binding "MAILER" auf den Worker devunox-kontakt-mailer (workers/kontakt-mailer, kostenlos über Email Routing)
 *   2. Binding "EMAIL" (send_email), falls im Pages-Projekt verfügbar
 *   3. Cloudflare Email Service REST-API mit CF_ACCOUNT_ID und CF_EMAIL_TOKEN (Secret, Workers Paid)
 *
 * Variablen im Pages-Projekt (Settings → Variables and Secrets):
 *   CF_ACCOUNT_ID   Cloudflare-Konto-ID
 *   CF_EMAIL_TOKEN  API-Token mit Berechtigung zum Senden von E-Mails (als Secret)
 *   CONTACT_TO      optional, Empfänger (Standard yigit@devunox-consulting.com)
 *   CONTACT_FROM    optional, Absender auf der eingerichteten Domain (Standard kontakt@devunox.ai)
 */

const DEFAULT_TO = "yigit@devunox-consulting.com";
const DEFAULT_FROM = "kontakt@devunox.ai";
const TOPICS_MAX = 60, NAME_MAX = 120, COMPANY_MAX = 160, MAIL_MAX = 200, MSG_MAX = 5000;

const json = (body, status = 200) =>
  new Response(JSON.stringify(body), { status, headers: { "content-type": "application/json; charset=utf-8", "cache-control": "no-store" } });

const clean = (v, max) => String(v ?? "").replace(/\r\n?/g, "\n").replace(/[\u0000-\u0008\u000B\u000C\u000E-\u001F\u007F]/g, "").trim().slice(0, max);
const oneLine = (v, max) => clean(v, max).replace(/\s+/g, " ");
const esc = (s) => s.replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
const isMail = (s) => /^[^\s@<>()",;:]+@[^\s@<>()",;:]+\.[^\s@<>()",;:]{2,}$/.test(s);

async function readBody(request) {
  const type = request.headers.get("content-type") || "";
  if (type.includes("application/json")) return await request.json();
  const fd = await request.formData();
  return Object.fromEntries(fd.entries());
}

export async function onRequestPost({ request, env }) {
  // Nur Anfragen von der eigenen Website annehmen
  const origin = request.headers.get("origin");
  if (origin) {
    let ok = false;
    try { ok = new URL(origin).host === new URL(request.url).host; } catch (e) { ok = false; }
    if (!ok) return json({ ok: false, error: "origin" }, 403);
  }

  let data;
  try { data = await readBody(request); } catch (e) { return json({ ok: false, error: "invalid" }, 400); }

  // Spam-Schutz: verstecktes Feld muss leer bleiben, Formular nicht schneller als 3 Sekunden abgeschickt
  if (clean(data.website, 200)) return json({ ok: true });
  const elapsed = Number(data.t);
  if (Number.isFinite(elapsed) && elapsed >= 0 && elapsed < 3000) return json({ ok: true });

  const name = oneLine(data.name, NAME_MAX);
  const company = oneLine(data.company, COMPANY_MAX);
  const email = oneLine(data.email, MAIL_MAX);
  const topic = oneLine(data.topic, TOPICS_MAX);
  const message = clean(data.message, MSG_MAX);
  const lang = data.lang === "en" ? "en" : "de";

  if (!name || !isMail(email)) return json({ ok: false, error: "missing" }, 422);

  const to = env.CONTACT_TO || DEFAULT_TO;
  const from = env.CONTACT_FROM || DEFAULT_FROM;
  const when = new Date().toLocaleString("de-DE", { timeZone: "Europe/Berlin", dateStyle: "medium", timeStyle: "short" });
  const subject = `Neue Anfrage über devunox.ai: ${topic || "Kontakt"} – ${name}${company ? " (" + company + ")" : ""}`.slice(0, 200);

  const rows = [["Name", name], ["Firma", company || "–"], ["E-Mail", email], ["Thema", topic || "–"], ["Sprache", lang.toUpperCase()], ["Eingang", when + " Uhr"]];
  const text = `Neue Anfrage über das Kontaktformular auf devunox.ai\n\n${rows.map(([k, v]) => `${k}: ${v}`).join("\n")}\n\nNachricht:\n${message || "(keine Nachricht)"}\n\nAntworten: einfach auf diese E-Mail antworten oder an ${email} schreiben.`;
  const html = `<div style="font-family:Arial,Helvetica,sans-serif;font-size:15px;line-height:1.5;color:#141417">
<h2 style="margin:0 0 12px;font-size:18px">Neue Anfrage über devunox.ai</h2>
<table style="border-collapse:collapse;margin-bottom:16px">${rows.map(([k, v]) => `<tr><td style="padding:4px 16px 4px 0;color:#5c5c6b;vertical-align:top">${esc(k)}</td><td style="padding:4px 0">${k === "E-Mail" ? `<a href="mailto:${esc(v)}">${esc(v)}</a>` : esc(v)}</td></tr>`).join("")}</table>
<div style="background:#f4f4f6;border-radius:10px;padding:14px 16px;white-space:pre-wrap">${esc(message || "(keine Nachricht)")}</div>
<p style="color:#5c5c6b;font-size:13px;margin-top:16px">Antworten: einfach auf diese E-Mail antworten oder an <a href="mailto:${esc(email)}">${esc(email)}</a> schreiben.</p></div>`;

  try {
    // Kostenloser Weg: Mail-Worker "devunox-kontakt-mailer" über Service-Binding MAILER (Email Routing)
    if (env.MAILER && typeof env.MAILER.send === "function") {
      await env.MAILER.send({ subject, text, html, replyTo: email, replyName: name });
      return json({ ok: true });
    }
    if (env.EMAIL && typeof env.EMAIL.send === "function") {
      await env.EMAIL.send({ to, from: { email: from, name: "devunoxAI Website" }, replyTo: { email, name }, subject, text, html });
      return json({ ok: true });
    }
    if (!env.CF_ACCOUNT_ID || !env.CF_EMAIL_TOKEN) {
      console.error("Kontaktformular: CF_ACCOUNT_ID oder CF_EMAIL_TOKEN fehlt");
      return json({ ok: false, error: "not_configured" }, 503);
    }
    const send = (extra) => fetch(`https://api.cloudflare.com/client/v4/accounts/${env.CF_ACCOUNT_ID}/email/sending/send`, {
      method: "POST",
      headers: { authorization: `Bearer ${env.CF_EMAIL_TOKEN}`, "content-type": "application/json" },
      body: JSON.stringify(Object.assign({ from, to, subject, text, html }, extra)),
    });
    // Erst mit Reply-To (Antworten gehen direkt an die anfragende Person); wird der Header abgelehnt, ohne ihn
    let res = await send({ headers: { "Reply-To": email } });
    let out = await res.json().catch(() => ({}));
    if (res.status >= 400 && res.status < 500 && res.status !== 401 && res.status !== 403) {
      res = await send({});
      out = await res.json().catch(() => ({}));
    }
    if (!res.ok || out.success === false) {
      console.error("Kontaktformular: Versand fehlgeschlagen", res.status, JSON.stringify(out.errors || out).slice(0, 500));
      return json({ ok: false, error: "send_failed" }, 502);
    }
    return json({ ok: true });
  } catch (e) {
    console.error("Kontaktformular: Fehler", e && (e.code || e.message));
    return json({ ok: false, error: "send_failed" }, 502);
  }
}

export const onRequestGet = () => json({ ok: false, error: "method" }, 405);
