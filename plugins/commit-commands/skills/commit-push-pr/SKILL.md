---
name: commit-push-pr
description: "Use when the user asks to commit, push, and open a GitHub PR, GitLab MR, or Gitea PR."
---

# Commit, Push, and Open Review Request

Commit → normal push → PR/MR 생성 workflow. 세 단계 전체의 mutation plan을 먼저 승인받는다.

## 1. Preflight

1. Git root, HEAD, current branch, status, upstream, remote URL을 확인한다.
2. Candidate tracked working-tree diff, index diff, untracked file의 실제 content와 file type을 읽고 task 관련 `포함`과 `제외`로 분류한다.
3. Candidate별 cryptographic content hash 또는 byte-identical diff snapshot을 만든다. `git status`는 content identity가 아니다.
4. 기존 staged와 unrelated 변경은 보존한다. Partial staged 상태나 동일 path의 index/working-tree 내용을 승인 범위와 안전하게 분리할 수 없으면 index를 변경하지 않고 중단한다.
5. Repository scanner가 있으면 candidate content를 검사한다. 없으면 tracked/index diff와 untracked 실제 content를 read-only로 검사하고, binary/unreadable content 또는 secret·token·credential·private key 의심 항목이 있으면 중단한다.
6. `references/providers.md`에 따라 selected provider, remote, hostname, repository, 실제 default branch ref, CLI/인증 상태를 확인한다.
7. Detached HEAD, 선택 불가능한 remote, 확인되지 않은 default branch ref에서는 중단한다.
8. Current branch가 default branch이면 새 feature branch 이름을 제안한다.

## 2. Preview and approval

다음을 한 번에 제시한다.

- 포함·제외 파일과 commit message
- Candidate tracked/index/untracked content identity와 security scan 결과·한계
- 생성할 branch와 base branch
- exact staging, commit, normal push 명령
- provider와 authentication 상태 및 hostname, repository, source/base branch, title/body에 고정된 exact PR/MR 명령
- CLI/인증 부재 시 exact manual review URL 또는 URL을 안전하게 구성할 수 없을 때의 project web URL·source/base branch·사용자 실행 UI 절차

사용자의 명시적 승인 전에는 branch 생성, stage, commit, push, PR/MR 생성을 하지 않는다.

## 3. Execute

1. 승인 직후 HEAD, branch, upstream, selected remote URL/default ref와 모든 tracked/index/untracked content identity를 같은 방식으로 다시 확인한다. Hash 또는 byte-identical diff가 다르면 status가 같아도 중단한다.
2. 필요한 경우 승인된 이름으로 branch를 생성한다.
3. 승인된 path만 명시해 stage하고, 해당 path의 cached diff와 commit 예정 diff가 approved diff와 byte-identical인지 확인한다. 기존 unrelated staged content는 commit 대상에서 제외하고 보존한다. 일치와 분리를 증명할 수 없으면 commit하지 않는다.
4. 승인된 content와 message만 commit한다.
5. 승인된 remote/current branch로 normal push한다.
6. Push 성공 후에만 provider CLI로 PR/MR을 생성한다. Probe와 create 명령은 승인된 hostname, repository, source/base branch, title/body를 explicit argument로 사용한다.
7. PR/MR title, summary, test plan은 전체 branch diff와 repository template을 반영한다. 별도 언어 규칙이 없으면 한국어로 작성한다.

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
