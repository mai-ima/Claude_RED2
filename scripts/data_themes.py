# ==========================================================================
# サイトカラーテーマの単一ソース(H-9-1)
#
# ここが唯一の定義。gen.py がこのデータから
#   - assets/css/themes.css([data-theme="..."] ブロック。自動生成・手編集禁止)
#   - ヘッダードロップダウン / ドロワー / 設定ページのテーマボタン
#   - 早期適用スクリプト用の最小データ(window.SZ_THEMES)
# をすべて生成する。テーマの追加は THEMES に dict を1つ足すだけでよい。
#
# 各項目のキー:
#   id           … data-theme 値 / localStorage sz_theme の保存値(一意)
#   status       … "live"(公開) / "planned"(予約枠。CSS・UI・JSのどこにも出力されない)
#   kind         … "concrete"(CSS変数を持つ実テーマ) / "virtual"(auto/system のような解決型)
#   label/short  … 正式名称(ドロップダウン・トースト)/ 短縮名(ドロワー・設定)
#   swatch       … 選択UIの色見本(CSS background 値)
#   meta         … <meta name="theme-color"> に同期する色(virtual は解決先の値を使う)
#   color_scheme … CSS color-scheme(concrete のみ)
#   default      … True のテーマは ":root, [data-theme=id]" として生成(既定テーマ。1つだけ)
#   vars         … THEME_VAR_KEYS の16変数(concrete かつ live で必須)
#   extra_vars   … テーマ固有の追加上書き(grad/glow/shadow 等。任意)
# ==========================================================================

# 全 concrete テーマが必ず上書きする意味変数(validate.py が欠落を機械検査する)
THEME_VAR_KEYS = [
    "bg", "bg-deep", "surface", "surface-2", "surface-3",
    "line", "line-strong",
    "text", "text-strong", "text-soft", "text-faint",
    "accent", "accent-hover", "accent-contrast",
    "header-bg", "card-hover-line",
]

