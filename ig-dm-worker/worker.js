// Instagram 댓글 키워드 → 자동 DM (Cloudflare Worker, 단일 파일)
//
// 흐름: 누군가 게시물에 키워드가 담긴 댓글을 남기면 Meta가 이 Worker로 webhook을 보내고,
// Worker는 댓글 단 사람에게 Private Reply(DM)를 1통 보낸 뒤 댓글에 짧은 답글을 남긴다.
//
// 필요한 설정 (Cloudflare 대시보드 → Worker → 설정 → 변수 및 비밀):
//   IG_ACCESS_TOKEN  (비밀)  instagram_business_manage_comments, instagram_business_manage_messages 권한이 있는 토큰
//   IG_APP_SECRET    (비밀)  Meta 앱의 "Instagram 앱 시크릿" — webhook 서명 검증용
//   VERIFY_TOKEN     (비밀)  아무 문자열. Meta webhook 설정 화면의 "토큰 확인"에 같은 값을 넣는다
//   DM_SENT          (KV 바인딩, 선택)  같은 댓글에 두 번 보내지 않도록 처리한 댓글 ID를 기록

const API = "https://graph.instagram.com/v25.0";
const SITE = "https://tjguswns6891-blip.github.io/test1";

// 댓글에 이 단어 중 하나가 들어 있으면 DM을 보낸다 (띄어쓰기·대소문자 무시)
const KEYWORDS = ["링크", "사이트", "link"];

// 게시물(media id)별로 보낼 사이트. 여기에 없는 게시물은 DEFAULT_LINK를 쓴다.
const LINALG = { name: "선형대수 실험실", url: `${SITE}/linalg/` };
const CIRCUIT = { name: "보이는 회로이론", url: `${SITE}/circuit/` };
const THEMES = { name: "테마 강도", url: `${SITE}/themes/` };
const INVEST = { name: "금리와 주가 50년", url: `${SITE}/invest/` };
const DEFAULT_LINK = { name: "마르코프 사이트", url: `${SITE}/` };

const POST_LINKS = {
  // 회로이론 릴스
  "17887098912486670": CIRCUIT, // RLC 진동
  "18135670315637716": CIRCUIT, // KVL·KCL
  "17863370658692804": CIRCUIT, // 페이저
  // 선형대수 릴스
  "17960678120999017": LINALG, // 고유벡터·SVD
  "18478440244116656": LINALG, // 가우스 소거
  "18392543266204487": LINALG, // 가우스 소거 (중복 게시물)
  "18093099611692288": LINALG, // 행렬식
  // 증시 릴스
  "18134260132672784": THEMES, // 미국 테마 27개
  "18355489840168762": THEMES, // 돈 몰리는 테마 vs 빠지는 테마
  "18009597893986339": INVEST, // 경고등 3개
  "17932029132404726": INVEST, // 주식 불안하면 채권?
};

const dmText = (link) =>
  `안녕하세요! 요청하신 ${link.name} 링크예요 👇\n${link.url}\n\n도움이 됐다면 팔로우하고 다음 콘텐츠도 받아보세요 🙌`;

// 댓글에 남길 공개 답글. 매번 같은 문장이면 스팸으로 보일 수 있어 돌아가며 쓴다.
const PUBLIC_REPLIES = ["DM으로 보내드렸어요! 📩", "DM 확인해 주세요 🙌", "링크 DM으로 보냈어요 👀"];

export default {
  async fetch(request, env, ctx) {
    const url = new URL(request.url);

    // Meta가 webhook 주소를 등록할 때 한 번 보내는 확인 요청
    if (request.method === "GET") {
      if (
        url.searchParams.get("hub.mode") === "subscribe" &&
        url.searchParams.get("hub.verify_token") === env.VERIFY_TOKEN
      ) {
        return new Response(url.searchParams.get("hub.challenge"));
      }
      return new Response("ok");
    }
    if (request.method !== "POST") return new Response("method not allowed", { status: 405 });

    const body = await request.text();
    if (!(await validSignature(body, request.headers.get("x-hub-signature-256"), env.IG_APP_SECRET))) {
      return new Response("bad signature", { status: 401 });
    }

    // Meta는 빨리 200을 받지 못하면 재시도하므로, 응답은 바로 하고 DM은 뒤에서 보낸다
    ctx.waitUntil(handle(JSON.parse(body), env));
    return new Response("EVENT_RECEIVED");
  },
};

async function handle(payload, env) {
  for (const entry of payload.entry || []) {
    for (const change of entry.changes || []) {
      if (change.field !== "comments") continue;
      const c = change.value || {};
      // 내 계정이 단 댓글(자동 답글 포함)은 무시해야 무한 반복이 생기지 않는다
      if (!c.id || !c.text || c.from?.id === entry.id) continue;
      if (!matches(c.text)) continue;
      try {
        await processComment(c, env);
      } catch (e) {
        console.log(`comment ${c.id} failed: ${e.message}`);
      }
    }
  }
}

async function processComment(c, env) {
  if (env.DM_SENT && (await env.DM_SENT.get(c.id))) return; // Meta 재전송으로 같은 댓글이 또 온 경우

  const link = POST_LINKS[c.media?.id] || DEFAULT_LINK;
  await igPost(env, "/me/messages", {
    recipient: { comment_id: c.id },
    message: { text: dmText(link) },
  });
  // Private Reply는 7일 동안만 가능하니 기록도 그만큼만 남긴다
  if (env.DM_SENT) await env.DM_SENT.put(c.id, "1", { expirationTtl: 8 * 86400 });
  console.log(`DM sent for comment ${c.id} (@${c.from?.username})`);

  const reply = PUBLIC_REPLIES[Math.floor(Math.random() * PUBLIC_REPLIES.length)];
  try {
    await igPost(env, `/${c.id}/replies`, { message: reply });
  } catch (e) {
    console.log(`public reply failed for ${c.id}: ${e.message}`); // DM은 이미 갔으니 실패해도 넘어간다
  }
}

function matches(text) {
  const t = text.replace(/\s+/g, "").toLowerCase();
  return KEYWORDS.some((k) => t.includes(k.toLowerCase()));
}

async function igPost(env, path, json) {
  const res = await fetch(API + path, {
    method: "POST",
    headers: { "content-type": "application/json", authorization: `Bearer ${env.IG_ACCESS_TOKEN}` },
    body: JSON.stringify(json),
  });
  if (!res.ok) throw new Error(`${res.status} ${await res.text()}`);
  return res.json();
}

async function validSignature(body, header, secret) {
  if (!header || !secret || !header.startsWith("sha256=")) return false;
  const key = await crypto.subtle.importKey(
    "raw",
    new TextEncoder().encode(secret),
    { name: "HMAC", hash: "SHA-256" },
    false,
    ["sign"],
  );
  const mac = await crypto.subtle.sign("HMAC", key, new TextEncoder().encode(body));
  const hex = [...new Uint8Array(mac)].map((b) => b.toString(16).padStart(2, "0")).join("");
  const expected = header.slice(7);
  if (hex.length !== expected.length) return false;
  let diff = 0;
  for (let i = 0; i < hex.length; i++) diff |= hex.charCodeAt(i) ^ expected.charCodeAt(i);
  return diff === 0;
}
