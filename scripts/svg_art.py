# -*- coding: utf-8 -*-
"""SUZAKU サイト用SVGアート生成。

製品ビジュアル・技術ダイアグラム・アイコン類をすべてコードから生成する。
外部画像に一切依存しないため、画像のリンク切れが構造的に発生しない。
"""

import math


def _shade(hex_color, f):
    """hex色を明暗調整する。f>0 で白へ、f<0 で黒へ混ぜる(0〜±1)。"""
    h = hex_color.lstrip("#")
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    if f >= 0:
        r, g, b = (round(c + (255 - c) * f) for c in (r, g, b))
    else:
        r, g, b = (round(c * (1 + f)) for c in (r, g, b))
    return f"#{r:02x}{g:02x}{b:02x}"


def _is_light(hex_color):
    """ボディ色が明色かどうか(白銀・白練などで刻印を黒系に反転するため)。"""
    h = hex_color.lstrip("#")
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    return (0.2126 * r + 0.7152 * g + 0.0722 * b) > 150


def _phone_defs(gid, body_hex, tex_kind="matte"):
    """背面共通の材質定義(ボディ/フレーム/レンズ/シーン/テクスチャ/影)。"""
    lite = _shade(body_hex, 0.42)
    lite2 = _shade(body_hex, 0.16)
    dark = _shade(body_hex, -0.38)
    dark2 = _shade(body_hex, -0.6)
    if tex_kind == "carbon":
        tex = f"""<pattern id="tex{gid}" width="8" height="8" patternUnits="userSpaceOnUse" patternTransform="rotate(45)">
  <path d="M0 0 V8 M4 0 V8" stroke="#ffffff" stroke-opacity="0.05" stroke-width="1.4"/>
  <path d="M0 0 H8" stroke="#000000" stroke-opacity="0.14" stroke-width="1.4"/>
</pattern>"""
    elif tex_kind == "hairline":
        tex = f"""<pattern id="tex{gid}" width="6" height="3" patternUnits="userSpaceOnUse">
  <path d="M0 1 H6" stroke="#ffffff" stroke-opacity="0.05" stroke-width="1"/>
</pattern>"""
    elif tex_kind == "gloss":
        tex = f"""<pattern id="tex{gid}" width="10" height="10" patternUnits="userSpaceOnUse">
  <path d="M0 0" stroke="none"/>
</pattern>"""
    else:  # matte: 微細ノイズドット
        tex = f"""<pattern id="tex{gid}" width="9" height="9" patternUnits="userSpaceOnUse">
  <circle cx="2" cy="3" r="0.7" fill="#ffffff" fill-opacity="0.045"/>
  <circle cx="6.5" cy="7" r="0.6" fill="#000000" fill-opacity="0.1"/>
</pattern>"""
    return f"""<defs>
<linearGradient id="body{gid}" x1="0" y1="0" x2="0.9" y2="1">
  <stop offset="0" stop-color="{lite}"/>
  <stop offset="0.28" stop-color="{lite2}"/>
  <stop offset="0.62" stop-color="{body_hex}"/>
  <stop offset="1" stop-color="{dark}"/>
</linearGradient>
<linearGradient id="frame{gid}" x1="0" y1="0" x2="0" y2="1">
  <stop offset="0" stop-color="{_shade(body_hex, 0.55)}"/>
  <stop offset="0.12" stop-color="{_shade(body_hex, -0.15)}"/>
  <stop offset="0.5" stop-color="{dark2}"/>
  <stop offset="0.88" stop-color="{_shade(body_hex, -0.2)}"/>
  <stop offset="1" stop-color="{_shade(body_hex, 0.35)}"/>
</linearGradient>
<radialGradient id="lens{gid}" cx="0.38" cy="0.32" r="0.95">
  <stop offset="0" stop-color="#3c4454"/>
  <stop offset="0.35" stop-color="#141821"/>
  <stop offset="1" stop-color="#04040a"/>
</radialGradient>
<linearGradient id="sheen{gid}" x1="0" y1="0" x2="1" y2="1">
  <stop offset="0" stop-color="#ffffff" stop-opacity="{0.4 if tex_kind == 'gloss' else 0.28}"/>
  <stop offset="0.5" stop-color="#ffffff" stop-opacity="0.03"/>
  <stop offset="1" stop-color="#ffffff" stop-opacity="0"/>
</linearGradient>
{tex}
<filter id="soft{gid}" x="-40%" y="-40%" width="180%" height="180%">
  <feGaussianBlur stdDeviation="7"/>
</filter>
</defs>"""


def _lens(cx, cy, r, gid, body_hex, glow):
    """単一の円形レンズ(外環+グローリング+ガラス+瞳+スペキュラ)。"""
    return f"""
<circle cx="{cx}" cy="{cy}" r="{r}" fill="#0b0d13" stroke="{_shade(body_hex, 0.3)}" stroke-width="1.6"/>
<circle cx="{cx}" cy="{cy}" r="{r * 0.76:.0f}" fill="none" stroke="{glow}" stroke-opacity="0.5" stroke-width="1.3"/>
<circle cx="{cx}" cy="{cy}" r="{r * 0.6:.0f}" fill="url(#lens{gid})"/>
<circle cx="{cx}" cy="{cy}" r="{r * 0.22:.0f}" fill="#04040a"/>
<circle cx="{cx - r * 0.22:.0f}" cy="{cy - r * 0.24:.0f}" r="{max(2.4, r * 0.14):.1f}" fill="#ffffff" opacity="0.55"/>"""


def _peri_cell(x, y, w, gid, body_hex, glow):
    """ペリスコープ望遠の角形セル。"""
    return f"""
<rect x="{x}" y="{y}" width="{w}" height="{w}" rx="{w * 0.22:.0f}" fill="#0b0d13" stroke="{_shade(body_hex, 0.3)}" stroke-width="1.6"/>
<rect x="{x + w * 0.16:.0f}" y="{y + w * 0.16:.0f}" width="{w * 0.68:.0f}" height="{w * 0.68:.0f}" rx="{w * 0.14:.0f}" fill="none" stroke="{glow}" stroke-opacity="0.5" stroke-width="1.3"/>
<circle cx="{x + w / 2:.0f}" cy="{y + w / 2:.0f}" r="{w * 0.24:.0f}" fill="url(#lens{gid})"/>
<circle cx="{x + w / 2:.0f}" cy="{y + w / 2:.0f}" r="{w * 0.09:.0f}" fill="#04040a"/>"""


def _phone_camera(d, gid, body_hex, glow, ink):
    """designプロファイル(plate/cams/tele/macro)に従ってカメラ島を描く。
    レンズ数・構成はspecsのリアカメラ表記と一致させる。
    戻り値: (svg断片, プレート下端y)。LED等の干渉防止に使う。"""
    plate_kind = d.get("plate", "band")
    cams = d.get("cams", 2)
    plate_fill = _shade(body_hex, -0.3)
    bottom = 154
    out = ""
    if plate_kind == "band":
        # 全幅の帯型プレート(現行旗艦)。丸レンズ cams 個 + tele で角形セル
        slots = cams + (1 if d.get("tele") else 0)
        xs = {1: [170], 2: [130, 210], 3: [108, 170, 232]}[slots]
        out += f"""
<rect x="66" y="64" width="208" height="90" rx="26" fill="{plate_fill}"/>
<rect x="66" y="64" width="208" height="90" rx="26" fill="url(#sheen{gid})" opacity="0.5"/>
<rect x="66.7" y="64.7" width="206.6" height="88.6" rx="25.3" fill="none" stroke="#ffffff" stroke-opacity="0.12" stroke-width="1.4"/>
<circle cx="86" cy="80" r="5" fill="#f4efdf" opacity="0.9"/>
<text x="262" y="83" font-family="'Noto Sans JP',sans-serif" font-size="8.5" font-weight="700" fill="{ink}" opacity="0.5" text-anchor="end" letter-spacing="2">TENGAN</text>"""
        for i, cx in enumerate(xs):
            if d.get("tele") and i == len(xs) - 1:
                out += _peri_cell(cx - 24, 92, 48, gid, body_hex, glow)
            else:
                out += _lens(cx, 116, 25, gid, body_hex, glow)
    elif plate_kind == "pill":
        # 縦長ピル(左上)。レンズ縦積み
        h = 76 + cams * 62
        bottom = 58 + h
        out += f"""
<rect x="66" y="58" width="88" height="{h}" rx="44" fill="{plate_fill}"/>
<rect x="66" y="58" width="88" height="{h}" rx="44" fill="url(#sheen{gid})" opacity="0.5"/>
<rect x="66.7" y="58.7" width="86.6" height="{h - 1.4}" rx="43.3" fill="none" stroke="#ffffff" stroke-opacity="0.12" stroke-width="1.4"/>
<circle cx="186" cy="86" r="6" fill="#f4efdf" opacity="0.9"/>
<text x="186" y="118" font-family="'Noto Sans JP',sans-serif" font-size="8" font-weight="700" fill="{ink}" opacity="0.5" letter-spacing="2" text-anchor="middle">TENGAN</text>"""
        for i in range(cams):
            out += _lens(110, 102 + i * 62, 27, gid, body_hex, glow)
    elif plate_kind == "square":
        # 角形プレート(左上)・レンズ斜め配置
        bottom = 184
        out += f"""
<rect x="66" y="58" width="126" height="126" rx="20" fill="{plate_fill}"/>
<rect x="66" y="58" width="126" height="126" rx="20" fill="url(#sheen{gid})" opacity="0.5"/>
<rect x="66.7" y="58.7" width="124.6" height="124.6" rx="19.3" fill="none" stroke="#ffffff" stroke-opacity="0.12" stroke-width="1.4"/>
<circle cx="168" cy="86" r="5.5" fill="#f4efdf" opacity="0.9"/>"""
        out += _lens(102, 94, 24, gid, body_hex, glow)
        if cams >= 2:
            out += _lens(156, 148, 24, gid, body_hex, glow)
        out += f'<circle cx="102" cy="152" r="7" fill="#0b0d13" stroke="{_shade(body_hex, 0.3)}" stroke-width="1.2"/>'
    elif plate_kind == "circle":
        # 大円プレート(初代旗艦の意匠)
        bottom = 192
        out += f"""
<circle cx="170" cy="128" r="64" fill="{plate_fill}"/>
<circle cx="170" cy="128" r="64" fill="url(#sheen{gid})" opacity="0.5"/>
<circle cx="170" cy="128" r="63.3" fill="none" stroke="#ffffff" stroke-opacity="0.12" stroke-width="1.4"/>
<circle cx="170" cy="128" r="56" fill="none" stroke="{glow}" stroke-opacity="0.35" stroke-width="1.4"/>"""
        if cams == 1:
            out += _lens(170, 128, 30, gid, body_hex, glow)
        else:
            out += _lens(143, 128, 22, gid, body_hex, glow) + _lens(197, 128, 22, gid, body_hex, glow)
        out += '<circle cx="170" cy="176" r="4.5" fill="#f4efdf" opacity="0.9"/>'
    elif plate_kind == "diag":
        # 斜めプレート(NEO系)・レンズを斜めに段付き配置
        bottom = 170
        out += f"""
<path d="M66 70 h158 a18 18 0 0 1 17 23 l-18 64 a18 18 0 0 1 -17 13 h-140 a18 18 0 0 1 -18 -18 v-64 a18 18 0 0 1 18 -18z" fill="{plate_fill}"/>
<path d="M66 70 h158 a18 18 0 0 1 17 23 l-18 64 a18 18 0 0 1 -17 13 h-140 a18 18 0 0 1 -18 -18 v-64 a18 18 0 0 1 18 -18z" fill="url(#sheen{gid})" opacity="0.5"/>
<circle cx="222" cy="152" r="5" fill="#f4efdf" opacity="0.9"/>
<text x="94" y="160" font-family="'Noto Sans JP',sans-serif" font-size="8" font-weight="700" fill="{ink}" opacity="0.5" letter-spacing="2">TENGAN</text>"""
        out += _lens(112, 108, 26, gid, body_hex, glow)
        if cams >= 2:
            out += _lens(186, 116, 22, gid, body_hex, glow)
    else:
        # corner: 角丸スクエア(左上)・スタンダード系
        if cams == 1 and not d.get("macro"):
            bottom = 150
            out += f"""
<rect x="66" y="58" width="92" height="92" rx="26" fill="{plate_fill}"/>
<rect x="66" y="58" width="92" height="92" rx="26" fill="url(#sheen{gid})" opacity="0.5"/>
<rect x="66.7" y="58.7" width="90.6" height="90.6" rx="25.3" fill="none" stroke="#ffffff" stroke-opacity="0.12" stroke-width="1.4"/>"""
            out += _lens(112, 104, 28, gid, body_hex, glow)
            out += '<circle cx="182" cy="76" r="5" fill="#f4efdf" opacity="0.9"/>'
        else:
            h = 158 if (cams >= 2 or d.get("macro")) else 92
            bottom = 58 + h
            out += f"""
<rect x="66" y="58" width="92" height="{h}" rx="26" fill="{plate_fill}"/>
<rect x="66" y="58" width="92" height="{h}" rx="26" fill="url(#sheen{gid})" opacity="0.5"/>
<rect x="66.7" y="58.7" width="90.6" height="{h - 1.4}" rx="25.3" fill="none" stroke="#ffffff" stroke-opacity="0.12" stroke-width="1.4"/>
<circle cx="182" cy="76" r="5" fill="#f4efdf" opacity="0.9"/>"""
            out += _lens(112, 100, 26, gid, body_hex, glow)
            if d.get("macro"):
                out += _lens(112, 168, 13, gid, body_hex, glow)
            elif cams >= 2:
                out += _lens(112, 168, 22, gid, body_hex, glow)
    return out, bottom


def svg_phone(pid, body_hex, glow, label, kana="", line="suzaku", hz="144Hz", design=None):
    """スマートフォン背面ビュー(実機比率 約76.5×164mm ≒ 1:2.15)。

    designプロファイル(data_products.py)駆動で、カメラ構成・プレート形状・
    LED・テクスチャ・ファン窓を機種ごとに変える。specsの記載と描画を一致させ、
    廉価版/最上級/旧世代の背面がすべて判別できるようにする。
    コラボ機は _PHONE_CUSTOM の完全専用描画に委譲する。"""
    d = design or {}
    if d.get("custom"):
        return _PHONE_CUSTOM[d["custom"]](pid, body_hex, glow, label, kana, hz)

    gid = pid.replace("-", "")
    gaming = d.get("fan", line in ("suzaku", "neo", "collab"))
    dark2 = _shade(body_hex, -0.6)
    light_body = _is_light(body_hex)
    ink = "#1c1c26" if light_body else "#ffffff"
    blade = _shade(body_hex, -0.35) if light_body else _shade(body_hex, 0.22)
    tex_kind = d.get("tex", "matte")

    defs = _phone_defs(gid, body_hex, tex_kind)
    if d.get("cams") == 0:
        # カメラレス(セキュア仕様): レンズの代わりに盾の刻印+規格表記
        camera = f"""
<rect x="66" y="60" width="208" height="92" rx="18" fill="none" stroke="{ink}" stroke-opacity="0.16" stroke-width="1.4"/>
<path d="M170 76 l22 10 v15 c0 14 -10 23 -22 28 c-12 -5 -22 -14 -22 -28 v-15 z" fill="none" stroke="{glow}" stroke-width="2.4" stroke-linejoin="round"/>
<path d="M161 103 l7 7 12 -14" fill="none" stroke="{glow}" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"/>
<text x="170" y="142" font-family="'Noto Sans JP',sans-serif" font-size="8" font-weight="700" fill="{ink}" opacity="0.55" text-anchor="middle" letter-spacing="3">SECURE ・ NO CAMERA</text>"""
        plate_bottom = 152
    else:
        camera, plate_bottom = _phone_camera(d, gid, body_hex, glow, ink)

    # LED意匠(カメラ島の下端から距離を取り干渉を防ぐ)
    led_kind = d.get("led", "none")
    led = ""
    led_y = plate_bottom + 24
    if led_kind.startswith("slash"):
        n = int(led_kind[-1])
        ops = (0.92, 0.55, 0.28)[:n]
        led = "".join(
            f'<path d="M{66 + i * 66} {led_y} h44 l-13 13 h-44 z" fill="{glow}" opacity="{o}"/>'
            for i, o in enumerate(ops))
    elif led_kind == "dot":
        led = "".join(
            f'<circle cx="{92 + i * 26}" cy="{led_y + 6}" r="5" fill="{glow}" opacity="{0.9 - i * 0.28}"/>'
            for i in range(3))

    # 中央の特徴(ファン窓 or エンブレム)
    if gaming:
        blades = "".join(
            f'<path d="M170 328 L170 296" stroke="{blade}" stroke-width="9" stroke-linecap="round" transform="rotate({a} 170 328)"/>'
            for a in range(0, 360, 40))
        feature = f"""
<circle cx="170" cy="328" r="50" fill="{dark2}"/>
<circle cx="170" cy="328" r="50" fill="none" stroke="{glow}" stroke-opacity="0.55" stroke-width="2"/>
<circle cx="170" cy="328" r="42" fill="#0a0b10"/>
{blades}
<circle cx="170" cy="328" r="13" fill="#101018" stroke="{glow}" stroke-opacity="0.8" stroke-width="1.6"/>
<circle cx="170" cy="328" r="4" fill="{glow}"/>
<text x="170" y="398" font-family="'Noto Sans JP',sans-serif" font-size="9" font-weight="700" fill="{ink}" opacity="0.5" text-anchor="middle" letter-spacing="3">SENPU COOLING</text>"""
        side_r = f"""
<rect x="292.5" y="112" width="5" height="44" rx="2.5" fill="{glow}"/>
<rect x="292.5" y="172" width="5" height="44" rx="2.5" fill="{glow}"/>
<rect x="292.5" y="250" width="5" height="48" rx="2.5" fill="{dark2}"/>"""
    else:
        feature = f"""
<g transform="translate(122 268) scale(2)" opacity="0.9">
  <path d="M24 6 C21.4 16.5 12 21 12 30 a12 12 0 0 0 24 0 C36 21 26.6 16.5 24 6 Z" fill="none" stroke="{glow}" stroke-width="2.6" stroke-linejoin="round"/>
  <circle cx="24" cy="31.5" r="3.2" fill="{glow}"/>
</g>"""
        side_r = f'<rect x="292.5" y="162" width="5" height="56" rx="2.5" fill="{dark2}"/>'

    # 刻印(長いコラボ名は「×」で2行に分割してはみ出しを防ぐ)
    if "×" in label and len(label) > 14:
        l1, l2 = (s.strip() for s in label.split("×", 1))
        etched = f"""
<text x="170" y="452" font-family="'Noto Sans JP',sans-serif" font-size="13" font-weight="800" fill="{ink}" opacity="0.72" text-anchor="middle" letter-spacing="1.5">{l1} ×</text>
<text x="170" y="470" font-family="'Noto Sans JP',sans-serif" font-size="12" font-weight="700" fill="{ink}" opacity="0.6" text-anchor="middle" letter-spacing="1">{l2}</text>"""
    else:
        etched = f"""
<text x="170" y="462" font-family="'Noto Sans JP',sans-serif" font-size="14.5" font-weight="800" fill="{ink}" opacity="0.72" text-anchor="middle" letter-spacing="2.5">{label}</text>"""
    if kana:
        etched += f"""
<text x="170" y="487" font-family="'Noto Sans JP',sans-serif" font-size="9" fill="{ink}" opacity="0.4" text-anchor="middle" letter-spacing="4">{kana}</text>"""

    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 340 600" role="img" aria-label="{label}">
{defs}
<ellipse cx="170" cy="577" rx="116" ry="13" fill="#000000" opacity="0.4" filter="url(#soft{gid})"/>
<rect x="43" y="30" width="254" height="540" rx="47" fill="url(#frame{gid})"/>
<rect x="49" y="36" width="242" height="528" rx="42" fill="{body_hex}"/>
<rect x="49" y="36" width="242" height="528" rx="42" fill="url(#body{gid})"/>
<rect x="49" y="36" width="242" height="528" rx="42" fill="url(#tex{gid})"/>
<rect x="50" y="37" width="240" height="526" rx="41" fill="none" stroke="#ffffff" stroke-opacity="0.14" stroke-width="1.6"/>
<path d="M43 128 h6 M43 448 h6 M291 128 h6 M291 448 h6" stroke="{dark2}" stroke-width="3"/>
{camera}
{led}
{feature}
{etched}
<text x="170" y="546" font-family="'Noto Sans JP',sans-serif" font-size="8" fill="{ink}" opacity="0.38" text-anchor="middle" letter-spacing="2">DESIGNED BY SUZAKU ・ {hz}</text>
<path d="M78 36 L206 36 L96 564 L49 564 L49 300 Z" fill="url(#sheen{gid})"/>
<path d="M232 36 L262 36 L150 564 L124 564 Z" fill="#ffffff" opacity="0.05"/>
{side_r}
<rect x="42.5" y="146" width="5" height="62" rx="2.5" fill="{dark2}"/>
</svg>"""


# ==========================================================================
# コラボ4機種の完全専用背面(共通フレームを使わないゼロ設計)
# ==========================================================================

def _phone_shichiyo(pid, body_hex, glow, label, kana, hz):
    """七耀(原神): 白磁×金彩・中央円形デュアルカメラ+七元素リング発光。"""
    gid = pid.replace("-", "")
    gold = "#c9a24b"
    gold_d = "#8d6c1e"
    ink = "#3a3324" if _is_light(body_hex) else "#f4efe0"
    elems = ("#74c2a8", "#d8b45c", "#a68cc8", "#9ac546", "#4cc2f1", "#ef7938", "#9fd6e3")
    ring_dots = ""
    for i, c in enumerate(elems):
        a = math.radians(-90 + i * 360 / 7)
        x, y = 170 + 96 * math.cos(a), 150 + 96 * math.sin(a)
        ring_dots += f'<circle cx="{x:.1f}" cy="{y:.1f}" r="5.5" fill="{c}"/><circle cx="{x:.1f}" cy="{y:.1f}" r="9" fill="none" stroke="{c}" stroke-opacity="0.4" stroke-width="1.4"/>'
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 340 600" role="img" aria-label="{label}">
<defs>
<linearGradient id="body{gid}" x1="0" y1="0" x2="0.85" y2="1">
  <stop offset="0" stop-color="{_shade(body_hex, 0.5)}"/>
  <stop offset="0.3" stop-color="{_shade(body_hex, 0.18)}"/>
  <stop offset="0.62" stop-color="{body_hex}"/>
  <stop offset="1" stop-color="{_shade(body_hex, -0.16)}"/>
</linearGradient>
<linearGradient id="irid{gid}" x1="0" y1="0" x2="1" y2="1">
  <stop offset="0" stop-color="#2fb9a3" stop-opacity="0.1"/>
  <stop offset="0.5" stop-color="#cbb26a" stop-opacity="0.12"/>
  <stop offset="1" stop-color="#a68cc8" stop-opacity="0.1"/>
</linearGradient>
<linearGradient id="frame{gid}" x1="0" y1="0" x2="0" y2="1">
  <stop offset="0" stop-color="#e8d391"/>
  <stop offset="0.5" stop-color="{gold_d}"/>
  <stop offset="1" stop-color="#dcc57e"/>
</linearGradient>
<radialGradient id="lens{gid}" cx="0.38" cy="0.32" r="0.95">
  <stop offset="0" stop-color="#3c4454"/><stop offset="0.35" stop-color="#141821"/><stop offset="1" stop-color="#04040a"/>
</radialGradient>
<filter id="soft{gid}" x="-40%" y="-40%" width="180%" height="180%"><feGaussianBlur stdDeviation="7"/></filter>
</defs>
<ellipse cx="170" cy="577" rx="116" ry="13" fill="#000000" opacity="0.35" filter="url(#soft{gid})"/>
<rect x="43" y="30" width="254" height="540" rx="47" fill="url(#frame{gid})"/>
<rect x="49" y="36" width="242" height="528" rx="42" fill="{body_hex}"/>
<rect x="49" y="36" width="242" height="528" rx="42" fill="url(#body{gid})"/>
<rect x="49" y="36" width="242" height="528" rx="42" fill="url(#irid{gid})"/>
<rect x="50.2" y="37.2" width="239.6" height="525.6" rx="40.8" fill="none" stroke="#ffffff" stroke-opacity="0.5" stroke-width="1.2"/>
<circle cx="170" cy="150" r="96" fill="none" stroke="{gold}" stroke-opacity="0.55" stroke-width="1.6" stroke-dasharray="2 5"/>
{ring_dots}
<circle cx="170" cy="150" r="66" fill="{_shade(body_hex, -0.12)}" stroke="{gold}" stroke-width="2.4"/>
<circle cx="170" cy="150" r="58" fill="none" stroke="{gold}" stroke-opacity="0.5" stroke-width="1"/>
<circle cx="145" cy="150" r="23" fill="#0b0d13" stroke="{gold}" stroke-width="1.6"/>
<circle cx="145" cy="150" r="17" fill="none" stroke="#2fb9a3" stroke-opacity="0.55" stroke-width="1.2"/>
<circle cx="145" cy="150" r="13" fill="url(#lens{gid})"/>
<circle cx="140" cy="144" r="3" fill="#ffffff" opacity="0.55"/>
<circle cx="196" cy="150" r="23" fill="#0b0d13" stroke="{gold}" stroke-width="1.6"/>
<circle cx="196" cy="150" r="17" fill="none" stroke="#2fb9a3" stroke-opacity="0.55" stroke-width="1.2"/>
<circle cx="196" cy="150" r="13" fill="url(#lens{gid})"/>
<circle cx="191" cy="144" r="3" fill="#ffffff" opacity="0.55"/>
<circle cx="170" cy="186" r="7" fill="#101018" stroke="{gold}" stroke-width="1.3"/>
<circle cx="170" cy="186" r="3" fill="#2fb9a3"/>
<circle cx="170" cy="114" r="4.5" fill="#f4efdf" stroke="{gold}" stroke-width="1"/>
<text x="170" y="292" font-family="'Noto Sans JP',sans-serif" font-size="9" font-weight="700" fill="{gold_d}" opacity="0.85" text-anchor="middle" letter-spacing="5">ELEMENTAL RING</text>
<path d="M60 320 H280" stroke="{gold}" stroke-opacity="0.5" stroke-width="1"/>
<g transform="translate(146 348) scale(1)" opacity="0.95">
  <path d="M24 6 C21.4 16.5 12 21 12 30 a12 12 0 0 0 24 0 C36 21 26.6 16.5 24 6 Z" fill="none" stroke="{gold_d}" stroke-width="2.4" stroke-linejoin="round"/>
  <circle cx="24" cy="31.5" r="3" fill="{gold_d}"/>
</g>
<path d="M60 412 H280" stroke="{gold}" stroke-opacity="0.5" stroke-width="1"/>
<text x="170" y="452" font-family="'Shippori Mincho','Noto Sans JP',serif" font-size="15" font-weight="800" fill="{ink}" opacity="0.85" text-anchor="middle" letter-spacing="3">SUZAKU × 原神</text>
<text x="170" y="476" font-family="'Shippori Mincho','Noto Sans JP',serif" font-size="20" font-weight="800" fill="{gold_d}" text-anchor="middle" letter-spacing="10">七 耀</text>
<text x="170" y="546" font-family="'Noto Sans JP',sans-serif" font-size="8" fill="{ink}" opacity="0.45" text-anchor="middle" letter-spacing="2">SHICHIYO ・ JOINT DESIGN ・ {hz}</text>
<path d="M84 36 L200 36 L100 564 L49 564 L49 320 Z" fill="#ffffff" opacity="0.16"/>
<rect x="292.5" y="140" width="5" height="48" rx="2.5" fill="{gold_d}"/>
<rect x="292.5" y="202" width="5" height="70" rx="2.5" fill="{gold_d}"/>
</svg>"""


