# commit-commands Plugin Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** GitHub, GitLab, Gitea에서 안전하게 commit·push·PR/MR·stale branch 정리를 수행하는 runtime-neutral Agent Skills plugin을 추가한다.

**Architecture:** `plugins/commit-commands`를 self-contained Claude/Codex marketplace plugin으로 만들고 `commit`, `commit-push-pr`, `clean-gone` Skill을 독립 제공한다. 두 runtime manifest는 canonical `skills/` 한 벌을 공유한다. Skill은 prompt-first 방식으로 작성하며 Claude Code, Codex, Antigravity의 native file/shell tool을 사용하고 mutation 전에 preview와 승인을 강제한다.

**Tech Stack:** Markdown Agent Skills, YAML frontmatter, Claude/Codex plugin JSON manifest, Git, GitHub CLI (`gh`), GitLab CLI (`glab`), Gitea CLI (`tea`), PowerShell validation

## Global Constraints

- Design source: `docs/superpowers/specs/2026-07-29-commit-and-agents-md-plugins-design.md`.
- Plugin name과 version은 `commit-commands` / `1.0.0`으로 고정한다.
- 기존 root `zzizily` plugin version `1.8.4`와 기존 19개 Skill을 변경하지 않는다.
- `SKILL.md`는 Claude Code, Codex, Antigravity 공통본 한 벌만 유지한다.
- Claude manifest는 `.claude-plugin/plugin.json`, Codex manifest는 `.codex-plugin/plugin.json`에 두고 둘 다 동일한 `./skills/`를 가리킨다.
- Claude marketplace는 `.claude-plugin/marketplace.json`, Codex marketplace는 `.agents/plugins/marketplace.json`에서 관리한다.
- Vendor 전용 `allowed-tools`, Claude shell interpolation, runtime 고유 tool 이름을 사용하지 않는다.
- 모든 mutation은 대상·명령·영향 preview와 명시적 승인 후 실행한다.
- `git add .`, `git add -A`, force push, rebase, `git branch -D`, 강제 worktree 제거를 실행하지 않는다.
- 현재 task와 무관한 변경 및 기존 staged 상태를 보존한다.
- 결과와 README는 한국어로 작성하고 IT 전문 용어는 영어를 사용한다.
- Upstream Apache License 2.0과 변경 attribution을 보존한다.
- File edit은 `apply_patch`로 수행하고, task마다 지정된 파일만 commit한다.

---

### Task 1: Plugin foundation과 `commit` Skill

**Files:**
- Create: `plugins/commit-commands/.claude-plugin/plugin.json`
- Create: `plugins/commit-commands/.codex-plugin/plugin.json`
- Create: `plugins/commit-commands/LICENSE`
- Create: `plugins/commit-commands/README.md`
- Create: `plugins/commit-commands/skills/commit/SKILL.md`
- Modify: `.claude-plugin/marketplace.json:6-13`
- Create: `.agents/plugins/marketplace.json`
- Modify: `README.md:5-33`

**Interfaces:**
- Consumes: 기존 marketplace name `zzizily`, root plugin entry `deuxksy`
- Produces: installable plugin `commit-commands@zzizily`, Skill name `commit`, version `1.0.0`

- [ ] **Step 1: Run the structural check and verify it fails**

Run:

```powershell
$paths = @(
  'plugins/commit-commands/.claude-plugin/plugin.json',
  'plugins/commit-commands/.codex-plugin/plugin.json',
  'plugins/commit-commands/skills/commit/SKILL.md'
)
if (($paths | Where-Object { -not (Test-Path -LiteralPath $_) }).Count -eq 0) {
  throw 'Expected commit-commands files to be absent before implementation'
}
```

Expected: command succeeds because at least one required file is absent.

- [ ] **Step 2: Create the plugin manifest**

Create `plugins/commit-commands/.claude-plugin/plugin.json` with:

```json
{
  "name": "commit-commands",
  "description": "Safe runtime-neutral Git commit, push, pull/merge request, and stale branch cleanup skills",
  "version": "1.0.0",
  "author": {
    "name": "Crong"
  },
  "skills": "./skills/"
}
```

- [ ] **Step 2a: Create the Codex plugin manifest**

Create `plugins/commit-commands/.codex-plugin/plugin.json` with the same name, version, description, author, and `skills: "./skills/"` as the Claude manifest. Add the Codex-required `interface` fields with `Productivity` category, a concise Korean-facing description, `Write` capability, and at most three task-specific default prompts.

