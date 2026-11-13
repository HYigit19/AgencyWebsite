"""Erzeugt bzw. aktualisiert die Vertriebs-Bausteine der Website (DE/EN):

- Lösungsseiten (site/de/loesungen/, site/en/solutions/): eine Seite pro Kundenproblem, mit passender Demo
- Messe-/Event-Seite für den QR-Code (site/de/messe.html, site/en/event.html, nicht indexiert)
- Abschnitt "Kostenloser Pilot" auf der Startseite und Pilot-Angebot im CTA aller Seiten
- Abschnitt "Fallbeispiele" auf der Startseite, sobald CASES Einträge hat (leer = kein Abschnitt)
- Footer-Link "Lösungen", Einbindung von assets/consent.js (Google-Ads-Messung, erst nach Einwilligung)

Aufruf: python3 tools/growth_pages.py   (danach committen; build.py bleibt unverändert)
Das Skript kann beliebig oft laufen, es ersetzt seine eigenen Abschnitte statt sie zu doppeln.
Kopf und Fuß kommen wie bei tools/content_pages.py aus einer bestehenden Leistungsseite.
"""
import html, re, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import content_pages as cp  # noqa: E402

SITE, BASE, ORG, ARROW = cp.SITE, cp.BASE, cp.ORG, cp.ARROW
e = html.escape
TICK = '<span class="tick" aria-hidden="true"><svg viewBox="0 0 16 16"><path d="M3.5 8.5l3 3 6-7" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg></span>'
CROSS = '<span class="tick tick-x" aria-hidden="true"><svg viewBox="0 0 16 16"><path d="M5 5l6 6M11 5l-6 6" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"/></svg></span>'
ROUND = '<span class="round-arrow" aria-hidden="true">' + ARROW + '</span>'

L = {
 "de": dict(dir="loesungen", hub="Lösungen", home="Start", contact="kontakt.html", demos="demos.html", event="messe.html",
            pilot_btn="Kostenlosen Pilot anfragen", demo_btn="Demo ansehen", demo_open="Demo öffnen", sol="Lösung",
            pain_k="Das Problem", pain_h="Kennen Sie das?", fix_k="Die Lösung", fix_h="So funktioniert es",
            demo_k="Demo zum Ausprobieren", demo_h="So kann das aussehen", demo_lead="Ein Beispiel mit fiktiven Daten. Ihre Lösung bauen wir passend zu Ihren Abläufen.",
            path_k="Kostenloser Pilot", path_h="Erst sehen, dann entscheiden",
            path_lead="Wir bauen eine erste Version Ihrer Lösung mit Ihren eigenen Beispielen. Sie zahlen erst, wenn Sie überzeugt sind.",
            steps=[("30 Minuten · kostenlos", "Gespräch", "Sie zeigen uns die Aufgabe, die am meisten Zeit kostet."),
                   ("ca. 1 Woche · kostenlos", "Pilot", "Wir bauen eine funktionierende erste Version mit Ihren Beispielen."),
                   ("in Ihrem Alltag", "Test", "Sie und Ihr Team probieren den Piloten mit echten Fällen aus."),
                   ("Ihre Entscheidung", "Festpreis", "Überzeugt Sie das Ergebnis, erhalten Sie einen verbindlichen Festpreis. Wenn nicht, entstehen keine Kosten.")],
            cta_p="Im kostenlosen Erstgespräch finden wir heraus, wo sich Automatisierung oder eigene Software für Sie lohnt. Den Piloten bauen wir kostenlos.",
            cases_k="Fallbeispiele", cases_h="Aus unseren Pilotprojekten", cases_labels=("Ausgangslage", "Lösung", "Ergebnis"),
            footer_after='ki-qualitaetsmanagement.html">KI im Qualitätsmanagement</a></li>'),
 "en": dict(dir="solutions", hub="Solutions", home="Home", contact="contact.html", demos="demos.html", event="event.html",
            pilot_btn="Request a free pilot", demo_btn="View the demo", demo_open="Open demo", sol="Solution",
            pain_k="The problem", pain_h="Sound familiar?", fix_k="The solution", fix_h="How it works",
            demo_k="Try the demo", demo_h="What it can look like", demo_lead="An example with fictional data. Your solution is built around your own processes.",
            path_k="Free pilot", path_h="See it first, then decide",
            path_lead="We build a first version of your solution with your own examples. You only pay once you are convinced.",
            steps=[("30 minutes · free", "Call", "You show us the task that costs the most time."),
                   ("about 1 week · free", "Pilot", "We build a working first version with your examples."),
                   ("in your daily work", "Test", "You and your team try the pilot with real cases."),
                   ("your decision", "Fixed price", "If the result convinces you, you get a binding fixed price. If not, there is no cost.")],
            cta_p="In a free intro call we find out where automation or custom software pays off for you. We build the pilot free of charge.",
            cases_k="Case studies", cases_h="From our pilot projects", cases_labels=("Starting point", "Solution", "Result"),
            footer_after='ai-quality-management.html">AI for quality management</a></li>'),
}

# ----------------------------------------------------------------------------- Lösungsseiten

