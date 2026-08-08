# Rename `agents-md-management` Plugin to `rules` Design Document

**Date:** 2026-08-08  
**Status:** Approved  
**Target Plugin:** `agents-md-management` -> `rules`

---

## 1. Overview

Rename the existing `agents-md-management` plugin to `rules` across the entire codebase. This includes moving the plugin directory, updating plugin and marketplace manifests, renaming installation package references to `rules@zzizily`, and updating skill command prefixes from `/agents-md-management:*` to `/rules:*`.

---

## 2. Scope & Objectives

- **Directory Move**: Rename `plugins/agents-md-management` to `plugins/rules`.
- **Manifest Updates**:
  - `plugins/rules/.claude-plugin/plugin.json`: Update `"name"` to `"rules"`.
  - `plugins/rules/.codex-plugin/plugin.json`: Update `"name"` to `"rules"`.
  - `.claude-plugin/marketplace.json`: Update plugin entry name to `"rules"` and source path to `./plugins/rules`.
  - `.agents/plugins/marketplace.json`: Update plugin entry name to `"rules"` and path to `./plugins/rules`.
- **Skill Prefixes & References**:
  - `/agents-md-management:agents-md-management` -> `/rules:agents-md-management`
  - `/agents-md-management:revise-agents-md` -> `/rules:revise-agents-md`
  - Package installation identifier: `agents-md-management@zzizily` -> `rules@zzizily`
- **Documentation Updates**:
  - `plugins/rules/README.md`
  - `README.md`
  - `CLAUDE.md`
  - `AGENTS.md`

---

## 3. Detailed Component Specification

### 3.1 Directory Relocation
- Move directory using `git mv plugins/agents-md-management plugins/rules`.

### 3.2 Manifest Schema & Values
- `plugins/rules/.claude-plugin/plugin.json`:
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
- `plugins/rules/.codex-plugin/plugin.json`:
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

### 3.3 Marketplace Registries
- `.claude-plugin/marketplace.json`:
  - `name`: `"rules"`
  - `source`: `"./plugins/rules"`
- `.agents/plugins/marketplace.json`:
  - `name`: `"rules"`
  - `path`: `"./plugins/rules"`

### 3.4 Root Documentation & Prompt Rules
- `README.md`: Update all installation examples and command references from `agents-md-management` to `rules`.
- `CLAUDE.md`: Update plugin table, installation commands, and directory tree.
- `AGENTS.md`: Update plugin table and command references.

---

## 4. Error Handling & Verification

1. **Manifest Validation**: Run JSON parser checks on all modified JSON files.
2. **Residual Reference Audit**: Run `grep` for `agents-md-management` across the codebase to ensure no stale references remain (excluding past historical spec/plan files in `docs/superpowers/`).
