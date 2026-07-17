# -*- coding: utf-8 -*-
"""SUZAKU サイト データ検証層(ビルド前ゲート)。

`gen.py` の生成前に単一ソースデータ(製品/コラボ/ニュース/技術)の不変条件を検査し、
壊れたデータを「早期・明快に」失敗させる。従来は生成時に KeyError 等で分かりにくく
落ちていたものを、原因の分かるメッセージで停止させるのが狙い。

追加チェック:
- 絵文字ガード: データファイルに未承認の絵文字が混入していないか(承認記号は許可)。
- 機密ガード(任意): 第2弾コラボ相手名の混入検査。禁止語はリポジトリ内に置かない方針の
  ため、環境変数 SZ_BLOCKLIST_FILE で「リポジトリ外」のワードリストを渡したときだけ動く。

使い方:
    python3 scripts/validate.py        # 単体実行(NG があれば exit 1)
    from validate import validate_all  # gen.py main() 冒頭で呼ぶ
"""
import os
import re
import sys
import unicodedata
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from data_products import ALL_PRODUCTS, BIZ_PRODUCTS, LINES  # noqa: E402
from data_collab import COLLABS, COLLAB_SILICON, COLLAB_COOLING  # noqa: E402
from data_misc import NEWS  # noqa: E402
from data_tech import TECHS, OS_VERSIONS  # noqa: E402

HERE = Path(__file__).resolve().parent

# 本文・データ中で許可する記号(絵文字扱いしない)。プロジェクト規約の承認記号。
_ALLOWED_SYMBOLS = set("◆▲◇▽●▶◎▣△✓★→←↑↓ ✕")
# 絵文字とみなす Unicode 範囲(代表的な絵文字ブロック)。
_EMOJI_RE = re.compile(
    "["
    "\U0001F300-\U0001FAFF"   # 記号・絵文字・拡張
    "\U00002600-\U000026FF"   # その他の記号
    "\U00002700-\U000027BF"   # 装飾記号
    "\U0001F1E6-\U0001F1FF"   # 国旗
    "\U0000FE00-\U0000FE0F"   # 異体字セレクタ
    "\U00002B00-\U00002BFF"   # 矢印・星など
    "]"
)


class Issue(Exception):
    pass


def _err(errs, where, msg):
    errs.append(f"[{where}] {msg}")


def check_products(errs):
    seen = set()
    for p in ALL_PRODUCTS + BIZ_PRODUCTS:
        pid = p.get("id")
        where = f"product:{pid or '?'}"
        for key in ("id", "cat", "line", "name", "price", "status"):
            if key not in p:
                _err(errs, where, f"必須キー '{key}' がありません")
        if pid in seen:
            _err(errs, where, "id が重複しています")
        seen.add(pid)
        if p.get("cat") not in ("phone", "tablet", "accessory"):
            _err(errs, where, f"cat が不正: {p.get('cat')!r}")
        if p.get("line") not in LINES:
            _err(errs, where, f"line が LINES 未定義: {p.get('line')!r}")
        if not isinstance(p.get("price"), int) or p.get("price", 0) < 0:
            _err(errs, where, f"price が正の整数ではありません: {p.get('price')!r}")
        if p.get("status") not in ("current", "old"):
            _err(errs, where, f"status が不正: {p.get('status')!r}")
        if not isinstance(p.get("colors", []), list):
            _err(errs, where, "colors は list である必要があります")


def check_collab(errs):
    seen = set()
    for c in COLLABS:
        slug = c.get("slug")
        where = f"collab:{slug or '?'}"
        for key in ("slug", "game", "edition", "tokens", "hero"):
            if key not in c:
                _err(errs, where, f"必須キー '{key}' がありません")
        if slug in seen:
            _err(errs, where, "slug が重複しています")
        seen.add(slug)
        tok = c.get("tokens", {})
        for k in ("bg", "ink", "accent", "glow"):
            if k not in tok:
                _err(errs, where, f"tokens に '{k}' がありません")
        is_teaser = c.get("motif") == "teaser"
        if is_teaser and not c.get("reveal_at"):
            _err(errs, where, "teaser には reveal_at が必要です")
        if c.get("active") and slug not in COLLAB_SILICON:
            _err(errs, where, "active コラボに COLLAB_SILICON がありません")
        if c.get("active") and slug not in COLLAB_COOLING:
            _err(errs, where, "active コラボに COLLAB_COOLING がありません")
    # シリコンは 4 部品そろっているか
    for slug, comps in COLLAB_SILICON.items():
        keys = {x.get("key") for x in comps}
        for need in ("soc", "gpu", "mem", "ssd"):
            if need not in keys:
                _err(errs, f"silicon:{slug}", f"部品 '{need}' がありません")
    # タブレットのフルLPデータ(price がある=二状態ページ対象)の必須キーとSoC整合
    for c in COLLABS:
        t = c.get("tablet")
        if not t or not t.get("price"):
            continue
        where = f"tablet:{c['slug']}"
        for key in ("tagline", "qty", "reserve", "release", "until", "stats", "highlights", "specs"):
            if not t.get(key):
                _err(errs, where, f"フルLP必須キー '{key}' がありません")
        if len(t.get("stats", [])) < 3:
            _err(errs, where, "stats は3個以上必要です")
        if len(t.get("highlights", [])) < 3:
            _err(errs, where, "highlights は3本必要です")
        # スマホ版と同じ専用SoC名(先頭語)が specs に含まれるか
        soc = next((x for x in COLLAB_SILICON.get(c["slug"], []) if x["key"] == "soc"), None)
        if soc:
            soc_head = soc["name"].split(" ")[0]
            spec_text = str(t.get("specs", ""))
            if soc_head not in spec_text:
                _err(errs, where, f"specs にスマホ版と同じ専用SoC名({soc_head})がありません")