SOLUTIONS = [
 dict(demo="makler", shot="makler", de=dict(
   slug="ki-posteingang", name="KI-Posteingang", title="KI-Posteingang für Unternehmen | devunoxAI",
   meta="Der KI-Posteingang liest eingehende E-Mails, erkennt das Anliegen, übernimmt die Daten ins CRM und bereitet Antworten vor. Kostenloser Pilot, Hosting in der EU.",
   h1="KI-Posteingang: Anfragen beantworten sich fast von selbst",
   lede="Jeden Tag landen Anfragen, Bestellungen und Rückfragen im Postfach. Der KI-Posteingang sortiert sie, erkennt das Anliegen und bereitet die Antwort vor. Ihr Team prüft und schickt ab.",
   pains=[("Das Postfach wächst schneller, als Sie antworten", "Wichtige Anfragen gehen zwischen Newslettern, Rechnungen und Rückfragen unter."),
          ("Immer wieder dieselben Fragen", "Lieferzeiten, Preise, Unterlagen: Ihr Team schreibt jeden Tag ähnliche Antworten neu."),
          ("Daten werden abgetippt", "Name, Firma, Menge und Termin wandern von Hand aus der E-Mail ins CRM oder ERP.")],
   fixes=[("Anliegen erkennen", "Die KI ordnet jede E-Mail ein, zum Beispiel als Anfrage, Bestellung, Reklamation oder Rechnung, und setzt eine Priorität."),
          ("Daten übernehmen", "Kunde, Produkt, Menge und Frist werden ausgelesen und in Ihr CRM, ERP oder eine Tabelle übertragen."),
          ("Antwort vorbereiten", "Zu jeder Anfrage liegt ein Antwortentwurf auf Basis Ihrer Unterlagen bereit. Ein Mensch prüft und gibt frei."),
          ("An die richtige Person", "Die E-Mail landet direkt bei der zuständigen Person, mit Zusammenfassung und nächstem Schritt."),
          ("Mit Ihrem bestehenden Postfach", "Ihr Team arbeitet weiter im gewohnten Postfach. Welche Anbindung passt, klären wir im Erstgespräch.")],
   demo_kind="Kundenindividuelle Software + KI", demo_field="Immobilien", demo_h="Makler-Suite mit KI-Posteingang",
   demo_p="Anfragen aus E-Mails und Portalen werden automatisch zu Leads: Die KI liest Kontakt, Objekt und Budget aus und weist die passende Person zu.",
   faq=[("Schickt die KI Antworten ohne Prüfung raus?", "Nur wenn Sie das ausdrücklich wollen. Üblich ist, dass die KI einen Entwurf vorbereitet und ein Mensch freigibt."),
        ("Welche Postfächer werden unterstützt?", "Wir binden gängige Postfächer an, zum Beispiel Microsoft 365 oder Google Workspace. Welche Anbindung für Sie passt, klären wir im Erstgespräch."),
        ("Was passiert mit unseren E-Mails?", "Die Verarbeitung läuft in Rechenzentren in der EU, DSGVO-konform mit Vertrag zur Auftragsverarbeitung. Ihre Daten werden nicht zum Training von KI-Modellen verwendet.")]),
  en=dict(
   slug="ai-inbox", name="AI inbox", title="AI inbox for businesses | devunoxAI",
   meta="The AI inbox reads incoming emails, recognises the request, adds the data to your CRM and drafts replies. Free pilot, hosting in the EU.",
   h1="AI inbox: requests that almost answer themselves",
   lede="Every day, enquiries, orders and follow-up questions land in your inbox. The AI inbox sorts them, recognises the request and drafts the reply. Your team checks and sends.",
   pains=[("The inbox grows faster than you can reply", "Important requests get lost between newsletters, invoices and follow-ups."),
          ("The same questions over and over", "Delivery times, prices, documents: your team rewrites similar answers every day."),
          ("Data is typed in by hand", "Name, company, quantity and date are copied from the email into the CRM or ERP.")],
   fixes=[("Recognise the request", "The AI classifies every email, for example as an enquiry, order, complaint or invoice, and sets a priority."),
          ("Take over the data", "Customer, product, quantity and deadline are extracted and transferred to your CRM, ERP or a spreadsheet."),
          ("Draft the reply", "Every request comes with a draft answer based on your documents. A person checks and approves it."),
          ("To the right person", "The email goes straight to the person in charge, with a summary and the next step."),
          ("With your existing inbox", "Your team keeps working in the inbox they know. We agree on the right connection in the intro call.")],
   demo_kind="Custom software + AI", demo_field="Real estate", demo_h="Real estate suite with AI inbox",
   demo_p="Requests from emails and portals turn into leads automatically: the AI extracts contact, property and budget and assigns the right person.",
   faq=[("Does the AI send replies without a check?", "Only if you explicitly want it to. Usually the AI prepares a draft and a person approves it."),
        ("Which mailboxes are supported?", "We connect common mailboxes such as Microsoft 365 or Google Workspace. We agree on the right connection in the intro call."),
        ("What happens to our emails?", "Processing runs in data centres in the EU, GDPR compliant with a data processing agreement. Your data is not used to train AI models.")])),

 dict(demo="pod", shot="pod", de=dict(
   slug="dokumente-auslesen", name="Dokumente automatisch auslesen", title="Dokumente automatisch auslesen mit KI | devunoxAI",
   meta="KI liest Rechnungen, Lieferscheine und Formulare aus und überträgt die Daten in ERP, Buchhaltung oder Tabelle. Kostenloser Pilot, Hosting in der EU.",
   h1="Dokumente automatisch auslesen statt abtippen",
   lede="Rechnungen, Lieferscheine, Auftragsbestätigungen und Formulare: Die KI liest die Daten aus, prüft sie und überträgt sie in Ihr System. Ihr Team kümmert sich nur noch um die Ausnahmen.",
   pains=[("Stapel von PDFs und Scans", "Dokumente kommen per E-Mail, Post oder Foto und werden von Hand erfasst."),
          ("Tippfehler kosten Geld", "Ein Zahlendreher bei Menge, Preis oder Bankverbindung fällt oft erst spät auf."),
          ("Wissen steckt in wenigen Köpfen", "Nur wenige Mitarbeitende wissen, welche Angabe wohin gehört.")],
   fixes=[("Jedes Format", "PDF, Scan, Foto vom Handy oder E-Mail-Anhang, auch mehrseitig."),
          ("Felder erkennen", "Absender, Nummern, Positionen, Beträge, Daten und Fristen werden strukturiert ausgelesen."),
          ("Abgleich und Prüfung", "Die Daten werden mit Bestellung oder Stammdaten verglichen. Unsichere Felder werden markiert."),
          ("Übergabe an Ihr System", "Die Daten landen in ERP, Buchhaltung oder Tabelle, per Schnittstelle oder Export."),
          ("Freigabe durch den Menschen", "Ihr Team prüft nur noch markierte Felder und gibt frei.")],
   demo_kind="Kundenindividuelle Software + Handy-App", demo_field="Logistik", demo_h="Proof of Delivery mit KI",
   demo_p="Der Fahrer fotografiert Lieferschein, CMR oder Rechnung mit dem Handy. Die KI erkennt den Dokumenttyp, liest Nummern und Mengen aus und trägt alles in den Auftrag ein.",
   faq=[("Wie genau ist das Auslesen?", "Das hängt von der Qualität der Dokumente ab. Deshalb testen wir im kostenlosen Piloten mit Ihren echten Beispielen, bevor Sie sich entscheiden. Unsichere Felder werden immer markiert."),
        ("Funktioniert das auch mit E-Rechnungen?", "Ja. Strukturierte E-Rechnungen wie XRechnung oder ZUGFeRD lassen sich direkt einlesen, Papier- und PDF-Rechnungen liest die KI aus."),
        ("Wo werden die Dokumente gespeichert?", "In Rechenzentren in der EU, DSGVO-konform mit Vertrag zur Auftragsverarbeitung. Ihre Daten werden nicht zum Training von KI-Modellen verwendet.")]),
  en=dict(
   slug="document-extraction", name="Automatic document extraction", title="Extract data from documents with AI | devunoxAI",
   meta="AI reads invoices, delivery notes and forms and transfers the data to your ERP, accounting or spreadsheet. Free pilot, hosting in the EU.",
   h1="Extract data from documents instead of typing it",
   lede="Invoices, delivery notes, order confirmations and forms: the AI extracts the data, checks it and transfers it to your system. Your team only handles the exceptions.",
   pains=[("Piles of PDFs and scans", "Documents arrive by email, post or photo and are entered by hand."),
          ("Typos cost money", "A swapped digit in a quantity, price or bank account is often noticed too late."),
          ("Know-how sits with a few people", "Only a few colleagues know which detail goes where.")],
   fixes=[("Any format", "PDF, scan, phone photo or email attachment, including multi-page documents."),
          ("Recognise the fields", "Sender, numbers, line items, amounts, dates and deadlines are extracted in a structured way."),
          ("Match and check", "The data is compared with the order or master data. Uncertain fields are flagged."),
          ("Hand over to your system", "The data lands in your ERP, accounting or spreadsheet, via interface or export."),
          ("A person approves", "Your team only reviews flagged fields and approves.")],
   demo_kind="Custom software + mobile app", demo_field="Logistics", demo_h="Proof of delivery with AI",
   demo_p="The driver photographs the delivery note, CMR or invoice. The AI recognises the document type, reads numbers and quantities and adds everything to the order.",
   faq=[("How accurate is the extraction?", "That depends on the quality of the documents. That is why we test with your real examples in the free pilot before you decide. Uncertain fields are always flagged."),
        ("Does it work with e-invoices?", "Yes. Structured e-invoices such as XRechnung or ZUGFeRD can be read directly; the AI extracts paper and PDF invoices."),
        ("Where are the documents stored?", "In data centres in the EU, GDPR compliant with a data processing agreement. Your data is not used to train AI models.")])),

 dict(demo="wissen", shot="wissen", de=dict(
   slug="wissensdatenbank-ki", name="Wissensdatenbank mit KI", title="Wissensdatenbank mit KI-Suche | devunoxAI",
   meta="Fragen stellen statt suchen: Die KI-Wissensdatenbank beantwortet Fragen aus Handbüchern, Verträgen und Richtlinien, immer mit Quelle. Kostenloser Pilot.",
   h1="Wissensdatenbank mit KI: Fragen stellen statt suchen",
   lede="Handbücher, Verträge, Prozessbeschreibungen und Richtlinien liegen verstreut auf Laufwerken. Mit der KI-Wissensdatenbank fragt Ihr Team einfach nach und bekommt die Antwort mit Quelle.",
   pains=[("Suchen kostet Stunden", "Die richtige Version eines Dokuments zu finden, dauert oft länger als die eigentliche Arbeit."),
          ("Immer dieselben Rückfragen", "Erfahrene Kolleginnen und Kollegen beantworten täglich die gleichen Fragen."),
          ("Einarbeitung dauert", "Neue Mitarbeitende brauchen Wochen, bis sie wissen, wo was steht.")],
   fixes=[("Fragen in normaler Sprache", "Zum Beispiel: Welche Gewährleistung haben wir mit Kunde X vereinbart?"),
          ("Antwort mit Quelle", "Jede Antwort verweist auf das Dokument und die Stelle, aus der sie stammt."),
          ("Ihre Dokumente, Ihre Rechte", "PDFs, Word-Dateien und Wiki-Seiten werden eingebunden. Jede Person sieht nur, was sie sehen darf."),
          ("Lücken erkennen", "Fragen ohne gute Antwort werden gesammelt, damit Sie Ihr Wissen gezielt ergänzen.")],
   demo_kind="Kundenindividuelle Software", demo_field="Wissen", demo_h="Wissensdatenbank mit KI-Suche",
   demo_p="Fragen stellen statt suchen: Antworten aus PDFs, Word-Dateien und Wiki mit Quellenangabe. Dazu Dokumente hochladen und Wiki pflegen.",
   faq=[("Erfindet die KI Antworten?", "Die Wissensdatenbank antwortet aus Ihren Dokumenten und zeigt die Quelle. Findet sie nichts Passendes, sagt sie das."),
        ("Welche Dateien können eingebunden werden?", "Gängige Formate wie PDF, Word und Textdateien sowie Wiki-Seiten. Weitere Quellen klären wir im Erstgespräch."),
        ("Können vertrauliche Dokumente geschützt werden?", "Ja. Zugriffsrechte werden wie in Ihrer Ablage abgebildet. Gehostet wird in der EU, DSGVO-konform.")]),
  en=dict(
   slug="ai-knowledge-base", name="AI knowledge base", title="AI knowledge base with search | devunoxAI",
   meta="Ask instead of searching: the AI knowledge base answers questions from manuals, contracts and policies, always with the source. Free pilot.",
   h1="AI knowledge base: ask instead of searching",
   lede="Manuals, contracts, process descriptions and policies are scattered across drives. With the AI knowledge base your team simply asks and gets the answer with its source.",
   pains=[("Searching takes hours", "Finding the right version of a document often takes longer than the actual work."),
          ("The same questions every day", "Experienced colleagues answer the same questions again and again."),
          ("Onboarding takes long", "New staff need weeks to learn where everything is.")],
   fixes=[("Questions in plain language", "For example: which warranty did we agree with customer X?"),
          ("Answers with sources", "Every answer links to the document and the passage it comes from."),
          ("Your documents, your permissions", "PDFs, Word files and wiki pages are connected. Everyone only sees what they are allowed to see."),
          ("Spot the gaps", "Questions without a good answer are collected so you can add the missing knowledge.")],
   demo_kind="Custom software", demo_field="Knowledge", demo_h="Knowledge base with AI search",
   demo_p="Ask instead of searching: answers from PDFs, Word files and the wiki, with sources. Plus document upload and wiki editing.",
   faq=[("Does the AI make up answers?", "The knowledge base answers from your documents and shows the source. If it finds nothing suitable, it says so."),
        ("Which files can be connected?", "Common formats such as PDF, Word and text files as well as wiki pages. We agree on other sources in the intro call."),
        ("Can confidential documents be protected?", "Yes. Access rights mirror your existing file structure. Hosting is in the EU, GDPR compliant.")])),

 dict(demo="suite", shot="kunden", anchor="#kunden", de=dict(
   slug="reklamationsmanagement-software", name="Reklamationsmanagement", title="Reklamationsmanagement-Software | devunoxAI",
   meta="Kunden- und Lieferantenreklamationen digital erfassen, mit 8D und Maßnahmen bearbeiten und Fristen im Blick behalten. Als eigene Lösung, kostenloser Pilot.",
   h1="Reklamationsmanagement ohne Excel-Listen und E-Mail-Pingpong",
   lede="Kunden- und Lieferantenreklamationen an einem Ort: erfassen, Ursachen klären, Maßnahmen verfolgen und Fristen einhalten. Zugeschnitten auf Ihre Abläufe, mit KI-Unterstützung.",
   pains=[("Reklamationen in Excel und Postfach", "Status, Fotos und Antworten verteilen sich auf Listen, Ordner und E-Mails."),
          ("Fristen werden knapp", "Wer muss bis wann was tun? Ohne Übersicht laufen Termine aus."),
          ("Dieselben Fehler kommen wieder", "Ursachen und Maßnahmen werden nicht sauber ausgewertet.")],
   fixes=[("Erfassung in Minuten", "Reklamation per Formular, E-Mail oder Handy mit Fotos und Dokumenten anlegen."),
          ("Strukturierte Bearbeitung", "Von der Sofortmaßnahme bis zum Abschluss, zum Beispiel nach 8D, mit klaren Zuständigkeiten."),
          ("Fristen und Erinnerungen", "Automatische Erinnerungen, bevor ein Termin verstreicht."),
          ("KI hilft beim Schreiben", "Die KI fasst Fälle zusammen und schlägt Antworten und Berichte vor."),
          ("Auswertung auf Knopfdruck", "Kennzahlen nach Kunde, Lieferant, Fehlerart und Kosten.")],
   demo_kind="App-Suite", demo_field="Qualität", demo_h="Workflow und Reklamationen in einer App",
   demo_p="Workflow Management, Kundenreklamationen und Lieferantenreklamationen in einer App, mit gemeinsamen Stammdaten, Aufgaben und Auswertungen.",
   faq=[("Passt das zu unserem Qualitätsmanagement?", "Wir bilden Ihre Abläufe und Formulare ab, statt Sie an einen Standard anzupassen. Bestehende Daten lassen sich übernehmen."),
        ("Können Lieferanten mitarbeiten?", "Auf Wunsch ja, über einen eigenen Zugang, in dem sie nur ihre eigenen Fälle sehen."),
        ("Was kostet das?", "Den Piloten bauen wir kostenlos. Danach erhalten Sie einen Festpreis, ohne Abo pro Nutzer.")]),
  en=dict(
   slug="complaint-management-software", name="Complaint management", title="Complaint management software | devunoxAI",
   meta="Record customer and supplier complaints digitally, work through 8D and actions and keep deadlines in view. Built for you, with a free pilot.",
   h1="Complaint management without spreadsheets and email ping-pong",
   lede="Customer and supplier complaints in one place: record them, find root causes, track actions and meet deadlines. Tailored to your processes, with AI support.",
   pains=[("Complaints in spreadsheets and inboxes", "Status, photos and replies are spread across lists, folders and emails."),
          ("Deadlines get tight", "Who has to do what by when? Without an overview, dates slip."),
          ("The same defects come back", "Root causes and actions are not evaluated properly.")],
   fixes=[("Recorded in minutes", "Create a complaint by form, email or phone, with photos and documents."),
          ("Structured handling", "From containment to closure, for example following 8D, with clear responsibilities."),
          ("Deadlines and reminders", "Automatic reminders before a deadline passes."),
          ("AI helps with writing", "The AI summarises cases and suggests replies and reports."),
          ("Reports at the push of a button", "Figures by customer, supplier, defect type and cost.")],
   demo_kind="App suite", demo_field="Quality", demo_h="Workflow and complaints in one app",
   demo_p="Workflow management, customer complaints and supplier complaints in one app, with shared master data, tasks and reports.",
   faq=[("Does it fit our quality management?", "We map your processes and forms instead of forcing you into a standard. Existing data can be migrated."),
        ("Can suppliers take part?", "If you want, yes, through their own access where they only see their own cases."),
        ("What does it cost?", "We build the pilot free of charge. After that you get a fixed price, with no per-user subscription.")])),

 dict(demo="geoauftrag", shot="geoauftrag", de=dict(
   slug="aussendienst-app", name="Außendienst-App", title="Außendienst-App mit GPS und Fotos | devunoxAI",
   meta="Aufträge aufs Handy, Rückmeldung mit Fotos und GPS-Standort, das Büro sieht alles live. Die Außendienst-App als eigene Lösung für Ihr Team. Kostenloser Pilot.",
   h1="Außendienst-App: Aufträge raus, Rückmeldungen rein",
   lede="Ihr Team im Außendienst bekommt Aufträge aufs Handy und meldet mit Fotos, Dokumenten und Standort zurück. Im Büro sehen Sie live, wer wo was erledigt hat.",
   pains=[("Zettel, Anrufe und Chatnachrichten", "Aufträge und Rückmeldungen laufen über viele Kanäle und gehen verloren."),
          ("Nachweise fehlen", "Ob eine Arbeit erledigt wurde, lässt sich im Streitfall schwer belegen."),
          ("Abrechnung verzögert sich", "Bis alle Rückmeldungen im Büro sind, vergehen Tage.")],
   fixes=[("Aufträge aufs Handy", "Mit Adresse, Navigation, Unterlagen und Checkliste."),
          ("Rückmeldung mit Nachweis", "Fotos, Material und Dokumente, automatisch mit Zeit und Standort."),
          ("Überblick im Büro", "Karte, Status und Verlauf aller Aufträge, bereit für die Abrechnung."),
          ("Passend zu Ihren Abläufen", "Felder, Checklisten und Freigaben richten wir nach Ihrem Bedarf ein.")],
   demo_kind="Kundenindividuelle Software", demo_field="Bau und Service", demo_h="GeoAuftrag: Feldaufträge mit GPS-Nachweis",
   demo_p="Monteure melden vom Handy mit automatischem Standort, Fotostempel und Materialverbrauch. Das Büro sieht, wer wo was gemacht hat.",
   faq=[("Brauchen unsere Mitarbeitenden ein bestimmtes Handy?", "Nein. Die App läuft auf Android und iPhone. Welche Geräte Sie nutzen, klären wir im Erstgespräch."),
        ("Wird der Standort dauerhaft verfolgt?", "Nein. Der Standort wird bei einer Rückmeldung gespeichert, nicht laufend. Die Regeln dafür legen wir gemeinsam mit Ihnen fest."),
        ("Lässt sich das an unsere Abrechnung anbinden?", "Ja, zum Beispiel per Export oder Schnittstelle zu Ihrer Buchhaltung oder Ihrem ERP.")]),
  en=dict(
   slug="field-service-app", name="Field service app", title="Field service app with GPS and photos | devunoxAI",
   meta="Jobs on the phone, reports with photos and GPS location, the office sees everything live. A field service app built for your team. Free pilot.",
   h1="Field service app: jobs out, reports in",
   lede="Your field team gets jobs on their phones and reports back with photos, documents and location. In the office you see live who did what and where.",
   pains=[("Paper, calls and chat messages", "Jobs and reports run through many channels and get lost."),
          ("Missing proof", "In a dispute, it is hard to prove that a job was done."),
          ("Invoicing is delayed", "It takes days until all reports reach the office.")],
   fixes=[("Jobs on the phone", "With address, navigation, documents and checklist."),
          ("Reports with proof", "Photos, material and documents, automatically with time and location."),
          ("Overview in the office", "Map, status and history of all jobs, ready for invoicing."),
          ("Fits your processes", "Fields, checklists and approvals are set up to match your needs.")],
   demo_kind="Custom software", demo_field="Construction and service", demo_h="GeoAuftrag: field jobs with GPS proof",
   demo_p="Technicians report from their phone with automatic location, photo stamp and material used. The office sees who did what and where.",
   faq=[("Do our people need a specific phone?", "No. The app runs on Android and iPhone. We clarify which devices you use in the intro call."),
        ("Is the location tracked all the time?", "No. The location is stored with a report, not continuously. We agree on the rules together with you."),
        ("Can it connect to our invoicing?", "Yes, for example via export or an interface to your accounting or ERP.")])),
]

