---
name: commit-push
description: "Use when the user asks to commit task-related Git changes and push them to the remote without opening a PR/MR."
---

# Commit and Push

현재 task와 관련된 변경만 commit하고 normal push한다. PR/MR 생성은 담당하지 않는다 — review request가 필요하면 `commit-push-pr`을 사용한다. Commit과 push 전체의 mutation plan을 먼저 승인받는다.

## 1. Read-only preflight

1. Git repository root, current branch/HEAD, status, upstream, remote URL을 확인한다.
2. staged, unstaged, untracked 변경을 각각 확인한다.
3. 최근 commit 10개의 style과 적용 가능한 project instruction을 확인한다.
4. 현재 task에 직접 관련된 파일만 `포함`으로 분류하고 나머지는 `제외`한다.
5. Partial staging 또는 기존 index 상태를 안전하게 분리할 수 없으면 index를 변경하지 않고 범위를 질문한다.
6. Current branch에 upstream이 없으면 push 대상 remote·branch와 upstream 설정 포함 여부를 preview에 명시한다.
7. Upstream이 current branch보다 앞서 있으면(behind) 중단하고 상황만 보고한다. 자동 pull·merge·rebase는 하지 않는다.
8. Pathspec을 받는 Git command는 `git diff -- <paths>`처럼 option terminator를 사용하고 path를 active shell의 개별 argv로 전달한다.

## 2. Security check

1. Repository가 제공하는 gitleaks 또는 동등 scanner가 있으면 사용한다.
2. Scanner가 없으면 승인 대상의 tracked diff와 승인 대상 untracked 파일의 실제 content를 read-only로 검사한다. Binary 또는 읽을 수 없는 승인 대상 untracked 파일이면 중단하고, deterministic scanner 부재 한계를 preview에 명시한다.
3. Secret, token, credential, private key 의심 항목이 있으면 중단한다.

## 3. Preview and approval

다음을 한 번에 제시한다.

- 포함 파일과 선택 이유, 제외 파일과 제외 이유
- Security scan 결과와 한계
- Active shell에 맞게 각 path를 quote/escape한 exact staging argv (`git add -- <paths>`)
- Proposed commit message
- Exact push 명령 — upstream이 있으면 `git push`, 없으면 승인받은 `git push -u <remote> <branch>`

사용자의 명시적 승인 전에는 stage, commit, push를 하지 않는다.

## 4. Execute

1. 승인 직후 HEAD, branch, upstream, remote URL과 working tree 상태를 다시 확인한다. 승인 시점과 달라졌으면 중단하고 preview를 갱신한다.
2. 포함 파일을 active shell의 개별 argv로 전달해 `git add -- <paths>`로 stage한다. Working tree 전체 shorthand는 사용하지 않는다.
3. Staged diff가 승인 범위와 일치하는지 확인한다.
4. Project instruction, 최근 repository style, Conventional Commits 순으로 message 규칙을 적용한다. 별도 규칙이 없으면 type은 영어, subject는 한국어로 작성한다. Empty commit을 만들지 않는다.
5. Commit 실패 시 index를 임의 rollback하지 않고 현재 상태를 보고한다.
6. Commit 성공 후에만 승인된 대상으로 normal push한다. Push 실패 시 commit을 rollback하지 않고 실패 원인과 재시도 방법을 보고한다.

## 5. Result

Commit SHA, message, 포함 파일, push 결과(remote·branch·upstream 설정 여부), 남아 있는 staged/unstaged 변경을 보고한다.

## Safety

- Force push, rebase, branch overwrite를 하지 않는다.
- Push 전 자동 pull·merge·rebase를 하지 않는다.
- Unrelated 변경을 stage하거나 commit하지 않고, 기존 staged 변경을 자동 unstage하지 않는다.
- File content를 수정하지 않는다.
- Secret 의심 변경을 commit하거나 push하지 않는다.
- Path를 command 문자열로 조합하거나 eval하지 않는다.

## Attribution

Adapted from Anthropic `commit-commands` under Apache License 2.0. Modified for runtime-neutral Agent Skills, push-only flow, selective staging, security checks, and approval gates.
