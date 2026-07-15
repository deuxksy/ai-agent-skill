# zzizily verify 컴포넌트 구현 계획

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** zzizily verify 검증 컴포넌트(skill 진입점 + subagent 격리 검증 하이브리드) 구현 — 05-multi-agent.md 검증 체계를 plugin 컴포넌트로 이관.

**Architecture:** 하이브리드. skill(`skills/verify/SKILL.md`, 신뢰 영역)이 보안 책임(snapshot 생성·secret redaction·격리 dir·무결성 감시)과 판사 역할(취합) 담당. subagent(`.claude-plugin/agents/verify.md`, 격리)은 격리 snapshot에서 순수 2-Way(Codex+Antigravity) 검증만 수행. 보안 결정권은 subagent에 없음.

**Tech Stack:** Claude Code plugin(skill/agent markdown), Codex MCP, Antigravity CLI(`agy`), gitleaks, sops, git, YAML frontmatter

**Spec:** `docs/superpowers/specs/2026-07-15-verify-subagent-design.md` (v3). 각 task의 문서 본문은 spec의 해당 섹션에서 발췌 — 이 plan은 정형 요소(frontmatter·출력 포맷·dispatch 계약·명령어)를 complete로 제공하고, 설명 본문은 정확한 spec 섹션을 인용.

## Global Constraints

- subagent frontmatter: `model: opus`, `level: 3`, `disallowedTools: Write, Edit`. 보안 결정권(redaction/배제/무결성 판정) 없음
- Codex: 모든 경로 MCP-first, 실패 시 `codex exec`. 항상 `cwd=<격리dir>` + `--sandbox read-only` (workspace-write 절대 금지)
- spec/plan 대상: 항상 2-Way (티어 무관, 메인 검증)
- plugin.json/marketplace.json: version `1.7.0` 동기화 필수
- SKILL.md 규격: frontmatter `name`+`description` 필수 (CLAUDE.md SKILL.md 규격)
- 결과는 항상 한국어
- 이 프로젝트는 빌드/테스트 과정 없음 (CLAUDE.md). 검증 단계 = frontmatter YAML 검증 + `/reload-plugins` 후 discovery/호출 테스트. TDD 코드 작성 없음

## File Structure

| 파일 | 책임 | 신규/수정 |
| :--- | :--- | :--- |
| `.claude-plugin/agents/verify.md` | subagent — 격리 snapshot에서 2-Way 검증, B/R/A/T 반환. 보안 결정권 없음 | 신규 |
| `skills/verify/SKILL.md` | skill 진입점 — 대상 수집·redaction·격리 snapshot·무결성 감시·dispatch·취합 | 신규 |
| `.claude-plugin/plugin.json` | `agents` 필드 추가, version 1.7.0 | 수정 |
| `.claude-plugin/marketplace.json` | version 1.7.0 동기화 | 수정 |
| `CLAUDE.md` | 구조 다이어그램·카탈로그·환경별 패키지 | 수정 |
| `~/git/dotfiles/base/.claude/rules/05-multi-agent.md` | 검증 절차 섹션 삭제, 트리거 최소 규칙+인프라 포인터 잔류 | 수정 (dotfiles repo) |

---

### Task 1: subagent verify.md

**Files:**
- Create: `.claude-plugin/agents/verify.md`

**Interfaces:**
- Consumes: skill(Task 2)가 dispatch한 입력 — `isolated_cwd`, `target_kind`, `target_files`, `tier`, `acceptance_criteria`, `provider_config`
- Produces: 최종 메시지 = Verification Report (B/R/A/T + VERDICT)

- [ ] **Step 1: 디렉토리 생성**

```bash
mkdir -p /Users/crong/git/ai-agent-skill/.claude-plugin/agents
```

- [ ] **Step 2: verify.md 작성 (frontmatter + 시스템 프롬프트)**

