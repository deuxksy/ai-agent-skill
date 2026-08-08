---
name: clean-gone
description: "Use when the user asks to clean stale or gone Git branches without force deletion."
---

# Clean Gone Branches Safely

Remote에서 사라진 local branch를 강제 삭제 없이 정리한다.

## 1. Read-only discovery

1. Git root, current branch, remote, remote-tracking refs를 확인한다.
2. Local branch의 upstream 상태는 machine-readable ref 정보 또는 `git branch -vv`로 확인한다.
3. 모든 worktree의 porcelain branch ref/path, lock, dirty 상태를 확인한다.
4. 후보마다 current branch 제외 여부와 local branch tip SHA snapshot을 기록하고, default/base tip SHA에 `git merge-base --is-ancestor <branch-sha> <base-sha>`로 완전 merge를 검증한다.
5. 모든 porcelain worktree의 branch ref/path를 candidate branch snapshot과 1:1 매핑하고 detached/unrelated worktree는 제외한다.
6. Linked worktree는 lock reason과 `git status --porcelain`을 확인한다.
7. Remote ref 최신화가 필요하면 prune dry-run 결과와 실제 prune 계획을 분리한다.

## 2. Safety classification

각 후보를 다음 중 하나로 분류한다.

- 삭제 가능: upstream gone, current branch 아님, merged, worktree 없음 또는 해당 candidate에 1:1 매핑된 clean·unlocked worktree.
- 제외: 미병합 commit, current branch, dirty/locked/detached/unrelated worktree, SHA 또는 branch mapping 확인 실패.

Branch별 SHA와 제외 사유를 기록한다.

## 3. Preview and approval

다음을 제시한다.

- Remote prune 필요 여부와 exact command
- 해당 validated branch 후보에 1:1 매핑된 clean worktree path와 `git worktree remove -- <safely-quoted-path>` exact command
- 삭제할 merged local branch, snapshot SHA와 `git branch -d -- <safely-quoted-validated-branch>` exact command
- 제외 대상과 이유

Path와 branch name은 active shell에 맞게 quote/escape한 개별 argv로 전달한다. Placeholder를 literal로 전달하거나 command 문자열로 조합하거나 eval하지 않는다.

승인 전에는 prune, worktree 제거, branch 삭제를 하지 않는다.

## 4. Execute

1. 승인 직후 candidate SHA, fully merged, upstream gone, current branch 여부, mapped worktree clean/unlocked 및 branch mapping을 다시 확인한다.
2. 하나라도 Drift가 있으면 전체 실행을 중단한다.
3. 승인된 경우에만 remote refs를 prune한다.
4. actual prune 직후 branch/worktree 제거 전 candidate SHA, fully merged, upstream still gone, current branch 아님, mapped worktree clean/unlocked 및 branch mapping을 다시 검증한다.
5. 하나라도 Drift가 있으면 전체 실행을 중단한다.
6. 각 worktree 제거 직전 candidate SHA, base ancestry, upstream gone, current branch 아님, mapped worktree branch ref·HEAD의 candidate snapshot 일치, clean/unlocked 및 branch mapping을 다시 검증한다.
7. 검증된 path만 active shell의 개별 argv로 전달해 `git worktree remove -- <safely-quoted-path>`로 제거한다.
8. 각 branch 삭제 직전 candidate SHA, base ancestry, upstream gone, current branch 아님과 전체 worktree mapping을 다시 확인한다. Mapped worktree가 존재하면 branch ref·HEAD의 candidate snapshot 일치와 clean/unlocked 상태를 확인한 뒤 branch 삭제를 중단하며, 원래 없었거나 승인된 remove로 제거한 mapping이 여전히 없는 경우만 진행한다.
9. 검증된 branch name만 active shell의 개별 argv로 전달해 `git branch -d -- <safely-quoted-validated-branch>`로 삭제한다.
10. 각 mismatch 또는 첫 실패 시 remaining mutation을 중단하고 이미 제거된 대상, 남은 대상, 현재 partial state를 보고한다.

## Safety

- Force option을 사용하지 않는다.
- `git rebase`를 포함한 history-rewriting command를 사용하지 않는다.
- Dirty, locked, current worktree를 제거하지 않는다.
- 미병합 branch를 삭제하지 않는다.
- Path 또는 branch name을 command 문자열로 조합하거나 eval하지 않는다.
- 안전 검사를 우회하는 대체 명령을 실행하지 않는다.

## Attribution

Adapted from Anthropic `commit-commands/commands/clean_gone.md` under Apache License 2.0. Modified to remove force deletion, add merge/worktree checks, state-drift detection, preview, and approval.