# Fallbeispiele: erst eintragen, wenn ein Pilotkunde zugestimmt hat. Leer = kein Abschnitt auf der Startseite.
# Format: dict(de=dict(company="Name oder z. B. 'Spedition aus Hessen'", field="Logistik", start="...", solution="...", result="..."), en=dict(...))
CASES = []

# ----------------------------------------------------------------------------- Bausteine

def btn(cls, href, label):
    return f'<a class="btn {cls}" href="{href}">{e(label)}{ARROW}</a>'

def pilot_path(lang, pre=""):
    c = L[lang]
    steps = "".join(f'<li><span class="dot">{i}</span><span class="pill">{e(p)}</span><h3>{e(h)}</h3><p>{e(t)}</p></li>' for i, (p, h, t) in enumerate(c["steps"], 1))
    return (f'<section class="sec pilot-sec" id="pilot"><div class="w sec-in"><div class="sec-head"><p class="kicker">{c["path_k"]}</p><h2>{c["path_h"]}</h2>'
            f'<p class="sec-lead">{c["path_lead"]}</p></div><ol class="path">{steps}</ol>'
            f'<div class="demo-foot">{btn("btn-o", pre + c["contact"] + "#contact-form", c["pilot_btn"])}</div></div></section>')

def items(lst, tick=True):
    return "".join(f'<li>{TICK if tick else CROSS}<h3>{e(h)}</h3><p>{e(t)}</p></li>' for h, t in lst)

