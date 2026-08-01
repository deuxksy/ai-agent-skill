# `readme-md-management` Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Create `plugins/readme-md-management` containing `readme-md-management` and `revise-readme-md` skills to audit, generate, and update `README.md` and repository document hierarchy according to Diátaxis framework, OKF standards, 100~500 character human summary constraints, and orphan document detection.

**Architecture:** A runtime-neutral plugin structure following `agents-md-management` patterns. Consists of a manifest for Claude/Codex/AGY runtime discovery, reference specs (`diataxis-spec.md`, `okf-spec.md`), a main audit/indexing skill (`readme-md-management`), and a lightweight incremental revision skill (`revise-readme-md`).

**Tech Stack:** Markdown (`SKILL.md`, `plugin.json`), Shell/Git read-only commands for inspection and audit.

## Global Constraints

- **Plugin Directory:** `plugins/readme-md-management/`
- **Summary Length:** Project summary in `README.md` MUST be 100~500 characters.
- **Diátaxis Quadrants:** Tutorials, How-To Guides, Reference, Explanation.
- **Sub-Hub Document Links:** Root `README.md` points to `docs/README.md` and `docs/okf/README.md`.
- **Exclusion Rules:** `docs/superpowers/`, `.git`, `.ai/`, `.claude/`, `.gemini/`, `node_modules/` MUST be excluded from README document indexing and orphan page detection.
- **Safety:** Approval gate required before modifying files. Surgical edits to `README.md` only.

---

### Task 1: Plugin Scaffold & Manifests

**Files:**
- Create: `plugins/readme-md-management/README.md`
- Create: `plugins/readme-md-management/.claude-plugin/plugin.json`
- Create: `plugins/readme-md-management/.codex-plugin/plugin.json`

**Interfaces:**
- Consumes: N/A
- Produces: Marketplace plugin metadata for Claude Code and Codex / Antigravity plugins.

- [ ] **Step 1: Create `plugins/readme-md-management/README.md`**

```markdown
# Readme Markdown Management Plugin

Runtime-neutral AI Agent skills for auditing, structuring, and updating repository `README.md` files and documentation hierarchy based on the Diátaxis framework, OKF standards, and orphan document detection.

## Skills

- `readme-md-management`: Audits `README.md`, verifies 100~500 char summary, builds Diátaxis document indexes, and detects orphan docs.
- `revise-readme-md`: Lightly updates `README.md` index and summary when new documentation or features are added.
```

- [ ] **Step 2: Create `.claude-plugin/plugin.json`**

```json
{
  "name": "readme-md-management",
  "description": "Audit and revise README.md, document hubs (docs/README.md, docs/okf/README.md), Diátaxis indexes, and orphan docs",
  "version": "1.0.0"
}
```

- [ ] **Step 3: Create `.codex-plugin/plugin.json`**

```json
{
  "name": "readme-md-management",
  "description": "Audit and revise README.md, document hubs, Diátaxis indexes, and orphan docs",
  "version": "1.0.0"
}
```

- [ ] **Step 4: Verify files created**

Run: `ls -la plugins/readme-md-management/ plugins/readme-md-management/.claude-plugin/ plugins/readme-md-management/.codex-plugin/`
Expected: Files exist with non-zero size.

- [ ] **Step 5: Commit**

```bash
git add plugins/readme-md-management/
git commit -m "feat(plugin): scaffold readme-md-management plugin manifests"
```

---

### Task 2: Reference Documentation Specs (`diataxis-spec.md` & `okf-spec.md`)

**Files:**
- Create: `plugins/readme-md-management/skills/readme-md-management/references/diataxis-spec.md`
- Create: `plugins/readme-md-management/skills/readme-md-management/references/okf-spec.md`

