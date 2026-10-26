/**
 * devunox-kontakt-mailer: verschickt die Anfragen aus dem Kontaktformular von devunox.ai.
 *
 * Kostenlos über Cloudflare Email Routing (send_email-Binding). Mails gehen nur an die in
 * Email Routing bestätigte Adresse. Absender ist eine Adresse auf devunox.ai.
 *
 * Aufruf ausschließlich über das Service-Binding der Pages-Funktion (RPC: env.MAILER.send(...)).
 * Über die öffentliche URL ist nichts erreichbar (404).
 *
 * Bindings des Workers:
 *   EMAIL  Send-Email-Binding (Ziel: yigit@devunox-consulting.com)
 * Variablen (optional):
 *   MAIL_FROM  Absender, Standard kontakt@devunox.ai
 *   MAIL_TO    Empfänger, Standard yigit@devunox-consulting.com
 */
import { WorkerEntrypoint } from "cloudflare:workers";
import { EmailMessage } from "cloudflare:email";

const b64 = (s) => {
  const bytes = new TextEncoder().encode(s);
  let bin = "";
  for (let i = 0; i < bytes.length; i += 0x8000) bin += String.fromCharCode(...bytes.subarray(i, i + 0x8000));
  return btoa(bin);
};
const wrap = (s) => s.replace(/.{1,76}/g, "$&\r\n");
const hdrWord = (s) => (/^[\x20-\x7E]*$/.test(s) ? s : `=?UTF-8?B?${b64(s)}?=`);
const noBreak = (s) => String(s || "").replace(/[\r\n]+/g, " ").trim();
const addr = (email, name) => (name ? `${hdrWord(noBreak(name).replace(/"/g, "'"))} <${email}>` : `<${email}>`);
const isMail = (s) => /^[^\s@<>()",;:]+@[^\s@<>()",;:]+\.[^\s@<>()",;:]{2,}$/.test(s || "");

export default class Mailer extends WorkerEntrypoint {
  async fetch() {
    return new Response("Not found", { status: 404 });
  }

  /** m = { subject, text, html, replyTo, replyName } */
  async send(m) {
    const from = this.env.MAIL_FROM || "kontakt@devunox.ai";
    const to = this.env.MAIL_TO || "yigit@devunox-consulting.com";
    const domain = from.split("@")[1];
    const boundary = "b_" + crypto.randomUUID().replace(/-/g, "");
    const headers = [
      `From: ${addr(from, "devunoxAI Website")}`,
      `To: <${to}>`,
      isMail(m.replyTo) ? `Reply-To: ${addr(noBreak(m.replyTo), m.replyName)}` : null,
      `Subject: ${hdrWord(noBreak(m.subject).slice(0, 200))}`,
      `Date: ${new Date().toUTCString()}`,
      `Message-ID: <${crypto.randomUUID()}@${domain}>`,
      "MIME-Version: 1.0",
      `Content-Type: multipart/alternative; boundary="${boundary}"`,
    ].filter(Boolean);
    const part = (type, body) => `--${boundary}\r\nContent-Type: ${type}; charset=UTF-8\r\nContent-Transfer-Encoding: base64\r\n\r\n${wrap(b64(body || ""))}`;
    const raw = `${headers.join("\r\n")}\r\n\r\n${part("text/plain", m.text)}${m.html ? part("text/html", m.html) : ""}--${boundary}--\r\n`;
    await this.env.EMAIL.send(new EmailMessage(from, to, raw));
    return { ok: true };
  }
}