def _phone_zankyo(pid, body_hex, glow, label, kana, hz):
    """残響(鳴潮): 漆黒モノリス・縦列トリプル(丸2+角形ペリスコ)・音叉LED。"""
    gid = pid.replace("-", "")
    light_body = _is_light(body_hex)
    ink = "#1c1c26" if light_body else "#e9e9f0"
    ln = _shade(body_hex, -0.35) if light_body else _shade(body_hex, 0.3)
    cyan = "#00e0ff"
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 340 600" role="img" aria-label="{label}">
<defs>
<linearGradient id="body{gid}" x1="0" y1="0" x2="0.85" y2="1">
  <stop offset="0" stop-color="{_shade(body_hex, 0.26)}"/>
  <stop offset="0.5" stop-color="{body_hex}"/>
  <stop offset="1" stop-color="{_shade(body_hex, -0.34)}"/>
</linearGradient>
<linearGradient id="frame{gid}" x1="0" y1="0" x2="0" y2="1">
  <stop offset="0" stop-color="{_shade(body_hex, 0.4)}"/>
  <stop offset="0.5" stop-color="{_shade(body_hex, -0.55)}"/>
  <stop offset="1" stop-color="{_shade(body_hex, 0.22)}"/>
</linearGradient>
<radialGradient id="lens{gid}" cx="0.38" cy="0.32" r="0.95">
  <stop offset="0" stop-color="#39414f"/><stop offset="0.35" stop-color="#12151d"/><stop offset="1" stop-color="#04040a"/>
</radialGradient>
<pattern id="tex{gid}" width="4" height="7" patternUnits="userSpaceOnUse">
  <path d="M1 0 V7" stroke="{'#000000' if light_body else '#ffffff'}" stroke-opacity="0.05" stroke-width="1"/>
</pattern>
<filter id="soft{gid}" x="-40%" y="-40%" width="180%" height="180%"><feGaussianBlur stdDeviation="7"/></filter>
</defs>
<ellipse cx="170" cy="577" rx="112" ry="12" fill="#000000" opacity="0.5" filter="url(#soft{gid})"/>
<rect x="45" y="30" width="250" height="540" rx="16" fill="url(#frame{gid})"/>
<rect x="50" y="35" width="240" height="530" rx="12" fill="{body_hex}"/>
<rect x="50" y="35" width="240" height="530" rx="12" fill="url(#body{gid})"/>
<rect x="50" y="35" width="240" height="530" rx="12" fill="url(#tex{gid})"/>
<rect x="51" y="36" width="238" height="528" rx="11" fill="none" stroke="#ffffff" stroke-opacity="0.1" stroke-width="1.2"/>
<rect x="66" y="54" width="86" height="228" rx="12" fill="{_shade(body_hex, -0.28)}"/>
<rect x="66.6" y="54.6" width="84.8" height="226.8" rx="11.4" fill="none" stroke="#ffffff" stroke-opacity="0.1" stroke-width="1.2"/>
<circle cx="109" cy="94" r="26" fill="#0b0d13" stroke="{ln}" stroke-width="1.5"/>
<circle cx="109" cy="94" r="19" fill="none" stroke="{cyan}" stroke-opacity="0.4" stroke-width="1.2"/>
<circle cx="109" cy="94" r="15" fill="url(#lens{gid})"/>
<circle cx="103" cy="88" r="3.2" fill="#ffffff" opacity="0.5"/>
<circle cx="109" cy="158" r="26" fill="#0b0d13" stroke="{ln}" stroke-width="1.5"/>
<circle cx="109" cy="158" r="19" fill="none" stroke="{cyan}" stroke-opacity="0.4" stroke-width="1.2"/>
<circle cx="109" cy="158" r="15" fill="url(#lens{gid})"/>
<circle cx="103" cy="152" r="3.2" fill="#ffffff" opacity="0.5"/>
<rect x="83" y="204" width="52" height="52" rx="11" fill="#0b0d13" stroke="{ln}" stroke-width="1.5"/>
<rect x="92" y="213" width="34" height="34" rx="8" fill="none" stroke="{cyan}" stroke-opacity="0.4" stroke-width="1.2"/>
<circle cx="109" cy="230" r="10" fill="url(#lens{gid})"/>
<circle cx="178" cy="70" r="5" fill="#f4efdf" opacity="0.9"/>
<text x="178" y="98" font-family="'Noto Sans JP',sans-serif" font-size="7.5" fill="{ink}" opacity="0.5" letter-spacing="2">50MP ×2</text>
<text x="178" y="112" font-family="'Noto Sans JP',sans-serif" font-size="7.5" fill="{ink}" opacity="0.5" letter-spacing="2">64MP PERI</text>
<path d="M158 330 v54 M182 330 v54 M158 384 a12 12 0 0 0 24 0" fill="none" stroke="{cyan}" stroke-opacity="0.75" stroke-width="3" stroke-linecap="round"/>
<path d="M146 344 h-10 M204 344 h-10" stroke="{cyan}" stroke-opacity="0.35" stroke-width="2" stroke-linecap="round"/>
<text x="170" y="428" font-family="'Noto Sans JP',sans-serif" font-size="8" fill="{ink}" opacity="0.5" text-anchor="middle" letter-spacing="4">RESONANCE FORK</text>
<text x="170" y="474" font-family="'Zen Old Mincho','Noto Sans JP',serif" font-size="19" font-weight="900" fill="{ink}" opacity="0.85" text-anchor="middle" letter-spacing="12">残 響</text>
<text x="170" y="496" font-family="'Noto Sans JP',sans-serif" font-size="8.5" fill="{ink}" opacity="0.45" text-anchor="middle" letter-spacing="3">SUZAKU × 鳴潮 ・ ZANKYO</text>
<text x="170" y="546" font-family="'Noto Sans JP',sans-serif" font-size="8" fill="{ink}" opacity="0.38" text-anchor="middle" letter-spacing="2">MONOLITH 8.2mm ・ {hz}</text>
<path d="M70 35 L180 35 L92 565 L50 565 L50 300 Z" fill="#ffffff" opacity="{0.12 if light_body else 0.045}"/>
<rect x="292.5" y="128" width="5" height="44" rx="2.5" fill="{cyan}" opacity="0.85"/>
<rect x="292.5" y="184" width="5" height="66" rx="2.5" fill="{_shade(body_hex, -0.5)}"/>
</svg>"""


def _phone_yako(pid, body_hex, glow, label, kana, hz):
    """夜行(NTE): EL発光ガラス背面・超大型デュアルカメラ・ネオン管サイン。"""
    gid = pid.replace("-", "")
    ink = "#1c1c26" if _is_light(body_hex) else "#f4ecff"
    mag = "#ff3ea5"
    cyanc = "#39d7f5"
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 340 600" role="img" aria-label="{label}">
<defs>
<linearGradient id="body{gid}" x1="0" y1="0" x2="0.85" y2="1">
  <stop offset="0" stop-color="{_shade(body_hex, 0.34)}"/>
  <stop offset="0.32" stop-color="{_shade(body_hex, 0.1)}"/>
  <stop offset="0.66" stop-color="{body_hex}"/>
  <stop offset="1" stop-color="{_shade(body_hex, -0.4)}"/>
</linearGradient>
<linearGradient id="frame{gid}" x1="0" y1="0" x2="0" y2="1">
  <stop offset="0" stop-color="{_shade(body_hex, 0.5)}"/>
  <stop offset="0.5" stop-color="{_shade(body_hex, -0.6)}"/>
  <stop offset="1" stop-color="{_shade(body_hex, 0.3)}"/>
</linearGradient>
<radialGradient id="lens{gid}" cx="0.38" cy="0.32" r="0.95">
  <stop offset="0" stop-color="#3c4454"/><stop offset="0.35" stop-color="#141821"/><stop offset="1" stop-color="#04040a"/>
</radialGradient>
<filter id="glow{gid}" x="-60%" y="-60%" width="220%" height="220%"><feGaussianBlur stdDeviation="4"/></filter>
<filter id="soft{gid}" x="-40%" y="-40%" width="180%" height="180%"><feGaussianBlur stdDeviation="7"/></filter>
</defs>
<ellipse cx="170" cy="577" rx="116" ry="13" fill="#000000" opacity="0.5" filter="url(#soft{gid})"/>
<rect x="43" y="30" width="254" height="540" rx="40" fill="url(#frame{gid})"/>
<rect x="49" y="36" width="242" height="528" rx="35" fill="{body_hex}"/>
<rect x="49" y="36" width="242" height="528" rx="35" fill="url(#body{gid})"/>
<rect x="55" y="42" width="230" height="516" rx="30" fill="none" stroke="{mag}" stroke-opacity="0.4" stroke-width="1.6"/>
<rect x="66" y="62" width="208" height="116" rx="34" fill="{_shade(body_hex, -0.3)}"/>
<rect x="66.7" y="62.7" width="206.6" height="114.6" rx="33.3" fill="none" stroke="#ffffff" stroke-opacity="0.14" stroke-width="1.4"/>
<circle cx="122" cy="120" r="36" fill="#0b0d13" stroke="{_shade(body_hex, 0.35)}" stroke-width="1.8"/>
<circle cx="122" cy="120" r="28" fill="none" stroke="{mag}" stroke-opacity="0.55" stroke-width="1.4"/>
<circle cx="122" cy="120" r="22" fill="url(#lens{gid})"/>
<circle cx="122" cy="120" r="8" fill="#04040a"/>
<circle cx="113" cy="110" r="4.5" fill="#ffffff" opacity="0.55"/>
<circle cx="212" cy="120" r="30" fill="#0b0d13" stroke="{_shade(body_hex, 0.35)}" stroke-width="1.8"/>
<circle cx="212" cy="120" r="23" fill="none" stroke="{cyanc}" stroke-opacity="0.5" stroke-width="1.4"/>
<circle cx="212" cy="120" r="17" fill="url(#lens{gid})"/>
<circle cx="205" cy="112" r="3.8" fill="#ffffff" opacity="0.55"/>
<circle cx="256" cy="86" r="5" fill="#f4efdf" opacity="0.9"/>
<text x="256" y="152" font-family="'Noto Sans JP',sans-serif" font-size="7.5" fill="{ink}" opacity="0.55" text-anchor="middle" letter-spacing="1">1/0.98"</text>
<path d="M92 250 h60 a16 16 0 0 1 0 32 h-40 a16 16 0 0 0 0 32 h60" fill="none" stroke="{mag}" stroke-width="5" stroke-linecap="round" filter="url(#glow{gid})" opacity="0.7"/>
<path d="M92 250 h60 a16 16 0 0 1 0 32 h-40 a16 16 0 0 0 0 32 h60" fill="none" stroke="{mag}" stroke-width="2.4" stroke-linecap="round"/>
<path d="M206 268 l16 -18 v50 l16 -18" fill="none" stroke="{cyanc}" stroke-width="4" stroke-linecap="round" stroke-linejoin="round" filter="url(#glow{gid})" opacity="0.7"/>
<path d="M206 268 l16 -18 v50 l16 -18" fill="none" stroke="{cyanc}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
<text x="170" y="372" font-family="'Noto Sans JP',sans-serif" font-size="8.5" fill="{ink}" opacity="0.5" text-anchor="middle" letter-spacing="4">NEON SIGN EL</text>
{"".join(f'<circle cx="{104 + i * 26}" cy="400" r="3.5" fill="{c}" opacity="0.8"/>' for i, c in enumerate((mag, cyanc, "#ffd166", mag, cyanc, "#ffd166")))}
<text x="170" y="462" font-family="'Archivo','Noto Sans JP',sans-serif" font-size="26" font-weight="900" font-style="italic" fill="none" stroke="{mag}" stroke-width="1.2" text-anchor="middle" letter-spacing="6">YAKO</text>
<text x="170" y="486" font-family="'Noto Sans JP',sans-serif" font-size="8.5" fill="{ink}" opacity="0.5" text-anchor="middle" letter-spacing="3">SUZAKU × NTE ・ 夜行</text>
<text x="170" y="546" font-family="'Noto Sans JP',sans-serif" font-size="8" fill="{ink}" opacity="0.38" text-anchor="middle" letter-spacing="2">HETHEREAU NIGHT ・ {hz}</text>
<path d="M80 36 L206 36 L98 564 L49 564 L49 300 Z" fill="#ffffff" opacity="0.06"/>
<rect x="292.5" y="128" width="5" height="44" rx="2.5" fill="{mag}"/>
<rect x="292.5" y="184" width="5" height="66" rx="2.5" fill="{_shade(body_hex, -0.5)}"/>
</svg>"""


def _phone_zensen(pid, body_hex, glow, label, kana, hz):
    """前線(エンドフィールド): 装甲リブ・ハザード・2眼+ToF・計器窓・防塵ファン。"""
    gid = pid.replace("-", "")
    light_body = _is_light(body_hex)
    ink = "#1c1c26" if light_body else "#f2f1ec"
    yl = "#f2d800"
    dk = _shade(body_hex, -0.5)
    ribs = "".join(
        f'<path d="{d}" fill="{_shade(body_hex, -0.25)}" stroke="{_shade(body_hex, 0.2)}" stroke-width="1"/>'
        for d in ("M49 78 L49 46 Q49 36 62 36 L94 36 L94 50 L66 50 L63 78 Z",
                  "M291 78 L291 46 Q291 36 278 36 L246 36 L246 50 L274 50 L277 78 Z",
                  "M49 522 L49 554 Q49 564 62 564 L94 564 L94 550 L66 550 L63 522 Z",
                  "M291 522 L291 554 Q291 564 278 564 L246 564 L246 550 L274 550 L277 522 Z"))
    screws = "".join(
        f'<circle cx="{x}" cy="{y}" r="4" fill="{dk}" stroke="{_shade(body_hex, 0.3)}" stroke-width="1"/><path d="M{x - 2} {y} h4 M{x} {y - 2} v4" stroke="{_shade(body_hex, 0.35)}" stroke-width="0.9"/>'
        for x, y in ((72, 62, ), (268, 62), (72, 538), (268, 538)))
    slats = "".join(f'<rect x="128" y="{306 + i * 14}" width="84" height="6" rx="3" fill="{dk}"/>' for i in range(4))
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 340 600" role="img" aria-label="{label}">
<defs>
<linearGradient id="body{gid}" x1="0" y1="0" x2="0.85" y2="1">
  <stop offset="0" stop-color="{_shade(body_hex, 0.3)}"/>
  <stop offset="0.5" stop-color="{body_hex}"/>
  <stop offset="1" stop-color="{_shade(body_hex, -0.3)}"/>
</linearGradient>
<linearGradient id="frame{gid}" x1="0" y1="0" x2="0" y2="1">
  <stop offset="0" stop-color="{_shade(body_hex, 0.42)}"/>
  <stop offset="0.5" stop-color="{_shade(body_hex, -0.55)}"/>
  <stop offset="1" stop-color="{_shade(body_hex, 0.25)}"/>
</linearGradient>
<radialGradient id="lens{gid}" cx="0.38" cy="0.32" r="0.95">
  <stop offset="0" stop-color="#3c4454"/><stop offset="0.35" stop-color="#141821"/><stop offset="1" stop-color="#04040a"/>
</radialGradient>
<pattern id="hz{gid}" width="26" height="26" patternUnits="userSpaceOnUse" patternTransform="rotate(-45)">
  <rect width="13" height="26" fill="{yl}"/>
  <rect x="13" width="13" height="26" fill="#17171a"/>
</pattern>
<pattern id="tex{gid}" width="14" height="14" patternUnits="userSpaceOnUse">
  <path d="M0 7 H14" stroke="{'#000' if light_body else '#fff'}" stroke-opacity="0.05" stroke-width="2"/>
