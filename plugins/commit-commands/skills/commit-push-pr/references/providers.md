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
- GitLab CLI/인증 부재 시 선택된 GitLab HTTPS/SSH remote URL에서 scheme, host, port, 전체 project path(subgroup 포함)를 보존하고 terminal `.git`만 제거해 project web URL을 얻는다. source와 base branch를 URL-encode하여 `<project-web-url>/-/merge_requests/new?merge_request[source_branch]=<encoded-source>&merge_request[target_branch]=<encoded-base>` exact manual MR URL을 preview한다.
- GitLab remote URL 또는 branch를 신뢰성 있게 parse/encode할 수 없으면 URL을 임의로 만들지 않는다. 사용자에게 exact project web URL을 요청하고, preview에 project web URL, source branch, base branch와 함께 해당 project의 UI에서 **New merge request**를 선택해 source와 target을 지정하는 절차를 제시한다.
- GitHub/Gitea CLI/인증 부재 시 provider가 확인한 exact compare/create URL이 있으면 preview한다. 없으면 endpoint 형식을 추측하지 않고 project web URL, source branch, base branch와 해당 provider UI에서 Pull Request를 생성하는 절차를 preview한다.
- API를 직접 호출하거나 credential을 요청·출력하지 않는다.
