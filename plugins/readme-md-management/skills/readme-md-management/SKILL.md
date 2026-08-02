---
name: readme-md-management
description: "Use when repository README.md, document hubs (docs/README.md, docs/okf/README.md), Diátaxis indexes, or orphan docs need audit or update."
---

# README Markdown Management

Audit repository `README.md` and documentation hierarchy, enforce human-friendly project summaries (100~500 chars), build Diátaxis document indexes, and report orphan markdown files.

## Key Principles (핵심 원칙)

1. **사람 중심의 문서 (Human-Centric Documentation)**:
   - 본 스킬이 다루는 모든 문서는 AI 에이전트용 문서(`docs/superpowers/`, `AGENTS.md` 등)와 구분되며, **사람(개발자, 사용자)**이 읽고 이해하기 쉽고 직관적인 톤으로 작성합니다.
2. **한국어 작성 원칙 (Korean Language Standard)**:
   - `README.md`, 서브 허브(`docs/README.md`, `docs/okf/README.md`), 문서 설명, 카테고리 인덱스 및 모든 감사 보고서는 **한국어**로 작성합니다.

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

## 2. Summary, Index & Score Audit

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
5. **100-Point Quality Scoring Matrix**:
   - Evaluate `README.md` and documentation hierarchy against `references/readme-quality-criteria.md` (Total 100 points):
     - Summary (20p), Diátaxis Structure (20p), Actionability & Quick Start (20p), Link Integrity & Hubs (15p), Human-Centric Formatting (15p), No Orphan/Conciseness (10p).
     - Calculate grade (A: 90-100, B: 70-89, C: 50-69, D: 30-49, F: 0-29).

---

## 3. Quality Report & Score Card

Output audit findings and score card before proposing any changes:
- Scanned markdown files count
- **Overall Score & Grade Card** (100-point breakdown and letter grade)
- Summary character count status (100~500 chars)
- Diátaxis index structure preview
- Stale links found
- Orphan pages detected with recommended Diátaxis placement
- Surgical diff proposal for `README.md` to achieve Grade A (90~100)

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
