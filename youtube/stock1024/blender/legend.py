# Intro3D 위에 얹는 제목 PNG (1920×1080). 숫자는 Yahoo 종가(raw/stock1024/yf.json)·기사.
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../tools")); import shorts as S
from PIL import Image, ImageDraw, ImageFont
f = ImageFont.truetype(S.FONT_BLACK, 58); g = ImageFont.truetype(S.FONT_BLACK, 38)
im = Image.new('RGBA', (1920, 1080)); d = ImageDraw.Draw(im)
d.text((80, 140), "이번 주 코스피 · 5분봉 · 10/19 ~ 10/23", font=g, fill=(141, 148, 161, 255))
d.text((80, 200), "5,668 → 5,550  주간 −2.1%", font=f, fill=(255, 197, 61, 255), stroke_width=5, stroke_fill=(10, 11, 14, 255))
im.save(sys.argv[1])
