# 영상 편집 작업 순서 (다른 세션에서 이어 하기용)

"유튜브 영상 편집" 세션(브랜치 `claude/usage-history-access-tu81at`)의 도구·효과음·대본 자료를 그대로 옮겨 왔다.
여러 세션이 동시에 다른 영상을 편집할 수 있다. 새 세션에서는 먼저 `bash youtube/setup.sh`.

## 자료 위치
| 폴더 | 내용 |
|---|---|
| `tools/` | 편집 도구 (아래 순서) |
| `sfx/kit/` | 상황별 효과음 16개 (intro·visual·emph·trans·cta·base), `sfx/*.mp3` 예전 효과음 |
| `logos/` | 썸네일용 회사 로고 PNG (`tools/logos.js` 로 추가) |
| `index.html`, `today/`, `0930`·`1001`·`1003`·`1009`, `linalg/`, `circuit/`, `cloudsoma/` | 영상별 대본·카드·썸네일·쇼츠 구성 |
| `subs/` | 자막 교정(fixes.txt)·사진 등장 문구(image_cues.json)·쇼츠 구성(shorts.json) |
| `script_guide.md` | 대본 쓰는 규칙 (참고 릴스 분석·후킹 문장) |
| `reels.md` | 릴스 캡션·해시태그 기록 (해시태그 5개 규칙) |
| `upload.md` | 업로드 제목·설명 |
| `raw/` | 촬영 원본 (git에 안 올라감 → 영상마다 `fetch_drive.py` 로 다시 받는다) |

## 편집 순서
```bash
cd youtube/tools
python3 fetch_drive.py "<구글 드라이브 공유 링크>" -o ../raw/<날짜>   # 1) 원본 받기
python3 transcribe.py ../raw/<날짜>/raw.mp4 --hotwords "..." --fix ../subs/fixes.txt   # 2) 받아쓰기
python3 align_script.py ../raw/<날짜>/raw.words.json                  # 3) 대본과 맞추기
python3 retakes.py ...                                                # 4) NG 테이크 찾기
python3 autocut.py ../raw/<날짜>/raw.mp4 --transcript ... --cut-file ...retakes.json   # 5) 컷 편집
python3 compose.py raw.cut.cuts.json raw.script.words.json -o final.mp4 --cues ../subs/image_cues.json [--sub-box]  # 6) 자막·사진·모션카드
python3 broll.py ...            # (선택) 화면 녹화 B롤 + 얼굴 PIP
python3 shorts.py raw.cut.cuts.json raw.script.words.json ../subs/shorts.json -o shorts/   # 7) 쇼츠 9:16
python3 sfx.py ...              # 8) 쇼츠 효과음 (30초에 4~8개)
python3 thumbnail.py frame.png --cutout -o thumb.png   # 9) 썸네일 1280×720
```
각 도구의 자세한 옵션은 파일 맨 위 설명과 `-h` 참고.

## 정해 둔 규칙
- 색: 배경 #111318 · 상승 #ff5a5f · 하락 #4c8dff · 강조 #ffc53d · 폰트 Noto Sans CJK KR
- 증시 영상에는 "투자 권유 아님" 고정 문구
- 쇼츠 배치: 카드 칸 크게, 얼굴은 아래 작게, 자막은 그 사이 고정
- 두 줄 자막은 상자 하나로 (`--sub-box`)
- 로고는 해당 회사를 가리키는 용도로만

## 동시에 작업할 때
- 영상마다 폴더를 따로 쓴다 (`raw/<날짜>`, `youtube/<날짜>/`). 같은 파일(`index.html`, `subs/*.json`)을 두 세션이 동시에 고치면 충돌한다.
- 각 세션은 자기 브랜치에 올린다.
