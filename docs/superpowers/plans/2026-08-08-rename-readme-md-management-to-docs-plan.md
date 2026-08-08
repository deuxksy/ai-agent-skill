# Rename `readme-md-management` Plugin to `docs` Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Rename `plugins/readme-md-management` to `plugins/docs`, update all plugin/marketplace manifests, and rename command prefixes/references from `readme-md-management` to `docs`.

**Architecture:** Execute clean git directory move (`plugins/readme-md-management` -> `plugins/docs`), update JSON manifests (`plugin.json`, `marketplace.json`), and perform bulk updates across all documentation and configuration files (`README.md`, `CLAUDE.md`, `AGENTS.md`, `plugins/docs/README.md`).

**Tech Stack:** Git, Shell, JSON

## Global Constraints

- Rename target: `readme-md-management` -> `docs`
- Package target: `readme-md-management@zzizily` -> `docs@zzizily`
- Command prefix target: `/readme-md-management:*` -> `/docs:*`
- Direct path target: `plugins/readme-md-management` -> `plugins/docs`

---

### Task 1: Directory Move and Manifest Updates

**Files:**
- Move: `plugins/readme-md-management` -> `plugins/docs`
- Modify: `plugins/docs/.claude-plugin/plugin.json`
- Modify: `plugins/docs/.codex-plugin/plugin.json`
- Modify: `.claude-plugin/marketplace.json`
- Modify: `.agents/plugins/marketplace.json`

**Interfaces:**
- Consumes: Existing directory `plugins/readme-md-management`
- Produces: `plugins/docs` directory with updated `plugin.json` and marketplace entries for `docs`

- [ ] **Step 1: Move directory with git mv**

Run:
```bash
git mv plugins/readme-md-management plugins/docs
```

- [ ] **Step 2: Update plugin manifests**

Update `plugins/docs/.claude-plugin/plugin.json`:
```json
{
  "name": "docs",
  "description": "Audit and revise README.md and overall project documentation under docs/, Diátaxis indexes, and orphan docs",
  "version": "1.10.0",
  "author": {
    "name": "Crong"
  },
  "skills": "./skills/"
}
```

Update `plugins/docs/.codex-plugin/plugin.json`:
```json
{
  "name": "docs",
  "description": "Audit and revise README.md and overall project documentation under docs/, Diátaxis indexes, and orphan docs",
  "version": "1.10.0",
  "author": {
    "name": "Crong"
  },
  "skills": "./skills/"
}
```

- [ ] **Step 3: Update marketplace manifests**

In `.claude-plugin/marketplace.json`, update the plugin entry:
```json
{
  "name": "docs",
  "source": "./plugins/docs",
  "description": "Audit and revise README.md and overall project documentation under docs/, Diátaxis indexes, and orphan docs",
  "version": "1.10.0"
}
```

In `.agents/plugins/marketplace.json`, update the plugin entry:
```json
{
  "name": "docs",
  "version": "1.10.0",
  "description": "Audit and revise README.md and overall project documentation under docs/, Diátaxis indexes, and orphan docs",
  "path": "./plugins/docs",
  "installationPolicy": "AVAILABLE",
  "authenticationPolicy": "ON_INSTALL",
  "category": "Productivity"
}
```

- [ ] **Step 4: Verify JSON validity**

Run:
```bash
python3 -c "import json; [json.load(open(f)) for f in ['plugins/docs/.claude-plugin/plugin.json', 'plugins/docs/.codex-plugin/plugin.json', '.claude-plugin/marketplace.json', '.agents/plugins/marketplace.json']]"
```
Expected: Exit code 0 (Valid JSON)

- [ ] **Step 5: Commit changes**

```bash
git add plugins/docs .claude-plugin/marketplace.json .agents/plugins/marketplace.json
git commit -m "refactor(plugins): rename readme-md-management directory and manifests to docs"
```

---

### Task 2: Documentation and Reference Updates

**Files:**
- Modify: `plugins/docs/README.md`
- Modify: `README.md`
- Modify: `CLAUDE.md`
- Modify: `AGENTS.md`

**Interfaces:**
- Consumes: Task 1 output
- Produces: Updated documentation referencing `docs` plugin and `/docs:*` commands

- [ ] **Step 1: Update plugins/docs/README.md**

Replace all occurrences of `readme-md-management` with `docs`, `/readme-md-management:` with `/docs:`, and `readme-md-management@zzizily` with `docs@zzizily` in `plugins/docs/README.md`.

- [ ] **Step 2: Update root README.md**

Update the plugin table row, code examples, and instructions in `README.md`:
- `readme-md-management` -> `docs`
- `readme-md-management@zzizily` -> `docs@zzizily`
- `/readme-md-management:` -> `/docs:`
- `plugins/readme-md-management` -> `plugins/docs`

- [ ] **Step 3: Update CLAUDE.md and AGENTS.md**

Update plugin tables, tree representation, and installation commands in `CLAUDE.md` and `AGENTS.md`.

- [ ] **Step 4: Search for residual readme-md-management references**

Run:
```bash
grep -rn "readme-md-management" --exclude-dir="docs/superpowers" .
```
Expected: 0 matches outside of `docs/superpowers/`

- [ ] **Step 5: Commit changes**

```bash
git add plugins/docs/README.md README.md CLAUDE.md AGENTS.md
git commit -m "docs: update plugin and skill references from readme-md-management to docs"
```
