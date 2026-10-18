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


def youtube_update(args):
    """이미 올린 영상의 제목·설명·태그를 고친다. 비운 항목은 그대로 둔다."""
    auth = {"Authorization": f"Bearer {youtube_token()}"}
    items = request_json("GET", f"https://www.googleapis.com/youtube/v3/videos?part=snippet&id={args.video_id}",
                         headers=auth).get("items")
    if not items:
        sys.exit(f"영상을 찾을 수 없습니다: {args.video_id}")
    snippet = items[0]["snippet"]
    if args.title:
        snippet["title"] = args.title
    if args.description:
        snippet["description"] = args.description
    if args.tags:
        snippet["tags"] = [t.strip() for t in args.tags.split(",") if t.strip()]
    request("PUT", "https://www.googleapis.com/youtube/v3/videos?part=snippet",
            data=json.dumps({"id": args.video_id, "snippet": snippet}).encode(),
            headers={**auth, "Content-Type": "application/json; charset=UTF-8"})
    print(f"유튜브 수정 완료: https://youtu.be/{args.video_id} ({snippet['title']})")
    write_summary(f"유튜브 수정: https://youtu.be/{args.video_id}")


def youtube_list(args):
    """내 채널의 모든 영상(ID·길이·조회수·제목)과 재생목록, 채널 소개를 보여 준다."""
    auth = {"Authorization": f"Bearer {youtube_token()}"}
    api = "https://www.googleapis.com/youtube/v3"
    ch = request_json("GET", f"{api}/channels?part=snippet,contentDetails,statistics,brandingSettings&mine=true",
                      headers=auth)["items"][0]
    print(f"채널: {ch['snippet']['title']} ({ch['id']}) 구독자 {ch['statistics'].get('subscriberCount')}")
    print(f"소개: {ch['snippet'].get('description', '')!r}")
    print(f"키워드: {ch.get('brandingSettings', {}).get('channel', {}).get('keywords', '')!r}")

    uploads = ch["contentDetails"]["relatedPlaylists"]["uploads"]
    ids, page = [], ""
    while True:
        res = request_json("GET", f"{api}/playlistItems?part=contentDetails&maxResults=50&playlistId={uploads}"
                                  f"&pageToken={page}", headers=auth)
        ids += [i["contentDetails"]["videoId"] for i in res.get("items", [])]
        page = res.get("nextPageToken")
        if not page:
            break
    print(f"\n영상 {len(ids)}개 (ID | 공개 | 길이 | 조회수 | 올린 날 | 제목)")
    for i in range(0, len(ids), 50):
        res = request_json("GET", f"{api}/videos?part=snippet,contentDetails,statistics,status"
                                  f"&id={','.join(ids[i:i + 50])}", headers=auth)
        for v in res.get("items", []):
            print(f"{v['id']} | {v['status']['privacyStatus']} | {v['contentDetails']['duration']} | "
                  f"{v['statistics'].get('viewCount')} | {v['snippet']['publishedAt'][:10]} | {v['snippet']['title']}")

    res = request_json("GET", f"{api}/playlists?part=snippet,contentDetails&mine=true&maxResults=50", headers=auth)
    print("\n재생목록:")
    for p in res.get("items", []):
        print(f"{p['id']} | {p['contentDetails']['itemCount']}개 | {p['snippet']['title']}")


def youtube_playlist(args):
    """제목이 같은 재생목록을 찾거나 새로 만들고, 영상 ID들을 순서대로 넣는다 (이미 있는 영상은 건너뜀)."""
    auth = {"Authorization": f"Bearer {youtube_token()}"}
    api = "https://www.googleapis.com/youtube/v3"
    json_headers = {**auth, "Content-Type": "application/json; charset=UTF-8"}
    found = [p for p in request_json("GET", f"{api}/playlists?part=snippet&mine=true&maxResults=50",
                                     headers=auth).get("items", [])
             if p["snippet"]["title"] == args.title]
    if found:
        playlist_id = found[0]["id"]
    else:
        body = {"snippet": {"title": args.title, "description": args.description, "defaultLanguage": "ko"},
                "status": {"privacyStatus": "public"}}
        playlist_id = request_json("POST", f"{api}/playlists?part=snippet,status",
                                   data=json.dumps(body).encode(), headers=json_headers)["id"]
        print(f"재생목록 만듦: {args.title}")
    existing = {i["contentDetails"]["videoId"] for i in request_json(
        "GET", f"{api}/playlistItems?part=contentDetails&maxResults=50&playlistId={playlist_id}",
        headers=auth).get("items", [])}
    for vid in [v.strip() for v in args.video_ids.split(",") if v.strip()]:
        if vid in existing:
            continue
        body = {"snippet": {"playlistId": playlist_id, "resourceId": {"kind": "youtube#video", "videoId": vid}}}
        request("POST", f"{api}/playlistItems?part=snippet", data=json.dumps(body).encode(), headers=json_headers)
        print(f"  + {vid}")
    print(f"재생목록: https://www.youtube.com/playlist?list={playlist_id}")
    write_summary(f"재생목록 {args.title}: https://www.youtube.com/playlist?list={playlist_id}")


