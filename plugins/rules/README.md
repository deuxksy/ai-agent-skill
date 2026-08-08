# rules

공통 `.ai/RULES.md`와 vendor별 `AGENTS.md`, `CLAUDE.md`, `GEMINI.md`를 audit하고 session learning을 반영하는 runtime-neutral Agent Skills plugin.

**Version:** 1.0.0

## Skills

| Skill | 설명 |
| :--- | :--- |
| `agents-md-management` | Root+nested instruction hierarchy audit와 targeted update |
| `revise-agents-md` | Session learning을 common/vendor/subtree로 분류해 승인 후 최소 반영 |

## Instruction model

| File | Scope |
| :--- | :--- |
| `.ai/RULES.md` | 모든 runtime 공통 |
| `AGENTS.md` | AGENTS.md 표준/Codex 전용 |
| `CLAUDE.md` | Claude Code 전용 |
| `GEMINI.md` | Gemini/Antigravity 전용 |

Root `CLAUDE.md`와 `GEMINI.md`는 `@./.ai/RULES.md`를 import한다. Root `AGENTS.md`는 작업 전에 `.ai/RULES.md`를 읽도록 지시한다. Nested vendor 파일은 subtree override만 가진다.

## Workflow 선택

- Repository 전체 instruction 품질과 codebase 정합성 점검: `agents-md-management`
- 현재 session에서 확인한 learning만 최소 반영: `revise-agents-md`

## Claude Code

```bash
claude plugin install rules@zzizily
```

호출:

```text
/rules:agents-md-management
/rules:revise-agents-md
```

## Codex와 Antigravity

Canonical Skill source는 `skills/<skill-name>/`이다. Runtime별 복제본은 유지하지 않는다.

| Runtime | Repository scope | User/global scope | 호출 |
| :--- | :--- | :--- | :--- |
| Codex | `<repo>/.agents/skills/<skill-name>/` | `$HOME/.agents/skills/<skill-name>/` | `$<skill-name>` 또는 implicit |
| Antigravity | `<workspace>/.agents/skills/<skill-name>/` | `~/.gemini/config/skills/<skill-name>/` | Skill 이름 명시 또는 implicit |

Codex에서는 이 repository의 `.agents/plugins/marketplace.json`을 등록해 plugin 단위로 설치할 수도 있다. 다른 project에서는 Skill directory를 지원되는 copy/link 방식으로 등록한다.

## Reference semantics

- Claude Code: root `CLAUDE.md`의 `@./.ai/RULES.md`를 native import한다.
- Antigravity/Gemini: root `GEMINI.md`의 `@./.ai/RULES.md`를 native import한다.
- Codex/AGENTS.md: native import가 없으므로 root `AGENTS.md`가 `.ai/RULES.md`를 먼저 읽도록 지시한다. 이 방식은 best-effort다.
- Nested vendor file은 common rule을 다시 import하지 않는다.

## Safety

- Quality report 또는 learning diff 우선
- 명시적 승인 후 file mutation
- Symlink와 승인 후 drift는 fail-closed
- Secret과 one-off context 기록 금지

## Limitations

- Runtime별 자동 installer를 제공하지 않는다.
- `AGENTS.md`에서 `.ai/RULES.md` loading은 native import가 아니다.
- Background sync와 vendor file로의 common rule 복제를 수행하지 않는다.

## Attribution

Adapted from Anthropic [`claude-md-management`](https://github.com/anthropics/claude-plugins-official/tree/main/plugins/claude-md-management) under Apache License 2.0. This version generalizes the workflow for AGENTS.md, CLAUDE.md, GEMINI.md, and shared `.ai/RULES.md`.
