# agents-md-management Plugin Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** `.ai/RULES.md` 공통 규칙과 `AGENTS.md`, `CLAUDE.md`, `GEMINI.md` vendor 규칙을 계층적으로 audit하고 session learning을 안전하게 반영하는 runtime-neutral Agent Skills plugin을 추가한다.

**Architecture:** `plugins/agents-md-management`를 self-contained marketplace plugin으로 만들고 repository audit용 `agents-md-management`와 session learning 반영용 `revise-agents-md`를 분리한다. Root `.ai/RULES.md`를 common Single Source of Truth로 사용하며 root vendor 파일은 reference만 가지고 nested vendor 파일은 subtree override만 보유한다.

**Tech Stack:** Markdown Agent Skills, YAML frontmatter, Claude plugin JSON manifest, AGENTS.md open standard, Claude Code `@file` import, Gemini `@file` import, PowerShell validation

## Global Constraints

- Design source: `docs/superpowers/specs/2026-07-29-commit-and-agents-md-plugins-design.md`.
- Plugin name과 version은 `agents-md-management` / `1.0.0`으로 고정한다.
- 기존 root `zzizily` plugin version `1.8.4`와 기존 19개 Skill을 변경하지 않는다.
- `agents-md-management`와 `revise-agents-md`는 별도 Skill로 구현한다.
- 공통 규칙은 repository root `.ai/RULES.md`에서만 관리한다.
- Root `CLAUDE.md`와 `GEMINI.md`는 `@./.ai/RULES.md`를 native import한다.
- Root `AGENTS.md`는 `.ai/RULES.md`를 작업 전에 읽도록 명시한다. Native import로 가장하지 않는다.
- Nested vendor 파일은 root common rule을 재-import하지 않고 해당 subtree override만 가진다.
- 모든 file mutation은 quality report 또는 learning diff preview와 명시적 승인 후 실행한다.
- Symlink target, 승인 후 drift가 발생한 file, secret 포함 learning은 수정하지 않는다.
- Runtime별 `SKILL.md` 복제본과 자동 installer를 만들지 않는다.
- 결과와 README는 한국어로 작성하고 IT 전문 용어는 영어를 사용한다.
- Upstream Apache License 2.0과 변경 attribution을 보존한다.
- File edit은 `apply_patch`로 수행하고, task마다 지정된 파일만 commit한다.

---

### Task 1: Plugin foundation과 `agents-md-management` audit Skill

**Files:**
- Create: `plugins/agents-md-management/.claude-plugin/plugin.json`
- Create: `plugins/agents-md-management/LICENSE`
- Create: `plugins/agents-md-management/README.md`
- Create: `plugins/agents-md-management/skills/agents-md-management/SKILL.md`
- Create: `plugins/agents-md-management/skills/agents-md-management/references/quality-criteria.md`
- Modify: `.claude-plugin/marketplace.json:6-13`
- Modify: `README.md:5-33`

**Interfaces:**
- Consumes: repository file tree, codebase commands/configuration, root/nested instruction files
- Produces: installable plugin `agents-md-management@zzizily`, audit Skill `agents-md-management`, 100-point quality report contract

- [ ] **Step 1: Run the structural check and verify it fails**

Run:

```powershell
$paths = @(
  'plugins/agents-md-management/.claude-plugin/plugin.json',
  'plugins/agents-md-management/skills/agents-md-management/SKILL.md',
  'plugins/agents-md-management/skills/agents-md-management/references/quality-criteria.md'
)
if (($paths | Where-Object { -not (Test-Path -LiteralPath $_) }).Count -eq 0) {
  throw 'Expected agents-md-management files to be absent before implementation'
}
```

Expected: command succeeds because at least one required file is absent.

- [ ] **Step 2: Create the plugin manifest**

Create `plugins/agents-md-management/.claude-plugin/plugin.json` with:

```json
{
  "name": "agents-md-management",
  "description": "Audit and revise common and vendor-specific AI agent instruction files",
  "version": "1.0.0",
  "author": {
    "name": "Crong"
  },
  "skills": "./skills/"
}
```

