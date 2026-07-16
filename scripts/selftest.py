# -*- coding: utf-8 -*-
"""SUZAKU サイトのスモークテスト(ワンコマンド品質ゲート)。

    python3 scripts/selftest.py            # 生成→検証→リンク検査→アサーション
    python3 scripts/selftest.py --no-build # 既存の生成物に対してのみ検査

CI やセッション開始時に走らせ、基盤が壊れていないことを1コマンドで保証する。
Playwright 監査(audit.js)は別途 Node が必要なため、ここでは含めない。
"""
import json
import subprocess
import sys
import xml.dom.minidom as minidom
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCRIPTS = ROOT / "scripts"

# 生成物に必ず存在してほしい代表ページ(壊れると即分かる要所)。
REQUIRED_FILES = [
    "index.html",
    "products/index.html",
    "products/phone/suzaku-4/index.html",
    "collab/index.html",
    "collab/genshin/cooling/index.html",
    "collab/wuwa/silicon/soc/index.html",
    "os/v4/index.html",
    "news/index.html",
    "business/kaname-b1/index.html",
    "sitemap.xml",
    "data/products.js",
]
MIN_PAGES = 220


def run(cmd):
    return subprocess.run(cmd, cwd=str(ROOT), capture_output=True, text=True)


def main():
    do_build = "--no-build" not in sys.argv
    fails = []

    if do_build:
        r = run([sys.executable, "scripts/gen.py"])
        sys.stdout.write(r.stdout)
        if r.returncode != 0:
            print(r.stderr, file=sys.stderr)
            fails.append("gen.py が異常終了")

    # 1) 代表ファイルの存在
    for rel in REQUIRED_FILES:
        if not (ROOT / rel).exists():
            fails.append(f"必須ファイルが無い: {rel}")

    # 2) ビルドレポートのページ数
    rep = ROOT / ".build" / "report.json"
    if rep.exists():
        data = json.loads(rep.read_text(encoding="utf-8"))
        if data.get("pages", 0) < MIN_PAGES:
            fails.append(f"ページ数が少なすぎる: {data.get('pages')} < {MIN_PAGES}")
        if data.get("duplicate_urls"):
            fails.append(f"重複URLがある: {data['duplicate_urls']}")
    else:
        fails.append(".build/report.json が無い(gen.py 未実行?)")

    # 3) sitemap.xml が整形式で、URL を十分含む
    sm = ROOT / "sitemap.xml"
    if sm.exists():
        try:
            dom = minidom.parseString(sm.read_text(encoding="utf-8"))
            locs = dom.getElementsByTagName("loc")
            if len(locs) < MIN_PAGES:
                fails.append(f"sitemap の URL 数が少ない: {len(locs)}")
        except Exception as e:
            fails.append(f"sitemap.xml が不正: {e}")

    # 4) データ検証(strict=False で結果だけ受け取る)
    sys.path.insert(0, str(SCRIPTS))
    try:
        from validate import validate_all
        if not validate_all(strict=False):
            fails.append("データ検証に失敗")
    except SystemExit:
        fails.append("データ検証が例外終了")

    # 5) リンク切れ検査
    r = run([sys.executable, "scripts/check_links.py"])
    if r.returncode != 0 or "リンク切れ 0件" not in r.stdout:
        sys.stdout.write(r.stdout)
        fails.append("リンク切れ検査に失敗")

    print("-" * 48)
    if fails:
        print(f"SELFTEST: NG {len(fails)}件", file=sys.stderr)
        for f in fails:
            print("  - " + f, file=sys.stderr)
        raise SystemExit(1)
    print("SELFTEST: OK — 生成・検証・リンク・整合すべて合格")


if __name__ == "__main__":
    main()
