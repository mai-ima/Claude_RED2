# サイクルG 事前調査報告 — 全ページ改修+コラボ作り込み+カウントダウン自動切替(2026-07)

実装前の調査記録。対象: ①タブレット予告→フルLP自動切替 ②第1弾コラボLP作り込み
③カウントダウンUI改修 ④薄いページ補強 ⑤FAQ/用語集/検索の拡充。
※第2弾コラボの相手名は本書にも記載しない(機密方針の継続)。

---

## 1. タブレット予告 → フルLP自動切替(二状態ページ)

### 現状
- タブレット予告は `gen.py: build_collab_tablet_teaser`(~3788行)が生成。本文はサイト最薄層
  (493〜545字)。データは `data_collab.py` の `cfg["tablet"]` に `reveal_at / device / lead` の
  3キーのみ。
- カウントダウンは全コラボ共通の `.cl-count[data-until]`(collab-core.js 14〜55行)。
  D-Aで実装済みのグレース機構(`.cl-count__soon` の有無で発表系/受付終了系を判別)が
  そのまま切替トリガに流用できる。
- ページの title/desc は「COMING SOON/予告ページ」で**現状ネタバレなし**(発表後情報を
  head に足さない限り維持される)。

### 実装方針(確定)
- 同一URL `/collab/{slug}/tablet/` に `data-reveal-stage="teaser"`(現行)と
  `data-reveal-stage="full" hidden`(フルLP)を両方描画し、collab-core.js の
  `diff <= 0` 分岐(既存グレース処理の隣)で teaser→full を切替。読込時に既に過ぎて
  いる場合も同処理(`tick()` は初回即時実行されるため追加コード最小)。
- `hidden` 属性の付け外しで切替(CSSだけに頼らない)。`aria-hidden` は hidden と重複する
  ため不要(HTML標準で hidden が支援技術からも隠す)。
- 演出: full 表示時に body へ `is-revealed` を付与し、CSSで fade+glow。
  `prefers-reduced-motion` では即時表示。

### 必要データ設計(cfg["tablet"] 拡張スキーマ)
```
tagline / price / qty / reserve(予約=発表当日) / release(発売) / until(受付終了)
stats: 4個 / highlights: 3本 / specs: 2群(ディスプレイ・性能 / 本体・販売)
```

### 数値案(スマホ版・Pad 2 と整合)
アンカー: Pad 2=¥109,800(12.4型・165Hz・RAI-G4)。コラボスマホ=¥159,800〜172,800。
コラボPadはその中間のプレミアム帯に置く。SoCはスマホ版と同じ専用SoC(タブレット駆動
チューン表記)、冷却は専用冷却の拡張版表記で D-B と整合させる。

| 機種 | 発表(reveal) | 予約 | 発売 | 受付終了 | 数量 | 価格案 |
|---|---|---|---|---|---|---|
| 七耀 Pad | 7/29 20:00 | 7/29 | 8/12 | 10/4 | 5,000 | ¥146,800 |
| 残響 Pad | 7/30 20:00 | 7/30 | 8/13 | 10/11 | 4,500 | ¥149,800 |
| 夜行 Pad | 7/31 20:00 | 7/31 | 8/14 | 10/18 | 4,000 | ¥152,800 |
| 前線 Pad | 8/1 20:00 | 8/1 | 8/15 | 10/25 | 4,500 | ¥144,800 |

- ヒーロー図版: `svg_art.svg_tablet(pid, body_hex, glow, label, ...)` をインライン呼び出し
  (製品画像ファイルは products 専用のため使わない)。`_DESIGNS` はスマホのコラボ4機
  (shichiyo/zankyo/yako/zensen)分しかないため、タブレットは line="pad" の標準造形+
  作品色(tokens)で描く。**専用 design の新設は任意**(やるなら svg_art に tablet 用
  意匠を追加するが、初回は色+ラベルで十分成立)。

### 第2弾(next系)の発表後
- 相手名は出せない → `_collab_lp_teaser` に hidden の「REVEALED — 共同設計、正式発表。
  詳細は続報で。」ブロックを追加し、同じ切替機構で表示。通知CTA・ニュース導線を強調。
  ヒント欄は「答え合わせは続報で」の文言に差し替わる程度に留める。