- [ ] **Step 3: Add the marketplace entry without changing existing entries**

Add this object to `.claude-plugin/marketplace.json` `plugins` array. Preserve the `deuxksy` entry and any independently-added plugin entries.

```json
{
  "name": "commit-commands",
  "source": "./plugins/commit-commands",
  "description": "Safe runtime-neutral Git commit, PR/MR, and stale branch cleanup workflows",
  "version": "1.0.0"
}
```

Parse check:

```powershell
$marketplace = Get-Content -Raw '.claude-plugin/marketplace.json' | ConvertFrom-Json
$entry = $marketplace.plugins | Where-Object name -eq 'commit-commands'
if ($entry.Count -ne 1 -or $entry.version -ne '1.0.0' -or $entry.source -ne './plugins/commit-commands') {
  throw 'commit-commands marketplace entry is invalid'
}
```

Expected: no output, exit code `0`.

- [ ] **Step 3a: Create the Codex marketplace**

Create `.agents/plugins/marketplace.json` with marketplace name/display name `zzizily`. Add `commit-commands` using local source path `./plugins/commit-commands`, `AVAILABLE` installation policy, `ON_INSTALL` authentication policy, and `Productivity` category. Preserve any independently-added entries.

- [ ] **Step 4: Add Apache 2.0 license**

Create `plugins/commit-commands/LICENSE` by copying the exact Apache License 2.0 text from:

```text
https://raw.githubusercontent.com/anthropics/claude-plugins-official/main/plugins/commit-commands/LICENSE
```

Verify:

```powershell
$license = Get-Content -Raw 'plugins/commit-commands/LICENSE'
if ($license -notmatch 'Apache License' -or $license -notmatch 'Version 2.0') {
  throw 'Apache 2.0 license text is missing'
}
```

- [ ] **Step 5: Create the complete `commit` Skill**

Create `plugins/commit-commands/skills/commit/SKILL.md` with this frontmatter:

```yaml
---
name: commit
description: "Use when the user asks to commit task-related Git changes while preserving unrelated or pre-staged work."
---
```

The Markdown body must contain these exact sections and executable contract:

```markdown
# Commit

현재 task와 관련된 변경만 단일 atomic commit으로 만든다. 파일 내용을 수정하지 않는다.

## 1. Read-only preflight

1. Git repository root, current branch/HEAD, status를 확인한다.
2. staged, unstaged, untracked 변경을 각각 확인한다.
3. 최근 commit 10개의 style과 적용 가능한 project instruction을 확인한다.
4. 현재 task에 직접 관련된 파일만 `포함`으로 분류하고 나머지는 `제외`한다.
5. partial staging 또는 기존 index 상태를 안전하게 분리할 수 없으면 index를 변경하지 않고 범위를 질문한다.

## 2. Security check

1. Repository가 제공하는 gitleaks 또는 동등 scanner가 있으면 사용한다.
2. Scanner가 없으면 승인 대상의 tracked diff와 승인 대상 untracked 파일의 실제 content를 read-only로 검사한다. Binary 또는 읽을 수 없는 승인 대상 untracked 파일이면 중단하고, deterministic scanner 부재 한계를 preview에 명시한다.
3. Secret, token, credential, private key 의심 항목이 있으면 중단한다.

## 3. Preview and approval

다음을 한 번에 제시한다.

- 포함 파일과 선택 이유
- 제외 파일과 제외 이유
- security scan 결과와 한계
- exact staging command
- proposed commit message

사용자의 명시적 승인 전에는 stage 또는 commit하지 않는다.

## 4. Commit

1. 승인 직후 HEAD와 working tree 상태를 다시 확인한다.
2. 승인 시점과 달라졌으면 중단하고 preview를 갱신한다.
3. 포함 파일을 path별로 명시해 stage한다. Working tree 전체 shorthand는 사용하지 않는다.
4. staged diff가 승인 범위와 일치하는지 확인한다.
5. Project instruction, 최근 repository style, Conventional Commits 순으로 message 규칙을 적용한다. 별도 규칙이 없으면 type은 영어, subject는 한국어로 작성한다.
6. Empty commit을 만들지 않는다.
7. Commit 실패 시 index를 임의 rollback하지 않고 현재 상태를 보고한다.

## 5. Result

Commit SHA, message, 포함 파일, 남아 있는 staged/unstaged 변경을 보고한다.

## Safety

- Unrelated 변경을 stage하거나 commit하지 않는다.
- 기존 staged 변경을 자동 unstage하지 않는다.
- File content를 수정하지 않는다.
- Secret 의심 변경을 commit하지 않는다.
- 강제 또는 history rewrite Git option을 사용하지 않는다.

## Attribution

Adapted from Anthropic `commit-commands/commands/commit.md` under Apache License 2.0. Modified for runtime-neutral Agent Skills, selective staging, security checks, and approval gates.
```

