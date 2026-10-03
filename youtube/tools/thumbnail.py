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
    # 경고등 칩
    cf = font(BLACK, 38)
    cx, y = x, y + 6
    for s, color in CHIPS:
        w = text_w(d, s, cf)
        d.rounded_rectangle((cx, y, cx + w + 36, y + 62), 14, fill=(28, 31, 40), outline=color, width=4)
        d.ellipse((cx + 14, y + 23, cx + 30, y + 39), fill=color)  # 경고등 불빛
        d.text((cx + 38, y + 5), s, font=cf, fill=WHITE)
        cx += w + 36 + 18
    y += 90
    # 질문 띠
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
    bw = max(bw, text_w(d, QUESTION, qf) + 64)
    bw = min(bw, right - left)
    x0 = left + ((right - left) - bw) / 2
    cxm = x0 + bw / 2
    gap, chip_h, q_h, badge_h = 18, 62, 96, 58
    heights = [badge_h + 26] + [int(s * 1.18) for _, s in LINES] + [28, chip_h + 28, q_h]
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
    # 칩: 같은 폭으로
    n = len(CHIPS)
    cw = (bw - gap * (n - 1)) / n
    size = 38
    while size > 24 and max(text_w(d, t, font(BLACK, size)) for t, _ in CHIPS) > cw - 54:
        size -= 2
    cf = font(BLACK, size)
    for i, (t, color) in enumerate(CHIPS):
        cx = x0 + i * (cw + gap)
        d.rounded_rectangle((cx, y, cx + cw, y + chip_h), 14, fill=(28, 31, 40), outline=color, width=4)
        tw = text_w(d, t, cf)
        tx = cx + (cw - (tw + 26)) / 2
        d.ellipse((tx, y + chip_h / 2 - 8, tx + 16, y + chip_h / 2 + 8), fill=color)
        d.text((tx + 26, y + chip_h / 2), t, font=cf, fill=WHITE, anchor="lm")
    y += chip_h + 28
    # 질문 띠: 묶음 폭 그대로, 글씨 가운데
    d.rounded_rectangle((x0, y, x0 + bw, y + q_h), 18, fill=UP)
    d.text((cxm, y + q_h / 2), QUESTION, font=qf, fill=WHITE, anchor="mm")


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("person", help="인물 이미지 (배경 투명 PNG, 또는 --cutout 과 함께 영상 프레임)")
    p.add_argument("--cutout", action="store_true", help="rembg 로 배경을 지운다")
    p.add_argument("--height", type=int, default=650, help="인물 높이(px)")
    p.add_argument("--right", type=int, default=1300, help="인물 오른쪽 끝 x (화면 밖으로 조금 넘겨도 됨)")
    p.add_argument("-o", "--out", default="thumbnail.png")
    p.add_argument("--align", choices=["left", "center"], default="center",
                   help="center: 글씨 묶음을 좌우 대칭(같은 폭)으로, left: 예전처럼 왼쪽 정렬")
    p.add_argument("--text-left", type=int, default=48, help="글씨 칸 왼쪽 x (center 정렬)")
    p.add_argument("--text-right", type=int, default=700, help="글씨 칸 오른쪽 x (center 정렬, 인물 얼굴 앞)")
    p.add_argument("--config", help="문구 JSON: badge, lines[[[글자,색],...],크기], chips[[글자,색]], question. 색은 white/up/down/accent")
    args = p.parse_args()
    if args.config:
        import json
        global BADGE, LINES, CHIPS, QUESTION
        col = {"white": WHITE, "up": UP, "down": DOWN, "accent": ACCENT}
        with open(args.config, encoding="utf-8") as f:
            cfg = json.load(f)
        BADGE = cfg.get("badge", BADGE)
        if "lines" in cfg:
            LINES = [([(t, col[c]) for t, c in parts], size) for parts, size in cfg["lines"]]
        if "chips" in cfg:
            CHIPS = [(t, col[c]) for t, c in cfg["chips"]]
        QUESTION = cfg.get("question", QUESTION)

    img = background()
    person = person_layer(args.person, args.cutout, args.height)
    img.alpha_composite(person, (args.right - person.width, H - person.height + 30))

    d = ImageDraw.Draw(img)
    if args.align == "center":
        draw_text_centered(img, d, args.text_left, args.text_right)
    else:
        draw_text_left(img, d)

    img.convert("RGB").save(args.out, quality=95)
    print(f"썸네일: {args.out} ({W}×{H})")


if __name__ == "__main__":
    main()
