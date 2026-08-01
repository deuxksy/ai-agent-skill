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