def solution_page(lang, s):
    c, x = L[lang], s[lang]
    other = "en" if lang == "de" else "de"
    path = f'{lang}/{c["dir"]}/{x["slug"]}.html'
    alt = f'{other}/{L[other]["dir"]}/{s[other]["slug"]}.html'
    url = f'{BASE}/{lang}/{c["dir"]}/{x["slug"]}'
    shot = s["shot"] + ("" if lang == "de" else "-en")
    demo_href = f'../../demos/{s["demo"]}.html?lang={lang}{s.get("anchor", "")}'
    hero_btns = f'\n  <div class="cta-row">{btn("btn-o", "../" + c["contact"] + "#contact-form", c["pilot_btn"])}<a class="btn btn-line" href="{demo_href}">{c["demo_btn"]}</a></div>'
    main = (
        f'<section class="sec soft"><div class="w sec-in split"><div class="sec-head sticky"><p class="kicker">{c["pain_k"]}</p><h2>{c["pain_h"]}</h2></div><ul class="task-list">{items(x["pains"], False)}</ul></div></section>'
        f'<section class="sec"><div class="w sec-in split"><div class="sec-head sticky"><p class="kicker">{c["fix_k"]}</p><h2>{c["fix_h"]}</h2></div><ul class="task-list">{items(x["fixes"])}</ul></div></section>'
        f'<section class="sec soft"><div class="w sec-in"><div class="sec-head"><p class="kicker">{c["demo_k"]}</p><h2>{c["demo_h"]}</h2><p class="sec-lead">{c["demo_lead"]}</p></div>'
        f'<div class="demo-grid demo-one"><a class="demo-card" href="{demo_href}"><div class="demo-shot"><img src="../../assets/demos/{shot}.jpg" alt="Screenshot: {e(x["demo_h"])}" width="1280" height="800" loading="lazy"></div>'
        f'<div class="demo-info"><div class="demo-meta"><span class="kind">{e(x["demo_kind"])}</span><span class="field">{e(x["demo_field"])}</span></div><h3>{e(x["demo_h"])}</h3><p>{e(x["demo_p"])}</p>'
        f'<span class="demo-open">{c["demo_open"]}{ARROW}</span></div></a></div></div></section>'
        + pilot_path(lang, "../") + cp.faq_html(lang, x["faq"]) + cta(lang, 1))
    hub_url = f'{BASE}/{lang}/{c["dir"]}/'
    schema = [{"@context": "https://schema.org", "@type": "Service", "name": x["name"], "description": x["meta"], "url": url, "inLanguage": lang,
               "provider": {"@id": ORG}, "areaServed": ["DE", "AT", "CH", "EU"]},
              cp.crumb_ld([(c["home"], f"{BASE}/{lang}/"), (c["hub"], hub_url), (x["name"], url)]), cp.faq_ld(x["faq"])]
    doc = cp.page(lang, path, alt, x["title"], x["meta"], x["h1"], x["lede"],
                  [(c["home"], None), (c["hub"], "index.html"), (x["name"], None)], main, schema, meta_line=hero_btns)
    return path, doc