**Interfaces:**
- Consumes: Diátaxis (https://diataxis.fr/) framework principles and OKF documentation standards.
- Produces: Reference specifications loaded by `readme-md-management/SKILL.md` during document audit.

- [ ] **Step 1: Write `diataxis-spec.md`**

```markdown
# Diátaxis Documentation Framework Reference

This reference defines the 4-quadrant classification rules for repository documentation.

## 1. Tutorials (학습/입문)
- **Goal:** Help new users learn by doing.
- **Target Files:** `getting-started.md`, `quickstart.md`, `tutorial-*.md`, `walkthrough.md`.
- **Characteristics:** Step-by-step beginner lessons, non-technical, outcome-oriented.

## 2. How-To Guides (실무/작업 가이드)
- **Goal:** Help experienced users solve specific practical tasks.
- **Target Files:** `how-to-*.md`, `deployment.md`, `contributing.md`, `troubleshooting.md`, `migration.md`.
- **Characteristics:** Goal-oriented, problem-solving procedures.

## 3. Reference (참조/명세)
- **Goal:** Provide technical specifications and reference material.
- **Target Files:** `docs/README.md`, `docs/okf/README.md`, `api-*.md`, `cli.md`, `spec.md`, `configuration.md`.
- **Characteristics:** Information-oriented, structured, accurate.

## 4. Explanation (원리/아키텍처)
- **Goal:** Explain concepts, background decisions, and architecture.
- **Target Files:** `architecture.md`, `design.md`, `concepts.md`, `philosophy.md`.
- **Characteristics:** Understanding-oriented, contextual, architectural decisions.

## Exclusions
- `docs/superpowers/`: Internal agent specs and plans are EXCLUDED from human Diátaxis indexes.
- Configuration and dotfiles (`.git/`, `.claude/`, `.ai/`, `.gemini/`): EXCLUDED.
```

- [ ] **Step 2: Write `okf-spec.md`**

```markdown
# OKF (Open Knowledge Framework) Reference

This specification defines how `docs/okf/` documentation hub is audited.

## 1. Hub Responsibility
- `docs/okf/README.md` is the Single Source of Truth for OKF documents under `docs/okf/`.
- Root `README.md` links to `docs/okf/README.md` under the Reference quadrant of the Diátaxis index.
- Individual OKF specification files under `docs/okf/*.md` are indexed within `docs/okf/README.md`, NOT listed directly in root `README.md`.

## 2. Orphan Audit Integration
- An OKF document inside `docs/okf/` is considered healthy if it is indexed in `docs/okf/README.md`.
- If an OKF document is unlinked in `docs/okf/README.md`, it is flagged as an Orphan Document during the `readme-md-management` audit.
```

- [ ] **Step 3: Verify reference files**

Run: `ls -la plugins/readme-md-management/skills/readme-md-management/references/`
Expected: `diataxis-spec.md` and `okf-spec.md` exist.

- [ ] **Step 4: Commit**

```bash
git add plugins/readme-md-management/skills/readme-md-management/references/
git commit -m "docs(readme-md): add Diataxis and OKF reference specifications"
```

---

### Task 3: Main Skill (`readme-md-management/SKILL.md`)

**Files:**
- Create: `plugins/readme-md-management/skills/readme-md-management/SKILL.md`

**Interfaces:**
- Consumes: `references/diataxis-spec.md`, `references/okf-spec.md`
- Produces: Skill instructions for auditing `README.md`, enforcing 100~500 char summary, building Diátaxis index, checking stale links, and flagging orphan docs.

- [ ] **Step 1: Write `readme-md-management/SKILL.md`**

```markdown
---
name: readme-md-management
description: "Use when repository README.md, document hubs (docs/README.md, docs/okf/README.md), Diátaxis indexes, or orphan docs need audit or update."
---

# README Markdown Management

Audit repository `README.md` and documentation hierarchy, enforce human-friendly project summaries (100~500 chars), build Diátaxis document indexes, and report orphan markdown files.

## Documentation Hierarchy

- **Root `README.md`**: Human-readable project summary (100~500 chars) + top-level Diátaxis index pointing to key guides and sub-hubs (`docs/README.md`, `docs/okf/README.md`).
- **`docs/README.md`**: Sub-hub explaining `docs/` subdirectories (`okf`, `superpowers`, etc.) and their purposes.
- **`docs/okf/README.md`**: Sub-hub indexing all OKF specification docs under `docs/okf/`.
- **`docs/superpowers/`**: Internal AI agent specs (`specs/`) and plans (`plans/`). EXCLUDED from general human index & orphan doc scanning.

---

## 1. Discovery & Exclusion

1. Find Git root (or current working directory if non-Git).
2. Check existence of `README.md`, `docs/README.md`, `docs/okf/README.md`.
3. Scan repository markdown files (`*.md`, `docs/**/*.md`).
4. **Strict Exclusion Filter**: Exclude `.git`, `node_modules`, `dist`, `build`, `docs/superpowers/`, `.ai/`, `.claude/`, `.gemini/`, `.agents/`, `.codex/`.

---

## 2. Summary & Index Audit

1. **Project Goal & Summary Audit**:
   - Check if `README.md` top header contains a 100~500 character human-friendly overview.
   - 100 chars: Core 1-sentence purpose.
   - 500 chars max: Concise overview of target audience and key capabilities.
2. **Diátaxis 4-Quadrant Indexing**:
   - Classify scanned human docs using `references/diataxis-spec.md`:
     - **Tutorials**: Beginner lessons & getting started.
     - **How-To Guides**: Practical task procedures.
     - **Reference**: Technical specs, `docs/README.md`, `docs/okf/README.md`, API & CLI refs.
     - **Explanation**: Architecture, concepts, design decisions.
   - Format relative links: `[Doc Title](./relative/path.md) - 1-line description`.
3. **Sub-Hub Integrity Check**:
   - Verify `docs/README.md` correctly describes subfolder roles (`okf`, `superpowers`, etc.).
   - Verify `docs/okf/README.md` correctly indexes OKF files under `docs/okf/`.
4. **Stale Link & Orphan Page Audit**:
   - Check for broken relative links in `README.md`.
   - Identify unindexed human markdown files (files not linked in `README.md` or sub-hubs) as **Orphan Pages** and suggest their Diátaxis category.

---

## 3. Quality Report

Output audit findings before proposing any changes:
- Scanned markdown files count
- Summary character count status (100~500 chars)
- Diátaxis index structure preview
- Stale links found
- Orphan pages detected with recommended Diátaxis placement
- Surgical diff proposal for `README.md`

---

## 4. Proposed Changes & Approval Gate

1. Present exact diff for `README.md` (and sub-hubs if needed).
2. Preserve existing custom sections (badges, installation scripts, license, etc.).
3. Wait for explicit user approval before writing to disk.

---

## Safety

- Never modify files without explicit user approval.
- Never index internal agent workspace `docs/superpowers/`.
- Do not edit symlink target files.
- Keep project summary strictly between 100 and 500 characters.

---

## Attribution

Adapted for runtime-neutral AI Agent skills following Diátaxis framework and OKF documentation standards.
```

- [ ] **Step 2: Verify `SKILL.md` content and formatting**

Run: `view_file` on `plugins/readme-md-management/skills/readme-md-management/SKILL.md`
Expected: Line count and contents match specification.

- [ ] **Step 3: Commit**

```bash
git add plugins/readme-md-management/skills/readme-md-management/SKILL.md
git commit -m "feat(skill): add readme-md-management main skill"
```

---

### Task 4: Revision Skill (`revise-readme-md/SKILL.md`)

**Files:**
- Create: `plugins/readme-md-management/skills/revise-readme-md/SKILL.md`

**Interfaces:**
- Consumes: Existing `README.md` and new documentation/feature changes.
- Produces: Lightweight incremental update diffs for `README.md` summary and Diátaxis index.

- [ ] **Step 1: Write `revise-readme-md/SKILL.md`**

```markdown
---
name: revise-readme-md
description: "Use when new documentation or features are added and README.md index or summary needs a light incremental update."
---

# Revise README Markdown

Incremental and lightweight updater for `README.md` after adding new documentation files or modifying features.

---

## 1. Fast Preflight

1. Identify newly added or modified markdown files in current task/commit.
2. Filter out internal files (`docs/superpowers/`, `.git/`, `.claude/`, `.gemini/`).
3. If no human markdown docs were added/modified, check if project summary requires adjustment.

---

## 2. Diátaxis Classification & Index Hunk Update

1. Classify new/modified files into Diátaxis quadrants (Tutorials, How-To, Reference, Explanation).
2. Generate targeted hunk diff for `README.md` (or `docs/okf/README.md` if the file is an OKF doc).
3. Re-verify project summary character count (must remain between 100 and 500 characters).

---

## 3. Approval & Apply

1. Present minimal diff for `README.md`.
2. Wait for explicit user approval.
3. Apply surgical change without modifying unrelated sections.

---

## Safety

- Do not rewrite the entire `README.md`.
- Preserve existing badges, quick start, license, and custom sections.
- Exclude `docs/superpowers/` from indexing.
```

- [ ] **Step 2: Verify `revise-readme-md/SKILL.md` content**

Run: `ls -la plugins/readme-md-management/skills/revise-readme-md/SKILL.md`
Expected: File exists.

- [ ] **Step 3: Commit**

```bash
git add plugins/readme-md-management/skills/revise-readme-md/SKILL.md
git commit -m "feat(skill): add revise-readme-md revision skill"
```

---

### Task 5: Register Plugin in Marketplace Manifests

**Files:**
- Modify: `.agents/plugins/marketplace.json`
- Modify: `.claude-plugin/marketplace.json`

**Interfaces:**
- Consumes: `plugins/readme-md-management`
- Produces: Global marketplace registration for `readme-md-management` plugin.

- [ ] **Step 1: Register in `.agents/plugins/marketplace.json`**

Ensure `readme-md-management` plugin entry is added to `plugins` array:

```json
{
  "name": "readme-md-management",
  "source": {
    "source": "local",
    "path": "./plugins/readme-md-management"
  },
  "policy": {
    "installation": "AVAILABLE",
    "authentication": "ON_INSTALL"
  },
  "category": "Productivity"
}
```

- [ ] **Step 2: Register in `.claude-plugin/marketplace.json`**

Ensure `readme-md-management` plugin entry is added to `plugins` array:

```json
{
  "name": "readme-md-management",
  "source": "./plugins/readme-md-management",
  "description": "Audit and revise README.md, document hubs, Diátaxis indexes, and orphan docs",
  "version": "1.0.0"
}
```

- [ ] **Step 3: Verify JSON syntax**

Run: `jq . .agents/plugins/marketplace.json && jq . .claude-plugin/marketplace.json`
Expected: Valid JSON output with exit code 0.

- [ ] **Step 4: Commit**

```bash
git add .agents/plugins/marketplace.json .claude-plugin/marketplace.json
git commit -m "feat(marketplace): register readme-md-management plugin"
```

---

## Plan Self-Review

1. **Spec coverage:** All requirements from design spec covered:
   - 100~500 char summary constraint: Covered in Task 3 & Task 4.
   - Diátaxis 4-quadrant index: Covered in Task 2 & Task 3.
   - Hierarchy (`README.md`, `docs/README.md`, `docs/okf/README.md`, `docs/superpowers/` excluded): Covered in Task 2 & Task 3.
   - Orphan page detection & Stale link check: Covered in Task 3.
   - Manifests & Skills structure: Covered in Task 1, 3, 4, 5.
2. **Placeholder scan:** No TBD/TODO/placeholders found.
3. **Type consistency:** File paths and skill names are consistent across all tasks.
