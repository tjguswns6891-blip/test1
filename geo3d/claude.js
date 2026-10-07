// 문제 사진 → Claude → 3D 장면 JSON + 풀이
// 정적 사이트(GitHub Pages)이므로 사용자가 입력한 API 키로 브라우저에서 직접 호출한다.
import Anthropic from "https://cdn.jsdelivr.net/npm/@anthropic-ai/sdk@0/+esm";

const MODEL = "claude-opus-5-5";

const vec3 = { type: "array", items: { type: "number" } };
const obj = (properties) => ({
  type: "object",
  additionalProperties: false,
  required: Object.keys(properties),
  properties,
});
const arr = (items) => ({ type: "array", items });

export const SCENE_SCHEMA = obj({
  title: { type: "string" },
  problem: { type: "string" },
  points: arr(obj({ name: { type: "string" }, coord: vec3, showLabel: { type: "boolean" } })),
  segments: arr(
    obj({
      id: { type: "string" },
      from: { type: "string" },
      to: { type: "string" },
      style: { type: "string", enum: ["solid", "dashed"] },
      color: { type: "string" },
    }),
  ),
  lines: arr(
    obj({
      id: { type: "string" },
      label: { type: "string" },
      point: vec3,
      direction: vec3,
      color: { type: "string" },
    }),
  ),
  polygons: arr(
    obj({
      id: { type: "string" },
      vertices: arr({ type: "string" }),
      color: { type: "string" },
      opacity: { type: "number" },
    }),
  ),
  planes: arr(
    obj({
      id: { type: "string" },
      label: { type: "string" },
      point: vec3,
      normal: vec3,
      size: { type: "number" },
      color: { type: "string" },
    }),
  ),
  spheres: arr(
    obj({
      id: { type: "string" },
      label: { type: "string" },
      center: vec3,
      radius: { type: "number" },
      color: { type: "string" },
    }),
  ),
  circles: arr(
    obj({
      id: { type: "string" },
      label: { type: "string" },
      center: vec3,
      normal: vec3,
      radius: { type: "number" },
      color: { type: "string" },
      style: { type: "string", enum: ["solid", "dashed"] },
    }),
  ),
  projections: arr(
    obj({
      id: { type: "string" },
      label: { type: "string" },
      sourceId: { type: "string" },
      planeId: { type: "string" },
      color: { type: "string" },
    }),
  ),
  steps: arr(
    obj({
      title: { type: "string" },
      explanation: { type: "string" },
      highlight: arr({ type: "string" }),
      view: { type: "string" },
    }),
  ),
  answer: { type: "string" },
});