</pattern>
<filter id="soft{gid}" x="-40%" y="-40%" width="180%" height="180%"><feGaussianBlur stdDeviation="7"/></filter>
</defs>
<ellipse cx="170" cy="578" rx="120" ry="13" fill="#000000" opacity="0.45" filter="url(#soft{gid})"/>
<rect x="41" y="28" width="258" height="544" rx="26" fill="url(#frame{gid})"/>
<rect x="49" y="36" width="242" height="528" rx="20" fill="{body_hex}"/>
<rect x="49" y="36" width="242" height="528" rx="20" fill="url(#body{gid})"/>
<rect x="49" y="36" width="242" height="528" rx="20" fill="url(#tex{gid})"/>
{ribs}
{screws}
<rect x="66" y="58" width="130" height="130" rx="16" fill="{_shade(body_hex, -0.32)}" stroke="{_shade(body_hex, 0.25)}" stroke-width="1.4"/>
<circle cx="103" cy="96" r="25" fill="#0b0d13" stroke="{_shade(body_hex, 0.3)}" stroke-width="1.6"/>
<circle cx="103" cy="96" r="18" fill="none" stroke="{yl}" stroke-opacity="0.55" stroke-width="1.3"/>
<circle cx="103" cy="96" r="14" fill="url(#lens{gid})"/>
<circle cx="98" cy="90" r="3" fill="#ffffff" opacity="0.5"/>
<circle cx="159" cy="150" r="25" fill="#0b0d13" stroke="{_shade(body_hex, 0.3)}" stroke-width="1.6"/>
<circle cx="159" cy="150" r="18" fill="none" stroke="{yl}" stroke-opacity="0.55" stroke-width="1.3"/>
<circle cx="159" cy="150" r="14" fill="url(#lens{gid})"/>
<circle cx="154" cy="144" r="3" fill="#ffffff" opacity="0.5"/>
<rect x="146" y="82" width="26" height="26" rx="6" fill="#0b0d13" stroke="{_shade(body_hex, 0.3)}" stroke-width="1.4"/>
<circle cx="159" cy="95" r="6" fill="url(#lens{gid})"/>
<text x="159" y="76" font-family="ui-monospace,monospace" font-size="7" fill="{ink}" opacity="0.6" text-anchor="middle">ToF</text>
<circle cx="96" cy="156" r="5" fill="#f4efdf" opacity="0.9"/>
<rect x="206" y="78" width="56" height="26" rx="5" fill="url(#hz{gid})" opacity="0.95"/>
<rect x="206" y="78" width="56" height="26" rx="5" fill="none" stroke="{_shade(body_hex, 0.25)}" stroke-width="1.2"/>
<rect x="210" y="128" width="66" height="40" rx="8" fill="#101010" stroke="{_shade(body_hex, 0.3)}" stroke-width="1.4"/>
<rect x="216" y="146" width="54" height="8" rx="3" fill="#2a2a22"/>
<rect x="216" y="146" width="50" height="8" rx="3" fill="{yl}"/>
<text x="243" y="141" font-family="ui-monospace,monospace" font-size="8" fill="{yl}" text-anchor="middle" letter-spacing="1">PWR 99%</text>
<circle cx="170" cy="328" r="52" fill="{dk}"/>
<circle cx="170" cy="328" r="52" fill="none" stroke="{yl}" stroke-opacity="0.6" stroke-width="2.2"/>
<circle cx="170" cy="328" r="44" fill="#0a0b0a"/>
{"".join(f'<path d="M170 328 L170 294" stroke="{_shade(body_hex, 0.24)}" stroke-width="9" stroke-linecap="round" transform="rotate({a} 170 328)"/>' for a in range(0, 360, 40))}
{slats}
<circle cx="170" cy="328" r="12" fill="#101010" stroke="{yl}" stroke-opacity="0.85" stroke-width="1.6"/>
<circle cx="170" cy="328" r="3.6" fill="{yl}"/>
<text x="170" y="402" font-family="'Noto Sans JP',sans-serif" font-size="9" font-weight="700" fill="{ink}" opacity="0.55" text-anchor="middle" letter-spacing="3">SEALED FAN ・ IP68</text>
<rect x="66" y="428" width="208" height="1.6" fill="{yl}" opacity="0.7"/>
<text x="170" y="458" font-family="'Oswald','Noto Sans JP',sans-serif" font-size="21" font-weight="700" fill="{ink}" opacity="0.9" text-anchor="middle" letter-spacing="4">// ZENSEN</text>
<text x="170" y="480" font-family="'Noto Sans JP',sans-serif" font-size="8.5" fill="{ink}" opacity="0.55" text-anchor="middle" letter-spacing="2">SUZAKU × エンドフィールド 前線</text>
<text x="170" y="502" font-family="ui-monospace,monospace" font-size="7" fill="{ink}" opacity="0.42" text-anchor="middle" letter-spacing="1.5">MIL-STD-810H / -20〜45C / {hz}</text>
<text x="170" y="546" font-family="'Noto Sans JP',sans-serif" font-size="8" fill="{ink}" opacity="0.38" text-anchor="middle" letter-spacing="2">ENDFIELD INDUSTRIES ・ JOINT ENGINEERING</text>
<path d="M84 36 L196 36 L100 564 L49 564 L49 320 Z" fill="#ffffff" opacity="{0.1 if light_body else 0.05}"/>
<rect x="292.5" y="120" width="6" height="46" rx="2" fill="{yl}"/>
<rect x="292.5" y="178" width="6" height="46" rx="2" fill="{dk}"/>
<rect x="292.5" y="250" width="6" height="52" rx="2" fill="{dk}"/>
</svg>"""


_PHONE_CUSTOM = {
    "shichiyo": _phone_shichiyo,
    "zankyo": _phone_zankyo,
    "yako": _phone_yako,
    "zensen": _phone_zensen,
}


def _tablet_tex(gid, kind):
    """タブレット背面テクスチャ(スマホと同じ4種の語彙: carbon/hairline/matte/gloss)。"""
    if kind == "carbon":
        return f"""<pattern id="tex{gid}" width="8" height="8" patternUnits="userSpaceOnUse" patternTransform="rotate(45)">
  <path d="M0 0 V8 M4 0 V8" stroke="#ffffff" stroke-opacity="0.05" stroke-width="1.4"/>
  <path d="M0 0 H8" stroke="#000000" stroke-opacity="0.14" stroke-width="1.4"/>
</pattern>"""
    if kind == "matte":
        return f"""<pattern id="tex{gid}" width="9" height="9" patternUnits="userSpaceOnUse">
  <circle cx="2" cy="3" r="0.7" fill="#ffffff" fill-opacity="0.045"/>
  <circle cx="6.5" cy="7" r="0.6" fill="#000000" fill-opacity="0.1"/>
</pattern>"""
    if kind == "gloss":
        return f"""<pattern id="tex{gid}" width="10" height="10" patternUnits="userSpaceOnUse">
  <path d="M0 0" stroke="none"/>
</pattern>"""
    return f"""<pattern id="tex{gid}" width="7" height="7" patternUnits="userSpaceOnUse" patternTransform="rotate(35)">
  <path d="M0 0 V7" stroke="#ffffff" stroke-opacity="0.045" stroke-width="1"/>
</pattern>"""


def svg_tablet(pid, body_hex, glow, label, kana="", line="pad", hz="120Hz", design=None):
    """タブレット背面ビュー(横持ち)。スマホ背面と同じ質感エンジンで描く。

    designプロファイルでカメラ数(specsと一致)とファン有無を制御。
    ゲーミング系(pad/pad-neo)は冷却ファン窓+LEDスラッシュ、
    スタンダード系(t-pad)は朱雀エンブレム型押し+キーボード用ポゴピン。"""
    d = design or {}
    cams = d.get("cams", 2)
    gid = pid.replace("-", "")
    gaming = d.get("fan", line in ("pad", "pad-neo"))
    lite = _shade(body_hex, 0.42)
    lite2 = _shade(body_hex, 0.16)
    dark = _shade(body_hex, -0.38)
    dark2 = _shade(body_hex, -0.6)
    plate = _shade(body_hex, -0.3)
    light_body = _is_light(body_hex)
    ink = "#1c1c26" if light_body else "#ffffff"
    blade = _shade(body_hex, -0.35) if light_body else _shade(body_hex, 0.22)

    defs = f"""<defs>
<linearGradient id="body{gid}" x1="0" y1="0" x2="0.9" y2="1">
  <stop offset="0" stop-color="{lite}"/>
  <stop offset="0.28" stop-color="{lite2}"/>
  <stop offset="0.62" stop-color="{body_hex}"/>
  <stop offset="1" stop-color="{dark}"/>
</linearGradient>
<linearGradient id="frame{gid}" x1="0" y1="0" x2="0" y2="1">
  <stop offset="0" stop-color="{_shade(body_hex, 0.55)}"/>
  <stop offset="0.12" stop-color="{_shade(body_hex, -0.15)}"/>
  <stop offset="0.5" stop-color="{dark2}"/>
  <stop offset="0.88" stop-color="{_shade(body_hex, -0.2)}"/>
  <stop offset="1" stop-color="{_shade(body_hex, 0.35)}"/>
</linearGradient>
<radialGradient id="lens{gid}" cx="0.38" cy="0.32" r="0.95">
  <stop offset="0" stop-color="#3c4454"/>
  <stop offset="0.35" stop-color="#141821"/>
  <stop offset="1" stop-color="#04040a"/>
</radialGradient>
<linearGradient id="sheen{gid}" x1="0" y1="0" x2="1" y2="1">
  <stop offset="0" stop-color="#ffffff" stop-opacity="0.26"/>
  <stop offset="0.5" stop-color="#ffffff" stop-opacity="0.03"/>
  <stop offset="1" stop-color="#ffffff" stop-opacity="0"/>
</linearGradient>
{_tablet_tex(gid, d.get("tex", "hairline"))}
<filter id="soft{gid}" x="-40%" y="-40%" width="180%" height="180%">
  <feGaussianBlur stdDeviation="7"/>
</filter>
</defs>"""

    # カメラ島(左上・横持ち基準)。形状は design.plate、レンズ数はspecsと一致
    def lens_at(cx, cy, r=19):
        return f"""
<circle cx="{cx}" cy="{cy}" r="{r}" fill="#0b0d13" stroke="{_shade(body_hex, 0.3)}" stroke-width="1.5"/>
<circle cx="{cx}" cy="{cy}" r="{r - 5}" fill="none" stroke="{glow}" stroke-opacity="0.5" stroke-width="1.2"/>
<circle cx="{cx}" cy="{cy}" r="{r - 8}" fill="url(#lens{gid})"/>
<circle cx="{cx}" cy="{cy}" r="4" fill="#04040a"/>
<circle cx="{cx - 4}" cy="{cy - 4.5}" r="2.6" fill="#ffffff" opacity="0.55"/>"""

    plate_kind = d.get("plate", "corner")
    if plate_kind == "band":
        # 横長バンド: 2眼+角丸スクエア望遠セル+フラッシュ(旗艦の顔)
        camera = f"""
<rect x="66" y="58" width="238" height="68" rx="22" fill="{plate}"/>
<rect x="66" y="58" width="238" height="68" rx="22" fill="url(#sheen{gid})" opacity="0.5"/>
<rect x="66.7" y="58.7" width="236.6" height="66.6" rx="21.3" fill="none" stroke="#ffffff" stroke-opacity="0.12" stroke-width="1.3"/>
{lens_at(102, 92)}{lens_at(154, 92)}
<rect x="196" y="70" width="44" height="44" rx="10" fill="#0b0d13" stroke="{_shade(body_hex, 0.3)}" stroke-width="1.5"/>
<rect x="203" y="77" width="30" height="30" rx="6" fill="none" stroke="{glow}" stroke-opacity="0.5" stroke-width="1.2"/>
<circle cx="218" cy="92" r="10" fill="url(#lens{gid})"/>
<circle cx="218" cy="92" r="3.4" fill="#04040a"/>
<circle cx="262" cy="76" r="4.5" fill="#f4efdf" opacity="0.9"/>
<text x="262" y="112" font-family="'Noto Sans JP',sans-serif" font-size="7.5" font-weight="700" fill="{ink}" opacity="0.5" letter-spacing="2" text-anchor="middle">TENGAN</text>"""
    elif plate_kind == "square":
        camera = f"""
<rect x="70" y="60" width="86" height="86" rx="18" fill="{plate}"/>
<rect x="70" y="60" width="86" height="86" rx="18" fill="url(#sheen{gid})" opacity="0.5"/>
<rect x="70.7" y="60.7" width="84.6" height="84.6" rx="17.3" fill="none" stroke="#ffffff" stroke-opacity="0.12" stroke-width="1.3"/>
{lens_at(113, 96, 22)}
<circle cx="140" cy="76" r="4" fill="#f4efdf" opacity="0.9"/>"""
    elif plate_kind == "diag":
        camera = f"""
<path d="M78 60 h116 a18 18 0 0 1 18 18 v22 a18 18 0 0 1 -18 18 l-116 14 a18 18 0 0 1 -18 -18 v-36 a18 18 0 0 1 18 -18z" fill="{plate}"/>
<path d="M78 60 h116 a18 18 0 0 1 18 18 v22 a18 18 0 0 1 -18 18 l-116 14 a18 18 0 0 1 -18 -18 v-36 a18 18 0 0 1 18 -18z" fill="url(#sheen{gid})" opacity="0.5"/>
{lens_at(102, 92, 18)}{lens_at(158, 98, 18)}
<circle cx="192" cy="78" r="4" fill="#f4efdf" opacity="0.9"/>"""
    elif plate_kind == "none":
        # プレート無し: 素のリングレンズ(エントリーの潔さ)
        camera = f"""
{lens_at(96, 88, 21)}
<circle cx="132" cy="72" r="3.6" fill="#f4efdf" opacity="0.85"/>"""
    else:  # corner
        flash = '<circle cx="126" cy="76" r="4" fill="#f4efdf" opacity="0.9"/>' if d.get("flash") else ""
        camera = f"""
<rect x="72" y="62" width="66" height="60" rx="20" fill="{plate}"/>
<rect x="72" y="62" width="66" height="60" rx="20" fill="url(#sheen{gid})" opacity="0.5"/>
<rect x="72.7" y="62.7" width="64.6" height="58.6" rx="19.3" fill="none" stroke="#ffffff" stroke-opacity="0.12" stroke-width="1.3"/>
{lens_at(104, 92)}
{flash}"""

    # 背面のLED/ファン(ゲーミング)またはエンブレム(スタンダード)。
    # LED開始位置はカメラ島の右端から取り、プレート形状と干渉しない。
    _plate_right = {"band": 304, "square": 156, "diag": 212, "none": 130}.get(plate_kind, 138)
    led_x0 = _plate_right + 28
    led_kind = d.get("led", "slash3" if gaming else "none")
    if led_kind == "slash3":
        leds = "".join(
            f'<path d="M{led_x0 + i * 58} 78 h38 l-11 11 h-38 z" fill="{glow}" opacity="{o}"/>'
            for i, o in enumerate((0.92, 0.55, 0.28)))
    elif led_kind == "slash1":
        leds = f'<path d="M{led_x0} 78 h96 l-13 12 h-96 z" fill="{glow}" opacity="0.85"/>'
    elif led_kind == "dot":
        leds = "".join(
            f'<circle cx="{led_x0 + 10 + i * 26}" cy="84" r="4.6" fill="{glow}" opacity="{o}"/>'
            for i, o in enumerate((0.9, 0.6, 0.32)))
    else:
        leds = ""

    if gaming:
        fan_r = 52 if plate_kind == "band" else 44
        blades = "".join(
            f'<path d="M320 238 L320 {238 - fan_r + 12}" stroke="{blade}" stroke-width="8" stroke-linecap="round" transform="rotate({a} 320 238)"/>'
            for a in range(0, 360, 40))
        vents = "".join(
            f'<rect x="{596.5}" y="{150 + i * 30}" width="5" height="20" rx="2.5" fill="{dark2}"/>' for i in range(4))
        feature = f"""
{leds}
<circle cx="320" cy="238" r="{fan_r}" fill="{dark2}"/>
<circle cx="320" cy="238" r="{fan_r}" fill="none" stroke="{glow}" stroke-opacity="0.55" stroke-width="2"/>
<circle cx="320" cy="238" r="{fan_r - 7}" fill="#0a0b10"/>
{blades}
<circle cx="320" cy="238" r="11" fill="#101018" stroke="{glow}" stroke-opacity="0.8" stroke-width="1.5"/>
<circle cx="320" cy="238" r="3.5" fill="{glow}"/>
{vents}
<text x="320" y="{238 + fan_r + 18}" font-family="'Noto Sans JP',sans-serif" font-size="9" font-weight="700" fill="{ink}" opacity="0.5" text-anchor="middle" letter-spacing="3">SENPU COOLING</text>"""
        top_btn = f"""
<rect x="128" y="17.5" width="52" height="5" rx="2.5" fill="{glow}"/>
<rect x="196" y="17.5" width="40" height="5" rx="2.5" fill="{dark2}"/>"""
    else:
        emblem_kind = d.get("emblem", "small")
        if emblem_kind == "large":
            emblem = f"""
<g transform="translate(252 168) scale(2.6)" opacity="0.92">
  <path d="M24 6 C21.4 16.5 12 21 12 30 a12 12 0 0 0 24 0 C36 21 26.6 16.5 24 6 Z" fill="none" stroke="{glow}" stroke-width="2.4" stroke-linejoin="round"/>
  <circle cx="24" cy="31.5" r="3.2" fill="{glow}"/>
</g>
<text x="320" y="322" font-family="'Noto Sans JP',sans-serif" font-size="8.5" fill="{ink}" opacity="0.42" text-anchor="middle" letter-spacing="4">TSUBAME PAD</text>"""
        elif emblem_kind == "outline":
            emblem = f"""
<g transform="translate(288 208) scale(1.4)" opacity="0.55">
  <path d="M24 6 C21.4 16.5 12 21 12 30 a12 12 0 0 0 24 0 C36 21 26.6 16.5 24 6 Z" fill="none" stroke="{ink}" stroke-width="2" stroke-linejoin="round"/>
</g>"""
        else:
            emblem = f"""
<g transform="translate(276 194) scale(1.85)" opacity="0.9">
  <path d="M24 6 C21.4 16.5 12 21 12 30 a12 12 0 0 0 24 0 C36 21 26.6 16.5 24 6 Z" fill="none" stroke="{glow}" stroke-width="2.6" stroke-linejoin="round"/>
  <circle cx="24" cy="31.5" r="3.2" fill="{glow}"/>
</g>"""
        pogo = ("".join(
            f'<circle cx="{296 + i * 24}" cy="436" r="4" fill="{dark2}" stroke="#ffffff" stroke-opacity="0.25" stroke-width="1"/>'
            for i in range(3)) if d.get("pogo") else "")
        spk_n = {"large": 4, "outline": 2}.get(emblem_kind, 0)
        spks = "".join(
            f'<rect x="{560 - i * 18}" y="436.5" width="10" height="3.5" rx="1.75" fill="{dark2}"/>' for i in range(spk_n))
        feature = f"""
{leds}
{emblem}
{pogo}
{spks}"""
        top_btn = f'<rect x="128" y="17.5" width="52" height="5" rx="2.5" fill="{dark2}"/>'

    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 640 480" role="img" aria-label="{label}">
{defs}
<ellipse cx="320" cy="459" rx="216" ry="11" fill="#000000" opacity="0.4" filter="url(#soft{gid})"/>
<rect x="36" y="22" width="568" height="428" rx="35" fill="url(#frame{gid})"/>
<rect x="42" y="28" width="556" height="416" rx="30" fill="{body_hex}"/>
<rect x="42" y="28" width="556" height="416" rx="30" fill="url(#body{gid})"/>
<rect x="42" y="28" width="556" height="416" rx="30" fill="url(#tex{gid})"/>
<rect x="43" y="29" width="554" height="414" rx="29" fill="none" stroke="#ffffff" stroke-opacity="0.14" stroke-width="1.5"/>
<path d="M120 22 v6 M520 22 v6 M120 444 v6 M520 444 v6" stroke="{dark2}" stroke-width="3"/>
{camera}
{feature}
<text x="320" y="368" font-family="'Noto Sans JP',sans-serif" font-size="17" font-weight="800" fill="{ink}" opacity="0.72" text-anchor="middle" letter-spacing="3">{label}</text>
<text x="320" y="392" font-family="'Noto Sans JP',sans-serif" font-size="9.5" fill="{ink}" opacity="0.4" text-anchor="middle" letter-spacing="4">{kana}</text>
<text x="556" y="430" font-family="'Noto Sans JP',sans-serif" font-size="8" fill="{ink}" opacity="0.38" text-anchor="end" letter-spacing="2">DESIGNED BY SUZAKU ・ {hz}</text>
<path d="M92 28 L300 28 L136 444 L42 444 L42 240 Z" fill="url(#sheen{gid})"/>
<path d="M350 28 L400 28 L212 444 L168 444 Z" fill="#ffffff" opacity="0.05"/>
{top_btn}
</svg>"""


