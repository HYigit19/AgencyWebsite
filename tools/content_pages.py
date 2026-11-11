"""Erzeugt die Seiten "Über uns" und "Ratgeber" (DE/EN) als statische HTML-Dateien in site/.

Aufruf: python3 tools/content_pages.py   (danach wie gewohnt committen; build.py bleibt unverändert)

Kopf und Fuß kommen aus einer bestehenden Leistungsseite (site/de/ki-automatisierung.html bzw.
site/en/ai-automation.html), damit Navigation, Footer und Stile immer zur restlichen Website passen.
Neue Artikel: einen Eintrag in ARTICLES ergänzen (DE und EN), Skript ausführen.
"""
import html, json, re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SITE = ROOT / "site"
BASE = "https://www.devunox.ai"
ORG = BASE + "/#organization"
OG = {"de": BASE + "/assets/brand/og-de.jpg", "en": BASE + "/assets/brand/og-en.jpg"}
e = html.escape

L = {
  "de": dict(tpl="ki-automatisierung.html", home="Start", hub_dir="ratgeber", hub_name="Ratgeber", about="ueber-uns", about_name="Über uns",
             contact="kontakt.html", cta_btn="Kostenloses Erstgespräch", read="Min. Lesezeit", by="Von devunoxAI", take="Das Wichtigste in Kürze",
             faq_k="Häufige Fragen", faq_h="Antworten vorab", more_k="Weiterlesen", more_h="Weitere Ratgeber", guide="Ratgeber", locale="de_DE",
             months=["Januar","Februar","März","April","Mai","Juni","Juli","August","September","Oktober","November","Dezember"]),
  "en": dict(tpl="ai-automation.html", home="Home", hub_dir="insights", hub_name="Insights", about="about", about_name="About us",
             contact="contact.html", cta_btn="Free intro call", read="min read", by="By devunoxAI", take="Key takeaways",
             faq_k="FAQ", faq_h="Common questions", more_k="Keep reading", more_h="More insights", guide="Guide", locale="en_US",
             months=["January","February","March","April","May","June","July","August","September","October","November","December"]),
}

ARROW = '<svg class="arr" viewBox="0 0 20 20" aria-hidden="true"><path d="M5 15L15 5M7 5h8v8" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>'
HOME_ICON = '<svg viewBox="0 0 20 20" aria-hidden="true"><path d="M3.5 9.2L10 3.8l6.5 5.4M5.3 7.8v7.7a1 1 0 0 0 1 1h2.6v-4.3h2.2v4.3h2.6a1 1 0 0 0 1-1V7.8" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"/></svg>'

# ----------------------------------------------------------------------------- Inhalte

ABOUT = {
 "de": dict(
  title="Über uns: devunoxAI – KI-Software aus der EU",
  meta="devunoxAI entwickelt KI-Automatisierung und Individualsoftware für KMU. Fast 10 Jahre Enterprise-Erfahrung, kostenloser Pilot, Festpreis, Hosting in der EU.",
  h1="Über devunoxAI",
  lede="Wir entwickeln KI-Automatisierungen, Websites, kundenindividuelle Software und Dashboards für kleine und mittlere Unternehmen. Mit der Erfahrung aus großen Unternehmensprojekten, aber so einfach und schnell, wie es ein Mittelständler braucht.",
  body="""
<h2>Wer hinter devunoxAI steht</h2>
<p>devunoxAI ist eine Marke der DEVUNOX SOLUTIONS Sp. z o.o. mit Sitz in Warschau. Gegründet und geführt wird das Unternehmen von Hüseyin Yigit. Er arbeitet seit fast zehn Jahren mit Unternehmenssoftware: zuerst als SAP-Berater bei Accenture und IBM, seit 2021 selbstständig in Projekten für Industrie- und Handelsunternehmen. Er ist unter anderem für SAP S/4HANA zertifiziert und hat eine Projektmanagement-Zertifizierung des PMI.</p>
<p>Aus diesen Projekten kennen wir beides: wie mächtig große Systeme sind und wie viel Handarbeit trotzdem übrig bleibt. Genau da setzen wir an. Wir bauen Software, die die Routine übernimmt, sich an Ihre Abläufe anpasst und nicht umgekehrt.</p>

<h2>Wie wir arbeiten</h2>
<ul>
<li><b>Pilot kostenlos:</b> Wir entwickeln eine Pilot-Lösung für Ihren Anwendungsfall, ohne dass Sie etwas zahlen. Erst wenn Sie Ja sagen, kommt eine Zusammenarbeit infrage.</li>
<li><b>Festpreis statt Stundenzettel:</b> Nach dem Piloten erhalten Sie einen verbindlichen Festpreis.</li>
<li><b>Kein Abo pro Nutzer:</b> Ihr ganzes Team nutzt die Software ohne Aufpreis, egal ob 5 oder 500 Mitarbeitende.</li>
<li><b>Ihre eigene Lösung:</b> Wir bauen kundeneigene Software, keine Standardsoftware mit Ihrem Logo.</li>
<li><b>Hosting in der EU:</b> DSGVO-konform, mit Vertrag zur Auftragsverarbeitung. Ihre Daten werden nicht zum Training von KI-Modellen verwendet.</li>
<li><b>Schnell sichtbar:</b> Den ersten klickbaren Prototyp sehen Sie meist nach etwa einer Woche.</li>
</ul>

<h2>Für wen wir arbeiten</h2>
<p>Unsere Kunden sind kleine und mittlere Unternehmen in Deutschland, Österreich und der Schweiz, zum Beispiel aus Produktion, Logistik, Handel, Immobilienverwaltung und Dienstleistung. Für Behörden, Hochschulen und Unternehmen mit eigener IT bieten wir auch Betrieb auf eigenen Servern an.</p>
<p>Unsere <a href="demos.html">Demos</a> zeigen, wie solche Lösungen aussehen können. Verkauft wird aber nie die Demo, sondern immer eine Lösung, die nur für Sie entsteht.</p>

<h2>Unternehmensdaten</h2>
<p>DEVUNOX SOLUTIONS Sp. z o.o., ul. Stanisława Żaryna 2B/D, 02-593 Warszawa, Polen · KRS 0001201377 · Telefon <a href="tel:+4961423306055">+49 6142 330 60 55</a>. Weitere Angaben im <a href="impressum.html">Impressum</a>.</p>
""",
  faq=[("Wo sitzt devunoxAI?", "devunoxAI ist eine Marke der DEVUNOX SOLUTIONS Sp. z o.o. mit Sitz in Warschau. Wir arbeiten für Kunden in Deutschland, Österreich, der Schweiz und der EU, meist per Video und bei Bedarf vor Ort."),
       ("In welcher Sprache arbeiten wir zusammen?", "Auf Deutsch oder Englisch. Websites und Software liefern wir auf Wunsch in beiden Sprachen."),
       ("Wie startet ein Projekt?", "Mit einem kostenlosen 30-minütigen Erstgespräch. Danach entwickeln wir einen kostenlosen Piloten für Ihren Anwendungsfall.")]),
 "en": dict(
  title="About devunoxAI – AI software from the EU",
  meta="devunoxAI builds AI automation and custom software for SMBs. Nearly 10 years of enterprise experience, free pilot, fixed prices, EU hosting.",
  h1="About devunoxAI",
  lede="We build AI automation, websites, custom software and dashboards for small and mid-sized businesses. With the experience of large enterprise projects, but as simple and fast as a growing company needs.",
  body="""
<h2>Who is behind devunoxAI</h2>
<p>devunoxAI is a brand of DEVUNOX SOLUTIONS Sp. z o.o., based in Warsaw, Poland. The company was founded and is led by Hüseyin Yigit. He has worked with enterprise software for almost ten years: first as an SAP consultant at Accenture and IBM, and since 2021 independently on projects for industrial and trading companies. His certifications include SAP S/4HANA and a project management certification from PMI.</p>
<p>Those projects taught us two things: how powerful large systems are, and how much manual work is still left over. That is where we come in. We build software that takes over the routine and adapts to your processes, not the other way round.</p>

<h2>How we work</h2>
<ul>
<li><b>Free pilot:</b> we build a pilot for your use case at no cost. Only if you say yes do we talk about working together.</li>
<li><b>Fixed price, not hourly billing:</b> after the pilot you receive a binding fixed price.</li>
<li><b>No per-user subscription:</b> your whole team uses the software at no extra cost, whether 5 or 500 people.</li>
<li><b>Your own solution:</b> we build software that belongs to you, not off-the-shelf software with your logo.</li>
<li><b>EU hosting:</b> GDPR compliant, with a data processing agreement. Your data is not used to train AI models.</li>
<li><b>Fast results:</b> you usually see the first clickable prototype after about a week.</li>
</ul>

<h2>Who we work for</h2>
<p>Our clients are small and mid-sized businesses in Europe, for example in manufacturing, logistics, trade, property management and services. For public bodies, universities and companies with their own IT, we also offer operation on their own servers.</p>
<p>Our <a href="demos.html">demos</a> show what such solutions can look like. We never sell the demo itself, but always a solution built only for you.</p>

<h2>Company details</h2>
<p>DEVUNOX SOLUTIONS Sp. z o.o., ul. Stanisława Żaryna 2B/D, 02-593 Warsaw, Poland · KRS 0001201377 · Phone <a href="tel:+4961423306055">+49 6142 330 60 55</a>. More in the <a href="legal-notice.html">legal notice</a>.</p>
""",
  faq=[("Where is devunoxAI based?", "devunoxAI is a brand of DEVUNOX SOLUTIONS Sp. z o.o., based in Warsaw, Poland. We work with clients across Europe, mostly by video call and on site when needed."),
       ("Which language do we work in?", "German or English. Websites and software can be delivered in both languages."),
       ("How does a project start?", "With a free 30-minute intro call. After that we build a free pilot for your use case.")]),
}

