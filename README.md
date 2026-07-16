# 朱雀 / SUZAKU — 架空ゲーミングデバイス企業 公式サイト

REDMAGICと同じ思想(自社シリコン・冷却技術・ゲーミング特化)を持つ架空の日本企業
「株式会社朱雀(SUZAKU Inc.)」のコーポレートサイトです。
2022年5月1日創業、2023年5月1日初製品発表という設定で、製品・技術・法人・開発者・
サポート・法務・コラボレーションまで **約232ページ** をフル構成で実装しています。

主な領域:

- **一般製品**: スマホ/タブレット4ライン・全世代、アクセサリ、比較ツール、ストア(カート〜チェックアウト)
- **法人向け(一般と完全分離・`/business/` 配下)**: 法人専用スマホ「KANAME B1」・法人専用ストア(見積フロー)・法人専用OS
- **コラボレーション**: 第1弾4作品(原神/鳴潮/NTE/エンドフィールド)の専用LP+専用SoC、第2弾ティザー(相手非公開)、コラボタブレット予告
- **技術/OS/ニュース/サポート/法務/企業情報**、管理ボード(`/admin/`)

**すべてのコンテンツ・企業・製品・数値はフィクションです。**

## 技術構成

- **静的HTML + CSS + JavaScript**(ビルド不要・外部ライブラリ0・外部画像0)
- Vercelにゼロ設定でデプロイ可能(`vercel.json` 同梱)
- ローカル確認: `python3 -m http.server 3000` → http://localhost:3000/

```
/
├── index.html ほか各ページ     # 生成物(ディレクトリ = ルート)
├── assets/
│   ├── css/   tokens / base / components / animations /
│   │          collab-core・collab-{genshin,wuwa,nte,endfield,next}(コラボLP専用)
│   ├── js/    keys(sz_*キー一元管理) / fmt(esc・yen共通ヘルパー) /
│   │          main(nav・Cookie同意・演出) / charts(SVGグラフ) / store(カート・購入・比較) /
│   │          biz(法人機の構成プレビュー・store非依存) / pages(FAQ・検索・もしかして) /
│   │          collab-core+collab-{slug}(コラボLP・カウントダウン・ティザー演出) /
│   │          auth-core・auth-guard・auth-account・auth-admin・auth-status(認証・管理ボード)
│   └── img/   全SVG自動生成(製品画像・ダイアグラム)
├── data/products.js            # クライアント用データ(自動生成・法人機は含めない)
├── src/pages/                  # フラグメント(本文のみのHTML+METAコメント)
├── project-notes/              # 内部メモ(構成監査・コラボ調査・backlog。配信対象外)
└── scripts/
    ├── gen.py                  # 静的サイトジェネレータ(このリポジトリの心臓)
    ├── lib.py                  # 共通ユーティリティ(esc/yen/num/slugify・純粋関数)
    ├── validate.py             # データ検証層(スキーマ・絵文字・機密ガード。ビルド前ゲート)
    ├── selftest.py             # スモークテスト(生成→検証→リンク→整合をワンコマンド)
    ├── data_products.py        # 製品データ(単一ソース。一般 + 法人 BIZ_PRODUCTS + 法人OS)
    ├── data_collab.py          # コラボデータ(第1弾/第2弾ティザー/専用シリコン/専用冷却/タブレット予告)
    ├── data_tech.py            # 技術・OSデータ
    ├── data_misc.py            # ニュース・FAQ・沿革(+ NEWS_BODY_ARCHIVE)
    ├── data_docs.py            # 開発者ドキュメント
    ├── svg_art.py              # SVGアート生成(製品・シルエット・ダイアグラム・ニュースアイキャッチ)
    ├── check_links.py          # リンク切れ検査
    ├── audit.js                # 全ページ監査(Playwright)
    └── shot.js / interact.js   # スクショ / 主要インタラクションの実地検証(QA用)
```

## ビルドと品質ゲート

データ生成は「**検証 → 生成 → 整合チェック**」の順で走る。`gen.py` は冒頭で
`validate.py` を呼び、壊れたデータ(必須キー欠落・id重複・不正な日付/価格・データ
ファイルへの絵文字混入など)を**生成前に明快なメッセージで停止**させる。生成後は
重複URLを検出し(あれば失敗)、グループ別ページ数を `.build/report.json`(配信対象外)
へ書き出す。

```bash
python3 scripts/validate.py     # データの不変条件だけを検査
python3 scripts/gen.py          # 検証 → 全ページ生成 → 整合チェック
python3 scripts/selftest.py     # 生成→検証→リンク→整合 をワンコマンドで(CIと同じゲート)

make verify                     # = selftest(既定タスク)
make build / make links / make audit / make serve / make clean
```

- CI(`.github/workflows/verify.yml`)は push/PR で `validate.py` + `selftest.py` を実行する。
- 第2弾コラボ相手名の機密チェックは、禁止語をリポジトリ内に置かない方針のため、
  リポジトリ外のワードリストを `SZ_BLOCKLIST_FILE` で渡したときだけ `validate.py` が検査する。

