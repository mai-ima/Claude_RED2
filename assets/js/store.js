/* ==========================================================================
   SUZAKU store.js — カート / 製品構成 / ストア一覧 / チェックアウト / 注文照会 / 比較
   すべて localStorage で完結する実動作モック。
   ========================================================================== */
(function () {
  "use strict";

  var $ = function (sel, root) { return (root || document).querySelector(sel); };
  var $$ = function (sel, root) { return Array.prototype.slice.call((root || document).querySelectorAll(sel)); };
  var SZ = window.SZ || { products: [], tax: 0.1, freeShipping: 5000, shippingFee: 550 };

  /* 注文・修理の進行段階(管理ボードと照会画面で共有する単一ソース) */
  window.szStages = {
    order: ["ご注文受付", "お支払い確認", "出荷準備中", "出荷済み", "お届け完了"],
    repair: ["受付完了", "診断中", "修理作業中", "返送手配", "お届け完了"]
  };

  var yen = window.szFmt.yen;
  var esc = window.szFmt.esc;
  function productImg(pid, idx) {
    var v = (window.SZ && window.SZ.assetV) ? "?v=" + window.SZ.assetV : "";
    return "/assets/img/products/" + pid + "-" + idx + ".svg" + v;
  }
  function product(id) {
    return SZ.products.filter(function (p) { return p.id === id; })[0] || null;
  }
  function unitPrice(p, storageIdx) {
    var d = (p.storage && p.storage[storageIdx]) ? p.storage[storageIdx].delta : 0;
    return p.price + d;
  }

  /* ---------------- カート ---------------- */
  function getCart() { return window.szStore.get("sz_cart", []); }
  function setCart(c) { window.szStore.set("sz_cart", c); window.szUpdateCartBadge(); }

  function shopStopped() {
    var g = window.szStore.get("sz_global", {});
    return !!g.shopStop;
  }

  function addToCart(id, colorIdx, storageIdx, qty) {
    if (shopStopped()) {
      window.szToast("現在、ご購入の受付を停止しています。再開までお待ちください");
      return false;
    }
    var cart = getCart();
    var hit = cart.filter(function (x) {
      return x.id === id && x.color === colorIdx && x.storage === storageIdx;
    })[0];
    if (hit) hit.qty = Math.min(9, hit.qty + qty);
    else cart.push({ id: id, color: colorIdx, storage: storageIdx, qty: qty });
    setCart(cart);
    return true;
  }
  window.szAddToCart = addToCart;

  function cartTotals() {
    var cart = getCart();
    var sub = 0;
    cart.forEach(function (x) {
      var p = product(x.id);
      if (p) sub += unitPrice(p, x.storage) * x.qty;
    });
    // 管理ボードのストア設定(送料無料しきい値・配送料)があれば優先する
    var cfg = window.szStore.get("sz_store_cfg", {});
    var freeAt = typeof cfg.freeShipping === "number" ? cfg.freeShipping : SZ.freeShipping;
    var fee = typeof cfg.shippingFee === "number" ? cfg.shippingFee : SZ.shippingFee;
    var ship = sub === 0 || sub >= freeAt ? 0 : fee;
    return { sub: sub, ship: ship, total: sub + ship, count: cart.reduce(function (a, x) { return a + x.qty; }, 0), freeAt: freeAt };
  }

  /* ---------------- 製品ページ: 構成選択 ---------------- */
  var buyBox = $(".buy-grid[data-product]");
  if (buyBox) {
    var pid = buyBox.getAttribute("data-product");
    var p = product(pid);
    var colorIdx = 0;
    function storageIdx() {
      var r = buyBox.querySelector("input[name=storage]:checked");
      return r ? parseInt(r.value, 10) : 0;
    }
    var buyView = "back"; // 背面⇔正面トグル(正面はカラー共通の1枚)
    function camlessSelected() {
      var r = buyBox.querySelector("input[name=camopt]:checked");
      return r && r.value === "1"; // 1 = カメラレス(セキュア仕様)
    }
    function backImgSrc() {
      var v = (window.SZ && window.SZ.assetV) ? "?v=" + window.SZ.assetV : "";
      return camlessSelected()
        ? "/assets/img/products/" + pid + "-nc-" + colorIdx + ".svg" + v
        : productImg(pid, colorIdx);
    }
    function refresh() {
      if (!p) return;
      var img = $("#buyImage");
      if (img) {
        if (buyView === "front") {
          var fb = buyBox.querySelector("[data-buyview=front]");
          img.src = fb ? fb.getAttribute("data-front-src") : backImgSrc();
        } else {
          img.src = backImgSrc();
        }
      }
      var cn = $("#colorName");
      if (cn && p.colors[colorIdx]) cn.textContent = p.colors[colorIdx].name;
      var priceEl = $("#buyPrice");
      if (priceEl) priceEl.textContent = yen(unitPrice(p, storageIdx()));
    }
    $$("[data-buyview]", buyBox).forEach(function (btn) {
      btn.addEventListener("click", function () {
        buyView = btn.getAttribute("data-buyview");
        $$("[data-buyview]", buyBox).forEach(function (b) {
          var on = b === btn;
          b.classList.toggle("is-active", on);
          b.setAttribute("aria-pressed", on ? "true" : "false");
        });
        refresh();
      });
    });
    $$(".swatch", buyBox).forEach(function (sw) {
      sw.addEventListener("click", function () {
        $$(".swatch", buyBox).forEach(function (s) { s.classList.remove("is-active"); });
        sw.classList.add("is-active");
        colorIdx = parseInt(sw.getAttribute("data-color-index"), 10);
        buyView = "back"; // カラー選択時は背面に戻して色を見せる
        $$("[data-buyview]", buyBox).forEach(function (b) {
          var on = b.getAttribute("data-buyview") === "back";
          b.classList.toggle("is-active", on);
          b.setAttribute("aria-pressed", on ? "true" : "false");
        });
        refresh();
      });
    });
    $$("input[name=camopt]", buyBox).forEach(function (r) {
      r.addEventListener("change", function () {
        buyView = "back"; // 構成変更は背面(刻印の有無)を見せる
        $$("[data-buyview]", buyBox).forEach(function (b) {
          var on = b.getAttribute("data-buyview") === "back";
          b.classList.toggle("is-active", on);
          b.setAttribute("aria-pressed", on ? "true" : "false");
        });
        refresh();
      });
    });
    $$("input[name=storage]", buyBox).forEach(function (r) {
      r.addEventListener("change", refresh);
    });
    var addBtn = $("#addToCart");
    if (addBtn) {
      addBtn.addEventListener("click", function () {
        if (addToCart(pid, colorIdx, storageIdx(), 1)) window.szToast(p.name + " をカートに追加しました");
      });
    }
    refresh();
  }

  /* ---------------- ストア一覧 ---------------- */
  var storeGrid = $("#storeGrid");
  if (storeGrid) {
    var cat = "all";
    var sort = "featured";
    function storeCard(p) {
      var badge = p.flag === "new" ? '<span class="badge badge--new">NEW</span>' : "";
      return '<div class="product-card">' +
        '<a class="product-card__media" href="' + p.url + '" aria-label="' + p.name + '"><img src="' + p.img + '" alt="' + p.name + '" loading="lazy"></a>' +
        '<div class="product-card__body">' +
        '<p class="product-card__tag">' + p.lineLabel + " / " + p.year + "</p>" +
        '<p class="product-card__name">' + p.name + " " + badge + "</p>" +
        '<p class="product-card__copy">' + p.tagline + "</p>" +
        '<p class="product-card__price">' + yen(p.price) + ' <small>(税込)〜</small></p>' +
        '<div class="cluster" style="margin-top:6px">' +
        '<button class="btn btn--primary btn--sm" data-quick-add="' + p.id + '">カートに追加</button>' +
        '<a class="btn btn--ghost btn--sm" href="' + p.url + '">詳細</a>' +
        "</div></div></div>";
    }
    function renderStore() {
      var items = SZ.products.filter(function (p) { return p.status === "current"; });
      if (cat !== "all") items = items.filter(function (p) { return p.cat === cat; });
      if (sort === "price-asc") items.sort(function (a, b) { return a.price - b.price; });
      else if (sort === "price-desc") items.sort(function (a, b) { return b.price - a.price; });
      else if (sort === "new") items.sort(function (a, b) { return b.year - a.year; });
      else items.sort(function (a, b) { return (b.flag === "new") - (a.flag === "new") || b.price - a.price; });
      storeGrid.innerHTML = items.map(storeCard).join("");
      var count = $("#storeCount");
      if (count) count.textContent = items.length + "件の製品";
    }
    $$("#storeTabs .tab").forEach(function (tab) {
      tab.addEventListener("click", function () {
        $$("#storeTabs .tab").forEach(function (t) { t.classList.remove("is-active"); });
        tab.classList.add("is-active");
        cat = tab.getAttribute("data-cat");
        renderStore();
      });
    });
    var sortSel = $("#storeSort");
    if (sortSel) sortSel.addEventListener("change", function () { sort = sortSel.value; renderStore(); });
    document.addEventListener("click", function (e) {
      var btn = e.target.closest("[data-quick-add]");
      if (!btn) return;
      var p = product(btn.getAttribute("data-quick-add"));
      if (addToCart(p.id, 0, 0, 1)) window.szToast(p.name + " をカートに追加しました");
    });
    renderStore();
  }

  /* ---------------- カートページ ---------------- */
  var cartList = $("#cartList");
  if (cartList) {
    function renderCart() {
      var cart = getCart();
      var t = cartTotals();
      if (!cart.length) {
        cartList.innerHTML = '<div class="empty"><p class="empty__icon"><svg class="ic" viewBox="0 0 24 24" aria-hidden="true"><path d="M6 7h13l-1.5 9h-10z"/><path d="M6 7L5 4H2.5"/><circle cx="9" cy="20" r="1.6"/><circle cx="16" cy="20" r="1.6"/></svg></p><p>カートは空です。</p><a class="btn btn--primary" href="/store/">ストアで製品を見る</a></div>';
      } else {
        cartList.innerHTML = cart.map(function (x, i) {
          var p = product(x.id);
          if (!p) return "";
          var conf = [];
          if (p.colors[x.color]) conf.push(p.colors[x.color].name);
          if (p.storage && p.storage[x.storage]) conf.push(p.storage[x.storage].label);
          return '<div class="cart-line">' +
            '<a class="cart-line__thumb" href="' + p.url + '"><img src="' + productImg(p.id, x.color || 0) + '" alt=""></a>' +
            '<div class="stack" style="gap:4px">' +
            '<p style="font-weight:800;color:var(--text-strong)">' + p.name + "</p>" +
            '<p class="t-micro t-faint">' + (conf.join(" / ") || "標準構成") + "</p>" +
            '<button class="cart-line__remove" data-remove="' + i + '" style="justify-self:start">削除</button>' +
            "</div>" +
            '<div class="stack" style="gap:8px;justify-items:end">' +
            '<p style="font-weight:800;color:var(--text-strong)">' + yen(unitPrice(p, x.storage) * x.qty) + "</p>" +
            '<div class="qty"><button data-qty="' + i + ':-1" aria-label="数量を減らす">−</button><output>' + x.qty + '</output><button data-qty="' + i + ':1" aria-label="数量を増やす">+</button></div>' +
            "</div></div>";
        }).join("");
      }
      var box = $("#cartSummary");
      if (box) {
        var maintC = window.szStore.get("sz_maintenance", { on: false });
        var paused = maintC.on || shopStopped();
        var pausedNote = paused
          ? '<div class="notice" style="margin-bottom:14px"><svg class="ic" viewBox="0 0 24 24" aria-hidden="true"><path d="M14.5 6.5a4 4 0 0 0-5.6 5L4 16.4V20h3.6l4.9-4.9a4 4 0 0 0 5-5.6L15 12l-3-3z"/></svg> <span>' +
            (maintC.on ? "メンテナンス中のため、ただいまご注文いただけません。" : "ただいまご注文の受付を停止しています。") +
            "カートの中身は保存されます。</span></div>"
          : "";
        var checkoutBtn = paused
          ? '<button class="btn btn--primary btn--block" disabled>ただいま購入いただけません</button>'
          : (t.count ? '<a class="btn btn--primary btn--block" href="/store/checkout/">レジに進む</a>' : '<button class="btn btn--primary btn--block" disabled>レジに進む</button>');
        box.innerHTML =
          '<h2 class="t-h4">ご注文内容</h2>' + pausedNote +
          '<div class="summary-box__row"><span>小計(税込)</span><span>' + yen(t.sub) + "</span></div>" +
          '<div class="summary-box__row"><span>配送料</span><span>' + (t.ship ? yen(t.ship) : "無料") + "</span></div>" +
          '<div class="summary-box__row summary-box__row--total"><span>合計</span><span>' + yen(t.total) + "</span></div>" +
          '<p class="t-micro t-faint">合計金額には消費税10%が含まれています。' + (t.ship ? "あと" + yen(t.freeAt - t.sub) + "で送料無料。" : "") + "</p>" +
          checkoutBtn +
          '<a class="btn btn--ghost btn--block" href="/store/">買い物を続ける</a>';
      }
    }
    cartList.addEventListener("click", function (e) {
      var rm = e.target.closest("[data-remove]");
      var qb = e.target.closest("[data-qty]");
      var cart = getCart();
      if (rm) {
        cart.splice(parseInt(rm.getAttribute("data-remove"), 10), 1);
        setCart(cart); renderCart();
      } else if (qb) {
        var parts = qb.getAttribute("data-qty").split(":");
        var item = cart[parseInt(parts[0], 10)];
        if (item) {
          item.qty = Math.max(1, Math.min(9, item.qty + parseInt(parts[1], 10)));
          setCart(cart); renderCart();
        }
      }
    });
    renderCart();
  }

  /* ---------------- チェックアウト ---------------- */
  var checkout = $("#checkout");
  if (checkout) {
    var stepIdx = 0;
    var order = { customer: {}, shipping: {}, payment: {} };
    var stepsEl = $$("#checkoutSteps li");
    var panels = $$(".checkout-panel");

    var t0 = cartTotals();
    if (t0.count === 0) {
      checkout.innerHTML = '<div class="empty"><p class="empty__icon"><svg class="ic" viewBox="0 0 24 24" aria-hidden="true"><path d="M6 7h13l-1.5 9h-10z"/><path d="M6 7L5 4H2.5"/><circle cx="9" cy="20" r="1.6"/><circle cx="16" cy="20" r="1.6"/></svg></p><p>カートが空のため、チェックアウトに進めません。</p><a class="btn btn--primary" href="/store/">ストアへ戻る</a></div>';
      return;
    }

    /* 購入受付が停止中(メンテナンス/購入停止)なら、情報入力の前に手続き自体を止めて
       案内する。最後まで入力させてから弾く不親切さを避けるための先出しガード。 */
    var maint0 = window.szStore.get("sz_maintenance", { on: false });
    if (maint0.on || shopStopped()) {
      var isMaint = !!maint0.on;
      checkout.innerHTML = '<div class="empty">' +
        '<p class="empty__icon"><svg class="ic" viewBox="0 0 24 24" aria-hidden="true"><path d="M14.5 6.5a4 4 0 0 0-5.6 5L4 16.4V20h3.6l4.9-4.9a4 4 0 0 0 5-5.6L15 12l-3-3z"/></svg></p>' +
        '<p><strong>' + (isMaint ? "ただいまメンテナンス中のため、ご注文を一時停止しています。" : "ただいまご注文の受付を一時停止しています。") + "</strong></p>" +
        (isMaint && maint0.msg ? '<p class="t-small t-soft">' + esc(maint0.msg) + "</p>" : "") +
        '<p class="t-small t-soft">カートの中身はそのまま保存されます。再開後にあらためてお手続きください。ご不便をおかけして申し訳ありません。</p>' +
        '<div class="cluster cluster--center" style="margin-top:8px"><a class="btn btn--primary" href="/store/cart/">カートを見る</a><a class="btn btn--ghost" href="/maintenance/">稼働状況を見る</a></div>' +
        "</div>";
      return;
    }

    function goto(i) {
      stepIdx = i;
      stepsEl.forEach(function (li, k) {
        li.classList.toggle("is-current", k === i);
        li.classList.toggle("is-done", k < i);
      });
      panels.forEach(function (pn, k) { pn.classList.toggle("is-active", k === i); });
      window.scrollTo({ top: 0, behavior: "smooth" });
      if (i === 3) renderConfirm();
    }

    function fieldError(input, msg) {
      var field = input.closest(".field");
      if (!field) return;
      field.classList.toggle("has-error", !!msg);
      var err = field.querySelector(".field__error");
      if (err && msg) err.textContent = msg;
    }
    function validatePanel(panel) {
      var ok = true;
      $$("input[required], select[required], textarea[required]", panel).forEach(function (inp) {
        if (inp.offsetParent === null && inp.type !== "radio") return; // 非表示はスキップ
        var v = inp.value.trim();
        var msg = "";
        if (!v) msg = "入力してください";
        else if (inp.type === "email" && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(v)) msg = "メールアドレスの形式が正しくありません";
        else if (inp.dataset.kind === "tel" && !/^0\d{9,10}$/.test(v.replace(/[-\s]/g, ""))) msg = "電話番号の形式が正しくありません(例: 09012345678)";
        else if (inp.dataset.kind === "postal" && !/^\d{3}-?\d{4}$/.test(v)) msg = "郵便番号は 123-4567 の形式で入力してください";
        if (msg) ok = false;
        fieldError(inp, msg);
      });
      return ok;
    }

    /* クレジットカード */
    function luhn(num) {
      var s = 0, alt = false;
      for (var i = num.length - 1; i >= 0; i--) {
        var d = parseInt(num[i], 10);
        if (alt) { d *= 2; if (d > 9) d -= 9; }
        s += d; alt = !alt;
      }
      return s % 10 === 0;
    }
    var ccNum = $("#ccNumber");
    if (ccNum) {
      ccNum.addEventListener("input", function () {
        var v = ccNum.value.replace(/\D/g, "").slice(0, 16);
        ccNum.value = v.replace(/(.{4})/g, "$1 ").trim();
      });
    }
    var ccExp = $("#ccExpiry");
    if (ccExp) {
      ccExp.addEventListener("input", function () {
        var v = ccExp.value.replace(/\D/g, "").slice(0, 4);
        ccExp.value = v.length > 2 ? v.slice(0, 2) + "/" + v.slice(2) : v;
      });
    }
    function validateCard() {
      var ok = true;
      var num = ccNum.value.replace(/\s/g, "");
      if (!/^\d{14,16}$/.test(num) || !luhn(num)) { fieldError(ccNum, "カード番号が正しくありません"); ok = false; }
      else fieldError(ccNum, "");
      var m = ccExp.value.match(/^(\d{2})\/(\d{2})$/);
      var expOk = false;
      if (m) {
        var mm = parseInt(m[1], 10), yy = 2000 + parseInt(m[2], 10);
        expOk = mm >= 1 && mm <= 12 && (yy > 2026 || (yy === 2026 && mm >= 7));
      }
      if (!expOk) { fieldError(ccExp, "有効期限が正しくありません(MM/YY)"); ok = false; }
      else fieldError(ccExp, "");
      var cvv = $("#ccCvv");
      if (!/^\d{3,4}$/.test(cvv.value)) { fieldError(cvv, "セキュリティコードは3〜4桁です"); ok = false; }
      else fieldError(cvv, "");
      var nm = $("#ccName");
      if (!nm.value.trim()) { fieldError(nm, "入力してください"); ok = false; }
      else fieldError(nm, "");
      return ok;
    }

    function payMethod() {
      var r = checkout.querySelector("input[name=payMethod]:checked");
      return r ? r.value : "card";
    }
    $$("input[name=payMethod]", checkout).forEach(function (r) {
      r.addEventListener("change", function () {
        var cardBox = $("#cardFields");
        if (cardBox) cardBox.hidden = payMethod() !== "card";
        var instBox = $("#installmentBox");
        if (instBox) instBox.hidden = payMethod() !== "card";
      });
    });

    function payLabel() {
      var map = {
        card: "クレジットカード",
        cvs: "コンビニ払い(払込票)",
        cod: "代金引換(手数料 ¥330)"
      };
      var label = map[payMethod()];
      if (payMethod() === "card") {
        var inst = $("#installments");
        var n = inst ? inst.value : "1";
        label += n === "1" ? "(一括払い)" : "(" + n + "回分割)";
      }
      return label;
    }

    function renderConfirm() {
      var t = cartTotals();
      var cod = payMethod() === "cod" ? 330 : 0;
      var cart = getCart();
      var lines = cart.map(function (x) {
        var p = product(x.id);
        var conf = [];
        if (p.colors[x.color]) conf.push(p.colors[x.color].name);
        if (p.storage && p.storage[x.storage]) conf.push(p.storage[x.storage].label);
        return "<div class='summary-box__row'><span>" + p.name + (conf.length ? "(" + conf.join("/") + ")" : "") + " × " + x.qty + "</span><span>" + yen(unitPrice(p, x.storage) * x.qty) + "</span></div>";
      }).join("");
      var c = order.customer, s = order.shipping;
      $("#confirmBox").innerHTML =
        '<h3 class="t-h4">ご注文商品</h3>' + lines +
        '<div class="summary-box__row"><span>配送料</span><span>' + (t.ship ? yen(t.ship) : "無料") + "</span></div>" +
        (cod ? '<div class="summary-box__row"><span>代引手数料</span><span>' + yen(cod) + "</span></div>" : "") +
        '<div class="summary-box__row summary-box__row--total"><span>合計(税込)</span><span>' + yen(t.total + cod) + "</span></div>" +
        '<hr class="divider">' +
        '<h3 class="t-h4">お届け先</h3>' +
        "<p class='t-small'>〒" + c.postal + " " + c.address + "<br>" + c.name + " 様 / " + c.tel + "<br>" + c.email + "</p>" +
        '<h3 class="t-h4">配送方法</h3>' +
        "<p class='t-small'>" + s.method + " / お届け希望: " + s.date + " " + s.time + "</p>" +
        '<h3 class="t-h4">お支払い方法</h3>' +
        "<p class='t-small'>" + payLabel() + "</p>";
    }

    $$("[data-step-next]").forEach(function (btn) {
      btn.addEventListener("click", function () {
        var panel = panels[stepIdx];
        if (!validatePanel(panel)) { window.szToast("入力内容をご確認ください"); return; }
        if (stepIdx === 0) {
          order.customer = {
            name: $("#coName").value.trim(),
            postal: $("#coPostal").value.trim(),
            address: $("#coAddress").value.trim(),
            tel: $("#coTel").value.trim(),
            email: $("#coEmail").value.trim()
          };
        } else if (stepIdx === 1) {
          order.shipping = {
            method: checkout.querySelector("input[name=shipMethod]:checked").value,
            date: $("#shipDate").value || "指定なし",
            time: $("#shipTime").value
          };
        } else if (stepIdx === 2) {
          if (payMethod() === "card" && !validateCard()) { window.szToast("カード情報をご確認ください"); return; }
        }
        goto(stepIdx + 1);
      });
    });
    $$("[data-step-back]").forEach(function (btn) {
      btn.addEventListener("click", function () { goto(Math.max(0, stepIdx - 1)); });
    });

    var placeBtn = $("#placeOrder");
    if (placeBtn) {
      placeBtn.addEventListener("click", function () {
        var maint = window.szStore.get("sz_maintenance", { on: false });
        if (maint.on) {
          window.szToast("メンテナンス中のため、ご注文を一時停止しています");
          return;
        }
        if (shopStopped()) {
          window.szToast("現在、ご注文の受付を停止しています。再開までお待ちください");
          return;
        }
        var agree = $("#agreeTerms");
        if (agree && !agree.checked) { window.szToast("利用規約と販売条件への同意が必要です"); return; }
        placeBtn.disabled = true;
        placeBtn.innerHTML = '<span class="spinner"></span> 注文を処理しています…';
        setTimeout(function () {
          var t = cartTotals();
          var cod = payMethod() === "cod" ? 330 : 0;
          var no = "SZ-" + new Date().getFullYear() + "-" + String(Math.floor(100000 + Math.random() * 900000));
          var orders = window.szStore.get("sz_orders", []);
          orders.unshift({
            no: no,
            date: new Date().toISOString(),
            items: getCart(),
            total: t.total + cod,
            pay: payLabel(),
            customer: order.customer,
            shipping: order.shipping,
            status: "受付完了"
          });
          window.szStore.set("sz_orders", orders);
          setCart([]);
          $("#orderNumber").textContent = no;
          $("#orderEmail").textContent = order.customer.email;
          goto(4);
        }, 1400);
      });
    }

    /* 配送日の選択肢(明後日〜14日後)を生成 */
    var shipDate = $("#shipDate");
    if (shipDate) {
      var days = ["日", "月", "火", "水", "木", "金", "土"];
      for (var d = 2; d <= 14; d++) {
        var dt = new Date();
        dt.setDate(dt.getDate() + d);
        var opt = document.createElement("option");
        opt.value = (dt.getMonth() + 1) + "月" + dt.getDate() + "日(" + days[dt.getDay()] + ")";
        opt.textContent = opt.value;
        shipDate.appendChild(opt);
      }
    }
    goto(0);
  }

  /* ---------------- 注文照会 ---------------- */
  var orderLookup = $("#orderLookupForm");
  if (orderLookup) {
    orderLookup.addEventListener("submit", function (e) {
      e.preventDefault();
      var no = $("#orderNo").value.trim().toUpperCase();
      var orders = window.szStore.get("sz_orders", []);
      var hit = orders.filter(function (o) { return o.no === no; })[0];
      var box = $("#orderResult");
      if (!hit) {
        box.innerHTML = '<div class="notice"><svg class="ic" viewBox="0 0 24 24" aria-hidden="true"><path d="M12 4l9 16H3z"/><path d="M12 10.5v4M12 17.6h.01"/></svg> 注文番号「' + no.replace(/[<>&"]/g, "") + '」は見つかりませんでした。この端末で行われたご注文のみ照会できます(デモ仕様)。</div>';
        return;
      }
      var placed = new Date(hit.date);
      var hours = (Date.now() - placed.getTime()) / 36e5;
      var stages = window.szStages.order;
      /* 管理ボードで明示的にステータスを設定していればそれを優先。
         未設定なら経過時間から推定する(デモの自動進行)。 */
      var reached = typeof hit.statusIdx === "number"
        ? hit.statusIdx
        : (hours > 96 ? 4 : hours > 36 ? 3 : hours > 12 ? 2 : hours > 0.01 ? 1 : 0);
      if (hit.cancelled) {
        box.innerHTML = '<div class="card" style="margin-top:24px"><p class="eyebrow">注文番号 ' + hit.no + "</p>" +
          '<div class="notice"><svg class="ic" viewBox="0 0 24 24" aria-hidden="true"><path d="M12 4l9 16H3z"/><path d="M12 10.5v4M12 17.6h.01"/></svg> このご注文はキャンセルされました。ご不明な点は<a href="/support/contact/">お問い合わせ</a>ください。</div></div>';
        return;
      }
      var timeline = stages.map(function (t, i) {
        return '<li class="' + (i <= reached ? "is-done" : "") + '"><span>' + t + "</span></li>";
      }).join("");
      var items = hit.items.map(function (x) {
        var p = product(x.id);
        return "<li>" + (p ? p.name : x.id) + " × " + x.qty + "</li>";
      }).join("");
      box.innerHTML =
        '<div class="card" style="margin-top:24px">' +
        '<p class="eyebrow">注文番号 ' + hit.no + "</p>" +
        '<p class="t-small t-soft">注文日時: ' + placed.toLocaleString("ja-JP") + " / お支払い: " + hit.pay +
        ' / 現在の状況: <strong style="color:var(--accent)">' + stages[reached] + "</strong></p>" +
        '<ol class="order-track">' + timeline + "</ol>" +
        '<h3 class="t-h4">ご注文商品</h3><ul class="t-small t-soft" style="display:grid;gap:4px">' + items + "</ul>" +
        '<p class="summary-box__row summary-box__row--total"><span>合計(税込)</span><span>' + yen(hit.total) + "</span></p>" +
        "</div>";
    });
  }

  /* ---------------- 比較ツール ---------------- */
  var compare = $("#compareTool");
  if (compare) {
    var devices = SZ.products.filter(function (p) { return p.cmp; });
    var sels = $$(".compare-select", compare);
    var defaults = ["suzaku-4", "neo-3", "tsubame-3"];
    sels.forEach(function (sel, i) {
      sel.innerHTML = '<option value="">— 機種を選択 —</option>' + devices.map(function (p) {
        return '<option value="' + p.id + '">' + p.name + "(" + p.year + ")</option>";
      }).join("");
      sel.value = defaults[i] || "";
      sel.addEventListener("change", renderCompare);
    });
    // プリセット(ワンタップで機種セット)
    $$("#comparePresets .cmp-preset").forEach(function (btn) {
      btn.addEventListener("click", function () {
        var ids = (btn.getAttribute("data-preset") || "").split(",");
        sels.forEach(function (s, i) { s.value = ids[i] || ""; });
        renderCompare();
        var res = $("#compareDash");
        if (res && res.scrollIntoView) res.scrollIntoView({ behavior: "smooth", block: "start" });
      });
    });

    var ROWS = ["発売日", "価格", "ディスプレイ", "リフレッシュレート", "常時表示(AOD)", "SoC", "AnTuTu", "GPU", "メモリ", "ストレージ", "冷却方式", "バッテリー", "急速充電", "リアカメラ", "背面演出", "防塵防水", "重量", "OS更新", "OS"];
    // 数値比較する行と方向(high=大きいほど良い / low=小さいほど良い)+差分の単位
    var NUM = {
      "価格": { dir: "low", u: "円" }, "リフレッシュレート": { dir: "high", u: "Hz" },
      "AnTuTu": { dir: "high", u: "万点" }, "バッテリー": { dir: "high", u: "mAh" },
      "急速充電": { dir: "high", u: "W" }, "重量": { dir: "low", u: "g" }
    };
    var METRICS = [
      { key: "30分後fps維持率", u: "%", dir: "high" },
      { key: "タッチ遅延(推定)", u: "ms", dir: "low" },
      { key: "0→50%充電(推定)", u: "分", dir: "low" },
      { key: "コスパ(1万円あたり)", u: "万点", dir: "high" }
    ];
    function pnum(s) { var m = String(s == null ? "" : s).replace(/,/g, "").match(/-?\d+(\.\d+)?/); return m ? parseFloat(m[0]) : null; }
    function fmtNum(n) { return n.toLocaleString("ja-JP"); }
    function bestOf(vals, dir) {
      var nums = vals.filter(function (v) { return v != null; });
      if (!nums.length) return null;
      return dir === "low" ? Math.min.apply(null, nums) : Math.max.apply(null, nums);
    }
    function assetV() { return (window.SZ && window.SZ.assetV) ? "?v=" + window.SZ.assetV : ""; }

    function renderDash(chosen) {
      var box = $("#compareDash");
      if (!box) return;
      var rows = METRICS.map(function (m) {
        var vals = chosen.map(function (p) {
          var d = (p.dash || []).filter(function (x) { return x.key === m.key; })[0];
          return d ? d.v : null;
        });
        var best = bestOf(vals, m.dir);
        var maxv = Math.max.apply(null, vals.map(function (v) { return v == null ? 0 : v; }).concat([0.0001]));
        var minv = bestOf(vals, "low");
        var bars = chosen.map(function (p, i) {
          var v = vals[i];
          if (v == null) return '<div class="cmp-bar cmp-bar--na"><span class="cmp-bar__name">' + p.name + '</span><span class="cmp-bar__val">—</span></div>';
          // 幅: high は最大値基準、low は最小値/自分(小さいほど満杯)
          var w = m.dir === "low" ? (minv / v) : (v / maxv);
          var isBest = v === best;
          return '<div class="cmp-bar' + (isBest ? " is-best" : "") + '">'
            + '<span class="cmp-bar__name">' + p.name + (isBest ? ' <svg class="cmp-crown" viewBox="0 0 24 24" width="14" height="14" aria-label="最良値" role="img"><path d="M3 8l4.5 3.5L12 4l4.5 7.5L21 8l-1.6 10.5H4.6z" fill="currentColor"/></svg>' : '') + '</span>'
            + '<span class="cmp-bar__track"><span class="cmp-bar__fill" style="width:' + Math.max(6, Math.round(w * 100)) + '%"></span></span>'
            + '<span class="cmp-bar__val">' + fmtNum(v) + m.u + '</span></div>';
        }).join("");
        var hint = m.dir === "low" ? "小さいほど良い" : "大きいほど良い";
        return '<div class="cmp-metric"><div class="cmp-metric__head"><h4 class="t-h4">' + m.key + '</h4><span class="t-micro t-faint">' + hint + '</span></div><div class="cmp-metric__bars">' + bars + '</div></div>';
      }).join("");
      box.innerHTML = '<div class="cmp-dash">' + rows + '</div>';
    }

    function renderCompare() {
      var chosen = sels.map(function (s) { return product(s.value); }).filter(Boolean);
      var box = $("#compareResult");
      var dashBox = $("#compareDash");
      if (chosen.length < 2) {
        box.innerHTML = '<div class="empty"><p>2機種以上を選択すると比較表が表示されます。</p></div>';
        if (dashBox) dashBox.innerHTML = "";
        var rb0 = $("#compareRadar"); if (rb0) rb0.hidden = true;
        return;
      }
      renderDash(chosen);

      var head = '<tr><th scope="col" class="cmp-rowhead"></th>' + chosen.map(function (p) {
        return '<th scope="col"><a href="' + p.url + '" style="color:var(--accent)">' + p.name + "</a></th>";
      }).join("") + "</tr>";
      // 正面+背面の2段サムネ
      var v = assetV();
      var imgs = '<tr><th scope="row" class="cmp-rowhead">正面 / 背面</th>' + chosen.map(function (p) {
        return '<td><div class="cmp-thumbs">'
          + '<img src="/assets/img/products/' + p.id + '-front.svg' + v + '" alt="' + p.name + ' 正面" loading="lazy">'
          + '<img src="/assets/img/products/' + p.id + '-0.svg' + v + '" alt="' + p.name + ' 背面" loading="lazy">'
          + '</div></td>';
      }).join("") + "</tr>";

      var rows = ROWS.map(function (key) {
        var meta = NUM[key];
        var best = null;
        if (meta) best = bestOf(chosen.map(function (p) { return pnum(p.cmp[key]); }), meta.dir);
        var cells = chosen.map(function (p) {
          var raw = p.cmp[key] || "—";
          if (!meta) return "<td>" + raw + "</td>";
          var n = pnum(p.cmp[key]);
          if (n == null) return "<td>" + raw + "</td>";
          var isBest = (n === best);
          var diff = "";
          if (!isBest && best != null) {
            var d = n - best;
            var sign = d > 0 ? "+" : "−";
            diff = '<span class="cmp-diff">' + sign + fmtNum(Math.abs(d)) + meta.u + '</span>';
          }
          return '<td class="' + (isBest ? "cmp-best" : "") + '">' + raw + (isBest ? ' <svg class="cmp-crown" viewBox="0 0 24 24" width="14" height="14" aria-label="最良値" role="img"><path d="M3 8l4.5 3.5L12 4l4.5 7.5L21 8l-1.6 10.5H4.6z" fill="currentColor"/></svg>' : diff) + "</td>";
        }).join("");
        return '<tr><th scope="row" class="cmp-rowhead">' + key + "</th>" + cells + "</tr>";
      }).join("");
      box.innerHTML = '<div class="scroll-x"><table class="spec-table compare-table"><thead>' + head + "</thead><tbody>" + imgs + rows + "</tbody></table></div>";

      // 5軸レーダーチャートで重ね比較
      var radarBox = $("#compareRadar");
      if (radarBox && window.szCharts) {
        var series = chosen.filter(function (p) { return p.radar; }).map(function (p) {
          return { name: p.name, values: p.radar };
        });
        if (series.length >= 1) {
          radarBox.hidden = false;
          window.szCharts.renderInto(radarBox, {
            type: "radar",
            title: "性能バランス比較(5軸・当社評価)",
            axes: ["性能", "カメラ", "バッテリー", "冷却", "コスパ"],
            series: series
          });
        } else {
          radarBox.hidden = true;
        }
      }
    }
    renderCompare();
  }

  /* ---------------- フローティング購入バー + ローカルナビ(製品ページ) ---------------- */
  var buyFloat = $("#buyFloat");
  var localnav = $("#localnav");
  if (buyFloat || localnav) {
    var buySection = $("#buy");
    var heroSection = $(".hero");
    var onScrollFloat = function () {
      if (buyFloat && buySection) {
        var show = buySection.getBoundingClientRect().bottom < 0;
        buyFloat.classList.toggle("is-visible", show);
        buyFloat.setAttribute("aria-hidden", String(!show));
      }
      if (localnav && heroSection) {
        var showNav = heroSection.getBoundingClientRect().bottom < 70;
        localnav.classList.toggle("is-visible", showNav);
        localnav.setAttribute("aria-hidden", String(!showNav));
      }
    };
    window.addEventListener("scroll", onScrollFloat, { passive: true });
    onScrollFloat();
  }
})();