ARTICLES = [
 dict(key="kosten", date="2026-11-11", services={"de": ["ki-automatisierung.html", "web-apps.html", "dashboards.html", "preise.html"], "en": ["ai-automation.html", "web-apps.html", "dashboards.html", "pricing.html"]},
  de=dict(slug="ki-automatisierung-kosten",
   title="Was kostet KI-Automatisierung? Preise 2026",
   meta="Was KI-Automatisierung, Individualsoftware und Dashboards für KMU kosten: Richtpreise 2026, Preistreiber, laufende Kosten und wie Sie ohne Risiko starten.",
   h1="Was kostet KI-Automatisierung?",
   lede="Ein ehrlicher Überblick über die Kosten von KI-Automatisierung und eigener Software für kleine und mittlere Unternehmen: Richtpreise, Preistreiber und laufende Kosten.",
   take=["Eine einzelne KI-Automatisierung für einen Ablauf startet bei uns ab 4.090 € (Festpreis).",
         "Den Preis treiben vor allem Schnittstellen, Sonderfälle und Freigabeschritte, kaum das KI-Modell selbst.",
         "Laufende Kosten: Hosting und Wartung ab 79 € im Monat, dazu die Nutzung des KI-Modells nach Menge.",
         "Starten Sie mit einem kostenlosen Piloten an Ihren eigenen Daten, bevor Sie ein Budget freigeben."],
   body="""
<h2>Die kurze Antwort</h2>
<p>Eine KI-Automatisierung für einen klar umrissenen Ablauf, etwa das Auslesen von Eingangsrechnungen oder das Vorsortieren von Kundenanfragen, kostet bei uns ab 4.090 € als einmaliger Festpreis. Je mehr Systeme angebunden werden und je mehr Sonderfälle es gibt, desto höher wird der Preis. Plattformen mit mehreren Modulen oder eigenen KI-Agenten beginnen ab etwa 25.000 €.</p>
<p>Dazu kommen laufende Kosten für Hosting, Wartung und die Nutzung des KI-Modells. Sie sind bei den meisten Mittelständlern deutlich kleiner als die eingesparte Arbeitszeit, sollten aber von Anfang an eingeplant werden.</p>

<h2>Richtpreise im Überblick</h2>
<div class="tbl"><table>
<thead><tr><th>Leistung</th><th>Richtpreis</th><th>Typischer Umfang</th></tr></thead>
<tbody>
<tr><td>Pilot-Lösung</td><td>0 €</td><td>Ein Anwendungsfall, bis zu 5 Arbeitstage, mit Ihren Beispieldaten</td></tr>
<tr><td>KI-Automatisierung</td><td>ab 4.090 €</td><td>Ein Ablauf, z. B. Posteingang, Angebote oder Belege, mit Anbindung an Postfach, CRM oder ERP</td></tr>
<tr><td>Dashboard</td><td>ab 3.390 €</td><td>Kennzahlen aus ERP, Excel und Ihren Tools, mit Ampeln und Warnungen</td></tr>
<tr><td>Kundenindividuelle Software</td><td>ab 4.090 €</td><td>Internes Tool oder Kundenportal mit Rollen und Rechten</td></tr>
<tr><td>Website</td><td>ab 2.690 €</td><td>Unternehmenswebsite, Deutsch und Englisch, SEO-Grundlagen</td></tr>
<tr><td>Große Plattformen und KI-Software</td><td>ab 25.000 €</td><td>Mehrere Module, eigene KI-Agenten, viele Standorte</td></tr>
</tbody></table></div>
<p>Alle Preise sind einmalige Projektpreise, kein Abo und keine Kosten pro Nutzer. Details finden Sie auf unserer <a href="../preise.html">Preisseite</a>.</p>

<h2>Was den Preis bestimmt</h2>
<h3>Schnittstellen</h3>
<p>Der größte Kostentreiber ist fast immer die Anbindung an Ihre Systeme. Eine E-Mail auszulesen ist einfach. Daten sicher in ein ERP wie SAP, in DATEV oder ein CRM zu schreiben, braucht saubere Schnittstellen, Tests und Rechte.</p>
<h3>Sonderfälle</h3>
<p>Der Normalfall ist schnell automatisiert. Aufwand entsteht bei den Ausnahmen: unleserliche Dokumente, fehlende Bestellnummern, abweichende Preise. Je klarer Sie festlegen, was in diesen Fällen passieren soll, desto günstiger wird die Lösung.</p>
<h3>Freigaben und Nachvollziehbarkeit</h3>
<p>Soll ein Mensch vor dem Buchen, Versenden oder Bestellen freigeben, braucht es eine Oberfläche, Benachrichtigungen und ein Protokoll. Das kostet etwas mehr, macht die Lösung aber im Alltag sicher.</p>
<h3>Sprachen und Kanäle</h3>
<p>Deutsch und Englisch, Web und Handy, E-Mail und Chat: Jeder zusätzliche Kanal und jede Sprache erhöht den Test- und Gestaltungsaufwand.</p>

<h2>Laufende Kosten</h2>
<ul>
<li><b>Hosting und Wartung:</b> Server in der EU, Sicherheitsupdates, Überwachung und kleine Anpassungen. Bei uns ab 79 € im Monat, pro Unternehmen und nicht pro Nutzer.</li>
<li><b>KI-Nutzung:</b> Die Anbieter von KI-Modellen rechnen nach Menge ab. Bei typischen Mittelstandsabläufen mit einigen hundert Dokumenten oder Anfragen pro Monat ist das meist ein kleiner Betrag.</li>
<li><b>Weiterentwicklung:</b> Neue Funktionen oder weitere Abläufe vereinbaren wir wieder zum Festpreis.</li>
</ul>

<h2>Lohnt sich das?</h2>
<p>Rechnen Sie es an einem Ablauf nach: Wie viele Minuten kostet ein Vorgang heute, wie oft kommt er im Monat vor, und was kostet eine Stunde in Ihrem Team? Wenn eine Rechnung zehn Minuten Handarbeit kostet und 400 Rechnungen im Monat eingehen, sind das über 60 Stunden im Monat. Schon ein Teil davon rechtfertigt eine Automatisierung meist innerhalb weniger Monate.</p>

<h2>So starten Sie ohne Risiko</h2>
<ol>
<li>Wählen Sie den Ablauf, der Ihr Team am meisten Zeit kostet.</li>
<li>Lassen Sie einen Piloten mit Ihren echten Beispielen bauen.</li>
<li>Entscheiden Sie erst danach, mit einem Festpreis auf dem Tisch.</li>
</ol>
<p>Bei uns ist der Pilot kostenlos. <a href="../kontakt.html">Erzählen Sie uns, welcher Ablauf Sie Zeit kostet.</a></p>
""",
   faq=[("Was kostet ein KI-Chatbot für die Website?", "Ein Chatbot, der Fragen auf Basis Ihrer eigenen Inhalte beantwortet, fällt bei uns unter KI-Automatisierung und startet ab 4.090 € Festpreis, plus laufende Kosten für Hosting und KI-Nutzung."),
        ("Gibt es monatliche Kosten?", "Ja, für Hosting, Wartung und die Nutzung des KI-Modells. Hosting und Wartung beginnen bei uns ab 79 € im Monat pro Unternehmen, nicht pro Nutzer."),
        ("Kann ich KI-Automatisierung vorher testen?", "Ja. Wir entwickeln einen kostenlosen Piloten für Ihren Anwendungsfall. Erst wenn Sie Ja sagen, kommt eine Zusammenarbeit infrage."),
        ("Gibt es Förderungen für KI-Projekte?", "In Deutschland gibt es je nach Bundesland und Unternehmensgröße Förderprogramme für Digitalisierung. Welche passen, klären Sie am besten mit Ihrer IHK oder Förderbank.")]),
  en=dict(slug="ai-automation-cost",
   title="How Much Does AI Automation Cost? 2026 Prices",
   meta="What AI automation, custom software and dashboards cost for small and mid-sized businesses: 2026 guide prices, cost drivers, running costs, risk-free start.",
   h1="How much does AI automation cost?",
   lede="An honest overview of what AI automation and custom software cost for small and mid-sized businesses: guide prices, cost drivers and running costs.",
   take=["A single AI automation for one process starts at €4,090 with us (fixed price).",
         "Integrations, edge cases and approval steps drive the price far more than the AI model itself.",
         "Running costs: hosting and maintenance from €79 per month, plus AI model usage by volume.",
         "Start with a free pilot on your own data before you commit a budget."],
   body="""
<h2>The short answer</h2>
<p>An AI automation for a clearly defined process, such as reading incoming invoices or sorting customer requests, starts at €4,090 as a one-off fixed price with us. The more systems are connected and the more edge cases there are, the higher the price. Platforms with several modules or custom AI agents start at around €25,000.</p>
<p>On top of that come running costs for hosting, maintenance and AI model usage. For most businesses they are much smaller than the working time saved, but they should be planned from the start.</p>

<h2>Guide prices at a glance</h2>
<div class="tbl"><table>
<thead><tr><th>Service</th><th>Guide price</th><th>Typical scope</th></tr></thead>
<tbody>
<tr><td>Pilot</td><td>€0</td><td>One use case, up to 5 working days, with your sample data</td></tr>
<tr><td>AI automation</td><td>from €4,090</td><td>One process, e.g. inbox, quotes or documents, connected to email, CRM or ERP</td></tr>
<tr><td>Dashboard</td><td>from €3,390</td><td>KPIs from ERP, Excel and your tools, with traffic lights and alerts</td></tr>
<tr><td>Custom software</td><td>from €4,090</td><td>Internal tool or customer portal with roles and permissions</td></tr>
<tr><td>Website</td><td>from €2,690</td><td>Company website in two languages with SEO basics</td></tr>
<tr><td>Large platforms and AI software</td><td>from €25,000</td><td>Several modules, custom AI agents, many locations</td></tr>
</tbody></table></div>
<p>All prices are one-off project prices, with no subscription and no per-user fees. See our <a href="../pricing.html">pricing page</a> for details.</p>

<h2>What drives the price</h2>
<h3>Integrations</h3>
<p>The biggest cost driver is almost always the connection to your systems. Reading an email is easy. Writing data safely into an ERP such as SAP, an accounting tool or a CRM needs proper interfaces, testing and permissions.</p>
<h3>Edge cases</h3>
<p>The normal case is automated quickly. Effort comes from the exceptions: unreadable documents, missing order numbers, prices that do not match. The clearer you define what should happen in those cases, the cheaper the solution.</p>
<h3>Approvals and audit trail</h3>
<p>If a person should approve before something is booked, sent or ordered, you need a user interface, notifications and a log. That costs a little more but makes the solution safe in daily use.</p>
<h3>Languages and channels</h3>
<p>Two languages, web and mobile, email and chat: every additional channel and language adds design and testing effort.</p>

<h2>Running costs</h2>
<ul>
<li><b>Hosting and maintenance:</b> servers in the EU, security updates, monitoring and small changes. From €79 per month with us, per company and not per user.</li>
<li><b>AI usage:</b> AI model providers charge by volume. For typical business processes with a few hundred documents or requests a month, this is usually a small amount.</li>
<li><b>Further development:</b> new features or additional processes are again agreed at a fixed price.</li>
</ul>

<h2>Is it worth it?</h2>
<p>Do the maths for one process: how many minutes does one case take today, how often does it occur each month, and what does an hour cost in your team? If an invoice takes ten minutes of manual work and 400 invoices arrive each month, that is more than 60 hours a month. Saving even part of that usually pays for an automation within a few months.</p>

<h2>How to start without risk</h2>
<ol>
<li>Pick the process that costs your team the most time.</li>
<li>Have a pilot built with your real examples.</li>
<li>Decide only after that, with a fixed price on the table.</li>
</ol>
<p>With us, the pilot is free. <a href="../contact.html">Tell us which process costs you time.</a></p>
""",
   faq=[("How much does an AI chatbot for a website cost?", "A chatbot that answers questions from your own content counts as an AI automation with us and starts at a €4,090 fixed price, plus running costs for hosting and AI usage."),
        ("Are there monthly costs?", "Yes, for hosting, maintenance and AI model usage. Hosting and maintenance start at €79 per month per company, not per user."),
        ("Can I test AI automation first?", "Yes. We build a free pilot for your use case. Only if you say yes do we talk about working together.")])),

 dict(key="recht", date="2026-11-11", services={"de": ["ki-automatisierung.html", "ki-qualitaetsmanagement.html"], "en": ["ai-automation.html", "ai-quality-management.html"]},
  de=dict(slug="ki-dsgvo-ai-act",
   title="KI im Unternehmen: DSGVO und EU AI Act 2026",
   meta="Was Unternehmen beim Einsatz von KI beachten müssen: DSGVO, AV-Vertrag, Hosting in der EU und die Pflichten aus dem EU AI Act mit allen Fristen bis 2028.",
   h1="KI im Unternehmen: DSGVO und EU AI Act",
   lede="Welche Regeln gelten, wenn Sie KI für Kundenanfragen, Dokumente oder interne Abläufe einsetzen? Ein praxisnaher Überblick über DSGVO und EU AI Act, Stand November 2026.",
   take=["Für die meisten KI-Automatisierungen im Mittelstand gelten vor allem die DSGVO und die Transparenzpflichten des AI Act.",
         "Seit dem 2. August 2026 müssen KI-Chatbots für Nutzer als KI erkennbar sein (Art. 50 AI Act).",
         "Seit Februar 2025 sollen Unternehmen sicherstellen, dass ihre Mitarbeitenden ausreichende KI-Kompetenz haben.",
         "Die Pflichten für Hochrisiko-KI wurden verschoben: auf Dezember 2027 bzw. August 2028."],
   body="""
<p class="note">Dieser Beitrag ist ein praktischer Überblick und keine Rechtsberatung. Prüfen Sie Ihren konkreten Fall mit Ihrer Datenschutz- oder Rechtsberatung.</p>

<h2>Zwei Regelwerke, zwei Fragen</h2>
<p>Beim Einsatz von KI im Unternehmen sind zwei europäische Regelwerke entscheidend. Die <b>DSGVO</b> regelt, ob und wie Sie personenbezogene Daten verarbeiten dürfen, ganz gleich, ob mit oder ohne KI. Der <b>EU AI Act</b> (KI-Verordnung) regelt KI-Systeme selbst: welche verboten sind, welche als Hochrisiko gelten und wann Sie offenlegen müssen, dass KI im Spiel ist.</p>

<h2>DSGVO: Was bei KI-Projekten wichtig ist</h2>
<h3>Rechtsgrundlage und Zweck</h3>
<p>Für die meisten Automatisierungen, etwa das Beantworten von Kundenanfragen oder das Verarbeiten von Rechnungen, verarbeiten Sie Daten zur Erfüllung eines Vertrags oder aus berechtigtem Interesse. Legen Sie den Zweck vor dem Start fest und verarbeiten Sie nur, was dafür nötig ist.</p>
<h3>Auftragsverarbeitung</h3>
<p>Wenn ein Dienstleister die KI-Lösung für Sie betreibt, brauchen Sie einen Vertrag zur Auftragsverarbeitung (AV-Vertrag). Das gilt auch für den Anbieter des KI-Modells, wenn dort personenbezogene Daten ankommen.</p>
<h3>Hosting und Drittländer</h3>
<p>Am einfachsten ist es, wenn Anwendung und Daten in der EU liegen. Werden Daten an Anbieter außerhalb der EU übermittelt, brauchen Sie eine Grundlage dafür, etwa einen Angemessenheitsbeschluss oder Standardvertragsklauseln. Oft lässt sich das vermeiden, indem Namen und Kontaktdaten entfernt werden, bevor ein Dokument an das Modell geht.</p>
<h3>Kein Training mit Ihren Daten</h3>
<p>Klären Sie vertraglich, dass Ihre Daten nicht zum Training von KI-Modellen genutzt werden. Bei den Geschäftsangeboten der großen Anbieter ist das in der Regel ausgeschlossen, sollte aber dokumentiert sein.</p>
<h3>Betroffenenrechte und Löschung</h3>
<p>Auch in KI-Lösungen müssen Auskunft und Löschung möglich sein. Planen Sie Aufbewahrungsfristen und Löschroutinen von Anfang an ein.</p>

<h2>EU AI Act: Welche Fristen gelten</h2>
<p>Der AI Act ist seit August 2024 in Kraft und gilt schrittweise. Mit dem sogenannten Digital Omnibus, der Ende Juli 2026 in Kraft getreten ist, wurden einige Fristen verschoben. Stand heute gilt:</p>
<div class="tbl"><table>
<thead><tr><th>Seit / ab</th><th>Was gilt</th></tr></thead>
<tbody>
<tr><td>2. Februar 2025</td><td>Verbotene KI-Praktiken; Pflicht, für ausreichende KI-Kompetenz der Mitarbeitenden zu sorgen</td></tr>
<tr><td>2. August 2025</td><td>Pflichten für Anbieter von KI-Modellen mit allgemeinem Verwendungszweck</td></tr>
<tr><td>2. August 2026</td><td>Transparenzpflichten (Art. 50): z. B. Chatbots müssen als KI erkennbar sein</td></tr>
<tr><td>2. Dezember 2026</td><td>Ende der Übergangsfrist für die maschinenlesbare Kennzeichnung KI-generierter Inhalte bei bestehenden Systemen</td></tr>
<tr><td>2. Dezember 2027</td><td>Pflichten für eigenständige Hochrisiko-KI (Anhang III), z. B. im Personalbereich</td></tr>
<tr><td>2. August 2028</td><td>Pflichten für Hochrisiko-KI in regulierten Produkten (Anhang I)</td></tr>
</tbody></table></div>

<h2>Was das für typische Projekte bedeutet</h2>
<ul>
<li><b>KI-Chatbot auf der Website oder im Kundenservice:</b> Nutzer müssen erkennen können, dass sie mit einer KI sprechen. Ein klarer Hinweis im Chatfenster genügt in der Regel.</li>
<li><b>Rechnungen, Lieferscheine, E-Mails auslesen:</b> Das ist in aller Regel keine Hochrisiko-KI. Wichtig sind hier DSGVO, AV-Vertrag und eine Freigabe durch Ihr Team bei kritischen Schritten.</li>
<li><b>KI im Personalbereich</b>, etwa zur Vorauswahl von Bewerbungen: Das kann unter Hochrisiko-KI fallen. Hier lohnt sich eine frühe rechtliche Prüfung, auch wenn die Pflichten erst ab Dezember 2027 greifen.</li>
<li><b>KI-generierte Texte und Bilder:</b> Für veröffentlichte Inhalte gelten Kennzeichnungspflichten. Planen Sie eine redaktionelle Prüfung ein.</li>
</ul>

<h2>Checkliste für Ihr KI-Projekt</h2>
<ol>
<li>Zweck und Datenarten festlegen, nur das Nötige verarbeiten.</li>
<li>Hosting in der EU wählen oder Drittlandübermittlung absichern.</li>
<li>AV-Verträge mit allen beteiligten Dienstleistern abschließen.</li>
<li>Training mit Ihren Daten vertraglich ausschließen.</li>
<li>KI für Nutzer kenntlich machen, wo sie direkt mit ihr interagieren.</li>
<li>Menschliche Freigabe für kritische Entscheidungen vorsehen.</li>
<li>Mitarbeitende im Umgang mit dem System schulen.</li>
</ol>
<p>So bauen wir unsere Lösungen: Hosting in der EU, AV-Vertrag, kein Training mit Ihren Daten und Freigaben dort, wo es darauf ankommt. Mehr zu unserer <a href="../ki-automatisierung.html">KI-Automatisierung</a>.</p>
""",
   faq=[("Darf ich ChatGPT oder Claude mit Kundendaten nutzen?", "Grundsätzlich ja, wenn eine Rechtsgrundlage besteht, ein AV-Vertrag mit dem Anbieter vorliegt, die Datenübermittlung abgesichert ist und Training mit Ihren Daten ausgeschlossen ist. Für Geschäftskunden bieten die großen Anbieter entsprechende Verträge an."),
        ("Muss ich meinen KI-Chatbot kennzeichnen?", "Ja. Seit dem 2. August 2026 müssen Nutzer erkennen können, dass sie mit einem KI-System interagieren, sofern das nicht ohnehin offensichtlich ist."),
        ("Ist meine KI-Automatisierung Hochrisiko-KI?", "Typische Automatisierungen wie das Auslesen von Rechnungen oder Vorsortieren von E-Mails sind es in der Regel nicht. Hochrisiko betrifft vor allem Bereiche wie Personalauswahl, Kreditwürdigkeit oder Bildung."),
        ("Wurde der AI Act verschoben?", "Teilweise. Der Digital Omnibus hat die Pflichten für Hochrisiko-KI auf Dezember 2027 bzw. August 2028 verschoben. Die Transparenzpflichten gelten dagegen seit dem 2. August 2026.")]),
  en=dict(slug="ai-gdpr-eu-ai-act",
   title="AI in Business: GDPR and the EU AI Act in 2026",
   meta="What businesses must consider when using AI: GDPR, data processing agreements, EU hosting and the EU AI Act obligations with all deadlines up to 2028.",
   h1="AI in business: GDPR and the EU AI Act",
   lede="Which rules apply when you use AI for customer requests, documents or internal processes? A practical overview of the GDPR and the EU AI Act, as of November 2026.",
   take=["For most business AI automation, the GDPR and the AI Act's transparency obligations matter most.",
         "Since 2 August 2026, AI chatbots must be recognisable as AI to users (Article 50 AI Act).",
         "Since February 2025, organisations must ensure sufficient AI literacy among their staff.",
         "High-risk AI obligations were postponed to December 2027 and August 2028."],
   body="""
<p class="note">This article is a practical overview, not legal advice. Check your specific case with your data protection or legal advisers.</p>

<h2>Two sets of rules, two questions</h2>
<p>Two European regulations matter when you use AI in your business. The <b>GDPR</b> governs whether and how you may process personal data, with or without AI. The <b>EU AI Act</b> governs AI systems themselves: which are prohibited, which count as high-risk, and when you must disclose that AI is involved.</p>

<h2>GDPR: what matters in AI projects</h2>
<h3>Legal basis and purpose</h3>
<p>For most automations, such as answering customer requests or processing invoices, you process data to perform a contract or based on legitimate interest. Define the purpose before you start and process only what is needed.</p>
<h3>Data processing agreements</h3>
<p>If a service provider runs the AI solution for you, you need a data processing agreement. This also applies to the AI model provider if personal data reaches it.</p>
<h3>Hosting and transfers outside the EU</h3>
<p>The simplest setup keeps the application and its data in the EU. If data is transferred to providers outside the EU, you need a legal basis such as an adequacy decision or standard contractual clauses. Often you can avoid this by removing names and contact details before a document is sent to the model.</p>
<h3>No training on your data</h3>
<p>Make sure by contract that your data is not used to train AI models. The business offerings of the large providers usually exclude this, but it should be documented.</p>
<h3>Data subject rights and deletion</h3>
<p>Access and deletion requests must also work in AI solutions. Plan retention periods and deletion routines from the start.</p>

<h2>EU AI Act: which deadlines apply</h2>
<p>The AI Act has been in force since August 2024 and applies in stages. The so-called Digital Omnibus, in force since the end of July 2026, moved some deadlines. As of today:</p>
<div class="tbl"><table>
<thead><tr><th>Since / from</th><th>What applies</th></tr></thead>
<tbody>
<tr><td>2 February 2025</td><td>Prohibited AI practices; duty to ensure sufficient AI literacy of staff</td></tr>
<tr><td>2 August 2025</td><td>Obligations for providers of general-purpose AI models</td></tr>
<tr><td>2 August 2026</td><td>Transparency obligations (Article 50), e.g. chatbots must be recognisable as AI</td></tr>
<tr><td>2 December 2026</td><td>End of the grace period for machine-readable marking of AI-generated content in existing systems</td></tr>
<tr><td>2 December 2027</td><td>Obligations for stand-alone high-risk AI (Annex III), e.g. in recruitment</td></tr>
<tr><td>2 August 2028</td><td>Obligations for high-risk AI in regulated products (Annex I)</td></tr>
</tbody></table></div>

<h2>What this means for typical projects</h2>
<ul>
<li><b>AI chatbot on your website or in customer service:</b> users must be able to tell that they are talking to an AI. A clear note in the chat window is usually enough.</li>
<li><b>Reading invoices, delivery notes and emails:</b> this is generally not high-risk AI. What matters here is the GDPR, a data processing agreement and human approval for critical steps.</li>
<li><b>AI in HR</b>, such as pre-screening applications: this can count as high-risk AI. An early legal review pays off, even though the obligations only apply from December 2027.</li>
<li><b>AI-generated text and images:</b> labelling duties apply to published content. Plan an editorial review.</li>
</ul>

<h2>Checklist for your AI project</h2>
<ol>
<li>Define purpose and data types; process only what is needed.</li>
<li>Choose EU hosting or secure any transfer outside the EU.</li>
<li>Sign data processing agreements with all providers involved.</li>
<li>Exclude training on your data by contract.</li>
<li>Make AI recognisable where users interact with it directly.</li>
<li>Keep human approval for critical decisions.</li>
<li>Train your staff in using the system.</li>
</ol>
<p>This is how we build our solutions: EU hosting, a data processing agreement, no training on your data, and approvals where they matter. More about our <a href="../ai-automation.html">AI automation</a>.</p>
""",
   faq=[("Can I use ChatGPT or Claude with customer data?", "In principle yes, if there is a legal basis, a data processing agreement with the provider, safeguards for data transfers and training on your data is excluded. The large providers offer such contracts for business customers."),
        ("Do I have to label my AI chatbot?", "Yes. Since 2 August 2026, users must be able to recognise that they are interacting with an AI system, unless this is obvious anyway."),
        ("Was the AI Act postponed?", "Partly. The Digital Omnibus moved high-risk AI obligations to December 2027 and August 2028. The transparency obligations have applied since 2 August 2026.")])),

 dict(key="rechnung", date="2026-11-11", services={"de": ["ki-automatisierung.html", "web-apps.html"], "en": ["ai-automation.html", "web-apps.html"]},
  de=dict(slug="e-rechnung-ki",
   title="E-Rechnung und KI: Eingangsrechnungen automatisieren",
   meta="E-Rechnungspflicht 2025 bis 2028 und wie KI Eingangsrechnungen ausliest, mit Bestellungen abgleicht und zur Freigabe vorbereitet: PDF, XRechnung, ZUGFeRD.",
   h1="E-Rechnung und KI: Eingangsrechnungen automatisch verarbeiten",
   lede="Seit 2025 müssen Unternehmen in Deutschland E-Rechnungen empfangen können, ab 2027 beginnt die Pflicht zum Ausstellen. Ein guter Anlass, den ganzen Rechnungseingang zu automatisieren.",
   take=["Seit dem 1. Januar 2025 müssen alle Unternehmen in Deutschland E-Rechnungen empfangen können.",
         "Ab 2027 müssen Unternehmen mit mehr als 800.000 € Vorjahresumsatz E-Rechnungen ausstellen, ab 2028 alle.",
         "KI liest PDF-Rechnungen und E-Rechnungen gleichermaßen aus und gleicht sie mit Bestellungen ab.",
         "Ihr Team prüft nur noch Abweichungen statt jede Rechnung abzutippen."],
   body="""
<h2>Die E-Rechnungspflicht im Überblick</h2>
<p>Mit dem Wachstumschancengesetz wird die elektronische Rechnung im inländischen B2B-Geschäft in Deutschland schrittweise Pflicht. Eine E-Rechnung ist dabei ein strukturiertes Datenformat wie XRechnung oder ZUGFeRD. Ein einfaches PDF zählt nicht dazu.</p>
<div class="tbl"><table>
<thead><tr><th>Ab</th><th>Was gilt</th></tr></thead>
<tbody>
<tr><td>1. Januar 2025</td><td>Alle Unternehmen müssen E-Rechnungen empfangen können</td></tr>
<tr><td>1. Januar 2027</td><td>Ausstellungspflicht für Unternehmen mit mehr als 800.000 € Gesamtumsatz im Vorjahr</td></tr>
<tr><td>1. Januar 2028</td><td>Ausstellungspflicht für alle Unternehmen im inländischen B2B-Geschäft</td></tr>
</tbody></table></div>
<p>Ausnahmen gibt es unter anderem für Kleinbetragsrechnungen bis 250 € und für Kleinunternehmer beim Ausstellen. Welche Regeln für Sie gelten, klären Sie am besten mit Ihrer Steuerberatung.</p>

<h2>Warum der Rechnungseingang trotzdem Handarbeit bleibt</h2>
<p>In der Praxis kommen Rechnungen noch lange in gemischter Form an: als E-Rechnung, als PDF, als Scan oder als Foto. Eine XRechnung ist eine XML-Datei, die ohne passende Software kaum lesbar ist. Und auch eine perfekt strukturierte Rechnung muss geprüft werden: Passt sie zur Bestellung, ist die Ware angekommen, stimmt der Preis?</p>

<h2>So automatisiert KI den Rechnungseingang</h2>
<h3>1. Eingang sammeln</h3>
<p>Rechnungen aus dem Postfach, aus Lieferantenportalen oder vom Scanner landen automatisch an einer Stelle.</p>
<h3>2. Auslesen</h3>
<p>Bei E-Rechnungen werden die strukturierten Daten direkt übernommen. Bei PDFs und Scans liest die KI Lieferant, Rechnungsnummer, Datum, Positionen, Beträge, Steuer und Bankdaten aus, ohne Vorlage pro Lieferant.</p>
<h3>3. Prüfen und abgleichen</h3>
<p>Die Daten werden mit Ihren Stammdaten, Bestellungen und Wareneingängen abgeglichen. Doppelte Rechnungen, falsche Preise oder fehlende Wareneingänge fallen sofort auf.</p>
<h3>4. Freigeben und übergeben</h3>
<p>Stimmt alles, geht ein Buchungsvorschlag zur Freigabe oder direkt an Ihr ERP oder Ihre Buchhaltung, etwa per Export für DATEV. Abweichungen landen mit klarer Begründung bei der zuständigen Person.</p>

<h2>Was das bringt</h2>
<ul>
<li>Weniger Abtippen: Ihr Team prüft Ausnahmen statt jede Rechnung.</li>
<li>Schnellere Freigaben und weniger verpasste Skonti.</li>
<li>Ein Prozess für alle Formate, egal ob E-Rechnung oder PDF.</li>
<li>Nachvollziehbar: Wer hat wann was freigegeben, ist protokolliert.</li>
</ul>

<h2>So fangen Sie an</h2>
<p>Sammeln Sie 20 bis 50 typische Rechnungen aus dem letzten Monat, inklusive der schwierigen Fälle. Daran lässt sich in einem Piloten zeigen, wie viel automatisch durchläuft. Bei uns ist dieser Pilot kostenlos. <a href="../kontakt.html">Sprechen Sie uns an</a> oder sehen Sie sich unsere <a href="../ki-automatisierung.html">KI-Automatisierung</a> an.</p>
""",
   faq=[("Ist eine PDF-Rechnung eine E-Rechnung?", "Nein. Eine E-Rechnung ist ein strukturiertes elektronisches Format wie XRechnung oder ZUGFeRD. Ein reines PDF gilt als sonstige Rechnung."),
        ("Ab wann muss ich E-Rechnungen ausstellen?", "Ab dem 1. Januar 2027, wenn Ihr Gesamtumsatz im Vorjahr über 800.000 € lag, sonst ab dem 1. Januar 2028. Empfangen müssen Sie E-Rechnungen schon seit 2025."),
        ("Kann KI auch PDF-Rechnungen verarbeiten?", "Ja. KI liest PDFs, Scans und Fotos aus und überführt die Daten in denselben Prozess wie E-Rechnungen."),
        ("Funktioniert das mit DATEV oder SAP?", "Ja. Die geprüften Daten werden an Ihr ERP übergeben oder als Export für die Buchhaltung bereitgestellt, etwa für DATEV.")]),
  en=dict(slug="invoice-automation-ai",
   title="Invoice Automation with AI: E-Invoices and PDFs",
   meta="How AI reads incoming invoices, matches them to purchase orders and prepares them for approval, for PDFs, scans and e-invoices such as XRechnung and ZUGFeRD.",
   h1="Invoice automation with AI: e-invoices and PDFs",
   lede="E-invoicing is becoming mandatory across Europe, but invoices still arrive in every format. Here is how AI handles the whole incoming invoice process, from inbox to approval.",
   take=["In Germany, all businesses must be able to receive e-invoices since 1 January 2025.",
         "Issuing e-invoices becomes mandatory in Germany from 2027 for larger and from 2028 for all businesses.",
         "AI reads PDF invoices and e-invoices alike and matches them against purchase orders.",
         "Your team only reviews exceptions instead of typing every invoice."],
   body="""
<h2>E-invoicing is coming</h2>
<p>Across Europe, structured electronic invoices are replacing PDFs. In Germany, for example, domestic B2B e-invoicing is being phased in: an e-invoice is a structured format such as XRechnung or ZUGFeRD, and a plain PDF does not count.</p>
<div class="tbl"><table>
<thead><tr><th>From</th><th>What applies in Germany</th></tr></thead>
<tbody>
<tr><td>1 January 2025</td><td>All businesses must be able to receive e-invoices</td></tr>
<tr><td>1 January 2027</td><td>Issuing e-invoices is mandatory for businesses with more than €800,000 turnover in the previous year</td></tr>
<tr><td>1 January 2028</td><td>Issuing e-invoices is mandatory for all businesses in domestic B2B trade</td></tr>
</tbody></table></div>
<p>Other EU countries have their own timelines. Check the rules for your country with your tax adviser.</p>

<h2>Why incoming invoices are still manual work</h2>
<p>In practice, invoices will arrive in mixed formats for a long time: e-invoices, PDFs, scans and photos. An XRechnung is an XML file that is hard to read without suitable software. And even a perfectly structured invoice still needs checking: does it match the purchase order, has the goods receipt been posted, is the price right?</p>

<h2>How AI automates incoming invoices</h2>
<h3>1. Collect</h3>
<p>Invoices from your inbox, supplier portals or the scanner land automatically in one place.</p>
<h3>2. Read</h3>
<p>For e-invoices, the structured data is taken over directly. For PDFs and scans, AI reads supplier, invoice number, date, line items, amounts, tax and bank details, without a template per supplier.</p>
<h3>3. Check and match</h3>
<p>The data is matched against your master data, purchase orders and goods receipts. Duplicate invoices, wrong prices or missing goods receipts are flagged immediately.</p>
<h3>4. Approve and hand over</h3>
<p>If everything matches, a posting proposal goes to approval or straight to your ERP or accounting system. Exceptions go to the right person with a clear reason.</p>

<h2>What you gain</h2>
<ul>
<li>Less typing: your team reviews exceptions instead of every invoice.</li>
<li>Faster approvals and fewer missed early-payment discounts.</li>
<li>One process for every format, e-invoice or PDF.</li>
<li>A full audit trail of who approved what and when.</li>
</ul>

<h2>How to get started</h2>
<p>Collect 20 to 50 typical invoices from last month, including the difficult ones. A pilot on these shows how much can run automatically. With us, that pilot is free. <a href="../contact.html">Get in touch</a> or see our <a href="../ai-automation.html">AI automation</a>.</p>
""",
   faq=[("Is a PDF invoice an e-invoice?", "No. An e-invoice is a structured electronic format such as XRechnung or ZUGFeRD. A plain PDF does not count as an e-invoice."),
        ("Can AI process PDF invoices too?", "Yes. AI reads PDFs, scans and photos and feeds the data into the same process as e-invoices."),
        ("Does it work with SAP or other ERP systems?", "Yes. The checked data is passed to your ERP or provided as an export for your accounting system.")])),

 dict(key="software", date="2026-11-11", services={"de": ["web-apps.html", "dashboards.html", "preise.html"], "en": ["web-apps.html", "dashboards.html", "pricing.html"]},
  de=dict(slug="individualsoftware-vs-standardsoftware",
   title="Individualsoftware oder Standardsoftware? Ein Vergleich",
   meta="Individualsoftware oder Standardsoftware: Kosten, Vor- und Nachteile, wann sich eine eigene Lösung für KMU lohnt und wie Sie das Risiko klein halten.",
   h1="Individualsoftware oder Standardsoftware?",
   lede="Wann reicht eine fertige Software, und wann lohnt sich eine eigene Lösung? Ein ehrlicher Vergleich für kleine und mittlere Unternehmen.",
   take=["Standardsoftware passt, wenn Ihr Ablauf dem Branchenstandard entspricht.",
         "Individualsoftware lohnt sich, wenn Ihr Ablauf Sie besonders macht oder Standardlösungen nur mit vielen Excel-Listen funktionieren.",
         "Abo-Kosten pro Nutzer summieren sich über die Jahre oft auf mehr als eine eigene Lösung.",
         "Mit Pilot und Festpreis bleibt das Risiko einer eigenen Software klein."],
   body="""
<h2>Der Unterschied in einem Satz</h2>
<p><b>Standardsoftware</b> ist ein fertiges Produkt für viele Unternehmen, meist im Abo pro Nutzer. <b>Individualsoftware</b> wird für ein einziges Unternehmen entwickelt und bildet genau dessen Abläufe ab.</p>

<h2>Vergleich auf einen Blick</h2>
<div class="tbl"><table>
<thead><tr><th></th><th>Standardsoftware</th><th>Individualsoftware</th></tr></thead>
<tbody>
<tr><td>Start</td><td>Sofort nutzbar</td><td>Prototyp nach Tagen, fertig nach Wochen</td></tr>
<tr><td>Kosten</td><td>Monatliches Abo, oft pro Nutzer</td><td>Einmaliger Projektpreis plus Betrieb</td></tr>
<tr><td>Passgenauigkeit</td><td>Sie passen Ihre Abläufe an die Software an</td><td>Die Software passt sich Ihren Abläufen an</td></tr>
<tr><td>Schnittstellen</td><td>Was der Hersteller anbietet</td><td>Genau die Systeme, die Sie nutzen</td></tr>
<tr><td>Weiterentwicklung</td><td>Nach Plan des Herstellers</td><td>Nach Ihrem Bedarf</td></tr>
<tr><td>Abhängigkeit</td><td>Vom Hersteller und seinen Preisen</td><td>Vom Entwickler, abgefedert durch Dokumentation und Quellcode</td></tr>
</tbody></table></div>

<h2>Wann Standardsoftware die richtige Wahl ist</h2>
<ul>
<li>Ihr Ablauf ist branchenüblich, zum Beispiel Lohnabrechnung oder Finanzbuchhaltung.</li>
<li>Es gibt ein etabliertes Produkt, das Ihre Anforderungen ohne Umwege erfüllt.</li>
<li>Gesetzliche Vorgaben ändern sich häufig und der Hersteller pflegt sie für Sie.</li>
</ul>

<h2>Wann sich eine eigene Lösung lohnt</h2>
<ul>
<li><b>Excel als Klebstoff:</b> Ihre Standardsoftware funktioniert nur mit vielen Listen, Kopien und Nacharbeit drumherum.</li>
<li><b>Ihr Ablauf ist Ihr Vorteil:</b> Die Art, wie Sie Aufträge, Prüfungen oder Reklamationen abwickeln, unterscheidet Sie vom Wettbewerb.</li>
<li><b>Viele Nutzer, wenig Funktionen:</b> Sie zahlen für 50 Lizenzen, nutzen aber nur einen Bruchteil der Funktionen.</li>
<li><b>Mobile Teams:</b> Mitarbeitende im Außendienst, auf der Baustelle oder im Lager brauchen eine einfache App mit Fotos, GPS und Offline-Modus.</li>
<li><b>Mehrere Systeme verbinden:</b> Daten aus ERP, CRM und Tabellen sollen an einer Stelle zusammenkommen.</li>
</ul>

<h2>Die Kosten über fünf Jahre</h2>
<p>Ein Beispiel: Eine Standardlösung für 30 Nutzer zu 40 € pro Nutzer und Monat kostet in fünf Jahren 72.000 €. Eine eigene Lösung mit einem Projektpreis von 15.000 € und Betrieb für 150 € im Monat kostet im selben Zeitraum 24.000 €, und jeder weitere Nutzer kostet nichts. Die Zahlen sind beispielhaft, aber die Rechnung lohnt sich für jede Entscheidung.</p>

<h2>Der Mittelweg</h2>
<p>Oft ist die beste Lösung eine Kombination: Standardsoftware für den Kern, etwa ERP oder Buchhaltung, und eine schlanke eigene Anwendung für den Ablauf, der nicht hineinpasst. Über Schnittstellen bleiben beide verbunden.</p>

<h2>So halten Sie das Risiko klein</h2>
<ol>
<li>Mit einem Ablauf starten, nicht mit dem ganzen Unternehmen.</li>
<li>Einen Prototyp mit echten Daten testen, bevor Sie investieren.</li>
<li>Einen Festpreis vereinbaren und sich Quellcode und Dokumentation sichern.</li>
</ol>
<p>Wir entwickeln <a href="../web-apps.html">kundenindividuelle Software</a> genau so: kostenloser Pilot, dann Festpreis, kein Abo pro Nutzer. Beispiele finden Sie in unseren <a href="../demos.html">Demos</a>.</p>
""",
   faq=[("Was kostet Individualsoftware?", "Bei uns beginnen kundenindividuelle Lösungen ab 4.090 € als Festpreis, größere Plattformen ab etwa 25.000 €. Den Piloten entwickeln wir kostenlos."),
        ("Wie lange dauert die Entwicklung?", "Einen ersten klickbaren Prototyp gibt es meist nach etwa einer Woche, die Umsetzung dauert typischerweise zwei bis sechs Wochen."),
        ("Bin ich danach vom Entwickler abhängig?", "Weniger als bei Standardsoftware, wenn Quellcode und Dokumentation an Sie übergeben werden. Auf Wunsch übernehmen Sie das Hosting selbst.")]),
  en=dict(slug="custom-vs-off-the-shelf-software",
   title="Custom Software or Off-the-Shelf? A Comparison",
   meta="Custom software or off-the-shelf software: costs, pros and cons, when your own solution pays off for SMBs and how to keep the risk low.",
   h1="Custom software or off-the-shelf software?",
   lede="When is ready-made software enough, and when does your own solution pay off? An honest comparison for small and mid-sized businesses.",
   take=["Off-the-shelf software fits when your process matches the industry standard.",
         "Custom software pays off when your process is what sets you apart, or when standard tools only work with lots of spreadsheets.",
         "Per-user subscriptions often add up to more than your own solution over the years.",
         "A pilot and a fixed price keep the risk of custom software low."],
   body="""
<h2>The difference in one sentence</h2>
<p><b>Off-the-shelf software</b> is a ready-made product for many companies, usually a per-user subscription. <b>Custom software</b> is built for one company and mirrors exactly its processes.</p>

<h2>Comparison at a glance</h2>
<div class="tbl"><table>
<thead><tr><th></th><th>Off-the-shelf</th><th>Custom</th></tr></thead>
<tbody>
<tr><td>Start</td><td>Ready immediately</td><td>Prototype in days, finished in weeks</td></tr>
<tr><td>Cost</td><td>Monthly subscription, often per user</td><td>One-off project price plus operation</td></tr>
<tr><td>Fit</td><td>You adapt your processes to the software</td><td>The software adapts to your processes</td></tr>
<tr><td>Integrations</td><td>Whatever the vendor offers</td><td>Exactly the systems you use</td></tr>
<tr><td>Roadmap</td><td>The vendor's plan</td><td>Your needs</td></tr>
<tr><td>Dependency</td><td>On the vendor and its prices</td><td>On the developer, reduced by documentation and source code</td></tr>
</tbody></table></div>

<h2>When off-the-shelf is the right choice</h2>
<ul>
<li>Your process is standard for your industry, such as payroll or financial accounting.</li>
<li>An established product meets your requirements without workarounds.</li>
<li>Legal requirements change often and the vendor maintains them for you.</li>
</ul>

<h2>When your own solution pays off</h2>
<ul>
<li><b>Spreadsheets as glue:</b> your standard software only works with lots of lists, copies and rework around it.</li>
<li><b>Your process is your edge:</b> the way you handle orders, inspections or complaints sets you apart.</li>
<li><b>Many users, few features:</b> you pay for 50 licences but use a fraction of the features.</li>
<li><b>Mobile teams:</b> staff in the field, on site or in the warehouse need a simple app with photos, GPS and offline mode.</li>
<li><b>Connecting systems:</b> data from ERP, CRM and spreadsheets should come together in one place.</li>
</ul>

<h2>The cost over five years</h2>
<p>An example: a standard tool for 30 users at €40 per user and month costs €72,000 over five years. Your own solution with a €15,000 project price and €150 a month for operation costs €24,000 over the same period, and every extra user costs nothing. The figures are illustrative, but the calculation is worth doing for every decision.</p>

<h2>The middle ground</h2>
<p>Often the best answer is a combination: standard software for the core, such as ERP or accounting, and a lean custom application for the process that does not fit. Integrations keep both connected.</p>

<h2>How to keep the risk low</h2>
<ol>
<li>Start with one process, not the whole company.</li>
<li>Test a prototype with real data before you invest.</li>
<li>Agree a fixed price and secure source code and documentation.</li>
</ol>
<p>This is how we build <a href="../web-apps.html">custom software</a>: free pilot, then a fixed price, no per-user subscription. See examples in our <a href="../demos.html">demos</a>.</p>
""",
   faq=[("How much does custom software cost?", "With us, custom solutions start at a €4,090 fixed price, larger platforms at around €25,000. We build the pilot for free."),
        ("How long does development take?", "A first clickable prototype is usually ready after about a week; implementation typically takes two to six weeks."),
        ("Will I depend on the developer afterwards?", "Less than with off-the-shelf software, if source code and documentation are handed over to you. You can also host it yourself.")])),
]

