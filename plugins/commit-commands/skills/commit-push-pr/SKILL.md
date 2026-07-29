---
name: commit-push-pr
description: "Use when the user asks to commit, push, and open a GitHub PR, GitLab MR, or Gitea PR."
---

# Commit, Push, and Open Review Request

Commit → normal push → PR/MR 생성 workflow. 세 단계 전체의 mutation plan을 먼저 승인받는다.

## 1. Preflight

1. Git root, HEAD, current branch, status, upstream, remote URL을 확인한다.
2. 변경이 있으면 `commit` Skill과 동일하게 task 관련 파일만 분류하고 security 검사한다. 기존 staged와 unrelated 변경은 보존한다.
3. `references/providers.md`에 따라 provider, remote, default branch, CLI/인증 상태를 확인한다.
4. Detached HEAD, 선택 불가능한 remote, 결정 불가능한 default branch에서는 중단한다.
5. Current branch가 default branch이면 새 feature branch 이름을 제안한다.

## 2. Preview and approval

다음을 한 번에 제시한다.

- 포함·제외 파일과 commit message
- 생성할 branch와 base branch
- exact commit, normal push, PR/MR 명령
- provider와 authentication 상태
- CLI/인증 부재 시 exact manual review URL 또는 URL을 안전하게 구성할 수 없을 때의 project web URL·source/base branch·사용자 실행 UI 절차

사용자의 명시적 승인 전에는 branch 생성, stage, commit, push, PR/MR 생성을 하지 않는다.

## 3. Execute

1. 승인 직후 HEAD, status, remote를 다시 확인한다. Drift가 있으면 중단한다.
2. 필요한 경우 승인된 이름으로 branch를 생성한다.
3. 변경이 있으면 승인된 범위만 commit한다.
4. 승인된 remote/current branch로 normal push한다.
5. Push 성공 후에만 provider CLI로 PR/MR을 생성한다.
6. PR/MR title, summary, test plan은 전체 branch diff와 repository template을 반영한다. 별도 언어 규칙이 없으면 한국어로 작성한다.

## 4. Failure handling

- Branch 또는 commit 실패: 이후 단계 중단.
- Push 실패: PR/MR 생성 금지.
- PR/MR 실패: commit·push를 rollback하지 않고 재시도 방법 안내.
- Unknown provider 또는 CLI/인증 부재: push까지만 수행하고 `references/providers.md`에 따른 exact manual review URL 또는 fail-safe manual UI 절차를 안내한다.

## Safety

- Force push, rebase, branch overwrite를 하지 않는다.
- Provider API를 직접 호출하지 않는다.
- Credential을 요청하거나 출력하지 않는다.
- 승인 범위를 벗어난 mutation을 하지 않는다.

## Attribution

Adapted from Anthropic `commit-commands/commands/commit-push-pr.md` under Apache License 2.0. Modified for runtime-neutral skills, GitHub/GitLab/Gitea adapters, selective staging, and approval gates.