def _front_scene_phone(line, glow, hz, motif, scene=None):
    """スマホ正面ビューの画面内シーン。ライン/コラボ作品/世代(scene)で差し替える。
    scene: hud(現行HUD) / hud2(横バー型HUD) / classic(旧世代OS) /
           home(標準ホーム) / home-lite(エントリー簡易ホーム)。
    画面領域: x54〜286, y41〜559(中心 x=170)。"""
    fps = hz.replace("Hz", "")
    fjp = "'Noto Sans JP',sans-serif"
    if scene == "hud-ai":
        # Neo系HUD: リング計器+AIフレーム生成/予測冷却バッジ(トリガー無し構成)
        ring_c = 2 * math.pi * 66
        return f"""
<text x="170" y="118" font-family="{fjp}" font-size="10" fill="#9c9cb0" text-anchor="middle" letter-spacing="6">GAME SPACE</text>
<circle cx="170" cy="236" r="66" fill="none" stroke="#ffffff" stroke-opacity="0.08" stroke-width="9"/>
<circle cx="170" cy="236" r="66" fill="none" stroke="{glow}" stroke-width="9" stroke-linecap="round"
  stroke-dasharray="{ring_c * 0.78:.0f} {ring_c:.0f}" transform="rotate(-90 170 236)"/>
<text x="170" y="248" font-family="{fjp}" font-size="46" font-weight="900" fill="#ffffff" text-anchor="middle">{fps}</text>
<text x="170" y="274" font-family="{fjp}" font-size="10" fill="{glow}" text-anchor="middle" letter-spacing="5">FPS</text>
<rect x="70" y="336" width="200" height="42" rx="12" fill="{glow}" opacity="0.13"/>
<rect x="70" y="336" width="200" height="42" rx="12" fill="none" stroke="{glow}" stroke-opacity="0.55" stroke-width="1.4"/>
<text x="86" y="354" font-family="{fjp}" font-size="10" font-weight="800" fill="#ffffff">AIフレーム生成 ON</text>
<text x="86" y="370" font-family="{fjp}" font-size="8.5" fill="#c9c9d6">神楽 KAGURA ・ 60→{fps}fps 補間</text>
<rect x="70" y="392" width="200" height="42" rx="12" fill="#ffffff" opacity="0.06"/>
<text x="86" y="410" font-family="{fjp}" font-size="10" font-weight="700" fill="#ececf2">予測冷却 スタンバイ</text>
<text x="86" y="426" font-family="{fjp}" font-size="8.5" fill="#9c9cb0">負荷を先読みしてファンを助走</text>
<rect x="70" y="486" width="200" height="26" rx="13" fill="#ffffff" opacity="0.07"/>
<text x="170" y="503" font-family="{fjp}" font-size="9" font-weight="700" fill="#ececf2" text-anchor="middle" letter-spacing="1">ゲームライブラリ 42本</text>"""
    if scene == "work":
        # 法人機: 業務ホーム(予定・メール・MDM管理バッジ)
        return f"""
<text x="70" y="132" font-family="{fjp}" font-size="34" font-weight="300" fill="#ffffff" letter-spacing="1">12:34</text>
<text x="70" y="154" font-family="{fjp}" font-size="10" fill="#b9b9c8" letter-spacing="2">7月10日(金) ・ 社給端末</text>
<rect x="70" y="176" width="200" height="72" rx="14" fill="#ffffff" opacity="0.07"/>
<rect x="70" y="176" width="4" height="72" rx="2" fill="{glow}"/>
<text x="88" y="200" font-family="{fjp}" font-size="10.5" font-weight="800" fill="#ececf2">13:00 定例ミーティング</text>
<text x="88" y="218" font-family="{fjp}" font-size="9" fill="#9c9cb0">第2会議室 ・ あと26分</text>
<text x="88" y="236" font-family="{fjp}" font-size="9" fill="#9c9cb0">15:30 現場巡回(A棟)</text>
<rect x="70" y="262" width="200" height="56" rx="14" fill="#ffffff" opacity="0.05"/>
<path d="M86 282 h28 v20 h-28 z M86 282 l14 11 14 -11" fill="none" stroke="{glow}" stroke-width="1.8" stroke-linejoin="round"/>
<text x="126" y="288" font-family="{fjp}" font-size="10" font-weight="700" fill="#ececf2">未読メール 4件</text>
<text x="126" y="306" font-family="{fjp}" font-size="8.5" fill="#9c9cb0">うち承認待ち 2件</text>
<rect x="70" y="332" width="200" height="44" rx="12" fill="{glow}" opacity="0.13"/>
<rect x="70" y="332" width="200" height="44" rx="12" fill="none" stroke="{glow}" stroke-opacity="0.55" stroke-width="1.4"/>
<path d="M86 344 l9 4 v6 c0 6 -4 9 -9 11 c-5 -2 -9 -5 -9 -11 v-6 z" fill="none" stroke="{glow}" stroke-width="1.7"/>
<text x="104" y="350" font-family="{fjp}" font-size="9.5" font-weight="800" fill="#ffffff">MDM管理下 ・ ポリシー適用中</text>
<text x="104" y="366" font-family="{fjp}" font-size="8" fill="#c9c9d6">情報システム部 ・ 最終同期 3分前</text>
<rect x="70" y="486" width="96" height="26" rx="13" fill="#ffffff" opacity="0.07"/>
<text x="118" y="503" font-family="{fjp}" font-size="9" font-weight="700" fill="#ececf2" text-anchor="middle">業務アプリ</text>
<rect x="174" y="486" width="96" height="26" rx="13" fill="#ffffff" opacity="0.07"/>
<text x="222" y="503" font-family="{fjp}" font-size="9" font-weight="700" fill="#ececf2" text-anchor="middle">内線</text>"""
    if scene == "hud2":
        # 一世代前のGAME SPACE: 左上に大きなfps+横長グラフ+下部トグル
        bars = "".join(
            f'<rect x="{66 + i * 20}" y="{318 - h}" width="12" height="{h}" rx="3" fill="{glow}" opacity="{0.85 - i * 0.055:.2f}"/>'
            for i, h in enumerate((58, 74, 66, 82, 70, 88, 76, 62, 72, 58, 66)))
        return f"""
<text x="66" y="118" font-family="{fjp}" font-size="10" fill="#9c9cb0" letter-spacing="5">GAME SPACE</text>
<text x="66" y="188" font-family="{fjp}" font-size="58" font-weight="900" fill="#ffffff">{fps}</text>
<text x="66" y="212" font-family="{fjp}" font-size="10" fill="{glow}" letter-spacing="4">FPS ・ 安定率 99.1%</text>
<path d="M62 318 H278" stroke="#ffffff" stroke-opacity="0.14" stroke-width="1"/>
{bars}
<text x="66" y="352" font-family="{fjp}" font-size="9" fill="#9c9cb0" letter-spacing="2">フレームタイム(直近60秒)</text>
<rect x="66" y="392" width="204" height="44" rx="12" fill="#ffffff" opacity="0.07"/>
<text x="82" y="412" font-family="{fjp}" font-size="9.5" font-weight="700" fill="#ececf2">冷却ブースト ON</text>
<text x="82" y="428" font-family="{fjp}" font-size="8.5" fill="#9c9cb0">旋風ファン 22,000rpm</text>
<rect x="66" y="452" width="204" height="44" rx="12" fill="#ffffff" opacity="0.05"/>
<text x="82" y="472" font-family="{fjp}" font-size="9.5" font-weight="700" fill="#ececf2">通知ブロック ON</text>
<text x="82" y="488" font-family="{fjp}" font-size="8.5" fill="#9c9cb0">プレイ中の割り込みを遮断</text>"""
    if scene == "classic":
        # 旧世代 SUZAKU OS: 角丸スクエアのfpsタイルと簡素なリスト
        rows = "".join(
            f'<rect x="66" y="{330 + i * 52}" width="204" height="40" rx="10" fill="#ffffff" opacity="0.06"/>'
            f'<text x="82" y="{355 + i * 52}" font-family="{fjp}" font-size="10" font-weight="700" fill="#ececf2">{t}</text>'
            f'<text x="254" y="{355 + i * 52}" font-family="{fjp}" font-size="10" fill="{glow}" text-anchor="end">{v}</text>'
            for i, (t, v) in enumerate((("パフォーマンス", "高"), ("冷却ファン", "自動"), ("録画", "OFF"))))
        return f"""
<text x="170" y="128" font-family="{fjp}" font-size="10" fill="#9c9cb0" text-anchor="middle" letter-spacing="5">GAME SPACE</text>
<rect x="102" y="156" width="136" height="136" rx="26" fill="#ffffff" opacity="0.07"/>
<rect x="102" y="156" width="136" height="136" rx="26" fill="none" stroke="{glow}" stroke-opacity="0.6" stroke-width="2"/>
<text x="170" y="232" font-family="{fjp}" font-size="44" font-weight="900" fill="#ffffff" text-anchor="middle">{fps}</text>
<text x="170" y="258" font-family="{fjp}" font-size="9" fill="{glow}" text-anchor="middle" letter-spacing="4">FPS</text>
{rows}"""
    if scene == "home-lite":
        # エントリー: 時計+電池だけの簡素なホーム
        dock = "".join(
            f'<rect x="{104 + i * 46}" y="472" width="38" height="38" rx="11" fill="{c}" opacity="{o}"/>'
            for i, (c, o) in enumerate(((glow, 0.85), ("#ffffff", 0.13), ("#ffffff", 0.1))))
        return f"""
<text x="170" y="196" font-family="{fjp}" font-size="52" font-weight="300" fill="#ffffff" text-anchor="middle" letter-spacing="2">12:34</text>
<text x="170" y="222" font-family="{fjp}" font-size="11" fill="#b9b9c8" text-anchor="middle" letter-spacing="2">7月10日(金)</text>
<rect x="70" y="262" width="200" height="58" rx="15" fill="#ffffff" opacity="0.06"/>
<path d="M96 302 c-3.5 -12 4 -19 8 -26 c4 7 11.5 14 8 26 a8 8 0 0 1 -16 0z" fill="none" stroke="{glow}" stroke-width="2"/>
<text x="122" y="288" font-family="{fjp}" font-size="10" font-weight="700" fill="#ececf2">バッテリー 86%</text>
<text x="122" y="305" font-family="{fjp}" font-size="8.5" fill="#9c9cb0">省電力モード ON</text>
{dock}"""
    if motif == "genshin":
        # 七元素ホイール(七耀 SHICHIYO)
        cols = ("#74c2a8", "#d8b45c", "#a68cc8", "#9ac546", "#4cc2f1", "#ef7938", "#9fd6e3")
        dots = ""
        for i, col in enumerate(cols):
            a = math.radians(-90 + i * 360 / 7)
            x, y = 170 + 74 * math.cos(a), 250 + 74 * math.sin(a)
            dots += f'<circle cx="{x:.1f}" cy="{y:.1f}" r="11" fill="{col}" opacity="0.92"/><circle cx="{x:.1f}" cy="{y:.1f}" r="15.5" fill="none" stroke="{col}" stroke-opacity="0.4" stroke-width="1.5"/>'
        stars = "".join(f'<circle cx="{x}" cy="{y}" r="{r}" fill="#ffffff" opacity="{o}"/>'
                        for x, y, r, o in ((92, 110, 1.5, 0.6), (250, 96, 1, 0.45), (270, 170, 1.3, 0.5), (80, 330, 1, 0.4), (238, 396, 1.4, 0.5)))
        return f"""{stars}
<circle cx="170" cy="250" r="74" fill="none" stroke="#ffffff" stroke-opacity="0.14" stroke-width="1.2" stroke-dasharray="3 6"/>
{dots}
<path d="M170 218 c-6 24 -29 34 -29 59 a29 29 0 0 0 58 0 c0 -25 -23 -35 -29 -59z" fill="none" stroke="{glow}" stroke-width="3.4" stroke-linejoin="round"/>
<circle cx="170" cy="284" r="6" fill="{glow}"/>
<text x="170" y="392" font-family="{fjp}" font-size="15" font-weight="800" fill="#efe7d2" text-anchor="middle" letter-spacing="6">七元素共鳴</text>
<text x="170" y="414" font-family="{fjp}" font-size="8.5" fill="#b9b2a0" text-anchor="middle" letter-spacing="3">ELEMENTAL BACKGLOW</text>
<rect x="106" y="452" width="128" height="30" rx="15" fill="none" stroke="{glow}" stroke-opacity="0.7" stroke-width="1.4"/>
<text x="170" y="471.5" font-family="{fjp}" font-size="10" font-weight="700" fill="{glow}" text-anchor="middle" letter-spacing="2">七耀 SHICHIYO</text>"""
    if motif == "wuwa":
        # 共鳴波形HUD(残響 ZANKYO)
        wave = "M62 300 " + " ".join(
            f"Q {74 + i * 24} {300 - a} {86 + i * 24} 300"
            for i, a in enumerate((14, -38, 82, -120, 96, -60, 26, -12, 6)))
        bars = "".join(
            f'<rect x="{84 + i * 16}" y="{392 - h}" width="8" height="{h}" rx="2" fill="{glow}" opacity="{0.9 - i * 0.07:.2f}"/>'
            for i, h in enumerate((14, 26, 40, 30, 48, 22, 34, 16, 24, 10, 18)))
        return f"""
<path d="M66 84 h30 M66 84 v30 M274 84 h-30 M274 84 v30 M66 516 h30 M66 516 v-30 M274 516 h-30 M274 516 v-30" stroke="{glow}" stroke-opacity="0.75" stroke-width="2"/>
<text x="170" y="140" font-family="{fjp}" font-size="10" fill="#9adfe8" text-anchor="middle" letter-spacing="6" opacity="0.85">RESONANCE HUD</text>
<text x="170" y="216" font-family="{fjp}" font-size="52" font-weight="900" fill="#ffffff" text-anchor="middle" letter-spacing="1">4.1<tspan font-size="20" fill="{glow}">GHz</tspan></text>
<text x="170" y="242" font-family="{fjp}" font-size="9" fill="#9c9cb0" text-anchor="middle" letter-spacing="4">MAX CLOCK ・ ANTUTU 418万</text>
<path d="{wave}" fill="none" stroke="{glow}" stroke-width="2.6" stroke-linecap="round"/>
<path d="M62 300 H278" stroke="{glow}" stroke-opacity="0.25" stroke-width="1"/>
{bars}
<text x="170" y="428" font-family="{fjp}" font-size="9" fill="#9adfe8" text-anchor="middle" letter-spacing="3" opacity="0.8">RESONANCE HAPTICS 3200Hz</text>
<rect x="106" y="452" width="128" height="30" rx="15" fill="none" stroke="{glow}" stroke-opacity="0.7" stroke-width="1.4"/>
<text x="170" y="471.5" font-family="{fjp}" font-size="10" font-weight="700" fill="{glow}" text-anchor="middle" letter-spacing="2">残響 ZANKYO</text>"""
    if motif == "nte":
        # ネオン都市の夜景(夜行 YAKO)
        bl = "#191327"
        buildings = "".join(
            f'<rect x="{x}" y="{y}" width="{w}" height="{460 - y}" fill="{bl}" opacity="{o}"/>'
            for x, y, w, o in ((58, 300, 36, 0.9), (98, 252, 44, 1), (146, 286, 34, 0.85), (184, 224, 48, 1), (236, 268, 42, 0.9)))
        windows = "".join(
            f'<rect x="{x}" y="{y}" width="5" height="7" fill="{c}" opacity="{o}"/>'
            for x, y, c, o in ((106, 266, "#ff2d78", 0.9), (120, 266, "#39d7f5", 0.7), (106, 284, "#ffd166", 0.6),
                               (192, 240, "#39d7f5", 0.9), (206, 240, "#ff2d78", 0.8), (220, 240, "#ffd166", 0.55),
                               (192, 260, "#ff2d78", 0.6), (220, 260, "#39d7f5", 0.75), (66, 316, "#ffd166", 0.6),
                               (80, 316, "#ff2d78", 0.7), (244, 282, "#39d7f5", 0.8), (258, 282, "#ff2d78", 0.6),
                               (152, 300, "#ffd166", 0.7), (164, 300, "#39d7f5", 0.6)))
        return f"""
<circle cx="236" cy="118" r="26" fill="#f2ecdc" opacity="0.9"/>
<circle cx="228" cy="112" r="24" fill="#0d0a14"/>
{buildings}
{windows}
<path d="M58 460 H282" stroke="{glow}" stroke-opacity="0.5" stroke-width="1.5"/>
<rect x="84" y="150" width="172" height="52" rx="12" fill="none" stroke="{glow}" stroke-width="2" filter="url(#fzf)" opacity="0.8"/>
<rect x="84" y="150" width="172" height="52" rx="12" fill="none" stroke="{glow}" stroke-width="1.6"/>
<text x="170" y="184" font-family="{fjp}" font-size="21" font-weight="900" fill="{glow}" text-anchor="middle" letter-spacing="4">NEON CITY</text>
<text x="170" y="228" font-family="{fjp}" font-size="8.5" fill="#c9a7d6" text-anchor="middle" letter-spacing="3">NIGHT ISP ・ 2TB</text>
<rect x="106" y="486" width="128" height="30" rx="15" fill="none" stroke="{glow}" stroke-opacity="0.7" stroke-width="1.4"/>
<text x="170" y="505.5" font-family="{fjp}" font-size="10" font-weight="700" fill="{glow}" text-anchor="middle" letter-spacing="1">夜行 YAKO</text>"""
    if motif == "endfield":
        # 産業ターミナル(前線 ZENSEN)
        hazard = "".join(
            f'<path d="M{64 + i * 30} 96 l16 0 -10 14 -16 0 z" fill="{glow}" opacity="{0.9 if i % 2 == 0 else 0.35}"/>'
            for i in range(8))
        lines = (("SYSTEM CHECK", "OK", 0.95), ("POWER CELL 8500mAh", "OK", 0.8),
                 ("IP68 / MIL-STD-810H", "OK", 0.65), ("SUSTAIN MODE", "READY", 0.5))
        rows = "".join(
            f'<text x="66" y="{176 + i * 30}" font-family="monospace" font-size="11" fill="#ffb066" opacity="{o}">&gt; {t}</text>'
            f'<text x="274" y="{176 + i * 30}" font-family="monospace" font-size="11" fill="#7ee787" opacity="{o}" text-anchor="end">[{s}]</text>'
            for i, (t, s, o) in enumerate(lines))
        return f"""
{hazard}
<path d="M62 118 H278" stroke="{glow}" stroke-opacity="0.4" stroke-width="1"/>
{rows}
<rect x="66" y="306" width="208" height="10" rx="3" fill="#241c14"/>
<rect x="66" y="306" width="152" height="10" rx="3" fill="{glow}" opacity="0.85"/>
<text x="66" y="336" font-family="monospace" font-size="10" fill="#c9b8a4">UPTIME 73%</text>
<rect x="66" y="360" width="9" height="14" fill="{glow}"/>
<text x="170" y="418" font-family="{fjp}" font-size="13" font-weight="800" fill="#ead9c4" text-anchor="middle" letter-spacing="4">TERMINAL HUD</text>
<rect x="106" y="452" width="128" height="30" rx="15" fill="none" stroke="{glow}" stroke-opacity="0.7" stroke-width="1.4"/>
<text x="170" y="471.5" font-family="{fjp}" font-size="10" font-weight="700" fill="{glow}" text-anchor="middle" letter-spacing="2">前線 ZENSEN</text>"""
    if line in ("suzaku", "neo", "collab"):
        # ゲーミング: パフォーマンスHUD
        ring_c = 2 * math.pi * 66
        stats = (("GPU", 0.82), ("CPU", 0.64), ("温度", 0.38))
        bars = "".join(
            f'<text x="70" y="{392 + i * 34}" font-family="{fjp}" font-size="10" font-weight="700" fill="#9c9cb0">{l}</text>'
            f'<rect x="104" y="{384 + i * 34}" width="166" height="9" rx="3" fill="#ffffff" opacity="0.08"/>'
            f'<rect x="104" y="{384 + i * 34}" width="{166 * v:.0f}" height="9" rx="3" fill="{glow}" opacity="{0.95 - i * 0.18}"/>'
            for i, (l, v) in enumerate(stats))
        return f"""
<text x="170" y="118" font-family="{fjp}" font-size="10" fill="#9c9cb0" text-anchor="middle" letter-spacing="6">GAME SPACE</text>
<circle cx="170" cy="240" r="66" fill="none" stroke="#ffffff" stroke-opacity="0.08" stroke-width="9"/>
<circle cx="170" cy="240" r="66" fill="none" stroke="{glow}" stroke-width="9" stroke-linecap="round"
  stroke-dasharray="{ring_c * 0.8:.0f} {ring_c:.0f}" transform="rotate(-90 170 240)"/>
<text x="170" y="252" font-family="{fjp}" font-size="46" font-weight="900" fill="#ffffff" text-anchor="middle">{fps}</text>
<text x="170" y="278" font-family="{fjp}" font-size="10" fill="{glow}" text-anchor="middle" letter-spacing="5">FPS</text>
<text x="170" y="344" font-family="{fjp}" font-size="9" fill="#9c9cb0" text-anchor="middle" letter-spacing="3">フレーム安定率 99.4%</text>
{bars}
<rect x="70" y="486" width="96" height="26" rx="13" fill="#ffffff" opacity="0.07"/>
<text x="118" y="503" font-family="{fjp}" font-size="9" font-weight="700" fill="#ececf2" text-anchor="middle" letter-spacing="1">Lトリガー ON</text>
<rect x="174" y="486" width="96" height="26" rx="13" fill="#ffffff" opacity="0.07"/>
<text x="222" y="503" font-family="{fjp}" font-size="9" font-weight="700" fill="#ececf2" text-anchor="middle" letter-spacing="1">Rトリガー ON</text>"""
    # スタンダード/エントリー: ホーム画面
    dock = "".join(
        f'<rect x="{82 + i * 46}" y="472" width="38" height="38" rx="11" fill="{c}" opacity="{o}"/>'
        for i, (c, o) in enumerate(((glow, 0.85), ("#ffffff", 0.14), ("#ffffff", 0.11), ("#ffffff", 0.14))))
    return f"""
<text x="170" y="172" font-family="{fjp}" font-size="52" font-weight="300" fill="#ffffff" text-anchor="middle" letter-spacing="2">12:34</text>
<text x="170" y="198" font-family="{fjp}" font-size="11" fill="#b9b9c8" text-anchor="middle" letter-spacing="2">7月10日(金)</text>
<rect x="70" y="232" width="200" height="66" rx="16" fill="#ffffff" opacity="0.07"/>
<circle cx="106" cy="265" r="15" fill="none" stroke="#f2c14e" stroke-width="2.5"/>
{"".join(f'<path d="M106 243 v-6" stroke="#f2c14e" stroke-width="2.5" stroke-linecap="round" transform="rotate({a} 106 265)"/>' for a in range(0, 360, 45))}
<text x="136" y="261" font-family="{fjp}" font-size="15" font-weight="800" fill="#ffffff">24℃</text>
<text x="136" y="281" font-family="{fjp}" font-size="9.5" fill="#b9b9c8">東京 ・ 晴れ</text>
<rect x="70" y="312" width="200" height="52" rx="14" fill="#ffffff" opacity="0.05"/>
<path d="M92 352 c-3.5 -12 4 -19 8 -26 c4 7 11.5 14 8 26 a8 8 0 0 1 -16 0z" fill="none" stroke="{glow}" stroke-width="2"/>
<text x="118" y="336" font-family="{fjp}" font-size="9.5" font-weight="700" fill="#ececf2">バッテリー 82%</text>
<text x="118" y="352" font-family="{fjp}" font-size="8.5" fill="#9c9cb0">あと1日と4時間</text>
{dock}"""


def svg_phone_front(pid, body_hex, glow, label, line="suzaku", hz="144Hz", motif=None, design=None):
    """スマートフォン正面ビュー(ディスプレイ点灯状態)。

    ライン/コラボ作品ごとに画面内シーンを差し替えて差別化する。
    旗艦系はアンダーディスプレイカメラのためパンチホール無し。"""
    gid = "f" + pid.replace("-", "")
    d = design or {}
    dark2 = _shade(body_hex, -0.6)
    # パンチホール位置: none(UDC)/center/left。旧booleanも受ける
    punch = d.get("punch", "center" if line in ("tsubame", "lite") else "none")
    if punch is True:
        punch = "center"
    elif punch is False:
        punch = "none"
    thick = d.get("bezel") == "thick"  # 旧世代機の太ベゼル
    scr_x, scr_y, scr_w, scr_h = (58, 47, 224, 506) if thick else (54, 41, 232, 518)
    # フレーム角丸は背面の筐体形状に合わせる(残響=角形モノリス等)
    rx_out = d.get("front_rx", 47)
    rx_in = max(6, rx_out - 5)
    rx_scr = max(4, rx_out - 10)
    defs = f"""<defs>
<linearGradient id="frame{gid}" x1="0" y1="0" x2="0" y2="1">
  <stop offset="0" stop-color="{_shade(body_hex, 0.55)}"/>
  <stop offset="0.12" stop-color="{_shade(body_hex, -0.15)}"/>
  <stop offset="0.5" stop-color="{dark2}"/>
  <stop offset="0.88" stop-color="{_shade(body_hex, -0.2)}"/>
  <stop offset="1" stop-color="{_shade(body_hex, 0.35)}"/>
</linearGradient>
<linearGradient id="scr{gid}" x1="0" y1="0" x2="0.8" y2="1">
  <stop offset="0" stop-color="#171722"/>
  <stop offset="0.5" stop-color="#0d0d14"/>
  <stop offset="1" stop-color="#07070c"/>
</linearGradient>
<radialGradient id="flare{gid}" cx="0.5" cy="0.32" r="0.85">
  <stop offset="0" stop-color="{glow}" stop-opacity="0.3"/>
  <stop offset="0.55" stop-color="{glow}" stop-opacity="0.09"/>
  <stop offset="1" stop-color="{glow}" stop-opacity="0"/>
</radialGradient>
<filter id="soft{gid}" x="-40%" y="-40%" width="180%" height="180%">
  <feGaussianBlur stdDeviation="7"/>
</filter>
<filter id="fzf" x="-60%" y="-60%" width="220%" height="220%"><feGaussianBlur stdDeviation="5"/></filter>
<clipPath id="clip{gid}"><rect x="{scr_x}" y="{scr_y}" width="{scr_w}" height="{scr_h}" rx="{rx_scr}"/></clipPath>
</defs>"""
    scene = _front_scene_phone(line, glow, hz, motif, d.get("scene"))
    status = f"""
<text x="70" y="72" font-family="'Noto Sans JP',sans-serif" font-size="11" font-weight="700" fill="#e6e6ee">12:34</text>
{"".join(f'<rect x="{222 + i * 6}" y="{70 - i * 2.5}" width="3.5" height="{5 + i * 2.5}" rx="1" fill="#c9c9d6" opacity="{0.55 + i * 0.15}"/>' for i in range(3))}
<rect x="248" y="61.5" width="20" height="10" rx="3" fill="none" stroke="#c9c9d6" stroke-width="1.3"/>
<rect x="250" y="63.5" width="13" height="6" rx="1.5" fill="{glow}"/>
<rect x="268.6" y="64" width="2.4" height="5" rx="1" fill="#c9c9d6"/>"""
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 340 600" role="img" aria-label="{label} 正面">
{defs}
<ellipse cx="170" cy="577" rx="116" ry="13" fill="#000000" opacity="0.4" filter="url(#soft{gid})"/>
<rect x="43" y="30" width="254" height="540" rx="{rx_out}" fill="url(#frame{gid})"/>
<rect x="48" y="35" width="244" height="530" rx="{rx_in}" fill="#06060a"/>
<rect x="{scr_x}" y="{scr_y}" width="{scr_w}" height="{scr_h}" rx="{rx_scr}" fill="url(#scr{gid})"/>
<g clip-path="url(#clip{gid})">
<ellipse cx="170" cy="210" rx="180" ry="200" fill="url(#flare{gid})"/>
{scene}
{status}
{f'<circle cx="{84 if punch == "left" else 170}" cy="64" r="5.5" fill="#04040a" stroke="#2a2a36" stroke-width="1.4"/>' if punch != 'none' else ''}
<rect x="125" y="544" width="90" height="4.5" rx="2.25" fill="#ffffff" opacity="0.55"/>
<path d="M54 41 L206 41 L84 559 L54 559 Z" fill="#ffffff" opacity="0.035"/>
</g>
<rect x="{scr_x + 0.8}" y="{scr_y + 0.8}" width="{scr_w - 1.6}" height="{scr_h - 1.6}" rx="{rx_scr}" fill="none" stroke="#ffffff" stroke-opacity="0.08" stroke-width="1.4"/>
<rect x="292.5" y="140" width="5" height="46" rx="2.5" fill="{dark2}"/>
<rect x="292.5" y="200" width="5" height="70" rx="2.5" fill="{dark2}"/>
</svg>"""


def svg_tablet_front(pid, body_hex, glow, label, line="pad", hz="120Hz", design=None):
    """タブレット正面ビュー(横持ち・ディスプレイ点灯状態)。
    design.scene で機種ごとに画面内容を描き分ける:
    hud=リング計器 / hud2=左寄せ大fps+フレームタイム / classic=タイル+設定行 /
    home=ホーム / reader=動画+読書 / home-lite=時計と電池のみ。"""
    d = design or {}
    gid = "f" + pid.replace("-", "")
    gaming = d.get("fan", line in ("pad", "pad-neo"))
    scene_kind = d.get("scene", "hud" if gaming else "home")
    rx_scr = d.get("front_rx", 22)
    dark2 = _shade(body_hex, -0.6)
    fps = hz.replace("Hz", "")
    fjp = "'Noto Sans JP',sans-serif"
    if scene_kind == "hud":
        ring_c = 2 * math.pi * 62
        bars = "".join(
            f'<text x="368" y="{170 + i * 44}" font-family="{fjp}" font-size="11" font-weight="700" fill="#9c9cb0">{l}</text>'
            f'<rect x="410" y="{161 + i * 44}" width="150" height="10" rx="3" fill="#ffffff" opacity="0.08"/>'
            f'<rect x="410" y="{161 + i * 44}" width="{150 * v:.0f}" height="10" rx="3" fill="{glow}" opacity="{0.95 - i * 0.18}"/>'
            for i, (l, v) in enumerate((("GPU", 0.84), ("CPU", 0.62), ("温度", 0.36))))
        scene = f"""