파일 `.claude-plugin/agents/verify.md` 생성. frontmatter는 아래 complete, 시스템 프롬프트 본문은 spec의 [subagent 상세 구성](../../specs/2026-07-15-verify-subagent-design.md#subagent-상세-구성)·[병렬 orchestration](../../specs/2026-07-15-verify-subagent-design.md#병렬-orchestration)·[라우팅 매핑](../../specs/2026-07-15-verify-subagent-design.md#라우팅-매핑)·[fail-closed 판정](../../specs/2026-07-15-verify-subagent-design.md#fail-closed-판정) 섹션을 발췌 작성.

frontmatter (complete, 그대로 사용):

```yaml
---
name: verify
description: 격리 snapshot에서 Codex+Antigravity 2-Way 교차검증. 보안 결정권 없음, 순수 검증 후 B/R/A/T 반환.
model: opus
level: 3
disallowedTools: Write, Edit
---
```

시스템 프롬프트 본문에 반드시 포함할 섹션 (spec 발췌):
1. **역할**: 격리 컨텍스트에서 순수 2-Way 검증. 보안 결정(redaction·배제·무결성 판정)은 skill이 완료한 상태로 받음 — subagent는 재판단 금지
2. **도구 세트**: `Bash`(cwd=격리 dir 강제, 외부 전송 금지), `mcp__codex__codex`(cwd 격리 dir, sandbox read-only), `mcp__codex__codex-reply`, `Read/Grep/Glob`(격리 dir 범위만)
3. **라우팅 매핑**: spec [라우팅 매핑](../../specs/2026-07-15-verify-subagent-design.md#라우팅-매핑) 표 그대로. spec/plan=항상 2-Way, 코드=경량·표준(Codex MCP 단일), 고위험(2-Way). MCP-first
4. **병렬 orchestration**: spec [병렬 orchestration](../../specs/2026-07-15-verify-subagent-design.md#병렬-orchestration) — 한 메시지에서 Antigravity+Codex 동시 호출. Codex Fallback은 Codex 라인 내 순차
5. **Codex Plan B**: spec [Codex Fallback](../../specs/2026-07-15-verify-subagent-design.md#codex-fallback-plan-b) — MCP 실패 시 `codex exec --sandbox read-only --cd <격리dir>`. quoting 규칙 포함
6. **fail-closed**: spec [fail-closed 판정](../../specs/2026-07-15-verify-subagent-design.md#fail-closed-판정) truth table 그대로. Antigravity 빈 응답/필드 누락=실패
7. **출력 포맷** (complete, 그대로 사용):

```text
## Verification Report

### Verdict
**Status**: PASS | FAIL | INCOMPLETE
**Target**: spec-plan | code
**Tier**: light | standard | high
**Routes used**: Antigravity(agy | failed), Codex(MCP | Bash-fallback | failed)
**Integrity**: skill이 별도 보고 (subagent는 모름)

### Findings (출처 표기)
- [Blocker] 즉시 수정 필요 — 근거(file:line/인용) — 출처: Codex | Antigravity | both
- [Risk] 수정 권장 — 근거 — 출처
- [Assumption] 검증된 가정 — 출처
- [Test] 제안 테스트 — 출처

### Cross-Check (2-Way 시)
| 항목 | Antigravity | Codex | 일치여부 | 충돌해결 |
| :--- | :--- | :--- | :--- | :--- |

### Recommendation
APPROVE | REQUEST_CHANGES | NEEDS_MORE_EVIDENCE
[한 줄 근거]
```

8. **충돌 해결**: 보안/권한·코드정확성=Codex 우선, 아키텍처/설계=Antigravity 우선. 상충 시 보수적 FAIL 우선

- [ ] **Step 3: frontmatter YAML 검증**

```bash
head -8 /Users/crong/git/ai-agent-skill/.claude-plugin/agents/verify.md
```
Expected: frontmatter 7개 필드(name, description, model, level, disallowedTools + `---` 구분선 2개) 출력

- [ ] **Step 4: commit**

```bash
cd /Users/crong/git/ai-agent-skill
git add .claude-plugin/agents/verify.md
git commit -m "feat(verify): subagent verify.md 추가 — 격리 2-Way 검증"
```

---

### Task 2: skill verify/SKILL.md

**Files:**
- Create: `skills/verify/SKILL.md`

**Interfaces:**
- Consumes: subagent(Task 1) — `Agent` 도구로 dispatch
- Produces: `/zzizily:verify` 진입점 + 보안 처리된 격리 snapshot + Verification Report 취합

- [ ] **Step 1: 디렉토리 생성**

```bash
mkdir -p /Users/crong/git/ai-agent-skill/skills/verify
```

- [ ] **Step 2: SKILL.md 작성**

파일 `skills/verify/SKILL.md` 생성. frontmatter complete, 본문은 spec 해당 섹션 발췌.

frontmatter (complete):

```yaml
---
name: verify
description: "Codex+Antigravity 2-Way 교차검증. spec/plan(항상 2-Way, 메인 검증)·코드(3단계 티어)를 격리 snapshot에서 검증. 보안(redaction·무결성)은 skill이 담당. /zzizily:verify [대상]"
---
```

본문에 반드시 포함할 섹션 (spec 발췌):
1. **진입점/Usage**: `/zzizily:verify [대상]` + 자동 트리거 키워드("검증", "verify", "리뷰해줘"). 단, rules 제외 필터(실행 중/출력 중/opt-out)로 무한 루프 방지
2. **외부 전송 동의**: 최초 1회 (project-level 사전 동의 또는 첫 호출 확인). 미동의 시 수동 안내 종료
3. **보안 책임 (v3 핵심)** — spec [보안 책임 분리](../../specs/2026-07-15-verify-subagent-design.md#보안-책임-분리-v3-핵심):
   - 대상 snapshot 결정적 생성 (git diff: staged/unstaged/untracked/rename/delete/binary/대용량/혼합)
   - secret redaction (gitleaks/sops 스캔, `[REDACTED]` 치환, scanner 실패 시 fail-closed)
   - 민감 파일 배제 (`.env*`, `.key`, `.sops`, `~/.codex/`, `~/.config/**`)
   - **격리 tmp directory**에 정제 복사본 생성 → 원본 workspace 접근 차단
   - 원본 무결성 기록(전): tracked/untracked hash, git status, mtime, permission
4. **dispatch 실행 계약** (complete, 그대로 사용):

```text
도구: Agent
subagent: verify (namespace zzizily:verify)
입력(자연어 지시에 포함):
  - isolated_cwd: 격리 tmp directory 절대경로
  - target_kind: spec-plan | code
  - target_files: 격리 복사본 내 상대경로 목록
  - tier: light | standard | high (코드만)
  - acceptance_criteria: 선택
  - provider_config: Codex model/sandbox, Antigravity 모델 (rules에서 읽어 전달)
반환: subagent 최종 메시지 = Verification Report
미발견 처리: discovery 실패 시 에러 리포트(plugin 미설치/agents 필드 누락/reload-plugins 의심) 출력 후 종료
```

5. **무결성 사후 검증**: 모든 child process 종료 확인(TOCU 방지 대기) 후 원본 무결성 광범위 비교(tracked/untracked/metadata/대상 외/write→restore). 변경 시 `Integrity: TAMPER-DETECTED` → INCOMPLETE
6. **취합·표시**: subagent 결과 + Integrity 보고 통합 표시. blocker 시 수정 권고. 격리 tmp dir 정리
7. **데이터 흐름**: spec [데이터 흐름](../../specs/2026-07-15-verify-subagent-design.md#데이터-흐름) 11단계 그대로
8. **`## Key Rules`**: 한국어 리포트, 보안 책임 skill 전담, Codex workspace-write 금지, fail-closed, 격리 dir 정리

- [ ] **Step 3: frontmatter 검증**

```bash
head -4 /Users/crong/git/ai-agent-skill/skills/verify/SKILL.md
```
Expected: `name: verify`, `description:`, `---` 구분선 2개

- [ ] **Step 4: commit**

```bash
cd /Users/crong/git/ai-agent-skill
git add skills/verify/SKILL.md
git commit -m "feat(verify): skill verify/SKILL.md 추가 — 진입점 + 보안 책임"
```

---

### Task 3: plugin manifests (agents 필드 + 버전)

**Files:**
- Modify: `.claude-plugin/plugin.json`
- Modify: `.claude-plugin/marketplace.json`

**Interfaces:**
- Produces: plugin이 `agents` 디렉토리 인식, version 1.7.0

- [ ] **Step 1: plugin.json 수정**

`"skills": "./skills/"` 뒤에 `"agents"` 필드 추가, `version` 1.7.0. 최종 형태:

```json
{
  "name": "zzizily",
  "description": "Personal skill collection: agents install/upgrade/setup, security audit, deploy, translation, game deals, exchange rate",
  "version": "1.7.0",
  "author": {
    "name": "Crong"
  },
  "skills": "./skills/",
  "agents": "./.claude-plugin/agents/"
}
```

- [ ] **Step 2: marketplace.json 수정**

`plugins[0].version` 1.6.0 → 1.7.0:

```json
{
  "name": "zzizily",
  "owner": { "name": "Crong" },
  "plugins": [
    {
      "name": "deuxksy",
      "source": "./",
      "description": "Personal skill collection: agents install/upgrade/setup, security audit, deploy, translation, game deals, exchange rate",
      "version": "1.7.0"
    }
  ]
}
```

- [ ] **Step 3: 버전 동기화 검증**

```bash
grep -h '"version"' /Users/crong/git/ai-agent-skill/.claude-plugin/plugin.json /Users/crong/git/ai-agent-skill/.claude-plugin/marketplace.json
```
Expected: `1.7.0` 2회 출력 (양쪽 동기화). agents 필드 확인:

```bash
grep '"agents"' /Users/crong/git/ai-agent-skill/.claude-plugin/plugin.json
```
Expected: `"agents": "./.claude-plugin/agents/"`

- [ ] **Step 4: commit**

```bash
cd /Users/crong/git/ai-agent-skill
git add .claude-plugin/plugin.json .claude-plugin/marketplace.json
git commit -m "feat(verify): plugin manifests agents 필드 추가 + v1.7.0"
```

---

### Task 4: CLAUDE.md 업데이트

**Files:**
- Modify: `CLAUDE.md`

**Interfaces:**
- Produces: 카탈로그/구조/패키지에 verify 반영

- [ ] **Step 1: 구조 다이어그램에 agents 추가**

`CLAUDE.md`의 구조 트리에서 `.claude-plugin/` 하위에 `agents/`와 `verify.md` 추가:

```text
├── .claude-plugin/
│   ├── plugin.json          # 플러그인 매니페스트
│   ├── marketplace.json     # 마켓플레이스 등록 정보
│   └── agents/
│       └── verify.md        # 검증 subagent (격리 2-Way)
└── skills/
    ...
    ├── verify/                    # 검증 (skill 진입점 + subagent 하이브리드)
    ...
```

`skills/` 트리에 `verify/` 행 추가.

- [ ] **Step 2: 스킬 카탈로그에 verify 행 추가**

`### AI Agent · 배포 (Agents & Deploy)` 그룹 테이블에 행 추가 (분류 원칙: 개발 워크플로우 검증 도구 → AI Agent·배포 그룹):

```markdown
| verify | Codex+Antigravity 2-Way 교차검증 (spec/plan 항상 2-Way, 코드 3단계 티어) |
```

동시에 "스킬 카탈로그 (16)" → "(17)" 로 카운트 수정.

- [ ] **Step 3: 환경별 패키지 관리 섹션에 agents 언급**

macOS 항목 아래 또는 별도 행에 verify 컴포넌트 의존성(gitleaks, sops는 기존, Codex/agy는 agents 스킬) 언급 한 줄 추가. 예:

```markdown
- zzizily verify: Codex MCP + Antigravity(agy) + gitleaks/sops 의존 (agents 스킬로 설치)
```

- [ ] **Step 4: commit**

```bash
cd /Users/crong/git/ai-agent-skill
git add CLAUDE.md
git commit -m "docs(claude-md): verify 컴포넌트 카탈로그/구조/패키지 반영"
```

---

### Task 5: rules 05-multi-agent.md 검증 절차 이관

**Files:**
- Modify: `/Users/crong/git/dotfiles/base/.claude/rules/05-multi-agent.md` (dotfiles repo, stow 배포)

**Interfaces:**
- Produces: rules 검증 절차 섹션 삭제 + 트리거 최소 규칙/인프라 포인터 잔류

> 주의: 이 파일은 `~/git/dotfiles` repo. ai-agent-skill과 별도 git. commit은 dotfiles repo에서.

- [ ] **Step 1: 파일 백업 태그**

```bash
cd /Users/crong/git/dotfiles
git tag rules-pre-verify-migration
```
검증 절차 이관 전 체크포인트 (사용자 동의 후 복구 가능).

- [ ] **Step 2: 검증 절차 섹션 식별**

`05-multi-agent.md`에서 이관 대상 섹션: `## Verification Workflow`, `### 3단계 검증 티어`, `### 기본 라우팅`, `### 고위험 승격 조건`, `### 특수 경로`, `### 검증 출력 포맷`, `### 충돌 해결 규칙`, `### 검증 원칙`, `### 교차 검증 (현재 2-Way 운영)` (+ Mermaid). 이 섹션들은 zzizily `verify` subagent(Task 1) 시스템 프롬프트로 이미 이관됨.

- [ ] **Step 3: 검증 절차 섹션 삭제 + 잔류 섹션 정리**

위 섹션들을 삭제. 대신 파일 상단(또는 `## Verification Workflow` 자리)에 최소 트리거 규칙 + 인프라 포인터 삽입:

```markdown
## 검증 (zzizily verify로 이관)

검증 실행 로직(3단계 티어, Codex+Antigravity 2-Way, 라우팅, B/R/A/T 포맷, 충돌 해결)은
zzizily plugin의 `verify` 컴포넌트(skill + subagent)로 이관됨.

**자동 트리거**: 사용자 명시적 입력에서 '검증'/'verify'/'리뷰해줘' + 검증 대상(spec/plan/diff)
감지 시 `/zzizily:verify` 자동 호출.
**제외**(무한 루프 방지): 이미 verify 실행 중 / 리포트 출력 중 / opt-out 플래그 세션에서는 트리거 안 함.

**인프라 설정**(아래 각 섹션 유지, Source of Truth): 검증 시 zzizily verify가 소비.
- Codex: MCP 설정·파라미터 → 아래 `## Codex` 섹션
- Antigravity: CLI 사용법·모델 → 아래 `## Antigravity CLI` 섹션
- K8sGPT/Holmes/Serena: 도메인 에이전트 → 아래 각 섹션
```

잔류 유지 섹션: `## Codex (MCP + Bash Hybrid)`, `## Antigravity CLI`, `## K8sGPT`, `## Holmes`, `## Serena`, `## Gmail MCP`, `### Provider Models`.

- [ ] **Step 4: 잔류 섹션 확인**

```bash
grep -n '^##' /Users/crong/git/dotfiles/base/.claude/rules/05-multi-agent.md
```
Expected: `## 검증 (zzizily verify로 이관)`, `## Codex`, `## Antigravity CLI`, `## K8sGPT`, `## Holmes`, `## Serena`, `## Gmail MCP`, `### Provider Models` 등. 검증 절차 섹션(Verification Workflow, 3단계 검증 티어, 충돌 해결 규칙 등)은 사라져야 함.

- [ ] **Step 5: commit (dotfiles repo)**

```bash
cd /Users/crong/git/dotfiles
git add base/.claude/rules/05-multi-agent.md
git commit -m "refactor(rules): 05-multi-agent 검증 절차 zzizily verify로 이관

검증 실행 로직(티어/2-Way/라우팅/B-R-A-T/충돌해결)은 zzizily plugin verify로 이관.
rules에는 자동 트리거 최소 규칙 + 인프라 설정(Codex/Antigravity/K8sGPT 등) 잔류."
```

---

### Task 6: 통합 검증

**Files:**
- 없음 (검증만)

- [ ] **Step 1: plugin reload**

사용자에게 `/reload-plugins` 실행 요청 (또는 `! /reload-plugins` 입력). verify skill/agent가 registry에 로드됨.

- [ ] **Step 2: skill discovery 확인**

```bash
ls /Users/crong/git/ai-agent-skill/skills/verify/SKILL.md /Users/crong/git/ai-agent-skill/.claude-plugin/agents/verify.md
```
Expected: 두 파일 존재. plugin이 `skills/` + `.claude-plugin/agents/` 모두 인식.

- [ ] **Step 3: `/zzizily:verify` 호출 테스트**

사용자가 `/zzizily:verify docs/superpowers/specs/2026-07-15-verify-subagent-design.md` 호출 (이 spec은 이미 dogfood 검증됐으므로 좋은 테스트 대상).

검증 항목:
- skill이 진입점으로 활성화 (자동 트리거 또는 명시 호출)
- 외부 전송 동의 프롬프트 (최초 1회)
- 격리 snapshot 생성 로직 출력
- subagent dispatch (zzizily:verify discovery)
- 2-Way 실행 (Antigravity + Codex)
- B/R/A/T + VERDICT + Cross-Check 출력
- 무결성 보고 (TAMPER 미탐지 시 verified)

- [ ] **Step 4: 실패 시나리오 점검 (수동)**

- Codex MCP 강제 실패 상황에서 `codex exec` fallback 전환 확인
- 민감 파일(`.env`) 포함 대상 → redaction/배제 확인
- 무한 루프: 리포트 출력 후 자동 재호출 안 일어나는지 확인

- [ ] **Step 5: 최종 보고**

검증 결과를 사용자에게 보고. blocker 시 Task 1-5 중 해당 파일 수정 후 재검증.

---

## Self-Review

**1. Spec coverage:**
- subagent(격리 2-Way, 보안 결정권 없음) → Task 1
- skill(진입점+보안 책임+dispatch+취합) → Task 2
- plugin.json agents 필드 + v1.7.0 동기화 → Task 3
- CLAUDE.md 카탈로그/구조/패키지 → Task 4
- rules 검증 절차 이관, 트리거/포인터 잔류 → Task 5
- 통합 검증/discovery → Task 6
- 격리 snapshot, 무결성, redaction, fail-closed truth table, 무한루프 방지, 외부 전송 동의 → Task 1/2 본문(spec 발췌)
- gap: 없음

**2. Placeholder scan:** "spec 발췌" 지시는 정확한 섹션 링크 포함 → placeholder 아님. frontmatter·출력 포맷·dispatch 계약·명령어는 complete.

**3. Type consistency:** subagent 입력 필드(`isolated_cwd`, `target_kind`, `target_files`, `tier`, `provider_config`)가 Task 2 dispatch 계약과 Task 1 시스템 프롬프트에서 일치. 출력 포맷(B/R/A/T + VERDICT) 양쪽 일치.
