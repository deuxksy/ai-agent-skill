---
name: commit
description: "Use when the user asks to commit task-related Git changes while preserving unrelated or pre-staged work."
---

# Commit

현재 task와 관련된 변경만 단일 atomic commit으로 만든다. 파일 내용을 수정하지 않는다.

## 1. Read-only preflight

1. Git repository root, current branch/HEAD, status를 확인한다.
2. staged, unstaged, untracked 변경을 각각 확인한다.
3. 최근 commit 10개의 style과 적용 가능한 project instruction을 확인한다.
4. 현재 task에 직접 관련된 파일만 `포함`으로 분류하고 나머지는 `제외`한다.
5. partial staging 또는 기존 index 상태를 안전하게 분리할 수 없으면 index를 변경하지 않고 범위를 질문한다.
6. Pathspec을 받는 Git command는 `git diff -- <paths>`처럼 option terminator를 사용하고 path를 active shell의 개별 argv로 전달한다.

## 2. Security check

1. Repository가 제공하는 gitleaks 또는 동등 scanner가 있으면 사용한다.
2. Scanner가 없으면 승인 대상의 tracked diff와 승인 대상 untracked 파일의 실제 content를 read-only로 검사한다. Binary 또는 읽을 수 없는 승인 대상 untracked 파일이면 중단하고, deterministic scanner 부재 한계를 preview에 명시한다.
3. Secret, token, credential, private key 의심 항목이 있으면 중단한다.

## 3. Preview and approval

다음을 한 번에 제시한다.

- 포함 파일과 선택 이유
- 제외 파일과 제외 이유
- security scan 결과와 한계
- active shell에 맞게 각 path를 quote/escape한 exact staging argv (`git add -- <paths>`)
- proposed commit message

사용자의 명시적 승인 전에는 stage 또는 commit하지 않는다.

## 4. Commit

1. 승인 직후 HEAD와 working tree 상태를 다시 확인한다.
2. 승인 시점과 달라졌으면 중단하고 preview를 갱신한다.
3. 포함 파일을 active shell의 개별 argv로 전달해 `git add -- <paths>`로 stage한다. Working tree 전체 shorthand는 사용하지 않는다.
4. staged diff가 승인 범위와 일치하는지 확인한다.
5. Project instruction, 최근 repository style, Conventional Commits 순으로 message 규칙을 적용한다. 별도 규칙이 없으면 type은 영어, subject는 한국어로 작성한다.
6. Empty commit을 만들지 않는다.
7. Commit 실패 시 index를 임의 rollback하지 않고 현재 상태를 보고한다.

## 5. Result

Commit SHA, message, 포함 파일, 남아 있는 staged/unstaged 변경을 보고한다.

## Safety

- Unrelated 변경을 stage하거나 commit하지 않는다.
- 기존 staged 변경을 자동 unstage하지 않는다.
- File content를 수정하지 않는다.
- Secret 의심 변경을 commit하지 않는다.
- Path를 command 문자열로 조합하거나 eval하지 않는다.
- 강제 또는 history rewrite Git option을 사용하지 않는다.

## Attribution

Adapted from Anthropic `commit-commands/commands/commit.md` under Apache License 2.0. Modified for runtime-neutral Agent Skills, selective staging, security checks, and approval gates.
