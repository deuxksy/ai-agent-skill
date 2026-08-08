---
name: agents-md-management
description: "Use when repository AI agent instruction files need hierarchy, reference, duplication, conflict, or codebase-consistency review."
---

# Agents Markdown Management

AI coding agent instruction hierarchy를 audit하고 targeted improvement를 제안한다.

## Instruction model

- Repository root `.ai/RULES.md`: 모든 runtime 공통 rule의 Single Source of Truth.
- Root `CLAUDE.md`: Claude 전용 rule + `@./.ai/RULES.md`.
- Root `GEMINI.md`: Gemini/Antigravity 전용 rule + `@./.ai/RULES.md`.
- Root `AGENTS.md`: AGENTS.md/Codex 전용 rule + 작업 전 root `.ai/RULES.md`를 읽으라는 instruction.
- Nested vendor file: 해당 subtree 전용 override. Common rule을 재-import하지 않는다.

Codex `AGENTS.md` reference는 native import가 아니라 instruction-based best-effort임을 report한다.

## 1. Discovery

1. Git root를 우선 사용하고 non-Git이면 current directory를 root로 사용한다.
2. Root와 nested `AGENTS.md`, `CLAUDE.md`, `GEMINI.md` 및 root `.ai/RULES.md`를 찾는다.
3. `.git`, dependency cache, generated/build output은 제외한다.
4. 각 file이 symlink인지 확인하고 write 가능 대상으로 간주하지 않는다.
5. Directory별 effective hierarchy와 nearest-file precedence를 계산한다.

## 2. Codebase assessment

1. Build/test/lint/deploy command를 package manifest, task runner, CI config와 비교한다.
2. Architecture, entry point, key path를 실제 file tree와 비교한다.
3. Common rule과 vendor-specific rule의 위치를 분류한다.
4. Root reference 누락·오류, nested duplicate import, 중복·충돌을 확인한다.
5. `references/quality-criteria.md`로 file별 score와 근거를 작성한다.

## 3. Quality report

Update 전에 발견 file 수, 평균 score, update 필요 file 수, file별 근거, exact stale command/path, conflict, duplicate, reference 오류, targeted update와 검증 한계를 출력한다.

## 4. Proposed changes

1. 누락 file은 자동 생성하지 않고 complete creation diff를 제시한다.
2. 기존 structure와 style을 보존한 최소 diff를 제시한다.
3. Common rule은 `.ai/RULES.md`에만 제안한다.
4. Vendor/subtree rule은 정확한 vendor 또는 nested file에 제안한다.
5. Conflict를 임의 병합하지 않고 선택을 요청한다.

## 5. Approval and apply

1. File별 변경 사유와 diff를 제시하고 명시적 승인을 기다린다.
2. 승인 직후 target content identity와 symlink 상태를 다시 확인한다.
3. Drift 또는 symlink이면 write하지 않고 새 diff가 필요함을 보고한다.
4. 승인된 file과 hunk만 수정한다.
5. Reference, hierarchy, duplicate, conflict를 다시 검사한다.

## Safety

- 승인 전 file을 생성·수정하지 않는다.
- 전체 rewrite와 unrelated 문서 개선을 하지 않는다.
- Secret, credential, 개인 절대경로를 instruction에 추가하지 않는다.
- Symlink target을 수정하지 않는다.
- Non-Git 환경의 current/stale 검증 한계를 명시한다.

## Attribution

Adapted from Anthropic `claude-md-management/skills/claude-md-improver` under Apache License 2.0. Modified for AGENTS.md standard, shared `.ai/RULES.md`, Claude/Codex/Antigravity hierarchies, symlink safety, and approval gates.
