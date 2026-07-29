# commit-commands 및 agents-md-management Plugin 분리 이식 — Design Spec

**날짜**: 2026-07-29

**상태**: 설계 승인, 문서 review 대기
**접근법**: Prompt-first 독립 Skill + marketplace monorepo

## 1. 배경

현재 `zzizily` plugin은 19개 Skill을 한 plugin에 포함한다. 여기에 Git workflow와 AI agent instruction 관리를 추가하면 domain boundary가 더 약해지고, 사용자는 필요 없는 Skill까지 함께 설치해야 한다.

Anthropic 공식 `commit-commands`와 `claude-md-management`의 핵심 workflow를 이식하되 다음 환경에서 같은 `SKILL.md`를 사용해야 한다.

- Anthropic Claude Code
- OpenAI Codex
- Google Antigravity

신규 기능은 기존 `zzizily`와 분리하고, 기존 19개 Skill의 재구성은 이번 작업 완료 후 별도 spec으로 진행한다.

## 2. 목표

1. 신규 `commit-commands` plugin을 추가한다.
   - `commit`
   - `commit-push-pr`
   - `clean-gone`
2. 신규 `agents-md-management` plugin을 추가한다.
   - `agents-md-management`
   - `revise-agents-md`
3. 각 Skill은 Claude Code, Codex, Antigravity에서 사용할 수 있는 runtime-neutral instruction으로 작성한다.
4. GitHub, GitLab, Gitea의 review request 생성을 지원한다.
5. 모든 mutation은 대상·명령·영향 preview와 명시적 승인 후 수행한다.
6. 기존 root `zzizily` plugin과 19개 Skill에는 breaking change를 만들지 않는다.

## 3. 비목표

- 기존 19개 Skill의 domain plugin migration
- runtime별 `SKILL.md` 복제본
- runtime별 자동 installer
- GitHub, GitLab, Gitea API 직접 구현
- 강제 branch/worktree 삭제
- instruction 파일의 background 동기화
- 실제 remote를 사용하는 자동 integration test
- 공통 engine 또는 두 plugin 사이 runtime dependency

## 4. 접근법 결정

### 채택: Prompt-first 독립 Skill

각 plugin은 `SKILL.md`와 필요한 reference 문서만 포함한다. Skill은 현재 runtime의 file/shell tool을 사용하도록 지시하고 특정 vendor tool 이름에 의존하지 않는다.

장점:

- 별도 Python, Bash runtime dependency가 없다.
- Windows, macOS, Linux에서 같은 instruction을 사용한다.
- Skill별 책임이 분리된다.
- 현재 repository 스타일과 Agent Skills의 progressive disclosure 모델에 맞는다.

한계:

- script 기반 구현보다 출력 표현과 일부 판단이 agent마다 달라질 수 있다.
- 안전성은 executable guard가 아니라 명시적 workflow contract로 보장한다.

### 기각: Cross-platform script core

Git 분석과 instruction inventory를 Python으로 구현하면 deterministic 결과를 얻을 수 있지만, runtime dependency와 OS test matrix가 추가된다. 이번 prompt workflow 규모에는 과하다.

### 기각: 공유 core + plugin adapter

Marketplace plugin은 cache에 plugin directory 단위로 복사되며 상위 상대경로 공유가 제한된다. 별도 packaging dependency는 두 domain을 불필요하게 결합한다.

## 5. Architecture

### 5.1 Repository layout

```text
.
├── .claude-plugin/
│   ├── marketplace.json
│   └── plugin.json
├── skills/                              # 기존 zzizily Skill 19개, 변경 없음
└── plugins/
    ├── commit-commands/
    │   ├── .claude-plugin/
    │   │   └── plugin.json
    │   ├── README.md
    │   ├── LICENSE
    │   └── skills/
    │       ├── commit/
    │       │   └── SKILL.md
    │       ├── commit-push-pr/
    │       │   ├── SKILL.md
    │       │   └── references/
    │       │       └── providers.md
    │       └── clean-gone/
    │           └── SKILL.md
    └── agents-md-management/
        ├── .claude-plugin/
        │   └── plugin.json
        ├── README.md
        ├── LICENSE
        └── skills/
            ├── agents-md-management/
            │   ├── SKILL.md
            │   └── references/
            │       └── quality-criteria.md
            └── revise-agents-md/
                └── SKILL.md
```

