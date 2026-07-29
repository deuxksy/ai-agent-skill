# commit-commands

안전한 Git commit, PR/MR, stale branch 정리를 제공하는 runtime-neutral Agent Skills plugin.

**Version:** 1.0.0

## Skills

| Skill | 설명 |
| :--- | :--- |
| `commit` | 현재 task 관련 변경만 preview·승인 후 commit |
| `commit-push-pr` | 관련 변경 commit → normal push → GitHub PR/GitLab MR/Gitea PR 생성 |

## Claude Code

```bash
claude plugin install commit-commands@zzizily
```

호출:

```text
/commit-commands:commit
/commit-commands:commit-push-pr
```

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

## Attribution

Adapted from Anthropic
[`commit-commands`](https://github.com/anthropics/claude-plugins-official/tree/main/plugins/commit-commands)
under Apache License 2.0. This version changes the original commands into runtime-neutral, approval-gated Agent Skills.