- [ ] **Step 3: Add the marketplace entry without changing existing entries**

Add this object to `.claude-plugin/marketplace.json` `plugins` array. Preserve the `deuxksy` entry and any independently-added plugin entries.

```json
{
  "name": "agents-md-management",
  "source": "./plugins/agents-md-management",
  "description": "Audit and revise AGENTS.md, CLAUDE.md, GEMINI.md, and shared .ai/RULES.md",
  "version": "1.0.0"
}
```

Parse check:

```powershell
$marketplace = Get-Content -Raw '.claude-plugin/marketplace.json' | ConvertFrom-Json
$entry = $marketplace.plugins | Where-Object name -eq 'agents-md-management'
if ($entry.Count -ne 1 -or $entry.version -ne '1.0.0' -or $entry.source -ne './plugins/agents-md-management') {
  throw 'agents-md-management marketplace entry is invalid'
}
```

Expected: no output, exit code `0`.

- [ ] **Step 4: Add Apache 2.0 license**

Create `plugins/agents-md-management/LICENSE` by copying the exact Apache License 2.0 text from:

```text
https://raw.githubusercontent.com/anthropics/claude-plugins-official/main/plugins/claude-md-management/LICENSE
```

Verify:

```powershell
$license = Get-Content -Raw 'plugins/agents-md-management/LICENSE'
if ($license -notmatch 'Apache License' -or $license -notmatch 'Version 2.0') {
  throw 'Apache 2.0 license text is missing'
}
```

- [ ] **Step 5: Create the quality criteria reference**

Create `plugins/agents-md-management/skills/agents-md-management/references/quality-criteria.md` with:

```markdown
# Instruction Quality Criteria

각 instruction file과 effective hierarchy를 100점으로 평가한다.

| Criterion | Weight | Pass condition |
| :--- | ---: | :--- |
| Commands/workflows | 15 | Build, test, lint, deploy command가 실제 config와 일치 |
| Architecture/key paths | 15 | Entry point, 주요 module, dependency 관계가 현재 codebase와 일치 |
| Currency | 15 | 삭제·이동·rename된 command/path가 없음 |
| Actionability | 15 | 모호한 권고가 아니라 실행·검증 가능한 instruction |
| Common/vendor separation | 15 | 공통 rule은 `.ai/RULES.md`, vendor rule은 해당 vendor file에만 존재 |
| Hierarchy/reference | 15 | Root reference와 nested precedence가 정확하며 중복 import 없음 |
| Non-obvious gotchas | 5 | 반복 가능한 환경·tool·workflow 함정만 포함 |
| Conciseness | 5 | 자명한 설명, 장황함, 중복 없음 |

## Grades

- A: 90-100
- B: 70-89
- C: 50-69
- D: 30-49
- F: 0-29

## Required report

1. 발견한 file과 적용 scope
2. File별 score와 근거
3. Effective hierarchy의 conflict/reference 문제
4. Codebase와 불일치하는 exact command/path
5. Targeted addition, edit, removal 제안
6. 평균 score와 update 필요 file 수

Score는 근거 없는 감점에 사용하지 않는다. 확인할 수 없는 항목은 `미검증`으로 표시하고 전체 score 한계를 명시한다.
```

- [ ] **Step 6: Create the complete audit Skill**

Create `plugins/agents-md-management/skills/agents-md-management/SKILL.md` with this frontmatter:

```yaml
---
name: agents-md-management
description: "Repository의 root·nested AGENTS.md, CLAUDE.md, GEMINI.md와 공통 .ai/RULES.md를 discovery하고 codebase 정합성, hierarchy, reference, 중복, 충돌을 audit한 뒤 승인된 targeted update만 적용한다."
---
```

The Markdown body must contain:

```markdown
# Agents Markdown Management

AI coding agent instruction hierarchy를 audit하고 targeted improvement를 제안한다.

## Instruction model

- Repository root `.ai/RULES.md`: 모든 runtime 공통 rule의 Single Source of Truth.
- Root `CLAUDE.md`: Claude 전용 rule + `@./.ai/RULES.md`.
- Root `GEMINI.md`: Gemini/Antigravity 전용 rule + `@./.ai/RULES.md`.
- Root `AGENTS.md`: AGENTS.md/Codex 전용 rule + 작업 전 root `.ai/RULES.md`를 읽으라는 instruction.
- Nested vendor file: 해당 subtree 전용 override. Common rule을 재-import하지 않는다.

Codex `AGENTS.md` reference는 native import가 아니라 instruction-based best-effort임을 report한다.

## 1. Discovery

1. Git root를 우선 사용하고 non-Git이면 current directory를 root로 사용한다.
2. Root와 nested `AGENTS.md`, `CLAUDE.md`, `GEMINI.md` 및 root `.ai/RULES.md`를 찾는다.
3. `.git`, dependency cache, generated/build output은 제외한다.
4. 각 file이 symlink인지 확인하고 write 가능 대상으로 간주하지 않는다.
5. Directory별 effective hierarchy와 nearest-file precedence를 계산한다.

## 2. Codebase assessment

1. Build/test/lint/deploy command를 package manifest, task runner, CI config와 비교한다.
2. Architecture, entry point, key path를 실제 file tree와 비교한다.
3. Common rule과 vendor-specific rule의 위치를 분류한다.
4. Root reference 누락·오류, nested duplicate import, 중복·충돌을 확인한다.
5. `references/quality-criteria.md`로 file별 score와 근거를 작성한다.

## 3. Quality report

Update 전에 반드시 다음을 출력한다.

- 발견 file 수, 평균 score, update 필요 file 수
- File별 scope, score, 확인 근거
- Exact stale command/path, conflict, duplicate, reference 오류
- Targeted update와 기대 효과
- 확인할 수 없는 항목과 한계

## 4. Proposed changes

1. 누락 file은 자동 생성하지 않고 complete creation diff를 제시한다.
2. 기존 structure와 style을 보존한 최소 diff를 제시한다.
3. Common rule은 `.ai/RULES.md`에만 제안한다.
4. Vendor/subtree rule은 정확한 vendor 또는 nested file에 제안한다.
5. Conflict를 임의 병합하지 않고 선택을 요청한다.

## 5. Approval and apply

1. File별 변경 사유와 diff를 제시하고 명시적 승인을 기다린다.
2. 승인 직후 target content와 symlink 상태를 다시 확인한다.
3. Drift 또는 symlink이면 write하지 않고 새 diff가 필요함을 보고한다.
4. 승인된 file과 hunk만 수정한다.
5. Reference, hierarchy, duplicate, conflict를 다시 검사한다.

## Safety

- 승인 전 file을 생성·수정하지 않는다.
- 전체 rewrite와 unrelated 문서 개선을 하지 않는다.
- Secret, credential, 개인 절대경로를 instruction에 추가하지 않는다.
- Symlink target을 수정하지 않는다.
- Non-Git 환경의 current/stale 검증 한계를 명시한다.

## Attribution

Adapted from Anthropic `claude-md-management/skills/claude-md-improver` under Apache License 2.0. Modified for AGENTS.md standard, shared `.ai/RULES.md`, Claude/Codex/Antigravity hierarchies, symlink safety, and approval gates.
```

- [ ] **Step 7: Create the initial plugin README**

Create `plugins/agents-md-management/README.md` with:

```markdown
# agents-md-management

공통 `.ai/RULES.md`와 vendor별 `AGENTS.md`, `CLAUDE.md`, `GEMINI.md`를 audit하고 session learning을 반영하는 runtime-neutral Agent Skills plugin.

**Version:** 1.0.0

## Skills

| Skill | 설명 |
| :--- | :--- |
| `agents-md-management` | Root+nested instruction hierarchy audit와 targeted update |

## Instruction model

| File | Scope |
| :--- | :--- |
| `.ai/RULES.md` | 모든 runtime 공통 |
| `AGENTS.md` | AGENTS.md 표준/Codex 전용 |
| `CLAUDE.md` | Claude Code 전용 |
| `GEMINI.md` | Gemini/Antigravity 전용 |

Root `CLAUDE.md`와 `GEMINI.md`는 `@./.ai/RULES.md`를 import한다. Root `AGENTS.md`는 작업 전에 `.ai/RULES.md`를 읽도록 지시한다. Nested vendor 파일은 subtree override만 가진다.

## Claude Code

```bash
claude plugin install agents-md-management@zzizily
```

호출: `/agents-md-management:agents-md-management`

## Safety

- Quality report와 diff 우선
- 명시적 승인 후 file mutation
- Symlink와 승인 후 drift는 fail-closed
- Secret과 one-off context 기록 금지

## Attribution

Adapted from Anthropic
[`claude-md-management`](https://github.com/anthropics/claude-plugins-official/tree/main/plugins/claude-md-management)
under Apache License 2.0. This version generalizes the workflow for AGENTS.md, CLAUDE.md, GEMINI.md, and shared `.ai/RULES.md`.
```

- [ ] **Step 8: Add the independent plugin catalog to root README**

Immediately before `## 스킬 카탈로그 (19)`, create `## 독립 Plugin` if absent and add the `agents-md-management` row. If another plan already created the section, preserve its rows and append only the missing row.

```markdown
## 독립 Plugin

기존 `zzizily`와 별도로 설치하는 domain plugin.

| Plugin | Version | Skills |
| :--- | :--- | :--- |
| `agents-md-management` | 1.0.0 | `agents-md-management`, `revise-agents-md` |
```

Add this install command to the Quick Start code block without changing the existing `deuxksy@zzizily` command:

```bash
claude plugin install agents-md-management@zzizily
```

- [ ] **Step 9: Run focused validation**

Run:

```powershell
$manifest = Get-Content -Raw 'plugins/agents-md-management/.claude-plugin/plugin.json' | ConvertFrom-Json
$marketplace = Get-Content -Raw '.claude-plugin/marketplace.json' | ConvertFrom-Json
$skill = Get-Content -Raw 'plugins/agents-md-management/skills/agents-md-management/SKILL.md'
$criteria = Get-Content -Raw 'plugins/agents-md-management/skills/agents-md-management/references/quality-criteria.md'
if ($manifest.name -ne 'agents-md-management' -or $manifest.version -ne '1.0.0') { throw 'manifest mismatch' }
if (($marketplace.plugins | Where-Object name -eq 'agents-md-management').Count -ne 1) { throw 'marketplace mismatch' }
if ($skill -notmatch '(?m)^name: agents-md-management$' -or $skill -notmatch '(?m)^description:') { throw 'frontmatter mismatch' }
if ($criteria -notmatch '100점' -or $criteria -notmatch 'Hierarchy/reference') { throw 'quality criteria mismatch' }
git diff --check
```

Expected: no output, exit code `0`.

- [ ] **Step 10: Security review and commit**

Run:

```powershell
rg -n "(?i)(api[_-]?key|access[_-]?token|password)\s*[:=]\s*[^\s`]+" plugins/agents-md-management README.md .claude-plugin/marketplace.json
git status --short
```

Expected: secret assignment scan returns no findings; status contains only Task 1 files.

Commit:

```bash
git add .claude-plugin/marketplace.json README.md plugins/agents-md-management/.claude-plugin/plugin.json plugins/agents-md-management/LICENSE plugins/agents-md-management/README.md plugins/agents-md-management/skills/agents-md-management/SKILL.md plugins/agents-md-management/skills/agents-md-management/references/quality-criteria.md
git commit -m "feat(agents-md): instruction audit skill 추가"
```

---

### Task 2: `revise-agents-md` session learning Skill

**Files:**
- Create: `plugins/agents-md-management/skills/revise-agents-md/SKILL.md`
- Modify: `plugins/agents-md-management/README.md`

**Interfaces:**
- Consumes: 현재 session context, 기존 root/nested instruction files
- Produces: Skill name `revise-agents-md`, common/vendor/subtree learning classification과 approval-gated diff

- [ ] **Step 1: Run the file-existence check and verify it fails**

Run:

```powershell
if (Test-Path 'plugins/agents-md-management/skills/revise-agents-md/SKILL.md') {
  throw 'Expected revise-agents-md skill to be absent'
}
```

Expected: exit code `0`.

- [ ] **Step 2: Create the complete `revise-agents-md` Skill**

Create `plugins/agents-md-management/skills/revise-agents-md/SKILL.md` with this frontmatter:

```yaml
---
name: revise-agents-md
description: "현재 session에서 반복 사용할 가치가 있는 learning을 추출해 공통 .ai/RULES.md 또는 vendor·subtree별 AGENTS.md, CLAUDE.md, GEMINI.md에 분류하고 승인된 최소 diff만 반영한다."
---
```

The Markdown body must contain:

```markdown
# Revise Agent Instructions