- [ ] **Step 6: Create the initial plugin README**

Create `plugins/commit-commands/README.md` with:

```markdown
# commit-commands

안전한 Git commit, PR/MR, stale branch 정리를 제공하는 runtime-neutral Agent Skills plugin.

**Version:** 1.0.0

## Skills

| Skill | 설명 |
| :--- | :--- |
| `commit` | 현재 task 관련 변경만 preview·승인 후 commit |

## Claude Code

```bash
claude plugin install commit-commands@zzizily
```

호출: `/commit-commands:commit`

## Safety

- Read-only inspection 우선
- Mutation plan 승인 필수
- Unrelated/staged 변경 보존
- Force/history rewrite 금지

## Attribution

Adapted from Anthropic
[`commit-commands`](https://github.com/anthropics/claude-plugins-official/tree/main/plugins/commit-commands)
under Apache License 2.0. This version changes the original commands into runtime-neutral, approval-gated Agent Skills.
```

- [ ] **Step 7: Add the independent plugin catalog to root README**

Immediately before `## 스킬 카탈로그 (19)`, create `## 독립 Plugin` if absent and add the `commit-commands` row. If another plan already created the section, preserve its rows and append only the missing row.

```markdown
## 독립 Plugin

기존 `zzizily`와 별도로 설치하는 domain plugin.

| Plugin | Version | Skills |
| :--- | :--- | :--- |
| `commit-commands` | 1.0.0 | `commit`, `commit-push-pr`, `clean-gone` |
```

Add this install command to the Quick Start code block without changing the existing `deuxksy@zzizily` command:

```bash
claude plugin install commit-commands@zzizily
```

- [ ] **Step 8: Run focused validation**

Run:

```powershell
$manifest = Get-Content -Raw 'plugins/commit-commands/.claude-plugin/plugin.json' | ConvertFrom-Json
$marketplace = Get-Content -Raw '.claude-plugin/marketplace.json' | ConvertFrom-Json
$skill = Get-Content -Raw 'plugins/commit-commands/skills/commit/SKILL.md'
if ($manifest.name -ne 'commit-commands' -or $manifest.version -ne '1.0.0') { throw 'manifest mismatch' }
if (($marketplace.plugins | Where-Object name -eq 'commit-commands').Count -ne 1) { throw 'marketplace mismatch' }
if ($skill -notmatch '(?m)^name: commit$' -or $skill -notmatch '(?m)^description:') { throw 'frontmatter mismatch' }
$untrackedFixture = [PSCustomObject]@{ Path = 'notes.txt'; Content = 'access_token = token_like_value' }
if ($untrackedFixture.Path -match '(?i)(\.env|\.pem|credential|token)' -or $untrackedFixture.Content -notmatch '(?i)(api[_-]?key|access[_-]?token|password)\s*[:=]\s*[^\s`]+') { throw 'invalid untracked fixture' }
if ($skill -notmatch '승인 대상 untracked 파일의 실제 content를 read-only로 검사한다\.' -or $skill -notmatch 'Binary 또는 읽을 수 없는 승인 대상 untracked 파일이면 중단하고' -or $skill -notmatch 'deterministic scanner 부재 한계를 preview에 명시한다\.') { throw 'untracked token-like content fallback mismatch' }
git diff --check
```

Expected: no output from assertions or `git diff --check`, exit code `0`.

- [ ] **Step 9: Security review and commit**

Run:

```powershell
rg -n "(?i)(api[_-]?key|access[_-]?token|password)\s*[:=]\s*[^\s`]+" plugins/commit-commands README.md .claude-plugin/marketplace.json
git status --short
```

Expected: secret assignment scan returns no findings; status contains only Task 1 files.

Commit:

```bash
git add .claude-plugin/marketplace.json README.md plugins/commit-commands/.claude-plugin/plugin.json plugins/commit-commands/LICENSE plugins/commit-commands/README.md plugins/commit-commands/skills/commit/SKILL.md
git commit -m "feat(commit): 안전한 commit skill 추가"
```

---

### Task 2: Provider-neutral `commit-push-pr` Skill

**Files:**
- Create: `plugins/commit-commands/skills/commit-push-pr/SKILL.md`
- Create: `plugins/commit-commands/skills/commit-push-pr/references/providers.md`
- Modify: `plugins/commit-commands/README.md`

**Interfaces:**
- Consumes: Task 1의 `commit` safety contract, Git remote URL과 current branch upstream
- Produces: Skill name `commit-push-pr`, provider mapping `GitHub→gh`, `GitLab→glab`, `Gitea→tea`

- [ ] **Step 1: Run the file-existence check and verify it fails**

Run:

```powershell
if (Test-Path 'plugins/commit-commands/skills/commit-push-pr/SKILL.md') {
  throw 'Expected commit-push-pr skill to be absent'
}
```

Expected: exit code `0`.

- [ ] **Step 2: Create provider reference**

Create `plugins/commit-commands/skills/commit-push-pr/references/providers.md` with:

```markdown
# Git Provider Adapters

