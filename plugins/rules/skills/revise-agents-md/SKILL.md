---
name: revise-agents-md
description: "Use when reusable learning from the current session should be added to common, vendor-specific, or subtree AI agent instructions."
---

# Revise Agent Instructions

현재 session learning을 다음 session에도 필요한 최소 instruction으로 반영한다. 전체 quality audit은 수행하지 않는다.

## 1. Reflect

실제로 검증된 command, 반복되는 code/architecture pattern, 재현 가능한 environment quirk, 반복 가능한 gotcha, runtime별 동작 차이만 추출한다. One-off fix, 자명한 정보, 추측, raw output은 제외한다.

## 2. Discover targets

1. Git root를 우선 사용하고 non-Git이면 current directory를 root로 사용한다.
2. Root와 관련 subtree의 `.ai/RULES.md`, `AGENTS.md`, `CLAUDE.md`, `GEMINI.md`를 확인한다.
3. Symlink target은 write 대상으로 사용하지 않는다.
4. 기존 rule과 learning의 중복·충돌을 확인한다.

## 3. Classify

| Learning | Target |
| :--- | :--- |
| 모든 runtime 공통 | Root `.ai/RULES.md` |
| AGENTS.md 표준 또는 Codex 전용 | `AGENTS.md` |
| Claude Code 전용 | `CLAUDE.md` |
| Gemini/Antigravity 전용 | `GEMINI.md` |
| 특정 subtree 전용 | 해당 subtree의 vendor file |

Scope가 불명확하면 한 번에 하나의 질문으로 확인한다. Common rule을 vendor file에 복제하지 않는다.

## 4. Secret and relevance filter

- Secret, token, credential, private key, 개인 절대경로를 제거한다.
- Raw command output과 file content dump를 저장하지 않는다.
- 검증되지 않은 사실과 일회성 workaround를 제거한다.
- 기존 instruction과 의미가 같은 learning은 추가하지 않는다.

## 5. Preview and approval

Target file별 learning 요약, common/vendor/subtree 분류 근거, conflict/duplicate 여부, 최소 diff를 제시한다. 명시적 승인 전에는 file을 생성·수정하지 않으며 conflict를 자동 선택하지 않는다.

## 6. Apply

1. 승인 직후 target content identity와 symlink 상태를 다시 확인한다.
2. Drift 또는 symlink이면 write하지 않고 새 diff가 필요함을 보고한다.
3. 승인된 target과 hunk만 수정한다.
4. Root reference와 nested duplicate import를 확인한다.
5. 변경 file과 반영·제외한 learning을 보고한다.

## Attribution

Adapted from Anthropic `claude-md-management/commands/revise-claude-md.md` under Apache License 2.0. Modified for shared `.ai/RULES.md`, AGENTS.md/CLAUDE.md/GEMINI.md classification, nested scope, secret filtering, and approval gates.