def hub_page(lang):
    c = L[lang]
    other = "en" if lang == "de" else "de"
    path, alt = f'{lang}/{c["dir"]}/index.html', f'{other}/{L[other]["dir"]}/index.html'
    url = f'{BASE}/{lang}/{c["dir"]}/'
    cards = "".join(f'<a href="{s[lang]["slug"]}.html"><small>{c["sol"]}</small><b>{e(s[lang]["name"])}</b><span>{e(s[lang]["lede"])}</span></a>' for s in SOLUTIONS)
    if lang == "de":
        title, meta = "Lösungen für typische Aufgaben | devunoxAI", "KI-Posteingang, Dokumente auslesen, Wissensdatenbank, Reklamationsmanagement und Außendienst-App: Lösungen für KMU, mit kostenlosem Pilot."
        h1, lede = "Lösungen für Aufgaben, die jeden Tag Zeit kosten", "Fünf Lösungen, die wir oft umsetzen. Jede wird an Ihre Abläufe angepasst, und den Piloten bauen wir kostenlos."
    else:
        title, meta = "Solutions for everyday tasks | devunoxAI", "AI inbox, document extraction, knowledge base, complaint management and field service app: solutions for SMEs, with a free pilot."
        h1, lede = "Solutions for tasks that cost time every day", "Five solutions we build often. Each one is adapted to your processes, and we build the pilot free of charge."
    main = f'<section class="sec"><div class="w sec-in"><div class="post-list">{cards}</div></div></section>' + pilot_path(lang, "../") + cta(lang, 1)
    schema = [{"@context": "https://schema.org", "@type": "CollectionPage", "name": h1, "url": url, "inLanguage": lang, "about": {"@id": ORG},
               "hasPart": [{"@type": "WebPage", "name": s[lang]["name"], "url": f'{url}{s[lang]["slug"]}'} for s in SOLUTIONS]},
              cp.crumb_ld([(c["home"], f"{BASE}/{lang}/"), (c["hub"], url)])]
    return path, cp.page(lang, path, alt, title, meta, h1, lede, [(c["home"], None), (c["hub"], None)], main, schema)