## Provider detection

1. Current branch upstream remote를 우선한다.
2. Upstream이 없고 remote가 하나면 그 remote를 사용한다.
3. Remote가 여러 개면 mutation 전에 사용자에게 선택을 요청한다.
4. SSH와 HTTPS remote URL의 hostname을 정규화한다.
5. `github.com` 또는 GitHub Enterprise로 확인되면 GitHub, GitLab host로 확인되면 GitLab, Gitea API/banner 또는 configured `tea` login과 일치하면 Gitea다.
6. Self-hosted provider를 확정할 수 없으면 unknown으로 처리한다.

## Review request adapters

| Provider | Probe | Create |
| :--- | :--- | :--- |
| GitHub | `gh auth status` | `gh pr create` |
| GitLab | `glab auth status` | `glab mr create` |
| Gitea | `tea login list` | `tea pr create` (`pulls` alias 허용) |

## Default branch

1. `<remote>/HEAD`
2. Provider CLI가 반환하는 default branch
3. 실제 존재하는 `main`
4. 실제 존재하는 `master`
5. 결정 불가 시 중단

## Fallback

- Unknown provider 또는 CLI/인증 부재 시 normal push까지만 수행한다.
- 수동 PR/MR 생성 명령 또는 compare URL을 안내한다.
- API를 직접 호출하거나 credential을 요청·출력하지 않는다.
```

- [ ] **Step 3: Create the complete `commit-push-pr` Skill**

Create `plugins/commit-commands/skills/commit-push-pr/SKILL.md` with this frontmatter:

```yaml
---
name: commit-push-pr
description: "Use when the user asks to commit, push, and open a GitHub PR, GitLab MR, or Gitea PR."
---
```

The body must contain:

```markdown
# Commit, Push, and Open Review Request

Commit → normal push → PR/MR 생성 workflow. 세 단계 전체의 mutation plan을 먼저 승인받는다.

## 1. Preflight

1. Git root, HEAD, current branch, status, upstream, remote URL을 확인한다.
2. 변경이 있으면 `commit` Skill과 동일하게 task 관련 파일만 분류하고 security 검사한다.
3. `references/providers.md`에 따라 provider, remote, default branch, CLI/인증 상태를 확인한다.
4. Detached HEAD, 선택 불가능한 remote, 결정 불가능한 default branch에서는 중단한다.
5. Current branch가 default branch이면 새 feature branch 이름을 제안한다.

## 2. Preview and approval

다음을 한 번에 제시한다.

- 포함·제외 파일과 commit message
- 생성할 branch와 base branch
- exact commit, normal push, PR/MR 명령
- provider와 authentication 상태
- CLI 부재 시 fallback

승인 전에는 branch 생성, stage, commit, push, PR/MR 생성을 하지 않는다.

## 3. Execute

1. 승인 직후 HEAD, status, remote를 다시 확인한다. Drift가 있으면 중단한다.
2. 필요한 경우 승인된 이름으로 branch를 생성한다.
3. 변경이 있으면 승인된 범위만 commit한다.
4. 승인된 remote/current branch로 normal push한다.
5. Push 성공 후에만 provider CLI로 PR/MR을 생성한다.
6. PR/MR title, summary, test plan은 전체 branch diff와 repository template을 반영한다. 별도 언어 규칙이 없으면 한국어로 작성한다.