<text x="210" y="122" font-family="{fjp}" font-size="10" fill="#9c9cb0" text-anchor="middle" letter-spacing="6">GAME SPACE</text>
<circle cx="210" cy="240" r="62" fill="none" stroke="#ffffff" stroke-opacity="0.08" stroke-width="9"/>
<circle cx="210" cy="240" r="62" fill="none" stroke="{glow}" stroke-width="9" stroke-linecap="round"
  stroke-dasharray="{ring_c * 0.8:.0f} {ring_c:.0f}" transform="rotate(-90 210 240)"/>
<text x="210" y="252" font-family="{fjp}" font-size="42" font-weight="900" fill="#ffffff" text-anchor="middle">{fps}</text>
<text x="210" y="278" font-family="{fjp}" font-size="10" fill="{glow}" text-anchor="middle" letter-spacing="5">FPS</text>
<text x="210" y="342" font-family="{fjp}" font-size="9" fill="#9c9cb0" text-anchor="middle" letter-spacing="3">フレーム安定率 99.2%</text>
{bars}
<rect x="368" y="300" width="192" height="46" rx="12" fill="#ffffff" opacity="0.05"/>
<text x="380" y="320" font-family="{fjp}" font-size="9.5" font-weight="700" fill="#ececf2">旋風ファン 21,000rpm</text>
<text x="380" y="336" font-family="{fjp}" font-size="8.5" fill="#9c9cb0">表面温度 38.2℃ ・ 静音モード</text>"""
    elif scene_kind == "hud2":
        cols = "".join(
            f'<rect x="{368 + i * 22}" y="{330 - h}" width="14" height="{h}" rx="3" fill="{glow}" opacity="{0.4 + (h - 44) * 0.012:.2f}"/>'
            for i, h in enumerate((48, 52, 46, 50, 47, 53, 49, 46, 51)))
        scene = f"""
<text x="96" y="132" font-family="{fjp}" font-size="10" fill="#9c9cb0" letter-spacing="6">GAME SPACE</text>
<text x="90" y="238" font-family="{fjp}" font-size="86" font-weight="900" fill="#ffffff">{fps}</text>
<text x="96" y="268" font-family="{fjp}" font-size="11" fill="{glow}" letter-spacing="4">FPS ・ 安定率 99.1%</text>
<rect x="90" y="292" width="200" height="52" rx="12" fill="#ffffff" opacity="0.05"/>
<text x="104" y="314" font-family="{fjp}" font-size="9.5" font-weight="700" fill="#ececf2">冷却ブースト ON</text>
<text x="104" y="330" font-family="{fjp}" font-size="8.5" fill="#9c9cb0">旋風ファン 20,000rpm</text>
<text x="368" y="132" font-family="{fjp}" font-size="10" fill="#9c9cb0" letter-spacing="3">フレームタイム(直近60秒)</text>
<rect x="360" y="148" width="212" height="196" rx="14" fill="#ffffff" opacity="0.04"/>
{cols}
<text x="368" y="366" font-family="{fjp}" font-size="8.5" fill="#9c9cb0">分散 0.4ms ・ ドロップ 0</text>"""
    elif scene_kind == "classic":
        rows = "".join(
            f'<rect x="356" y="{150 + i * 62}" width="204" height="48" rx="12" fill="#ffffff" opacity="0.06"/>'
            f'<text x="372" y="{179 + i * 62}" font-family="{fjp}" font-size="10.5" font-weight="700" fill="#ececf2">{l}</text>'
            f'<text x="544" y="{179 + i * 62}" font-family="{fjp}" font-size="10" font-weight="700" fill="{glow}" text-anchor="end">{v}</text>'
            for i, (l, v) in enumerate((("パフォーマンス", "高"), ("冷却ファン", "自動"), ("録画", "OFF"))))
        scene = f"""
<text x="200" y="140" font-family="{fjp}" font-size="10" fill="#9c9cb0" text-anchor="middle" letter-spacing="6">GAME SPACE</text>
<rect x="130" y="162" width="140" height="140" rx="30" fill="{glow}" opacity="0.14"/>
<rect x="130" y="162" width="140" height="140" rx="30" fill="none" stroke="{glow}" stroke-opacity="0.6" stroke-width="2"/>
<text x="200" y="242" font-family="{fjp}" font-size="44" font-weight="900" fill="#ffffff" text-anchor="middle">{fps}</text>
<text x="200" y="268" font-family="{fjp}" font-size="10" fill="{glow}" text-anchor="middle" letter-spacing="4">FPS</text>
<text x="200" y="336" font-family="{fjp}" font-size="9" fill="#9c9cb0" text-anchor="middle" letter-spacing="2">フレーム安定率 98.9%</text>
{rows}"""
    elif scene_kind == "reader":
        scene = f"""
<rect x="86" y="120" width="250" height="150" rx="16" fill="#ffffff" opacity="0.07"/>
<rect x="86" y="120" width="250" height="150" rx="16" fill="{glow}" opacity="0.08"/>
<path d="M196 178 l32 17 -32 17z" fill="#ffffff" opacity="0.9"/>
<rect x="102" y="242" width="150" height="5" rx="2.5" fill="#ffffff" opacity="0.16"/>
<rect x="102" y="242" width="96" height="5" rx="2.5" fill="{glow}" opacity="0.9"/>
<text x="86" y="298" font-family="{fjp}" font-size="11" font-weight="700" fill="#ececf2">ドキュメンタリー「朱雀の設計室」</text>
<text x="86" y="318" font-family="{fjp}" font-size="9" fill="#9c9cb0">42:10 / 65:00 ・ 燐光ディスプレイで再生中</text>
<rect x="368" y="120" width="192" height="120" rx="16" fill="#ffffff" opacity="0.06"/>
<path d="M388 148 h44 v64 l-22 -12 -22 12 z" fill="none" stroke="{glow}" stroke-width="2.2"/>
<text x="448" y="168" font-family="{fjp}" font-size="10.5" font-weight="700" fill="#ececf2">続きから読む</text>
<text x="448" y="186" font-family="{fjp}" font-size="8.5" fill="#9c9cb0">「熱設計の教科書」</text>
<text x="448" y="202" font-family="{fjp}" font-size="8.5" fill="#9c9cb0">第4章 ・ 62%</text>
<rect x="368" y="258" width="192" height="70" rx="16" fill="#ffffff" opacity="0.05"/>
<text x="384" y="286" font-family="{fjp}" font-size="10" font-weight="700" fill="#ececf2">メモ 3件</text>
<text x="384" y="304" font-family="{fjp}" font-size="8.5" fill="#9c9cb0">キーボード接続中 ・ ポゴピン</text>"""
    elif scene_kind == "home-lite":
        scene = f"""
<text x="320" y="216" font-family="{fjp}" font-size="64" font-weight="300" fill="#ffffff" text-anchor="middle" letter-spacing="2">12:34</text>
<text x="320" y="246" font-family="{fjp}" font-size="12" fill="#b9b9c8" text-anchor="middle" letter-spacing="2">7月10日(金)</text>
<rect x="222" y="278" width="196" height="52" rx="14" fill="#ffffff" opacity="0.05"/>
<path d="M252 316 c-4 -11 4 -18 8 -25 c4 7 12 14 8 25 a8 8 0 0 1 -16 0z" fill="none" stroke="{glow}" stroke-width="2"/>
<text x="280" y="300" font-family="{fjp}" font-size="10" font-weight="700" fill="#ececf2">バッテリー 91%</text>
<text x="280" y="316" font-family="{fjp}" font-size="8.5" fill="#9c9cb0">低電力モード ON</text>
{"".join(f'<rect x="{262 + i * 60}" y="352" width="40" height="40" rx="11" fill="{c}" opacity="{o}"/>' for i, (c, o) in enumerate(((glow, 0.8), ("#ffffff", 0.12))))}"""
    else:
        scene = f"""
<text x="200" y="200" font-family="{fjp}" font-size="58" font-weight="300" fill="#ffffff" text-anchor="middle" letter-spacing="2">12:34</text>
<text x="200" y="228" font-family="{fjp}" font-size="12" fill="#b9b9c8" text-anchor="middle" letter-spacing="2">7月10日(金)</text>
<rect x="356" y="140" width="204" height="92" rx="16" fill="#ffffff" opacity="0.07"/>
<circle cx="396" cy="186" r="17" fill="none" stroke="#f2c14e" stroke-width="2.5"/>
{"".join(f'<path d="M396 162 v-7" stroke="#f2c14e" stroke-width="2.5" stroke-linecap="round" transform="rotate({a} 396 186)"/>' for a in range(0, 360, 45))}
<text x="428" y="182" font-family="{fjp}" font-size="17" font-weight="800" fill="#ffffff">24℃</text>
<text x="428" y="204" font-family="{fjp}" font-size="10" fill="#b9b9c8">東京 ・ 晴れ</text>
<rect x="356" y="248" width="204" height="66" rx="16" fill="#ffffff" opacity="0.05"/>
<path d="M382 302 c-4 -13 4.5 -21 9 -29 c4.5 8 13 16 9 29 a9 9 0 0 1 -18 0z" fill="none" stroke="{glow}" stroke-width="2.2"/>
<text x="410" y="280" font-family="{fjp}" font-size="10.5" font-weight="700" fill="#ececf2">バッテリー 88%</text>
<text x="410" y="298" font-family="{fjp}" font-size="9" fill="#9c9cb0">あと2日と1時間</text>
{"".join(f'<rect x="{110 + i * 60}" y="264" width="44" height="44" rx="12" fill="{c}" opacity="{o}"/>' for i, (c, o) in enumerate(((glow, 0.85), ("#ffffff", 0.14), ("#ffffff", 0.11))))}"""
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 640 480" role="img" aria-label="{label} 正面">
<defs>
<linearGradient id="frame{gid}" x1="0" y1="0" x2="0" y2="1">
  <stop offset="0" stop-color="{_shade(body_hex, 0.55)}"/>
  <stop offset="0.12" stop-color="{_shade(body_hex, -0.15)}"/>
  <stop offset="0.5" stop-color="{dark2}"/>
  <stop offset="0.88" stop-color="{_shade(body_hex, -0.2)}"/>
  <stop offset="1" stop-color="{_shade(body_hex, 0.35)}"/>
</linearGradient>
<linearGradient id="scr{gid}" x1="0" y1="0" x2="0.8" y2="1">
  <stop offset="0" stop-color="#171722"/>
  <stop offset="0.5" stop-color="#0d0d14"/>
  <stop offset="1" stop-color="#07070c"/>
</linearGradient>
<radialGradient id="flare{gid}" cx="0.5" cy="0.35" r="0.85">
  <stop offset="0" stop-color="{glow}" stop-opacity="0.28"/>
  <stop offset="0.55" stop-color="{glow}" stop-opacity="0.08"/>
  <stop offset="1" stop-color="{glow}" stop-opacity="0"/>
</radialGradient>
<filter id="soft{gid}" x="-40%" y="-40%" width="180%" height="180%">
  <feGaussianBlur stdDeviation="7"/>
</filter>
<clipPath id="clip{gid}"><rect x="58" y="44" width="524" height="388" rx="{rx_scr}"/></clipPath>
</defs>
<ellipse cx="320" cy="459" rx="216" ry="11" fill="#000000" opacity="0.4" filter="url(#soft{gid})"/>
<rect x="36" y="22" width="568" height="428" rx="35" fill="url(#frame{gid})"/>
<rect x="42" y="28" width="556" height="416" rx="30" fill="#06060a"/>
<rect x="58" y="44" width="524" height="388" rx="{rx_scr}" fill="url(#scr{gid})"/>
<g clip-path="url(#clip{gid})">
<ellipse cx="320" cy="200" rx="300" ry="180" fill="url(#flare{gid})"/>
{scene}
<text x="78" y="74" font-family="{fjp}" font-size="11" font-weight="700" fill="#e6e6ee">12:34</text>
<rect x="536" y="63.5" width="20" height="10" rx="3" fill="none" stroke="#c9c9d6" stroke-width="1.3"/>
<rect x="538" y="65.5" width="13" height="6" rx="1.5" fill="{glow}"/>
<rect x="556.6" y="66" width="2.4" height="5" rx="1" fill="#c9c9d6"/>
<rect x="275" y="418" width="90" height="4.5" rx="2.25" fill="#ffffff" opacity="0.5"/>
<path d="M58 44 L300 44 L120 432 L58 432 Z" fill="#ffffff" opacity="0.035"/>
</g>
<rect x="58.8" y="44.8" width="522.4" height="386.4" rx="{rx_scr - 0.6}" fill="none" stroke="#ffffff" stroke-opacity="0.08" stroke-width="1.4"/>
<circle cx="320" cy="36" r="4" fill="#04040a" stroke="#2a2a36" stroke-width="1.2"/>
</svg>"""


def svg_die(gid, label, sub, glow, accent2=None):
    """実チップパッケージ風ビジュアル(基板+金属リッド+シルク印字+周辺部品)。

    技術ページのヒーローとコラボ専用シリコンページで使用。CPUパッケージの
    外観(サブストレート・IHSリッド・コーナーインデックス・受動部品)を再現する。"""
    gid = gid.replace("-", "")
    a2 = accent2 or glow
    import random
    rnd = random.Random(gid)
    # サブストレート上の受動部品(コンデンサ列)
    caps = ""
    for i in range(9):
        x = 96 + i * 32
        caps += (f'<rect x="{x}" y="66" width="14" height="7" rx="1.5" fill="#b58a3c"/>'
                 f'<rect x="{x}" y="66" width="4" height="7" fill="#7a5a22"/>')
        caps += (f'<rect x="{x}" y="407" width="14" height="7" rx="1.5" fill="#b58a3c"/>'
                 f'<rect x="{x + 10}" y="407" width="4" height="7" fill="#7a5a22"/>')
    caps2 = ""
    for i in range(6):
        y = 128 + i * 40
        caps2 += f'<rect x="66" y="{y}" width="7" height="14" rx="1.5" fill="#8a8a96"/>'
        caps2 += f'<rect x="407" y="{y}" width="7" height="14" rx="1.5" fill="#8a8a96"/>'
    # 基板端の金メッキパッド
    pads = "".join(
        f'<rect x="{74 + i * 24}" y="446" width="14" height="8" rx="1" fill="#c8a24a"/>'
        for i in range(14))
    lot = f"SZK{rnd.randint(2400, 2699)}-{rnd.randint(100, 999)}"
    # 刻印はリッド幅(244px)に収まるよう文字数でサイズを落とす
    fs = 27 if len(label) <= 9 else (20 if len(label) <= 13 else 16)
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 480 480" role="img" aria-label="{label}">
<defs>
<linearGradient id="sub{gid}" x1="0" y1="0" x2="1" y2="1">
  <stop offset="0" stop-color="#1b2426"/><stop offset="1" stop-color="#101718"/>
</linearGradient>
<linearGradient id="ihs{gid}" x1="0" y1="0" x2="0.7" y2="1">
  <stop offset="0" stop-color="#c8ccd4"/>
  <stop offset="0.24" stop-color="#9aa0aa"/>
  <stop offset="0.55" stop-color="#7d838e"/>
  <stop offset="0.78" stop-color="#9aa0aa"/>
  <stop offset="1" stop-color="#6c727c"/>
</linearGradient>
<pattern id="brush{gid}" width="5" height="5" patternUnits="userSpaceOnUse">
  <path d="M0 2.5 H5" stroke="#ffffff" stroke-opacity="0.06" stroke-width="1"/>
</pattern>
<filter id="dsh{gid}" x="-30%" y="-30%" width="160%" height="160%"><feGaussianBlur stdDeviation="6"/></filter>
</defs>
<rect width="480" height="480" fill="#0b0b10"/>
<ellipse cx="240" cy="250" rx="220" ry="200" fill="{glow}" opacity="0.08"/>
<rect x="238" y="462" width="4" height="0" fill="none"/>
<ellipse cx="240" cy="452" rx="180" ry="12" fill="#000" opacity="0.5" filter="url(#dsh{gid})"/>
<rect x="56" y="56" width="368" height="368" rx="10" fill="url(#sub{gid})" stroke="#2c3a3c" stroke-width="2"/>
<rect x="60" y="60" width="360" height="360" rx="8" fill="none" stroke="#31494b" stroke-opacity="0.6" stroke-width="1"/>
{caps}{caps2}{pads}
<rect x="118" y="118" width="244" height="244" rx="14" fill="url(#ihs{gid})" stroke="#4c525c" stroke-width="2"/>
<rect x="118" y="118" width="244" height="244" rx="14" fill="url(#brush{gid})"/>
<path d="M118 190 L362 190 M118 290 L362 290" stroke="#ffffff" stroke-opacity="0.08" stroke-width="30" />
<circle cx="140" cy="140" r="6" fill="none" stroke="#3a4048" stroke-width="2"/>
<circle cx="140" cy="140" r="2.2" fill="#3a4048"/>
<path d="M226 152 c-4.5 17 -21 24 -21 42 a21 21 0 0 0 42 0 c0 -18 -16.5 -25 -21 -42z" fill="none" stroke="{glow}" stroke-width="3" stroke-linejoin="round" transform="translate(14 0)"/>
<text x="240" y="252" font-family="'Noto Sans JP',sans-serif" font-size="{fs}" font-weight="900" fill="#22262c" text-anchor="middle" letter-spacing="2.5">{label}</text>
<text x="240" y="251" font-family="'Noto Sans JP',sans-serif" font-size="{fs}" font-weight="900" fill="#f0f2f5" fill-opacity="0.9" text-anchor="middle" letter-spacing="2.5">{label}</text>
<text x="240" y="278" font-family="ui-monospace,monospace" font-size="11" fill="#30343c" text-anchor="middle" letter-spacing="2">{sub}</text>
<text x="240" y="298" font-family="ui-monospace,monospace" font-size="10" fill="#3c414a" text-anchor="middle" letter-spacing="3">{lot} ・ 3nm</text>
<rect x="318" y="318" width="26" height="26" fill="#22262c"/>
{"".join(f'<rect x="{321 + (i % 4) * 5}" y="{321 + (i // 4) * 5}" width="4" height="4" fill="{"#f0f2f5" if (i * 7) % 3 else "#22262c"}"/>' for i in range(16))}
<path d="M124 124 L200 124 L142 356 L124 356 Z" fill="#ffffff" opacity="0.1"/>
<circle cx="240" cy="240" r="0.1" fill="none"/>
<path d="M56 92 h-14 M56 388 h-14 M424 92 h14 M424 388 h14" stroke="{a2}" stroke-opacity="0.6" stroke-width="2"/>
<text x="240" y="443" font-family="ui-monospace,monospace" font-size="9" fill="#5d6a6c" text-anchor="middle" letter-spacing="4">SUZAKU SILICON ・ JAPAN</text>
</svg>"""


_UID_SEQ = 0  # ページ内 id 衝突防止の呼び出し連番(ビルド順固定=決定的)


def svg_art(kind, glow="#e8442e", body_hex="#181820", motif=None):
    """feature-split・アクセサリ用のアートパネル(480×360)。

    kind ごとに専用の造形を描く。アクセサリ系(cooler/grip/buds/charger/case/
    dock/powerbank)は body_hex を筐体色として質感グラデーションで塗り、
    powerbank は motif(コラボslug)で意匠を差別化する。"""
    g = glow
    b = body_hex
    # 同一ページに複数インライン展開しても勾配定義が衝突しないよう、
    # パラメータ由来の決定的なID接尾辞を付ける
    # 同一ページに同じ (kind, glow) で複数回展開しても id が衝突しないよう、
    # パラメータに加えて呼び出し連番も付ける(ビルド順は固定なので出力は決定的)。
    global _UID_SEQ
    _UID_SEQ += 1
    u = (kind + glow + body_hex + (motif or "")).replace("#", "") + f"n{_UID_SEQ}"
    bl = _shade(b, 0.4)
    bl2 = _shade(b, 0.14)
    bd = _shade(b, -0.4)
    bd2 = _shade(b, -0.62)
    ink = "#1c1c26" if _is_light(b) else "#e9e9f2"
    grid = "".join(f'<path d="M{x} 0 V360" stroke="#ffffff" stroke-opacity="0.03"/>' for x in range(40, 480, 40)) + \
           "".join(f'<path d="M0 {y} H480" stroke="#ffffff" stroke-opacity="0.03"/>' for y in range(40, 360, 40))
    common = f"""<defs>
<radialGradient id="ag{u}" cx="0.5" cy="0.4" r="0.8">
  <stop offset="0" stop-color="{g}" stop-opacity="0.7"/>
  <stop offset="0.55" stop-color="{g}" stop-opacity="0.16"/>
  <stop offset="1" stop-color="{g}" stop-opacity="0"/>
</radialGradient>
<linearGradient id="al{u}" x1="0" y1="0" x2="1" y2="0">
  <stop offset="0" stop-color="{g}" stop-opacity="0"/>
  <stop offset="0.5" stop-color="{g}"/>
  <stop offset="1" stop-color="{g}" stop-opacity="0"/>
</linearGradient>
<linearGradient id="mb{u}" x1="0" y1="0" x2="0.85" y2="1">
  <stop offset="0" stop-color="{bl}"/>
  <stop offset="0.3" stop-color="{bl2}"/>
  <stop offset="0.65" stop-color="{b}"/>
  <stop offset="1" stop-color="{bd}"/>
