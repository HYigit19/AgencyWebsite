(function () {
  function store(k, v) { try { localStorage.setItem(k, v); } catch (e) {} }

  // Remember language choice when switching.
  document.querySelectorAll(".lang a").forEach(function (a) {
    a.addEventListener("click", function () { store("devunox-lang", a.getAttribute("hreflang")); });
  });

  // Mobile menu
  var btn = document.getElementById("menu-btn");
  var menu = document.getElementById("mobile-menu");
  if (btn && menu) {
    btn.addEventListener("click", function () {
      var open = menu.hidden;
      menu.hidden = !open;
      btn.setAttribute("aria-expanded", String(open));
    });
  }

  var reduce = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  // Live feed in the hero: steps complete one after another, then the cycle restarts.
  // Every step is readable at rest; the animation only starts after a pause.
  document.querySelectorAll(".feed-list[data-anim]").forEach(function (list) {
    var rows = Array.prototype.slice.call(list.querySelectorAll(".fi"));
    if (reduce || !rows.length) return;
    var i = 0;
    var paint = function () {
      rows.forEach(function (r, idx) {
        r.classList.toggle("done", idx < i);
        r.classList.toggle("active", idx === i);
        r.classList.toggle("pending", idx > i);
      });
    };
    var tick = function () {
      i = (i + 1) % (rows.length + 2);
      if (i > rows.length) {
        rows.forEach(function (r) { r.classList.remove("active", "pending"); r.classList.add("done"); });
      } else { paint(); }
      setTimeout(tick, i === rows.length ? 2800 : 1100);
    };
    setTimeout(function () { i = 0; paint(); setTimeout(tick, 1100); }, 2400);
  });

  // Web design example: colour options cycle on their own and can be clicked.
  document.querySelectorAll(".design-ex").forEach(function (box) {
    var buttons = box.querySelectorAll(".sw");
    var set = function (v) {
      box.dataset.v = v;
      buttons.forEach(function (b) { b.setAttribute("aria-pressed", String(b.dataset.v === String(v))); });
    };
    var auto = !reduce, v = 1;
    buttons.forEach(function (b) { b.addEventListener("click", function () { auto = false; set(b.dataset.v); }); });
    if (auto) setInterval(function () { if (!auto) return; v = v % 3 + 1; set(v); }, 2600);
  });

  // Service video: no autoplay when the viewer prefers reduced motion.
  document.querySelectorAll(".video-frame video").forEach(function (v) {
    if (reduce) { v.removeAttribute("autoplay"); try { v.pause(); } catch (e) {} }
  });

  // Contact form: sent by the Cloudflare function /api/contact
  var form = document.getElementById("contact-form");
  if (form) {
    var started = Date.now();
    form.addEventListener("submit", function (e) {
      e.preventDefault();
      var st = document.getElementById("form-status");
      var submit = form.querySelector('button[type="submit"]');
      var name = document.getElementById("f-name").value.trim();
      var mail = document.getElementById("f-mail");
      var show = function (text, kind) { st.textContent = text; st.dataset.kind = kind || ""; st.hidden = false; };
      if (!(name && mail.value && mail.checkValidity())) { show(form.dataset.missing, "error"); return; }
      if (submit.disabled) return;
      var label = submit.textContent;
      submit.disabled = true; submit.textContent = form.dataset.sending;
      var body = {
        name: name,
        company: document.getElementById("f-company").value,
        email: mail.value.trim(),
        topic: document.getElementById("f-topic").value,
        message: document.getElementById("f-msg").value,
        website: (form.querySelector('[name="website"]') || {}).value || "",
        lang: document.documentElement.lang === "en" ? "en" : "de",
        t: Date.now() - started
      };
      fetch(form.action || "/api/contact", { method: "POST", headers: { "content-type": "application/json" }, body: JSON.stringify(body) })
        .then(function (r) { return r.json().catch(function () { return {}; }).then(function (d) { return { ok: r.ok && d.ok, d: d }; }); })
        .then(function (r) {
          if (r.ok) { form.reset(); show(form.dataset.success, "ok"); submit.textContent = form.dataset.sent; return; }
          show(r.d && r.d.error === "missing" ? form.dataset.missing : form.dataset.error, "error");
          submit.disabled = false; submit.textContent = label;
        })
        .catch(function () { show(form.dataset.error, "error"); submit.disabled = false; submit.textContent = label; });
    });
  }


  // Copy email address
  var copyBtn = document.getElementById("copy-mail");
  if (copyBtn) {
    var label = copyBtn.textContent;
    copyBtn.addEventListener("click", function () {
      var el = document.getElementById("mail-addr");
      var done = function () { copyBtn.textContent = copyBtn.dataset.done; setTimeout(function () { copyBtn.textContent = label; }, 1600); };
      var fallback = function () {
        var r = document.createRange(); r.selectNodeContents(el);
        var s = window.getSelection(); s.removeAllRanges(); s.addRange(r);
      };
      try { navigator.clipboard.writeText(el.textContent).then(done, fallback); } catch (e) { fallback(); }
    });
  }
})();
