> **Source**: 본 문서는 `/superpowers:brainstorming` 세션 결과물. spec 검증(`/zzizily:verify` 2-Way: Codex+Antigravity) 2회 수행 — 1차 Blocker 5건으로 접근법 A → 수동 v1 전환, 2차 신규 Blocker 2건(보안 정밀도) 반영. 상세는 §12 검증 이력.

## 목차

- [1. 배경 및 문제](#1-배경-및-문제)
- [2. 목표 및 비목표](#2-목표-및-비목표)
- [3. 핵심 결정 및 근거](#3-핵심-결정-및-근거)
- [4. 컴포넌트 구성](#4-컴포넌트-구성)
- [5. 파일 레이아웃](#5-파일-레이아웃)
- [6. handoff 데이터 구조](#6-handoff-데이터-구조)
- [7. 데이터 흐름](#7-데이터-흐름)
- [8. 엣지 케이스 및 에러 처리](#8-엣지-케이스-및-에러-처리)
- [9. 보안 고려사항](#9-보안-고려사항)
- [10. 검증 계획 (dogfood)](#10-검증-계획-dogfood)
- [11. v2 로드맵 (자동 저장)](#11-v2-로드맵-자동-저장)
- [12. 검증 이력 및 근거](#12-검증-이력-및-근거)

---

# zzizily context-handoff — Design Spec

**날짜**: 2026-07-16
**상태**: Draft v3 (수동 중심, 2차 검증 반영)
**접근법**: 수동 중심 v1 — `/zzizily:handoff` + `/zzizily:resume` 2 컴포넌트

## 1. 배경 및 문제

TUI(Claude Code) 작업 중 context window가 소진되면 현재 진행 작업이 단절된다. 사용자는 "context가 다 차면 현재 작업을 MEMORY에 업로드하고, new session에서 이어서 작업"하기를 원한다.

### 기존 시스템과의 관계

| 시스템 | 트리거 | 저장 위치 | 한계 |
| :--- | :--- | :--- | :--- |
| `/remember` (remember plugin) | 수동 명령 | `~/.remember/` 또는 `<repo>/.remember/` | 저장은 있으나 능동 복원(TODO 재구성)이 약함 |
| OMC (`.omc/`) | 여러 skill | `.omc/notepad`, `project-memory`, `sessions`, `handoffs/` | multi-agent 상태 관리 치중, `handoffs/` 미사용 |

**식별된 gap**: "저장(쓰기) + 능동 복원(읽기/재개)의 양방향 쌍"이 zzizily 생태계에 없다.

## 2. 목표 및 비목표

### 목표

1. `/zzizily:handoff` 수동 저장 — 사용자가 `/clear` 전 제어 시점에 현재 작업을 구조화 저장
2. `/zzizily:resume` 능동 복원 — new session에서 handoff를 읽어 **사용자 승인 후 TaskCreate로 task 재구성** + 진행상태 + 다음 액션 복원
3. zzizily plugin 독립 동작 (remember/OMC 의존 없음)

### 비목표 (YAGNI)

- **자동 저장(PreCompact/PostCompact hook)** — 검증 결과 prompt hook은 파일 쓰기 불가, command hook은 LLM 요약 불가. v1은 수동 중심, 자동은 v2 로드맵(§11)
- session transcript 무손실 백업
- SessionStart 자동 context 주입 (모든 세션 노이즈, remember 중복)
- git diff fingerprint 기반 stale 정밀 탐지, latest.md cache 무결성 검증 (KISS 초과 — §12 R4/R5)
- 타 기기 동기화

## 3. 핵심 결정 및 근거

### 3.1 수동 중심 v1 (자동 저장 제거)

**결정**: PreCompact/PostCompact hook 없이 `/handoff` + `/resume` 2 컴포넌트만.

**근거 (2-Way 검증 — §12)**: 원 설계 "PreCompact `type:"prompt"` hook → LLM in-memory 요약 → 파일 저장"은 Claude Code hook runtime model과 양립 불가. prompt hook은 single-turn yes/no evaluator로 **tool/file access가 없다** (3소스 일치 확정). 따라서 자동 저장은 command hook 기반 별도 LLM 세션(`claude -p`) 호출이 필요한데 비용·timeout·recursion 위험이 크다. v1은 수동으로 신뢰성 확보.

### 3.2 복원 방식: 수동 `/zzizily:resume` (승인 후 TaskCreate)

new session에서 사용자 명시적 호출. **파싱된 task preview를 사용자에게 먼저 보여주고 승인 후 TaskCreate**로 승격 — untrusted handoff의 embedded instruction이 자동으로 task가 되는 injection 경로 차단 (검증 2차 신B2).

### 3.3 저장 위치: 프로젝트 로컬 `.zzizily/handoff/`

`<repo>/.zzizily/handoff/`. `.zzizily/.gitignore`를 **자동 생성**해 기본 추적 제외(§9).

### 3.4 task 관리: TaskCreate 계약

resume의 TODO 재구성은 `TaskCreate`/`TaskUpdate`/`TaskList` 사용. `TodoWrite`는 최근 Claude Code에서 기본 disabled이므로 비의존 (검증 B4).

### 3.5 secret: best-effort + gitleaks 연동

secret 저장 금지는 SKILL.md 지침 + 저장 전 gitleaks detect(설치 시) fail-closed로 운영. **gitleaks 미설치 환경에서는 deterministic 보장 불가** → LLM 지침 best-effort + 한계 명시 (검증 2차 신B1).

## 4. 컴포넌트 구성

| 컴포넌트 | 역할 | 위치 |
| :--- | :--- | :--- |
| `/zzizily:handoff` | 수동 저장. LLM이 현재 context에서 §6 규격 handoff 작성 후 안전한 순서로 저장 | `skills/handoff/SKILL.md` |
| `/zzizily:resume` | 저장된 handoff 읽어 task preview → 사용자 승인 → TaskCreate 재구성 + 다음 액션 | `skills/resume/SKILL.md` |

hook 컴포넌트 없음. skill 2개 분리(zzizily `skills/<name>` → `/zzizily:<name>` 매핑, 저장/복원 명시 구분).

## 5. 파일 레이아웃

```text
skills/
├── handoff/SKILL.md            # 신규 — /zzizily:handoff (수동 저장)
└── resume/SKILL.md             # 신규 — /zzizily:resume (복원)

<repo>/.zzizily/                # 런타임 (gitignore 자동 생성)
├── .gitignore                  # * (전체 무시) — handoff 첫 write 전 자동 생성
└── handoff/
    ├── .tmp-<short8>           # 임시 파일 (scan 후 rename)
    ├── handoff-<UTC-ts>-<short8>.md   # 시간순 적재 (Windows-safe, 충돌 방지 suffix)
    └── latest.md               # 최신 복사본 (같은 filesystem atomic rename)
```

## 6. handoff 데이터 구조

remember(20줄)보다 task 복원 필드를 추가, 간결 유지.

```markdown
---
schema_version: 1
session_id: <uuid>
project: <repo name>
saved_at: <ISO 8601>
git_branch: <branch>
git_head: <short SHA>
git_dirty: <bool>
trigger: manual(handoff)
---

# Handoff — <project>

## 작업 목표
<이 세션 최상위 목표 1-2줄>

## 완료
<done — 커밋 SHA / 파일 / 결정>

## 진행 중
<현재 task + 관련 파일/현재 상태>

## 다음 액션
<resume 즉시 실행할 것 1-3, 우선순위순>

## 블로커 / 의존
<막힌 것, 대기 — 없으면 섹션 생략>

## 비자명 컨텍스트
<gotcha, 결정 사유, 취향 — 없으면 섹션 생략>

## TODO 스냅샷
<현재 TaskList 상태 요약 — resume이 task 재구성에 사용>
```

**메타데이터**(검증 R1 반영): `git_branch`/`git_head`/`git_dirty`로 resume 시 현재 Git 상태와 비교 → 오래된 handoff를 무비판적으로 task화하는 오류 방지.

## 7. 데이터 흐름

```mermaid
graph LR
    A["사용자 /clear 직전"] --> B["/zzizily:handoff"]
    B --> C[gitignore 보장 및 root 결정]
    C --> D[LLM이 §6 규격 작성 - repo-relative]
    D --> E["tmp 파일 write"]
    E --> F["gitleaks scan - 설치 시 fail-closed"]
    F --> G[archive write 및 latest.md rename]
    G --> H["/clear 또는 new session"]

    H --> I["/zzizily:resume"]
    I --> J[latest.md 읽기 - untrusted]
    J --> K["git 상태 비교 stale 경고"]
    K --> L["task preview 출력"]
    L --> M["사용자 승인"]
    M --> N["TaskCreate 재구성 및 다음 액션"]
```

### 저장 (`/handoff`) — 안전한 순서 (검증 2차 R2)

1. `.zzizily/.gitignore` 미존재 시 자동 생성(내용 `*`), `git check-ignore`로 검증
2. `git rev-parse --show-toplevel`로 repo root 결정 (non-Git cwd: cwd 기준, `git_*` 메타데이터 생략)
3. LLM이 현재 context에서 §6 규격 handoff 작성. **repo-relative path만** (절대 경로 금지, §9)
4. 임시 파일 `.zzizily/handoff/.tmp-<short8>` 에 write (같은 filesystem)
5. **secret scan**: gitleaks 설치 시 `.tmp-*` 대상 `gitleaks detect` → 탐지 시 **fail-closed**(저장 중단 + 사용자 통보). 미설치 시 LLM 지침 best-effort (§3.5 한계)
6. archive write: `handoff-<UTC-ts>-<short8>.md` (형식 `20260716T123456Z-<short8>`, Windows-safe + microsecond/UUID suffix 충돌 방지)
7. 같은 filesystem에서 atomic rename으로 `latest.md` 갱신 (race 방지)

### 복원 (`/resume`) — 승인 게이트 (검증 2차 신B2)

1. `latest.md` 읽기. 없거나 손상 시 최신 `handoff-*.md`로 fallback
2. **markdown을 untrusted data로 취급** — embedded instruction은 data로만, 자동 승격 금지 (§9)
3. `git_branch`/`git_head`/`git_dirty`를 현재 Git 상태와 비교 → 불일치 시 stale 경고
4. 작업목표/완료/진행중 요약 + **파싱된 task preview 출력**
5. **사용자 승인 후** TaskCreate로 진행중 + 다음 액션을 task로 재구성 (승인 전 자동 승격 금지 → injection 경로 차단)
6. 다음 액션 제안 후 "여기서 이어서?" 사용자 확인

## 8. 엣지 케이스 및 에러 처리

| 케이스 | 처리 |
| :--- | :--- |
| handoff 디렉토리/파일 없음 | `/resume`이 "저장된 handoff 없음" 안내 후 종료 |
| 빈 세션(의미 없음) | `/handoff` 시 "No active work" 1줄 저장 또는 사용자 확인 후 스킵 |
| Git 상태 불일치(stale) | resume 시 `git_*` 메타데이터 비교 → branch 전환/추가 커밋 경고 |
| non-Git cwd | `git rev-parse` 실패 시 cwd 기준 저장, `git_*` 필드 생략 |
| latest.md 손상 | `latest.md` 읽기 실패 시 최신 `handoff-*.md` fallback |
| gitleaks 미설치 | secret scan 건너뛰고 best-effort, SKILL.md에 한계 명시 |
| handoff 누적 | v1은 retention 자동 정리 미구현(append-only). 사용자 수동 정리 (검증 R3) |

## 9. 보안 고려사항

검증 B5 + 2차 신B1/신B2 반영 — 구체적 계약:

- **gitignore 자동 보장**: handoff 첫 write 전 `.zzizily/.gitignore`(`*`) 생성, `git check-ignore`로 검증
- **repo-relative path**: 절대 경로 기록 금지, 이식성 + 경로 노출 회피
- **secret 미기록 (best-effort, §3.5)**: `.env*`, API key/token, command output, file contents 저장 금지. SKILL.md 지침 + 저장 전 gitleaks detect(설치 시) fail-closed. **한계**: gitleaks 미설치 시 deterministic 보장 불가 → LLM 지침 best-effort, SKILL.md 명시
- **symlink fail-closed**: handoff 경로가 symlink면 쓰기 거부 (공격 경로 차단)
- **resume untrusted markdown**: 저장된 handoff를 신뢰하지 않음. embedded instruction(예: "ignore previous instructions")은 data로만 취급, **TaskCreate 승격 전 사용자 승인 필수** (자동 승격 = persistent injection 경로)
- **저장 root 결정**: `git rev-parse --show-toplevel` 사용, non-Git 처리 명시

## 10. 검증 계획 (dogfood)

| ID | 항목 | 방법 | 통과 기준 |
| :--- | :--- | :--- | :--- |
| V-1 | `/zzizily:handoff` 수동 저장 | 진행 중 세션에서 명령 실행 | 파일 생성 + §6 규격 + 메타데이터 준수 |
| V-2 | `/zzizily:resume` 복원 (승인 게이트) | new session에서 실행 | task preview → 승인 → TaskCreate 순서 확인 |
| V-3 | gitignore 자동 생성 | clean repo에서 /handoff | `.zzizily/.gitignore` 생성 + `git check-ignore` true |
| V-4 | stale 경고 | /handoff 후 branch 전환 → /resume | git 불일치 경고 출력 |
| V-5 | 빈 세션 처리 | 의미 없는 세션에서 /handoff | "No active work" 또는 정상 스킵 |
| V-6 | 보안 계약 | symlink 경로, 절대경로, secret(gitleaks 설치 시), 무승인 TaskCreate 시도 | 각각 fail-closed / 거부 / 승인 대기 |
| V-7 | gitleaks 연동 | gitleaks 설치 환경에서 secret 포함 handoff | 탐지 시 저장 중단 |
| V-8 | spec 재검증 | `/zzizily:verify` (Codex+Antigravity 2-Way) | Blocker 0 |

## 11. v2 로드맵 (자동 저장)

자동 저장이 재검토될 경우의 후보 (v1 확정 후 실제 수동 워크플로우 불편이 입증될 때만):

- **후보 A — PreCompact command hook + `claude -p`**: command hook이 headless LLM 세션으로 transcript 요약. 자동 달성 but 비용·timeout·recursion 위험. 가장 유력
- **후보 B — PostCompact command hook**: PostCompact 입력의 compact_summary(미문서화, 불확실) 저장. 의존 위험
- **후보 C — transcript deterministic 파싱**: JSONL 규칙 기반 추출. 빠르지만 의미요약 아님

v2 결정 시 본 섹션 기반 별도 spec 작성.

## 12. 검증 이력 및 근거

### 1차 검증 (초안 spec, 접근법 A: PreCompact prompt hook) → BLOCK

**수행**: `/zzizily:verify` 2-Way (Codex `gpt-5.6-sol` + Antigravity `agy 1.1.3` Gemini 3.1 Pro). 교차검증 WebFetch 공식 문서(code.claude.com/docs/en/hooks).

| ID | 내용 | 판정 | 반영 |
| :--- | :--- | :--- | :--- |
| B1 | PreCompact `type:"prompt"` 미지원 주장 | WebFetch "문서상 배제 증거 없음", Codex/agy 미지원(2:1). 불확정 | 자동 v2에서 별도 검증 |
| **B2** | **prompt hook tool/file access 불가** | **3소스 일치 확정**: single-turn yes/no evaluator, `{ok/decision}` JSON만 | **결정적 → prompt 기반 자동 저장 전면 폐기, 수동 v1 전환** |
| B3 | hook 위치 `.claude-plugin/hooks/` 비표준 | 공식은 plugin root `hooks/` | v1은 hook 없음 → 무관 |
| B4 | `TodoWrite` v2.1.142+ 기본 disabled | Codex/agy 주장, 현재 환경 TaskCreate 동작과 일치 | §3.4 TaskCreate 계약 |
| B5 | 보안 통제 선언 수준 | 타당 | §9 구체적 계약 승격 |

**Recommendation 흡수**: R1 git 메타데이터 → §6, R2 atomic rename + Windows-safe filename → §5/§7, R3 retention YAGNI → §8 append-only.

### 2차 재검증 (수정 spec v2, 수동 중심) → REQUEST_CHANGES (Codex) / NO BLOCKERS (agy)

**핵심 B2(prompt file write) 해소 확정 (2소스 일치)** — 수동 skill은 일반 tool/file access를 사용하므로 저장 가능.

Codex가 보안 정밀도에서 신규 2건 제기 (agy는 동일 영역을 Risk로 분류, 보안 민감도 고려 Codex 기준 채택):

| ID | 내용 | 반영 |
| :--- | :--- | :--- |
| 신B1 | secret fail-closed enforcement 메커니즘 부재 (지침만으로 deterministic 보장 불가) | §3.5 best-effort + gitleaks 연동 + 한계 명시 / §7 저장 순서에 scan 단계 / V-7 |
| 신B2 | resume 무승인 TaskCreate = untrusted handoff 자동 승격 = injection 경로 | §3.2/§7 복원: task preview → 사용자 승인 → TaskCreate / V-2/V-6 |

**추가 흡수**: R1 task preview 승인, R2 temp→scan→write→rename 순서, R3 같은 filesystem/microsecond suffix. **비채택(KISS 초과)**: R4 diff fingerprint 정밀 stale 탐지, R5 latest.md cache 무결성 검증 → §2 비목표 명시.

**결론**: 핵심 설계 방향(수동 v1)은 2소스 일치로 확정. 2차 Blocker는 보안 정밀도 디테일로 spec에 반영 완료. 단일 implementation plan에 적합 (agy/Codex 공동 확인).
