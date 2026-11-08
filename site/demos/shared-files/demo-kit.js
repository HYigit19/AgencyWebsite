/*! devunoxAI Demo-Kit: Sprachumschalter (DE/EN), geführte Tour, kleine SVG-Diagramme.
 *
 * Einbinden im <head> VOR dem App-Script (damit Datums-/Zahlenformate in EN greifen):
 *   <link rel="stylesheet" href="shared-files/demo-kit.css">
 *   <script src="shared-files/demo-kit.js"></script>
 * Danach (am Ende der App, wenn die App gestartet ist):
 *   DemoKit.init({ app:'suite', accent:'#6E4AF2', i18n:{dict, rules, words}, tour:{steps, welcome}, langMount:'.selector', tourMount:'.selector' })
 *
 * Sprache: ?lang=en|de  >  localStorage 'dvx-lang'  >  'de'.
 * Übersetzung: DOM-Übersetzer (Textknoten + Attribute) über Wörterbuch/Regeln, nur wenn EN aktiv ist.
 * Elemente mit [data-no-i18n] (und alles darin) werden nicht übersetzt.
 */
(function () {
  'use strict';
  if (window.DemoKit) return;

  // ---------- Sprache ----------
  var LS_LANG = 'dvx-lang';
  function readLang() {
    try {
      var q = new URLSearchParams(location.search).get('lang');
      if (q === 'en' || q === 'de') { try { localStorage.setItem(LS_LANG, q); } catch (e) {} return q; }
      var h = /(?:^|[#&?])lang=(en|de)\b/.exec(location.hash);
      if (h) { try { localStorage.setItem(LS_LANG, h[1]); } catch (e) {} return h[1]; }
      var s = localStorage.getItem(LS_LANG);
      if (s === 'en' || s === 'de') return s;
    } catch (e) {}
    return 'de';
  }
  var LANG = readLang();
  var EN = LANG === 'en';
  document.documentElement.setAttribute('data-dvx-lang', LANG);
  if (EN) document.documentElement.lang = 'en';

  // ---------- Datums- und Zahlenformate in EN ----------
  if (EN) {
    var mapLoc = function (l) {
      var first = Array.isArray(l) ? l[0] : l;
      return (first == null || /^de\b/i.test(String(first))) ? 'en-GB' : l;
    };
    var D = Date.prototype;
    ['toLocaleDateString', 'toLocaleTimeString', 'toLocaleString'].forEach(function (k) {
      var orig = D[k];
      D[k] = function (l, o) { return orig.call(this, mapLoc(l), o); };
    });
    if (!window.DVX_NO_NUMBER_PATCH) {
      var nOrig = Number.prototype.toLocaleString;
      Number.prototype.toLocaleString = function (l, o) { return nOrig.call(this, mapLoc(l), o); };
    }
    var wrapIntl = function (name) {
      var O = Intl[name];
      if (!O) return;
      var W = function (l, o) { return new O(mapLoc(l), o); };
      W.prototype = O.prototype;
      W.supportedLocalesOf = O.supportedLocalesOf;
      Intl[name] = W;
    };
    wrapIntl('DateTimeFormat');
    wrapIntl('RelativeTimeFormat');
    wrapIntl('ListFormat');
    if (!window.DVX_NO_NUMBER_PATCH) wrapIntl('NumberFormat');
  }

  // ---------- Übersetzer ----------
  var dict = Object.create(null);
  var rules = [];      // [RegExp, string|function]
  var wordRe = null, words = Object.create(null);
  var cache = new Map();
  var done = new WeakMap(); // Textknoten -> zuletzt gesetzter Wert
  var ATTRS = ['placeholder', 'title', 'aria-label', 'alt', 'data-tip', 'data-tooltip', 'data-title', 'data-label', 'data-empty'];
  var SKIP = { SCRIPT: 1, STYLE: 1, TEXTAREA: 1, NOSCRIPT: 1, TEMPLATE: 1, svgSTYLE: 1 };
  var LETTER = /[A-Za-zÄÖÜäöüß]/;

  function addI18n(cfg) {
    if (!cfg) return;
    if (cfg.dict) for (var k in cfg.dict) dict[norm(k)] = cfg.dict[k];
    if (cfg.rules) cfg.rules.forEach(function (r) { rules.push(r); });
    if (cfg.words) {
      for (var w in cfg.words) words[w] = cfg.words[w];
      var keys = Object.keys(words).sort(function (a, b) { return b.length - a.length; })
        .map(function (x) { return x.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'); });
      wordRe = keys.length ? new RegExp('(^|[^A-Za-zÄÖÜäöüß0-9])(' + keys.join('|') + ')(?=$|[^A-Za-zÄÖÜäöüß0-9])', 'g') : null;
    }
    if (cfg.attrs) cfg.attrs.forEach(function (a) { if (ATTRS.indexOf(a) < 0) ATTRS.push(a); });
    cache.clear();
    done = new WeakMap(); // neue Einträge: bereits gesehene Knoten erneut prüfen
  }
  function norm(s) { return String(s).replace(/\s+/g, ' ').trim(); }

  function trCore(core) {
    if (cache.has(core)) return cache.get(core);
    var r = dict[core];
    if (r == null) {
      var out = core;
      for (var i = 0; i < rules.length; i++) {
        var re = rules[i][0];
        re.lastIndex = 0;
        if (re.test(out)) { re.lastIndex = 0; out = out.replace(re, rules[i][1]); }
      }
      if (out !== core && dict[norm(out)] != null) out = dict[norm(out)];
      if (wordRe) out = out.replace(wordRe, function (m, pre, w) { return pre + words[w]; });
      r = out;
    }
    if (cache.size > 20000) cache.clear();
    cache.set(core, r);
    return r;
  }
  function tr(s) {
    if (!EN || s == null) return s;
    s = String(s);
    if (!LETTER.test(s)) return s;
    var m = /^(\s*)([\s\S]*?)(\s*)$/.exec(s);
    var core = norm(m[2]);
    if (!core) return s;
    var r = trCore(core);
    return r === core ? s : m[1] + r + m[3];
  }

  function skipEl(el) {
    for (var e = el; e && e.nodeType === 1; e = e.parentNode) {
      if (SKIP[e.nodeName] || SKIP[e.tagName]) return true;
      if (e.hasAttribute('data-no-i18n') || e.isContentEditable) return true;
    }
    return false;
  }
  function doText(n) {
    if (done.get(n) === n.data) return;
    var p = n.parentNode;
    if (!p || skipEl(p)) return;
    var t = tr(n.data);
    if (t !== n.data) n.data = t;
    done.set(n, n.data);
  }
  function doAttrs(el) {
    for (var i = 0; i < ATTRS.length; i++) {
      var a = ATTRS[i];
      if (el.hasAttribute && el.hasAttribute(a)) {
        var v = el.getAttribute(a), t = tr(v);
        if (t !== v) el.setAttribute(a, t);
      }
    }
    if (el.tagName === 'INPUT' && /^(button|submit|reset)$/i.test(el.type) && el.value) {
      var tv = tr(el.value); if (tv !== el.value) el.value = tv;
    }
  }
  function walk(root) {
    if (!root) return;
    if (root.nodeType === 3) { doText(root); return; }
    if (root.nodeType !== 1 && root.nodeType !== 9 && root.nodeType !== 11) return;
    if (root.nodeType === 1) { if (skipEl(root)) return; doAttrs(root); }
    var w = document.createTreeWalker(root, NodeFilter.SHOW_ELEMENT | NodeFilter.SHOW_TEXT, {
      acceptNode: function (n) {
        if (n.nodeType === 1) {
          if (SKIP[n.nodeName] || n.hasAttribute('data-no-i18n') || n.isContentEditable) return NodeFilter.FILTER_REJECT;
          return NodeFilter.FILTER_ACCEPT;
        }
        return NodeFilter.FILTER_ACCEPT;
      }
    });
    var n;
    while ((n = w.nextNode())) { if (n.nodeType === 3) doText(n); else doAttrs(n); }
  }
  var observer = null;
  function startObserver() {
    if (!EN || observer) return;
    observer = new MutationObserver(function (list) {
      for (var i = 0; i < list.length; i++) {
        var m = list[i];
        if (m.type === 'childList') {
          for (var j = 0; j < m.addedNodes.length; j++) walk(m.addedNodes[j]);
        } else if (m.type === 'characterData') {
          doText(m.target);
        } else if (m.type === 'attributes') {
          var el = m.target, a = m.attributeName;
          if (el.nodeType === 1 && !skipEl(el)) {
            var v = el.getAttribute(a), t = tr(v);
            if (v != null && t !== v) el.setAttribute(a, t);
          }
        }
      }
      ensureMounts();
    });
    observer.observe(document.documentElement, { childList: true, subtree: true, characterData: true, attributes: true, attributeFilter: ATTRS.slice() });
    walk(document.documentElement);
  }
  if (EN) {
    startObserver();
    var wrapDlg = function (k) {
      var o = window[k];
      window[k] = function (msg, def) { return o.call(window, tr(msg), def); };
    };
    wrapDlg('alert'); wrapDlg('confirm'); wrapDlg('prompt');
  }

  function setLang(l) {
    if (l === LANG) return;
    try { localStorage.setItem(LS_LANG, l); } catch (e) {}
    var u = new URL(location.href);
    u.searchParams.set('lang', l);
    u.hash = u.hash.replace(/([#&?])lang=(en|de)&?/, '$1').replace(/[&?]$/, '');
    location.replace(u.toString());
  }

  // ---------- Hilfen ----------
  function T(x) { return x == null ? '' : (typeof x === 'object' ? (x[LANG] != null ? x[LANG] : x.de) : x); }
  function h(tag, attrs, html) {
    var e = document.createElement(tag);
    if (attrs) for (var k in attrs) { if (k === 'class') e.className = attrs[k]; else e.setAttribute(k, attrs[k]); }
    if (html != null) e.innerHTML = html;
    return e;
  }
  function $(sel) { try { return typeof sel === 'function' ? sel() : document.querySelector(sel); } catch (e) { return null; } }
  function visible(el) {
    if (!el || !el.isConnected) return false;
    var r = el.getBoundingClientRect();
    if (r.width < 2 || r.height < 2) return false;
    var cs = getComputedStyle(el);
    return cs.visibility !== 'hidden' && cs.display !== 'none' && +cs.opacity !== 0;
  }
  function sleep(ms) { return new Promise(function (r) { setTimeout(r, ms); }); }
  function isMobile() { return window.innerWidth < 700; }

  var ICON = {
    globe: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="9"/><path d="M3 12h18M12 3a14 14 0 0 1 0 18M12 3a14 14 0 0 0 0 18"/></svg>',
    play: '<svg viewBox="0 0 24 24" fill="currentColor"><path d="M8 5.5v13a1 1 0 0 0 1.5.86l10.5-6.5a1 1 0 0 0 0-1.72L9.5 4.64A1 1 0 0 0 8 5.5z"/></svg>',
    spark: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 3l1.9 5.1L19 10l-5.1 1.9L12 17l-1.9-5.1L5 10l5.1-1.9z"/><path d="M19 15l.8 2.2L22 18l-2.2.8L19 21l-.8-2.2L16 18l2.2-.8z"/></svg>',
    tap: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M9 11V5.5a1.5 1.5 0 0 1 3 0V11m0-1.5a1.5 1.5 0 0 1 3 0V12m0-1a1.5 1.5 0 0 1 3 0v4a6 6 0 0 1-6 6h-1a6 6 0 0 1-4.8-2.4L4.6 15.2a1.6 1.6 0 0 1 2.5-2L9 15"/></svg>',
    close: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round"><path d="M6 6l12 12M18 6L6 18"/></svg>',
    cal: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="5" width="18" height="16" rx="3"/><path d="M8 3v4M16 3v4M3 10h18"/></svg>',
    check: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12.5l4.5 4.5L19 7.5"/></svg>'
  };
  var UI = {
    de: { tour: 'Geführte Tour', start: 'Tour starten', explore: 'Selbst erkunden', next: 'Weiter', back: 'Zurück', skip: 'Überspringen', finish: 'Fertig', step: 'Schritt', of: 'von', tapHint: 'Klicken Sie auf das markierte Element oder auf „Weiter“.', min: 'ca. 2 Minuten', doneTitle: 'Geschafft!', doneText: 'Sie kennen jetzt die wichtigsten Funktionen. Probieren Sie die Demo in Ruhe selbst aus. Alle Daten sind Beispieldaten und bleiben in Ihrem Browser.', tryIt: 'Selbst ausprobieren', book: 'Termin vereinbaren', restart: 'Tour neu starten', lang: 'Sprache', demoBadge: 'Interaktive Demo' },
    en: { tour: 'Guided tour', start: 'Start tour', explore: 'Explore on my own', next: 'Next', back: 'Back', skip: 'Skip', finish: 'Done', step: 'Step', of: 'of', tapHint: 'Click the highlighted element or press “Next”.', min: 'about 2 minutes', doneTitle: 'All set!', doneText: 'You now know the key features. Take your time and try the demo yourself. All data is sample data and stays in your browser.', tryIt: 'Try it myself', book: 'Book a call', restart: 'Restart tour', lang: 'Language', demoBadge: 'Interactive demo' }
  };
  function U(k) { return UI[LANG][k]; }
  var BOOK_URL = 'https://calendar.app.google/LaF7ox8DKMVbsdeU9';

  // ---------- Montage von Sprachumschalter und Tour-Knopf ----------
  var CFG = { app: 'demo' };
  var langEl = null, tourBtn = null;
  function makeLang(extra) {
    var e = h('div', { class: 'dvx-lang' + (extra ? ' ' + extra : ''), role: 'group', 'aria-label': U('lang'), 'data-no-i18n': '' },
      '<button type="button" data-l="de" aria-pressed="' + (!EN) + '">DE</button><button type="button" data-l="en" aria-pressed="' + EN + '">EN</button>');
    e.addEventListener('click', function (ev) {
      var b = ev.target.closest('button[data-l]');
      if (b) { ev.preventDefault(); ev.stopPropagation(); setLang(b.getAttribute('data-l')); }
    });
    return e;
  }
  function makeTourBtn(extra) {
    var b = h('button', { type: 'button', class: 'dvx-tourbtn' + (extra ? ' ' + extra : ''), 'data-no-i18n': '', 'aria-label': U('tour') },
      '<span class="dvx-tourbtn-i">' + ICON.play + '</span><span class="dvx-tourbtn-t">' + U('tour') + '</span>');
    b.addEventListener('click', function (ev) { ev.preventDefault(); ev.stopPropagation(); Tour.start(0); });
    return b;
  }
  function mountInto(el, sel, fallbackClass) {
    var host = sel ? $(sel) : null;
    if (host) {
      el.classList.remove(fallbackClass);
      if (el.parentNode !== host) {
        if (CFG.mountPrepend) host.insertBefore(el, host.firstChild); else host.appendChild(el);
      }
    } else if (!el.isConnected || (el.parentNode !== document.body)) {
      el.classList.add(fallbackClass);
      document.body.appendChild(el);
    }
  }
  var mounting = false;
  function ensureMounts() {
    if (mounting || !document.body || !CFG._inited) return;
    mounting = true;
    try {
      if (CFG.langMount !== false) {
        if (!langEl) langEl = makeLang();
        var lh = CFG.langMount ? $(CFG.langMount) : null;
        if (lh ? langEl.parentNode !== lh : !langEl.isConnected) mountInto(langEl, CFG.langMount, 'dvx-float-lang');
      }
      if (CFG.tourMount !== false && CFG.tour && CFG.tour.steps && CFG.tour.steps.length) {
        if (!tourBtn) tourBtn = makeTourBtn();
        var th = CFG.tourMount ? $(CFG.tourMount) : null;
        if (th ? tourBtn.parentNode !== th : !tourBtn.isConnected) mountInto(tourBtn, CFG.tourMount, 'dvx-float-tour');
      }
    } finally { mounting = false; }
  }

  // ---------- Geführte Tour ----------
  var Tour = (function () {
    var steps = [], idx = -1, active = false, root, hole, pop, blockers = [], raf = 0, lastRect = '', curEl = null, clickHandler = null, token = 0;

    function build() {
      root = h('div', { class: 'dvx-tour', 'data-no-i18n': '' });
      for (var i = 0; i < 5; i++) { var b = h('div', { class: 'dvx-tour-block' }); b.addEventListener('click', nudge); blockers.push(b); root.appendChild(b); }
      hole = h('div', { class: 'dvx-tour-hole' });
      pop = h('div', { class: 'dvx-tour-pop', role: 'dialog', 'aria-modal': 'true', 'aria-live': 'polite' });
      root.appendChild(hole); root.appendChild(pop);
      document.body.appendChild(root);
    }
    function nudge() { if (!pop) return; pop.classList.remove('dvx-nudge'); void pop.offsetWidth; pop.classList.add('dvx-nudge'); }
    function keys(e) {
      if (!active) return;
      if (e.key === 'Escape') { e.preventDefault(); end(true); }
      else if (e.key === 'ArrowRight' || e.key === 'Enter') { if (e.target && /INPUT|TEXTAREA|SELECT/.test(e.target.tagName)) return; e.preventDefault(); next(); }
      else if (e.key === 'ArrowLeft') { e.preventDefault(); prev(); }
    }
    function start(i) {
      steps = (CFG.tour && CFG.tour.steps) || [];
      if (!steps.length) return;
      closeWelcome();
      if (!root) build();
      active = true;
      document.documentElement.classList.add('dvx-tour-on');
      root.style.display = '';
      document.addEventListener('keydown', keys, true);
      if (CFG.tour.onStart) try { CFG.tour.onStart(); } catch (e) { console.warn(e); }
      go(i || 0);
      loop();
    }
    function loop() {
      cancelAnimationFrame(raf);
      var tick = function () { if (!active) return; place(false); raf = requestAnimationFrame(tick); };
      raf = requestAnimationFrame(tick);
    }
    function findEl(st) {
      var sel = (isMobile() && st.mobileEl) ? st.mobileEl : st.el;
      if (!sel) return null;
      var list = Array.isArray(sel) ? sel : [sel];
      for (var i = 0; i < list.length; i++) { var e = $(list[i]); if (visible(e)) return e; }
      return null;
    }
    async function go(i) {
      if (i < 0) i = 0;
      if (i >= steps.length) { finish(); return; }
      var my = ++token;
      idx = i;
      var st = steps[i];
      detachClick();
      curEl = null;
      root.classList.add('dvx-busy');
      pop.classList.add('dvx-hide');
      if (st.before) { try { await st.before(); } catch (e) { console.warn('[DemoKit] before()', e); } }
      if (my !== token) return;
      var el = null;
      if (st.el || st.mobileEl) {
        var t0 = Date.now(), maxWait = st.wait != null ? st.wait : 3000;
        while (!(el = findEl(st)) && Date.now() - t0 < maxWait) { await sleep(80); if (my !== token) return; }
        if (el) {
          var r = el.getBoundingClientRect();
          var vh = window.innerHeight, vw = window.innerWidth;
          var popRoom = isMobile() ? Math.min(vh * 0.46, 330) : 0;
          if (r.top < 8 || r.bottom > vh - popRoom - 8 || r.left < 0 || r.right > vw) {
            try { el.scrollIntoView({ block: isMobile() ? 'start' : 'center', inline: 'nearest', behavior: 'auto' }); } catch (e) { el.scrollIntoView(); }
            if (isMobile()) window.scrollBy(0, -12);
            await sleep(60);
          }
        }
      }
      if (my !== token) return;
      curEl = el;
      render(st, el);
      root.classList.remove('dvx-busy');
      lastRect = '';
      place(true);
      pop.classList.remove('dvx-hide');
      if (el && st.click) attachClick(el, st);
      if (st.after) { try { st.after(el); } catch (e) {} }
      var focusBtn = pop.querySelector('.dvx-next');
      if (focusBtn && !isMobile()) try { focusBtn.focus({ preventScroll: true }); } catch (e) {}
    }
    function render(st, el) {
      var n = steps.length;
      var pct = Math.round(((idx + 1) / n) * 100);
      var last = idx === n - 1;
      var interactive = !!(el && st.click);
      pop.className = 'dvx-tour-pop' + (el ? '' : ' dvx-center') + (isMobile() ? ' dvx-sheet' : '');
      pop.innerHTML =
        '<div class="dvx-tour-top"><span class="dvx-tour-badge">' + ICON.spark + U('tour') + '</span>' +
        '<span class="dvx-tour-count">' + U('step') + ' ' + (idx + 1) + ' ' + U('of') + ' ' + n + '</span>' +
        '<button type="button" class="dvx-tour-x" aria-label="' + U('skip') + '">' + ICON.close + '</button></div>' +
        '<div class="dvx-tour-bar"><i style="width:' + pct + '%"></i></div>' +
        '<h3 class="dvx-tour-h">' + T(st.title) + '</h3>' +
        '<div class="dvx-tour-p">' + T(st.text) + '</div>' +
        (interactive ? '<div class="dvx-tour-tap">' + ICON.tap + '<span>' + (T(st.hint) || U('tapHint')) + '</span></div>' : '') +
        '<div class="dvx-tour-actions"><button type="button" class="dvx-skip">' + U('skip') + '</button><span class="dvx-sp"></span>' +
        (idx > 0 ? '<button type="button" class="dvx-back">' + U('back') + '</button>' : '') +
        '<button type="button" class="dvx-next">' + (last ? U('finish') : U('next')) + '</button></div>';
      pop.querySelector('.dvx-tour-x').onclick = function () { end(true); };
      pop.querySelector('.dvx-skip').onclick = function () { end(true); };
      var b = pop.querySelector('.dvx-back'); if (b) b.onclick = prev;
      pop.querySelector('.dvx-next').onclick = next;
      // Klickbarkeit: interaktive Schritte lassen Klicks auf das Ziel durch
      blockers[4].style.display = interactive ? 'none' : '';
      hole.classList.toggle('dvx-pulse', interactive);
    }
    function place(force) {
      if (!active || !root) return;
      var vw = window.innerWidth, vh = window.innerHeight;
      var st = steps[idx] || {};
      var pad = st.padding != null ? st.padding : 6;
      var r = null;
      if (curEl && curEl.isConnected) {
        var b = curEl.getBoundingClientRect();
        if (b.width > 1 && b.height > 1) r = { x: Math.max(4, b.left - pad), y: Math.max(4, b.top - pad), r: Math.min(vw - 4, b.right + pad), b: Math.min(vh - 4, b.bottom + pad) };
      } else if (curEl && !curEl.isConnected) {
        // Ziel wurde neu gerendert: neu suchen
        var ne = findEl(st); if (ne) { curEl = ne; if (st.click) attachClick(ne, st); return place(true); }
      }
      var key = r ? [r.x, r.y, r.r, r.b, vw, vh].map(Math.round).join(',') : 'none' + vw + 'x' + vh;
      if (!force && key === lastRect) return;
      lastRect = key;
      if (r) {
        hole.style.display = '';
        hole.style.transform = 'translate(' + r.x + 'px,' + r.y + 'px)';
        hole.style.width = (r.r - r.x) + 'px'; hole.style.height = (r.b - r.y) + 'px';
        setBlock(0, 0, 0, vw, r.y); setBlock(1, 0, r.b, vw, vh - r.b);
        setBlock(2, 0, r.y, r.x, r.b - r.y); setBlock(3, r.r, r.y, vw - r.r, r.b - r.y);
        setBlock(4, r.x, r.y, r.r - r.x, r.b - r.y);
        root.classList.remove('dvx-dim');
      } else {
        hole.style.display = 'none';
        setBlock(0, 0, 0, vw, vh); for (var i = 1; i < 5; i++) setBlock(i, 0, 0, 0, 0);
        root.classList.add('dvx-dim');
      }
      placePop(r, vw, vh, st);
    }
    function setBlock(i, x, y, w, hh) { var s = blockers[i].style; s.transform = 'translate(' + x + 'px,' + y + 'px)'; s.width = Math.max(0, w) + 'px'; s.height = Math.max(0, hh) + 'px'; }
    function placePop(r, vw, vh, st) {
      if (isMobile()) { pop.style.transform = ''; pop.style.left = ''; pop.style.top = ''; return; }
      var pw = pop.offsetWidth, ph = pop.offsetHeight, m = 14, x, y;
      if (!r) { x = (vw - pw) / 2; y = (vh - ph) / 2; }
      else {
        var space = { right: vw - r.r, left: r.x, bottom: vh - r.b, top: r.y };
        var order = st.placement && st.placement !== 'auto' ? [st.placement, 'right', 'bottom', 'left', 'top'] : ['right', 'bottom', 'left', 'top'];
        var side = 'center';
        for (var i = 0; i < order.length; i++) {
          var s = order[i];
          if ((s === 'right' || s === 'left') && space[s] >= pw + m * 2) { side = s; break; }
          if ((s === 'top' || s === 'bottom') && space[s] >= ph + m * 2) { side = s; break; }
        }
        var cx = (r.x + r.r) / 2, cy = (r.y + r.b) / 2;
        if (side === 'right') { x = r.r + m; y = cy - ph / 2; }
        else if (side === 'left') { x = r.x - m - pw; y = cy - ph / 2; }
        else if (side === 'bottom') { x = cx - pw / 2; y = r.b + m; }
        else if (side === 'top') { x = cx - pw / 2; y = r.y - m - ph; }
        else { x = vw - pw - 24; y = vh - ph - 24; }
      }
      x = Math.max(12, Math.min(vw - pw - 12, x)); y = Math.max(12, Math.min(vh - ph - 12, y));
      pop.style.left = '0px'; pop.style.top = '0px';
      pop.style.transform = 'translate(' + Math.round(x) + 'px,' + Math.round(y) + 'px)';
    }
    function attachClick(el, st) {
      detachClick();
      var myIdx = idx;
      clickHandler = function (e) {
        if (!active || idx !== myIdx) return;
        if (curEl && (curEl === e.target || curEl.contains(e.target))) {
          detachClick();
          setTimeout(function () { if (active && idx === myIdx) go(idx + 1); }, st.delay != null ? st.delay : 450);
        }
      };
      document.addEventListener('click', clickHandler, true);
    }
    function detachClick() { if (clickHandler) document.removeEventListener('click', clickHandler, true); clickHandler = null; }
    function next() {
      var st = steps[idx];
      if (st && st.click && curEl) {
        // "Weiter" klickt für den Nutzer
        var el = curEl, myIdx = idx;
        detachClick();
        try { if (typeof st.click === 'function') st.click(el); else el.click(); } catch (e) { console.warn(e); }
        setTimeout(function () { if (active && idx === myIdx) go(idx + 1); }, st.delay != null ? st.delay : 450);
        return;
      }
      go(idx + 1);
    }
    function prev() {
      if (idx <= 0) return;
      var st = steps[idx - 1];
      go(idx - 1);
    }
    function finish() {
      var cfg = CFG.tour || {};
      end(false);
      if (cfg.end === false) return;
      showCard({
        icon: ICON.check, title: T(cfg.endTitle) || U('doneTitle'), text: T(cfg.endText) || U('doneText'),
        primary: U('tryIt'), secondary: cfg.cta === false ? null : U('book'),
        onPrimary: function () { closeWelcome(); },
        onSecondary: function () { window.open(BOOK_URL, '_blank', 'noopener'); },
        cls: 'dvx-done'
      });
    }
    function end(skipped) {
      active = false; token++;
      detachClick();
      cancelAnimationFrame(raf);
      document.removeEventListener('keydown', keys, true);
      document.documentElement.classList.remove('dvx-tour-on');
      if (root) root.style.display = 'none';
      markTour(skipped ? 'skipped' : 'done');
      var cfg = CFG.tour || {};
      if (cfg.onEnd) try { cfg.onEnd(skipped); } catch (e) { console.warn(e); }
    }
    return { start: start, end: end, next: next, prev: prev, get active() { return active; }, get index() { return idx; } };
  })();

  // Tour-Status: abgeschlossen = dauerhaft; übersprungen = nur für diesen Tab,
  // damit die Willkommenskarte beim nächsten Besuch wieder angeboten wird.
  function markTour(v) {
    var k = 'dvx-tour:' + CFG.app;
    try { if (v === 'done') localStorage.setItem(k, 'done'); else sessionStorage.setItem(k, v); } catch (e) {}
  }
  function tourSeen() {
    var k = 'dvx-tour:' + CFG.app;
    try { if (localStorage.getItem(k) === 'done') return 'done'; return sessionStorage.getItem(k); } catch (e) { return null; }
  }

  // ---------- Willkommens-/Abschlusskarte ----------
  var cardEl = null;
  function closeWelcome() { if (cardEl) { cardEl.remove(); cardEl = null; } }
  function showCard(o) {
    closeWelcome();
    cardEl = h('div', { class: 'dvx-modal ' + (o.cls || ''), 'data-no-i18n': '', role: 'dialog', 'aria-modal': 'true' });
    cardEl.innerHTML = '<div class="dvx-modal-card">' +
      '<div class="dvx-modal-art"><div class="dvx-modal-icon">' + o.icon + '</div>' + (o.badge ? '<span class="dvx-modal-badge">' + o.badge + '</span>' : '') + '</div>' +
      '<div class="dvx-modal-body"><h2>' + o.title + '</h2><div class="dvx-modal-text">' + o.text + '</div>' +
      (o.meta ? '<div class="dvx-modal-meta">' + o.meta + '</div>' : '') +
      '<div class="dvx-modal-actions">' + (o.secondary ? '<button type="button" class="dvx-btn-ghost dvx-m2">' + (o.secondaryIcon || '') + o.secondary + '</button>' : '') +
      '<button type="button" class="dvx-btn-primary dvx-m1">' + (o.primaryIcon || '') + o.primary + '</button></div>' +
      (o.foot ? '<div class="dvx-modal-foot">' + o.foot + '</div>' : '') + '</div></div>';
    document.body.appendChild(cardEl);
    cardEl.querySelector('.dvx-m1').onclick = function () { var f = o.onPrimary; closeWelcome(); if (f) f(); };
    var s = cardEl.querySelector('.dvx-m2'); if (s) s.onclick = function () { var f = o.onSecondary; if (o.closeOnSecondary !== false) closeWelcome(); if (f) f(); };
    cardEl.addEventListener('click', function (e) { if (e.target === cardEl) { var f = o.onDismiss; closeWelcome(); if (f) f(); } });
    var k = function (e) { if (e.key === 'Escape' && cardEl) { document.removeEventListener('keydown', k); var f = o.onDismiss; closeWelcome(); if (f) f(); } };
    document.addEventListener('keydown', k);
    setTimeout(function () { var p = cardEl && cardEl.querySelector('.dvx-m1'); if (p) try { p.focus({ preventScroll: true }); } catch (e) {} }, 30);
  }
  function welcome() {
    var w = (CFG.tour && CFG.tour.welcome) || {};
    showCard({
      icon: w.icon || ICON.spark,
      badge: U('demoBadge'),
      title: T(w.title) || U('tour'),
      text: T(w.text) || '',
      meta: '<span>' + ICON.play + U('min') + '</span>' + (w.meta ? '<span>' + T(w.meta) + '</span>' : ''),
      primary: U('start'), primaryIcon: ICON.play,
      secondary: U('explore'),
      foot: '',
      onPrimary: function () { Tour.start(0); },
      onSecondary: function () { markTour('skipped'); },
      onDismiss: function () { markTour('skipped'); },
      cls: 'dvx-welcome'
    });
  }

  // ---------- Diagramme (SVG-Strings) ----------
  var esc = function (s) { return String(s).replace(/[&<>"]/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]; }); };
  var Charts = {
    /** Balkendiagramm: {labels:[], series:[{name, values:[], color}], height:220, max, unit:'', grid:4} */
    bars: function (o) {
      var W = 640, H = o.height || 220, padL = 40, padB = 28, padT = 10, padR = 8;
      var series = o.series || [], labels = o.labels || [], n = labels.length || (series[0] ? series[0].values.length : 0);
      var max = o.max || Math.max.apply(null, [1].concat.apply([], series.map(function (s) { return s.values; })));
      var g0 = o.grid || 4;
      if (!o.max) { var raw = max / g0, mag = Math.pow(10, Math.floor(Math.log10(raw))), f = raw / mag;
        var step = (f <= 1 ? 1 : f <= 2 ? 2 : f <= 2.5 ? 2.5 : f <= 5 ? 5 : 10) * mag; if (step < 1 && !o.fmt) step = 1; max = step * g0; }
      var gw = (W - padL - padR) / Math.max(1, n), bw = Math.min(18, (gw * 0.7) / Math.max(1, series.length));
      var out = '<svg class="dvx-chart dvx-bars" viewBox="0 0 ' + W + ' ' + H + '" role="img" aria-label="' + esc(o.label || '') + '">';
      var g = o.grid || 4;
      for (var i = 0; i <= g; i++) {
        var y = padT + (H - padT - padB) * (i / g), v = max * (1 - i / g);
        out += '<line x1="' + padL + '" x2="' + (W - padR) + '" y1="' + y + '" y2="' + y + '" class="dvx-grid"/>';
        out += '<text x="' + (padL - 8) + '" y="' + (y + 4) + '" text-anchor="end" class="dvx-axis">' + esc((o.fmt ? o.fmt(v) : Math.round(v)) + (o.unit || '')) + '</text>';
      }
      for (var j = 0; j < n; j++) {
        var gx = padL + gw * j + (gw - bw * series.length - 4 * (series.length - 1)) / 2;
        series.forEach(function (s, k) {
          var v = s.values[j] || 0, bh = (H - padT - padB) * (v / max), x = gx + k * (bw + 4), y = H - padB - bh;
          out += '<rect x="' + x.toFixed(1) + '" y="' + y.toFixed(1) + '" width="' + bw.toFixed(1) + '" height="' + Math.max(0, bh).toFixed(1) + '" rx="' + Math.min(6, bw / 2) + '" fill="' + (s.color || 'var(--dvx-accent)') + '"><title>' + esc((s.name ? s.name + ': ' : '') + (o.fmt ? o.fmt(v) : v) + (o.unit || '')) + '</title></rect>';
        });
        if (labels[j] != null) out += '<text x="' + (padL + gw * j + gw / 2) + '" y="' + (H - 8) + '" text-anchor="middle" class="dvx-axis">' + esc(labels[j]) + '</text>';
      }
      return out + '</svg>';
    },
    /** Fortschrittsring: ring(72, {color, size:96, stroke:10, label:'72 %', sub:''}) */
    ring: function (pct, o) {
      o = o || {}; var s = o.size || 96, sw = o.stroke || 10, r = (s - sw) / 2, c = 2 * Math.PI * r, p = Math.max(0, Math.min(100, pct));
      return '<svg class="dvx-chart dvx-ring" width="' + s + '" height="' + s + '" viewBox="0 0 ' + s + ' ' + s + '" role="img" aria-label="' + p + '%">' +
        '<circle cx="' + s / 2 + '" cy="' + s / 2 + '" r="' + r + '" fill="none" stroke="' + (o.track || 'rgba(120,130,160,.16)') + '" stroke-width="' + sw + '"/>' +
        '<circle cx="' + s / 2 + '" cy="' + s / 2 + '" r="' + r + '" fill="none" stroke="' + (o.color || 'var(--dvx-accent)') + '" stroke-width="' + sw + '" stroke-linecap="round" stroke-dasharray="' + (c * p / 100).toFixed(2) + ' ' + c.toFixed(2) + '" transform="rotate(-90 ' + s / 2 + ' ' + s / 2 + ')"/>' +
        '<text x="50%" y="' + (o.sub ? '47%' : '50%') + '" dominant-baseline="middle" text-anchor="middle" class="dvx-ring-v" style="font-size:' + Math.round(s * 0.22) + 'px">' + esc(o.label != null ? o.label : Math.round(p) + '%') + '</text>' +
        (o.sub ? '<text x="50%" y="66%" dominant-baseline="middle" text-anchor="middle" class="dvx-ring-s" style="font-size:' + Math.round(s * 0.11) + 'px">' + esc(o.sub) + '</text>' : '') + '</svg>';
    },
    /** Tacho (Halbkreis mit Nadel): gauge(45, {size:180, colors:['#22C55E','#F5B82E','#EF4444'], label:'45 %'}) */
    gauge: function (pct, o) {
      o = o || {}; var w = o.size || 180, hh = w * (o.label != null ? 0.74 : 0.6), cx = w / 2, cy = w * 0.52, r = w * 0.4, sw = w * 0.1;
      var cols = o.colors || ['#22C55E', '#F5B82E', '#EF4444'], p = Math.max(0, Math.min(100, pct));
      var arc = function (a0, a1) {
        var p0 = [cx + r * Math.cos(Math.PI * (1 - a0)), cy - r * Math.sin(Math.PI * (1 - a0))], p1 = [cx + r * Math.cos(Math.PI * (1 - a1)), cy - r * Math.sin(Math.PI * (1 - a1))];
        return 'M' + p0[0].toFixed(1) + ' ' + p0[1].toFixed(1) + ' A' + r + ' ' + r + ' 0 0 1 ' + p1[0].toFixed(1) + ' ' + p1[1].toFixed(1);
      };
      var seg = 1 / cols.length, out = '<svg class="dvx-chart dvx-gauge" width="' + w + '" height="' + hh + '" viewBox="0 0 ' + w + ' ' + hh + '" role="img" aria-label="' + p + '%">';
      cols.forEach(function (c, i) { out += '<path d="' + arc(i * seg + 0.005, (i + 1) * seg - 0.005) + '" stroke="' + c + '" stroke-width="' + sw + '" fill="none" stroke-linecap="butt"/>'; });
      var a = Math.PI * (1 - p / 100), nx = cx + (r - sw * 0.2) * Math.cos(a), ny = cy - (r - sw * 0.2) * Math.sin(a);
      out += '<line x1="' + cx + '" y1="' + cy + '" x2="' + nx.toFixed(1) + '" y2="' + ny.toFixed(1) + '" stroke="var(--dvx-ink,#1F2433)" stroke-width="' + (w * 0.025) + '" stroke-linecap="round"/><circle cx="' + cx + '" cy="' + cy + '" r="' + (w * 0.04) + '" fill="var(--dvx-ink,#1F2433)"/>';
      if (o.label != null) out += '<text x="' + cx + '" y="' + (hh - 2) + '" text-anchor="middle" class="dvx-ring-v" style="font-size:' + Math.round(w * 0.09) + 'px">' + esc(o.label) + '</text>';
      return out + '</svg>';
    },
    /** Sparkline: spark([3,5,4,8], {color, w:120, h:36, fill:true}) */
    spark: function (vals, o) {
      o = o || {}; var w = o.w || 120, hh = o.h || 36, n = vals.length; if (n < 2) return '';
      var mn = Math.min.apply(null, vals), mx = Math.max.apply(null, vals), rg = mx - mn || 1;
      var pts = vals.map(function (v, i) { return [(i / (n - 1)) * (w - 4) + 2, hh - 3 - ((v - mn) / rg) * (hh - 8)]; });
      var d = pts.map(function (p, i) { return (i ? 'L' : 'M') + p[0].toFixed(1) + ' ' + p[1].toFixed(1); }).join(' ');
      var c = o.color || 'var(--dvx-accent)', id = 'sg' + Math.random().toString(36).slice(2, 8);
      return '<svg class="dvx-chart dvx-spark" width="' + w + '" height="' + hh + '" viewBox="0 0 ' + w + ' ' + hh + '" aria-hidden="true">' +
        (o.fill !== false ? '<defs><linearGradient id="' + id + '" x1="0" x2="0" y1="0" y2="1"><stop offset="0" stop-color="' + c + '" stop-opacity=".28"/><stop offset="1" stop-color="' + c + '" stop-opacity="0"/></linearGradient></defs><path d="' + d + ' L' + (w - 2) + ' ' + hh + ' L2 ' + hh + 'Z" fill="url(#' + id + ')"/>' : '') +
        '<path d="' + d + '" fill="none" stroke="' + c + '" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"/>' +
        '<circle cx="' + pts[n - 1][0].toFixed(1) + '" cy="' + pts[n - 1][1].toFixed(1) + '" r="3" fill="' + c + '"/></svg>';
    },
    /** Mehrteiliger Donut: donut([{value, color, label}], {size:120, stroke:16, center:'12', sub:'gesamt'}) */
    donut: function (segs, o) {
      o = o || {}; var s = o.size || 120, sw = o.stroke || 16, r = (s - sw) / 2, c = 2 * Math.PI * r, tot = segs.reduce(function (a, b) { return a + (b.value || 0); }, 0) || 1, off = 0;
      var out = '<svg class="dvx-chart dvx-donut" width="' + s + '" height="' + s + '" viewBox="0 0 ' + s + ' ' + s + '" role="img"><circle cx="' + s / 2 + '" cy="' + s / 2 + '" r="' + r + '" fill="none" stroke="rgba(120,130,160,.14)" stroke-width="' + sw + '"/>';
      segs.forEach(function (g) {
        var len = c * (g.value || 0) / tot, gap = segs.length > 1 ? Math.min(3, len / 3) : 0;
        out += '<circle cx="' + s / 2 + '" cy="' + s / 2 + '" r="' + r + '" fill="none" stroke="' + g.color + '" stroke-width="' + sw + '" stroke-dasharray="' + Math.max(0, len - gap).toFixed(2) + ' ' + c.toFixed(2) + '" stroke-dashoffset="' + (-off).toFixed(2) + '" transform="rotate(-90 ' + s / 2 + ' ' + s / 2 + ')"><title>' + esc((g.label || '') + ' ' + g.value) + '</title></circle>';
        off += len;
      });
      if (o.center != null) out += '<text x="50%" y="' + (o.sub ? '46%' : '50%') + '" dominant-baseline="middle" text-anchor="middle" class="dvx-ring-v" style="font-size:' + Math.round(s * 0.2) + 'px">' + esc(o.center) + '</text>';
      if (o.sub) out += '<text x="50%" y="64%" dominant-baseline="middle" text-anchor="middle" class="dvx-ring-s" style="font-size:' + Math.round(s * 0.1) + 'px">' + esc(o.sub) + '</text>';
      return out + '</svg>';
    }
  };

  // ---------- init ----------
  function init(cfg) {
    CFG = Object.assign({ app: 'demo' }, cfg || {});
    if (CFG.accent) document.documentElement.style.setProperty('--dvx-accent', CFG.accent);
    if (CFG.accent2) document.documentElement.style.setProperty('--dvx-accent-2', CFG.accent2);
    addI18n(CFG.i18n);
    if (EN) { startObserver(); walk(document.documentElement); if (document.title) document.title = tr(document.title); }
    CFG._inited = true;
    var go = function () {
      ensureMounts();
      // in DE gibt es keinen Observer: Montage bei Neu-Rendern über eigenen Beobachter halten
      if (!EN && !CFG._mo) {
        CFG._mo = new MutationObserver(function () { ensureMounts(); });
        CFG._mo.observe(document.body, { childList: true, subtree: true });
      }
      var q = new URLSearchParams(location.search).get('tour');
      var seen = tourSeen();
      var hasTour = CFG.tour && CFG.tour.steps && CFG.tour.steps.length;
      if (!hasTour) return;
      if (q === '1') setTimeout(function () { Tour.start(0); }, CFG.tour.delay || 500);
      else if (q !== '0' && !seen && CFG.tour.autoWelcome !== false) setTimeout(welcome, CFG.tour.delay || 700);
    };
    if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', go); else go();
    return api;
  }

  var api = {
    get lang() { return LANG; },
    isEN: EN,
    init: init,
    t: tr,                 // tr('Deutscher Text') -> englisch (wenn EN), sonst unverändert
    pick: T,               // pick({de:'..', en:'..'})
    setLang: setLang,
    addI18n: addI18n,
    translateNow: function (el) { if (EN) walk(el || document.body); },
    tour: Tour,
    startTour: function (i) { Tour.start(i || 0); },
    welcome: welcome,
    charts: Charts,
    langToggle: makeLang,
    tourButton: makeTourBtn,
    sleep: sleep,
    bookUrl: BOOK_URL
  };
  window.DemoKit = api;
})();
