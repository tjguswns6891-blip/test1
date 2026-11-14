"""python3 enqueue.py <video-files 작업트리> <주제> <시각 ISO> [<주제> <시각> ...]
out/<주제>/card_*.jpg 를 video-files 의 카드/<주제>/ 로 복사하고 queue.json 에 카드 항목을 추가한다 (이미 있으면 시각만 갱신).
커밋·푸시는 직접 한다 (queue.json 은 다른 세션도 고치므로 푸시 직전에 pull)."""
import glob, json, os, shutil, sys

HERE = os.path.dirname(os.path.abspath(__file__))
vf, args = sys.argv[1], sys.argv[2:]
q = json.load(open(os.path.join(vf, "queue.json")))
for name, at in zip(args[::2], args[1::2]):
    src = sorted(glob.glob(os.path.join(HERE, "out", name, "card_*.jpg")), key=lambda p: int(p.rsplit("_", 1)[1][:-4]))
    dst = os.path.join(vf, "카드", name)
    os.makedirs(dst, exist_ok=True)
    for f in src:
        shutil.copy(f, dst)
    item = {"id": "C-" + name, "kind": "card", "at": at,
            "cards": [f"카드/{name}/{os.path.basename(f)}" for f in src],
            "ig_caption": open(os.path.join(HERE, "out", name, "caption.txt")).read().strip(), "status": "pending"}
    old = next((e for e in q["items"] if e["id"] == item["id"]), None)
    if old:
        old.update({k: v for k, v in item.items() if k != "status"})
    else:
        q["items"].append(item)
    print(item["id"], at, len(src), "장")
json.dump(q, open(os.path.join(vf, "queue.json"), "w"), ensure_ascii=False, indent=1)
