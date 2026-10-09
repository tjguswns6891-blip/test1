#!/usr/bin/env python3
"""클라우드소마 언박싱 썸네일 (1280×720). 인물 컷아웃 + 신발 컷아웃 + 큰 문구.

사용: python3 thumbnail.py person.png shoe.png -o out_dir
  person.png / shoe.png 는 배경을 지운 PNG (rembg). 인물은 박스·팔이 걸리지 않게 --person-crop 으로 자른다.
"""
import argparse
import os

from PIL import Image, ImageDraw, ImageFilter, ImageFont

W, H = 1280, 720
BG = (18, 17, 16)
INK, HAZE, COBBLE, MUTE = (243, 240, 232), (231, 226, 154), (160, 135, 105), (168, 161, 146)
FONTS = os.path.expanduser("~/.fonts")
BLACK = os.path.join(FONTS, "NotoSansCJKkr-Black.otf")
BOLD = os.path.join(FONTS, "NotoSansCJKkr-Bold.otf")


def font(path, size):
    return ImageFont.truetype(path, size)


def outlined(img, xy, text, f, fill, stroke=7):
    sh = Image.new("RGBA", img.size, (0, 0, 0, 0))
    ImageDraw.Draw(sh).text((xy[0] + 5, xy[1] + 7), text, font=f, fill=(0, 0, 0, 180),
                            stroke_width=stroke, stroke_fill=(0, 0, 0, 180))
    img.alpha_composite(sh.filter(ImageFilter.GaussianBlur(7)))
    ImageDraw.Draw(img).text(xy, text, font=f, fill=fill, stroke_width=stroke, stroke_fill=(10, 10, 9))


def sticker(im, border=10, shadow=True):
    """컷아웃에 흰 테두리와 그림자를 두른다."""
    a = im.getchannel("A")
    edge = a.filter(ImageFilter.MaxFilter(border * 2 + 1))
    pad = border * 3
    out = Image.new("RGBA", (im.width + pad * 2, im.height + pad * 2), (0, 0, 0, 0))
    if shadow:
        sh = Image.new("RGBA", im.size, (0, 0, 0, 0))
        sh.putalpha(edge.point(lambda v: v * 0.65))
        out.alpha_composite(sh.filter(ImageFilter.GaussianBlur(14)), (pad + 6, pad + 10))
    wh = Image.new("RGBA", im.size, (255, 255, 255, 0))
    wh.putalpha(edge)
    out.alpha_composite(wh, (pad, pad))
    out.alpha_composite(im, (pad, pad))
    return out


def fit(im, height=None, width=None):
    im = im.crop(im.getbbox())
    r = height / im.height if height else width / im.width
    return im.resize((round(im.width * r), round(im.height * r)), Image.LANCZOS)


def background():
    img = Image.new("RGBA", (W, H), BG + (255,))
    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    g = ImageDraw.Draw(glow)
    g.ellipse((640, 60, 1400, 820), fill=COBBLE + (110,))
    g.ellipse((-260, 360, 620, 980), fill=HAZE + (38,))
    img.alpha_composite(glow.filter(ImageFilter.GaussianBlur(130)))
    # 돌 원 (협업의 마지막을 상징하는 테네리페 원형 설치물)
    ring = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(ring)
    import math, random
    rnd = random.Random(7)
    cx, cy, R = 980, 330, 300
    for i in range(70):
        a = i / 70 * math.tau
        x, y = cx + math.cos(a) * (R + rnd.uniform(-8, 8)), cy + math.sin(a) * (R + rnd.uniform(-8, 8))
        w = rnd.uniform(8, 17)
        d.ellipse((x - w, y - w * 0.7, x + w, y + w * 0.7), fill=(200, 192, 176, 70))
    img.alpha_composite(ring)
    return img


def text_block(img, x, y, big_size=138):
    d = ImageDraw.Draw(img)
    kf = font(BOLD, 34)
    k = "On × POST ARCHIVE FACTION"
    kw = d.textlength(k, font=kf)
    d.rounded_rectangle((x, y, x + kw + 40, y + 58), 29, outline=HAZE, width=3, fill=(18, 17, 16, 200))
    d.text((x + 20, y + 5), k, font=kf, fill=HAZE)
    y += 78
    bf = font(BLACK, big_size)
    outlined(img, (x, y), "마지막", bf, INK, stroke=8)
    outlined(img, (x, y + int(big_size * 1.08)), "신발", bf, HAZE, stroke=8)
    return y + int(big_size * 2.25)


def pill(img, x, y, text, size=56, fill=HAZE, ink=BG):
    d = ImageDraw.Draw(img)
    f = font(BLACK, size)
    w = d.textlength(text, font=f)
    d.rounded_rectangle((x, y, x + w + 44, y + size * 1.45), 16, fill=fill)
    d.text((x + 22, y + size * 0.08), text, font=f, fill=ink)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("person")
    p.add_argument("shoe")
    p.add_argument("--person-crop", default="600,0,1650,860", help="인물 컷아웃에서 쓸 영역 x1,y1,x2,y2")
    p.add_argument("-o", "--out", default=".")
    args = p.parse_args()
    os.makedirs(args.out, exist_ok=True)

    person = Image.open(args.person).convert("RGBA").crop(tuple(int(v) for v in args.person_crop.split(",")))
    shoe = Image.open(args.shoe).convert("RGBA")

    # A: 인물 오른쪽, 신발은 앞쪽 아래에 크게, 문구는 왼쪽
    img = background()
    ps = sticker(fit(person, height=800))            # 원본에서 머리가 화면 위에 닿아 있어 위쪽을 밖으로 뺀다
    img.alpha_composite(ps, (W - ps.width + 90, H - ps.height + 40))
    ss = sticker(fit(shoe, width=640), border=8)
    img.alpha_composite(ss, (440, H - ss.height + 36))
    yb = text_block(img, 48, 40)
    pill(img, 52, yb + 22, "파프를 1/3 가격에")
    img.convert("RGB").save(os.path.join(args.out, "thumbnail_A.png"))

    # B: 신발을 주인공으로 크게, 인물은 오른쪽 위에서 반응
    img = background()
    ps = sticker(fit(person, height=740))
    img.alpha_composite(ps, (W - ps.width + 110, H - ps.height + 30))
    ss = sticker(fit(shoe, width=820), border=8)
    img.alpha_composite(ss, (250, H - ss.height + 50))
    yb = text_block(img, 48, 40, big_size=118)
    pill(img, 52, yb + 18, "23.9만 원", size=52, fill=INK)
    img.convert("RGB").save(os.path.join(args.out, "thumbnail_B.png"))
    print("썸네일:", os.path.join(args.out, "thumbnail_A.png"), os.path.join(args.out, "thumbnail_B.png"))


if __name__ == "__main__":
    main()
