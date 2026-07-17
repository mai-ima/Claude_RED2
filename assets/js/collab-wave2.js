/* ==========================================================================
   SUZAKU collab-wave2.js — 第2弾ティザーの「???」グリッチ明滅のみ
   ========================================================================== */
(function () {
  "use strict";
  var el = document.querySelector("[data-nx-glitch]");
  if (!el) return;
  if (window.matchMedia("(prefers-reduced-motion: reduce)").matches) return;
  var frames = ["???", "??¿", "?■?", "¿??", "???", "#??", "???"];
  var i = 0;
  setInterval(function () {
    // ほとんどの時間は「???」のまま、たまに一瞬乱れる
    if (Math.random() < 0.82) { el.textContent = "???"; return; }
    i = (i + 1) % frames.length;
    el.textContent = frames[i];
    setTimeout(function () { el.textContent = "???"; }, 90);
  }, 700);
})();