const SYSTEM = `당신은 한국 수능 수학 '기하' 과목(공간도형, 공간좌표, 정사영, 이면각, 구, 벡터) 전문 강사입니다.
학생이 문제 사진을 올리면 (1) 문제를 정확히 옮겨 적고, (2) 완전히 풀고, (3) 풀이에 맞는 3D 장면을 좌표로 구성합니다.

장면 구성 규칙
- 오른손 좌표계, z축이 위쪽. 문제에 기준 평면(α 등)이 있으면 그 평면을 z=0으로 둔다.
- 반드시 문제를 먼저 끝까지 풀고, 풀어서 확정된 실제 값으로 좌표를 정한다. 모든 조건(길이, 거리, 각, 접함, 넓이)이 좌표에서 그대로 성립해야 한다. 무리수는 소수(최소 4자리)로 쓴다.
- 문제에 좌표가 없으면 계산이 쉬워지도록 좌표를 직접 설정하고, 그 설정을 풀이 단계에 적는다.
- 전체 장면 크기가 대략 원점 근처 2~20 범위가 되게 한다.
- 점 이름은 문제 표기(P, Q, R, O, H …)를 그대로 쓰고, 풀이에 필요한 보조점(수선의 발, 중심 등)도 추가한다.
- planes.size는 평면을 그릴 정사각형 한 변 길이. 관련 도형을 덮을 만큼 크게.
- segments의 from/to, polygons의 vertices는 points의 name을 참조한다.
- projections는 원·선분·다각형(sourceId)을 평면(planeId) 위로 정사영한 모양을 그릴 때 쓴다. 정사영 문제라면 반드시 넣는다.
- 보조선은 style "dashed", 핵심 도형은 "solid". 색은 #rrggbb.
- 모든 id와 점 이름은 서로 겹치지 않게 한다.

풀이 단계(steps) 규칙
- 학생이 따라올 수 있게 4~8단계로 나눈다. 각 단계는 핵심 아이디어 하나.
- explanation은 한국어 마크다운, 수식은 $...$ 또는 $$...$$ (KaTeX)로 쓴다. 문자열 안의 백슬래시는 JSON 규칙대로 이스케이프한다.
- highlight에는 그 단계에서 강조할 점 이름이나 도형 id를 넣는다.
- view는 그 단계를 가장 잘 보여주는 시점: "iso"(기본 사선), "top"(위에서), "front"(-y쪽에서 +y 방향), "side"(+x쪽에서), 또는 "normal:<평면id>"(그 평면에 수직으로 내려다보기 — 정사영·이면각 설명에 유용).
- answer에는 최종 답만 적는다(예: "28").
- 문제 이미지가 흐리거나 조건이 애매하면, 가장 자연스러운 해석을 택하고 첫 단계에 그 해석을 밝힌다.`;

export function getStoredKey() {
  try {
    return localStorage.getItem("geo3d.apiKey") || "";
  } catch {
    return "";
  }
}

export function storeKey(key) {
  try {
    if (key) localStorage.setItem("geo3d.apiKey", key);
    else localStorage.removeItem("geo3d.apiKey");
  } catch {}
}

/**
 * @param {{apiKey:string, imageBase64:string, mediaType:string, note?:string,
 *          onThinking?:(t:string)=>void, onText?:(n:number)=>void, signal?:AbortSignal}} opts
 */
export async function analyzeProblem({ apiKey, imageBase64, mediaType, note, onThinking, onText, signal }) {
  const client = new Anthropic({ apiKey, dangerouslyAllowBrowser: true });

  const stream = client.beta.messages.stream(
    {
      model: MODEL,
      max_tokens: 64000,
      betas: ["server-side-fallback-2026-07-01"],
      fallbacks: "default",
      thinking: { type: "adaptive", display: "summarized" },
      output_config: {
        effort: "high",
        format: { type: "json_schema", schema: SCENE_SCHEMA },
      },
      system: SYSTEM,
      messages: [
        {
          role: "user",
          content: [
            { type: "image", source: { type: "base64", media_type: mediaType, data: imageBase64 } },
            {
              type: "text",
              text:
                "이 기하 문제를 풀고 3D 장면을 구성해 주세요." +
                (note ? `\n\n추가 메모: ${note}` : ""),
            },
          ],
        },
      ],
    },
    { signal },
  );

  let textLen = 0;
  for await (const event of stream) {
    if (event.type === "content_block_delta") {
      if (event.delta.type === "thinking_delta") onThinking?.(event.delta.thinking);
      else if (event.delta.type === "text_delta") {
        textLen += event.delta.text.length;
        onText?.(textLen);
      }
    }
  }

  const message = await stream.finalMessage();
  if (message.stop_reason === "refusal") {
    throw new Error("요청이 거절되었습니다: " + (message.stop_details?.explanation || "사유 미상"));
  }
  if (message.stop_reason === "max_tokens") {
    throw new Error("응답이 너무 길어 중간에 잘렸습니다. 다시 시도해 주세요.");
  }
  const text = message.content
    .filter((b) => b.type === "text")
    .map((b) => b.text)
    .join("");
  try {
    return JSON.parse(text);
  } catch {
    throw new Error("응답을 해석하지 못했습니다(JSON 오류). 다시 시도해 주세요.");
  }
}
