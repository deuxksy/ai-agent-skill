# Git Provider Adapters

## Provider detection

1. Current branch upstream remote를 우선한다.
2. Upstream이 없고 remote가 하나면 그 remote를 사용한다.
3. Remote가 여러 개면 mutation 전에 사용자에게 선택을 요청한다.
4. SSH와 HTTPS remote URL의 hostname을 정규화한다.
5. `github.com` 또는 GitHub Enterprise로 확인되면 GitHub, GitLab host로 확인되면 GitLab, Gitea API/banner 또는 configured `tea` login과 일치하면 Gitea다.
6. Self-hosted provider를 확정할 수 없으면 unknown으로 처리한다.

## Review request adapters

명령과 flags는 installed CLI의 `--help` 또는 공식 CLI 문서로 먼저 검증한다. Probe는 read-only이며 selected hostname/repository를 explicit argument로 사용한다. Create는 승인된 hostname, repository, source/base branch, title/body를 모두 고정한다. Argument를 생략한 bare auth/repository probe 또는 bare create는 사용하지 않는다. 검증할 수 없는 command나 flag는 추측하지 않고 unavailable로 처리한다.

| Provider | Read-only probe | Create |
| :--- | :--- | :--- |
| GitHub | `gh auth status --active --hostname <host>`; `gh repo view <host>/<owner>/<repo> --json nameWithOwner,url,defaultBranchRef` | `gh pr create --repo <host>/<owner>/<repo> --head <source> --base <base> --title <title> --body <body>` |
| GitLab | `glab auth status --hostname <host>`; `glab repo view <verified-project-url> --output json` | `glab mr create --repo <verified-project-url> --source-branch <source> --target-branch <base> --title <title> --description <body> --yes` |
| Gitea | Installed `tea --help`와 subcommand help가 explicit host/repository를 받는 read-only auth/login-status와 repository probe를 확인해야 한다. `tea login list`만으로는 불충분하다. | `tea pr create` 또는 `tea pulls create`와 explicit host/repository/source/base/title/body flags를 installed help가 모두 확인한 경우만 사용한다. 아니면 unavailable이다. |

## Default branch

1. `refs/remotes/<selected-remote>/HEAD`가 가리키는 실제 remote-tracking ref
2. Selected hostname/repository에 고정된 read-only provider probe가 반환한 actual default branch ref
3. 두 값이 다르거나 실제 ref를 확인할 수 없으면 중단

`main` 또는 `master`를 추측하지 않는다.

## Fallback

- Unknown provider 또는 CLI/인증 부재 시 normal push까지만 수행한다.
- GitLab verified HTTPS remote는 scheme, host, port, 전체 project path(subgroup 포함)를 보존하고 terminal `.git`만 제거해 project web URL을 얻는다. source와 base branch를 URL-encode하여 `<project-web-url>/-/merge_requests/new?merge_request[source_branch]=<encoded-source>&merge_request[target_branch]=<encoded-base>` exact manual MR URL을 preview한다.
- GitLab SSH remote에서 web scheme 또는 web port를 자동 도출하지 않는다. Selected repository에 고정된 authenticated CLI/config의 read-only 결과로 web URL을 확인하거나 사용자에게 exact project web URL을 요청한다. 확인된 web URL이 없으면 URL을 만들지 않고 project web URL 요청, source/base branch, **New merge request** UI 절차를 preview한다.
- GitLab HTTPS remote URL 또는 branch를 신뢰성 있게 parse/encode할 수 없으면 URL을 임의로 만들지 않는다. 사용자에게 exact project web URL을 요청하고, preview에 project web URL, source branch, base branch와 함께 해당 project의 UI에서 **New merge request**를 선택해 source와 target을 지정하는 절차를 제시한다.
- GitHub/Gitea CLI/인증 부재 시 provider가 확인한 exact compare/create URL이 있으면 preview한다. 없으면 endpoint 형식을 추측하지 않고 project web URL, source branch, base branch와 해당 provider UI에서 Pull Request를 생성하는 절차를 preview한다.
- API를 직접 호출하거나 credential을 요청·출력하지 않는다.