# ----------------------------------------------------------------------------- Bausteine

def fmt_date(d, lang):
    y, m, dd = map(int, d.split("-"))
    return f"{dd}. {L['de']['months'][m-1]} {y}" if lang == "de" else f"{dd} {L['en']['months'][m-1]} {y}"

def read_min(a):
    words = len(re.sub(r"<[^>]+>", " ", a["body"]).split()) + sum(len((q + " " + x).split()) for q, x in a["faq"])
    return max(3, round(words / 200))

def template(lang):
    s = (SITE / lang / L[lang]["tpl"]).read_text(encoding="utf-8")
    head_end = s.index("</head>")
    body_start = s.index("<body")
    pre_main = s[body_start:s.index("<main>")]
    post_main = s[s.index("</main>") + len("</main>"):]
    head_static = re.search(r'<link href="/favicon.svg".*?\n', s).group(0)
    tail = s[head_end:body_start]  # nothing important, kept for structure
    style = re.search(r'<meta name="theme-color".*?</head>', s, re.S).group(0).replace("</head>", "")
    # Menü: kein aktueller Menüpunkt auf diesen Seiten
    pre_main = pre_main.replace(' aria-current="page"', "")
    return head_static, style, pre_main, post_main

def fix_rel(fragment, depth):
    """Relative Links/Quellen für Seiten in Unterordnern (depth=1: /de/ratgeber/) anpassen."""
    if depth == 0:
        return fragment
    pre = "../" * depth
    return re.sub(r'\b(href|src)="(?!https?:|/|#|mailto:|tel:|data:)([^"]+)"', lambda m: f'{m.group(1)}="{pre}{m.group(2)}"', fragment)