</linearGradient>
<linearGradient id="mt{u}" x1="0" y1="0" x2="0" y2="1">
  <stop offset="0" stop-color="#ffffff" stop-opacity="0.3"/>
  <stop offset="0.4" stop-color="#ffffff" stop-opacity="0.05"/>
  <stop offset="1" stop-color="#000000" stop-opacity="0.3"/>
</linearGradient>
<radialGradient id="gl{u}" cx="0.38" cy="0.32" r="0.95">
  <stop offset="0" stop-color="#39414f"/>
  <stop offset="0.4" stop-color="#12151d"/>
  <stop offset="1" stop-color="#04040a"/>
</radialGradient>
<filter id="fz{u}" x="-60%" y="-60%" width="220%" height="220%"><feGaussianBlur stdDeviation="6"/></filter>
</defs>
<rect width="480" height="360" fill="#0b0b10"/>
{grid}
<ellipse cx="240" cy="176" rx="225" ry="145" fill="url(#ag{u})"/>"""

    def shadow(cx, cy, rx):
        return f'<ellipse cx="{cx}" cy="{cy}" rx="{rx}" ry="10" fill="#000" opacity="0.45" filter="url(#fz{u})"/>'

    body = ""
    if kind in ("chip", "npu"):
        traces = "".join(
            f'<path d="M240 180 L{x} {y}" stroke="{g}" stroke-opacity="0.45" stroke-width="1.6"/><circle cx="{x}" cy="{y}" r="4" fill="{g}" opacity="0.85"/><circle cx="{x}" cy="{y}" r="7.5" fill="none" stroke="{g}" stroke-opacity="0.3"/>'
            for x, y in [(78, 66), (56, 180), (88, 292), (402, 66), (424, 180), (392, 292), (168, 36), (312, 36), (168, 324), (312, 324)])
        pins = "".join(f'<circle cx="{190 + c * 20}" cy="{262}" r="3" fill="#8a8a9c" opacity="0.8"/>' for c in range(6))
        body = f"""{traces}
{shadow(240, 268, 90)}
<rect x="168" y="104" width="144" height="144" rx="16" fill="#151520" stroke="{_shade('#151520', 0.35)}" stroke-width="1.6"/>
<rect x="168" y="104" width="144" height="144" rx="16" fill="url(#mt{u})"/>
<rect x="188" y="124" width="104" height="104" rx="10" fill="#07070c" stroke="{g}" stroke-width="1.8"/>
<rect x="188" y="124" width="104" height="104" rx="10" fill="url(#ag{u})" opacity="0.5"/>
<path d="M240 142 c-7 27 -33 38 -33 66 a33 33 0 0 0 66 0 c0 -28 -26 -39 -33 -66z" fill="none" stroke="{g}" stroke-width="3.6" stroke-linejoin="round"/>
<circle cx="240" cy="216" r="7" fill="{g}"/>
{pins}
<text x="240" y="290" font-family="sans-serif" font-size="10" fill="{g}" text-anchor="middle" letter-spacing="4" opacity="0.85">SUZAKU SILICON</text>"""
        if kind == "npu":
            mesh = "".join(f'<circle cx="{x}" cy="{y}" r="6.5" fill="none" stroke="{g}" stroke-width="2" opacity="0.9"/>'
                           for x, y in [(120, 108), (120, 252), (360, 108), (360, 252)])
            links = "".join(f'<path d="M{x1} {y1} L{x2} {y2}" stroke="{g}" stroke-opacity="0.35" stroke-width="1.4"/>'
                            for x1, y1, x2, y2 in [(120, 108, 120, 252), (360, 108, 360, 252), (120, 108, 360, 108), (120, 252, 360, 252)])
            body += links + mesh
    elif kind == "gpu":
        rows = "".join(
            f'<rect x="{158 + c * 30}" y="{118 + r * 30}" width="24" height="24" rx="4" fill="{g}" opacity="{0.2 + ((r * 5 + c * 3) % 10) * 0.07:.2f}"/>'
            for r in range(4) for c in range(6))
        body = f"""{shadow(240, 272, 110)}
<rect x="140" y="98" width="200" height="168" rx="16" fill="#151520" stroke="{_shade('#151520', 0.3)}" stroke-width="1.6"/>
<rect x="140" y="98" width="200" height="168" rx="16" fill="url(#mt{u})"/>
<rect x="150" y="108" width="180" height="148" rx="10" fill="#0a0a12"/>
{rows}
<rect x="352" y="120" width="46" height="30" rx="6" fill="#0f0f18" stroke="{g}" stroke-opacity="0.7" stroke-width="1.5"/>
<text x="375" y="139" font-family="sans-serif" font-size="10" font-weight="700" fill="{g}" text-anchor="middle">RT</text>
<rect x="352" y="160" width="46" height="30" rx="6" fill="#0f0f18" stroke="{g}" stroke-opacity="0.45" stroke-width="1.5"/>
<text x="375" y="179" font-family="sans-serif" font-size="10" font-weight="700" fill="{g}" opacity="0.7" text-anchor="middle">AI</text>
<path d="M60 306 L420 306" stroke="url(#al{u})" stroke-width="2.5"/>
<text x="240" y="330" font-family="sans-serif" font-size="10" fill="#9c9cb0" text-anchor="middle" letter-spacing="4">HOMURA GRAPHICS</text>"""
    elif kind == "memory":
        sticks = ""
        for i in range(4):
            x = 104 + i * 74
            op = 1 - i * 0.14
            sticks += f"""
<g opacity="{op:.2f}">{shadow(x + 24, 268, 34)}
<rect x="{x}" y="96" width="48" height="164" rx="7" fill="#151520" stroke="{_shade('#151520', 0.3)}" stroke-width="1.5"/>
<rect x="{x}" y="96" width="48" height="164" rx="7" fill="url(#mt{u})"/>
<rect x="{x + 9}" y="112" width="30" height="52" rx="4" fill="{g}" opacity="0.75"/>
<rect x="{x + 9}" y="172" width="30" height="52" rx="4" fill="{g}" opacity="0.35"/>
{"".join(f'<rect x="{x + 7 + j * 9}" y="248" width="5" height="10" fill="#c8a24a"/>' for j in range(4))}</g>"""
        body = f"""{sticks}
<path d="M70 60 h340" stroke="url(#al{u})" stroke-width="2" opacity="0.8"/>
<text x="240" y="326" font-family="sans-serif" font-size="10" fill="#9c9cb0" text-anchor="middle" letter-spacing="4">HAYATE LPDDR6</text>"""
    elif kind == "storage":
        arrows = "".join(
            f'<path d="M{58} {138 + i * 26} h56" stroke="{g}" stroke-opacity="{0.85 - i * 0.2}" stroke-width="4" stroke-linecap="round"/><path d="M{106} {132 + i * 26} l10 6 -10 6" fill="none" stroke="{g}" stroke-opacity="{0.85 - i * 0.2}" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/>'
            for i in range(4))
        body = f"""{shadow(248, 262, 120)}
<rect x="128" y="112" width="240" height="136" rx="14" fill="#151520" stroke="{_shade('#151520', 0.3)}" stroke-width="1.6"/>
<rect x="128" y="112" width="240" height="136" rx="14" fill="url(#mt{u})"/>
<rect x="146" y="132" width="86" height="96" rx="9" fill="#0a0a12" stroke="{g}" stroke-width="1.8"/>
<path d="M189 150 c-5 20 -25 28 -25 49 a25 25 0 0 0 50 0 c0 -21 -20 -29 -25 -49z" fill="none" stroke="{g}" stroke-width="2.8"/>
<rect x="248" y="132" width="50" height="96" rx="7" fill="{g}" opacity="0.35"/>
<rect x="306" y="132" width="50" height="96" rx="7" fill="{g}" opacity="0.22"/>
{arrows}
<text x="240" y="292" font-family="sans-serif" font-size="11" font-weight="700" fill="{g}" text-anchor="middle" letter-spacing="3" opacity="0.9">5,800 MB/s</text>
<text x="240" y="326" font-family="sans-serif" font-size="10" fill="#9c9cb0" text-anchor="middle" letter-spacing="4">SHUN UFS 4.1</text>"""
    elif kind == "cooling":
        layers = ""
        for i in range(7):
            w = 250 - i * 14
            x = 240 - w / 2
            y = 84 + i * 27
            layers += f"""{shadow(240, y + 20, w / 2)}
<rect x="{x}" y="{y}" width="{w}" height="16" rx="8" fill="{g}" opacity="{0.9 - i * 0.11:.2f}"/>
<rect x="{x}" y="{y}" width="{w}" height="16" rx="8" fill="url(#mt{u})"/>"""
        body = f"""{layers}
<path d="M140 312 q30 -20 60 0 t60 0 t60 0 t60 0" fill="none" stroke="{g}" stroke-width="3" opacity="0.75"/>
<text x="240" y="345" font-family="sans-serif" font-size="10" fill="#9c9cb0" text-anchor="middle" letter-spacing="4">11-LAYER COOLING</text>"""
    elif kind == "fan":
        blades = "".join(
            f'<path d="M240 180 q34 -36 80 -22" fill="none" stroke="{g}" stroke-width="10" stroke-linecap="round" opacity="0.9" transform="rotate({i * 40} 240 180)"/>'
            for i in range(9))
        vents = "".join(f'<path d="M240 180 m0 -122 a122 122 0 0 1 0 244" fill="none" stroke="{g}" stroke-opacity="0.25" stroke-width="2" transform="rotate({a} 240 180)"/>' for a in (0, 90))
        body = f"""{shadow(240, 312, 120)}
<circle cx="240" cy="180" r="122" fill="#10101a" stroke="{_shade('#10101a', 0.35)}" stroke-width="2"/>
<circle cx="240" cy="180" r="122" fill="url(#mt{u})"/>
<circle cx="240" cy="180" r="106" fill="#07070c"/>
{vents}{blades}
<circle cx="240" cy="180" r="27" fill="#0d0d16" stroke="{g}" stroke-width="2.6"/>
<circle cx="240" cy="180" r="8" fill="{g}"/>
<text x="240" y="336" font-family="sans-serif" font-size="10" fill="#9c9cb0" text-anchor="middle" letter-spacing="4">24,000 RPM</text>"""
    elif kind == "liquid":
        body = f"""{shadow(240, 276, 130)}
<rect x="104" y="88" width="272" height="180" rx="20" fill="#151520" stroke="{_shade('#151520', 0.3)}" stroke-width="1.8"/>
<rect x="104" y="88" width="272" height="180" rx="20" fill="url(#mt{u})"/>
<path d="M132 178 q54 -66 108 0 t108 0" fill="none" stroke="{g}" stroke-width="7" stroke-linecap="round"/>
<path d="M132 178 q54 66 108 0 t108 0" fill="none" stroke="{g}" stroke-width="7" stroke-linecap="round" opacity="0.4"/>
<circle cx="240" cy="178" r="24" fill="#07070c" stroke="{g}" stroke-width="3.2"/>
<circle cx="240" cy="178" r="9" fill="{g}"/>
<circle cx="168" cy="128" r="4" fill="{g}" opacity="0.7"/><circle cx="318" cy="228" r="4" fill="{g}" opacity="0.7"/>
<text x="240" y="304" font-family="sans-serif" font-size="10" fill="#9c9cb0" text-anchor="middle" letter-spacing="4">ACTIVE LIQUID LOOP</text>"""
    elif kind == "display":
        rays = "".join(f'<path d="M240 60 l0 -18" stroke="{g}" stroke-opacity="0.6" stroke-width="3" stroke-linecap="round" transform="rotate({a} 240 168)"/>' for a in range(-60, 61, 30))
        body = f"""{shadow(240, 276, 140)}
<rect x="104" y="72" width="272" height="192" rx="16" fill="#0c0c14" stroke="{_shade('#0c0c14', 0.4)}" stroke-width="2"/>
<rect x="112" y="80" width="256" height="176" rx="10" fill="#07070b"/>
<rect x="112" y="80" width="256" height="176" rx="10" fill="url(#ag{u})"/>
<path d="M112 80 L368 80 L220 256 L112 256 Z" fill="#ffffff" opacity="0.05"/>
{rays}
<path d="M240 118 c-8 30 -38 43 -38 74 a38 38 0 0 0 76 0 c0 -31 -30 -44 -38 -74z" fill="none" stroke="{g}" stroke-width="3.8" stroke-linejoin="round"/>
<rect x="196" y="276" width="88" height="26" rx="13" fill="#0f0f18" stroke="{g}" stroke-opacity="0.7" stroke-width="1.5"/>
<text x="240" y="294" font-family="sans-serif" font-size="13" font-weight="700" fill="{g}" text-anchor="middle" letter-spacing="2">175Hz</text>"""
    elif kind == "camera":
        aperture = "".join(f'<path d="M240 176 L240 118 A58 58 0 0 1 290 147 Z" fill="#0b0e15" stroke="#2a2f3c" stroke-width="1" transform="rotate({a} 240 176)"/>' for a in range(0, 360, 60))
        body = f"""{shadow(240, 296, 120)}
<circle cx="240" cy="176" r="112" fill="#151520" stroke="{_shade('#151520', 0.35)}" stroke-width="2.5"/>
<circle cx="240" cy="176" r="112" fill="url(#mt{u})"/>
<circle cx="240" cy="176" r="88" fill="#0a0d14" stroke="{g}" stroke-opacity="0.8" stroke-width="2"/>
<circle cx="240" cy="176" r="72" fill="url(#gl{u})"/>
{aperture}
<circle cx="240" cy="176" r="30" fill="url(#gl{u})"/>
<circle cx="240" cy="176" r="12" fill="#04040a"/>
<circle cx="216" cy="150" r="12" fill="#ffffff" opacity="0.4"/>
<circle cx="262" cy="204" r="6" fill="{g}" opacity="0.5"/>
<path d="M120 70 L180 110" stroke="#ffffff" stroke-opacity="0.25" stroke-width="3" stroke-linecap="round"/>
<text x="240" y="330" font-family="sans-serif" font-size="10" fill="#9c9cb0" text-anchor="middle" letter-spacing="4">TENGAN OPTICS</text>"""
    elif kind == "battery":
        cells = "".join(f'<rect x="{160 + i * 34}" y="150" width="24" height="60" rx="5" fill="{g}" opacity="{0.85 - i * 0.16:.2f}"/>' for i in range(4))
        body = f"""{shadow(240, 268, 110)}
<rect x="136" y="104" width="192" height="152" rx="20" fill="#151520" stroke="{_shade('#151520', 0.32)}" stroke-width="2"/>
<rect x="136" y="104" width="192" height="152" rx="20" fill="url(#mt{u})"/>
<rect x="328" y="150" width="20" height="60" rx="8" fill="{_shade('#151520', 0.25)}"/>
<rect x="148" y="116" width="168" height="128" rx="12" fill="#0a0a12"/>
{cells}
<path d="M252 120 l-46 70 h32 l-16 62 l56 -80 h-32 l24 -52z" fill="{g}" stroke="#0b0b10" stroke-width="5" stroke-linejoin="round" opacity="0.98"/>
<text x="240" y="298" font-family="sans-serif" font-size="11" font-weight="700" fill="{g}" text-anchor="middle" letter-spacing="2" opacity="0.9">120W HYPERCHARGE</text>"""
    elif kind == "os":
        tiles = "".join(
            f'<rect x="{140 + (i % 3) * 70}" y="{116 + (i // 3) * 70}" width="58" height="58" rx="13" fill="{g}" opacity="{0.22 + (i % 4) * 0.15:.2f}"/><rect x="{140 + (i % 3) * 70}" y="{116 + (i // 3) * 70}" width="58" height="58" rx="13" fill="url(#mt{u})" opacity="0.5"/>'
            for i in range(6))
        body = f"""{shadow(240, 292, 130)}
<rect x="118" y="76" width="244" height="212" rx="18" fill="#0c0c14" stroke="{_shade('#0c0c14', 0.4)}" stroke-width="2"/>
<rect x="126" y="84" width="228" height="196" rx="12" fill="#07070b"/>
<rect x="126" y="84" width="228" height="196" rx="12" fill="url(#ag{u})" opacity="0.45"/>
<text x="140" y="106" font-family="sans-serif" font-size="10" font-weight="700" fill="#e6e6ee">12:34</text>
<circle cx="340" cy="102" r="3.5" fill="{g}"/>
{tiles}
<rect x="196" y="296" width="88" height="5" rx="2.5" fill="#4a4a5c"/>
<path d="M240 128 c-5 18 -22 25 -22 43 a22 22 0 0 0 44 0 c0 -18 -17 -25 -22 -43z" fill="none" stroke="{g}" stroke-width="2.6" transform="translate(0 60)" opacity="0.9"/>"""
    elif kind == "panel":
        # ディスプレイの積層構造(カバーガラス〜発光層〜基板の分解図)
        layers = [
            ("カバーガラス", "#8fa8c8", 0.9), ("偏光板", _shade(g, 0.25), 0.55),
            ("タッチセンサー", g, 0.75), ("発光層(AMOLED)", g, 1.0),
            ("TFT基板", "#5a5a6e", 0.8), ("放熱シート", "#3a3a48", 0.9),
        ]
        stack = ""
        for i, (label, col, op) in enumerate(layers):
            y = 74 + i * 34
            stack += f"""
{shadow(226, y + 30, 108)}
<path d="M116 {y + 14} L226 {y} L336 {y + 14} L226 {y + 28} Z" fill="{col}" opacity="{op * 0.85:.2f}"/>
<path d="M116 {y + 14} L226 {y} L336 {y + 14}" fill="none" stroke="#ffffff" stroke-opacity="0.25" stroke-width="1.2"/>
<text x="352" y="{y + 16}" font-family="sans-serif" font-size="10" fill="#b9b9c8">{label}</text>"""
        body = f"""{stack}
<path d="M226 44 v250" stroke="{g}" stroke-opacity="0.25" stroke-width="1" stroke-dasharray="3 5"/>
<text x="240" y="330" font-family="sans-serif" font-size="10" fill="#9c9cb0" text-anchor="middle" letter-spacing="4">RINKO PANEL STACK</text>"""
    elif kind == "touch":
        # タッチ応答(指先タップ→同心円リップル→応答時間)
        ripples = "".join(
            f'<circle cx="200" cy="168" r="{r}" fill="none" stroke="{g}" stroke-width="{w}" stroke-opacity="{o}"/>'
            for r, w, o in ((18, 3, 0.95), (36, 2.4, 0.6), (58, 2, 0.35), (84, 1.6, 0.18)))
        body = f"""{shadow(240, 296, 130)}
<rect x="96" y="60" width="288" height="230" rx="18" fill="#0c0c14" stroke="{_shade('#0c0c14', 0.4)}" stroke-width="2"/>
<rect x="104" y="68" width="272" height="214" rx="12" fill="#07070b"/>
<rect x="104" y="68" width="272" height="214" rx="12" fill="url(#ag{u})" opacity="0.35"/>
{ripples}
<circle cx="200" cy="168" r="9" fill="{g}"/>
<path d="M208 160 c22 -30 44 -38 58 -34 c10 3 8 16 -2 22 l-34 22" fill="#e8c9a8" opacity="0.95" transform="rotate(18 208 160)"/>
<rect x="286" y="120" width="74" height="30" rx="8" fill="#0f0f18" stroke="{g}" stroke-opacity="0.7" stroke-width="1.4"/>
<text x="323" y="140" font-family="sans-serif" font-size="13" font-weight="800" fill="{g}" text-anchor="middle">0.4ms</text>
<path d="M120 254 h240" stroke="#2a2a36" stroke-width="2"/>
{"".join(f'<rect x="{124 + i * 30}" y="{246 - h}" width="14" height="{h}" rx="3" fill="{g}" opacity="{0.3 + h / 60:.2f}"/>' for i, h in enumerate((10, 18, 30, 42, 34, 24, 16, 12)))}
<text x="240" y="330" font-family="sans-serif" font-size="10" fill="#9c9cb0" text-anchor="middle" letter-spacing="4">TOUCH SAMPLING 2500Hz</text>"""
    elif kind == "gamespace":
        # ゲームスペース「陣」のオーバーレイUI(横持ち画面+HUDパネル)
        body = f"""{shadow(240, 300, 150)}
<rect x="72" y="76" width="336" height="212" rx="16" fill="#0c0c14" stroke="{_shade('#0c0c14', 0.4)}" stroke-width="2"/>
<rect x="80" y="84" width="320" height="196" rx="10" fill="#07070b"/>
<rect x="80" y="84" width="320" height="196" rx="10" fill="url(#ag{u})" opacity="0.4"/>
<rect x="92" y="96" width="120" height="172" rx="10" fill="#10101a" stroke="{g}" stroke-opacity="0.55" stroke-width="1.4"/>
<text x="152" y="116" font-family="sans-serif" font-size="11" font-weight="800" fill="#ececf2" text-anchor="middle" letter-spacing="2">陣 GAME SPACE</text>
{"".join(f'<rect x="102" y="{128 + i * 26}" width="100" height="18" rx="5" fill="{g}" opacity="{0.55 - i * 0.09:.2f}"/>' for i in range(5))}
<circle cx="300" cy="150" r="34" fill="none" stroke="#ffffff" stroke-opacity="0.1" stroke-width="7"/>
<circle cx="300" cy="150" r="34" fill="none" stroke="{g}" stroke-width="7" stroke-linecap="round" stroke-dasharray="150 214" transform="rotate(-90 300 150)"/>
<text x="300" y="156" font-family="sans-serif" font-size="17" font-weight="900" fill="#ffffff" text-anchor="middle">144</text>
<text x="300" y="196" font-family="sans-serif" font-size="8.5" fill="{g}" text-anchor="middle" letter-spacing="3">FPS</text>
<rect x="238" y="214" width="124" height="46" rx="9" fill="#10101a" stroke="{g}" stroke-opacity="0.4" stroke-width="1.2"/>
<text x="248" y="233" font-family="sans-serif" font-size="9" fill="#9c9cb0">GPU 82% ・ 38.2℃</text>
<text x="248" y="249" font-family="sans-serif" font-size="9" fill="#9c9cb0">旋風ファン 21,000rpm</text>
<rect x="238" y="96" width="124" height="40" rx="9" fill="#10101a" stroke="#ffffff" stroke-opacity="0.1" stroke-width="1.2"/>
<text x="248" y="120" font-family="sans-serif" font-size="9" fill="#ececf2">通知ブロック ON</text>
<text x="240" y="330" font-family="sans-serif" font-size="10" fill="#9c9cb0" text-anchor="middle" letter-spacing="4">GAME SPACE OVERLAY</text>"""
    elif kind == "cooler":
        blades = "".join(
            f'<path d="M240 168 q30 -32 68 -19" fill="none" stroke="{g}" stroke-width="9" stroke-linecap="round" opacity="0.92" transform="rotate({i * 51.4:.0f} 240 168)"/>'
            for i in range(7))
        body = f"""{shadow(240, 310, 120)}
