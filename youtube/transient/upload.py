# RC·RL 과도응답 업로드 정보 (publish.yml 입력값). python3 upload.py → upload.json
# 2026-10-25 사용자: 썸네일 V2, 10/26 12시 롱폼 + 쇼츠·릴스 A·B, 10/27 12시 C·D·E
import json, os
D = "과도응답"
SITE = "https://tjguswns6891-blip.github.io/test1/circuit/"
PL = "https://www.youtube.com/playlist?list=PLIXOZZwVtrbM"
LONG = os.environ.get("LONG", "{long}")
BASE = ("회로이론,전기회로,회로해석,전기전자,전자공학,전기공학,전기기사,공대생,공대,대학생,전공공부,시험공부,"
        "중간고사,기말고사,공학,shorts,쇼츠")
chap = """00:00 스위치 켜도 바로 안 올라가는 이유
00:10 왜 바로 안 바뀔까
00:24 RC 충전과 시정수
00:53 RC 방전
01:09 RL 회로
01:31 만능 공식
01:45 스위치 문제 3단계
02:22 정리"""
long = {"platform": "youtube", "video": f"{D}/long.sfx.mp4", "thumbnail": f"{D}/thumb_V2.png",
        "title": "RC 회로 과도응답 한 번에 정리 | 시정수, 충전·방전, RL 회로, 스위치 문제",
        "description": f"""스위치를 켜도 커패시터 전압은 바로 안 올라가요.
시정수 τ = RC와 63.2%, 충전·방전, RL 회로, 만능 공식 하나로 스위치 문제까지 정리했어요.

📚 회로이론 모아보기: {PL}
🔌 제가 만든 무료 사이트 '보이는 회로이론': {SITE}

{chap}

#회로이론 #과도응답 #시정수 #RC회로 #전기전자""",
        "tags": "회로이론,과도응답,과도현상,시정수,RC회로,RL회로,RC충전,RC방전,커패시터,인덕터,1차회로,스위치문제,"
                "초기조건,만능공식,회로해석,전기회로,기초회로이론,회로이론강의,전기전자,전자공학,전기공학,공대,공대생,"
                "중간고사,기말고사,전기기사,보이는회로이론",
        "publish_at": "2026-10-26T12:00:00+09:00"}
CL = {
 "A": ("시정수 τ = RC, 63.2%만 기억하면 끝 #shorts #회로이론 #시정수", "시정수,타우,RC회로,RC시정수,시정수공식,충전,방전,과도응답",
       "시정수, 숫자 하나만 기억하세요", "τ = RC, 10kΩ에 100μF면 1초.\n1τ 지나면 63.2%까지 차고, 방전은 36.8%가 남아요. 5τ면 다 찼다고 봐요.", "시정수"),
 "B": ("커패시터 전압은 순간에 못 바뀐다, 스위치 직전 = 직후 #shorts #회로이론 #과도응답", "커패시터,커패시터전압,연속성,초기조건,과도응답,인덕터전류,스위치,커패시터전류",
       "스위치를 켜도 커패시터 전압은 바로 안 바뀝니다", "i = C·dv/dt, 전압이 순간에 바뀌면 전류가 무한대가 돼요.\n그래서 v_C(0⁻) = v_C(0⁺). 인덕터는 반대로 전류가 연속이에요.", "과도응답"),
 "C": ("스위치 문제, t=0⁻ → 0⁺ → ∞ 세 단계면 끝 #shorts #회로이론 #과도응답", "스위치문제,과도응답,초기조건,최종값,정상상태,시정수,1차회로,커패시터",
       "스위치 문제, 세 단계면 끝납니다", "0⁻: 직류 정상상태라 커패시터는 개방, 12V.\n0⁺: 커패시터 전압은 그대로 12V. ∞: 분압으로 6V, τ = 1초.", "스위치문제"),
 "D": ("RL 회로, 인덕터는 전류를 붙잡는다 τ = L/R #shorts #회로이론 #RL회로", "RL회로,인덕터,RL시정수,시정수,인덕터전류,과도응답,인덕터시정수,1차회로",
       "인덕터는 전류를 붙잡습니다", "스위치를 켜도 전류는 0에서 천천히 올라가요.\n시정수는 L/R, RC는 곱하기 RL은 나누기. 오래 지나면 인덕터는 그냥 전선이에요.", "RL회로"),
 "E": ("만능 공식 하나로 1차 회로 과도응답 끝 #shorts #회로이론 #과도응답", "1차회로,과도응답,만능공식,초기값,최종값,시정수,RC회로,RL회로",
       "1차 회로, 공식 하나로 끝납니다", "x(t) = x(∞) + [x(0⁺) − x(∞)]·e^(−t/τ)\n구할 건 처음값, 최종값, 시정수 세 개뿐이에요.", "과도응답"),
}
out = {"long": long}
for k, (title, tags, hook, body, ht) in CL.items():
    at = "2026-10-26T12:00:00+09:00" if k in "AB" else "2026-10-27T12:00:00+09:00"
    out[k] = {"short": {"platform": "youtube", "video": f"{D}/쇼츠_{k}.sfx.mp4", "title": title,
                        "description": f"📺 전체 정리: {LONG}\n📚 회로이론 모아보기: {PL}\n🔌 무료 사이트 '보이는 회로이론': {SITE}\n\n{body}\n\n#shorts #회로이론 #전기전자 #공대생 #과도응답 #시정수 #회로해석 #전기기사 #공대공부",
                        "tags": tags + "," + BASE, "publish_at": at},
              "reel": {"platform": "instagram", "video": f"{D}/릴스_{k}.sfx.mp4", "thumbnail": f"{D}/cover_{k}.png", "at": at,
                       "caption": f"전기전자 주목⚡ {hook}\n\n{body}\n\n📌 시험 전에 저장, 같은 과 친구 태그해 주세요\n💬 팔로우하고 댓글에 '회로' 남겨 주시면, DM으로 사이트 링크 보내 드릴게요\n\n#회로이론 #전기전자 #공대생 #공대공부 #{ht}"}}
here = os.path.dirname(os.path.abspath(__file__))
json.dump(out, open(f"{here}/upload.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(len(long["tags"]), [len(out[k]["short"]["tags"]) for k in CL], [len(out[k]["short"]["tags"].split(",")) for k in CL])
