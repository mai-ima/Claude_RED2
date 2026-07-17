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
- 第2弾の正式発表時の手順: 相手名解禁後は、ティザーの full ステージを本物の発表LPに差し替える
  (現在は名前なしの REVEALED 演出)。相手名はそれまでリポジトリのどこにも書かない。
