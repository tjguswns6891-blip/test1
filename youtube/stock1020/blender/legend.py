# Intro3D 위에 얹는 범례 PNG (1920×1080). 숫자는 Yahoo 종가(raw/stock1020/yf.json).
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../tools")); import shorts as S
from PIL import Image, ImageDraw, ImageFont
f = ImageFont.truetype(S.FONT_BLACK, 54); g = ImageFont.truetype(S.FONT_BLACK, 40)
im = Image.new('RGBA', (1920, 1080)); d = ImageDraw.Draw(im)
d.text((80, 150), "최근 1년 · 10/20 마감", font=g, fill=(141, 148, 161, 255))
for y, c, t in [(215, (255, 94, 110), "코스피  오늘 −3.7% · 6월 꼭대기 대비 −39%"), (295, (120, 200, 255), "미국 S&P 500  어젯밤 +0.4% · 나스닥 +1.1%")]:
    d.ellipse((80, y + 12, 112, y + 44), fill=c + (255,)); d.text((132, y), t, font=f, fill=c + (255,), stroke_width=5, stroke_fill=(10, 11, 14, 255))
im.save(sys.argv[1])
