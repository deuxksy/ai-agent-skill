# Rename `readme-md-management` Plugin to `docs` Design Document

**Date:** 2026-08-08  
**Status:** Approved  
**Target Plugin:** `readme-md-management` -> `docs`

---

## 1. Overview

Rename the existing `readme-md-management` plugin to `docs` across the entire codebase. This includes moving the plugin directory, updating plugin and marketplace manifests, renaming installation package references to `docs@zzizily`, and updating skill command prefixes from `/readme-md-management:*` to `/docs:*`.

---

## 2. Scope & Objectives

- **Directory Move**: Rename `plugins/readme-md-management` to `plugins/docs`.
- **Manifest Updates**:
  - `plugins/docs/.claude-plugin/plugin.json`: Update `"name"` to `"docs"`.
  - `plugins/docs/.codex-plugin/plugin.json`: Update `"name"` to `"docs"`.
  - `.claude-plugin/marketplace.json`: Update plugin entry name to `"docs"` and source path to `./plugins/docs`.
  - `.agents/plugins/marketplace.json`: Update plugin entry name to `"docs"` and path to `./plugins/docs`.
- **Skill Prefixes & References**:
  - `/readme-md-management:docs-md-management` -> `/docs:docs-md-management`
  - `/readme-md-management:revise-readme-md` -> `/docs:revise-readme-md`
  - Package installation identifier: `readme-md-management@zzizily` -> `docs@zzizily`
- **Documentation Updates**:
  - `plugins/docs/README.md`
  - `README.md`
  - `CLAUDE.md`
  - `AGENTS.md`

---

## 3. Detailed Component Specification

### 3.1 Directory Relocation
- Move directory using `git mv plugins/readme-md-management plugins/docs`.

### 3.2 Manifest Schema & Values
- `plugins/docs/.claude-plugin/plugin.json`:
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
- `plugins/docs/.codex-plugin/plugin.json`:
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

### 3.3 Marketplace Registries
- `.claude-plugin/marketplace.json`:
  - `name`: `"docs"`
  - `source`: `"./plugins/docs"`
- `.agents/plugins/marketplace.json`:
  - `name`: `"docs"`
  - `path`: `"./plugins/docs"`

### 3.4 Root Documentation & Prompt Rules
- `README.md`: Update all installation examples and command references from `readme-md-management` to `docs`.
- `CLAUDE.md`: Update plugin table, installation commands, and directory tree.
- `AGENTS.md`: Update plugin table and command references if any exist.

---

## 4. Error Handling & Verification

1. **Manifest Validation**: Run JSON parser checks on all modified JSON files.
2. **Residual Reference Audit**: Run `grep` for `readme-md-management` across the codebase to ensure no stale references remain (excluding past historical spec/plan files in `docs/superpowers/`).
