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

## H-9 の設計メモ(2026-07-18)— テーマ/Cookie刷新・endfield予約枠・機能台帳

- **テーマシステム v3(H-9-1/2)**: 定義を `data_themes.py` に単一ソース化し、
  `gen.py write_themes_css()` が `assets/css/themes.css` を自動生成(ASSET_V 計算より
  先に書き出す順序制約あり)。`auto`(ページ既定)に加え `system`(OS連動)を新設。
  早期適用スクリプト(`window.SZ_THEMES`)で FOUC と meta theme-color を描画前に解決。
  磨き直しは WCAG AA 実測に基づく最小修正のみ(light/dark の text-faint)。
- **Cookie同意 v3(H-9-3)**: `data_consent.py` に CONSENT_VERSION=3 と4カテゴリ
  (必須/機能/分析/マーケティング)。保存形式 `{version, date, choices}`。旧v2は読み取り
  正規化しつつ、**版不一致でバナー再表示=意図的な再同意**。機能Cookie拒否時は
  テーマ・表示設定を適用のみ(保存スキップ+トースト)。撤回ボタンあり。
- **endfield テーマ予約枠(H-9-4)**: `data_themes.py` に `status:"planned"` の枠のみ。
  planned は CSS/UI/JS へ一切出力されず、validate(vars 持ち込み NG)と
  interact(ボタン非存在)が機械担保。実装手順は `theme-endfield-plan.md`
  (**collab-endfield.css 流用禁止**・参考資料待ち。資料はフェーズ終了後にユーザーへ確認)。
  ニュース告知 `/news/2026-07-endfield-site-theme/` は**新規記事のため
  NEWS_BODY_ARCHIVE への旧本文アーカイブは不要**(アーカイブ方針は「置換時に旧を残す」)。
- **機能台帳(H-9-5)**: `gen.py SITE_FEATURES` が主要機能の現行版を明示
  (theme v3 / consent v3 / prefs v2 / search v2 / compare v2 / reveal v1 / store v1 / auth v1)。
  /dev/ の一覧表と `window.SZ.features` に反映。consent の版だけは
  CONSENT_VERSION が原本(二重管理しない)。README に「拡張ポイント」章を追加。

## H-9-6 の設計メモ(2026-07-18)— 前線テーマ(endfield)を live 化

- ユーザーからエンドフィールドのゲーム内UI参考資料を6バッチ受領(静止画25枚+動画5本)。
  動画は imageio-ffmpeg で毎秒フレーム抽出→コンタクトシート化して確認。観察の全記録は
  `project-notes/theme-endfield-plan.md` の 0-A〜0-E に集約。
- 確定意匠: 極暗チャコール地(#0e0e11)×鮮烈イエロー(#f4df00。黄の上の文字は黒)。
  副光に橙(#ff7a1c)。作品UIは「黄=主アクセント/黄ピル+黒文字ボタン/白黒ブロック反転/
  coral警告/シアン環境光」が一貫。基調はダーク/ライト二系統あるが、既存テーマが全て
  ダーク運用のため endfield=ダークを採用(ライト版は将来別テーマに分離)。
- 実装: `data_themes.py` の endfield を `status:"planned"→"live"` に。16変数+extra_vars を
  実装しただけで、themes.css・切替UI(ヘッダ/ドロワー/設定)・早期適用・meta同期へ全自動反映。
  → 単一ソース化(H-9-1)の設計が想定通り機能。コントラストは WCAG AA を Python 実測。
- 付随更新: ニュース記事を「準備中」→「前線モードを公開」に、README テーマ章に endfield 追記、
  interact のテーマテストを「planned で非存在」→「live で切替・meta・早期適用」へ書換え。
- collab-endfield.css(LP専用 `--cl-*`)は流用せず、基礎トークンを独立実装(手順書の方針通り)。

## H-9-6 追補(2026-07-18)— 前線テーマの「全パーツ専用スキン」化

- ユーザー要望「色だけでなくスタイルを全て専用に。まるで全てがコラボページになるように」。
  参考動画5本を imageio-ffmpeg で 0.1秒刻み(fps=10・計1945枚)抽出→フレーム差分で
  遷移ピークを検出し、ボタン/カード/背景/見出し/ヘッダ等のパーツ意匠を精査。
- 新規 `assets/css/theme-endfield.css`(手書き)を全ページに読込。ただし
  **[data-theme="endfield"] スコープ**で、選択時のみ適用・他テーマ非影響。gen.py の
  head に link 追加(animations.css の後)。ASSET_V は assets/css/*.py glob で自動追従。
- 実装したパーツ: 黄フラット角切りピルボタン(clip-path+drop-shadow影+末尾黒マーカー)/
  副ボタン=チャコール+黄左エッジ/カード=上辺黄ヘアライン+右上HUDブラケット(ホバー点灯)/
  見出し eyebrow に「//」前置/背景=微グリッド+斜めハッチ+隅グロー(body::before は
  z-index:-1 固定でレイアウト不干渉)/チップ・フォーム・スクロールバー・フォーカス・選択色。
- ハマり: 当初 body::before を z-index:0 にし content を position:relative で持ち上げた際、
  **.drawer(通常 position:fixed のモバイルメニュー)まで relative 化して通常フローに入り、
  ヒーロー上に約1084pxの空白**が発生。→ body::before を z-index:-1 にし、持ち上げ規則を撤去して解決。
- 検証: 標準監査(デフォルトテーマ)に加え、endfield テーマを localStorage 注入した
  横スクロール検査(代表15ページ×375/1440px)を別途実施。