현재 session learning을 다음 session에도 필요한 최소 instruction으로 반영한다. 전체 quality audit은 수행하지 않는다.

## 1. Reflect

다음 중 반복 사용 가치가 있는 사실만 추출한다.

- 실제로 사용·검증된 build/test/lint/deploy command
- 반복되는 code style 또는 architecture pattern
- 재현 가능한 environment/configuration quirk
- 반복 가능한 warning 또는 gotcha
- Agent runtime별로 필요한 동작 차이

One-off fix, 자명한 정보, 추측, raw output은 제외한다.

## 2. Discover targets

1. Git root를 우선 사용하고 non-Git이면 current directory를 root로 사용한다.
2. Root와 관련 subtree의 `.ai/RULES.md`, `AGENTS.md`, `CLAUDE.md`, `GEMINI.md`를 확인한다.
3. Symlink target은 write 대상으로 사용하지 않는다.
4. 기존 rule과 learning의 중복·충돌을 확인한다.

## 3. Classify

| Learning | Target |
| :--- | :--- |
| 모든 runtime 공통 | Root `.ai/RULES.md` |
| AGENTS.md 표준 또는 Codex 전용 | `AGENTS.md` |
| Claude Code 전용 | `CLAUDE.md` |
| Gemini/Antigravity 전용 | `GEMINI.md` |
| 특정 subtree 전용 | 해당 subtree의 vendor file |

Scope가 불명확하면 한 번에 하나의 질문으로 확인한다. Common rule을 vendor file에 복제하지 않는다.

## 4. Secret and relevance filter

- Secret, token, credential, private key, 개인 절대경로를 제거한다.
- Raw command output과 file content dump를 저장하지 않는다.
- 검증되지 않은 사실과 일회성 workaround를 제거한다.
- 기존 instruction과 의미가 같은 learning은 추가하지 않는다.

## 5. Preview and approval

Target file별로 다음을 제시한다.

- Learning 한 줄 요약
- Common/vendor/subtree 분류 근거
- Existing conflict 또는 duplicate 여부
- 최소 diff

명시적 승인 전에는 file을 생성·수정하지 않는다. Conflict가 있으면 자동 선택하지 않는다.

## 6. Apply

1. 승인 직후 target content와 symlink 상태를 다시 확인한다.
2. Drift 또는 symlink이면 write하지 않고 새 diff가 필요함을 보고한다.
3. 승인된 target과 hunk만 수정한다.
4. Root reference와 nested duplicate import를 확인한다.
5. 변경 file과 반영·제외한 learning을 보고한다.

## Attribution

Adapted from Anthropic `claude-md-management/commands/revise-claude-md.md` under Apache License 2.0. Modified for shared `.ai/RULES.md`, AGENTS.md/CLAUDE.md/GEMINI.md classification, nested scope, secret filtering, and approval gates.
```

- [ ] **Step 3: Update plugin README**

Add the Skill row:

```markdown
| `revise-agents-md` | Session learning을 common/vendor/subtree로 분류해 승인 후 최소 반영 |
```

Add Claude invocation:

```text
/agents-md-management:revise-agents-md
```

Add the workflow distinction:

```markdown
## Workflow 선택

