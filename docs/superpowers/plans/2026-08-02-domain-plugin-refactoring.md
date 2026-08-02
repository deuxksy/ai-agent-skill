# 9 Domain-Focused Plugins Refactoring Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 19개 루트 스킬을 6개 신규 도메인 플러그인(`security-audit`, `infra-provisioning`, `trackers-automation`, `agent-dev-deploy`, `session-workflow`, `content-l10n`)으로 `git mv` 이관하고, `.claude-plugin/marketplace.json` 및 문서(`README.md`, `CLAUDE.md`)를 단일 통합 버전 `1.9.1`로 갱신하여 커밋/푸시한다.

**Architecture:** 루트 `skills/` 디렉토리를 정리하고 6개 신규 도메인 플러그인을 `plugins/` 하위에 배치한다. 기존 3개 독립 플러그인과 함께 총 9개 도메인 플러그인으로 마켓플레이스를 재구성하며, 전 플러그인이 `1.9.1` 단일 버전을 공유한다.

**Tech Stack:** Git (`git mv`), JSON manifests (`plugin.json`, `marketplace.json`), Markdown docs (`README.md`, `CLAUDE.md`).

## Global Constraints

- 모든 9개 독립 플러그인 버전은 `1.9.1`로 통일한다.
- 19개 스킬 이동 시 Git 이력을 보존하기 위해 반드시 `git mv` 명령을 사용한다.
- 모든 JSON 파일의 구문 유효성(Valid JSON)을 유지한다.
- 사용자 승인 전 임의 파일 롤백이나 강제 Git 커밋을 하지 않는다.

---

### Task 1: 6개 신규 도메인 플러그인 매니페스트 & README 생성

**Files:**
- Create: `plugins/security-audit/.claude-plugin/plugin.json`
- Create: `plugins/security-audit/.codex-plugin/plugin.json`
- Create: `plugins/security-audit/README.md`
- Create: `plugins/infra-provisioning/.claude-plugin/plugin.json`
- Create: `plugins/infra-provisioning/.codex-plugin/plugin.json`
- Create: `plugins/infra-provisioning/README.md`
- Create: `plugins/trackers-automation/.claude-plugin/plugin.json`
- Create: `plugins/trackers-automation/.codex-plugin/plugin.json`
- Create: `plugins/trackers-automation/README.md`
- Create: `plugins/agent-dev-deploy/.claude-plugin/plugin.json`
- Create: `plugins/agent-dev-deploy/.codex-plugin/plugin.json`
- Create: `plugins/agent-dev-deploy/README.md`
- Create: `plugins/session-workflow/.claude-plugin/plugin.json`
- Create: `plugins/session-workflow/.codex-plugin/plugin.json`
- Create: `plugins/session-workflow/README.md`
- Create: `plugins/content-l10n/.claude-plugin/plugin.json`
- Create: `plugins/content-l10n/.codex-plugin/plugin.json`
- Create: `plugins/content-l10n/README.md`

**Interfaces:**
- Consumes: Design spec (`docs/superpowers/specs/2026-08-02-domain-plugin-refactoring-design.md`)
- Produces: 6 new plugin directory layouts with `.claude-plugin/plugin.json`, `.codex-plugin/plugin.json`, and `README.md`

- [ ] **Step 1: 6개 도메인 디렉토리 및 매니페스트 생성**

Create all 18 manifest files and READMEs under `plugins/security-audit`, `plugins/infra-provisioning`, `plugins/trackers-automation`, `plugins/agent-dev-deploy`, `plugins/session-workflow`, and `plugins/content-l10n`.

- [ ] **Step 2: JSON 구문 파싱 검증**

Run: `node -e "['security-audit','infra-provisioning','trackers-automation','agent-dev-deploy','session-workflow','content-l10n'].forEach(p => { JSON.parse(require('fs').readFileSync('plugins/' + p + '/.claude-plugin/plugin.json')); JSON.parse(require('fs').readFileSync('plugins/' + p + '/.codex-plugin/plugin.json')); })"`
Expected: Clean exit (code 0) without JSON syntax error.

- [ ] **Step 3: Commit**

Run: `git add plugins/ && git commit -m "feat(plugins): 6개 신규 도메인 플러그인 매니페스트 및 README 생성 (v1.9.1)"`

---

### Task 2: 19개 스킬 `git mv` 이동 및 루트 `skills/` 정리