### 5.2 Marketplace

Root `.claude-plugin/marketplace.json`은 다음 installable plugin을 제공한다.

| Plugin | Source | Version |
| :--- | :--- | :--- |
| 기존 `deuxksy` | `./` | 기존 version 유지 |
| `commit-commands` | `./plugins/commit-commands` | `1.0.0` |
| `agents-md-management` | `./plugins/agents-md-management` | `1.0.0` |

Claude Code 설치 이름:

```text
commit-commands@zzizily
agents-md-management@zzizily
```

신규 plugin의 `plugin.json`, marketplace entry, plugin README version은 `1.0.0`으로 동기화한다. 기존 root plugin version은 신규 plugin 추가로 변경하지 않는다.

### 5.3 Self-contained boundary

- 각 plugin은 자체 Skill, reference, README, LICENSE를 가진다.
- plugin 간 상대경로 참조와 runtime dependency를 금지한다.
- repository root 문서는 marketplace catalog 역할만 수행한다.
- 각 Skill은 다른 Skill을 호출해야만 동작하는 구조를 사용하지 않는다.

### 5.4 Multi-agent distribution

Canonical source는 `plugins/<plugin>/skills/<skill>/` 한 벌이다.

| Runtime | 등록 방식 |
| :--- | :--- |
| Claude Code | Marketplace plugin 설치 후 namespaced Skill 사용 |
| Codex | repository 또는 user `.agents/skills/<skill>/`에 Skill directory 등록 |
| Antigravity | workspace `.agents/skills/<skill>/` 또는 global `~/.gemini/config/skills/<skill>/`에 등록 |

README는 runtime별 등록·호출 방법을 설명하지만 copy/link를 자동화하지 않는다. Windows symlink 권한 문제 때문에 symlink만을 유일한 설치 방식으로 요구하지 않는다.

## 6. Plugin A: commit-commands

### 6.1 공통 safety contract

세 Skill은 다음 계약을 공유하되 각 `SKILL.md`에 필요한 부분을 자체 포함한다.

1. Read-only inspection을 먼저 수행한다.
2. mutation 전에 대상, 실행 명령, 영향, 제외 대상을 preview한다.
3. 사용자의 명시적 승인을 받은 뒤 실행한다.
4. 승인 후 HEAD 또는 working tree가 바뀌면 중단하고 preview를 다시 만든다.
5. unrelated 변경과 기존 staged 상태를 보존한다.
6. force, rebase, destructive fallback을 사용하지 않는다.
7. 실패한 단계 이후의 mutation은 수행하지 않는다.
8. 완료된 Git mutation을 임의 rollback하지 않고 현재 상태를 보고한다.
9. Partial staging 또는 기존 index 상태를 안전하게 분리할 수 없으면 staging을 변경하지 않고 사용자에게 범위를 확인한다.

### 6.2 commit

책임:

- `git status`, staged/unstaged diff, untracked file, 최근 commit style 확인
- 현재 task 관련 파일만 선택
- repository instruction과 기존 commit convention에 맞는 message 작성
- 포함·제외 파일, security scan 결과, message preview
- 승인 후 선택 파일만 stage하고 단일 atomic commit 생성

기본 commit message 정책:

1. 현재 project의 `AGENTS.md`, `CLAUDE.md`, `GEMINI.md`, `.ai/RULES.md`에 명시된 규칙
2. repository의 최근 commit style
3. fallback으로 Conventional Commits

금지:

- `git add .`
- `git add -A`
- unrelated file staging
- empty commit
- secret 의심 변경 commit
- file content 수정

Security check:

- repository가 제공하는 gitleaks 또는 동등 scanner가 있으면 우선 사용한다.
- scanner가 없으면 staged diff와 민감 파일명을 검사하고 deterministic 보장이 아님을 보고한다.
- secret 의심 항목이 있으면 commit하지 않는다.

### 6.3 commit-push-pr

책임:

- uncommitted 변경이 있으면 `commit`과 동일한 계약으로 commit 준비
- current branch upstream remote를 우선하여 provider 감지
- default branch에서 실행하면 새 feature branch 계획 제시
- normal push 후 provider CLI로 PR/MR 생성
- 생성 URL 또는 fallback 절차 보고

