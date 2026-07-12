/* 法人専用モデルの構成プレビュー(色/容量/カメラ+背面正面トグル)。
   一般ストア(store.js)のカート/SZ.products とは完全分離し、data-biz 要素だけを制御する。
   価格・画像パスは data 属性から自己完結で計算する(SZ.products 非依存)。 */
(function () {
  "use strict";
  var box = document.querySelector("[data-biz]");
  if (!box) return;

  var pid = box.getAttribute("data-biz");
  var base = parseInt(box.getAttribute("data-base"), 10) || 0;
  var v = box.getAttribute("data-v") ? "?v=" + box.getAttribute("data-v") : "";
  var colorIdx = 0;
  var view = "back";

  var img = document.getElementById("bizImage");
  var priceEl = document.getElementById("bizPrice");
  var colorName = document.getElementById("bizColorName");

  var all = function (sel) { return Array.prototype.slice.call(box.querySelectorAll(sel)); };

  function camless() {
    var r = box.querySelector("input[name=bizcam]:checked");
    return !!(r && r.value === "1"); // 1 = カメラレス(セキュア仕様=リア・フロントとも非搭載)
  }
  function storageDelta() {
    var r = box.querySelector("input[name=bizstorage]:checked");
    return r ? (parseInt(r.getAttribute("data-delta"), 10) || 0) : 0;
  }
  function backSrc() {
    return camless()
      ? "/assets/img/products/" + pid + "-nc-" + colorIdx + ".svg" + v
      : "/assets/img/products/" + pid + "-" + colorIdx + ".svg" + v;
  }
  function yen(n) { return "¥" + n.toLocaleString("ja-JP"); }

  function setView(next) {
    view = next;
    all("[data-bizview]").forEach(function (b) {
      var on = b.getAttribute("data-bizview") === view;
      b.classList.toggle("is-active", on);
      b.setAttribute("aria-pressed", on ? "true" : "false");
    });
  }

  function refresh() {
    if (img) {
      if (view === "front") {
        var fb = box.querySelector("[data-bizview=front]");
        // カメラレス構成は前面カメラも非搭載の正面ビューへ差し替える
        var front = fb ? (camless() && fb.getAttribute("data-front-nc-src")
          ? fb.getAttribute("data-front-nc-src") : fb.getAttribute("data-front-src")) : backSrc();
        img.src = front;
      } else {
        img.src = backSrc();
      }
    }
    if (priceEl) priceEl.textContent = yen(base + storageDelta());
  }

  all(".swatch").forEach(function (sw) {
    sw.addEventListener("click", function () {
      all(".swatch").forEach(function (s) { s.classList.remove("is-active"); s.setAttribute("aria-pressed", "false"); });
      sw.classList.add("is-active");
      sw.setAttribute("aria-pressed", "true");
      colorIdx = parseInt(sw.getAttribute("data-color-index"), 10) || 0;
      if (colorName) colorName.textContent = sw.getAttribute("title") || "";
      setView("back"); // 色を変えたら背面へ戻して差分を見せる
      refresh();
    });
  });

  all("[data-bizview]").forEach(function (btn) {
    btn.addEventListener("click", function () {
      setView(btn.getAttribute("data-bizview"));
      refresh();
    });
  });

  all("input[name=bizstorage], input[name=bizcam]").forEach(function (r) {
    r.addEventListener("change", function () {
      if (r.name === "bizcam") setView("back"); // カメラ構成を変えたら背面で差分表示
      refresh();
    });
  });

  refresh();
})();