## 4. Failure handling

- Branch 또는 commit 실패: 이후 단계 중단.
- Push 실패: PR/MR 생성 금지.
- PR/MR 실패: commit·push를 rollback하지 않고 재시도 방법 안내.
- Unknown provider 또는 CLI/인증 부재: push까지만 수행하고 수동 생성 방법 안내.

## Safety

- Force push, rebase, branch overwrite를 하지 않는다.
- Provider API를 직접 호출하지 않는다.
- Credential을 요청하거나 출력하지 않는다.
- 승인 범위를 벗어난 mutation을 하지 않는다.

## Attribution

Adapted from Anthropic `commit-commands/commands/commit-push-pr.md` under Apache License 2.0. Modified for runtime-neutral skills, GitHub/GitLab/Gitea adapters, selective staging, and approval gates.
```

- [ ] **Step 4: Update plugin README**

Add the Skill row:

```markdown
| `commit-push-pr` | 관련 변경 commit → normal push → GitHub PR/GitLab MR/Gitea PR 생성 |
```

Add provider requirements:

```markdown
## Provider CLI

| Provider | CLI | Review request |
| :--- | :--- | :--- |
| GitHub | `gh` | Pull Request |
| GitLab | `glab` | Merge Request |
| Gitea | `tea` | Pull Request |

CLI가 없거나 인증되지 않았으면 push까지만 수행하고 수동 생성 절차를 안내한다.
```

Add Claude invocation:

```text
/commit-commands:commit-push-pr
```

- [ ] **Step 5: Validate provider coverage and safety**

Run:

```powershell
$skill = Get-Content -Raw 'plugins/commit-commands/skills/commit-push-pr/SKILL.md'
$providers = Get-Content -Raw 'plugins/commit-commands/skills/commit-push-pr/references/providers.md'
foreach ($required in @('GitHub', 'GitLab', 'Gitea', 'gh pr create', 'glab mr create', 'tea pr create')) {
  if (($skill + $providers) -notmatch [regex]::Escape($required)) { throw "Missing provider contract: $required" }
}
foreach ($required in @('승인', 'Push 실패', 'rollback')) {
  if ($skill -notmatch $required) { throw "Missing safety contract: $required" }
}
git diff --check
```

Expected: no output, exit code `0`.

- [ ] **Step 6: Commit**

```bash
git add plugins/commit-commands/README.md plugins/commit-commands/skills/commit-push-pr/SKILL.md plugins/commit-commands/skills/commit-push-pr/references/providers.md
git commit -m "feat(commit): provider-neutral PR workflow 추가"
```

---

### Task 3: Safe `clean-gone` Skill

**Files:**
- Create: `plugins/commit-commands/skills/clean-gone/SKILL.md`
- Modify: `plugins/commit-commands/README.md`

**Interfaces:**
- Consumes: local branch/upstream/worktree metadata
- Produces: Skill name `clean-gone`, safe removal contract limited to merged branches and clean worktrees

- [ ] **Step 1: Run the file-existence check and verify it fails**

Run:

```powershell
if (Test-Path 'plugins/commit-commands/skills/clean-gone/SKILL.md') {
  throw 'Expected clean-gone skill to be absent'
}
```

Expected: exit code `0`.

- [ ] **Step 2: Create the complete `clean-gone` Skill**

Create `plugins/commit-commands/skills/clean-gone/SKILL.md` with this frontmatter:

```yaml
---
name: clean-gone
description: "Use when the user asks to clean stale or gone Git branches without force deletion."
---
```

The body must contain:

```markdown
# Clean Gone Branches Safely

Remote에서 사라진 local branch를 강제 삭제 없이 정리한다.

## 1. Read-only discovery

1. Git root, current branch, remote, remote-tracking refs를 확인한다.
2. Local branch의 upstream 상태는 machine-readable ref 정보 또는 `git branch -vv`로 확인한다.
3. 모든 worktree의 path, branch, lock, dirty 상태를 확인한다.
4. Remote ref 최신화가 필요하면 prune dry-run 결과와 실제 prune 계획을 분리한다.

## 2. Safety classification

각 후보를 다음 중 하나로 분류한다.

