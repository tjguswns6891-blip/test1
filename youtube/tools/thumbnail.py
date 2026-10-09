#!/usr/bin/env python3
"""인물 컷아웃과 큰 문구로 유튜브 썸네일(1280×720)을 만드는 도구.

사용 예:
  python3 thumbnail.py person.png -o thumb.png                  # 인물 PNG(배경 투명)
  python3 thumbnail.py frame.png --cutout -o thumb.png          # 영상 프레임에서 배경 자동 제거 (rembg)

문구는 아래 LINES/CHIPS 를 영상마다 바꿔 쓴다. 색은 영상 그래픽과 같은 규칙:
배경 #111318 · 상승 #ff5a5f · 하락 #4c8dff · 강조 #ffc53d · 폰트 Noto Sans CJK KR.
"""
import argparse
import os

from PIL import Image, ImageDraw, ImageFilter, ImageFont

W, H = 1280, 720
BG = (17, 19, 24)
UP, DOWN, ACCENT, WHITE = (255, 90, 95), (76, 141, 255), (255, 197, 61), (255, 255, 255)
FONT_DIR = os.path.expanduser("~/.fonts")
BLACK = os.path.join(FONT_DIR, "NotoSansCJKkr-Black.otf")
BOLD = os.path.join(FONT_DIR, "NotoSansCJKkr-Bold.otf")

BADGE = "50년 데이터로 본 지금"
# 한 줄 = [(글자, 색), ...], 글자 크기
LINES = [
    ([("주가는 ", WHITE), ("사상 최고", UP)], 92),
    ([("경고등 ", WHITE), ("3개", ACCENT)], 150),
]
CHIPS = [("금리 5.18%", UP), ("유가 +66%", UP), ("물가 3.4%", UP)]
QUESTION = "지금 뭘 사야 할까?"
BG_STYLE = "stock"                # "linalg": 격자·벡터 배경


def font(path, size):
    return ImageFont.truetype(path, size)


def text_w(draw, s, f):
    return draw.textlength(s, font=f)


def draw_outlined(img, xy, s, f, fill, stroke=8, shadow=True):
    d = ImageDraw.Draw(img)
    if shadow:
        sh = Image.new("RGBA", img.size, (0, 0, 0, 0))
        ImageDraw.Draw(sh).text((xy[0] + 6, xy[1] + 8), s, font=f, fill=(0, 0, 0, 170),
                                stroke_width=stroke, stroke_fill=(0, 0, 0, 170))
        img.alpha_composite(sh.filter(ImageFilter.GaussianBlur(8)))
    d.text(xy, s, font=f, fill=fill, stroke_width=stroke, stroke_fill=(10, 11, 14))


def arrow(d, p0, p1, color, width=12, head=34):
    import math
    a = math.atan2(p1[1] - p0[1], p1[0] - p0[0])
    base = (p1[0] - head * 0.8 * math.cos(a), p1[1] - head * 0.8 * math.sin(a))
    d.line([p0, base], fill=color, width=width)
    l = (p1[0] - head * math.cos(a - 0.45), p1[1] - head * math.sin(a - 0.45))
    r = (p1[0] - head * math.cos(a + 0.45), p1[1] - head * math.sin(a + 0.45))
    d.polygon([p1, l, r], fill=color)


LOGO_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "logos")
LOGOS = []                      # [{"file": "samsung", "label": "", "x": 1250, "y": 36, "h": 64, "align": "right"}]


