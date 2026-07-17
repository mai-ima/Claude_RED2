/* ==========================================================================
   SUZAKU collab-core.js — コラボ特設の共通部(全コラボで共有する購入系のみ)
   ・.collab-page が無いページでは即 return(自己ゲート)
   ・カウントダウン / 在庫メーター(管理ボード上書き対応)
   ・LPナビの進行バー / 数値カウンタ [data-cl-count]
   作品固有の演出は collab-{slug}.js が持つ(このファイルには置かない)。
   ========================================================================== */
(function () {
  "use strict";
  if (!document.querySelector(".collab-page")) return;

  var reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  /* ---------- 期間限定カウントダウン ---------- */
  var countEl = document.querySelector(".cl-count[data-until]");
  if (countEl && countEl.getAttribute("data-until")) {
    var until = new Date(countEl.getAttribute("data-until")).getTime();
    var slots = {
      d: countEl.querySelector('[data-c="d"]'),
      h: countEl.querySelector('[data-c="h"]'),
      m: countEl.querySelector('[data-c="m"]'),
      s: countEl.querySelector('[data-c="s"]')
    };
    var pad = function (n) { return (n < 10 ? "0" : "") + n; };
    // 第2弾/タブレットの「発表カウントダウン」だけに存在する発表後グレース枠。
    // アクティブなコラボの「受付終了カウントダウン」には無いため、この有無で用途を判別する。
    var soonEl = countEl.querySelector(".cl-count__soon");
    var endEl = countEl.querySelector(".cl-count__end");
    // 二状態ページ(タブレット等): 発表ステージがあれば、ゼロ到達でフルLPへ自動切替。
    var stageT = document.querySelector('[data-reveal-stage="teaser"]');
    var stageF = document.querySelector('[data-reveal-stage="full"]');
    var revealFull = function () {
      if (!stageF || document.body.classList.contains("is-revealed")) return false;
      document.body.classList.add("is-revealed");
      if (stageT) { stageT.hidden = true; stageT.setAttribute("aria-hidden", "true"); }
      stageF.hidden = false;
      stageF.removeAttribute("aria-hidden");
      if (!reduce) {
        stageF.classList.add("is-arriving");
        setTimeout(function () { stageF.classList.remove("is-arriving"); }, 950);
      }
      window.scrollTo({ top: 0, behavior: reduce ? "auto" : "smooth" });
      return true;
    };
    var timer = null;
    var tick = function () {
      var diff = until - Date.now();
      if (diff <= 0) {
        if (slots.d) slots.d.textContent = "0";
        if (slots.h) slots.h.textContent = "00";
        if (slots.m) slots.m.textContent = "00";
        if (slots.s) slots.s.textContent = "00";
        countEl.classList.add("is-ended");
        // フルLPを持つページは発表状態へ切替。無ければ「発表準備中」の受け皿へ。
        if (!revealFull() && soonEl) {
          soonEl.hidden = false;
          if (endEl) endEl.textContent = "まもなく発表(準備中)";
        }
        if (timer) clearInterval(timer);
        return;
      }
      var sec = Math.floor(diff / 1000);
      if (slots.d) slots.d.textContent = String(Math.floor(sec / 86400));
      if (slots.h) slots.h.textContent = pad(Math.floor((sec % 86400) / 3600));
      if (slots.m) slots.m.textContent = pad(Math.floor((sec % 3600) / 60));
      if (slots.s) slots.s.textContent = pad(sec % 60);
    };
    tick();
    timer = setInterval(tick, 1000);
  }

  /* ---------- 数量限定メーター(sz_collab_stock の上書きを優先) ---------- */
  var stockEl = document.querySelector(".cl-stock[data-qty]");
  if (stockEl) {
    var qty = parseInt(stockEl.getAttribute("data-qty"), 10) || 0;
    var sold = parseInt(stockEl.getAttribute("data-sold"), 10) || 0;
    var slug = stockEl.getAttribute("data-slug");
    if (slug && window.szStore) {
      var ov = (window.szStore.get("sz_collab_stock", {}) || {})[slug];
      if (ov && typeof ov.sold === "number") {
        sold = ov.sold;
        if (typeof ov.qty === "number" && ov.qty > 0) qty = ov.qty;
      }
    }
    var remain = Math.max(0, qty - sold);
    var pct = qty > 0 ? Math.round((remain / qty) * 100) : 0;
    var fill = stockEl.querySelector(".cl-stock__fill");
    var remainEl = stockEl.querySelector(".cl-stock__remain");
    if (remainEl) remainEl.textContent = remain.toLocaleString("ja-JP");
    var setW = function () { if (fill) fill.style.width = pct + "%"; };
    if (reduce || !("IntersectionObserver" in window)) { setW(); } else {
      var io = new IntersectionObserver(function (es) {
        es.forEach(function (e) { if (e.isIntersecting) { setW(); io.disconnect(); } });
      }, { threshold: 0.3 });
      io.observe(stockEl);
    }
    if (pct <= 25) stockEl.classList.add("is-low");
  }

  /* ---------- LPナビ進行バー ---------- */
  var lpnav = document.getElementById("clLpnav");
  if (lpnav) {
    var onScroll = function () {
      var doc = document.documentElement;
      var max = doc.scrollHeight - doc.clientHeight;
      var p = max > 0 ? Math.min(1, doc.scrollTop / max) : 0;
      lpnav.style.setProperty("--lp-progress", p.toFixed(4));
    };
    onScroll();
    window.addEventListener("scroll", onScroll, { passive: true });
  }

  /* ---------- 数値カウンタ [data-cl-count] ---------- */
  var counters = document.querySelectorAll("[data-cl-count]");
  if (counters.length) {
    var animate = function (el) {
      var target = parseFloat(el.getAttribute("data-cl-count")) || 0;
      if (reduce) { el.textContent = target.toLocaleString("ja-JP"); return; }
      var t0 = null;
      var dur = 1200;
      var step = function (t) {
        if (!t0) t0 = t;
        var k = Math.min(1, (t - t0) / dur);
        k = 1 - Math.pow(1 - k, 3);
        el.textContent = Math.round(target * k).toLocaleString("ja-JP");
        if (k < 1) requestAnimationFrame(step);
      };
      requestAnimationFrame(step);
    };
    if ("IntersectionObserver" in window && !reduce) {
      var cio = new IntersectionObserver(function (es) {
        es.forEach(function (e) {
          if (e.isIntersecting) { animate(e.target); cio.unobserve(e.target); }
        });
      }, { threshold: 0.4 });
      counters.forEach(function (c) { cio.observe(c); });
    } else {
      counters.forEach(animate);
    }
  }
})();

/* ---------- 購入モジュールの背面⇔正面トグル([data-clview-scope]内で完結) ---------- */
(function () {
  "use strict";
  if (!document.querySelector(".collab-page")) return;
  Array.prototype.forEach.call(document.querySelectorAll("[data-clview-scope]"), function (scope) {
    var img = scope.querySelector(".clview-img");
    if (!img) return;
    Array.prototype.forEach.call(scope.querySelectorAll("[data-clview]"), function (btn) {
      btn.addEventListener("click", function () {
        var view = btn.getAttribute("data-clview");
        img.src = img.getAttribute("data-" + view + "-src") || img.src;
        Array.prototype.forEach.call(scope.querySelectorAll("[data-clview]"), function (b) {
          var on = b === btn;
          b.classList.toggle("is-on", on);
          b.setAttribute("aria-pressed", on ? "true" : "false");
        });
      });
    });
  });
})();