Provider adapter:

| Provider | Review request | CLI |
| :--- | :--- | :--- |
| GitHub | Pull Request | `gh pr create` |
| GitLab | Merge Request | `glab mr create` |
| Gitea | Pull Request | `tea pr create` (`pulls` alias 허용) |

Remote 결정 순서:

1. current branch upstream remote
2. 단일 configured remote
3. 복수 remote이면 사용자 선택

Default branch 결정 순서:

1. `<remote>/HEAD`
2. provider CLI가 반환하는 default branch
3. 실제 존재하는 `main` 또는 `master`
4. 결정 불가 시 중단

실행 순서:

```text
preflight
→ 전체 mutation plan 승인
→ 필요 시 branch 생성
→ commit
→ normal push
→ PR/MR 생성
→ URL 보고
```

Fallback:

- unknown provider: commit·push까지만 수행하고 review request 생성 방법 안내
- provider CLI 미설치 또는 미인증: push 후 수동 명령 또는 URL 안내
- push 실패: PR/MR 생성 금지
- PR/MR 생성 실패: commit과 push는 보존하고 재시도 방법 안내

금지:

- force push
- rebase
- 기존 branch overwrite
- provider CLI가 없는 상태에서 임의 API 호출

### 6.4 clean-gone

책임:

- stale remote-tracking ref, `[gone]` local branch, 연결 worktree 탐색
- 미병합 commit, dirty/current/locked worktree, branch SHA 확인
- 삭제 가능 대상과 제외 대상을 분리한 preview
- 승인 후 안전한 대상만 제거

허용 mutation:

- 필요한 경우 승인된 `git fetch --prune`
- clean worktree에 대한 `git worktree remove` without force
- merged branch에 대한 `git branch -d`

금지:

- `git worktree remove --force`
- `git branch -D`
- dirty, current, locked worktree 제거
- 미병합 branch 삭제
- 승인 후 SHA가 바뀐 branch 삭제

삭제는 대상별로 처리하며 첫 실패 시 중단한다. 이미 제거된 대상과 남은 대상을 구분해 보고한다.

## 7. Plugin B: agents-md-management

### 7.1 Instruction model

공통 규칙과 vendor 최적화 규칙을 분리한다.

```text
.ai/RULES.md   # 모든 runtime 공통
AGENTS.md      # AGENTS.md 표준 및 Codex 전용
CLAUDE.md      # Claude Code 전용
GEMINI.md      # Gemini/Antigravity 전용
```

Root reference:

- `CLAUDE.md`: `@./.ai/RULES.md` native import
- `GEMINI.md`: `@./.ai/RULES.md` native import
- `AGENTS.md`: 작업 전에 `.ai/RULES.md`를 읽고 준수하라는 명시적 instruction

Codex `AGENTS.md`에는 Claude/Gemini와 같은 native `@file` import가 없으므로 instruction-based reference는 best-effort다. Skill은 이 한계를 report하고 common rule을 vendor 파일로 복제하지 않는다.

Nested instruction:

- Root vendor 파일만 `.ai/RULES.md`를 reference한다.
- Nested vendor 파일은 해당 subtree 전용 override만 포함한다.
- 가장 가까운 nested instruction이 충돌 시 우선한다.
- 명시적 사용자 요청은 repository instruction보다 우선한다.

### 7.2 agents-md-management

책임:

- repository root와 nested directory의 세 vendor instruction 탐색
- directory별 effective hierarchy와 precedence 계산
- `.ai/RULES.md` reference 무결성 확인
- codebase와 command, architecture, environment, test instruction 정합성 평가
- 중복, 충돌, stale 정보, 과도한 verbosity 탐지
- quality report와 targeted diff 제안
- 승인된 파일만 수정하고 재검증

평가 항목:

| 항목 | 중요도 |
| :--- | :--- |
| Build/test/deploy command 정확성 | High |
| Architecture와 key path의 현재성 | High |
| 실행 가능한 구체성 | High |
| 공통/vendor rule 분류 정확성 | High |
| Nested scope와 precedence 일관성 | High |
| Non-obvious gotcha | Medium |
| 간결성 및 중복 없음 | Medium |