def event_page(lang):
    c = L[lang]
    other = "en" if lang == "de" else "de"
    path, alt = f'{lang}/{c["event"]}', f'{other}/{L[other]["event"]}'
    if lang == "de":
        title, meta = "Schön, Sie kennenzulernen | devunoxAI", "Demos, Terminbuchung und kostenloser Pilot: alles aus unserem Gespräch auf einen Blick."
        h1, lede = "Schön, dass wir uns kennengelernt haben", "Hier finden Sie alles aus unserem Gespräch: Demos zum Ausprobieren, einen Termin für das Erstgespräch und unser Angebot für einen kostenlosen Piloten."
        acts = [("Termin buchen", "30 Minuten per Video, kostenlos", "kontakt.html#termin"),
                ("Kostenlosen Pilot anfragen", "Wir bauen eine erste Version mit Ihren Beispielen", "kontakt.html#contact-form"),
                ("Demos ausprobieren", "Klickbare Anwendungen mit Beispieldaten", "demos.html"),
                ("Kontakt speichern", "Visitenkarte für Ihr Handy", "../assets/devunoxai.vcf")]
        sol_h, sol_k = "Was wir oft bauen", "Lösungen"
    else:
        title, meta = "Nice to meet you | devunoxAI", "Demos, booking and a free pilot: everything from our conversation at a glance."
        h1, lede = "Great to meet you", "Everything from our conversation in one place: demos to try, a slot for an intro call and our offer of a free pilot."
        acts = [("Book a call", "30 minutes by video, free of charge", "contact.html#termin"),
                ("Request a free pilot", "We build a first version with your examples", "contact.html#contact-form"),
                ("Try the demos", "Clickable apps with example data", "demos.html"),
                ("Save our contact", "Business card for your phone", "../assets/devunoxai.vcf")]
        sol_h, sol_k = "What we often build", "Solutions"
    links = "".join(f'<a href="{h}"{" download" if h.endswith(".vcf") else ""}><span class="o-name">{e(n)}</span><span class="o-more">{e(m)}</span>{ROUND}</a>' for n, m, h in acts)
    sols = "".join(f'<a href="{c["dir"]}/{s[lang]["slug"]}.html"><small>{c["sol"]}</small><b>{e(s[lang]["name"])}</b><span>{e(s[lang]["lede"])}</span></a>' for s in SOLUTIONS)
    main = (f'<section class="sec"><div class="w sec-in"><div class="others event-acts">{links}</div></div></section>'
            f'<section class="sec soft"><div class="w sec-in"><div class="sec-head"><p class="kicker">{sol_k}</p><h2>{sol_h}</h2></div><div class="post-list">{sols}</div></div></section>'
            + pilot_path(lang) + cta(lang, 0))
    doc = cp.page(lang, path, alt, title, meta, h1, lede, [(c["home"], None), ("Messe" if lang == "de" else "Event", None)], main, [])
    doc = doc.replace("<head>\n", '<head>\n<meta name="robots" content="noindex, follow"/>\n', 1)
    return path, doc