def lang_switch(pre_main, lang, own_href, other_href):
    other = "en" if lang == "de" else "de"
    def rep(m):
        return (f'<div class="lang" role="group" aria-label="{m.group(1)}">'
                f'<a href="{own_href if lang == "de" else other_href}" hreflang="de" lang="de" aria-current="{"true" if lang == "de" else "false"}">DE</a>'
                f'<a href="{own_href if lang == "en" else other_href}" hreflang="en" lang="en" aria-current="{"true" if lang == "en" else "false"}">EN</a></div>')
    return re.sub(r'<div class="lang" role="group" aria-label="([^"]+)">.*?</div>', rep, pre_main, count=1, flags=re.S)

def page(lang, path, alt_path, title, meta, h1, lede, crumbs, main, schema, og_type="website", meta_line=""):
    """path: z. B. 'de/ratgeber/x.html' (relativ zu site/). alt_path: Gegenstück in der anderen Sprache."""
    depth = path.count("/") - 1
    url = BASE + "/" + path.replace("index.html", "").replace(".html", "")
    alt_url = BASE + "/" + alt_path.replace("index.html", "").replace(".html", "")
    de_url, en_url = (url, alt_url) if lang == "de" else (alt_url, url)
    head_static, style, pre_main, post_main = template(lang)
    own = path.split("/")[-1]
    other_rel = "../" * (depth + 1) + alt_path
    pre_main = lang_switch(fix_rel(pre_main, depth), lang, own, other_rel)
    post_main = fix_rel(post_main, depth)
    style = fix_rel(style, depth)
    crumb_html = "".join(
        (f'<li><a href="{"../" * depth}index.html">{HOME_ICON}<span>{e(n)}</span></a></li>' if i == 0 else
         f'<li class="crumb-mid"><a href="{h}">{e(n)}</a></li>' if h else f'<li><span aria-current="page">{e(n)}</span></li>')
        for i, (n, h) in enumerate(crumbs))
    ld = "".join(f'<script type="application/ld+json">{json.dumps(x, ensure_ascii=False)}</script>' for x in schema)
    return f"""<!doctype html>
<html lang="{lang}">
<head>
<meta charset="utf-8"/>
<meta content="width=device-width, initial-scale=1, viewport-fit=cover" name="viewport"/>
<title>{e(title)}</title>
<meta content="{e(meta)}" name="description"/>
<link href="{url}" rel="canonical"/>
<link href="{de_url}" hreflang="de" rel="alternate"/><link href="{en_url}" hreflang="en" rel="alternate"/><link href="{de_url}" hreflang="x-default" rel="alternate"/>
<meta content="{og_type}" property="og:type"/>
<meta content="devunoxAI" property="og:site_name"/>
<meta content="{e(title)}" property="og:title"/>
<meta content="{e(meta)}" property="og:description"/>
<meta content="{url}" property="og:url"/>
<meta content="{L[lang]['locale']}" property="og:locale"/><meta content="{OG[lang]}" property="og:image"/><meta content="1200" property="og:image:width"/><meta content="630" property="og:image:height"/><meta content="devunoxAI" property="og:image:alt"/><meta content="summary_large_image" name="twitter:card"/>

{head_static}
{ld}
{style}</head>
{pre_main}<main>
<section class="hero-sub legal-hero"><div class="w">
  <nav class="crumbs" aria-label="Breadcrumb"><ol>{crumb_html}</ol></nav>
  <h1>{e(h1)}</h1>
  <p class="hh-lead">{e(lede)}</p>{meta_line}
</div></section>
{main}
</main>{post_main}"""

