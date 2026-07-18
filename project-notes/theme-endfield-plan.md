# サイトテーマ「前線」(endfield)追加手順書 — H-9-4 事前準備

作成: 2026-07-18(H-9-4)
状態: **着手待ち(参考資料待ち)**

## 0. 現状と着手条件

- `scripts/data_themes.py` に予約枠を登録済み:
  `{"id": "endfield", "status": "planned", "kind": "concrete", "label": "前線", "short": "前線"}`
- `status: "planned"` の間、このテーマは **CSS・UI・JS のどこにも出力されない**
  (validate.py の `check_themes()` が「planned に vars 等があれば NG」を機械検査、
  interact.js が「endfield ボタン非存在」を実地検証している)。
- ニュース告知は掲載済み: `/news/2026-07-endfield-site-theme/`(2026-07-18)。
- **着手条件**: エンドフィールドの参考資料(ゲーム内画像・UI スクリーンショット等)の
  提供を受けてから配色を決定する。**資料が届くまで vars を実装しないこと。**
  資料はフェーズ終了後にユーザーへ確認する(確認済みの合意事項)。

## 1. collab-endfield.css 流用禁止の理由(重要)

`assets/css/collab-endfield.css` は **コラボ特設 LP 専用のスコープ付き CSS** であり、
サイト全体テーマとは責務が別。流用してはならない(ユーザー指示)。

- 変数体系が別物: LP は `--cl-*` 系のローカル変数で、テーマ機構の
  `--bg / --surface / --text / --accent` 等(THEME_VAR_KEYS の16変数)とは互換がない。
- スコープが別物: LP の配色は `.cl-endfield` 配下だけで完結する演出用。
  サイトテーマは `[data-theme=endfield]` で **全ページの基礎トークンを上書き**する。
- 要求水準が別物: LP は暗背景前提の演出色だが、サイトテーマは全ページの本文・表・
  フォームで WCAG AA(本文 4.5:1 目安)を満たす必要がある(H-9-2 の磨き直し基準)。

よって実装は **data_themes.py への独立定義**として行う。LP と世界観(白×黒×
ビビッドイエロー、工業ターミナル)は共有してよいが、色値は AA 基準で新規に起こす。

## 2. 実装手順(資料到着後)

テーマ機構は単一ソース化済みのため、**編集するのは原則 data_themes.py の 1 dict のみ**。

1. `scripts/data_themes.py` の endfield 項目に以下を実装:
   - `status` を `"planned"` → `"live"` に変更
   - `swatch`(選択 UI の色見本)/ `meta`(theme-color)/ `color_scheme` を追加
   - `vars` に THEME_VAR_KEYS の16変数をすべて定義(欠落は validate が検出)
   - 必要に応じて `extra_vars`(`grad-flame` / `glow-*` 等。g / suzaku の項目を参照)
   - `desc`(任意。ドロップダウンの説明文)
2. `python3 scripts/gen.py` を実行 — これだけで以下がすべて自動反映される:
   - `assets/css/themes.css` に `[data-theme=endfield]` ブロック生成
   - ヘッダードロップダウン / ドロワー / 設定ページ(`<!--THEME_SEG-->`)にボタン追加
   - 早期適用スクリプト(`window.SZ_THEMES`)と meta theme-color 同期に組み込み
   - interact.js の「endfield ボタン非存在」テストは **live 化に合わせて削除または
     「存在する」側へ書き換えること**(そのままだと FAIL する。意図的な設計)
3. 続報ニュースを `scripts/data_misc.py` の NEWS に追加
   (「サイトテーマ『前線』提供開始」。告知記事 `2026-07-endfield-site-theme` からの
   リンク導線も検討)。

## 3. 配色決定の観点(資料到着後に埋める)

- ベース: エンドフィールド工業の設計言語(白×黒のブロック反転+ビビッドイエロー)。
  ダーク基調かライト基調かは資料を見て決定する(LP は暗基調だが、テーマとしては
  「計器パネル風の明部が多い配色」もあり得る)。
- コントラスト実測(H-9-2 と同じ手順): `text / text-soft / text-faint` を bg・surface
  に対して実測し、本文 4.5:1 / 補助 4.5:1 目安・装飾 3:1 を確認してから確定する。
- `accent-contrast`: ビビッドイエローを accent にする場合、白文字は AA を満たさない
  可能性が高い。暗色(例: 装甲の黒)を検討する。

## 4. 実装時チェックリスト

- [ ] data_themes.py: status=live / swatch / meta / color_scheme / vars 16変数
- [ ] `python3 scripts/selftest.py` 合格(validate の check_themes 含む)
- [ ] `node scripts/audit.js`(375px)+ `AUDIT_WIDTH=1440` の両幅で 0 件
- [ ] interact.js: endfield テストを live 前提へ更新して全 PASS
- [ ] `node scripts/shot.js` 等でテーマ適用スクショを撮り目視(ホーム / 製品 / 法務)
- [ ] ドロワー・設定ページでボタン7個の折返しを 375px で確認
- [ ] 続報ニュース追加+ホーム最新3件への自動反映確認
- [ ] README の「カラーテーマの単一ソース」章に endfield を追記
- [ ] 再生成の冪等性(2回生成で差分安定)+ 機密漏れ検査(wave2 相手名 0 件)