Workflow:

```text
root 결정
→ instruction discovery
→ effective hierarchy 계산
→ codebase/reference/충돌 평가
→ quality report
→ targeted diff
→ 승인
→ 대상 파일 drift 재검사
→ 수정
→ hierarchy/reference 재검증
```

제약:

- 누락 파일은 자동 생성하지 않고 생성 diff로 제안한다.
- 전체 rewrite보다 targeted change를 우선한다.
- unrelated 문서 개선을 수행하지 않는다.
- symlink 대상은 write하지 않고 실제 target과 위험을 보고한다.
- 승인 후 대상 파일이 변경되면 수정하지 않는다.
- 충돌을 임의 해석해 자동 병합하지 않는다.

Non-Git directory에서는 current directory를 root로 사용하되 Git 기반 current/stale 검증 한계를 표시한다.

### 7.3 revise-agents-md

책임:

- 현재 session에서 반복 사용 가치가 있는 learning 추출
- 공통, vendor, subtree scope 분류
- 기존 instruction과 중복·충돌 검사
- 최소 diff 제안
- 승인된 learning만 반영
- reference 무결성 재검사

분류:

| Learning | Target |
| :--- | :--- |
| 모든 runtime 공통 | `.ai/RULES.md` |
| Claude Code 전용 | `CLAUDE.md` |
| AGENTS.md 표준 또는 Codex 전용 | `AGENTS.md` |
| Gemini/Antigravity 전용 | `GEMINI.md` |
| 특정 subtree 전용 | 해당 nested vendor 파일 |

제외:

- one-off fix
- code에서 자명한 정보
- 검증되지 않은 추측
- secret, token, 개인 절대경로
- raw command output 또는 파일 내용 덤프

Scope가 불명확하면 한 번에 하나의 질문으로 확인한다. 기존 규칙과 충돌하면 변경하지 않고 선택을 요청한다. 전체 quality audit은 수행하지 않는다.

## 8. Error Handling

### 8.1 공통

- Read-only discovery 실패는 원인과 확인하지 못한 범위를 보고한다.
- 승인 전에 mutation을 실행하지 않는다.
- 승인 시점의 대상 상태가 달라지면 fail-closed한다.
- 부분 성공은 완료 항목과 미완료 항목을 분리해 보고한다.
- 실패를 숨기기 위한 destructive fallback을 사용하지 않는다.

### 8.2 Git workflow

| 조건 | 처리 |
| :--- | :--- |
| Git repository 아님 | 종료 |
| 변경 없음 | empty commit 없이 종료 |
| Partial staging 분리 불가 | index를 변경하지 않고 범위 확인 |
| detached HEAD | `commit`은 상태를 명시, `commit-push-pr`은 branch 선택 전 중단 |
| provider 불명 | push까지만 수행 가능 |
| provider CLI/인증 없음 | push 후 수동 생성 안내 |
| push 실패 | review request 생성 금지 |
| branch/worktree unsafe | 제외하고 이유 보고 |

### 8.3 Instruction management

| 조건 | 처리 |
| :--- | :--- |
| `.ai/RULES.md` 없음 | 생성 diff 제안 |
| vendor root file 없음 | 해당 wrapper 생성 diff 제안 |
| reference path 오류 | 수정 diff 제안 |
| nested conflict | precedence와 source를 report |
| symlink target | write 거부 |
| 승인 후 file drift | 수정 중단 후 새 diff 필요 |
| secret 포함 learning | 반영 거부 |

## 9. Verification

### 9.1 Structural validation

- Marketplace에 기존 plugin과 신규 plugin 2개가 등록된다.
- 신규 `plugin.json`, marketplace entry, README version이 일치한다.
- JSON과 YAML frontmatter가 parse된다.
- 모든 Skill name이 directory name과 일치한다.
- reference가 plugin directory 밖을 참조하지 않는다.
- 가능한 환경에서는 `claude plugin validate`를 실행한다.
- 기존 root plugin과 19개 Skill의 기능 diff가 없다.

### 9.2 Static safety scan

다음 pattern이 Skill instruction에 실행 가능한 동작으로 포함되지 않아야 한다.

```text
git add .
git add -A
git push --force
git push --force-with-lease
git branch -D
git worktree remove --force
```

