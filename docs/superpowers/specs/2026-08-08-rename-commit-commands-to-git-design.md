# Rename `commit-commands` Plugin to `git` Design Document

**Date:** 2026-08-08  
**Status:** Approved  
**Target Plugin:** `commit-commands` -> `git`

---

## 1. Overview

Rename the existing `commit-commands` plugin to `git` across the entire codebase. This includes moving the plugin directory, updating plugin and marketplace manifests, renaming installation package references to `git@zzizily`, and updating skill command prefixes from `/commit-commands:*` to `/git:*`.

---

## 2. Scope & Objectives

- **Directory Move**: Rename `plugins/commit-commands` to `plugins/git`.
- **Manifest Updates**:
  - `plugins/git/.claude-plugin/plugin.json`: Update `"name"` to `"git"`.
  - `plugins/git/.codex-plugin/plugin.json`: Update `"name"` to `"git"`.
  - `.claude-plugin/marketplace.json`: Update plugin entry name to `"git"` and source path to `./plugins/git`.
  - `.agents/plugins/marketplace.json`: Update plugin entry name to `"git"` and path to `./plugins/git`.
- **Skill Prefixes & References**:
  - `/commit-commands:commit` -> `/git:commit`
  - `/commit-commands:commit-push-pr` -> `/git:commit-push-pr`
  - `/commit-commands:clean-gone` -> `/git:clean-gone`
  - Package installation identifier: `commit-commands@zzizily` -> `git@zzizily`
- **Documentation Updates**:
  - `plugins/git/README.md`
  - `README.md`
  - `CLAUDE.md`
  - `AGENTS.md`

---

## 3. Detailed Component Specification

### 3.1 Directory Relocation
- Move directory using `git mv plugins/commit-commands plugins/git`.

### 3.2 Manifest Schema & Values
- `plugins/git/.claude-plugin/plugin.json`:
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
- `plugins/git/.codex-plugin/plugin.json`:
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

### 3.3 Marketplace Registries
- `.claude-plugin/marketplace.json`:
  - `name`: `"git"`
  - `source`: `"./plugins/git"`
- `.agents/plugins/marketplace.json`:
  - `name`: `"git"`
  - `path`: `"./plugins/git"`

### 3.4 Root Documentation & Prompt Rules
- `README.md`: Update all installation examples and command references from `/commit-commands:` and `commit-commands@zzizily` to `/git:` and `git@zzizily`.
- `CLAUDE.md`: Update plugin table, installation commands, and directory tree.
- `AGENTS.md`: Update plugin table and command references.

---

## 4. Error Handling & Verification

1. **Manifest Validation**: Run JSON parser checks on all modified JSON files.
2. **Residual Reference Audit**: Run `grep` for `commit-commands` across the codebase to ensure no stale references remain (excluding past historical spec/plan files in `docs/superpowers/`).
