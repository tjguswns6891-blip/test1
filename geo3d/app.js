import { GeoViewer } from "./scene.js";
import { DEMO_SCENE, DEMO_IMAGE } from "./demo.js";
import { analyzeProblem, getStoredKey, storeKey } from "./claude.js";

const $ = (s) => document.querySelector(s);
const viewer = new GeoViewer($("#viewport"));

const state = { data: null, step: -1, image: null };

// ---------- 텍스트 렌더링 (마크다운 일부 + KaTeX) ----------
const esc = (s) => s.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
function md(text) {
  return esc(text || "")
    .split(/\n{2,}/)
    .map((para) => "<p>" + para.replace(/\*\*(.+?)\*\*/g, "<strong>$1</strong>").replace(/\n/g, "<br>") + "</p>")
    .join("");
}
function typeset(el) {
  if (window.renderMathInElement) {
    window.renderMathInElement(el, {
      delimiters: [
        { left: "$$", right: "$$", display: true },
        { left: "$", right: "$", display: false },
      ],
      throwOnError: false,
    });
  }
}
function setRich(el, text) {
  el.innerHTML = md(text);
  typeset(el);
}

// ---------- 장면 불러오기 ----------
function loadScene(data) {
  data = normalize(data);
  state.data = data;
  viewer.load(data);
  $("#title").textContent = data.title || "기하 문제";
  setRich($("#problem"), data.problem);
  $("#answer").textContent = data.answer || "—";
  $("#answer-box").hidden = false;
  $("#answer").classList.add("blur");
  renderSteps();
  renderPlaneViews();
  renderLayers();
  $("#json").value = JSON.stringify(data, null, 2);
  selectStep(-1);
}

function normalize(d) {
  const keys = ["points", "segments", "lines", "polygons", "planes", "spheres", "circles", "projections", "steps"];
  for (const k of keys) if (!Array.isArray(d[k])) d[k] = [];
  return d;
}

function renderSteps() {
  const ol = $("#steps");
  ol.innerHTML = "";
  state.data.steps.forEach((s, i) => {
    const li = document.createElement("li");
    li.className = "step";
    li.innerHTML = `<button class="step-head" type="button"><span class="num">${i + 1}</span><span class="t"></span></button><div class="step-body"></div>`;
    li.querySelector(".t").textContent = s.title.replace(/^\d+\.\s*/, "");
    setRich(li.querySelector(".step-body"), s.explanation);
    li.querySelector(".step-head").addEventListener("click", () => selectStep(state.step === i ? -1 : i));
    ol.appendChild(li);
  });
  $("#step-count").textContent = state.data.steps.length ? `${state.data.steps.length}단계` : "";
}

function selectStep(i) {
  state.step = i;
  document.querySelectorAll(".step").forEach((el, k) => el.classList.toggle("open", k === i));
  $("#step-indicator").textContent = i < 0 ? "전체 보기" : `${i + 1} / ${state.data.steps.length}`;
  if (i < 0) {
    viewer.applyHighlight([]);
    return;
  }
  const s = state.data.steps[i];
  viewer.applyHighlight(s.highlight || []);
  if (s.view) viewer.setView(s.view);
  document.querySelectorAll(".step")[i]?.scrollIntoView({ block: "nearest", behavior: "smooth" });
}

function renderPlaneViews() {
  const box = $("#plane-views");
  box.innerHTML = "";
  for (const pl of state.data.planes) {
    const b = document.createElement("button");
    b.type = "button";
    b.className = "chip";
    b.textContent = `⊥ ${pl.label}`;
    b.title = `${pl.label}에 수직으로 보기 (정사영 모양 확인)`;
    b.addEventListener("click", () => viewer.setView("normal:" + pl.id));
    box.appendChild(b);
  }
}

function renderLayers() {
  const box = $("#layers");
  box.innerHTML = "";
  const groups = new Map();
  for (const [id, it] of viewer.items) {
    if (!groups.has(it.kind)) groups.set(it.kind, []);
    groups.get(it.kind).push([id, it]);
  }
  for (const [kind, list] of groups) {
    const g = document.createElement("div");
    g.className = "layer-group";
    g.innerHTML = `<div class="layer-kind">${esc(kind)}</div>`;
    for (const [id, it] of list) {
      const lab = document.createElement("label");
      lab.className = "layer";
      lab.innerHTML = `<input type="checkbox" checked><span></span>`;
      lab.querySelector("span").textContent = it.label;
      lab.querySelector("input").addEventListener("change", (e) => viewer.setVisible(id, e.target.checked));
      g.appendChild(lab);
    }
    box.appendChild(g);
  }
}

// ---------- 툴바 ----------
document.querySelectorAll("[data-view]").forEach((b) => b.addEventListener("click", () => viewer.setView(b.dataset.view)));
$("#prev").addEventListener("click", () => state.data && selectStep(Math.max(-1, state.step - 1)));
$("#next").addEventListener("click", () => state.data && selectStep(Math.min(state.data.steps.length - 1, state.step + 1)));
$("#t-ortho").addEventListener("change", (e) => viewer.setOrtho(e.target.checked));
$("#t-axes").addEventListener("change", (e) => viewer.setAxes(e.target.checked));
$("#t-labels").addEventListener("change", (e) => viewer.setLabels(e.target.checked));
$("#answer").addEventListener("click", (e) => e.target.classList.toggle("blur"));
document.addEventListener("keydown", (e) => {
  if (e.target.closest("input, textarea")) return;
  if (e.key === "ArrowRight") $("#next").click();
  if (e.key === "ArrowLeft") $("#prev").click();
});

