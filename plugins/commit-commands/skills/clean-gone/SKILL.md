---
name: clean-gone
description: "Use when the user asks to clean stale or gone Git branches without force deletion."
---

# Clean Gone Branches Safely

Remote에서 사라진 local branch를 강제 삭제 없이 정리한다.

## 1. Read-only discovery

1. Git root, current branch, remote, remote-tracking refs를 확인한다.
2. Local branch의 upstream 상태는 machine-readable ref 정보 또는 `git branch -vv`로 확인한다.
3. 모든 worktree의 path, branch, lock, dirty 상태를 확인한다.
4. 후보마다 current branch 제외 여부와 local branch tip SHA snapshot을 기록하고, default/base tip SHA에 `git merge-base --is-ancestor <branch-sha> <base-sha>`로 완전 merge를 검증한다.
5. Linked worktree는 lock reason과 `git status --porcelain`을 확인한다.
6. Remote ref 최신화가 필요하면 prune dry-run 결과와 실제 prune 계획을 분리한다.

## 2. Safety classification

각 후보를 다음 중 하나로 분류한다.

- 삭제 가능: upstream gone, current branch 아님, merged, worktree 없음 또는 clean·unlocked worktree.
- 제외: 미병합 commit, current branch, dirty/locked worktree, SHA 확인 실패.

Branch별 SHA와 제외 사유를 기록한다.

## 3. Preview and approval

다음을 제시한다.

- Remote prune 필요 여부와 exact command
- 제거할 clean worktree path와 `git worktree remove <path>` exact command
- 삭제할 merged local branch, snapshot SHA와 `git branch -d <branch>` exact command
- 제외 대상과 이유

승인 전에는 prune, worktree 제거, branch 삭제를 하지 않는다.

## 4. Execute

1. 승인 직후 branch SHA와 worktree 상태를 다시 확인한다.
2. Snapshot SHA, base merge 결과, current branch, worktree lock/dirty 상태 중 하나라도 Drift가 있으면 전체 실행을 중단한다.
3. 승인된 경우에만 remote refs를 prune한다.
4. Clean·unlocked worktree를 일반 remove로 제거한다.
5. Merged branch를 safe delete로 제거한다.
6. 첫 실패 시 중단하고 이미 제거된 대상과 남은 대상을 구분해 보고한다.

## Safety

- Force option을 사용하지 않는다.
- Dirty, locked, current worktree를 제거하지 않는다.
- 미병합 branch를 삭제하지 않는다.
- 안전 검사를 우회하는 대체 명령을 실행하지 않는다.

## Attribution

Adapted from Anthropic `commit-commands/commands/clean_gone.md` under Apache License 2.0. Modified to remove force deletion, add merge/worktree checks, state-drift detection, preview, and approval.