def check_news(errs):
    seen = set()
    for n in NEWS:
        nid = n.get("id")
        where = f"news:{nid or '?'}"
        for key in ("id", "date", "cat", "title", "excerpt", "body"):
            if key not in n:
                _err(errs, where, f"必須キー '{key}' がありません")
        if nid in seen:
            _err(errs, where, "id が重複しています")
        seen.add(nid)
        if not re.match(r"^\d{4}-\d{2}-\d{2}$", str(n.get("date", ""))):
            _err(errs, where, f"date が YYYY-MM-DD 形式ではありません: {n.get('date')!r}")
        if not isinstance(n.get("body"), list) or not n.get("body"):
            _err(errs, where, "body は非空の list である必要があります")


def check_tech(errs):
    for t in TECHS:
        where = f"tech:{t.get('id', '?')}"
        for key in ("id", "type", "hub", "name"):
            if key not in t:
                _err(errs, where, f"必須キー '{key}' がありません")
    for v in OS_VERSIONS:
        where = f"os:{v.get('path', '?')}"
        for key in ("path", "name", "code", "features"):
            if key not in v:
                _err(errs, where, f"必須キー '{key}' がありません")


def check_emoji(errs):
    """データファイルに未承認の絵文字が無いか。承認記号は除外する。"""
    for fn in ("data_products.py", "data_collab.py", "data_misc.py",
               "data_tech.py", "data_docs.py"):
        path = HERE / fn
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8")
        for i, line in enumerate(text.splitlines(), 1):
            for ch in _EMOJI_RE.findall(line):
                if ch in _ALLOWED_SYMBOLS:
                    continue
                name = unicodedata.name(ch, "UNKNOWN")
                _err(errs, f"{fn}:{i}", f"未承認の絵文字/記号 {ch!r}({name})")


def check_blocklist(errs):
    """機密ガード(任意)。禁止語はリポジトリ外に置く方針のため、環境変数
    SZ_BLOCKLIST_FILE でワードリストのパスを渡したときのみ、データ/生成物を検査する。"""
    bl = os.environ.get("SZ_BLOCKLIST_FILE")
    if not bl or not Path(bl).exists():
        return
    terms = [t.strip() for t in Path(bl).read_text(encoding="utf-8").splitlines() if t.strip()]
    if not terms:
        return
    scan_dirs = [HERE, HERE.parent / "assets", HERE.parent / "project-notes"]
    # 生成物も対象(あれば)
    for extra in ("collab", "news", "products", "index.html"):
        pth = HERE.parent / extra
        if pth.exists():
            scan_dirs.append(pth)
    hits = 0
    seen_files = set()
    for base in scan_dirs:
        files = [base] if base.is_file() else list(base.rglob("*"))
        for f in files:
            if not f.is_file() or f in seen_files:
                continue
            seen_files.add(f)
            if f.suffix not in (".py", ".js", ".css", ".html", ".md", ".txt"):
                continue
            try:
                txt = f.read_text(encoding="utf-8", errors="ignore")
            except Exception:
                continue
            for term in terms:
                if term and term in txt:
                    _err(errs, f"blocklist:{f.relative_to(HERE.parent)}", f"禁止語を検出しました")
                    hits += 1
    if hits == 0:
        print("  機密ガード: 禁止語の混入なし(SZ_BLOCKLIST_FILE 使用)")


def validate_all(strict=True):
    """全チェックを実行。NG があれば strict 時に SystemExit(1)。"""
    errs = []
    check_products(errs)
    check_collab(errs)
    check_news(errs)
    check_tech(errs)
    check_emoji(errs)
    check_blocklist(errs)
    if errs:
        print(f"データ検証: NG {len(errs)}件", file=sys.stderr)
        for e in errs:
            print("  - " + e, file=sys.stderr)
        if strict:
            raise SystemExit(1)
        return False
    print(f"データ検証: OK(製品{len(ALL_PRODUCTS + BIZ_PRODUCTS)} / コラボ{len(COLLABS)} / "
          f"ニュース{len(NEWS)} / 技術{len(TECHS)})")
    return True


if __name__ == "__main__":
    validate_all()
