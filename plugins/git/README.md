# git

안전한 Git commit, PR/MR, stale branch 정리, 버전 tag와 release 발행을 제공하는 runtime-neutral Agent Skills plugin.

**Version:** 1.15.0

## Skills

| Skill | 설명 |
| :--- | :--- |
| `commit` | 현재 task 관련 변경만 preview·승인 후 commit |
| `commit-push-pr` | 관련 변경 commit → normal push → GitHub PR/GitLab MR/Gitea PR 생성 |
| `clean-gone` | merged·clean `[gone]` branch/worktree만 preview·승인 후 안전하게 제거 |
| `tag-release` | 버전 sync 검증 후 annotated tag push → GitHub release 발행 (notes는 Conventional Commits 기반 생성) |

## Claude Code

```bash
claude plugin install git@zzizily
```

호출:

```text
/git:commit
/git:commit-push-pr
/git:clean-gone
/git:tag-release
```

## Codex와 Antigravity

Canonical Skill source는 `skills/<skill-name>/`이다. Runtime별 복제본은 유지하지 않는다.

| Runtime | Repository scope | User/global scope | 호출 |
| :--- | :--- | :--- | :--- |
| Codex | `<repo>/.agents/skills/<skill-name>/` | `$HOME/.agents/skills/<skill-name>/` | `$<skill-name>` 또는 implicit |
| Antigravity | `<workspace>/.agents/skills/<skill-name>/` | `~/.gemini/config/skills/<skill-name>/` | Skill 이름 명시 또는 implicit |

Codex marketplace entry는 `.agents/plugins/marketplace.json`이다. Repository clone에서 다음 순서로 등록·설치한다.

```bash
codex plugin marketplace add .agents/plugins
codex plugin add git@zzizily
```

다른 project에서 사용할 때 필요한 Skill directory를 위 location에 copy하거나 지원되는 link 방식으로 등록한다. Windows에서는 symlink 권한이 필요할 수 있으므로 copy 방식도 지원한다.

## Provider CLI

| Provider | CLI | Review request |
| :--- | :--- | :--- |
| GitHub | `gh` | Pull Request |
| GitLab | `glab` | Merge Request |
| Gitea | `tea` | Pull Request |

CLI가 없거나 인증되지 않았으면 push까지만 수행하고 수동 생성 절차를 안내한다.

## Safety

- Read-only inspection 우선
- Mutation plan 승인 필수
- Unrelated/staged 변경 보존
- Force/history rewrite 금지

`clean-gone`은 미병합 branch, dirty/locked worktree, current branch를 제거하지 않으며 force option을 제공하지 않는다.

## Requirements

- Git
- Review request 생성 시 provider에 맞는 authenticated CLI: `gh`, `glab`, 또는 `tea`
- Secret scan 강화 시 gitleaks 또는 repository가 지정한 scanner

## Limitations

- Runtime별 자동 installer를 제공하지 않는다.
- Provider CLI가 없으면 push까지만 수행한다.
- 실제 remote mutation integration test는 포함하지 않는다.

## Attribution

Adapted from Anthropic
[`git`](https://github.com/anthropics/claude-plugins-official/tree/main/plugins/git)
under Apache License 2.0. This version changes the original commands into runtime-neutral, approval-gated Agent Skills.
