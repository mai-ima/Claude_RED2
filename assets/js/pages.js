/* ==========================================================================
   SUZAKU pages.js — FAQ / ニュース一覧 / サイト内検索 / 修理受付・照会 / 汎用フォーム
   ========================================================================== */
(function () {
  "use strict";

  var $ = function (sel, root) { return (root || document).querySelector(sel); };
  var $$ = function (sel, root) { return Array.prototype.slice.call((root || document).querySelectorAll(sel)); };
  var SZ = window.SZ || { products: [], news: [], faq: [], pages: [] };

  var esc = window.szFmt.esc;

  /* ---------------- FAQ ---------------- */
  var faqList = $("#faqList");
  if (faqList) {
    var faqCat = "all";
    var faqQuery = "";
    function renderFaq() {
      var items = SZ.faq.filter(function (f) {
        if (faqCat !== "all" && f.cat !== faqCat) return false;
        if (faqQuery && (f.q + f.a).toLowerCase().indexOf(faqQuery) === -1) return false;
        return true;
      });
      if (!items.length) {
        faqList.innerHTML = '<div class="empty"><p class="empty__icon"><svg class="ic" viewBox="0 0 24 24" aria-hidden="true"><circle cx="11" cy="11" r="7"/><path d="M20 20l-3.5-3.5"/></svg></p><p>該当するご質問が見つかりませんでした。</p><a class="btn btn--ghost" href="/support/contact/">お問い合わせフォームへ</a></div>';
        return;
      }
      faqList.innerHTML = '<div class="accordion">' + items.map(function (f) {
        return '<div class="accordion__item"><button class="accordion__q" aria-expanded="false"><span><span class="badge" style="margin-right:10px">' + f.cat + "</span>" + esc(f.q) + "</span></button>" +
          '<div class="accordion__a"><div class="accordion__a-inner"><div class="accordion__a-body">' + f.a + "</div></div></div></div>";
      }).join("") + "</div>";
      var count = $("#faqCount");
      if (count) count.textContent = items.length + "件";
    }
    var tabsBox = $("#faqTabs");
    if (tabsBox) {
      var cats = ["all"];
      SZ.faq.forEach(function (f) { if (cats.indexOf(f.cat) === -1) cats.push(f.cat); });
      tabsBox.innerHTML = cats.map(function (c, i) {
        return '<button class="tab' + (i === 0 ? " is-active" : "") + '" data-faq-cat="' + c + '">' + (c === "all" ? "すべて" : c) + "</button>";
      }).join("");
      tabsBox.addEventListener("click", function (e) {
        var t = e.target.closest("[data-faq-cat]");
        if (!t) return;
        $$(".tab", tabsBox).forEach(function (x) { x.classList.remove("is-active"); });
        t.classList.add("is-active");
        faqCat = t.getAttribute("data-faq-cat");
        renderFaq();
      });
    }
    var faqSearch = $("#faqSearch");
    if (faqSearch) {
      faqSearch.addEventListener("input", function () {
        faqQuery = faqSearch.value.trim().toLowerCase();
        renderFaq();
      });
    }
    renderFaq();
  }

  /* ---------------- ニュース一覧 ---------------- */
  /* 管理ボードで作成されたニュース(localStorage)を静的ニュースとマージ */
  function adminNewsItems() {
    return (window.szStore ? window.szStore.get("sz_admin_news", []) : []).map(function (n) {
      return { date: n.date, cat: n.cat, title: n.title, excerpt: n.excerpt, url: "/news/article/?id=" + encodeURIComponent(n.id) };
    });
  }
  function mergedNews() {
    return adminNewsItems().concat(SZ.news).sort(function (a, b) { return a.date < b.date ? 1 : -1; });
  }
  var newsList = $("#newsList");
  if (newsList) {
    var NEWS_ALL = mergedNews();
    var nYear = "all";
    var nCat = "all";
    function renderNews() {
      var items = NEWS_ALL.filter(function (n) {
        if (nYear !== "all" && n.date.slice(0, 4) !== nYear) return false;
        if (nCat !== "all" && n.cat !== nCat) return false;
        return true;
      });
      if (!items.length) {
        newsList.innerHTML = '<div class="empty"><p>該当するニュースはありません。</p></div>';
        return;
      }
      newsList.innerHTML = items.map(function (n) {
        return '<a class="card card--hover" href="' + n.url + '">' +
          '<p class="t-micro t-faint">' + n.date.replace(/-/g, ".") + ' <span class="badge" style="margin-left:8px">' + n.cat + "</span></p>" +
          '<h2 class="t-h4">' + esc(n.title) + "</h2>" +
          '<p class="t-small t-soft">' + esc(n.excerpt) + "</p>" +
          '<p class="link-arrow">読む</p></a>';
      }).join("");
    }
    var yearBox = $("#newsYears");
    if (yearBox) {
      var years = ["all"];
      NEWS_ALL.forEach(function (n) {
        var y = n.date.slice(0, 4);
        if (years.indexOf(y) === -1) years.push(y);
      });
      yearBox.innerHTML = years.map(function (y, i) {
        return '<button class="tab' + (i === 0 ? " is-active" : "") + '" data-news-year="' + y + '">' + (y === "all" ? "すべての年" : y + "年") + "</button>";
      }).join("");
    }
    var catBox = $("#newsCats");
    if (catBox) {
      var ncats = ["all"];
      NEWS_ALL.forEach(function (n) { if (ncats.indexOf(n.cat) === -1) ncats.push(n.cat); });
      catBox.innerHTML = ncats.map(function (c, i) {
        return '<button class="tab' + (i === 0 ? " is-active" : "") + '" data-news-cat="' + c + '">' + (c === "all" ? "すべて" : c) + "</button>";
      }).join("");
    }
    document.addEventListener("click", function (e) {
      var y = e.target.closest("[data-news-year]");
      var c = e.target.closest("[data-news-cat]");
      if (y) {
        $$("[data-news-year]").forEach(function (x) { x.classList.remove("is-active"); });
        y.classList.add("is-active");
        nYear = y.getAttribute("data-news-year");
        renderNews();
      } else if (c) {
        $$("[data-news-cat]").forEach(function (x) { x.classList.remove("is-active"); });
        c.classList.add("is-active");
        nCat = c.getAttribute("data-news-cat");
        renderNews();
      }
    });
    renderNews();
  }

  /* ---------------- 管理ボード作成ニュースの記事ページ ---------------- */
  var customArticle = $("#customArticle");
  if (customArticle) {
    var caId = new URLSearchParams(window.location.search).get("id") || "";
    var caList = window.szStore ? window.szStore.get("sz_admin_news", []) : [];
    var ca = caList.filter(function (n) { return n.id === caId; })[0];
    if (!ca) {
      customArticle.innerHTML = '<div class="notice"><svg class="ic" viewBox="0 0 24 24" aria-hidden="true"><path d="M12 4l9 16H3z"/><path d="M12 10.5v4M12 17.6h.01"/></svg> この記事は見つかりませんでした(削除された可能性があります)。</div>' +
        '<div style="margin-top:20px"><a class="btn btn--ghost" href="/news/">ニュース一覧へ戻る</a></div>';
    } else {
      document.title = ca.title + " | SUZAKU(朱雀)";
      customArticle.innerHTML =
        '<p class="t-micro t-faint">' + ca.date.replace(/-/g, ".") + ' <span class="badge" style="margin-left:8px">' + esc(ca.cat) + "</span></p>" +
        '<h1 class="t-h2" style="margin:10px 0 24px">' + esc(ca.title) + "</h1>" +
        '<div class="prose">' + ca.body.split(/\n{2,}|\n/).filter(Boolean).map(function (p) { return "<p>" + esc(p) + "</p>"; }).join("") + "</div>" +
        '<p class="t-micro t-faint" style="margin-top:28px">この記事は管理ボードから作成されたデモ記事です(この端末のブラウザ内にのみ保存されています)。</p>' +
        '<div style="margin-top:20px"><a class="btn btn--ghost" href="/news/">ニュース一覧へ戻る</a></div>';
    }
  }

  /* ---------------- サイト内検索 ---------------- */
  var searchResults = $("#searchResults");
  if (searchResults) {
    var input = $("#siteSearchInput");
    var params = new URLSearchParams(window.location.search);
    var q0 = params.get("q") || "";
    if (input) input.value = q0;

    function buildIndex() {
      var idx = [];
      SZ.products.forEach(function (p) {
        idx.push({ type: "製品", title: p.name + "(" + p.lineLabel + " / " + p.year + ")", url: p.url, text: p.name + " " + p.kana + " " + p.tagline + " " + p.lineLabel });
      });
      SZ.news.forEach(function (n) {
        idx.push({ type: "ニュース", title: n.title, url: n.url, text: n.title + " " + n.excerpt + " " + n.cat });
      });
      SZ.faq.forEach(function (f) {
        idx.push({ type: "FAQ", title: f.q, url: "/support/faq/", text: f.q + " " + f.a.replace(/<[^>]+>/g, "") });
      });
      SZ.pages.forEach(function (pg) {
        idx.push({ type: pg.group, title: pg.title, url: pg.url, text: pg.title + " " + pg.desc });
      });
      return idx;
    }
    var index = buildIndex();

    /* 表記ゆれ正規化: NFKC(全角英数→半角等)+ カタカナ→ひらがな折りたたみ。
       「スザク」「suzaku」「SUZAKU」等を同一視するための共通形。 */
    function szNorm(s) {
      return String(s).normalize("NFKC").toLowerCase().replace(/[ァ-ヶ]/g, function (ch) {
        return String.fromCharCode(ch.charCodeAt(0) - 0x60);
      });
    }
    /* エイリアス辞書(同義語リング)。各要素は szNorm 済み表記で書く。
       かな⇔漢字⇔ラテンの橋渡し用(カナ⇔かなは szNorm が吸収する)。 */
    var ALIASES = [
      ["すざく", "朱雀", "suzaku"],
      ["らい", "雷", "rai"],
      ["つばめ", "燕", "tsubame"],
      ["ねお", "neo"],
      ["しちよう", "七耀", "shichiyo"],
      ["ざんきょう", "残響", "zankyo"],
      ["やこう", "夜行", "yako"],
      ["ぜんせん", "前線", "zensen"],
      ["げんしん", "原神", "genshin"],
      ["めいちょう", "鳴潮", "wuwa"],
      ["えぬてぃーいー", "nte"],
      ["えんどふぃーるど", "endfield", "エンドフィールド"],
      ["でんち", "電池", "ばってりー"],
      ["れいきゃく", "冷却"],
      ["いやほん", "イヤホン", "buds"],
      ["けーす", "ケース", "case"]
    ].map(function (g) { return g.map(szNorm); });
    function variantsOf(t) {
      var out = [t];
      ALIASES.forEach(function (g) {
        if (g.indexOf(t) !== -1) {
          g.forEach(function (v) { if (out.indexOf(v) === -1) out.push(v); });
        }
      });
      return out;
    }

    /* 「もしかして」用: 各同義語グループの代表表示名。かな/ラテン表記で入力されたら
       正式表記(漢字・作品名)を提案する。variants は szNorm 済みで持つ。 */
    var SUGGEST_GROUPS = [
      { display: "朱雀", variants: ["すざく", "朱雀", "suzaku"] },
      { display: "雷", variants: ["らい", "雷", "rai"] },
      { display: "燕", variants: ["つばめ", "燕", "tsubame"] },
      { display: "七耀", variants: ["しちよう", "七耀", "shichiyo"] },
      { display: "残響", variants: ["ざんきょう", "残響", "zankyo"] },
      { display: "夜行", variants: ["やこう", "夜行", "yako"] },
      { display: "前線", variants: ["ぜんせん", "前線", "zensen"] },
      { display: "原神", variants: ["げんしん", "原神", "genshin"] },
      { display: "鳴潮", variants: ["めいちょう", "鳴潮", "wuwa"] },
      { display: "NTE", variants: ["えぬてぃーいー", "nte"] },
      { display: "エンドフィールド", variants: ["えんどふぃーるど", "endfield", "エンドフィールド"] }
    ].map(function (g) { return { display: g.display, nvar: g.variants.map(szNorm) }; });

    /* 生クエリの各語について、別表記なら代表表示名へ置換した提案文字列を返す(なければ null)。 */
    function suggestFor(raw) {
      var changed = false;
      var out = String(raw).trim().split(/\s+/).map(function (rt) {
        var n = szNorm(rt);
        for (var i = 0; i < SUGGEST_GROUPS.length; i++) {
          var g = SUGGEST_GROUPS[i];
          if (g.nvar.indexOf(n) !== -1 && szNorm(g.display) !== n) { changed = true; return g.display; }
        }
        return rt;
      });
      return changed ? out.join(" ") : null;
    }
    function suggestHtml(raw) {
      var s = suggestFor(raw);
      if (!s) return "";
      return '<div class="did-you-mean">もしかして: <button type="button" class="dym-chip" data-suggest="' +
        esc(s) + '">' + esc(s) + "</button></div>";
    }

    function doSearch(q) {
      var raw = String(q).trim();
      var sug = suggestHtml(raw);
      q = szNorm(raw);
      var info = $("#searchInfo");
      if (!q) {
        searchResults.innerHTML = "";
        if (info) info.textContent = "キーワードを入力してください(例: SUZAKU 4、冷却、修理、保証)。";
        return;
      }
      var terms = q.split(/\s+/).map(variantsOf);
      var hits = index.map(function (item) {
        var hay = szNorm(item.title + " " + item.text);
        var title = szNorm(item.title);
        var score = 0;
        var ok = terms.every(function (vs) {
          return vs.some(function (v) { return hay.indexOf(v) !== -1; });
        });
        if (!ok) return null;
        terms.forEach(function (vs) {
          if (vs.some(function (v) { return title.indexOf(v) !== -1; })) score += 3;
          score += 1;
        });
        return { item: item, score: score };
      }).filter(Boolean).sort(function (a, b) { return b.score - a.score; }).slice(0, 40);
      if (info) info.textContent = '「' + raw + '」の検索結果: ' + hits.length + "件";
      if (!hits.length) {
        searchResults.innerHTML = sug + '<div class="empty"><p class="empty__icon"><svg class="ic" viewBox="0 0 24 24" aria-hidden="true"><circle cx="11" cy="11" r="7"/><path d="M20 20l-3.5-3.5"/></svg></p><p>一致する結果が見つかりませんでした。別のキーワードをお試しください。</p></div>';
        return;
      }
      searchResults.innerHTML = sug + hits.map(function (h) {
        return '<a class="card card--hover" href="' + h.item.url + '">' +
          '<p class="t-micro" style="color:var(--accent);font-weight:700">' + esc(h.item.type) + "</p>" +
          '<h2 class="t-h4">' + esc(h.item.title) + "</h2>" +
          '<p class="t-micro t-faint">' + h.item.url + "</p></a>";
      }).join("");
    }
    if (input) {
      input.addEventListener("input", function () { doSearch(input.value); });
    }
    // 「もしかして」チップ: クリックで代表表記に置換して再検索(URLも更新)
    searchResults.addEventListener("click", function (e) {
      var chip = e.target.closest ? e.target.closest("[data-suggest]") : null;
      if (!chip) return;
      e.preventDefault();
      var s = chip.getAttribute("data-suggest");
      if (input) input.value = s;
      if (window.history && history.replaceState) {
        history.replaceState(null, "", "?q=" + encodeURIComponent(s));
      }
      doSearch(s);
      if (input) input.focus();
    });
    doSearch(q0);
  }

  /* ---------------- 停止制御(管理ボード設定の参照) ---------------- */
  function ctrlGlobal() { return window.szStore ? window.szStore.get("sz_global", {}) : {}; }
  function svcStatus(key) {
    var s = window.szStore ? window.szStore.get("sz_services", {}) : {};
    return s[key] || "ok";
  }
  function stopNotice(form, msg) {
    var n = form.querySelector(".stop-notice");
    if (!n) {
      n = document.createElement("div");
      n.className = "notice stop-notice";
      form.insertBefore(n, form.firstChild);
    }
    n.innerHTML = '<svg class="ic" viewBox="0 0 24 24" aria-hidden="true"><path d="M12 4l9 16H3z"/><path d="M12 10.5v4M12 17.6h.01"/></svg> ' + msg;
    window.szToast(msg);
  }

  /* ---------------- 修理受付フォーム ---------------- */
  var repairForm = $("#repairForm");
  if (repairForm) {
    repairForm.addEventListener("submit", function (e) {
      e.preventDefault();
      if (svcStatus("repair") === "down") {
        stopNotice(repairForm, "現在、修理受付を停止しています。復旧までお待ちください。");
        return;
      }
      var ok = true;
      $$("input[required], select[required], textarea[required]", repairForm).forEach(function (inp) {
        var field = inp.closest(".field");
        var bad = !inp.value.trim();
        if (inp.type === "email" && inp.value && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(inp.value)) bad = true;
        if (field) field.classList.toggle("has-error", bad);
        if (bad) ok = false;
      });
      if (!ok) { window.szToast("入力内容をご確認ください"); return; }
      var no = "SZR-" + String(Math.floor(10000000 + Math.random() * 90000000));
      var tickets = window.szStore.get("sz_tickets", []);
      tickets.unshift({
        no: no,
        date: new Date().toISOString(),
        model: $("#rpModel").value,
        symptom: $("#rpSymptom").value,
        method: repairForm.querySelector("input[name=rpMethod]:checked").value,
        status: "受付完了"
      });
      window.szStore.set("sz_tickets", tickets);
      repairForm.hidden = true;
      var done = $("#repairDone");
      $("#repairNo").textContent = no;
      done.hidden = false;
      window.scrollTo({ top: 0, behavior: "smooth" });
    });
  }

  /* ---------------- 修理状況照会 ---------------- */
  var ticketLookup = $("#ticketLookupForm");
  if (ticketLookup) {
    ticketLookup.addEventListener("submit", function (e) {
      e.preventDefault();
      var no = $("#ticketNo").value.trim().toUpperCase();
      var tickets = window.szStore.get("sz_tickets", []);
      var hit = tickets.filter(function (t) { return t.no === no; })[0];
      var box = $("#ticketResult");
      if (!hit) {
        box.innerHTML = '<div class="notice"><svg class="ic" viewBox="0 0 24 24" aria-hidden="true"><path d="M12 4l9 16H3z"/><path d="M12 10.5v4M12 17.6h.01"/></svg> 受付番号「' + esc(no) + '」は見つかりませんでした。この端末で行われたお申し込みのみ照会できます(デモ仕様)。</div>';
        return;
      }
      var placed = new Date(hit.date);
      var hours = (Date.now() - placed.getTime()) / 36e5;
      var stages = (window.szStages && window.szStages.repair) || ["受付完了", "診断中", "修理作業中", "返送手配", "お届け完了"];
      /* 管理ボードで明示的に設定したステータスを優先。未設定なら経過時間から推定。 */
      var reached = typeof hit.statusIdx === "number"
        ? hit.statusIdx
        : (hours > 144 ? 4 : hours > 96 ? 3 : hours > 48 ? 2 : hours > 24 ? 1 : 0);
      box.innerHTML = '<div class="card" style="margin-top:24px">' +
        '<p class="eyebrow">受付番号 ' + hit.no + "</p>" +
        '<p class="t-small t-soft">受付日時: ' + placed.toLocaleString("ja-JP") + " / 対象機種: " + esc(hit.model) + " / 方法: " + esc(hit.method) +
        ' / 現在の状況: <strong style="color:var(--accent)">' + esc(stages[reached]) + "</strong></p>" +
        '<ol class="order-track">' + stages.map(function (t, i) {
          return '<li class="' + (i <= reached ? "is-done" : "") + '"><span>' + esc(t) + "</span></li>";
        }).join("") + "</ol></div>";
    });
  }

  /* ---------------- ドキュメントビューア(PDF閲覧) ---------------- */
  var docPages = $("#docPages");
  if (docPages) {
    var docs = SZ.docs || [];
    var docId = new URLSearchParams(window.location.search).get("doc") || (docs[0] && docs[0].id);
    var doc = docs.filter(function (d) { return d.id === docId; })[0] || docs[0];

    function block(b) {
      if (b.t === "h1") return "<h1>" + esc(b.v) + "</h1>";
      if (b.t === "h2") return "<h2>" + esc(b.v) + "</h2>";
      if (b.t === "p") return "<p>" + esc(b.v) + "</p>";
      if (b.t === "note") return '<p class="doc-note">' + esc(b.v) + "</p>";
      if (b.t === "list") return "<ul>" + b.v.map(function (x) { return "<li>" + esc(x) + "</li>"; }).join("") + "</ul>";
      if (b.t === "table") {
        return '<table>' + b.v.map(function (row, i) {
          var tag = i === 0 && b.v.length > 2 && b.v[0].length > 2 ? "th" : "td";
          return "<tr>" + row.map(function (c) { return "<" + tag + ">" + esc(c) + "</" + tag + ">"; }).join("") + "</tr>";
        }).join("") + "</table>";
      }
      return "";
    }

    if (doc) {
      $("#docTitle").textContent = doc.title;
      $("#docMeta").textContent = doc.category + " / " + doc.version;
      document.title = doc.title + " | SUZAKU(朱雀)";
      docPages.innerHTML = doc.pages.map(function (pg, i) {
        return '<article class="doc-page" data-page="' + (i + 1) + '">' +
          '<header class="doc-page__head"><span>SUZAKU — ' + esc(doc.title) + "</span><span>" + esc(doc.version) + "</span></header>" +
          pg.map(block).join("") +
          '<footer class="doc-page__foot"><span>© 2022-2026 SUZAKU Inc.(架空のデモ文書)</span><span>' + (i + 1) + " / " + doc.pages.length + "</span></footer></article>";
      }).join("");
      $("#docPageInfo").textContent = "1 / " + doc.pages.length;

      // 表示中ページ番号
      if ("IntersectionObserver" in window) {
        var pio = new IntersectionObserver(function (ens) {
          ens.forEach(function (en) {
            if (en.isIntersecting) $("#docPageInfo").textContent = en.target.getAttribute("data-page") + " / " + doc.pages.length;
          });
        }, { threshold: 0.5 });
        $$(".doc-page", docPages).forEach(function (el) { pio.observe(el); });
      }
    }

    // ズーム
    var zoom = 100;
    function applyZoom() {
      docPages.style.setProperty("--doc-zoom", zoom / 100);
      $("#zoomLevel").textContent = zoom + "%";
    }
    $("#zoomIn").addEventListener("click", function () { zoom = Math.min(150, zoom + 10); applyZoom(); });
    $("#zoomOut").addEventListener("click", function () { zoom = Math.max(70, zoom - 10); applyZoom(); });
    $("#docPrint").addEventListener("click", function () { window.print(); });

    // ライブラリ
    var lib = $("#docLibrary");
    if (lib) {
      lib.innerHTML = docs.map(function (d) {
        var cur = doc && d.id === doc.id;
        return '<a class="card card--hover' + (cur ? " is-current-doc" : "") + '" href="/viewer/?doc=' + d.id + '">' +
          '<div class="spread"><div><p class="eyebrow">' + esc(d.category) + "</p><h3 class='t-h4'>" + esc(d.title) +
          (cur ? ' <span class="badge">表示中</span>' : "") + "</h3><p class='t-micro t-faint'>" + esc(d.version) + " / " + d.pages.length + "ページ</p></div>" +
          '<span class="link-arrow">開く</span></div></a>';
      }).join("");
    }
  }

  /* ---------------- 汎用モックフォーム(お問い合わせ等) ---------------- */
  $$("form[data-mock-form]").forEach(function (form) {
    form.addEventListener("submit", function (e) {
      e.preventDefault();
      if (ctrlGlobal().contactStop) {
        stopNotice(form, "現在、お問い合わせの受付を停止しています。復旧までお待ちください。");
        return;
      }
      var ok = true;
      $$("input[required], select[required], textarea[required]", form).forEach(function (inp) {
        var field = inp.closest(".field");
        var bad = !inp.value.trim();
        if (inp.type === "email" && inp.value && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(inp.value)) bad = true;
        if (inp.type === "checkbox" && inp.required && !inp.checked) bad = true;
        if (field) field.classList.toggle("has-error", bad);
        if (bad) ok = false;
      });
      if (!ok) { window.szToast("入力内容をご確認ください"); return; }
      form.hidden = true;
      var doneSel = form.getAttribute("data-mock-form") || "#formDone";
      var done = $(doneSel);
      if (done) {
        done.hidden = false;
        var ref = done.querySelector("[data-ref-no]");
        if (ref) ref.textContent = "SZC-" + String(Math.floor(10000000 + Math.random() * 90000000));
      }
      window.scrollTo({ top: 0, behavior: "smooth" });
      window.szToast("送信が完了しました");
    });
  });

  /* ---------------- 設定ページ ---------------- */
  var settingsPage = $("#settingsPage");
  if (settingsPage && window.szPrefs) {
    /* data-pref を持つ各グループを汎用配線。設定項目を増やしても、HTMLに
       グループを1つ足すだけで動く(個別のJSは不要)。 */
    $$("[data-pref]", settingsPage).forEach(function (group) {
      var key = group.getAttribute("data-pref");
      function sync() {
        var cur = window.szPrefs.get()[key];
        $$("[data-pref-value]", group).forEach(function (b) {
          var on = b.getAttribute("data-pref-value") === cur;
          b.classList.toggle("is-active", on);
          b.setAttribute("aria-pressed", String(on));
        });
      }
      group.addEventListener("click", function (e) {
        var b = e.target.closest("[data-pref-value]");
        if (!b) return;
        window.szPrefs.set(key, b.getAttribute("data-pref-value"));
        sync();
        renderStorageInfo();
        window.szToast("設定を保存しました");
      });
      sync();
    });

    /* 保存データ一覧(localStorage 使用状況) */
    var STORAGE_LABELS = {
      sz_prefs: "表示設定(このページの設定)",
      sz_theme: "カラーテーマ",
      sz_cart: "カートの中身",
      sz_orders: "注文履歴(この端末)",
      sz_tickets: "修理受付(この端末)",
      sz_users: "アカウント情報",
      sz_session: "ログイン状態",
      sz_consent: "Cookie同意の記録",
      sz_maintenance: "メンテナンス設定(管理者)",
      sz_global: "全体制御設定(管理者)",
      sz_page_ctrl: "ページ別制御(管理者)",
      sz_services: "サービス状況(管理者)",
      sz_admin_news: "管理ボードで作成したニュース",
      sz_seed_del: "削除済みデモ会員の記録",
      sz_announce: "お知らせバナー設定(管理者)",
      sz_store_cfg: "ストア設定(管理者)",
      sz_admin_log: "管理ボードの操作記録",
      sz_announce_seen: "お知らせバナーの既読状態"
    };
    /* 対象キーは szKeys レジストリを情報源とし、STORAGE_LABELS 側の記載漏れで
       表示から抜け落ちないようにする(ラベル未登録キーはキー名をそのまま表示)。 */
    var STORAGE_KEYS = [].concat(window.szKeys.PREF, window.szKeys.DATA, window.szKeys.VOLATILE, ["sz_session"]);
    function renderStorageInfo() {
      var box = $("#storageInfo", settingsPage);
      if (!box) return;
      var rows = [];
      STORAGE_KEYS.forEach(function (key) {
        var raw = null;
        try { raw = localStorage.getItem(key); } catch (e) { /* noop */ }
        if (raw === null) return;
        var bytes = raw.length;
        var size = bytes < 1024 ? bytes + " B" : (bytes / 1024).toFixed(1) + " KB";
        rows.push('<div class="storage-list__row"><span>' + esc(STORAGE_LABELS[key] || key) +
          ' <code class="t-micro t-faint">' + esc(key) + '</code></span><span class="t-micro t-faint">' + size + "</span></div>");
      });
      box.innerHTML = rows.length
        ? rows.join("")
        : '<p class="t-small t-soft">保存されているデータはありません。</p>';
    }
    renderStorageInfo();

    var resetBtn = $("#prefReset", settingsPage);
    if (resetBtn) {
      resetBtn.addEventListener("click", function () {
        window.szPrefs.reset();
        window.szToast("表示設定を初期化しました");
        setTimeout(function () { window.location.reload(); }, 500);
      });
    }
  }

  /* ---------------- 用語集(/support/glossary/) ---------------- */
  var glossaryList = $("#glossaryList");
  if (glossaryList) {
    var terms = (SZ.glossary || []).slice().sort(function (a, b) {
      return a.reading < b.reading ? -1 : a.reading > b.reading ? 1 : 0;
    });
    var cats = ["すべて"];
    terms.forEach(function (t) { if (cats.indexOf(t.cat) === -1) cats.push(t.cat); });
    var curCat = "すべて";
    var query = "";
    var slugify = function (t) { return t.replace(/[^0-9A-Za-z一-龠ぁ-んァ-ヶー]+/g, "-").toLowerCase(); };

    var filtersBox = $("#glossaryFilters");
    if (filtersBox) {
      filtersBox.innerHTML = cats.map(function (c) {
        return '<button class="tab' + (c === "すべて" ? " is-active" : "") + '" type="button" data-gcat="' + esc(c) + '">' + esc(c) + "</button>";
      }).join("");
    }

    function render() {
      var list = terms.filter(function (t) {
        if (curCat !== "すべて" && t.cat !== curCat) return false;
        if (query) {
          var hay = (t.term + " " + t.reading + " " + t.cat + " " + t.desc).toLowerCase();
          if (hay.indexOf(query) === -1) return false;
        }
        return true;
      });
      glossaryList.innerHTML = list.length
        ? list.map(function (t) {
            var link = t.link ? '<a class="link-arrow" href="' + esc(t.link) + '">関連ページを見る</a>' : "";
            return '<article class="card reveal" id="term-' + slugify(t.term) + '">' +
              '<div class="spread" style="align-items:baseline;gap:10px"><h2 class="t-h4">' + esc(t.term) +
              ' <small class="t-faint" style="font-weight:400">' + esc(t.reading) + "</small></h2>" +
              '<span class="badge">' + esc(t.cat) + "</span></div>" +
              '<p class="t-soft t-small" style="margin-top:8px">' + t.desc + "</p>" +
              (link ? '<div style="margin-top:10px">' + link + "</div>" : "") + "</article>";
          }).join("")
        : '<p class="t-soft">該当する用語が見つかりませんでした。</p>';
      var info = $("#glossaryInfo");
      if (info) info.textContent = list.length + " 件の用語" + (curCat !== "すべて" ? "(" + curCat + ")" : "");
    }

    if (filtersBox) {
      filtersBox.addEventListener("click", function (e) {
        var b = e.target.closest("[data-gcat]");
        if (!b) return;
        curCat = b.getAttribute("data-gcat");
        Array.prototype.forEach.call(filtersBox.querySelectorAll(".tab"), function (x) {
          x.classList.toggle("is-active", x === b);
        });
        render();
      });
    }
    var gSearch = $("#glossarySearch");
    if (gSearch) gSearch.addEventListener("input", function () { query = gSearch.value.trim().toLowerCase(); render(); });
    render();

    // ハッシュ付きで来たら該当用語へスクロール
    if (location.hash) {
      var target = document.getElementById(location.hash.slice(1));
      if (target) setTimeout(function () { target.scrollIntoView(); }, 100);
    }
  }

  /* 沿革(/company/history/)は gen.py がビルド時にサーバー描画する(SEO対応)。 */

  /* ---------------- 製品セレクター(/products/finder/) ---------------- */
  var finder = $("#productFinder");
  if (finder) {
    var yen = window.szFmt.yen;
    var answers = { use: null, budget: null, priority: null };
    var runBtn = $("#finderRun");
    var resultBox = $("#finderResult");

    finder.addEventListener("click", function (e) {
      var opt = e.target.closest(".finder__opt");
      if (!opt) return;
      var q = opt.getAttribute("data-q");
      answers[q] = opt.getAttribute("data-val");
      Array.prototype.forEach.call(finder.querySelectorAll('[data-q="' + q + '"]'), function (b) {
        b.classList.toggle("is-active", b === opt);
      });
      var ready = answers.use && answers.budget && answers.priority;
      if (runBtn) runBtn.disabled = !ready;
      var hint = $("#finderHint");
      if (hint) hint.textContent = ready ? "準備ができました。「おすすめを見る」を押してください。" : "3つすべて選ぶと結果を表示します。";
    });

    // 用途 → ライン優先度(高いほど加点)
    var LINE_PREF = {
      game:    { suzaku: 30, collab: 26, neo: 22, tsubame: 8, lite: 2 },
      balance: { neo: 26, tsubame: 22, suzaku: 16, lite: 12, collab: 10 },
      daily:   { tsubame: 28, lite: 20, neo: 12, suzaku: 8, collab: 4 },
      first:   { lite: 32, tsubame: 16, neo: 6, suzaku: 0, collab: 0 }
    };
    // 重視点 → radar軸(0:性能 1:カメラ 2:電池 3:冷却 4:コスパ)
    var PRIORITY_AXIS = { perf: 0, cam: 1, bat: 2, cost: 4 };
    var PRIORITY_LABEL = { perf: "性能", cam: "カメラ", bat: "バッテリー", cost: "コストパフォーマンス" };

    function recommend() {
      var budget = parseInt(answers.budget, 10);
      var axis = PRIORITY_AXIS[answers.priority];
      var pref = LINE_PREF[answers.use] || {};
      var phones = (SZ.products || []).filter(function (p) {
        return p.cat === "phone" && p.status === "current" && p.radar;
      });
      var scored = phones.map(function (p) {
        var score = 0;
        score += (pref[p.line] || 0);
        score += (p.radar[axis] || 0) * 0.8;
        // 予算適合: 予算内は加点、超過は大きく減点
        if (p.price <= budget) score += 18 - (budget - p.price) / 20000;
        else score -= (p.price - budget) / 8000;
        return { p: p, score: score };
      }).sort(function (a, b) { return b.score - a.score; });
      return scored.slice(0, 2).map(function (s) { return s.p; });
    }

    function card(p, best) {
      var tag = best ? '<span class="badge badge--new">おすすめ No.1</span>' : '<span class="badge">次点</span>';
      return '<a class="product-card" href="' + esc(p.url) + '">' +
        '<div class="product-card__media"><img src="' + esc(p.img) + '" alt="' + esc(p.name) + '" loading="lazy" width="360" height="640"></div>' +
        '<div class="product-card__body"><p class="product-card__tag">' + esc(p.lineLabel) + " / " + p.year + " " + tag + "</p>" +
        '<p class="product-card__name">' + esc(p.name) + "</p>" +
        '<p class="product-card__copy">' + esc(p.tagline) + "</p>" +
        '<p class="product-card__price">' + yen(p.price) + " <small>(税込)〜</small></p></div></a>";
    }

    if (runBtn) runBtn.addEventListener("click", function () {
      var recs = recommend();
      if (!recs.length) { resultBox.innerHTML = '<p class="t-soft">条件に合うモデルが見つかりませんでした。予算を広げてお試しください。</p>'; return; }
      var reason = "「" + PRIORITY_LABEL[answers.priority] + "」重視・ご予算" +
        (parseInt(answers.budget, 10) >= 999999 ? "上限なし" : "〜" + yen(parseInt(answers.budget, 10))) + "のあなたには、こちらがおすすめです。";
      resultBox.innerHTML = '<div class="section-head"><p class="eyebrow">RESULT</p><h2 class="t-h2">あなたへのおすすめ</h2>' +
        '<p class="t-soft">' + esc(reason) + "</p></div>" +
        '<div class="grid grid--2 grid--cards">' + recs.map(function (p, i) { return card(p, i === 0); }).join("") + "</div>" +
        '<div class="cluster" style="margin-top:18px"><a class="btn btn--ghost btn--sm" href="/products/compare/">さらに詳しく比較する</a></div>';
      resultBox.scrollIntoView({ behavior: "smooth", block: "start" });
    });

    var resetBtn2 = $("#finderReset");
    if (resetBtn2) resetBtn2.addEventListener("click", function () {
      answers = { use: null, budget: null, priority: null };
      Array.prototype.forEach.call(finder.querySelectorAll(".finder__opt"), function (b) { b.classList.remove("is-active"); });
      if (runBtn) runBtn.disabled = true;
      resultBox.innerHTML = "";
      var hint = $("#finderHint");
      if (hint) hint.textContent = "3つすべて選ぶと結果を表示します。";
    });
  }

  /* ---------------- 下取り査定(/store/trade-in/) ---------------- */
  var tradein = $("#tradeinTool");
  if (tradein) {
    var tYen = window.szFmt.yen;
    var tSel = $("#tradeinModel");
    var tRes = $("#tradeinResult");
    var tCond = 1;
    // 下取り対象 = スマホ/タブレットの全世代(現行・販売終了とも)
    var tItems = (SZ.products || []).filter(function (p) { return p.cat === "phone" || p.cat === "tablet"; })
      .sort(function (a, b) { return b.year - a.year || b.price - a.price; });
    tSel.innerHTML = '<option value="">選択してください</option>' + tItems.map(function (p) {
      return '<option value="' + esc(p.id) + '">' + esc(p.name) + "(" + p.year + "年)</option>";
    }).join("");

    function tEstimate() {
      var id = tSel.value;
      if (!id) { tRes.style.display = "none"; return; }
      var p = tItems.filter(function (x) { return x.id === id; })[0];
      if (!p) return;
      // 経年で残価率を減衰(当年60% → 毎年-12pt、下限12%)、状態係数を乗算
      var age = new Date().getFullYear() - p.year;
      var rate = Math.max(0.12, 0.6 - age * 0.12);
      var base = Math.round(p.price * rate * tCond / 100) * 100;
      tRes.style.display = "";
      tRes.innerHTML = '<svg class="ic" viewBox="0 0 24 24" aria-hidden="true"><path d="M12 3v12M7 10l5 5 5-5"/><path d="M5 21h14"/></svg> ' +
        "<strong>" + esc(p.name) + "</strong> の概算下取り額: <strong style='font-size:1.3em'>" + tYen(base) + "</strong>" +
        '<br><small class="t-faint">購入時クーポンとして還元されます(デモ用の概算です)。</small>';
    }
    tSel.addEventListener("change", tEstimate);
    var condBox = $("#tradeinCond");
    condBox.addEventListener("click", function (e) {
      var b = e.target.closest("[data-cond]");
      if (!b) return;
      tCond = parseFloat(b.getAttribute("data-cond"));
      Array.prototype.forEach.call(condBox.querySelectorAll("button"), function (x) { x.classList.toggle("is-active", x === b); });
      tEstimate();
    });
  }

  /* ---------------- ギフト提案(/store/gift/) ---------------- */
  var gift = $("#giftTool");
  if (gift) {
    var gYen = window.szFmt.yen;
    var gRes = $("#giftResult");
    gift.addEventListener("click", function (e) {
      var b = e.target.closest("[data-gift]");
      if (!b) return;
      Array.prototype.forEach.call(gift.querySelectorAll("[data-gift]"), function (x) { x.classList.toggle("is-active", x === b); });
      var budget = parseInt(b.getAttribute("data-gift"), 10);
      var picks = (SZ.products || []).filter(function (p) {
        return p.status === "current" && p.price <= budget && p.flag !== "limited";
      }).sort(function (a, b2) { return b2.price - a.price; }).slice(0, 3);
      gRes.innerHTML = picks.length
        ? '<div class="grid grid--3 grid--cards">' + picks.map(function (p) {
            return '<a class="product-card" href="' + esc(p.url) + '">' +
              '<div class="product-card__media"><img src="' + esc(p.img) + '" alt="' + esc(p.name) + '" loading="lazy" width="360" height="640"></div>' +
              '<div class="product-card__body"><p class="product-card__tag">' + esc(p.lineLabel) + "</p>" +
              '<p class="product-card__name">' + esc(p.name) + "</p>" +
              '<p class="product-card__price">' + gYen(p.price) + " <small>(税込)〜</small></p></div></a>";
          }).join("") + "</div>"
        : '<p class="t-soft">ご予算内の製品が見つかりませんでした。</p>';
    });
  }
})();
