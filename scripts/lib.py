# -*- coding: utf-8 -*-
"""共通ユーティリティ(純粋関数)。gen.py など複数の生成モジュールから import する。

状態を持たない小さなヘルパーをここに集約し、gen.py の肥大化を抑える。
出力は従来の gen.py 内定義と完全に一致させること(バイト単位で不変)。
"""
import re

__all__ = ["esc", "yen", "num", "slugify"]


def esc(s):
    """HTML特殊文字をエスケープする(属性・本文共用)。"""
    return (s.replace("&", "&amp;").replace("<", "&lt;")
            .replace(">", "&gt;").replace('"', "&quot;"))


def yen(n):
    """整数を「¥1,234」形式に整形する。"""
    return f"¥{n:,}"


def num(s):
    """文字列中の最初の数値(カンマ区切り可)を int で取り出す。無ければ0。"""
    m = re.search(r"([\d,]+)", s or "")
    return int(m.group(1).replace(",", "")) if m else 0


def slugify(t):
    """日本語を含むテキストからアンカー用スラッグを作る(英数・かな・漢字を残す)。"""
    return re.sub(r"[^0-9A-Za-z一-龠ぁ-んァ-ヶー]+", "-", t).lower()