**Files:**
- Move: `skills/code-audit`, `skills/system-audit`, `skills/backdoor-investigation`, `skills/backdoor-remediation` -> `plugins/security-audit/skills/`
- Move: `skills/setup`, `skills/system-upgrade`, `skills/proxmox-vm-create`, `skills/openwrt-initd` -> `plugins/infra-provisioning/skills/`
- Move: `skills/calendar-sync`, `skills/exchange-rate-tracker`, `skills/hot-game-deals-n-news` -> `plugins/trackers-automation/skills/`
- Move: `skills/agents`, `skills/verify`, `skills/deploy-android-wifi` -> `plugins/agent-dev-deploy/skills/`
- Move: `skills/handoff`, `skills/resume` -> `plugins/session-workflow/skills/`
- Move: `skills/optimize-images-4k`, `skills/korean-translation-verify`, `skills/product-planning-dr-pipeline` -> `plugins/content-l10n/skills/`
- Delete: Root `skills/` directory after all moves

**Interfaces:**
- Consumes: Task 1 directory structure
- Produces: All 19 skills migrated into domain plugins under `plugins/<domain>/skills/` with git history preserved

- [ ] **Step 1: `git mv` 명령으로 19개 스킬 폴더 안전 이동**

Execute `git mv` for each skill into its target domain plugin's `skills/` directory.

- [ ] **Step 2: `git status` 추적 상태 검증**

Run: `git status`
Expected: 19 directories reported as `renamed: skills/<name> -> plugins/<domain>/skills/<name>`.

- [ ] **Step 3: Commit**

Run: `git commit -m "refactor(skills): 19개 메인 스킬을 6개 도메인 플러그인으로 git mv 이관"`

---

### Task 3: `.claude-plugin/marketplace.json` 9개 도메인 등록

**Files:**
- Modify: `.claude-plugin/marketplace.json`

**Interfaces:**
- Consumes: Task 1 and Task 2 plugin paths
- Produces: Updated `marketplace.json` registering all 9 domain plugins under `plugins` array

- [ ] **Step 1: `marketplace.json` 업데이트**

Update `.claude-plugin/marketplace.json` to list all 9 domain plugins (`security-audit`, `infra-provisioning`, `trackers-automation`, `agent-dev-deploy`, `session-workflow`, `content-l10n`, `commit-commands`, `agents-md-management`, `readme-md-management`) with `version: "1.9.1"`.

- [ ] **Step 2: `marketplace.json` 구문 검증**

Run: `node -e "JSON.parse(require('fs').readFileSync('.claude-plugin/marketplace.json'))"`
Expected: Clean exit (code 0).

- [ ] **Step 3: Commit**

Run: `git add .claude-plugin/marketplace.json && git commit -m "feat(marketplace): 9개 독립 도메인 플러그인 마켓플레이스 등록 (v1.9.1)"`

---

### Task 4: 루트 `README.md` & `CLAUDE.md` 문서 갱신

**Files:**
- Modify: `README.md`
- Modify: `CLAUDE.md`

**Interfaces:**
- Consumes: Task 3 marketplace structure
- Produces: Updated `README.md` and `CLAUDE.md` reflecting 9 domain plugins, installation guides, and full 26-skill catalog table.

- [ ] **Step 1: `README.md` 및 `CLAUDE.md` 테이블 갱신**

Update plugin catalog tables and installation commands in `README.md` and `CLAUDE.md` to document the 9 domain plugins.

- [ ] **Step 2: 마크다운 링크 검증**

Run: `node -e "const fs = require('fs'); const content = fs.readFileSync('README.md', 'utf8'); console.log('README length:', content.length)"`
Expected: README updated cleanly without missing sections.

- [ ] **Step 3: Commit**

Run: `git add README.md CLAUDE.md && git commit -m "docs(readme): 9개 도메인 플러그인 설치 가이드 및 카탈로그 문서 갱신"`

---

### Task 5: 로컬 환경 동기화 & 원격 저장소 푸시 (`origin/main`)

**Files:**
- Sync: `~/.gemini/config/plugins/`

**Interfaces:**
- Consumes: Task 1~4 commits
- Produces: Pushed `origin/main` commit and synchronized local `~/.gemini/config/plugins/` environment

- [ ] **Step 1: 로컬 `~/.gemini/config/plugins/` 동기화**

Copy updated plugin files to `~/.gemini/config/plugins/` so current agent runtime picks up all 9 domain plugins.

- [ ] **Step 2: 원격 저장소 푸시**

Run: `git push origin main`
Expected: `origin/main` updated successfully.

- [ ] **Step 3: 최종 검증**

Run: `git status`
Expected: `working tree clean` (except untracked `.omx/`).