def cta(lang, depth):
    c = L[lang]
    pre = "../" * depth
    h = "Erzählen Sie uns, was Sie Zeit kostet" if lang == "de" else "Tell us what costs you time"
    return f'<section class="cta"><div class="w cta-in"><h2>{h}</h2><div class="cta-side"><p>{c["cta_p"]}</p>{btn("btn-ink", pre + c["contact"] + "#contact-form", c["pilot_btn"])}</div></div></section>'

def cases_section(lang):
    if not CASES:
        return ""
    c = L[lang]
    a, b, d = c["cases_labels"]
    cards = "".join(f'<article class="case"><p class="kicker">{e(x[lang]["field"])}</p><h3>{e(x[lang]["company"])}</h3>'
                    f'<p><b>{a}:</b> {e(x[lang]["start"])}</p><p><b>{b}:</b> {e(x[lang]["solution"])}</p><p><b>{d}:</b> {e(x[lang]["result"])}</p></article>' for x in CASES)
    return f'<section class="sec soft cases-sec"><div class="w sec-in"><div class="sec-head"><p class="kicker">{c["cases_k"]}</p><h2>{c["cases_h"]}</h2></div><div class="cases">{cards}</div></div></section>\n'

# ----------------------------------------------------------------------------- bestehende Seiten anpassen