- Repository 전체 instruction 품질과 codebase 정합성 점검: `agents-md-management`
- 현재 session에서 확인한 learning만 최소 반영: `revise-agents-md`
```

- [ ] **Step 4: Validate classification and safety**

Run:

```powershell
$skill = Get-Content -Raw 'plugins/agents-md-management/skills/revise-agents-md/SKILL.md'
foreach ($required in @('.ai/RULES.md', 'AGENTS.md', 'CLAUDE.md', 'GEMINI.md', 'subtree', '승인', 'Secret', 'Symlink', 'Drift')) {
  if ($skill -notmatch [regex]::Escape($required)) { throw "Missing revise contract: $required" }
}
if ($skill -notmatch '전체 quality audit은 수행하지 않는다') { throw 'Audit/revise boundary is missing' }
git diff --check
```

Expected: no output, exit code `0`.

- [ ] **Step 5: Commit**

```bash
git add plugins/agents-md-management/README.md plugins/agents-md-management/skills/revise-agents-md/SKILL.md
git commit -m "feat(agents-md): session learning 반영 skill 추가"
```

---

### Task 3: Multi-agent documentation과 final verification

**Files:**
- Modify: `plugins/agents-md-management/README.md`
- Modify: `README.md`
- Modify: `CLAUDE.md:17-85`

**Interfaces:**
- Consumes: Tasks 1-2의 manifest, 두 Skill, quality criteria
- Produces: Claude Code/Codex/Antigravity 등록 문서, repository catalog, validated plugin release `1.0.0`

- [ ] **Step 1: Add runtime registration and reference semantics**

Add this section to `plugins/agents-md-management/README.md`:

```markdown
## Codex와 Antigravity

Canonical Skill source는 `skills/<skill-name>/`이다. Runtime별 복제본은 유지하지 않는다.

| Runtime | Repository scope | User/global scope | 호출 |
| :--- | :--- | :--- | :--- |
| Codex | `<repo>/.agents/skills/<skill-name>/` | `$HOME/.agents/skills/<skill-name>/` | `$<skill-name>` 또는 implicit |
| Antigravity | `<workspace>/.agents/skills/<skill-name>/` | `~/.gemini/config/skills/<skill-name>/` | Skill 이름 명시 또는 implicit |

다른 project에서 사용할 때 필요한 Skill directory를 위 location에 copy하거나 지원되는 link 방식으로 등록한다. Windows에서는 symlink 권한이 필요할 수 있으므로 copy 방식도 지원한다.

## Reference semantics

- Claude Code: root `CLAUDE.md`의 `@./.ai/RULES.md`를 native import한다.
- Antigravity/Gemini: root `GEMINI.md`의 `@./.ai/RULES.md`를 native import한다.
- Codex/AGENTS.md: native import가 없으므로 root `AGENTS.md`가 `.ai/RULES.md`를 먼저 읽도록 지시한다. 이 방식은 best-effort다.
- Nested vendor file은 common rule을 다시 import하지 않는다.

## Limitations

- Runtime별 자동 installer를 제공하지 않는다.
- `AGENTS.md`에서 `.ai/RULES.md` loading은 native import가 아니다.
- Background sync와 vendor file로의 common rule 복제를 수행하지 않는다.
```

- [ ] **Step 2: Update root project documentation**

In `CLAUDE.md`, add `plugins/agents-md-management` to the structure tree and add an `독립 Plugin` section that records:

```markdown
| Plugin | Version | Skills | 설치 |
| :--- | :--- | :--- | :--- |
| `agents-md-management` | 1.0.0 | `agents-md-management`, `revise-agents-md` | `agents-md-management@zzizily` |
```

If another independent plugin row exists, preserve it. Do not change the existing root Skill count `19` or root plugin version `1.8.4`.

Confirm `README.md` has the same plugin row and install name.

- [ ] **Step 3: Run manifest and file-boundary validation**

Run:

```powershell
$pluginRoot = (Resolve-Path 'plugins/agents-md-management').Path
$manifest = Get-Content -Raw 'plugins/agents-md-management/.claude-plugin/plugin.json' | ConvertFrom-Json
$marketplace = Get-Content -Raw '.claude-plugin/marketplace.json' | ConvertFrom-Json
$skillFiles = Get-ChildItem 'plugins/agents-md-management/skills' -Recurse -Filter SKILL.md

