---
name: agency-ko-guide
description: 방금 깔린 클로드 코드 에이전트 묶음(itallstartedwithaidea/agency-agents · 68개 · 부서 9개)을 사용자의 언어로 안내한다(사용자가 한국어로 물으면 한국어로). 사용자가 "에이전트 뭐 깔렸어", "어떤 에이전트 있어", "프론트엔드 에이전트 불러줘", "agency", "에이전트 목록", "부서별로 보여줘" 라고 하거나, 무슨 일을 시킬지 고르지 못할 때 쓴다. 에이전트를 어떻게 부르는지, 어느 부서에 무엇이 있는지, 스킬과 무엇이 다른지 알려 준다.
---

# 클로드 코드 에이전트 68개 — 사용자 언어로 안내

`npx reborn-agency` 로 깔린 것들을 안내한다. 이 파일에 적힌 것만 말한다.

## 0. 먼저 밝힐 것

- 저장소는 **`itallstartedwithaidea/agency-agents`** 이고 **MIT** 라이선스다.
- **남이 만든 오픈소스다.** 리본랩스는 그 저장소와 **제휴 관계가 없다.**
  우리가 만든 것은 설치기(`reborn-agency`)와 이 안내(사용자 언어로 답한다) 하나뿐이다.
- 받는 데 돈이 들지 않는다. 다만 **클로드 코드 구독은 따로다.**

## 1. 무엇이 깔렸나 — 에이전트 68개 · 부서 9개

2026-09-19 저장소 전수 실측이다. `strategy/` 16개(플레이북·런북)는 에이전트가 아니라 안 깔았다.

| 부서 | 개수 | 보기 |
|---|---|---|
| engineering | 11 | frontend-developer · backend-architect · ai-engineer · devops-automator · security-engineer |
| marketing | 11 | content-creator · growth-hacker · instagram-curator · tiktok-strategist |
| specialized | 9 | agents-orchestrator · data-analytics-reporter · developer-advocate |
| design | 8 | ui-designer · ux-architect · brand-guardian · visual-storyteller |
| testing | 8 | api-tester · performance-benchmarker · accessibility-auditor · reality-checker |
| support | 6 | analytics-reporter · finance-tracker · legal-compliance-checker · support-responder |
| spatial-computing | 6 | visionos-spatial-engineer · xr-interface-architect |
| project-management | 5 | project-shepherd · studio-producer · experiment-tracker |
| product | 4 | feedback-synthesizer · sprint-prioritizer · trend-researcher |

자리는 `~/.claude/agents/` (또는 `--local` 로 깔았으면 `./.claude/agents/`).
정확한 목록은 그 폴더를 직접 세서 답한다 — **기억으로 말하지 않는다.**

## 2. 어떻게 부르나

이름을 그대로 부른다. 별도 명령이 없다.

```
Frontend Developer 로 이 컴포넌트 고쳐줘
Reality Checker 로 이 기능이 진짜 배포해도 되는지 봐줘
Legal Compliance Checker 로 이 문구가 걸리는 데 없는지 봐줘
```

각 `.md` 파일 안에는 그 에이전트의 성격·작업 순서·내놓는 결과물·성공 기준이 적혀 있다.
어느 에이전트를 쓸지 모르겠다고 하면 **하려는 일을 먼저 묻고** 부서 하나를 고른다.

## 3. 에이전트와 스킬은 다른 칸이다

| | 에이전트 | 스킬 |
|---|---|---|
| 무엇 | **누가** 맡나 — 역할·말투·판단 기준 | **어떻게** 하나 — 절차·도구 |
| 자리 | `~/.claude/agents/` | `~/.claude/skills/` |
| 부르기 | 이름을 부른다 | 상황이 맞으면 알아서 뜬다 |

둘은 겹치지 않는다. 같이 쓸 때 제일 잘 돈다.

## 4. 이 안내가 말하지 않는 것

- **「280개」** — 이 저장소에 그런 수는 없다. 전수 실측은 68개다.
- **「변호사가 있다」** — 법무 쪽은 `support-legal-compliance-checker` **하나**다.
- **「세일즈 부서가 있다」** — sales 전용 부서는 없다. `sales-data-extraction-agent` 하나가
  판매 자료를 뽑는 에이전트다.
- **효과·성과** — 이 에이전트들이 무엇을 얼마나 개선하는지 우리는 잰 적이 없다.

## 5. 다시 깔거나 골라 깔기

```
npx --yes reborn-agency --check                 깔지 않고 이 컴퓨터를 잰다
npx --yes reborn-agency --only design,testing   부서를 골라서
npx --yes reborn-agency --local                 현재 폴더에
```

같은 이름이 이미 있으면 **덮어쓰지 않고 건너뛴다.** 원본을 고쳐 쓰고 있어도 안전하다.
다른 도구(Cursor · Aider · Windsurf · Gemini CLI · OpenCode)를 쓴다면 저장소의
`scripts/convert.sh` 가 그 형식으로 바꿔 준다 — 우리 설치기는 클로드 코드만 다룬다.