CTA_RE = re.compile(r'<div class="cta-side"><p>[^<]*</p><a class="btn btn-ink" href="((?:\.\./)*)(?:kontakt|contact)\.html[^"]*">[^<]*')

def update_existing():
    pages = [p for lang in ("de", "en") for p in (SITE / lang).rglob("*.html")]
    for p in pages:
        lang = p.relative_to(SITE).parts[0]
        c = L[lang]
        s = p.read_text(encoding="utf-8")
        orig = s
        # Pilot-Angebot im Abschluss-CTA jeder Seite
        s = CTA_RE.sub(lambda m: f'<div class="cta-side"><p>{c["cta_p"]}</p><a class="btn btn-ink" href="{m.group(1)}{c["contact"]}#contact-form">{c["pilot_btn"]}', s)
        # Footer: Link zu den Lösungen
        if f'{c["dir"]}/index.html">{c["hub"]}</a>' not in s:
            s = re.sub(r'<a href="((?:\.\./)*)' + re.escape(c["footer_after"]),
                       lambda m: m.group(0) + f'<li><a href="{m.group(1)}{c["dir"]}/index.html">{c["hub"]}</a></li>', s, count=1)
        # Google-Ads-Messung (aktiv erst mit ID in assets/consent.js und nach Einwilligung)
        if "consent.js" not in s:
            s = re.sub(r'(<script src="((?:\.\./)*)assets/main\.js[^"]*"></script>)', r'\1\n<script src="\2assets/consent.js" defer></script>', s, count=1)
        if s != orig:
            p.write_text(s, encoding="utf-8")

def update_home():
    for lang in ("de", "en"):
        c = L[lang]
        p = SITE / lang / "index.html"
        s = p.read_text(encoding="utf-8")
        # Hero: Pilot als Hauptangebot
        s = re.sub(r'(<section class="hero-home">.*?<div class="cta-row"><a class="btn btn-o" href=")[^"]*(">)[^<]*',
                   lambda m: m.group(1) + c["contact"] + "#contact-form" + m.group(2) + c["pilot_btn"], s, count=1, flags=re.S)
        # Abschnitte neu setzen
        s = re.sub(r'<section class="sec pilot-sec".*?</section>\n?', "", s, flags=re.S)
        s = re.sub(r'<section class="sec soft cases-sec">.*?</section>\n?', "", s, flags=re.S)
        i = s.index('id="demos"')
        j = s.index("</section>", i) + len("</section>")
        s = s[:j] + "\n" + pilot_path(lang) + s[j:]
        s = s.replace('<section class="cta">', cases_section(lang) + '<section class="cta">', 1)
        p.write_text(s, encoding="utf-8")

def update_contact():
    for lang, opt in (("de", "Kostenloser Pilot"), ("en", "Free pilot")):
        p = SITE / lang / L[lang]["contact"]
        s = p.read_text(encoding="utf-8")
        if f"<option>{opt}</option>" not in s:
            s = s.replace('<select id="f-topic" name="topic">', f'<select id="f-topic" name="topic"><option>{opt}</option>', 1)
            p.write_text(s, encoding="utf-8")

def build():
    written = []
    for lang in ("de", "en"):
        (SITE / lang / L[lang]["dir"]).mkdir(exist_ok=True)
        for s in SOLUTIONS:
            path, doc = solution_page(lang, s)
            (SITE / path).write_text(doc, encoding="utf-8"); written.append(path)
        path, doc = hub_page(lang)
        (SITE / path).write_text(doc, encoding="utf-8"); written.append(path)
        path, doc = event_page(lang)
        (SITE / path).write_text(doc, encoding="utf-8"); written.append(path)
    update_home()
    update_contact()
    update_existing()
    return written

if __name__ == "__main__":
    print("\n".join(build()))