<rect x="196" y="60" width="88" height="216" rx="14" fill="{_shade(b, -0.35)}" opacity="0.55"/>
<path d="M158 96 h-26 a12 12 0 0 0 -12 12 v14 h14 v-12 a4 4 0 0 1 4 -4 h20 z" fill="url(#mb{u})" stroke="{_shade(b, 0.25)}" stroke-width="1.2"/>
<path d="M322 96 h26 a12 12 0 0 1 12 12 v14 h-14 v-12 a4 4 0 0 0 -4 -4 h-20 z" fill="url(#mb{u})" stroke="{_shade(b, 0.25)}" stroke-width="1.2"/>
<path d="M158 240 h-26 a12 12 0 0 1 -12 -12 v-14 h14 v12 a4 4 0 0 0 4 4 h20 z" fill="url(#mb{u})" stroke="{_shade(b, 0.25)}" stroke-width="1.2"/>
<path d="M322 240 h26 a12 12 0 0 0 12 -12 v-14 h-14 v12 a4 4 0 0 1 -4 4 h-20 z" fill="url(#mb{u})" stroke="{_shade(b, 0.25)}" stroke-width="1.2"/>
<rect x="148" y="76" width="184" height="184" rx="30" fill="url(#mb{u})"/>
<rect x="148" y="76" width="184" height="184" rx="30" fill="url(#mt{u})"/>
<rect x="149.4" y="77.4" width="181.2" height="181.2" rx="28.6" fill="none" stroke="#ffffff" stroke-opacity="0.15" stroke-width="1.6"/>
<circle cx="240" cy="168" r="76" fill="#07070c" stroke="{g}" stroke-width="2.6"/>
{blades}
<circle cx="240" cy="168" r="20" fill="#0d0d16" stroke="{g}" stroke-width="2.4"/>
<circle cx="240" cy="168" r="6" fill="{g}"/>
<rect x="228" y="260" width="24" height="14" rx="4" fill="{_shade(b, -0.45)}" stroke="{_shade(b, 0.25)}" stroke-width="1.2"/>
<path d="M240 274 v22 q0 10 12 10 h20" fill="none" stroke="{_shade(b, -0.4)}" stroke-width="5" stroke-linecap="round"/>
<text x="240" y="326" font-family="sans-serif" font-size="10" fill="#e9e9f2" opacity="0.6" text-anchor="middle" letter-spacing="3">PELTIER -28℃ ・ CLAMP MOUNT</text>"""
    elif kind == "grip":
        abxy = "".join(
            f'<circle cx="{352 + dx}" cy="{172 + dy}" r="8.5" fill="{c}"/>'
            for (dx, dy), c in zip([(0, -20), (20, 0), (0, 20), (-20, 0)], ("#e8b23a", "#e8442e", "#3d8bff", "#38b67a")))
        body = f"""{shadow(240, 262, 150)}
<rect x="168" y="140" width="144" height="66" rx="12" fill="{bd2}"/>
<rect x="176" y="146" width="128" height="54" rx="8" fill="#07070b"/>
<rect x="176" y="146" width="128" height="54" rx="8" fill="url(#ag{u})" opacity="0.6"/>
<path d="M96 128 h72 a14 14 0 0 1 14 14 v64 a14 14 0 0 1 -14 14 h-72 a40 40 0 0 1 -40 -40 v-12 a40 40 0 0 1 40 -40z" fill="url(#mb{u})"/>
<path d="M96 128 h72 a14 14 0 0 1 14 14 v64 a14 14 0 0 1 -14 14 h-72 a40 40 0 0 1 -40 -40 v-12 a40 40 0 0 1 40 -40z" fill="url(#mt{u})"/>
<path d="M384 128 h-72 a14 14 0 0 0 -14 14 v64 a14 14 0 0 0 14 14 h72 a40 40 0 0 0 40 -40 v-12 a40 40 0 0 0 -40 -40z" fill="url(#mb{u})"/>
<path d="M384 128 h-72 a14 14 0 0 0 -14 14 v64 a14 14 0 0 0 14 14 h72 a40 40 0 0 0 40 -40 v-12 a40 40 0 0 0 -40 -40z" fill="url(#mt{u})"/>
<circle cx="128" cy="172" r="30" fill="#101018" stroke="{_shade(b, 0.3)}" stroke-width="2"/>
<circle cx="128" cy="172" r="30" fill="none" stroke="{g}" stroke-opacity="0.5" stroke-width="1.4"/>
<circle cx="128" cy="172" r="13" fill="url(#gl{u})" stroke="{g}" stroke-width="1.6"/>
{abxy}
<path d="M98 128 v-10 a8 8 0 0 1 8 -8 h36 a8 8 0 0 1 8 8 v4" fill="{g}"/>
<path d="M382 128 v-10 a8 8 0 0 0 -8 -8 h-36 a8 8 0 0 0 -8 8 v4" fill="{g}"/>
<circle cx="222" cy="216" r="5" fill="{g}"/><circle cx="258" cy="216" r="5" fill="{g}" opacity="0.5"/>
<text x="240" y="300" font-family="sans-serif" font-size="10" fill="#e9e9f2" opacity="0.6" text-anchor="middle" letter-spacing="3">HALL EFFECT ・ 0.8ms</text>"""
    elif kind == "buds":
        body = f"""{shadow(215, 296, 120)}
<rect x="118" y="118" width="190" height="160" rx="34" fill="url(#mb{u})"/>
<rect x="118" y="118" width="190" height="160" rx="34" fill="url(#mt{u})"/>
<rect x="119.6" y="119.6" width="186.8" height="156.8" rx="32.4" fill="none" stroke="#ffffff" stroke-opacity="0.16" stroke-width="1.6"/>
<path d="M120 184 h186" stroke="#000000" stroke-opacity="0.5" stroke-width="3"/>
<path d="M120 188 h186" stroke="#ffffff" stroke-opacity="0.1" stroke-width="1.2"/>
<rect x="186" y="112" width="54" height="10" rx="5" fill="{_shade(b, -0.35)}" stroke="{_shade(b, 0.25)}" stroke-width="1.2"/>
<circle cx="213" cy="206" r="4" fill="{g}"/>
<rect x="196" y="270" width="34" height="8" rx="4" fill="#000000" opacity="0.5"/>
<text x="213" y="246" font-family="sans-serif" font-size="9" fill="{ink}" opacity="0.4" text-anchor="middle" letter-spacing="3">SUZAKU</text>
<g transform="rotate(-14 352 172)">
<circle cx="352" cy="172" r="24" fill="url(#mb{u})" stroke="{_shade(b, 0.32)}" stroke-width="1.6"/>
<circle cx="352" cy="172" r="24" fill="url(#mt{u})"/>
<rect x="342" y="190" width="19" height="52" rx="9" fill="url(#mb{u})" stroke="{_shade(b, 0.32)}" stroke-width="1.4"/>
<rect x="342" y="190" width="19" height="52" rx="9" fill="url(#mt{u})"/>
<rect x="345" y="228" width="13" height="4" rx="2" fill="{g}" opacity="0.9"/>
<circle cx="352" cy="172" r="7" fill="{g}" opacity="0.55"/>
</g>
<g transform="rotate(62 402 268)">
<circle cx="402" cy="268" r="24" fill="url(#mb{u})" stroke="{_shade(b, 0.32)}" stroke-width="1.6"/>
<ellipse cx="402" cy="268" rx="15" ry="15" fill="{_shade(b, -0.4)}"/>
<ellipse cx="402" cy="268" rx="9" ry="9" fill="#07070b" stroke="{_shade(b, 0.2)}" stroke-width="1"/>
<rect x="392" y="286" width="19" height="52" rx="9" fill="url(#mb{u})" stroke="{_shade(b, 0.32)}" stroke-width="1.4"/>
</g>
<path d="M330 96 q-12 14 0 28 M348 84 q-20 24 0 48" fill="none" stroke="{g}" stroke-width="2.6" stroke-linecap="round" opacity="0.55"/>
<text x="240" y="330" font-family="sans-serif" font-size="10" fill="#e9e9f2" opacity="0.6" text-anchor="middle" letter-spacing="3">38ms LOW LATENCY ・ LDAC</text>"""
    elif kind == "charger":
        body = f"""{shadow(240, 292, 110)}
<rect x="152" y="84" width="176" height="176" rx="34" fill="url(#mb{u})"/>
<rect x="152" y="84" width="176" height="176" rx="34" fill="url(#mt{u})"/>
<rect x="153.2" y="85.2" width="173.6" height="173.6" rx="32.8" fill="none" stroke="#ffffff" stroke-opacity="0.14" stroke-width="1.6"/>
<path d="M250 108 l-46 66 h32 l-17 58 l56 -74 h-32 l23 -50z" fill="{g}" stroke="{bd2}" stroke-width="4" stroke-linejoin="round"/>
<rect x="192" y="260" width="16" height="34" rx="5" fill="url(#mt{u})" stroke="{bd2}" stroke-width="1"/>
<rect x="272" y="260" width="16" height="34" rx="5" fill="url(#mt{u})" stroke="{bd2}" stroke-width="1"/>
<rect x="222" y="176" width="36" height="14" rx="7" fill="#07070b" stroke="{g}" stroke-opacity="0.7" stroke-width="1.4" transform="translate(0 62)"/>
<text x="240" y="330" font-family="sans-serif" font-size="12" font-weight="700" fill="#e9e9f2" opacity="0.7" text-anchor="middle" letter-spacing="3">120W GaN</text>"""
    elif kind == "case":
        lattice = "".join(
            f'<path d="M{200 + i * 22} 168 l14 24 l-14 24 l-14 -24 z" fill="none" stroke="{g}" stroke-opacity="0.35" stroke-width="2"/>'
            for i in range(5))
        body = f"""{shadow(240, 322, 100)}
<rect x="152" y="48" width="176" height="266" rx="32" fill="url(#mb{u})"/>
<rect x="152" y="48" width="176" height="266" rx="32" fill="url(#mt{u})"/>
<rect x="153.4" y="49.4" width="173.2" height="263.2" rx="30.6" fill="none" stroke="#ffffff" stroke-opacity="0.13" stroke-width="1.8"/>
<rect x="170" y="64" width="118" height="92" rx="22" fill="#08080c"/>
<rect x="170" y="64" width="118" height="92" rx="22" fill="none" stroke="{_shade(b, 0.4)}" stroke-width="3"/>
<rect x="176" y="70" width="106" height="80" rx="17" fill="none" stroke="#ffffff" stroke-opacity="0.1" stroke-width="1.5"/>
<text x="229" y="115" font-family="sans-serif" font-size="8" fill="#3c3c48" text-anchor="middle" letter-spacing="2">CAMERA CUTOUT</text>
{lattice}
<path d="M240 236 c-6 20 -25 29 -25 49 a25 25 0 0 0 50 0 c0 -20 -19 -29 -25 -49z" fill="none" stroke="{g}" stroke-width="2.8" stroke-linejoin="round"/>
<rect x="326" y="120" width="7" height="42" rx="3.5" fill="{_shade(b, 0.28)}"/>
<rect x="326" y="176" width="7" height="30" rx="3.5" fill="{_shade(b, 0.28)}"/>
<circle cx="163" cy="292" r="5" fill="#08080c" stroke="{_shade(b, 0.3)}" stroke-width="1.2"/>
<text x="240" y="342" font-family="sans-serif" font-size="10" fill="#e9e9f2" opacity="0.6" text-anchor="middle" letter-spacing="3">MIL-STD-810H ・ 1.8m DROP</text>"""
    elif kind == "dock":
        body = f"""{shadow(240, 318, 140)}
<rect x="196" y="64" width="120" height="222" rx="18" fill="#0c0c14" stroke="{_shade(b, 0.32)}" stroke-width="2" transform="rotate(-8 256 175)"/>
<rect x="204" y="72" width="104" height="206" rx="12" fill="#07070b" transform="rotate(-8 256 175)"/>
<rect x="204" y="72" width="104" height="206" rx="12" fill="url(#ag{u})" opacity="0.55" transform="rotate(-8 256 175)"/>
<path d="M256 128 c-6 22 -28 31 -28 54 a28 28 0 0 0 56 0 c0 -23 -22 -32 -28 -54z" fill="none" stroke="{g}" stroke-width="3" stroke-linejoin="round" transform="rotate(-8 256 175)"/>
<text x="256" y="238" font-family="sans-serif" font-size="9" fill="#9c9cb0" text-anchor="middle" letter-spacing="2" transform="rotate(-8 256 175)">80W WIRELESS</text>
<path d="M132 306 L354 306 L332 236 a16 16 0 0 0 -15 -11 L172 225 a16 16 0 0 0 -16 12 Z" fill="url(#mb{u})"/>
<path d="M132 306 L354 306 L332 236 a16 16 0 0 0 -15 -11 L172 225 a16 16 0 0 0 -16 12 Z" fill="url(#mt{u})"/>
<rect x="120" y="300" width="246" height="18" rx="9" fill="{_shade(b, -0.5)}"/>
{"".join(f'<rect x="{170 + i * 26}" y="305" width="14" height="8" rx="2" fill="#07070b"/>' for i in range(6))}
<circle cx="336" cy="264" r="4.5" fill="{g}"/>
<text x="240" y="342" font-family="sans-serif" font-size="10" fill="#e9e9f2" opacity="0.6" text-anchor="middle" letter-spacing="3">4K/120 OUT ・ 80W DOCK</text>"""
    elif kind == "silhouette":
        # ティザー用: 正体不明の端末シルエット(輪郭グロー+「?」+ノイズ粒)
        dots = "".join(
            f'<circle cx="{x}" cy="{y}" r="{r}" fill="{g}" opacity="{o}"/>'
            for x, y, r, o in ((120, 84, 2, 0.6), (356, 66, 1.6, 0.4), (392, 150, 2.4, 0.5),
                               (86, 214, 1.8, 0.35), (368, 268, 2, 0.45), (128, 300, 1.4, 0.3)))
        scan = "".join(
            f'<path d="M60 {70 + i * 34} H420" stroke="{g}" stroke-opacity="{0.05 if i % 2 else 0.09}" stroke-width="1"/>'
            for i in range(8))
        body = f"""{shadow(240, 330, 100)}
{scan}
<rect x="168" y="44" width="144" height="276" rx="26" fill="#050506" stroke="{g}" stroke-width="2" stroke-opacity="0.9"/>
<rect x="168" y="44" width="144" height="276" rx="26" fill="url(#ag{u})" opacity="0.12"/>
<rect x="176" y="52" width="128" height="260" rx="20" fill="#0a0a0c"/>
<path d="M182 58 h44 l-96 248 v-44 z" fill="#ffffff" opacity="0.03"/>
<text x="240" y="206" font-family="'Oswald','Noto Sans JP',sans-serif" font-size="86" font-weight="700" fill="{g}" text-anchor="middle" opacity="0.95">?</text>
<rect x="206" y="286" width="68" height="10" rx="5" fill="none" stroke="{g}" stroke-opacity="0.5" stroke-width="1.4"/>
{dots}
<path d="M150 118 h-24 M150 140 h-38 M330 200 h24 M330 222 h38" stroke="{g}" stroke-opacity="0.5" stroke-width="1.6"/>
<text x="240" y="348" font-family="monospace" font-size="11" fill="{g}" opacity="0.75" text-anchor="middle" letter-spacing="6">UNIT_00 ・ CLASSIFIED</text>"""
    elif kind == "shield":
        # 法人MDM: 盾+ポリシー行+管理下の端末群(フリート管理コンソールの図)
        rows = "".join(
            f'<rect x="252" y="{116 + i * 34}" width="150" height="24" rx="6" fill="#ffffff" fill-opacity="0.05"/>'
            f'<circle cx="266" cy="{128 + i * 34}" r="5" fill="none" stroke="{g}" stroke-width="1.6"/>'
            f'<path d="M263 {128 + i * 34} l2.4 2.6 4 -5" fill="none" stroke="{g}" stroke-width="1.6" stroke-linecap="round"/>'
            f'<rect x="280" y="{124 + i * 34}" width="{w}" height="7" rx="3" fill="#9aa4b8" opacity="0.7"/>'
            for i, w in enumerate((96, 78, 108, 66)))
        fleet = "".join(
            f'<rect x="{96 + i * 34}" y="272" width="22" height="38" rx="5" fill="#10131a" stroke="{"#4a7ac8" if i < 4 else "#3a3f4c"}" stroke-width="1.5"/>'
            f'<circle cx="{107 + i * 34}" cy="304" r="1.8" fill="{"#7ee787" if i < 4 else "#3a3f4c"}"/>'
            for i in range(5))
        body = f"""{shadow(240, 322, 130)}
<path d="M162 78 l62 -26 62 26 v52 c0 46 -28 74 -62 90 c-34 -16 -62 -44 -62 -90 z" fill="#10131a" stroke="{g}" stroke-width="3" stroke-linejoin="round"/>
<path d="M162 78 l62 -26 62 26 v52 c0 46 -28 74 -62 90 c-34 -16 -62 -44 -62 -90 z" fill="url(#ag{u})" opacity="0.25"/>
<path d="M198 128 l18 19 34 -40" fill="none" stroke="{g}" stroke-width="7" stroke-linecap="round" stroke-linejoin="round"/>
<text x="327" y="100" font-family="sans-serif" font-size="10" font-weight="700" fill="#9aa4b8" letter-spacing="2">POLICY</text>
{rows}
{fleet}
<text x="240" y="340" font-family="sans-serif" font-size="10" fill="#e9e9f2" opacity="0.6" text-anchor="middle" letter-spacing="3">MDM READY ・ ZERO-TOUCH</text>"""
    elif kind == "clcase":
        # コラボ専用ケース。motifごとに完全個別デザイン(端末の意匠を引き継ぐ)。
        if motif == "genshin":
            elems = ("#74c2a8", "#d8b45c", "#a68cc8", "#9ac546", "#4cc2f1", "#ef7938", "#9fd6e3")
            dots = "".join(
                f'<circle cx="{240 + 58 * math.cos(math.radians(-90 + i * 360 / 7)):.1f}" cy="{136 + 58 * math.sin(math.radians(-90 + i * 360 / 7)):.1f}" r="4.5" fill="{c}"/>'
                for i, c in enumerate(elems))
            body = f"""{shadow(240, 322, 92)}
<rect x="162" y="48" width="156" height="272" rx="30" fill="url(#mb{u})"/>
<rect x="162" y="48" width="156" height="272" rx="30" fill="url(#mt{u})"/>
<rect x="163.4" y="49.4" width="153.2" height="269.2" rx="28.6" fill="none" stroke="#c9a24b" stroke-width="2"/>
<circle cx="240" cy="136" r="46" fill="#0e0e12" stroke="#c9a24b" stroke-width="2.4"/>
<circle cx="240" cy="136" r="58" fill="none" stroke="#c9a24b" stroke-opacity="0.5" stroke-width="1.2" stroke-dasharray="2 5"/>
{dots}
<path d="M240 216 c-4.5 16 -20 22 -20 39 a20 20 0 0 0 40 0 c0 -17 -15.5 -23 -20 -39z" fill="none" stroke="#c9a24b" stroke-width="2.2"/>
<path d="M176 62 h-8 v8 M304 62 h8 v8 M176 306 h-8 v-8 M304 306 h8 v-8" fill="none" stroke="#c9a24b" stroke-width="2"/>
<text x="240" y="340" font-family="sans-serif" font-size="10" fill="#9c9cb0" text-anchor="middle" letter-spacing="3">SHICHIYO PORCELAIN CASE</text>"""
        elif motif == "wuwa":
            body = f"""{shadow(240, 322, 92)}
<rect x="166" y="48" width="148" height="272" rx="10" fill="url(#mb{u})"/>
<rect x="166" y="48" width="148" height="272" rx="10" fill="url(#mt{u})"/>
<rect x="167.2" y="49.2" width="145.6" height="269.6" rx="9" fill="none" stroke="#ffffff" stroke-opacity="0.16" stroke-width="1.4"/>
<rect x="180" y="62" width="58" height="132" rx="10" fill="#0b0b0f" stroke="{_shade(b, 0.3)}" stroke-width="1.4"/>
<path d="M226 232 v30 M246 232 v30 M226 262 a10 10 0 0 0 20 0" fill="none" stroke="{g}" stroke-opacity="0.8" stroke-width="2.2" stroke-linecap="round"/>
<path d="M188 216 l10 0 4 -12 6 24 6 -18 4 6 h12" fill="none" stroke="{g}" stroke-opacity="0.5" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" transform="translate(52 60)"/>
<text x="240" y="340" font-family="sans-serif" font-size="10" fill="#9c9cb0" text-anchor="middle" letter-spacing="3">ZANKYO MONOLITH CASE</text>"""
        elif motif == "nte":
            body = f"""{shadow(240, 322, 92)}
<rect x="162" y="48" width="156" height="272" rx="26" fill="{_shade(b, -0.2)}" opacity="0.55"/>
<rect x="162" y="48" width="156" height="272" rx="26" fill="url(#mt{u})" opacity="0.6"/>
<rect x="163.4" y="49.4" width="153.2" height="269.2" rx="24.6" fill="none" stroke="{g}" stroke-width="2.2" filter="url(#fz{u})" opacity="0.8"/>
<rect x="163.4" y="49.4" width="153.2" height="269.2" rx="24.6" fill="none" stroke="{g}" stroke-width="1.4"/>
<rect x="176" y="62" width="128" height="74" rx="22" fill="#0b0b0f" stroke="{_shade(b, 0.35)}" stroke-width="1.4"/>
<path d="M196 196 h34 a10 10 0 0 1 0 20 h-22 a10 10 0 0 0 0 20 h34" fill="none" stroke="{g}" stroke-width="3" stroke-linecap="round" filter="url(#fz{u})" opacity="0.7"/>
<path d="M196 196 h34 a10 10 0 0 1 0 20 h-22 a10 10 0 0 0 0 20 h34" fill="none" stroke="{g}" stroke-width="1.6" stroke-linecap="round"/>
<path d="M262 208 l10 -12 v32 l10 -12" fill="none" stroke="#39d7f5" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"/>
<text x="240" y="340" font-family="sans-serif" font-size="10" fill="#9c9cb0" text-anchor="middle" letter-spacing="3">YAKO CLEAR EL CASE</text>"""
        else:  # endfield
            ribs = "".join(f'<rect x="{178 + i * 26}" y="150" width="10" height="150" rx="4" fill="#000000" opacity="0.18"/>' for i in range(5))
            body = f"""{shadow(240, 322, 96)}