### リスク・注意
- **JS再描画の罠(news一覧の教訓)**: pages.js を確認した結果、コラボ関連の再描画は無し
  (finder のライン重みに "collab" が出るだけ)。ハブ・LPは静的なので data-reveal 機構が
  素直に効く。
- ネタバレ防止: head(title/desc)には発表後情報(価格等)を**絶対に足さない**。
  selftest に「tablet ページの head に価格が含まれない」検査を追加予定。
- sitemap/検索インデックス: PAGES に登録されるのは title/desc のみなので、非ネタバレを
  維持すれば露出しない。full 側の本文は検索クロール対象になるが、デモサイトのため許容
  (気にする場合は full 側を JS 注入にする手もあるが、複雑化するので採らない)。

---

## 2. 第1弾コラボLPの作り込み(現状セクション棚卸し)

生成物から見出しを抽出した現状構成:

- **genshin(20節)**: TEYVAT / SEVEN ELEMENTS / CRAFT / ELEMENTAL DISPLAY / GENSORO-E1 /
  SPEC / ELEMENTAL TUNING / DEVELOPMENT NOTES / FIELD REPORT / THEME PACK / COLLECTOR'S BOX /
  DEDICATED SILICON / DEDICATED COOLING / ACCESSORY / IN THE BOX / SCHEDULE / 受付系 / FAQ
- **wuwa(18節)**: SOLARIS-3 / KYOSHIN-W1 / MONOLITH / SPEC / TOUCH TO PHOTON / ANATOMY /
  RESONANCE HAPTICS / WORDS / COMPARISON / SILICON / COOLING / ACCESSORY / …
- **nte(18節)**: HETHEREAU / NIGHT CITY / NEON SIGN EL / YASO-N1+2TB / NIGHT LAB /
  EL SIGN CATALOG / NIGHT SNAP / APPRAISAL / SCOREBOARD / …
- **endfield**: 独自の ef-* 体系(キースペック/専用機能/設計特性/耐久/持続fps 等の
  ターミナルUI)。すでに最重量級。

### 作り込み方針
- 4LP共通で追加: **タブレット帯**(「{device} Pad — 予告中/発表済み」。ラベルは既存の
  data-reveal/data-soon 機構で自動追従)+ **冷却×シリコン連携図**(専用SoCと専用冷却が
  同一設計で噛み合う接続ダイアグラム。cl-arch 系流用)。
- 作品別の新節(1〜2節): 七耀=色設計ノート(パネル調律の物語)、残響=入力遅延の実測
  分解(タッチ→フォトン内訳表)、夜行=夜景作例ギャラリー(SVG作例カード)、
  前線=フィールドレポート追補(気温・粉塵ログ風)。endfield は既に重いので追加は
  タブレット帯+連携スロットのみに抑える判断もあり。

---

## 3. カウントダウンUI改修

- 現状: `.cl-count__row`(日/時/分/秒の数字)+ `.cl-count__end` ラベル+グレース枠。
  スタイルは collab-core.css 193〜222行。
- 改修案: ①SVG進捗リング(公開時点→reveal_at の残割合。開始基準は「ページに来た時点
  からの見た目」ではなく、ティザー公開日(データに `announced_at` を足す)〜reveal_at の
  実割合が正確) ②残り24時間未満で `is-imminent`(数字グローパルス) ③秒の桁の
  tick アニメ(reduced-motion で無効)。
- JSは collab-core.js の `tick()` 内で残割合を CSS変数 `--cl-progress` に書くだけにし、
  描画はCSS(conic-gradient か SVG stroke-dashoffset)に寄せる。

---

## 4. 薄いページ補強(対象と実体の対応)

本文文字数の実測で特定(JSアプリページ=cart/検索等は対象外)。

