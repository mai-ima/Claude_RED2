# バックログ(未着手・将来対応メモ)

このファイルは今後対応予定のアイデアを残す内部メモ。`.vercelignore` で配信対象外。

## 方針: 過去データはコード内にアーカイブとして残す

コンテンツを大きく書き換える(例: 本文の大幅加筆、仕様の刷新)際は、**旧バージョンを
削除せずコード内にアーカイブとして保存する**。配信・表示には使わず、参照・復元用に残す。

- 実例: ニュース本文の加筆前(短い版)を `scripts/data_misc.py` の `NEWS_BODY_ARCHIVE`
  (id → {excerpt, body})として保存済み。gen.py からは未参照=非配信。
- 今後同種の書き換えを行う場合も、`*_ARCHIVE` 等の命名で旧データを併存させる。

## 第1弾コラボに「独自の冷却技術」を追加 — 完了(サイクルD)
- 対象: 第1弾コラボ4機種(七耀 / 残響 / 夜行 / 前線)。
- 実装: `scripts/data_collab.py` の `COLLAB_COOLING` に作品専用冷却を新規定義し、専用ページ
  `/collab/{slug}/cooling/`(`gen.py: build_collab_cooling_page`)を生成。各コラボLPに導線
  (`_cl_cooling`)、製品スペックの冷却名も専用へ、`/tech/cooling/` に相互リンク節を追加。
  - 七耀: 元素環 ELEMENT LOOP(循環ベイパー)
  - 残響: 共振鎖 RESONANCE CHAIN(既存LP既出を技術ページ化)
  - 夜行: 夜霧 NIGHT MIST(夜間撮影の発熱対策)
  - 前線: 機関 KIKAN(広温度域・密閉式の現場冷却)
- ステータス: **完了。標準の氷刃/旋風とは別設計として扱う。**

## 設計メモ: 二状態ページ(予告⇄発表の自動切替・サイクルG)

- 対象: `/collab/{slug}/tablet/`(4枚・フルLP付き)と第2弾ティザー4枚(発表演出のみ)。
- 仕組み: 同一URLに `data-reveal-stage="teaser"` と `data-reveal-stage="full"`(既定 hidden +
  aria-hidden)を両方描画し、`collab-core.js` が `data-until`(reveal_at)と実時刻を比較。
  ゼロ到達(または読込時に経過済み)で teaser を隠し full を表示、`body.is-revealed` を付与。
- ネタバレ防止: `<title>`/description には発表前情報のみ(価格は書かない)。selftest が
  二状態マーカーの存在と head への価格漏れを機械検査する。interact.js に切替の実地テストあり。
- カウントダウンUI: `data-since`(予告ニュース公開日時)→ reveal_at の経過割合を進捗リングで表示。
  残り24時間で `is-imminent`(グローパルス、reduced-motion では無効)。
- 第2弾の相手名の扱い(ユーザー承認により更新): **発表ステージ(data-reveal-stage="full")の
  中に限り、相手作品名・スタジオ名を記載してよい**(`data_collab.py` の `reveal` ブロック)。
  ティザー表示側・`<title>`/description・ハブ・ニュース・検索インデックスなど発表前の導線には
  引き続き出さない。発表第一報の機体名: 空洞 KUDO / 星軌 SEIKI / 結生 YUISEI / 彩歌 SAIKA。
  第2報(実LP化: 仕様・価格・専用シリコン)は reveal_at 経過後の次サイクルで実施する。

## H-2 の設計メモ(2026-07-17)

- **slug改名**: `next` 系は次回コラボのために空け、第2弾は `wave2{,-2,-3,-4}` へ改名済み。
  旧URLには meta refresh + noindex の転送ページを生成(`gen.py build_collab_redirects`)。
- **製品専用URL**: 発表済み枠は `reveal["url_slug"]`(zzz / hsr。第1弾と同じ作品名スラッグ)を持ち、
  `/collab/{url_slug}/` に発表フルLPの単独ページを生成(noindex・PAGES非登録)。
  ハブ/兄弟リンクは `data-reveal`+`data-reveal-href` で発表後に href 自動差替(main.js)。
  ティザーURLは発表後の再訪時に location.replace で専用URLへ転送(collab-core.js。
  視聴中にゼロ到達した場合はその場の切替演出を優先)。
  ※ href/転送先の属性値に zzz/hsr が発表前HTMLに含まれるのは「コード内記載OK」の
  承認範囲。表示テキスト・title/description には出さないことを漏れ検査で担保する。
- **ティザーアーカイブ**: `/collab/wave2{,-2}/teaser/`(noindex)。相手名は載せない。
  製品専用ページ末尾の小ボタン(.cl-minibtn)から導線。
- **仮SVG**: `svg_art.svg_prototype(pid, glow, label, kana, style)`。style=zzz / srail。
  量産版レンダリング(svg_phone の専用描画)が出来たら差し替える。
- **製品別FAQ**: `data_products.py PRODUCT_FAQ`(id→[(Q,A)])。product page で
  ライン別FAQより優先。第2報時にコラボアクセサリ追加分もここへ足す。
- **未使用アーカイブ**: 発表LPの旧・実機SVG呼び出し(svg_phone "kudo"/"seiki")は
  H-2-1 で仮SVGに置換した。実機デザイン確定時は svg_phone の _PHONE_CUSTOM に
  専用描画を実装して戻す。