- 삭제 가능: upstream gone, current branch 아님, merged, worktree 없음 또는 clean·unlocked worktree.
- 제외: 미병합 commit, current branch, dirty/locked worktree, SHA 확인 실패.

Branch별 SHA와 제외 사유를 기록한다.

## 3. Preview and approval

다음을 제시한다.

- Remote prune 필요 여부와 exact command
- 제거할 clean worktree path
- 삭제할 merged local branch
- 제외 대상과 이유

승인 전에는 prune, worktree 제거, branch 삭제를 하지 않는다.

## 4. Execute

1. 승인 직후 branch SHA와 worktree 상태를 다시 확인한다.
2. Drift가 있으면 전체 실행을 중단한다.
3. 승인된 경우에만 remote refs를 prune한다.
4. Clean·unlocked worktree를 일반 remove로 제거한다.
5. Merged branch를 safe delete로 제거한다.
6. 첫 실패 시 중단하고 이미 제거된 대상과 남은 대상을 구분해 보고한다.

## Safety

- Force option을 사용하지 않는다.
- Dirty, locked, current worktree를 제거하지 않는다.
- 미병합 branch를 삭제하지 않는다.
- 안전 검사를 우회하는 대체 명령을 실행하지 않는다.

## Attribution

Adapted from Anthropic `commit-commands/commands/clean_gone.md` under Apache License 2.0. Modified to remove force deletion, add merge/worktree checks, state-drift detection, preview, and approval.
```

- [ ] **Step 3: Update plugin README**

Add the Skill row:

```markdown
| `clean-gone` | merged·clean `[gone]` branch/worktree만 preview·승인 후 안전하게 제거 |
```

Add Claude invocation:

```text
/commit-commands:clean-gone
```

Add this explicit limitation:

```markdown
`clean-gone`은 미병합 branch, dirty/locked worktree, current branch를 제거하지 않으며 force option을 제공하지 않는다.
```

- [ ] **Step 4: Validate destructive-command exclusions**

Run:

```powershell
$skill = Get-Content -Raw 'plugins/commit-commands/skills/clean-gone/SKILL.md'
foreach ($required in @('미병합', 'current branch', 'dirty', 'locked', '승인', 'Drift', '첫 실패')) {
  if ($skill -notmatch [regex]::Escape($required)) { throw "Missing clean-gone contract: $required" }
}
$forbidden = @('branch ' + '-D', 'worktree remove ' + '--force')
foreach ($pattern in $forbidden) {
  if ($skill -match [regex]::Escape($pattern)) { throw "Forbidden command found: $pattern" }
}
git diff --check
```

Expected: no assertion output, exit code `0`.

- [ ] **Step 5: Commit**

```bash
git add plugins/commit-commands/README.md plugins/commit-commands/skills/clean-gone/SKILL.md
git commit -m "feat(commit): 안전한 clean-gone skill 추가"
```

---

### Task 4: Multi-agent documentation과 final verification

**Files:**
- Modify: `plugins/commit-commands/README.md`
- Modify: `README.md`
- Modify: `CLAUDE.md:17-85`

**Interfaces:**
- Consumes: Tasks 1-3의 manifest, 3개 Skill, provider reference
- Produces: Claude Code/Codex/Antigravity 등록 문서, repository catalog, validated plugin release `1.0.0`

- [ ] **Step 1: Add runtime registration documentation**

Add this section to `plugins/commit-commands/README.md`:

```markdown
## Codex와 Antigravity

Canonical Skill source는 `skills/<skill-name>/`이다. Runtime별 복제본은 유지하지 않는다.

| Runtime | Repository scope | User/global scope | 호출 |
| :--- | :--- | :--- | :--- |
| Codex | `<repo>/.agents/skills/<skill-name>/` | `$HOME/.agents/skills/<skill-name>/` | `$<skill-name>` 또는 implicit |
| Antigravity | `<workspace>/.agents/skills/<skill-name>/` | `~/.gemini/config/skills/<skill-name>/` | Skill 이름 명시 또는 implicit |

다른 project에서 사용할 때 필요한 Skill directory를 위 location에 copy하거나 지원되는 link 방식으로 등록한다. Windows에서는 symlink 권한이 필요할 수 있으므로 copy 방식도 지원한다.

## Requirements

- Git
- Review request 생성 시 provider에 맞는 authenticated CLI: `gh`, `glab`, 또는 `tea`
- Secret scan 강화 시 gitleaks 또는 repository가 지정한 scanner