| ページ | 実体 | 現状 | 補強案 |
|---|---|---|---|
| /store/ | src/pages/store.html(58行) | 465字 | 購入フロー図・会員特典・ギフト/下取り/学割導線 |
| /support/ | src/pages/support.html(64行) | 480字 | チャネル一覧表・自己解決フローチャート |
| /products/ | gen.py build_product_hubs | 493字 | 選び方ガイド帯・ライン概観(用途→ライン対応表) |
| /tech/memory/ | gen.py build_tech_hub | 504字 | hub_extra 新設(なぜ自社メモリか・協調設計図) |
| /tech/storage/ | gen.py build_tech_hub | 478字 | hub_extra 新設(ロード時間の分解・耐久の考え方) |
| /company/locations/ | fragment(41行) | 561字 | 拠点ごとの機能・アクセス表・フロア構成 |
| /company/ir/ | fragment(59行) | 594字 | IRカレンダー・開示方針・株主向けQ&A |
| /company/leadership/ | fragment(36行) | 652字 | 役員略歴の拡充・担当領域マップ |
| /community/ | src/pages/community/index.html | 586字 | 行動規範・年間イベント年表・公認コミュニティ制度 |
| /community/esports/ | fragment(68行) | 681字 | 大会フォーマット・過去大会結果表・機材レギュレーション |
| /sustainability/report/ | fragment(56行) | 569字 | 年次ハイライト表・目標と実績の対比 |
| /developers/showcase/ | fragment(58行) | 536字 | 採用事例カード増(ジャンル別)・導入効果の数値 |
| /business/store/ | gen.py build_biz_store | 610字 | 導入ステップ詳細・契約形態比較表 |
| /legal/accessibility/ | fragment(43行) | 671字 | 対応方針の具体化(JIS配慮・検証体制・窓口) |
| /store/trade-in/ | fragment(44行) | 478字 | 査定フロー表・買取価格例・データ消去手順 |

補強は各2〜4節。gen.py 側実体(products/tech/business-store)はビルダーへ、他は
フラグメント直書き。プレースホルダ禁止・既存の数値/日付と整合させる。

---

## 5. FAQ / 用語集 / 検索サジェストのギャップ

- **FAQ(現15件)**: コラボ関連が0件。追加候補: コラボ機と通常機の違い(総論)/
  専用冷却と氷刃の違い / タブレット予告の発表日と買い方 / 第2弾の相手非公開方針 /
  発表カウントダウン終了後の表示 / コラボ機のOSアップデート方針。→「コラボ」カテゴリ新設。
- **GLOSSARY(現19件)**: 専用シリコン(元素炉/共振/夜想/基幹)、専用冷却(元素環/共振鎖/
  夜霧/機関)、コラボタブレット、定速ガバナー/疾波ガバナー/幻彩エンジン等が未収録。
  8〜12語追加、各 term に関連リンク(/collab/{slug}/silicon/soc/ 等)。
- **SUGGEST_GROUPS(pages.js・現11組)**: 端末名・作品名のみ。追加候補:
  元素炉(げんそろ/gensoro)・共振(きょうしん)・夜想(やそう)・基幹(きかん)・
  元素環(げんそかん)・共振鎖(きょうしんさ)・夜霧(よぎり)・機関(きかん※基幹と
  衝突するため表示名で区別)・Pad系(しちようぱっど等)・水龍(すいりゅう)・KANAME
  (かなめ)。※「きかん」の重複は suggestFor が先勝ちのため表示名併記で回避する設計が必要。

---

## 6. 品質ゲート拡張ポイント

- **validate.py**: `cfg["tablet"]` にフルLPキーがある場合の必須キー検査+スマホ版との
  SoC名/冷却名整合(highlights 文字列に専用SoC名が含まれるか等の軽い検査)。
- **selftest.py**: ①タブレット4ページに `data-reveal-stage="teaser"` と `"full"` が両方
  存在 ②tablet ページ head に価格(¥14x,800)が漏れていない ③full 側に価格がある。
- **interact.js(現3テスト)**: カウントダウン切替テストを追加 —
  `page.evaluate` で `.cl-count` の data-until を過去日時に書き換え→ tick 相当を再実行
  させるのは実装依存になるため、**data-until を過去にした一時HTMLを file:// で開く**か、
  「読込時に既に過ぎている」パスを検証する(生成物を一時パッチ→localhost 経由で確認→
  再生成で復元)のが確実。後者は既にD-A検証で実績あり。

---

## 7. 実装順(確定プランの通り)

G-A(データ拡張→二状態ページ→切替JS→第2弾演出)→ G-B(LP作り込み)→ G-C(UI改修)
→ G-D(薄いページ15枚)→ G-E/F(品質ゲート+FAQ/用語集/検索/ハブ追従/notes)→ G-H(総合検証)。
各フェーズで 生成→selftest→audit(375px)→スクショ目視 を完了してからコミット。
