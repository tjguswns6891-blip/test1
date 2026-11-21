import sys, glob
from PIL import Image
for n in sys.argv[1:]:
    fs = sorted(glob.glob(f'out/{n}/card_*.png'), key=lambda p: int(p.rsplit('_', 1)[1][:-4]))
    w, h = 450, 562
    s = Image.new('RGB', (w * 3 + 40, h * 2 + 30), '#222')
    for k, f in enumerate(fs):
        s.paste(Image.open(f).resize((w, h)), (10 + (k % 3) * (w + 10), 10 + (k // 3) * (h + 10)))
    s.save(f'out/{n}/sheet.png')
