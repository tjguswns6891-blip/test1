# Intro3D 위에 얹는 제목 PNG (1920×1080).
import sys, os, json
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../tools")); import shorts as S
from PIL import Image, ImageDraw, ImageFont
f = ImageFont.truetype(S.FONT_BLACK, 58); g = ImageFont.truetype(S.FONT_BLACK, 38)
im = Image.new('RGBA', (1920, 1080)); d = ImageDraw.Draw(im)
d.text((80, 140), "코스피 종가 · 10/30 → 11/6", font=g, fill=(141, 148, 161, 255))
d.text((80, 200), "5,731 → 5,060  한 주 −11.7%", font=f, fill=(255, 197, 61, 255), stroke_width=5, stroke_fill=(10, 11, 14, 255))
im.save(sys.argv[1])