## Limitations

- Runtime별 자동 installer를 제공하지 않는다.
- Provider CLI가 없으면 push까지만 수행한다.
- 실제 remote mutation integration test는 포함하지 않는다.
```

- [ ] **Step 2: Update root project documentation**

In `CLAUDE.md`, add `plugins/commit-commands` to the structure tree and add an `독립 Plugin` section that records:

```markdown
| Plugin | Version | Skills | 설치 |
| :--- | :--- | :--- | :--- |
| `commit-commands` | 1.0.0 | `commit`, `commit-push-pr`, `clean-gone` | `commit-commands@zzizily` |
```

If another independent plugin row exists, preserve it. Do not change the existing root Skill count `19` or root plugin version `1.8.4`.

Confirm `README.md` has the same plugin row and install name.

- [ ] **Step 3: Run manifest and file-boundary validation**

Run:

```powershell
$pluginRoot = (Resolve-Path 'plugins/commit-commands').Path
$manifest = Get-Content -Raw 'plugins/commit-commands/.claude-plugin/plugin.json' | ConvertFrom-Json
$marketplace = Get-Content -Raw '.claude-plugin/marketplace.json' | ConvertFrom-Json
$skillFiles = Get-ChildItem 'plugins/commit-commands/skills' -Recurse -Filter SKILL.md

if ($manifest.name -ne 'commit-commands' -or $manifest.version -ne '1.0.0') { throw 'plugin manifest invalid' }
$entry = $marketplace.plugins | Where-Object name -eq 'commit-commands'
if ($entry.Count -ne 1 -or $entry.version -ne '1.0.0') { throw 'marketplace entry invalid' }
if ($skillFiles.Count -ne 3) { throw "Expected 3 skills, found $($skillFiles.Count)" }

foreach ($file in Get-ChildItem 'plugins/commit-commands' -Recurse -File) {
  if (-not $file.FullName.StartsWith($pluginRoot)) { throw "External file boundary: $($file.FullName)" }
}
git diff --check
```

Expected: no output, exit code `0`.

- [ ] **Step 4: Run frontmatter and runtime-neutral checks**

Run:

```powershell
$expected = @{
  'commit' = 'plugins/commit-commands/skills/commit/SKILL.md'
  'commit-push-pr' = 'plugins/commit-commands/skills/commit-push-pr/SKILL.md'
  'clean-gone' = 'plugins/commit-commands/skills/clean-gone/SKILL.md'
}
foreach ($name in $expected.Keys) {
  $content = Get-Content -Raw $expected[$name]
  if ($content -notmatch "(?m)^name: $([regex]::Escape($name))$") { throw "Name mismatch: $name" }
  if ($content -notmatch '(?m)^description:') { throw "Missing description: $name" }
}
rg -n "allowed-tools|!\x60git|Bash\(" plugins/commit-commands/skills
```

Expected: all assertions pass; `rg` returns no matches.

- [ ] **Step 5: Validate with Claude and cross-review**

If Claude Code is installed:

```powershell
claude plugin validate .
```

Expected: marketplace and plugin validation pass. If the installed Claude version does not support this command, record the exact version/limitation and keep the JSON/frontmatter checks as the deterministic fallback.

Run `/zzizily:verify` against:

```text
plugins/commit-commands
docs/superpowers/specs/2026-07-29-commit-and-agents-md-plugins-design.md
```

Required reviewers: Codex and Antigravity. Acceptance: Blocker `0`; fix any confirmed finding within this plugin scope and rerun focused validation.

- [ ] **Step 6: Final security scan and commit**

Run:

```powershell
if (Get-Command gitleaks -ErrorAction SilentlyContinue) {
  gitleaks detect --source plugins/commit-commands --no-git --redact --exit-code 1
} else {
  rg -n "(?i)(api[_-]?key|access[_-]?token|password)\s*[:=]\s*[^\s`]+" plugins/commit-commands
}
git status --short
git diff --check
```

Expected: no secret finding, no whitespace error, only Task 4 documentation or review fixes remain.

Commit:

```bash
git add README.md CLAUDE.md plugins/commit-commands
git commit -m "docs(commit): multi-agent 사용법과 검증 기준 추가"
```

Final verification:

```powershell
git status --short
git log -4 --oneline
```

Expected: clean working tree and four focused commits for this plan.
