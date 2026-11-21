"""python3 render.py <주제> [<주제> ...] → out/<주제>/card_N.png, .jpg 와 caption.txt
주제 파일: topics/<주제>.py (SPEC, CAPTION). 렌더는 Playwright(Chromium)."""
import importlib.util, os, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import cards

for name in sys.argv[1:]:
    spec_path = os.path.join(HERE, "topics", name + ".py")
    mod = importlib.util.module_from_spec(importlib.util.spec_from_file_location(name, spec_path))
    mod.__spec__.loader.exec_module(mod)
    out = os.path.join(HERE, "out", name)
    os.makedirs(out, exist_ok=True)
    for f in os.listdir(out):
        os.remove(os.path.join(out, f))
    pages = cards.build(mod.SPEC)
    for i, h in enumerate(pages, 1):
        open(os.path.join(out, f"{i}.html"), "w").write(h)
    subprocess.run(["node", os.path.join(HERE, "shot.js"), out, str(len(pages))], check=True)
    from PIL import Image
    for i in range(1, len(pages) + 1):
        Image.open(os.path.join(out, f"card_{i}.png")).convert("RGB").save(os.path.join(out, f"card_{i}.jpg"), quality=95)
        os.remove(os.path.join(out, f"{i}.html"))
    open(os.path.join(out, "caption.txt"), "w").write(mod.CAPTION.strip() + "\n")
    print(name, len(pages), "장")