### 全ページ監査(Playwright)

```bash
python3 -m http.server 8930 &   # リポジトリルートで配信(ブラウザの並列取得には threaded 推奨)
node scripts/audit.js           # AUDIT_WIDTH=1440 でPC幅、AUDIT_BASE で配信先変更
```

- 製品・価格・スペック・ニュースは `scripts/data_*.py` の単一ソースから、
  製品ページ / specsページ / ストア / 比較 / 検索 / チャートすべてに供給されます。
- 固有ページ(ホーム・ストア・サポート等)は `src/pages/` のフラグメントを編集します。
  先頭の `<!--META {...} -->` でタイトル・説明・テーマ(dark/light)・パンくずを指定します。

## 実動作するモック機能(すべてlocalStorage完結)

Cookie同意バナー(カテゴリ別設定) / カート / 多段チェックアウト(Luhn検証・
支払方法・配送日時指定・注文番号発行) / 注文照会 / 修理受付と照会 / 比較ツール
(実測ダッシュボード+最良値ハイライト+レーダーチャート) / 法人機の構成プレビュー
(色・容量・カメラ切替→画像/価格連動、`biz.js`) / FAQ検索 / ニュースフィルタ /
サイト内検索(「もしかして」表記ゆれサジェスト付き) / コラボ発表カウントダウン /
各種お問い合わせフォーム / SVGチャート(棒・折れ線・レーダー・ドーナツ、表フォールバック付き) /
アカウント・ログイン / メンテナンスシステム / サイトお知らせバナー / 表示設定(`/settings/`)

### 管理ボード(`/admin/`)

WAI-ARIA Tabsパターン(自動アクティベーション・roving tabindex・矢印キー/Home/End
操作対応)によるタブ構成で、以下の機能を提供する:

- **概要**: クイック操作・曜日別売上チャート・操作履歴(監査ログ)
- **稼働制御**: メンテナンスモード / 全体制御(立入禁止・購入停止・問い合わせ停止) /
  サービス別状況
- **ページ制御**: 個別ページを会員限定・管理者限定・メンテナンス中・非公開(404)に設定
- **ニュース**: 作成・削除(公開すると `/news/` 一覧と専用記事ページに反映)
- **サイト**: お知らせバナー設定・ストア設定(送料無料しきい値・配送料)
- **会員**: 追加・検索・権限変更・パスワード表示・削除
- **分析**: 会員登録推移・権限内訳のチャート
- **記録・ツール**: 注文/修理のステータス変更、データのバックアップ(書き出し/
  読み込み)・デモデータのリセット

バックアップ・リセット対象の `sz_*` キー一覧は `assets/js/keys.js` の
`window.szKeys` に一元管理されており、機能追加時にここへ1箇所追記するだけで
バックアップ・リセットの両方に反映される。

### 表示設定システム(`window.szPrefs`)

`assets/js/main.js` の `PREF_SCHEMA` が単一ソース。項目を追加するには
`{ default, apply }` を1行足すだけでよく、`applyPrefs()` が全項目を
`<html>` の `data-*` 属性へ自動反映する(個別配線は不要)。現在の項目:
`footerMode`(フッターの折りたたみ/常時展開)・`density`(文字とUIの大きさ)・
`motion`(アニメーション低減)。設定は `sz_prefs`(localStorage)に保存される。
設定ページ(`src/pages/settings.html`)側は `data-pref` / `data-pref-value`
属性だけで動く汎用配線のため、HTMLにグループを追加するだけで新項目に対応できる。

### カラーテーマの単一ソース

テーマ選択肢は `scripts/gen.py` の `THEME_OPTS` にのみ定義し、
ヘッダーのドロップダウン(`theme_menu_buttons()`)とドロワーの
セグメント切替(`theme_seg_buttons()`)を同じ配列から生成する。
テーマを追加・変更する場合は `THEME_OPTS` だけを編集すればよい。

### キャッシュバスティング

`scripts/gen.py` はビルド時に `assets/css`・`assets/js`・`scripts/data_*.py`
(`/data/products.js` の生成元)の内容ハッシュ(`ASSET_V`)を計算し、全
`<link>` / `<script>` に `?v=<hash>` を付与する。資産やデータが変わるたびに
URLが変わるため、CDN・ブラウザの古いキャッシュを確実に回避できる
(`vercel.json` の `/assets/` は `immutable` で長期キャッシュ)。
利用者は Cookie設定ページ(`/legal/cookie/`)からキャッシュを手動削除もできる。

### 法人向けエリア(一般ラインと完全分離)

法人向けは一般ラインと **完全に分離** している。`data_products.py` で法人機を
`BIZ_PRODUCTS` として `PHONES` から抽出し、`ALL_PRODUCTS`(=一般ストア/製品ハブ/比較/
検索/サイトマップの母集団)からは除外する。法人コンテンツは `/business/` 配下でのみ提供する:

- `/business/kaname-b1/`(+`/specs/`) — 法人専用スマホ「KANAME B1」。カート購入ではなく
  **見積・導入相談フロー**。構成プレビューは `store.js` 非依存の専用 `biz.js`(`data-biz` 属性)
