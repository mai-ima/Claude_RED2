# -*- coding: utf-8 -*-
"""リンク切れ検査 — 生成済みHTMLの全 href/src と #アンカーを検証する。

使い方:
    python3 scripts/gen.py && python3 scripts/check_links.py

終了コード 0 = リンク切れ0件。
"""
import re
import sys
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse, unquote

ROOT = Path(__file__).resolve().parent.parent
SKIP_DIRS = {".git", "src", "scripts", "node_modules"}
# fonts.* は外部フォント。suzaku.example.jp は自サイトの本番ドメイン
# (canonical / og:url / sitemap が自己参照の絶対URLで使う)。
EXTERNAL_ALLOW = {"fonts.googleapis.com", "fonts.gstatic.com", "suzaku.example.jp"}


class Collector(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []   # (attr値, 行番号)
        self.ids = set()

    def handle_starttag(self, tag, attrs):
        d = dict(attrs)
        for key in ("href", "src"):
            if key in d and d[key]:
                self.links.append((d[key], self.getpos()[0]))
        if "id" in d:
            self.ids.add(d["id"])
        if tag == "a" and "name" in d:
            self.ids.add(d["name"])


def page_files():
    for f in ROOT.rglob("*.html"):
        if not any(part in SKIP_DIRS for part in f.parts):
            yield f


def url_to_file(url_path):
    """サイト内URLパス→実ファイル。"""
    path = unquote(url_path)
    if path.endswith("/"):
        return ROOT / path.lstrip("/") / "index.html"
    p = ROOT / path.lstrip("/")
    if p.is_dir():
        return p / "index.html"
    return p


def main():
    pages = {}
    for f in page_files():
        c = Collector()
        c.feed(f.read_text(encoding="utf-8"))
        pages[f] = c

    errors = []
    checked = 0
    for f, c in pages.items():
        for raw, line in c.links:
            checked += 1
            u = urlparse(raw)
            if u.scheme in ("mailto", "tel", "javascript", "data"):
                continue
            if u.scheme in ("http", "https"):
                if u.netloc not in EXTERNAL_ALLOW:
                    errors.append(f"{f.relative_to(ROOT)}:{line}: 許可外の外部URL {raw}")
                continue
            # サイト内リンク
            path = u.path
            if path:
                if not path.startswith("/"):
                    errors.append(f"{f.relative_to(ROOT)}:{line}: 相対パスは禁止 {raw}")
                    continue
                target = url_to_file(path)
                if not target.exists():
                    errors.append(f"{f.relative_to(ROOT)}:{line}: リンク先なし {raw}")
                    continue
            else:
                target = f  # ページ内アンカー
            # アンカー検証
            if u.fragment:
                tf = target if target.suffix == ".html" else None
                if tf and tf in pages:
                    if u.fragment not in pages[tf].ids:
                        errors.append(f"{f.relative_to(ROOT)}:{line}: アンカーなし {raw}")
                elif tf and tf.exists():
                    c2 = Collector()
                    c2.feed(tf.read_text(encoding="utf-8"))
                    pages[tf] = c2
                    if u.fragment not in c2.ids:
                        errors.append(f"{f.relative_to(ROOT)}:{line}: アンカーなし {raw}")

    print(f"検査対象: {len(pages)}ページ / リンク{checked}件")
    if errors:
        print(f"\nリンク切れ {len(errors)}件:")
        for e in errors:
            print("  " + e)
        sys.exit(1)
    print("リンク切れ 0件: OK")


if __name__ == "__main__":
    main()