def youtube_channel(args):
    """채널 소개와 키워드를 바꾼다. 비운 항목은 그대로 둔다 (채널 이름은 API로 못 바꿈)."""
    auth = {"Authorization": f"Bearer {youtube_token()}"}
    api = "https://www.googleapis.com/youtube/v3"
    ch = request_json("GET", f"{api}/channels?part=brandingSettings&mine=true", headers=auth)["items"][0]
    channel = ch["brandingSettings"].setdefault("channel", {})
    if args.description:
        channel["description"] = args.description
    if args.keywords:
        channel["keywords"] = args.keywords
    request("PUT", f"{api}/channels?part=brandingSettings",
            data=json.dumps({"id": ch["id"], "brandingSettings": ch["brandingSettings"]}).encode(),
            headers={**auth, "Content-Type": "application/json; charset=UTF-8"})
    print("채널 소개·키워드 수정 완료")
    write_summary("채널 소개·키워드 수정 완료")


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


def instagram_comments(args):
    """최근 게시물의 댓글과 답글을 보여 준다 (DM 자동 답장이 동작하는지 확인용)."""
    token = env("IG_ACCESS_TOKEN")
    q = urllib.parse.urlencode({"fields": "id,caption,timestamp,comments_count,comments{text,username,timestamp,replies{text,username}}",
                                "limit": args.limit, "access_token": token})
    for m in request_json("GET", f"{IG_API}/me/media?{q}").get("data", []):
        print(f"\n[{m['id']}] {m.get('timestamp', '')[:16]} 댓글 {m.get('comments_count', 0)}개 | {(m.get('caption') or '')[:30]!r}")
        for c in m.get("comments", {}).get("data", []):
            print(f"  - @{c.get('username')}: {c.get('text')!r} ({c.get('timestamp', '')[:16]})")
            for r in c.get("replies", {}).get("data", []):
                print(f"      ↳ @{r.get('username')}: {r.get('text')!r}")
    perms = request_json("GET", f"{IG_API}/me?fields=username&access_token={token}")
    print(f"\n계정: @{perms.get('username')}")


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

    up = sub.add_parser("youtube-update")
    up.add_argument("video_id")
    up.add_argument("--title", default="")
    up.add_argument("--description", default="")
    up.add_argument("--tags", default="")

    sub.add_parser("youtube-list")

    pl = sub.add_parser("youtube-playlist")
    pl.add_argument("--title", required=True)
    pl.add_argument("--description", default="")
    pl.add_argument("--video-ids", default="")

    yc = sub.add_parser("youtube-channel")
    yc.add_argument("--description", default="")
    yc.add_argument("--keywords", default="")

    ic = sub.add_parser("instagram-comments")
    ic.add_argument("--limit", default="25")

    ig = sub.add_parser("instagram")
    ig.add_argument("video_url")
    ig.add_argument("--caption", default="")
    ig.add_argument("--cover-url", default="")
    ig.add_argument("--share-to-feed", action="store_true")

    args = p.parse_args()
    if args.platform == "youtube" and not os.path.isfile(args.video):
        sys.exit(f"영상 파일이 없습니다: {args.video}")
    {"youtube": youtube, "youtube-update": youtube_update, "youtube-list": youtube_list,
     "youtube-playlist": youtube_playlist, "youtube-channel": youtube_channel,
     "instagram": instagram, "instagram-comments": instagram_comments}[args.platform](args)


if __name__ == "__main__":
    main()
