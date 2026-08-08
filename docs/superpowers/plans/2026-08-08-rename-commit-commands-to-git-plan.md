# Rename `commit-commands` Plugin to `git` Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Rename `plugins/commit-commands` to `plugins/git`, update all plugin/marketplace manifests, and rename command prefixes/references from `commit-commands` to `git`.

**Architecture:** Execute clean git directory move (`plugins/commit-commands` -> `plugins/git`), update JSON manifests (`plugin.json`, `marketplace.json`), and perform bulk updates across all documentation and configuration files (`README.md`, `CLAUDE.md`, `AGENTS.md`, `plugins/git/README.md`).

**Tech Stack:** Git, Shell, JSON

## Global Constraints

- Rename target: `commit-commands` -> `git`
- Package target: `commit-commands@zzizily` -> `git@zzizily`
- Command prefix target: `/commit-commands:*` -> `/git:*`
- Direct path target: `plugins/commit-commands` -> `plugins/git`

---

### Task 1: Directory Move and Manifest Updates

**Files:**
- Move: `plugins/commit-commands` -> `plugins/git`
- Modify: `plugins/git/.claude-plugin/plugin.json`
- Modify: `plugins/git/.codex-plugin/plugin.json`
- Modify: `.claude-plugin/marketplace.json`
- Modify: `.agents/plugins/marketplace.json`

**Interfaces:**
- Consumes: Existing directory `plugins/commit-commands`
- Produces: `plugins/git` directory with updated `plugin.json` and marketplace entries for `git`

- [ ] **Step 1: Move directory with git mv**

Run:
```bash
git mv plugins/commit-commands plugins/git
```

- [ ] **Step 2: Update plugin manifests**

Update `plugins/git/.claude-plugin/plugin.json`:
```json
{
  "name": "git",
  "description": "Safe runtime-neutral Git commit, push, pull/merge request, and stale branch cleanup skills",
  "version": "1.10.0",
  "author": {
    "name": "Crong"
  },
  "skills": "./skills/"
}
```

Update `plugins/git/.codex-plugin/plugin.json`:
```json
{
  "name": "git",
  "description": "Safe runtime-neutral Git commit, push, pull/merge request, and stale branch cleanup skills",
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
  "name": "git",
  "source": "./plugins/git",
  "description": "Safe runtime-neutral Git commit, push, pull/merge request, and stale branch cleanup skills"
}
```

In `.agents/plugins/marketplace.json`, update the plugin entry:
```json
{
  "name": "git",
  "version": "1.10.0",
  "description": "Safe runtime-neutral Git commit, push, pull/merge request, and stale branch cleanup skills",
  "path": "./plugins/git",
  "installationPolicy": "AVAILABLE",
  "authenticationPolicy": "ON_INSTALL",
  "category": "Productivity"
}
```

- [ ] **Step 4: Verify JSON validity**

Run:
```bash
python3 -c "import json; [json.load(open(f)) for f in ['plugins/git/.claude-plugin/plugin.json', 'plugins/git/.codex-plugin/plugin.json', '.claude-plugin/marketplace.json', '.agents/plugins/marketplace.json']]"
```
Expected: Exit code 0 (Valid JSON)

- [ ] **Step 5: Commit changes**

```bash
git add plugins/git .claude-plugin/marketplace.json .agents/plugins/marketplace.json
git commit -m "refactor(plugins): rename commit-commands directory and manifests to git"
```

---

### Task 2: Documentation and Reference Updates

**Files:**
- Modify: `plugins/git/README.md`
- Modify: `README.md`
- Modify: `CLAUDE.md`
- Modify: `AGENTS.md`

**Interfaces:**
- Consumes: Task 1 output
- Produces: Updated documentation referencing `git` plugin and `/git:*` commands

- [ ] **Step 1: Update plugins/git/README.md**

Replace all occurrences of `commit-commands` with `git`, `/commit-commands:` with `/git:`, and `commit-commands@zzizily` with `git@zzizily` in `plugins/git/README.md`.

- [ ] **Step 2: Update root README.md**

Update the plugin table row, code examples, and instructions in `README.md`:
- `commit-commands` -> `git`
- `commit-commands@zzizily` -> `git@zzizily`
- `/commit-commands:` -> `/git:`
- `plugins/commit-commands` -> `plugins/git`

- [ ] **Step 3: Update CLAUDE.md and AGENTS.md**

Update plugin tables, tree representation, and installation commands in `CLAUDE.md` and `AGENTS.md`.

- [ ] **Step 4: Search for residual commit-commands references**

Run:
```bash
grep -rn "commit-commands" --exclude-dir="docs/superpowers" .
```
Expected: 0 matches outside of `docs/superpowers/`

- [ ] **Step 5: Commit changes**

```bash
git add plugins/git/README.md README.md CLAUDE.md AGENTS.md
git commit -m "docs: update plugin and skill references from commit-commands to git"
```