if ($manifest.name -ne 'agents-md-management' -or $manifest.version -ne '1.0.0') { throw 'plugin manifest invalid' }
$entry = $marketplace.plugins | Where-Object name -eq 'agents-md-management'
if ($entry.Count -ne 1 -or $entry.version -ne '1.0.0') { throw 'marketplace entry invalid' }
if ($skillFiles.Count -ne 2) { throw "Expected 2 skills, found $($skillFiles.Count)" }

foreach ($file in Get-ChildItem 'plugins/agents-md-management' -Recurse -File) {
  if (-not $file.FullName.StartsWith($pluginRoot)) { throw "External file boundary: $($file.FullName)" }
}
git diff --check
```

Expected: no output, exit code `0`.

- [ ] **Step 4: Run frontmatter and instruction-model checks**

Run:

```powershell
$expected = @{
  'agents-md-management' = 'plugins/agents-md-management/skills/agents-md-management/SKILL.md'
  'revise-agents-md' = 'plugins/agents-md-management/skills/revise-agents-md/SKILL.md'
}
foreach ($name in $expected.Keys) {
  $content = Get-Content -Raw $expected[$name]
  if ($content -notmatch "(?m)^name: $([regex]::Escape($name))$") { throw "Name mismatch: $name" }
  if ($content -notmatch '(?m)^description:') { throw "Missing description: $name" }
}

$all = Get-Content -Raw $expected.Values
foreach ($required in @('.ai/RULES.md', 'AGENTS.md', 'CLAUDE.md', 'GEMINI.md')) {
  if (($all -join "`n") -notmatch [regex]::Escape($required)) { throw "Missing instruction type: $required" }
}
rg -n "allowed-tools|!\x60|Bash\(" plugins/agents-md-management/skills
```

Expected: all assertions pass; `rg` returns no matches.

- [ ] **Step 5: Run scenario-oriented static checks**

Run:

```powershell
$audit = Get-Content -Raw 'plugins/agents-md-management/skills/agents-md-management/SKILL.md'
$revise = Get-Content -Raw 'plugins/agents-md-management/skills/revise-agents-md/SKILL.md'

foreach ($required in @('Root', 'Nested', 'reference', 'quality report', 'Symlink', 'Drift', 'Non-Git')) {
  if ($audit -notmatch [regex]::Escape($required)) { throw "Audit scenario missing: $required" }
}
foreach ($required in @('Common', 'vendor', 'subtree', 'Secret', 'Conflict', 'one-off')) {
  if ($revise -notmatch [regex]::Escape($required)) { throw "Revise scenario missing: $required" }
}
```

Expected: no output, exit code `0`.

- [ ] **Step 6: Validate with Claude and cross-review**

If Claude Code is installed:

```powershell
claude plugin validate .
```

Expected: marketplace and plugin validation pass. If the installed Claude version does not support this command, record the exact version/limitation and keep the JSON/frontmatter checks as the deterministic fallback.

Run `/zzizily:verify` against:

```text
plugins/agents-md-management
docs/superpowers/specs/2026-07-29-commit-and-agents-md-plugins-design.md
```

Required reviewers: Codex and Antigravity. Acceptance: Blocker `0`; fix any confirmed finding within this plugin scope and rerun focused validation.

- [ ] **Step 7: Final security scan and commit**

Run:

```powershell
if (Get-Command gitleaks -ErrorAction SilentlyContinue) {
  gitleaks detect --source plugins/agents-md-management --no-git --redact --exit-code 1
} else {
  rg -n "(?i)(api[_-]?key|access[_-]?token|password)\s*[:=]\s*[^\s`]+" plugins/agents-md-management
}
git status --short
git diff --check
```

Expected: no secret finding, no whitespace error, only Task 3 documentation or review fixes remain.

Commit:

```bash
git add README.md CLAUDE.md plugins/agents-md-management
git commit -m "docs(agents-md): multi-agent 사용법과 검증 기준 추가"
```

Final verification:

```powershell
git status --short
git log -3 --oneline
```

Expected: clean working tree and three focused commits for this plan.
