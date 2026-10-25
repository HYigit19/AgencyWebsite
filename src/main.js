(function () {
  function store(k, v) { try { localStorage.setItem(k, v); } catch (e) {} }

  // Remember language choice when switching.
  document.querySelectorAll(".lang a").forEach(function (a) {
    a.addEventListener("click", function () { store("nexvio-lang", a.getAttribute("hreflang")); });
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

  // Running log on the home page; every row stays readable at rest.
  var reduce = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  document.querySelectorAll(".log-list[data-anim]").forEach(function (list) {
  var rows = Array.prototype.slice.call(list.querySelectorAll(".log-row"));
  if (!reduce && rows.length) {
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
      setTimeout(tick, i === rows.length ? 2600 : 1100);
    };
    setTimeout(tick, 2200);
  }
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
    if (auto) {
      setInterval(function () { if (!auto) return; v = v % 3 + 1; set(v); }, 2600);
    }
  });

  // Contact form: no backend yet, so validate and say so plainly.
  var form = document.getElementById("contact-form");
  if (form) {
    form.addEventListener("submit", function (e) {
      e.preventDefault();
      var st = document.getElementById("form-status");
      var name = document.getElementById("f-name").value.trim();
      var mail = document.getElementById("f-mail");
      var ok = name && mail.value && mail.checkValidity();
      st.textContent = ok ? form.dataset.preview : form.dataset.missing;
      st.hidden = false;
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