def draw_logos(img):
    """회사 로고(logos.js 로 만든 브랜드 색 PNG)를 흰 둥근 판 위에 얹는다. 판들은 위에서 아래로 쌓인다."""
    d = ImageDraw.Draw(img)
    for it in LOGOS:
        h, pad = it.get("h", 64), it.get("pad", 22)
        logo = Image.open(os.path.join(LOGO_DIR, it["file"] + ".png")).convert("RGBA")
        logo = logo.resize((round(logo.width * h / logo.height), h), Image.LANCZOS)
        label = it.get("label", "")
        f = font(BLACK, round(h * 0.78))
        lw = round(text_w(d, label, f)) + 16 if label else 0
        w, hh = logo.width + lw + 2 * pad, h + 2 * pad
        x = it["x"] - w if it.get("align", "right") == "right" else it["x"]
        y = it["y"]
        sh = Image.new("RGBA", img.size, (0, 0, 0, 0))
        ImageDraw.Draw(sh).rounded_rectangle((x + 4, y + 8, x + w + 4, y + hh + 8), 24, fill=(0, 0, 0, 150))
        img.alpha_composite(sh.filter(ImageFilter.GaussianBlur(10)))
        ImageDraw.Draw(img).rounded_rectangle((x, y, x + w, y + hh), 24, fill=(255, 255, 255, 255))
        img.alpha_composite(logo, (x + pad, y + pad))
        if label:
            ImageDraw.Draw(img).text((x + pad + logo.width + 16, y + hh / 2), label, font=f, fill=(17, 19, 24),
                                     anchor="lm")


def background_linalg():
    """선형대수 영상용: 행렬로 기울어진 격자 + 두 열벡터(주황·초록)와 그 평행사변형(파랑)."""
    img = Image.new("RGBA", (W, H), BG + (255,))
    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    g = ImageDraw.Draw(glow)
    g.ellipse((700, 40, 1360, 760), fill=DOWN + (95,))        # 인물 뒤 파란 빛
    g.ellipse((-200, 380, 500, 900), fill=ACCENT + (24,))
    img.alpha_composite(glow.filter(ImageFilter.GaussianBlur(120)))
    ox, oy = 1075, 330                                        # 원점 (인물 머리 오른쪽 빈자리)
    a, b = (150, -40), (40, -150)                             # 행렬의 두 열 (화면 좌표, y 는 아래가 +)
    T = lambda u, v: (ox + u * a[0] + v * b[0], oy + u * a[1] + v * b[1])
    grid = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gd = ImageDraw.Draw(grid)
    for k in range(-14, 15):
        col = (255, 255, 255, 70) if k == 0 else (140, 150, 190, 34)
        gd.line([T(k, -14), T(k, 14)], fill=col, width=3 if k == 0 else 2)
        gd.line([T(-14, k), T(14, k)], fill=col, width=3 if k == 0 else 2)
    img.alpha_composite(grid)
    vec = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    vd = ImageDraw.Draw(vec)
    vd.polygon([T(0, 0), T(1, 0), T(1, 1), T(0, 1)], fill=DOWN + (90,), outline=DOWN + (200,))
    arrow(vd, T(0, 0), T(1, 0), (255, 140, 40, 255))
    arrow(vd, T(0, 0), T(0, 1), (46, 204, 113, 255))
    vd.ellipse((ox - 9, oy - 9, ox + 9, oy + 9), fill=(255, 255, 255, 230))
    img.alpha_composite(vec)
    return img


def background():
    img = Image.new("RGBA", (W, H), BG + (255,))
    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    g = ImageDraw.Draw(glow)
    g.ellipse((700, 40, 1360, 760), fill=UP + (90,))          # 인물 뒤 붉은 빛
    g.ellipse((-200, 380, 500, 900), fill=ACCENT + (28,))
    img.alpha_composite(glow.filter(ImageFilter.GaussianBlur(120)))
    # 오른쪽 위로 치솟는 주가선 (배경 장식)
    line = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    pts = [(0, 610), (120, 590), (220, 600), (330, 540), (430, 560), (540, 470), (640, 490),
           (760, 380), (860, 400), (980, 260), (1090, 280), (1280, 90)]
    ImageDraw.Draw(line).line(pts, fill=UP + (70,), width=10, joint="curve")
    img.alpha_composite(line.filter(ImageFilter.GaussianBlur(1)))
    return img


def person_layer(src, cutout, height):
    im = Image.open(src).convert("RGBA")
    if cutout:
        from rembg import new_session, remove
        im = remove(im, session=new_session("birefnet-portrait"))
    im = im.crop(im.getbbox())
    scale = height / im.height
    im = im.resize((int(im.width * scale), int(im.height * scale)), Image.LANCZOS)
    alpha = im.getchannel("A")
    # 흰 테두리(스티커 느낌) + 그림자
    edge = alpha.filter(ImageFilter.MaxFilter(13))
    outline = Image.new("RGBA", im.size, WHITE + (0,))
    outline.putalpha(edge)
    shadow = Image.new("RGBA", im.size, (0, 0, 0, 0))
    shadow.putalpha(edge.point(lambda v: v * 0.6))
    layer = Image.new("RGBA", (im.width + 60, im.height + 60), (0, 0, 0, 0))
    layer.alpha_composite(shadow.filter(ImageFilter.GaussianBlur(14)), (36, 40))
    layer.alpha_composite(outline, (30, 30))
    layer.alpha_composite(im, (30, 30))
    return layer