def faq_html(lang, faq):
    items = "".join(f'<details><summary><span>{e(q)}</span><i aria-hidden="true"></i></summary><p>{e(a)}</p></details>' for q, a in faq)
    return f'<section class="sec"><div class="w sec-in split"><div class="sec-head sticky"><p class="kicker">{L[lang]["faq_k"]}</p><h2>{L[lang]["faq_h"]}</h2></div><div class="faq">{items}</div></div></section>'

def faq_ld(faq):
    return {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
        {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in faq]}

def crumb_ld(items):
    return {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": i + 1, "name": n, "item": u} for i, (n, u) in enumerate(items)]}

def cta(lang, depth):
    pre = "../" * depth
    h = "Erzählen Sie uns, was Sie Zeit kostet" if lang == "de" else "Tell us what costs you time"
    p = ("Im kostenlosen Erstgespräch finden wir heraus, wo sich Automatisierung oder eigene Software für Sie lohnt." if lang == "de"
         else "In a free intro call we find out where automation or your own software pays off for you.")
    b = "Erstgespräch anfragen" if lang == "de" else "Book an intro call"
    return f'<section class="cta"><div class="w cta-in"><h2>{h}</h2><div class="cta-side"><p>{p}</p><a class="btn btn-ink" href="{pre}{L[lang]["contact"]}">{b}{ARROW}</a></div></div></section>'

def card(lang, a, href):
    x = a[lang]
    return f'<a href="{href}"><small>{fmt_date(a["date"], lang)} · {read_min(x)} {L[lang]["read"]}</small><b>{e(x["h1"])}</b><span>{e(x["lede"])}</span></a>'

# ----------------------------------------------------------------------------- Seiten bauen

def build():
    written = []
    other = {"de": "en", "en": "de"}
    for lang in ("de", "en"):
        c, hub = L[lang], L[lang]["hub_dir"]
        # Über uns
        a = ABOUT[lang]
        path, alt = f"{lang}/{c['about']}.html", f"{other[lang]}/{L[other[lang]]['about']}.html"
        url = f"{BASE}/{lang}/{c['about']}"
        main = f'<section class="sec"><div class="w article">{a["body"]}</div></section>{faq_html(lang, a["faq"])}{cta(lang, 0)}'
        schema = [{"@context": "https://schema.org", "@type": "AboutPage", "name": a["h1"], "url": url, "inLanguage": lang, "about": {"@id": ORG}, "mainEntity": {"@id": ORG}},
                  crumb_ld([(c["home"], f"{BASE}/{lang}/"), (c["about_name"], url)]), faq_ld(a["faq"])]
        (SITE / path).write_text(page(lang, path, alt, a["title"], a["meta"], a["h1"], a["lede"], [(c["home"], None), (c["about_name"], None)], main, schema), encoding="utf-8")
        written.append(path)

        # Ratgeber-Übersicht
        (SITE / lang / hub).mkdir(exist_ok=True)
        hub_path, hub_alt = f"{lang}/{hub}/index.html", f"{other[lang]}/{L[other[lang]]['hub_dir']}/index.html"
        hub_url = f"{BASE}/{lang}/{hub}/"
        posts = sorted(ARTICLES, key=lambda x: x["date"], reverse=True)
        cards = "".join(card(lang, x, f'{x[lang]["slug"]}.html') for x in posts)
        hub_title = "Ratgeber: KI-Automatisierung & Software für KMU | devunoxAI" if lang == "de" else "Insights: AI Automation & Custom Software | devunoxAI"
        hub_meta = ("Praxisnahe Ratgeber zu KI-Automatisierung, Kosten, DSGVO und EU AI Act, E-Rechnung und Individualsoftware für kleine und mittlere Unternehmen." if lang == "de"
                    else "Practical guides on AI automation, costs, GDPR and the EU AI Act, invoice automation and custom software for small and mid-sized businesses.")
        hub_h1 = "Ratgeber für KI und Software im Mittelstand" if lang == "de" else "Insights on AI and software for growing businesses"
        hub_lede = ("Praxiswissen zu KI-Automatisierung, Kosten, Recht und eigener Software. Ohne Hype, mit dem, was Sie für Ihre Entscheidung brauchen." if lang == "de"
                    else "Practical know-how on AI automation, costs, regulation and custom software. No hype, just what you need to decide.")
        main = f'<section class="sec"><div class="w sec-in"><div class="post-list">{cards}</div></div></section>{cta(lang, 1)}'
        schema = [{"@context": "https://schema.org", "@type": "Blog", "@id": hub_url + "#blog", "name": f"devunoxAI {c['hub_name']}", "url": hub_url, "inLanguage": lang,
                   "publisher": {"@id": ORG}, "blogPost": [{"@type": "BlogPosting", "headline": x[lang]["h1"], "url": f"{hub_url}{x[lang]['slug']}", "datePublished": x["date"]} for x in posts]},
                  crumb_ld([(c["home"], f"{BASE}/{lang}/"), (c["hub_name"], hub_url)])]
        (SITE / hub_path).write_text(page(lang, hub_path, hub_alt, hub_title, hub_meta, hub_h1, hub_lede, [(c["home"], None), (c["hub_name"], None)], main, schema), encoding="utf-8")
        written.append(hub_path)

        # Artikel
        for x in posts:
            art = x[lang]
            path = f"{lang}/{hub}/{art['slug']}.html"
            alt = f"{other[lang]}/{L[other[lang]]['hub_dir']}/{x[other[lang]]['slug']}.html"
            url = f"{BASE}/{lang}/{hub}/{art['slug']}"
            take = "".join(f"<li>{e(t)}</li>" for t in art["take"])
            others = [y for y in posts if y is not x][:2]
            more = "".join(card(lang, y, f'{y[lang]["slug"]}.html') for y in others)
            meta_line = f'\n  <div class="post-meta"><span>{fmt_date(x["date"], lang)}</span><span>{read_min(art)} {c["read"]}</span><span>{c["by"]}</span></div>'
            main = (f'<section class="sec"><div class="w article"><div class="take"><b>{c["take"]}</b><ul>{take}</ul></div>{art["body"]}</div></section>'
                    f'{faq_html(lang, art["faq"])}'
                    f'<section class="sec soft"><div class="w sec-in"><div class="sec-head"><p class="kicker">{c["more_k"]}</p><h2>{c["more_h"]}</h2></div><div class="post-list">{more}</div></div></section>'
                    f'{cta(lang, 1)}')
            schema = [{"@context": "https://schema.org", "@type": "BlogPosting", "headline": art["h1"], "description": art["meta"], "url": url, "mainEntityOfPage": url,
                       "datePublished": x["date"], "dateModified": x.get("updated", x["date"]), "inLanguage": lang, "image": OG[lang],
                       "author": {"@type": "Person", "name": "Hüseyin Yigit", "jobTitle": "CEO"}, "publisher": {"@id": ORG}, "isPartOf": {"@id": hub_url + "#blog"}},
                      crumb_ld([(c["home"], f"{BASE}/{lang}/"), (c["hub_name"], hub_url), (art["h1"], url)]), faq_ld(art["faq"])]
            (SITE / path).write_text(page(lang, path, alt, art["title"], art["meta"], art["h1"], art["lede"],
                                          [(c["home"], None), (c["hub_name"], "index.html"), (art["h1"], None)], main, schema, "article", meta_line), encoding="utf-8")
            written.append(path)
    return written

def related_sections():
    """'Ratgeber'-Abschnitt vor dem CTA der passenden Leistungsseiten einfügen bzw. aktualisieren."""
    for lang in ("de", "en"):
        c = L[lang]
        for svc in {s for a in ARTICLES for s in a["services"][lang]}:
            p = SITE / lang / svc
            s = p.read_text(encoding="utf-8")
            s = re.sub(r'<section class="sec soft related-guides">.*?</section>\n?', "", s, flags=re.S)
            hits = [a for a in ARTICLES if svc in a["services"][lang]][:2]
            cards = "".join(card(lang, a, f'{c["hub_dir"]}/{a[lang]["slug"]}.html') for a in hits)
            k = "Ratgeber" if lang == "de" else "Insights"
            h = "Gut zu wissen" if lang == "de" else "Good to know"
            sec = f'<section class="sec soft related-guides"><div class="w sec-in"><div class="sec-head"><p class="kicker">{k}</p><h2>{h}</h2></div><div class="post-list">{cards}</div></div></section>\n'
            s = s.replace('<section class="cta">', sec + '<section class="cta">', 1)
            p.write_text(s, encoding="utf-8")

if __name__ == "__main__":
    files = build()
    related_sections()
    print("\n".join(files))
