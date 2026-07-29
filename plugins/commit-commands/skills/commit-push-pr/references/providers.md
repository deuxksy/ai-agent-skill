# Git Provider Adapters

## Provider detection

1. Current branch upstream remote를 우선한다.
2. Upstream이 없고 remote가 하나면 그 remote를 사용한다.
3. Remote가 여러 개면 mutation 전에 사용자에게 선택을 요청한다.
4. SSH와 HTTPS remote URL의 hostname을 정규화한다.
5. `github.com` 또는 GitHub Enterprise로 확인되면 GitHub, GitLab host로 확인되면 GitLab, Gitea API/banner 또는 configured `tea` login과 일치하면 Gitea다.
6. Self-hosted provider를 확정할 수 없으면 unknown으로 처리한다.

## Review request adapters

| Provider | Probe | Create |
| :--- | :--- | :--- |
| GitHub | `gh auth status` | `gh pr create` |
| GitLab | `glab auth status` | `glab mr create` |
| Gitea | `tea login list` | `tea pr create` (`pulls` alias 허용) |

## Default branch

1. `<remote>/HEAD`
2. Provider CLI가 반환하는 default branch
3. 실제 존재하는 `main`
4. 실제 존재하는 `master`
5. 결정 불가 시 중단

## Fallback

- Unknown provider 또는 CLI/인증 부재 시 normal push까지만 수행한다.
- 수동 PR/MR 생성 명령 또는 compare URL을 안내한다.
- API를 직접 호출하거나 credential을 요청·출력하지 않는다.
