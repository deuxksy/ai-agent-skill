---
name: tag-release
description: "Use when the user asks to create a version tag and publish a GitHub release after verifying a clean, version-synced repository state."
---

# Tag and Release

버전 tag 생성 → tag push → GitHub release 발행 workflow. 모든 mutation 전에 승인받는다. 버전 bump 자체는 이 스킬 범위 밖이다.

## 1. Preflight (read-only)

1. Git root, HEAD, current branch, status, upstream, remote URL을 확인한다.
2. Working tree가 clean하고 staged/unstaged/untracked 변경이 없는지 확인한다. 있으면 중단하고 남은 변경을 보고한다.
3. HEAD가 upstream에 push되어 local-ahead commit이 없는지 확인한다. 있으면 중단하고 push를 안내한다.
4. Repository가 unified version 매니페스트 정책을 사용하면 버전 sync를 검증한다.
   - Marketplace manifest(`.claude-plugin/marketplace.json`, `.agents/plugins/marketplace.json`)의 등록 plugin version이 전부 동일한 unified version인지 확인한다.
   - 각 plugin별 manifest(`plugins/*/.claude-plugin/plugin.json`, `plugins/*/.codex-plugin/plugin.json`)의 version이 marketplace와 일치하는지 확인한다.
   - Marketplace 미등록 local-only plugin은 검증 대상에서 제외한다.
   - 불일치가 있으면 중단하고 파일, 실제 version, 기대값을 보고한다. 버전 수정은 수행하지 않는다.
5. Tag 이름을 unified version 앞에 `v`를 붙인 `vX.Y.Z`로 확정한다. Unified version 정책이 없으면 사용자에게 tag 이름을 확인받는다.
6. 동일 이름의 기존 tag(`git tag -l`)와 기존 release(`gh release view`)가 없는지 확인한다. 있으면 중단한다.
7. `gh` CLI 존재와 인증 상태를 확인한다.

## 2. Release notes draft

1. Release notes commit 범위를 직전 tag부터 HEAD까지로 한다. 기존 tag가 없으면 사용자에게 시작 commit을 질문한다.
2. 범위 내 `git log`를 Conventional Commits type(feat, fix, docs, chore, 기타)별로 그룹핑한다.
3. Commit message 원문을 그대로 항목으로 사용한다. 별도 언어 규칙이 없으면 원문 언어를 유지한다.

## 3. Preview and approval

다음을 한 번에 제시한다.

- Tag 이름, 대상 commit SHA, release title
- 버전 sync 검증 결과와 확정한 unified version
- Release notes 전문
- exact `git tag -a`, `git push origin <tag>`, `gh release create` 명령

사용자의 명시적 승인 전에는 tag 생성, tag push, release 생성을 하지 않는다.

## 4. Execute

1. 승인 직후 HEAD, working tree 상태, tag 존재 여부, 버전 sync를 같은 방식으로 다시 확인한다. 달라졌으면 중단하고 preview를 갱신한다.
2. `git tag -a vX.Y.Z -m "<message>"`로 annotated tag를 만든다.
3. `git push origin refs/tags/vX.Y.Z`로 tag만 push한다.
4. Push 성공 후에만 `gh release create vX.Y.Z --title "<title>" --notes "<notes>"`로 release를 발행한다.
5. Tag URL과 release URL을 보고한다.

## 5. Failure handling

- Tag 생성 실패: 이후 단계 중단.
- Tag push 실패: release 생성 금지, 재시도 방법 안내.
- Release 생성 실패: tag를 rollback하지 않고 수동 release URL과 절차를 안내한다.
- `gh` CLI 또는 인증 부재: tag push까지만 수행하고 web release 생성 URL을 안내한다.

## Safety

- 기존 tag를 수정하거나 삭제하지 않는다 (`git tag -f`, `git tag -d`, `git push --delete` 금지).
- Dirty working tree나 local-ahead commit, 버전 불일치 상태에서 tag를 만들지 않는다.
- 버전 매니페스트를 수정하지 않는다.
- Force push를 사용하지 않는다.
