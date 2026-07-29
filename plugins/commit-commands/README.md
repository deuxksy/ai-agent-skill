# commit-commands

안전한 Git commit, PR/MR, stale branch 정리를 제공하는 runtime-neutral Agent Skills plugin.

**Version:** 1.0.0

## Skills

| Skill | 설명 |
| :--- | :--- |
| `commit` | 현재 task 관련 변경만 preview·승인 후 commit |

## Claude Code

```bash
claude plugin install commit-commands@zzizily
```

호출: `/commit-commands:commit`

## Safety

- Read-only inspection 우선
- Mutation plan 승인 필수
- Unrelated/staged 변경 보존
- Force/history rewrite 금지

## Attribution

Adapted from Anthropic
[`commit-commands`](https://github.com/anthropics/claude-plugins-official/tree/main/plugins/commit-commands)
under Apache License 2.0. This version changes the original commands into runtime-neutral, approval-gated Agent Skills.