CHIP_H, CHIP_PAD, DOT, DOT_GAP = 62, 20, 16, 12


def chip_width(d, text, f):
    """칩 폭 = 왼쪽 여백 + 불빛 + 간격 + 글씨 실제 폭(외곽 픽셀 기준) + 오른쪽 여백."""
    l, _, r, _ = d.textbbox((0, 0), text, font=f, anchor="lm")
    return CHIP_PAD + DOT + DOT_GAP + (r - l) + CHIP_PAD


def draw_chip(d, x, y, w, text, color, size=38):
    """칩 틀 안에 글씨가 반드시 들어가게 그린다. 폭 w 를 주면 넘칠 때 글씨를 줄이고, 내용은 틀 가운데."""
    f = font(BLACK, size)
    while w and size > 22 and chip_width(d, text, f) > w:
        size -= 2
        f = font(BLACK, size)
    need = chip_width(d, text, f)
    w = w or need
    d.rounded_rectangle((x, y, x + w, y + CHIP_H), 14, fill=(28, 31, 40), outline=color, width=4)
    l, _, r, _ = d.textbbox((0, 0), text, font=f, anchor="lm")
    sx = x + (w - need) / 2 + CHIP_PAD
    cy = y + CHIP_H / 2
    d.ellipse((sx, cy - DOT / 2, sx + DOT, cy + DOT / 2), fill=color)   # 경고등 불빛
    d.text((sx + DOT + DOT_GAP - l, cy), text, font=f, fill=WHITE, anchor="lm")
    return w


