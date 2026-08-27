---
name: docs-restructure
description: "Use when a project's scattered, unstructured documentation needs bulk migration into the standard hierarchy — moving files into the Diátaxis/OKF structure, splitting multi-role documents, merging duplicates, and updating links repository-wide."
---

# Documentation Restructure & Migration

Surgical migration of scattered, rule-less project documentation into the standard structure audited by `docs-md-management`: Diátaxis 4-quadrant hierarchy, hub indexing (`docs/README.md`, `docs/okf/README.md`), and Source-of-Truth deduplication. This skill is the **execution** counterpart to `docs-md-management`'s **audit** — it moves, splits, and merges files. It never rewrites content and never scores quality.

## Key Principles (핵심 원칙)

1. **원문 충실 (Verbatim Content)**:
   - 콘텐츠를 재작성하지 않는다. 허용 연산은 이동(move)·절단(split)·병합(merge)·제목/frontmatter 갱신뿐. 요약·재구술·톤 정리 금지. 이관 중 발견한 품질 문제는 보고만 하고 수정하지 않는다.
2. **히스토리 보존 (History Preservation)**:
   - 파일 이동·이름 변경은 반드시 `git mv`로 실행해 rename detection을 유지한다. 삭제 후 재생성 금지.
3. **매핑 테이블 승인 (Approval Gate)**:
   - 매핑 테이블(old→new)과 split/merge 계획을 사용자에게 제시하고 명시적 승인 전에는 어떤 디스크 쓰기도 하지 않는다.
4. **진단/수술 분리 (Audit/Migration Separation)**:
   - 품질 평가·점수화·인덱스 구축은 `docs-md-management`가 담당. 본 스킬은 구조 이관만 수행하고, 완료 후 감사 스킬 재실행으로 검증을 위임한다.

## Scope & Exclusions

- **Targets**: repository `*.md` files — root-level stray docs, `docs/**`, duplicated README content.
- **Exclusions**: identical filter as `docs-md-management` — `.git`, `node_modules`, `dist`, `build`, `docs/archive/`, `docs/superpowers/`, `.ai/`, `.claude/`, `.gemini/`, `.agents/`, `.codex/`. AI agent instruction files (`AGENTS.md`, `CLAUDE.md`, `GEMINI.md`) are never migrated.
- **Prerequisite**: Git repository (history preservation requires `git mv`). Non-Git directory → abort.

---

## 1. Discovery & Classification

1. Find Git root; scan all in-scope markdown files.
2. Tag every file with exactly one action:
   - `move`: 올바른 내용, 잘못된 위치 → Diátaxis 사분면(`docs/okf/tutorials/`, `how-to/`, `reference/`, `explanation/`)으로 재배치.
   - `split`: 한 문서가 둘 이상의 Diátaxis 역할 겸함 → 분리 (예: 입문 실습(Tutorial)과 업무 절차(How-to)가 한 파일에 공존).
   - `merge`: 동일 내용이 둘 이상 파일에 중복 → 하나의 Source of Truth로 통합.
   - `keep`: 이미 준수 — 이관 대상 아님.
3. `split` 판단 기준: Tutorial↔How-to 혼재, Reference↔Explanation 혼재 (Diátaxis 구분 원칙).
4. `merge` 판단 기준: 같은 사실을 2개 이상 파일에서 유지 (예: README와 getting-started 문서에 동일 설치 절차). 기준본(survivor)은 명확성·최신성 기준, 모호하면 사용자에게 질의.

## 2. Migration Plan (Mapping Table)

모든 쓰기 전에 아래 형식으로 제시한다:

| Action | Source | Target | 비고 |
| :--- | :--- | :--- | :--- |
| move | `SETUP.md` | `docs/okf/how-to/machine-setup.md` | |
| split | `GUIDE.md` | `docs/okf/tutorials/intro.md` | §1-2 절만, 원본 `git mv` 후 잔여 분리 |
| split | `GUIDE.md` | `docs/okf/how-to/deploy.md` | §3-4 절 |
| merge | `install-full.md`, `install-short.md` | `docs/okf/reference/install.md` | full 기준본, short 고유 내용만 병합 후 `git rm` |

- 이동 관계가 5건 이상이면 Mermaid `graph LR`로 시각화해 함께 제시 (레이블 규칙: `["..."]` 따옴표·`<br/>`·특수기호 금지, `A[1. 원본문서]` 형식).
- split은 절(section) 단위 배치를 비고에 명시. merge는 기준본 선정 근거를 명시.

## 3. Approval Gate

- 매핑 테이블 + split 절 배치 + merge 기준본 근거를 보고한다.
- 명시적 승인을 받을 때까지 어떤 파일도 생성·이동·수정하지 않는다.

## 4. Execution (Phased Changesets)

각 Phase를 별도 changeset으로 분리한다 — 롤백 단위 확보. 커밋은 각 Phase 완료 후 사용자 승인하에 진행한다.

1. **Phase 1 — Move**: `move` 대상 전체 `git mv` (대상 디렉토리 생성 포함).
2. **Phase 2 — Split**: 원본을 주 타깃으로 `git mv` 후 나머지 절을 신규 파일로 절단 이동. 제목·frontmatter만 갱신, 본문 미수정.
3. **Phase 3 — Merge**: 기준본에 고유 내용 병합 후 중복 파일 `git rm`. 링크 참조는 기준본으로 통일.
4. **Phase 4 — Links**: 구경로를 가리키는 전체 상대 링크를 신규 경로로 갱신 (README, 허브, 본문 모두).

## 5. Verification

1. `git status` — 예상 외 파일·변경 없는지 확인.
2. `/docs:docs-md-management` 재실행 — 링크 무결성, 고아 문서 0건, 허브 인덱스 정합 확인.
3. 결과 보고: moved/split/merged/removed 건수 + 이관 중 발견한 콘텐츠 품질 문제 목록(수정하지 않음 — 원문 충실 원칙).

---

## Safety

- 매핑 테이블 승인 전 디스크 쓰기 금지.
- 콘텐츠 재작성 금지 — 이동·절단·병합·제목 갱신만.
- 제외 디렉토리·symlink 대상·AI 지침 파일 미관여.
- `git rm` 등 파괴적 연산은 승인된 매핑 테이블 범위 내에서만.
- merge 기준본이 모호하면 사용자에게 질의 후 진행.

---

## Attribution

Execution counterpart to `docs-md-management` following the investigation→remediation pattern (`backdoor-investigation` → `backdoor-remediation`). Split criteria per Diátaxis role separation; merge criteria per Source-of-Truth single-definition rule.