<rect x="158" y="44" width="164" height="280" rx="18" fill="url(#mb{u})"/>
<rect x="158" y="44" width="164" height="280" rx="18" fill="url(#mt{u})"/>
{ribs}
<rect x="159.6" y="45.6" width="160.8" height="276.8" rx="16.4" fill="none" stroke="#ffffff" stroke-opacity="0.16" stroke-width="1.6"/>
<rect x="172" y="58" width="94" height="94" rx="14" fill="#0e0e0c" stroke="{_shade(b, 0.3)}" stroke-width="1.6"/>
<path d="M158 70 l20 -20 h16 l-20 20 z" fill="{g}"/>
<path d="M302 304 l20 20 h-16 l-20 -20 z" fill="{g}"/>
{"".join(f'<circle cx="{x}" cy="{y}" r="3.4" fill="{_shade(b, -0.45)}" stroke="{_shade(b, 0.3)}" stroke-width="1"/>' for x, y in ((172, 60, ), (308, 60), (172, 310), (308, 310)))}
<circle cx="296" cy="288" r="10" fill="none" stroke="{_shade(b, 0.35)}" stroke-width="4"/>
<text x="240" y="196" font-family="'Oswald',sans-serif" font-size="11" font-weight="700" fill="{ink}" opacity="0.7" text-anchor="middle" letter-spacing="2">// ARMOR CASE</text>
<text x="240" y="340" font-family="sans-serif" font-size="10" fill="#9c9cb0" text-anchor="middle" letter-spacing="3">MIL-SPEC ・ LANYARD READY</text>"""
    elif kind == "clbuds":
        # コラボ専用ワイヤレスイヤホン。motifごとに完全個別デザイン。
        if motif == "genshin":
            elems = ("#74c2a8", "#d8b45c", "#a68cc8", "#9ac546", "#4cc2f1", "#ef7938", "#9fd6e3")
            dots = "".join(
                f'<circle cx="{212 + 46 * math.cos(math.radians(-90 + i * 360 / 7)):.1f}" cy="{186 + 46 * math.sin(math.radians(-90 + i * 360 / 7)):.1f}" r="3.6" fill="{c}"/>'
                for i, c in enumerate(elems))
            body = f"""{shadow(240, 296, 100)}
<circle cx="212" cy="186" r="72" fill="url(#mb{u})"/>
<circle cx="212" cy="186" r="72" fill="url(#mt{u})"/>
<circle cx="212" cy="186" r="70.6" fill="none" stroke="#c9a24b" stroke-width="2"/>
<circle cx="212" cy="186" r="46" fill="none" stroke="#c9a24b" stroke-opacity="0.5" stroke-width="1" stroke-dasharray="2 4"/>
{dots}
<path d="M212 166 c-3.6 13 -16 18 -16 31 a16 16 0 0 0 32 0 c0 -13 -12.4 -18 -16 -31z" fill="none" stroke="#c9a24b" stroke-width="2"/>
<ellipse cx="322" cy="150" rx="22" ry="26" fill="url(#mb{u})" stroke="#c9a24b" stroke-width="1.4"/>
<rect x="314" y="170" width="14" height="42" rx="7" fill="url(#mb{u})" stroke="#c9a24b" stroke-width="1.2"/>
<ellipse cx="352" cy="216" rx="22" ry="26" fill="url(#mb{u})" stroke="#c9a24b" stroke-width="1.4"/>
<rect x="344" y="236" width="14" height="42" rx="7" fill="url(#mb{u})" stroke="#c9a24b" stroke-width="1.2"/>
<text x="240" y="330" font-family="sans-serif" font-size="10" fill="#9c9cb0" text-anchor="middle" letter-spacing="3">元素の音 ・ LDAC ・ 32H</text>"""
        elif motif == "wuwa":
            body = f"""{shadow(240, 292, 104)}
<rect x="140" y="120" width="150" height="130" rx="12" fill="url(#mb{u})"/>
<rect x="140" y="120" width="150" height="130" rx="12" fill="url(#mt{u})"/>
<rect x="141.2" y="121.2" width="147.6" height="127.6" rx="11" fill="none" stroke="#ffffff" stroke-opacity="0.16" stroke-width="1.2"/>
<path d="M158 186 l12 0 5 -14 8 28 8 -20 5 6 h20" fill="none" stroke="{g}" stroke-opacity="0.8" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
<circle cx="272" cy="136" r="3" fill="{g}"/>
<ellipse cx="322" cy="160" rx="20" ry="24" fill="url(#mb{u})" stroke="{_shade(b, 0.35)}" stroke-width="1.4"/>
<path d="M318 178 v26 M326 178 v26 M318 204 a4 4 0 0 0 8 0" fill="none" stroke="{g}" stroke-opacity="0.8" stroke-width="1.8" stroke-linecap="round"/>
<ellipse cx="360" cy="212" rx="20" ry="24" fill="url(#mb{u})" stroke="{_shade(b, 0.35)}" stroke-width="1.4"/>
<path d="M356 230 v26 M364 230 v26 M356 256 a4 4 0 0 0 8 0" fill="none" stroke="{g}" stroke-opacity="0.8" stroke-width="1.8" stroke-linecap="round"/>
<text x="240" y="330" font-family="sans-serif" font-size="10" fill="#9c9cb0" text-anchor="middle" letter-spacing="3">残響の音叉ステム ・ 24bit</text>"""
        elif motif == "nte":
            body = f"""{shadow(240, 292, 104)}
<rect x="146" y="128" width="150" height="116" rx="58" fill="{_shade(b, -0.15)}" opacity="0.6"/>
<rect x="146" y="128" width="150" height="116" rx="58" fill="url(#mt{u})" opacity="0.6"/>
<rect x="147.4" y="129.4" width="147.2" height="113.2" rx="56.6" fill="none" stroke="{g}" stroke-width="2" filter="url(#fz{u})" opacity="0.8"/>
<rect x="147.4" y="129.4" width="147.2" height="113.2" rx="56.6" fill="none" stroke="{g}" stroke-width="1.3"/>
<path d="M186 172 h22 a8 8 0 0 1 0 16 h-14 a8 8 0 0 0 0 16 h22" fill="none" stroke="{g}" stroke-width="2" stroke-linecap="round"/>
<path d="M244 180 l8 -10 v26 l8 -10" fill="none" stroke="#39d7f5" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/>
<ellipse cx="330" cy="164" rx="21" ry="25" fill="{_shade(b, -0.1)}" stroke="{g}" stroke-width="1.6"/>
<circle cx="330" cy="158" r="6" fill="{g}" opacity="0.9"/>
<ellipse cx="362" cy="220" rx="21" ry="25" fill="{_shade(b, -0.1)}" stroke="#39d7f5" stroke-width="1.6"/>
<circle cx="362" cy="214" r="6" fill="#39d7f5" opacity="0.9"/>
<text x="240" y="330" font-family="sans-serif" font-size="10" fill="#9c9cb0" text-anchor="middle" letter-spacing="3">EL GLOW ・ 空間オーディオ</text>"""
        else:  # endfield
            body = f"""{shadow(240, 296, 104)}
<rect x="136" y="116" width="156" height="140" rx="14" fill="url(#mb{u})"/>
<rect x="136" y="116" width="156" height="140" rx="14" fill="url(#mt{u})"/>
<rect x="137.4" y="117.4" width="153.2" height="137.2" rx="12.6" fill="none" stroke="#ffffff" stroke-opacity="0.16" stroke-width="1.4"/>
<path d="M136 128 l14 -14 h12 l-14 14 z" fill="{g}"/>
{"".join(f'<rect x="{150 + i * 24}" y="132" width="9" height="108" rx="4" fill="#000000" opacity="0.16"/>' for i in range(5))}
<rect x="152" y="226" width="70 " height="8" rx="3" fill="#2a2a22"/>
<rect x="152" y="226" width="62" height="8" rx="3" fill="{g}"/>
<circle cx="286" cy="132" r="9" fill="none" stroke="{_shade(b, 0.35)}" stroke-width="3.4"/>
<ellipse cx="330" cy="168" rx="21" ry="25" fill="url(#mb{u})" stroke="{g}" stroke-width="1.6"/>
<rect x="322" y="188" width="15" height="34" rx="7" fill="url(#mb{u})" stroke="{g}" stroke-width="1.2"/>
<ellipse cx="366" cy="224" rx="21" ry="25" fill="url(#mb{u})" stroke="{g}" stroke-width="1.6"/>
<rect x="358" y="244" width="15" height="34" rx="7" fill="url(#mb{u})" stroke="{g}" stroke-width="1.2"/>
<text x="240" y="330" font-family="sans-serif" font-size="10" fill="#9c9cb0" text-anchor="middle" letter-spacing="3">// FIELD BUDS ・ IP57</text>"""
    elif kind == "powerbank":
        # コラボ・モバイルバッテリー。motif(作品slug)ごとにシルエットから別設計。
        if motif == "genshin":
            # 七天神像の石碑を思わせる縦長アーチ型・白磁×金リング
            elems = ("#74c2a8", "#d8b45c", "#a68cc8", "#9ac546", "#4cc2f1", "#ef7938", "#9fd6e3")
            dots = "".join(
                f'<circle cx="{240 + 52 * math.cos(math.radians(-90 + i * 360 / 7)):.1f}" cy="{150 + 52 * math.sin(math.radians(-90 + i * 360 / 7)):.1f}" r="6" fill="{c}" opacity="0.95"/>'
                for i, c in enumerate(elems))
            body = f"""{shadow(240, 312, 96)}
<path d="M164 312 V150 a76 76 0 0 1 152 0 v162 z" fill="url(#mb{u})"/>
<path d="M164 312 V150 a76 76 0 0 1 152 0 v162 z" fill="url(#mt{u})"/>
<path d="M165.4 310.6 V150 a74.6 74.6 0 0 1 149.2 0 v160.6 z" fill="none" stroke="#c9a24b" stroke-width="2.2"/>
<circle cx="240" cy="150" r="52" fill="none" stroke="#c9a24b" stroke-opacity="0.6" stroke-width="1.6" stroke-dasharray="2 5"/>
{dots}
<path d="M240 128 c-5 18 -22 25 -22 44 a22 22 0 0 0 44 0 c0 -19 -17 -26 -22 -44z" fill="none" stroke="#c9a24b" stroke-width="2.6" stroke-linejoin="round"/>
<path d="M188 236 H292" stroke="#c9a24b" stroke-opacity="0.55" stroke-width="1.2"/>
<text x="240" y="262" font-family="'Shippori Mincho',serif" font-size="11" font-weight="800" fill="{ink}" opacity="0.8" text-anchor="middle" letter-spacing="3">七耀の灯</text>
{"".join(f'<circle cx="{216 + i * 16}" cy="284" r="4" fill="#c9a24b" opacity="{0.95 - i * 0.22:.2f}"/>' for i in range(4))}
<rect x="222" y="304" width="36" height="8" rx="4" fill="#07070b" stroke="#c9a24b" stroke-width="1.2"/>
<text x="240" y="336" font-family="sans-serif" font-size="10" fill="#9c9cb0" text-anchor="middle" letter-spacing="3">10000mAh ・ 45W MAGNETIC</text>"""
        elif motif == "wuwa":
            # 漆黒の薄板モノリス・波形窓・音叉マーク(端末「残響」と同意匠)
            body = f"""{shadow(240, 306, 110)}
<rect x="150" y="66" width="180" height="240" rx="10" fill="url(#mb{u})"/>
<rect x="150" y="66" width="180" height="240" rx="10" fill="url(#mt{u})"/>
<rect x="151.2" y="67.2" width="177.6" height="237.6" rx="9" fill="none" stroke="#ffffff" stroke-opacity="0.16" stroke-width="1.4"/>
<rect x="170" y="96" width="140" height="58" rx="6" fill="#07070b" stroke="{_shade(b, 0.3)}" stroke-width="1.2"/>
<path d="M180 125 l14 0 5 -16 8 32 8 -24 6 8 h60" fill="none" stroke="#00e0ff" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"/>
<path d="M226 196 v40 M254 196 v40 M226 236 a14 14 0 0 0 28 0" fill="none" stroke="{g}" stroke-opacity="0.85" stroke-width="2.6" stroke-linecap="round"/>
{"".join(f'<circle cx="{216 + i * 16}" cy="262" r="3.5" fill="{g}" opacity="{0.95 - i * 0.22:.2f}"/>' for i in range(4))}
<rect x="222" y="284" width="36" height="8" rx="4" fill="#07070b" stroke="{_shade(b, 0.3)}" stroke-width="1.2"/>
<text x="240" y="330" font-family="sans-serif" font-size="10" fill="#9c9cb0" text-anchor="middle" letter-spacing="3">10000mAh ・ 45W ・ 12.8mm SLIM</text>"""
        elif motif == "nte":
            # ネオン看板ボックス・ネオン管の縁とサイン
            body = f"""{shadow(240, 300, 108)}
<rect x="146" y="76" width="188" height="216" rx="22" fill="url(#mb{u})"/>
<rect x="146" y="76" width="188" height="216" rx="22" fill="url(#mt{u})"/>
<rect x="154" y="84" width="172" height="200" rx="16" fill="none" stroke="{g}" stroke-width="2.6" opacity="0.9" filter="url(#fz{u})"/>
<rect x="154" y="84" width="172" height="200" rx="16" fill="none" stroke="{g}" stroke-width="1.6"/>
<path d="M186 138 h44 a12 12 0 0 1 0 24 h-28 a12 12 0 0 0 0 24 h44" fill="none" stroke="{g}" stroke-width="4" stroke-linecap="round" filter="url(#fz{u})" opacity="0.7"/>
<path d="M186 138 h44 a12 12 0 0 1 0 24 h-28 a12 12 0 0 0 0 24 h44" fill="none" stroke="{g}" stroke-width="2" stroke-linecap="round"/>
<path d="M262 150 l12 -14 v38 l12 -14" fill="none" stroke="#39d7f5" stroke-width="3" stroke-linecap="round" stroke-linejoin="round" filter="url(#fz{u})" opacity="0.8"/>
<path d="M262 150 l12 -14 v38 l12 -14" fill="none" stroke="#39d7f5" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/>
{"".join(f'<circle cx="{198 + i * 18}" cy="222" r="3.5" fill="{c}" opacity="0.85"/>' for i, c in enumerate((g, "#39d7f5", "#ffd166", g, "#39d7f5")))}
{"".join(f'<circle cx="{212 + i * 16}" cy="250" r="3.5" fill="{g}" opacity="{0.95 - i * 0.22:.2f}"/>' for i in range(4))}
<rect x="222" y="268" width="36" height="8" rx="4" fill="#07070b" stroke="{_shade(b, 0.3)}" stroke-width="1.2"/>
<text x="240" y="318" font-family="sans-serif" font-size="10" fill="#9c9cb0" text-anchor="middle" letter-spacing="3">10000mAh ・ 45W ・ EL SIGN</text>"""
        elif motif == "endfield":
            # リブ付き工具箱型・ハザードコーナー・計器LED(端末「前線」と同意匠)
            ribs = "".join(f'<rect x="{168 + i * 30}" y="84" width="12" height="200" rx="5" fill="#000000" opacity="0.16"/>' for i in range(5))
            body = f"""{shadow(240, 300, 116)}
<rect x="142" y="76" width="196" height="216" rx="14" fill="url(#mb{u})"/>
<rect x="142" y="76" width="196" height="216" rx="14" fill="url(#mt{u})"/>
{ribs}
<rect x="143.4" y="77.4" width="193.2" height="213.2" rx="12.6" fill="none" stroke="#ffffff" stroke-opacity="0.14" stroke-width="1.6"/>
<path d="M142 100 l24 -24 h20 l-24 24 z" fill="{g}"/>
<path d="M314 268 l24 24 h-20 l-24 -24 z" fill="{g}"/>
{"".join(f'<circle cx="{x}" cy="{y}" r="3.6" fill="{_shade(b, -0.45)}" stroke="{_shade(b, 0.3)}" stroke-width="1"/>' for x, y in ((156, 90, ), (324, 90), (156, 278), (324, 278)))}
<rect x="180" y="128" width="120" height="44" rx="8" fill="#101010" stroke="{_shade(b, 0.3)}" stroke-width="1.4"/>
<text x="240" y="147" font-family="ui-monospace,monospace" font-size="9" fill="{g}" text-anchor="middle" letter-spacing="1">PWR ▮▮▮▮▮ 100%</text>
<rect x="188" y="154" width="104" height="7" rx="3" fill="#2a2a22"/>
<rect x="188" y="154" width="98" height="7" rx="3" fill="{g}"/>
<text x="240" y="204" font-family="'Oswald',sans-serif" font-size="13" font-weight="700" fill="{ink}" opacity="0.8" text-anchor="middle" letter-spacing="3">// ZENSEN PACK</text>
{"".join(f'<circle cx="{212 + i * 16}" cy="232" r="3.5" fill="{g}" opacity="{0.95 - i * 0.22:.2f}"/>' for i in range(4))}
<rect x="216" y="256" width="48" height="12" rx="4" fill="#07070b" stroke="{_shade(b, 0.3)}" stroke-width="1.4"/>
<text x="240" y="318" font-family="sans-serif" font-size="10" fill="#9c9cb0" text-anchor="middle" letter-spacing="3">10000mAh ・ 45W ・ 18W OUT</text>"""
        else:
            leds = "".join(f'<circle cx="{204 + i * 24}" cy="238" r="5" fill="{g}" opacity="{0.95 - i * 0.22:.2f}"/>' for i in range(4))
            body = f"""{shadow(240, 302, 120)}
<rect x="140" y="72" width="200" height="216" rx="30" fill="url(#mb{u})"/>
<rect x="140" y="72" width="200" height="216" rx="30" fill="url(#mt{u})"/>
<rect x="141.4" y="73.4" width="197.2" height="213.2" rx="28.6" fill="none" stroke="#ffffff" stroke-opacity="0.14" stroke-width="1.8"/>
<circle cx="240" cy="150" r="66" fill="none" stroke="{_shade(b, 0.28)}" stroke-width="2" stroke-dasharray="7 7" opacity="0.9"/>
<path d="M240 118 c-7 26 -32 37 -32 64 a32 32 0 0 0 64 0 c0 -27 -25 -38 -32 -64z" fill="none" stroke="{g}" stroke-width="3.4"/>
{leds}
<rect x="286" y="230" width="34" height="16" rx="8" fill="#07070b" stroke="{_shade(b, 0.3)}" stroke-width="1.4"/>
<rect x="222" y="286" width="36" height="9" rx="4.5" fill="#07070b" stroke="{_shade(b, 0.3)}" stroke-width="1.4"/>
<text x="240" y="270" font-family="sans-serif" font-size="12" font-weight="800" fill="{ink}" opacity="0.75" text-anchor="middle" letter-spacing="2">10000mAh ・ 45W</text>
<text x="240" y="330" font-family="sans-serif" font-size="10" fill="#9c9cb0" text-anchor="middle" letter-spacing="3">MAGNETIC WIRELESS</text>"""
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 480 360" role="img" aria-label="">{common}{body}</svg>'


BRAND_MARK = """<svg viewBox="0 0 48 48" fill="none" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
<path class="brand-mark__flame" d="M24 4 C21 16 10 21 10 31 a14 14 0 0 0 28 0 C38 21 27 16 24 4 Z" stroke="url(#bm-g)" stroke-width="3" stroke-linejoin="round"/>
<circle cx="24" cy="33" r="4.2" fill="#e8442e"/>
<defs><linearGradient id="bm-g" x1="10" y1="4" x2="38" y2="45"><stop stop-color="#ff6a3c"/><stop offset="1" stop-color="#e8442e"/></linearGradient></defs>
</svg>"""

FAVICON = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 48 48"><rect width="48" height="48" rx="10" fill="#0b0b10"/><path d="M24 6 C21.4 16.5 12 21 12 30 a12 12 0 0 0 24 0 C36 21 26.6 16.5 24 6 Z" fill="none" stroke="#e8442e" stroke-width="3" stroke-linejoin="round"/><circle cx="24" cy="31.5" r="3.6" fill="#ff6a3c"/></svg>"""

ICONS = {
    "search": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" aria-hidden="true"><circle cx="11" cy="11" r="7"/><path d="M20 20l-3.5-3.5"/></svg>',
    "cart": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M6 7h13l-1.5 9h-10z"/><path d="M6 7L5 4H2.5"/><circle cx="9" cy="20" r="1.6"/><circle cx="16" cy="20" r="1.6"/></svg>',
    "user": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" aria-hidden="true"><circle cx="12" cy="8.5" r="4"/><path d="M4.5 20c1.5-3.5 4.2-5 7.5-5s6 1.5 7.5 5"/></svg>',
}


# ==========================================================================
# ニュースのアイキャッチ(カテゴリ別・決定的生成)。外部画像に頼らない。
# ==========================================================================
_NEWS_EC_PAL = {
    "製品": ("#e8442e", "#d9a441"),
    "技術": ("#2fb6d0", "#5b8cff"),
    "企業": ("#d9a441", "#e8442e"),
    "開発者": ("#2fd0a0", "#2fb6d0"),
    "コラボ": ("#a15bff", "#33ccdd"),
}


def news_eyecatch(cat, seed, glow=None):
    """記事カテゴリ(と任意のグロー)から決定的に生成する抽象アイキャッチ(640×260)。
    seed(記事id等)でモチーフ配置を変え、同じ記事は常に同じ絵になる。"""
    c1, c2 = _NEWS_EC_PAL.get(cat, ("#e8442e", "#d9a441"))
    if glow:
        c1 = glow
    h = 0
    for ch in str(seed):
        h = (h * 131 + ord(ch)) & 0xFFFFFFFF
    u = f"ec{h:x}"
    rnd = []
    x = h or 1
    for _ in range(12):
        x = (1103515245 * x + 12345) & 0x7FFFFFFF
        rnd.append(x / 0x7FFFFFFF)
    # 対角ライン
    lines = "".join(
        f'<path d="M{-60 + i * 90} 260 L{60 + i * 90} 0" stroke="#fff" stroke-opacity="{0.03 + rnd[i % 12] * 0.05:.3f}" stroke-width="1.5"/>'
        for i in range(9))
    # 円(泡)
    circs = "".join(
        f'<circle cx="{int(40 + rnd[i] * 560)}" cy="{int(30 + rnd[i + 1] * 200)}" r="{int(10 + rnd[i + 2] * 46)}" '
        f'fill="{c2 if i % 2 else c1}" fill-opacity="{0.06 + rnd[i] * 0.10:.3f}"/>'
        for i in range(0, 8, 2))
    # 前景の大リング
    rx = int(430 + rnd[3] * 120)
    return (
        f'<svg viewBox="0 0 640 260" role="img" aria-label="{cat}の記事アイキャッチ" width="640" height="260" preserveAspectRatio="xMidYMid slice">'
        f'<defs><linearGradient id="{u}g" x1="0" y1="0" x2="1" y2="1">'
        f'<stop offset="0" stop-color="{c1}" stop-opacity="0.52"/><stop offset="0.62" stop-color="{c2}" stop-opacity="0.16"/><stop offset="1" stop-color="#0d0d13" stop-opacity="1"/></linearGradient>'
        f'<radialGradient id="{u}r" cx="0.72" cy="0.32" r="0.62">'
        f'<stop offset="0" stop-color="{c1}" stop-opacity="0.62"/><stop offset="1" stop-color="{c1}" stop-opacity="0"/></radialGradient></defs>'
        f'<rect width="640" height="260" fill="#0d0d13"/><rect width="640" height="260" fill="url(#{u}g)"/>'
        f'{lines}{circs}'
        f'<circle cx="{rx}" cy="70" r="120" fill="none" stroke="{c1}" stroke-opacity="0.45" stroke-width="2"/>'
        f'<circle cx="{rx}" cy="70" r="120" fill="url(#{u}r)"/>'
        f'<rect width="640" height="260" fill="url(#{u}r)" opacity="0.5"/>'
        f'<text x="34" y="150" font-family="sans-serif" font-size="17" font-weight="800" letter-spacing="6" fill="#fff" fill-opacity="0.9">{cat.upper() if cat.isascii() else cat}</text>'
        f'<text x="34" y="176" font-family="sans-serif" font-size="12" font-weight="700" letter-spacing="4" fill="{c1}">SUZAKU NEWSROOM</text>'
        f'</svg>')
