# Rename `agents-md-management` Plugin to `rules` Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Rename `plugins/agents-md-management` to `plugins/rules`, update all plugin/marketplace manifests, and rename command prefixes/references from `agents-md-management` to `rules`.

**Architecture:** Execute clean git directory move (`plugins/agents-md-management` -> `plugins/rules`), update JSON manifests (`plugin.json`, `marketplace.json`), and perform bulk updates across all documentation and configuration files (`README.md`, `CLAUDE.md`, `AGENTS.md`, `plugins/rules/README.md`).

**Tech Stack:** Git, Shell, JSON

## Global Constraints

- Rename target: `agents-md-management` -> `rules`
- Package target: `agents-md-management@zzizily` -> `rules@zzizily`
- Command prefix target: `/agents-md-management:*` -> `/rules:*`
- Direct path target: `plugins/agents-md-management` -> `plugins/rules`

---

### Task 1: Directory Move and Manifest Updates

**Files:**
- Move: `plugins/agents-md-management` -> `plugins/rules`
- Modify: `plugins/rules/.claude-plugin/plugin.json`
- Modify: `plugins/rules/.codex-plugin/plugin.json`
- Modify: `.claude-plugin/marketplace.json`
- Modify: `.agents/plugins/marketplace.json`

**Interfaces:**
- Consumes: Existing directory `plugins/agents-md-management`
- Produces: `plugins/rules` directory with updated `plugin.json` and marketplace entries for `rules`

- [ ] **Step 1: Move directory with git mv**

Run:
```bash
git mv plugins/agents-md-management plugins/rules
```

- [ ] **Step 2: Update plugin manifests**

Update `plugins/rules/.claude-plugin/plugin.json`:
```json
{
  "name": "rules",
  "description": "Audit and revise AGENTS.md, CLAUDE.md, GEMINI.md, and shared .ai/RULES.md",
  "version": "1.10.0",
  "author": {
    "name": "Crong"
  },
  "skills": "./skills/"
}
```

Update `plugins/rules/.codex-plugin/plugin.json`:
```json
{
  "name": "rules",
  "description": "Audit and revise AGENTS.md, CLAUDE.md, GEMINI.md, and shared .ai/RULES.md",
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
  "name": "rules",
  "source": "./plugins/rules",
  "description": "Audit and revise AGENTS.md, CLAUDE.md, GEMINI.md, and shared .ai/RULES.md",
  "version": "1.10.0"
}
```

In `.agents/plugins/marketplace.json`, update the plugin entry:
```json
{
  "name": "rules",
  "version": "1.10.0",
  "description": "Audit and revise AGENTS.md, CLAUDE.md, GEMINI.md, and shared .ai/RULES.md",
  "path": "./plugins/rules",
  "installationPolicy": "AVAILABLE",
  "authenticationPolicy": "ON_INSTALL",
  "category": "Productivity"
}
```

- [ ] **Step 4: Verify JSON validity**

Run:
```bash
python3 -c "import json; [json.load(open(f)) for f in ['plugins/rules/.claude-plugin/plugin.json', 'plugins/rules/.codex-plugin/plugin.json', '.claude-plugin/marketplace.json', '.agents/plugins/marketplace.json']]"
```
Expected: Exit code 0 (Valid JSON)

- [ ] **Step 5: Commit changes**

```bash
git add plugins/rules .claude-plugin/marketplace.json .agents/plugins/marketplace.json
git commit -m "refactor(plugins): rename agents-md-management directory and manifests to rules"
```

---

### Task 2: Documentation and Reference Updates

**Files:**
- Modify: `plugins/rules/README.md`
- Modify: `README.md`
- Modify: `CLAUDE.md`
- Modify: `AGENTS.md`

**Interfaces:**
- Consumes: Task 1 output
- Produces: Updated documentation referencing `rules` plugin and `/rules:*` commands

- [ ] **Step 1: Update plugins/rules/README.md**

Replace all occurrences of `agents-md-management` with `rules`, `/agents-md-management:` with `/rules:`, and `agents-md-management@zzizily` with `rules@zzizily` in `plugins/rules/README.md`.

- [ ] **Step 2: Update root README.md**

Update the plugin table row, code examples, and instructions in `README.md`:
- `agents-md-management` -> `rules`
- `agents-md-management@zzizily` -> `rules@zzizily`
- `/agents-md-management:` -> `/rules:`
- `plugins/agents-md-management` -> `plugins/rules`

- [ ] **Step 3: Update CLAUDE.md and AGENTS.md**

Update plugin tables, tree representation, and installation commands in `CLAUDE.md` and `AGENTS.md`.

- [ ] **Step 4: Search for residual agents-md-management references**

Run:
```bash
grep -rn "agents-md-management" --exclude-dir="docs/superpowers" .
```
Expected: 0 matches outside of `docs/superpowers/`

- [ ] **Step 5: Commit changes**

```bash
git add plugins/rules/README.md README.md CLAUDE.md AGENTS.md
git commit -m "docs: update plugin and skill references from agents-md-management to rules"
```
