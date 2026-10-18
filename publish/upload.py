"""유튜브·인스타 공식 API로 영상 하나를 올린다 (표준 라이브러리만 사용).

  python3 publish/upload.py youtube   VIDEO --title T [--description D] [--tags a,b] [--privacy public]
                                      [--publish-at 2026-10-20T18:00:00+09:00] [--thumbnail PNG]
  python3 publish/upload.py instagram VIDEO_URL --caption C [--cover-url URL] [--share-to-feed]

필요한 환경 변수 (GitHub 저장소 Secrets에 넣고 publish.yml이 넘겨 준다):
  유튜브: YT_CLIENT_ID, YT_CLIENT_SECRET, YT_REFRESH_TOKEN
  인스타: IG_ACCESS_TOKEN  (instagram_business_content_publish 권한이 있는 토큰)
"""

import argparse
import json
import mimetypes
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

IG_API = "https://graph.instagram.com/v25.0"


def request(method, url, data=None, headers=None, form=None):
    """HTTP 요청 하나. JSON 응답은 dict로, 그 외에는 (status, headers, body)로 돌려준다."""
    headers = dict(headers or {})
    if form is not None:
        data = urllib.parse.urlencode(form).encode()
        headers.setdefault("Content-Type", "application/x-www-form-urlencoded")
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=600) as res:
            return res.status, res.headers, res.read()
    except urllib.error.HTTPError as e:
        sys.exit(f"{method} {url.split('?')[0]} 실패 ({e.code}): {e.read().decode(errors='replace')}")


def request_json(method, url, **kw):
    _, _, body = request(method, url, **kw)
    return json.loads(body or b"{}")


def env(name):
    value = os.environ.get(name)
    if not value:
        sys.exit(f"환경 변수 {name} 이(가) 없습니다. 저장소 Settings → Secrets and variables → Actions 에 추가하세요.")
    return value


# ---------- YouTube ----------

def youtube_token():
    res = request_json("POST", "https://oauth2.googleapis.com/token", form={
        "client_id": env("YT_CLIENT_ID"),
        "client_secret": env("YT_CLIENT_SECRET"),
        "refresh_token": env("YT_REFRESH_TOKEN"),
        "grant_type": "refresh_token",
    })
    return res["access_token"]


def youtube(args):
    token = youtube_token()
    auth = {"Authorization": f"Bearer {token}"}
    status = {"privacyStatus": args.privacy, "selfDeclaredMadeForKids": False}
    if args.publish_at:
        # 예약 공개는 private 상태에서만 받아 준다
        status.update(privacyStatus="private", publishAt=args.publish_at)
    meta = {
        "snippet": {
            "title": args.title,
            "description": args.description,
            "tags": [t.strip() for t in args.tags.split(",") if t.strip()],
            "categoryId": args.category,
            "defaultLanguage": "ko",
            "defaultAudioLanguage": "ko",
        },
        "status": status,
    }
    size = os.path.getsize(args.video)

    # 재개 가능 업로드: 먼저 메타데이터로 업로드 주소를 받고, 그 주소에 파일을 PUT 한다
    _, headers, _ = request(
        "POST",
        "https://www.googleapis.com/upload/youtube/v3/videos?uploadType=resumable&part=snippet,status",
        data=json.dumps(meta).encode(),
        headers={**auth, "Content-Type": "application/json; charset=UTF-8",
                 "X-Upload-Content-Type": "video/*", "X-Upload-Content-Length": str(size)},
    )
    with open(args.video, "rb") as f:
        _, _, body = request("PUT", headers["Location"], data=f.read(),
                             headers={**auth, "Content-Type": "video/*", "Content-Length": str(size)})
    video = json.loads(body)
    video_id = video["id"]
    print(f"유튜브 업로드 완료: https://youtu.be/{video_id} (상태: {video['status'].get('privacyStatus')}"
          f"{', 공개 예정 ' + args.publish_at if args.publish_at else ''})")
    if video["status"].get("privacyStatus") == "private" and args.privacy != "private" and not args.publish_at:
        print("주의: 공개로 요청했지만 비공개로 올라갔어요. 검수 전 API 프로젝트는 비공개로만 올라갑니다 (publish/README.md 참고).")

    if args.thumbnail:
        with open(args.thumbnail, "rb") as f:
            data = f.read()
        ctype = mimetypes.guess_type(args.thumbnail)[0] or "image/png"
        request("POST", f"https://www.googleapis.com/upload/youtube/v3/thumbnails/set?videoId={video_id}",
                data=data, headers={**auth, "Content-Type": ctype})
        print("썸네일 적용 완료")
    write_summary(f"유튜브: https://youtu.be/{video_id}")


# ---------- Instagram ----------

def instagram(args):
    token = env("IG_ACCESS_TOKEN")
    me = request_json("GET", f"{IG_API}/me?fields=user_id,username&access_token={token}")
    user_id = me.get("user_id") or me["id"]

    # Instagram 로그인 API는 파일 직접 업로드를 받지 않아서, 인스타가 공개 URL에서 영상을 가져가게 한다
    form = {"media_type": "REELS", "video_url": args.video_url, "caption": args.caption,
            "share_to_feed": "true" if args.share_to_feed else "false", "access_token": token}
    if args.cover_url:
        form["cover_url"] = args.cover_url
    container = request_json("POST", f"{IG_API}/{user_id}/media", form=form)

    # 인스타가 영상 처리를 끝낼 때까지 기다린다 (보통 30초~2분)
    for _ in range(60):
        status = request_json("GET", f"{IG_API}/{container['id']}?fields=status_code,status&access_token={token}")
        code = status.get("status_code")
        if code == "FINISHED":
            break
        if code in ("ERROR", "EXPIRED"):
            sys.exit(f"인스타 영상 처리 실패: {status}")
        time.sleep(10)
    else:
        sys.exit("인스타 영상 처리가 10분 안에 끝나지 않았어요.")

    published = request_json("POST", f"{IG_API}/{user_id}/media_publish",
                             form={"creation_id": container["id"], "access_token": token})
    link = request_json("GET", f"{IG_API}/{published['id']}?fields=permalink&access_token={token}").get("permalink", "")
    print(f"인스타 게시 완료 (@{me.get('username')}): {link}")
    write_summary(f"인스타: {link}")


def write_summary(line):
    path = os.environ.get("GITHUB_STEP_SUMMARY")
    if path:
        with open(path, "a") as f:
            f.write(line + "\n\n")


def main():
    p = argparse.ArgumentParser()
    sub = p.add_subparsers(dest="platform", required=True)

    yt = sub.add_parser("youtube")
    yt.add_argument("video")
    yt.add_argument("--title", required=True)
    yt.add_argument("--description", default="")
    yt.add_argument("--tags", default="")
    yt.add_argument("--privacy", default="public", choices=["public", "unlisted", "private"])
    yt.add_argument("--publish-at", default="")
    yt.add_argument("--thumbnail", default="")
    yt.add_argument("--category", default="27")  # 27 = 교육

    ig = sub.add_parser("instagram")
    ig.add_argument("video_url")
    ig.add_argument("--caption", default="")
    ig.add_argument("--cover-url", default="")
    ig.add_argument("--share-to-feed", action="store_true")

    args = p.parse_args()
    if args.platform == "youtube" and not os.path.isfile(args.video):
        sys.exit(f"영상 파일이 없습니다: {args.video}")
    {"youtube": youtube, "instagram": instagram}[args.platform](args)


if __name__ == "__main__":
    main()