def draw_text_left(img, d):
    x, y = 56, 52
    # 배지
    bf = font(BOLD, 34)
    bw = text_w(d, BADGE, bf)
    d.rounded_rectangle((x, y, x + bw + 40, y + 58), 29, fill=ACCENT)
    d.text((x + 20, y + 4), BADGE, font=bf, fill=BG)
    y += 84
    # 큰 문구
    for parts, size in LINES:
        f = font(BLACK, size)
        cx = x
        for s, color in parts:
            draw_outlined(img, (cx, y), s, f, color, stroke=max(6, size // 16))
            cx += text_w(d, s, f)
        y += int(size * 1.18)
    # 경고등 칩 (글씨가 틀 밖으로 나가지 않게 실제 폭을 재서 틀을 만든다)
    cx, y = x, y + 20          # 큰 글씨 획에 칩이 닿지 않게
    for t, color in CHIPS:
        cx += draw_chip(d, cx, y, 0, t, color) + 18
    y += 86
    # 질문 띠 (question 을 "" 로 주면 생략)
    if not QUESTION:
        return
    qf = font(BLACK, 64)
    qw = text_w(d, QUESTION, qf)
    d.rounded_rectangle((x - 8, y, x + qw + 40, y + 96), 18, fill=UP)
    draw_outlined(img, (x + 16, y + 4), QUESTION, qf, WHITE, stroke=0, shadow=False)


def draw_text_centered(img, d, left, right):
    """글씨 묶음을 한 폭(가장 긴 줄)에 맞춰 좌우 대칭으로 놓는다.
    배지·큰 문구는 가운데 정렬, 칩은 같은 폭으로 나눠 채우고, 질문 띠는 묶음 폭 그대로. 묶음은 글씨 칸과 화면 높이의 가운데."""
    def line_w(parts, size):
        f = font(BLACK, size)
        return sum(text_w(d, t, f) for t, _ in parts)

    bw = max(line_w(p, s) for p, s in LINES)
    qf = font(BLACK, 64)
    if QUESTION:
        bw = max(bw, text_w(d, QUESTION, qf) + 64)
    bw = min(bw, right - left)
    x0 = left + ((right - left) - bw) / 2
    cxm = x0 + bw / 2
    gap, chip_h, q_h, badge_h = 18, 62, 96, 58
    heights = [badge_h + 26] + [int(s * 1.18) for _, s in LINES] + [28, chip_h + 28, q_h if QUESTION else 0]
    y = (H - sum(heights)) / 2 + 8
    # 배지
    bf = font(BOLD, 34)
    w = text_w(d, BADGE, bf) + 40
    d.rounded_rectangle((cxm - w / 2, y, cxm + w / 2, y + badge_h), 29, fill=ACCENT)
    d.text((cxm, y + badge_h / 2), BADGE, font=bf, fill=BG, anchor="mm")
    y += badge_h + 26
    # 큰 문구
    for parts, size in LINES:
        f = font(BLACK, size)
        cx = cxm - line_w(parts, size) / 2
        for t, color in parts:
            draw_outlined(img, (cx, y), t, f, color, stroke=max(6, size // 16))
            cx += text_w(d, t, f)
        y += int(size * 1.18)
    y += 28                     # 큰 글씨 획(외곽선)이 칩에 닿지 않게
    # 칩: 같은 폭으로 (넘치면 글씨를 줄인다)
    n = len(CHIPS)
    cw = (bw - gap * (n - 1)) / n
    for i, (t, color) in enumerate(CHIPS):
        draw_chip(d, x0 + i * (cw + gap), y, cw, t, color)
    y += chip_h + 28
    # 질문 띠: 묶음 폭 그대로, 글씨 가운데
    if not QUESTION:
        return
    d.rounded_rectangle((x0, y, x0 + bw, y + q_h), 18, fill=UP)
    d.text((cxm, y + q_h / 2), QUESTION, font=qf, fill=WHITE, anchor="mm")


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("person", help="인물 이미지 (배경 투명 PNG, 또는 --cutout 과 함께 영상 프레임)")
    p.add_argument("--cutout", action="store_true", help="rembg 로 배경을 지운다")
    p.add_argument("--height", type=int, default=650, help="인물 높이(px)")
    p.add_argument("--right", type=int, default=1300, help="인물 오른쪽 끝 x (화면 밖으로 조금 넘겨도 됨)")
    p.add_argument("-o", "--out", default="thumbnail.png")
    p.add_argument("--align", choices=["left", "center"], default="left",
                   help="center: 글씨 묶음을 좌우 대칭(같은 폭)으로, left: 예전처럼 왼쪽 정렬")
    p.add_argument("--text-left", type=int, default=48, help="글씨 칸 왼쪽 x (center 정렬)")
    p.add_argument("--text-right", type=int, default=700, help="글씨 칸 오른쪽 x (center 정렬, 인물 얼굴 앞)")
    p.add_argument("--config", help="문구 JSON: badge, lines[[[글자,색],...],크기], chips[[글자,색]], question. 색은 white/up/down/accent")
    args = p.parse_args()
    if args.config:
        import json
        global BADGE, LINES, CHIPS, QUESTION, BG_STYLE, LOGOS
        col = {"white": WHITE, "up": UP, "down": DOWN, "accent": ACCENT}
        with open(args.config, encoding="utf-8") as f:
            cfg = json.load(f)
        BADGE = cfg.get("badge", BADGE)
        if "lines" in cfg:
            LINES = [([(t, col[c]) for t, c in parts], size) for parts, size in cfg["lines"]]
        if "chips" in cfg:
            CHIPS = [(t, col[c]) for t, c in cfg["chips"]]
        QUESTION = cfg.get("question", QUESTION)
        BG_STYLE = cfg.get("bg", BG_STYLE)
        LOGOS = cfg.get("logos", LOGOS)

    img = background_linalg() if BG_STYLE == "linalg" else background()
    person = person_layer(args.person, args.cutout, args.height)
    img.alpha_composite(person, (args.right - person.width, H - person.height + 30))
    draw_logos(img)

    d = ImageDraw.Draw(img)
    if args.align == "center":
        draw_text_centered(img, d, args.text_left, args.text_right)
    else:
        draw_text_left(img, d)

    img.convert("RGB").save(args.out, quality=95)
    print(f"썸네일: {args.out} ({W}×{H})")


if __name__ == "__main__":
    main()