THEMES = [
    # ---- 解決型(CSSは生成しない。JSが実テーマへ解決する) ----
    {
        "id": "auto", "status": "live", "kind": "virtual",
        "label": "ページ既定", "short": "既定",
        "swatch": "linear-gradient(90deg,#fafafc 50%,#0b0b10 50%)",
        "desc": "ページごとに用意された配色(製品=ダーク、法務=ライト等)に従います。",
    },
    {
        "id": "system", "status": "live", "kind": "virtual",
        "label": "OSの設定に連動", "short": "OS連動",
        "swatch": "linear-gradient(45deg,#0b0b10 50%,#fafafc 50%)",
        "desc": "端末(OS)のライト/ダーク設定に自動で追従します。",
    },

    # ---- 実テーマ(値は旧 tokens.css のテーマブロックから1:1移植) ----
    {
        "id": "light", "status": "live", "kind": "concrete",
        "label": "ライト", "short": "ライト",
        "swatch": "#fafafc", "meta": "#fafafc", "color_scheme": "light",
        "vars": {
            "bg": "#fafafc", "bg-deep": "#f0f0f4",
            "surface": "#ffffff", "surface-2": "#f4f4f8", "surface-3": "#ebebf1",
            "line": "rgba(10, 10, 20, 0.1)", "line-strong": "rgba(10, 10, 20, 0.22)",
            "text": "#2c2c38", "text-strong": "#101018",
            # text-faint はコントラスト比 4.6:1(旧 #85859a は 3.5:1 で WCAG AA 未達)
            "text-soft": "#5c5c6e", "text-faint": "#70708a",
            "accent": "#d43a24", "accent-hover": "#e8442e", "accent-contrast": "#ffffff",
            "header-bg": "rgba(250, 250, 252, 0.8)",
            "card-hover-line": "rgba(212, 58, 36, 0.4)",
        },
        "extra_vars": {
            "shadow-sm": "0 2px 8px rgba(20, 20, 40, 0.07)",
            "shadow-md": "0 8px 30px rgba(20, 20, 40, 0.1)",
            "shadow-lg": "0 24px 70px rgba(20, 20, 40, 0.14)",
            "glow-vermilion": "0 8px 30px rgba(212, 58, 36, 0.18)",
            "glow-strong": "0 10px 36px rgba(212, 58, 36, 0.28)",
        },
    },
    {
        "id": "dark", "status": "live", "kind": "concrete", "default": True,
        "label": "ダーク", "short": "ダーク",
        "swatch": "#0b0b10", "meta": "#0b0b10", "color_scheme": "dark",
        "vars": {
            "bg": "var(--n-1)", "bg-deep": "var(--n-0)",
            "surface": "var(--n-3)", "surface-2": "var(--n-4)", "surface-3": "var(--n-5)",
            "line": "rgba(255, 255, 255, 0.09)", "line-strong": "rgba(255, 255, 255, 0.18)",
            "text": "var(--n-10)", "text-strong": "#ffffff",
            # text-faint は n-7(3.8:1・AA未達)から独立させ 4.7:1 の専用値に
            # (n-7 自体は装飾用途で他所からも参照されるため触らない)
            "text-soft": "var(--n-8)", "text-faint": "#7a7a90",
            "accent": "var(--su-vermilion)", "accent-hover": "var(--su-vermilion-bright)",
            "accent-contrast": "#ffffff",
            "header-bg": "rgba(11, 11, 16, 0.72)",
            "card-hover-line": "rgba(232, 68, 46, 0.45)",
        },
        "extra_vars": {},
    },
    {
        "id": "g", "status": "live", "kind": "concrete",
        "label": "Gモード", "short": "G",
        "swatch": "linear-gradient(135deg,#00e68a,#00c2ff)", "meta": "#04070a", "color_scheme": "dark",
        "vars": {
            "bg": "#04070a", "bg-deep": "#020405",
            "surface": "#0a1116", "surface-2": "#101a21", "surface-3": "#17242d",
            "line": "rgba(0, 230, 170, 0.13)", "line-strong": "rgba(0, 230, 170, 0.3)",
            "text": "#e2f0ea", "text-strong": "#ffffff",
            "text-soft": "#9fb8ad", "text-faint": "#6d857c",
            "accent": "#00e68a", "accent-hover": "#2dffab", "accent-contrast": "#032117",
            "header-bg": "rgba(4, 7, 10, 0.74)",
            "card-hover-line": "rgba(0, 230, 138, 0.5)",
        },
        "extra_vars": {
            "grad-flame": "linear-gradient(135deg, #00c76f 0%, #00e68a 55%, #00c2ff 100%)",
            "grad-flame-v": "linear-gradient(180deg, #00e68a 0%, #00c2ff 100%)",
            "glow-vermilion": "0 0 24px rgba(0, 230, 138, 0.3), 0 0 80px rgba(0, 194, 255, 0.1)",
            "glow-strong": "0 0 30px rgba(0, 230, 138, 0.5), 0 0 110px rgba(0, 194, 255, 0.22)",
        },
    },
    {
        "id": "suzaku", "status": "live", "kind": "concrete",
        "label": "朱雀モード", "short": "朱雀",
        "swatch": "linear-gradient(135deg,#e8442e,#d9a441)", "meta": "#170609", "color_scheme": "dark",
        "vars": {
            "bg": "#170609", "bg-deep": "#0e0305",
            "surface": "#230a10", "surface-2": "#2d0e16", "surface-3": "#3a141d",
            "line": "rgba(255, 170, 130, 0.14)", "line-strong": "rgba(255, 170, 130, 0.3)",
            "text": "#f4e7e2", "text-strong": "#ffffff",
            "text-soft": "#cfa89c", "text-faint": "#9c7468",
            "accent": "#ff6a3c", "accent-hover": "#ff8a5c", "accent-contrast": "#ffffff",
            "header-bg": "rgba(17, 4, 7, 0.76)",
            "card-hover-line": "rgba(217, 164, 65, 0.55)",
        },
        "extra_vars": {
            "grad-flame": "linear-gradient(135deg, #e8442e 0%, #ff7a3c 45%, #d9a441 100%)",
            "grad-flame-v": "linear-gradient(180deg, #ff7a3c 0%, #d9a441 100%)",
            "glow-vermilion": "0 0 26px rgba(232, 68, 46, 0.4), 0 0 90px rgba(217, 164, 65, 0.14)",
            "glow-strong": "0 0 32px rgba(255, 122, 60, 0.55), 0 0 120px rgba(217, 164, 65, 0.28)",
        },
    },

    # ---- エンドフィールドコラボの一環のサイトテーマ「前線」(H-9-4→実装済み) ----
    # 配色は作品公式のゲーム内UI参考資料(2026-07-18受領・全6バッチ)に基づき、
    # project-notes/theme-endfield-plan.md の観察メモから確定。コントラストは WCAG AA 実測済み。
    # 意匠: 極暗チャコール地 × 鮮烈イエロー(#f4df00。黄の上の文字は黒)+ 橙の副光。
    # 注意: コラボ特設 collab-endfield.css(特設LP専用スコープ・--cl-* 系)の流用はしない。
    #        本テーマは基礎トークン(--bg/--surface/--text/--accent…)を独立実装したもの。
    {
        "id": "endfield", "status": "live", "kind": "concrete", "beta": True,
        "label": "前線モード", "short": "前線",
        "swatch": "linear-gradient(135deg,#f4df00,#ff7a1c)", "meta": "#0e0e11", "color_scheme": "dark",
        "desc": "エンドフィールド工業の設計言語。極暗チャコールに鮮烈イエローの標識色を差した配色です。",
        "vars": {
            "bg": "#0e0e11", "bg-deep": "#060607",
            "surface": "#1b1b1e", "surface-2": "#232326", "surface-3": "#2e2e32",
            "line": "rgba(255, 255, 255, 0.09)", "line-strong": "rgba(255, 255, 255, 0.2)",
            "text": "#ececee", "text-strong": "#ffffff",
            "text-soft": "#a9a9ae", "text-faint": "#7c7c84",
            "accent": "#f4df00", "accent-hover": "#ffe92e", "accent-contrast": "#141414",
            "header-bg": "rgba(14, 14, 17, 0.74)",
            "card-hover-line": "rgba(244, 223, 0, 0.55)",
        },
        "extra_vars": {
            "grad-flame": "linear-gradient(135deg, #f4df00 0%, #ffce00 50%, #ff7a1c 100%)",
            "grad-flame-v": "linear-gradient(180deg, #f4df00 0%, #ff7a1c 100%)",
            "glow-vermilion": "0 0 24px rgba(244, 223, 0, 0.32), 0 0 80px rgba(255, 122, 28, 0.12)",
            "glow-strong": "0 0 30px rgba(244, 223, 0, 0.5), 0 0 110px rgba(255, 122, 28, 0.22)",
        },
    },
]
