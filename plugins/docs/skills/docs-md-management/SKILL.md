---
name: docs-md-management
description: "Use when repository README.md, document hubs (docs/README.md, docs/okf/README.md), Diátaxis indexes, architecture documentation (arc42 structure, C4 diagrams, ADR decision records), or overall project docs under docs/ need audit, structuring, or updating."
---

# README & Project Documentation Management

Audit and manage repository `README.md` and **all project documentation under `docs/`**, enforce human-friendly project summaries (100~500 chars), build Diátaxis document indexes across `docs/`, verify sub-hubs, report orphan markdown files, and audit architecture documentation layered on the Diátaxis Explanation quadrant (arc42 structure + C4 diagrams + ADR records, per `references/arch-docs-spec.md`).

## Key Principles (핵심 원칙)

1. **사람 중심의 문서 (Human-Centric Documentation)**:
   - 본 스킬이 다루는 모든 문서는 AI 에이전트용 문서(`docs/superpowers/`, `AGENTS.md` 등)와 구분되며, **사람(개발자, 사용자)**이 읽고 이해하기 쉽고 직관적인 톤으로 작성합니다.
2. **한국어 작성 원칙 (Korean Language Standard)**:
   - `README.md`, 서브 허브(`docs/README.md`, `docs/okf/README.md`), 문서 설명, 카테고리 인덱스 및 모든 감사 보고서는 **한국어**로 작성합니다.
3. **전체 프로젝트 문서 종합 관리 (Comprehensive Docs Management)**:
   - 루트 `README.md` 단독 관리에 그치지 않고, `docs/` 이하 디렉터리 내 전체 프로젝트 문서의 디아탁시스(Diátaxis) 구조화, 허브 인덱싱, 링크 무결성 및 고아(Orphan) 문서 관리를 총괄합니다.

## Documentation Hierarchy & Scope

- **Root `README.md`**: Human-readable project summary (100~500 chars) + top-level Diátaxis index pointing to key guides and sub-hubs (`docs/README.md`, `docs/okf/README.md`).
- **`docs/README.md`**: Sub-hub explaining `docs/` subdirectories (`okf`, `archive`, `superpowers`, etc.) and their purposes.
- **`docs/okf/README.md`**: Sub-hub indexing all OKF specification docs under `docs/okf/`, structured into Diátaxis 4-quadrant subfolders (`tutorials/`, `how-to/`, `reference/`, `explanation/`).
- **`docs/okf/explanation/`**: Architecture documentation hub — arc42 12-section structure with C4 zoom-level diagrams (see `references/arch-docs-spec.md`). Audited only when architecture docs are detected.
- **`docs/okf/reference/decisions/`**: ADR (Architecture Decision Records) — indexed under the Reference quadrant in `docs/okf/README.md`. Fallback location when no OKF hub exists: `docs/decisions/`.
- **`docs/archive/`**: Reference archive storing unmanaged external planning docs (screen designs, project requirements), API specs (`openapi.json`, `swagger.json`), and Figma design tokens. EXCLUDED from general human index & orphan doc scanning.
- **`docs/superpowers/`**: Internal AI agent specs (`specs/`) and plans (`plans/`). EXCLUDED from general human index & orphan doc scanning.

---

## 1. Discovery & Exclusion

1. Find Git root (or current working directory if non-Git).
2. Check existence of `README.md`, `docs/README.md`, `docs/okf/README.md` and `docs/okf/` Diátaxis subfolders (`tutorials/`, `how-to/`, `reference/`, `explanation/`).
3. Scan repository markdown files (`*.md`, `docs/**/*.md`).
4. **Strict Exclusion Filter**: Exclude `.git`, `node_modules`, `dist`, `build`, `docs/archive/`, `docs/superpowers/`, `.ai/`, `.claude/`, `.gemini/`, `.agents/`, `.codex/`.

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
     - **Explanation**: Architecture, concepts, design rationale (arc42 documents). ADR records are indexed under Reference (`decisions/`), not here.
   - Format relative links: `[Doc Title](./relative/path.md) - 1-line description`.
3. **Sub-Hub Integrity Check**:
   - Verify `docs/README.md` correctly describes subfolder roles (`okf`, `archive`, `superpowers`, etc.).
   - Verify `docs/okf/README.md` correctly indexes OKF files categorized under Diátaxis subfolders (`tutorials/`, `how-to/`, `reference/`, `explanation/`).
4. **Stale Link & Orphan Page Audit**:
   - Check for broken relative links across `README.md`, `docs/README.md`, `docs/okf/README.md`, and all indexed project docs under `docs/`.
   - Identify unindexed human markdown files (files under `docs/` or root not linked in `README.md` or sub-hubs) as **Orphan Pages** and suggest their Diátaxis category placement.
5. **Architecture Docs Audit (Conditional)**:
   - Activate per artifact — a `decisions/` directory enables ADR checks; an architecture document (filename pattern `architecture*.md`/`arc42*.md` or arc42 section headers) enables arc42+C4 checks. Repos with neither skip this step entirely (current behavior unchanged).
   - Audit against `references/arch-docs-spec.md`:
     - **arc42 (structure)**: 12-section completeness of architecture docs in the Explanation quadrant (`docs/okf/explanation/`).
     - **C4 (diagrams)**: Zoom-level discipline (L1 Context / L2 Container / L3 Component) rendered with Mermaid `graph` keyword only.
     - **ADR (rationale)**: Record format (Status/Context/Decision/Consequences) and hub indexing of `docs/okf/reference/decisions/` (or `docs/decisions/` fallback).
   - Findings go to a separate report section. The 100-point scoring matrix below stays UNCHANGED.
6. **100-Point Quality Scoring Matrix**:
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
- Architecture audit findings (only when detected): arc42 section gaps, C4 zoom-level violations, ADR format/indexing issues
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

Adapted for runtime-neutral AI Agent skills following Diátaxis classification, OKF hub standards, and arc42/C4/ADR architecture documentation practices.