또한 다음을 확인한다.

- 승인 전 mutation 없음
- secret 또는 credential 기록 지시 없음
- vendor 전용 `allowed-tools`와 Claude shell interpolation 없음
- 외부 plugin path 참조 없음

### 9.3 Scenario matrix

| Skill | 필수 scenario |
| :--- | :--- |
| `commit` | 관련·무관 변경 혼재, staged/unstaged 혼재, 변경 없음, secret 의심, 승인 후 state drift |
| `commit-push-pr` | GitHub/GitLab/Gitea, 복수 remote, default branch, CLI/인증 없음, push 실패 |
| `clean-gone` | safe gone branch, 미병합 commit, dirty/locked worktree, current branch, SHA drift, 대상 없음 |
| `agents-md-management` | root+nested hierarchy, common file 누락, reference 오류, vendor conflict, symlink |
| `revise-agents-md` | common/vendor/subtree 분류, 중복, secret, scope 불명, 변경 거절 |

실제 remote push와 PR/MR 생성은 자동 test에서 제외한다. Command plan과 provider adapter mapping을 검증하고 실제 external mutation은 사용자가 명시적으로 요청한 smoke test에서만 수행한다.

### 9.4 Multi-agent compatibility

Claude Code, Codex, Antigravity에서 다음을 확인한다.

1. Skill discovery 또는 explicit invocation
2. 동일 `SKILL.md` 해석
3. Read-only phase와 approval gate 분리
4. 한국어 결과 보고
5. 없는 tool 또는 CLI에 대한 안전한 fallback

기존 `/zzizily:verify`를 사용해 Codex와 Antigravity 관점의 static cross-review를 수행한다.

## 10. License 및 Attribution

두 upstream plugin은 Apache License 2.0이다.

- 각 신규 plugin에 Apache 2.0 `LICENSE`를 포함한다.
- 각 plugin README에 원본 repository와 변경 사실을 명시한다.
- upstream을 직접 변형한 각 `SKILL.md`에 원본과 수정 사실을 식별할 수 있는 attribution section을 둔다.
- upstream에 별도 `NOTICE`가 없으므로 복제할 NOTICE는 없다.

## 11. 완료 기준

1. `commit-commands@zzizily`와 `agents-md-management@zzizily`를 독립 설치할 수 있다.
2. 5개 Skill이 각 책임 밖의 기능을 수행하지 않는다.
3. `.ai/RULES.md` 공통 규칙과 vendor instruction 경계가 유지된다.
4. 모든 mutation이 preview와 승인 후 실행된다.
5. `clean-gone`이 force option 없이 안전한 대상만 제거한다.
6. `commit-push-pr`이 GitHub, GitLab, Gitea를 감지하고 CLI 부재 시 안전하게 fallback한다.
7. Claude Code, Codex, Antigravity 등록·호출 방법이 문서화된다.
8. 기존 `zzizily` plugin 사용자에게 breaking change가 없다.
9. 신규 plugin version metadata가 각각 일치한다.
10. License와 attribution 조건을 충족한다.

## 12. 후속 작업

이번 이식 완료 후 기존 19개 Skill을 domain별 plugin으로 분리하는 별도 brainstorming → spec → plan cycle을 시작한다. 본 spec에서는 기존 Skill의 이동, namespace 변경, migration을 수행하지 않는다.

## 13. 근거 자료

- Anthropic commit-commands: <https://github.com/anthropics/claude-plugins-official/tree/main/plugins/commit-commands>
- Anthropic claude-md-management: <https://github.com/anthropics/claude-plugins-official/tree/main/plugins/claude-md-management>
- Claude Code plugin marketplace: <https://code.claude.com/docs/en/plugin-marketplaces>
- Claude Code instruction import: <https://code.claude.com/docs/en/memory>
- OpenAI Codex Skills: <https://developers.openai.com/codex/skills/>
- Google Antigravity Skills: <https://antigravity.google/docs/skills>
- AGENTS.md 표준: <https://agents.md/>
- GitHub CLI PR 생성: <https://cli.github.com/manual/gh_pr_create>
- GitLab CLI MR 생성: <https://docs.gitlab.com/cli/mr/create/>
- Gitea Tea: <https://about.gitea.com/products/tea/>