- `/business/store/` — 法人専用ストア(導入相談・お見積り)
- `/business/os/` — 法人専用OS「SUZAKU OS for Business」(`BIZ_OS` 単一ソース)

### コラボレーション(`/collab/`)

- **第1弾(公開・受付中)**: 原神/鳴潮/NTE/エンドフィールドの4作品。作品ごとに
  **完全個別のLPレイアウト**(`gen.py` の `_collab_lp_{slug}`)+ 専用SoC等のシリコンページ
  (`/collab/{slug}/silicon/{key}/`)+ **作品専用の冷却技術**(`COLLAB_COOLING` /
  `/collab/{slug}/cooling/`。標準の氷刃/旋風ではなく作品ごとに新規設計)。
  配色・フォントは各作品のトークン(`collab-{slug}.css` / `COLLAB_FONTS`)で切り替える
- **第2弾ティザー(相手非公開)**: `/collab/next{,-2,-3,-4}/`。共通の `_collab_lp_teaser` と
  `collab-next.css`(`.collab--next`)を **`assets_slug` で共有** しつつ、発表カウントダウン・
  ヒント・「言えること」・進捗バー・マーキー・通知CTAを掲載。ヒーロー背景と一部UIは
  `nx--{slug}` フックで **作品ごとに意匠を一部だけ変える**(相手名は一切出さない)。
  発表日時(`reveal_at`)を実時間が過ぎると、相手を伏せたまま「発表準備中」へ自動遷移する
  **グレース状態**(`collab-core.js` / ハブ・兄弟リンクは `main.js` の `data-reveal`/`data-soon`)
- **コラボタブレット予告**: `/collab/{slug}/tablet/`。第1弾4作品の続きを各作品テーマで予告
- ハブ `/collab/` は「第1弾(受付中)/第2弾(COMING SOON)/タブレット予告」を整理。
  ダーク背景で見えにくい暗いアクセント色(例: エンドフィールドの `#141412`)は
  `_hub_card_style()` が `accent2` を表示色に採用して可読性を担保する

> コラボ相手・用語の表記根拠は `project-notes/collab-research.md`、未着手アイデアは
> `project-notes/backlog.md` を参照(いずれも `.vercelignore` で配信対象外)。
> 第2弾の相手作品名はリポジトリのどこにも記載しない方針。

### 製品・OS・ニュースの演出(ライン別・旗艦別)

ページの単調さを避けるため、種別ごとに固有の演出を注入する(いずれも `gen.py` の
ビルダー分岐+既存CSS/JSで完結。`project-notes/structure-audit.md` 参照):

- **旗艦ショーケース**: SUZAKU 4 / Pad 2 のみ、ヒーロー直後にスクロール連動の分解
  ショーケース(`_flagship_showcase` / `main.js` の IntersectionObserver・reduced-motion 対応)
- **ライン別ヒーロー**: `hero--gaming/life/entry` に分岐(ゲーミング=ダーク+グロー、
  TSUBAME=明るめ+製品先行、Lite=価格先行)
- **組み合わせ提案**: 本体×アクセサリのセット提案(`_combo_section`・合計価格の目安付き)
- **OS最新版のUIモック**: 最新版のみスクショ風カルーセル(`_os_ui_carousel`)
- **ニュースアイキャッチ**: 記事はカテゴリ配色SVG(`svg_art.news_eyecatch`)、一覧は
  サーバ/JS(`pages.js`)双方でカテゴリ配色バナーを描画(JS再描画に追従)

## Next.js(App Router)への移行ガイド

本サイトは後日のNext.js移行を想定した構造になっています。

1. **ルーティング**: ディレクトリ構造がそのまま App Router に対応します。
   `/products/phone/suzaku-4/index.html` → `app/products/phone/suzaku-4/page.tsx`
2. **データ**: `scripts/data_*.py` の内容を `lib/data.ts` へ移植(構造はJSONそのまま)。
   製品ページ群は `generateStaticParams` による動的ルート1本に集約できます。
3. **スタイル**: `assets/css/tokens.css` のCSS変数を `globals.css` にそのままコピー。
   コンポーネントCSSはBEM風クラスのため、CSS Modulesへの分割が機械的に可能です。
4. **共通UI**: ヘッダー / フッター / Cookie同意 / 製品カードは全ページ同一マークアップ
   (`scripts/gen.py` の `header_html()` / `footer_html()` / `product_card()`)なので、
   そのままReactコンポーネント化できます。
5. **JS**: `charts.js` / `store.js` / `pages.js` は依存0のバニラJSのため、
   `"use client"` コンポーネントのフックへ段階的に移行できます。

## デプロイ(Vercel)

リポジトリをVercelにインポートするだけで公開できます(Framework Preset: Other)。
`vercel.json` でクリーンURL・キャッシュ・セキュリティヘッダを設定済みです。
`src/`・`scripts/`・`project-notes/`(内部監査メモ)は `.vercelignore` により配信対象
から除外されます。