// ---------- JSON 직접 편집 ----------
$("#apply-json").addEventListener("click", () => {
  try {
    loadScene(JSON.parse($("#json").value));
    toast("장면을 다시 그렸습니다.");
  } catch (err) {
    toast("JSON 오류: " + err.message, true);
  }
});

// ---------- 이미지 입력 ----------
const drop = $("#drop");
function setImage(file) {
  if (!file || !file.type.startsWith("image/")) return toast("이미지 파일을 올려 주세요.", true);
  const reader = new FileReader();
  reader.onload = async () => {
    const resized = await downscale(reader.result, 1800);
    state.image = resized;
    $("#preview").src = resized.dataUrl;
    drop.classList.add("has-image");
    $("#analyze").disabled = false;
  };
  reader.readAsDataURL(file);
}
// 너무 큰 사진은 줄여서 보낸다 (긴 변 maxSide px, JPEG)
function downscale(dataUrl, maxSide) {
  return new Promise((resolve) => {
    const img = new Image();
    img.onload = () => {
      const k = Math.min(1, maxSide / Math.max(img.width, img.height));
      const c = document.createElement("canvas");
      c.width = Math.round(img.width * k);
      c.height = Math.round(img.height * k);
      c.getContext("2d").drawImage(img, 0, 0, c.width, c.height);
      const out = c.toDataURL("image/jpeg", 0.9);
      resolve({ dataUrl: out, base64: out.split(",")[1], mediaType: "image/jpeg" });
    };
    img.src = dataUrl;
  });
}
$("#file").addEventListener("change", (e) => setImage(e.target.files[0]));
drop.addEventListener("dragover", (e) => {
  e.preventDefault();
  drop.classList.add("over");
});
drop.addEventListener("dragleave", () => drop.classList.remove("over"));
drop.addEventListener("drop", (e) => {
  e.preventDefault();
  drop.classList.remove("over");
  setImage(e.dataTransfer.files[0]);
});
window.addEventListener("paste", (e) => {
  const item = [...(e.clipboardData?.items || [])].find((i) => i.type.startsWith("image/"));
  if (item) setImage(item.getAsFile());
});

// ---------- API 키 ----------
$("#key").value = getStoredKey();
$("#key").addEventListener("change", (e) => storeKey(e.target.value.trim()));

// ---------- 분석 ----------
let controller = null;
$("#analyze").addEventListener("click", async () => {
  if (controller) {
    controller.abort();
    return;
  }
  const apiKey = $("#key").value.trim();
  if (!apiKey) {
    $("#settings").open = true;
    $("#key").focus();
    return toast("Anthropic API 키를 먼저 입력해 주세요.", true);
  }
  if (!state.image) return toast("문제 사진을 먼저 올려 주세요.", true);
  storeKey(apiKey);

  controller = new AbortController();
  const btn = $("#analyze");
  btn.textContent = "중지";
  btn.classList.add("busy");
  const log = $("#thinking");
  log.hidden = false;
  log.textContent = "";
  $("#status").textContent = "문제를 읽고 푸는 중…";
  try {
    const data = await analyzeProblem({
      apiKey,
      imageBase64: state.image.base64,
      mediaType: state.image.mediaType,
      note: $("#note").value.trim(),
      signal: controller.signal,
      onThinking: (t) => {
        log.textContent += t;
        log.scrollTop = log.scrollHeight;
      },
      onText: (n) => ($("#status").textContent = `3D 장면 구성 중… (${n.toLocaleString()}자)`),
    });
    loadScene(data);
    $("#status").textContent = "완료! 화면을 드래그해서 돌려 보세요.";
    log.hidden = true;
  } catch (err) {
    const aborted = err?.name === "AbortError" || controller.signal.aborted;
    $("#status").textContent = aborted ? "중지했습니다." : "";
    if (!aborted) toast(friendlyError(err), true);
  } finally {
    controller = null;
    btn.textContent = "3D로 풀기";
    btn.classList.remove("busy");
  }
});

function friendlyError(err) {
  const s = err?.status;
  if (s === 401) return "API 키가 올바르지 않습니다.";
  if (s === 429) return "요청이 너무 많습니다. 잠시 후 다시 시도해 주세요.";
  if (s >= 500) return "Claude 서버 오류입니다. 잠시 후 다시 시도해 주세요.";
  return err?.message || String(err);
}

let toastTimer;
function toast(msg, isErr = false) {
  const t = $("#toast");
  t.textContent = msg;
  t.className = "toast show" + (isErr ? " err" : "");
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => (t.className = "toast"), 4200);
}

// ---------- 예시 ----------
async function loadDemo() {
  loadScene(structuredClone(DEMO_SCENE));
  try {
    const blob = await (await fetch(DEMO_IMAGE)).blob();
    setImage(new File([blob], DEMO_IMAGE, { type: blob.type || "image/jpeg" }));
  } catch {}
}
$("#load-demo").addEventListener("click", loadDemo);
loadDemo();
