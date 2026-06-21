---
name: agents
description: "Install or upgrade all AI agents, MCP servers, and LSP servers. Detects OS and uses pnpm, uv, brew, nix with platform-specific methods. Use 'install' to set up new machine, 'upgrade' to update existing agents."
---

# Agents

모든 AI Agent를 설치하거나 업그레이드.

## OS 감지

```bash
# NixOS 감지
grep -q ^ID=nixos /etc/os-release 2>/dev/null && echo "NixOS"

# macOS 감지
[ "$(uname -s)" = "Darwin" ] && echo "macOS"

# Linux 배포판 감지
cat /etc/os-release 2>/dev/null | grep ^ID=
```

| 감지 결과 | 분기 |
| :--- | :--- |
| macOS | brew |
| SteamOS | mise (Node.js/corepack/pnpm) + brew (Linuxbrew, k8sgpt) |
| NixOS | nix 패키지로 관리 (k8sgpt, pnpm, uv 모두) |
| Debian/Ubuntu | apt/binary |
| Fedora | dnf/binary |

## 대상

### AI Agents

#### pnpm

| 패키지 | CLI 명령 |
| :--- | :--- |
| `@openai/codex` | `codex` |
| `@google/gemini-cli` | `gemini` |
| `oh-my-claude-sisyphus` | `omc`, `oh-my-claudecode` |
| `oh-my-codex` | `omx` |

#### uv

| 패키지 | CLI 명령 |
| :--- | :--- |
| `holmesgpt` | `holmes` |
| `serena-agent` | `serena`, `serena-agent`, `serena-hooks` |
| `shell-gpt` | `sgpt` |

#### OS별

| 패키지 | macOS | SteamOS | Debian/Ubuntu | Fedora | NixOS |
| :--- | :--- | :--- | :--- | :--- | :--- |
| k8sgpt | brew | brew (Linuxbrew) | binary download | binary download | nix (스킵) |

### MCP Servers

#### pnpm

| 패키지 | CLI 명령 |
| :--- | :--- |
| `mcp-hub` | `mcp-hub` |
| `@bytebase/dbhub` | `dbhub` |
| `kubernetes-mcp-server` | `kubernetes-mcp-server` |

#### uv

| 패키지 | CLI 명령 |
| :--- | :--- |
| `proxmox-mcp-plus` | `proxmox-mcp`, `proxmox-mcp-plus` |
| `doris-mcp-server` | `doris-mcp`, `doris-mcp-server` |
| `postgres-mcp` | `postgres-mcp` |

### LSP Servers

Serena/OMC LSP 도구(`lsp_*`)가 코드 심볼 분석에 사용. PATH에 있어야 자동 감지. `nil`은 NixOS는 nix, 타 OS는 cargo(mise rust)로 설치.

#### pnpm

| 패키지 | LSP | 용도 |
| :--- | :--- | :--- |
| `typescript-language-server` | TS/JS | TypeScript/TSX |
| `yaml-language-server` | YAML | Ansible, CI, config |
| `bash-language-server` | Bash/Zsh | shell script |
| `pyright` | Python | Python |
| `vscode-langservers-extracted` | JSON/HTML/CSS | 범용 번들 |
| `@ansible/ansible-language-server` | Ansible | playbook |

#### OS별

| 패키지 | macOS/SteamOS | Debian/Ubuntu/Fedora | NixOS |
| :--- | :--- | :--- | :--- |
| lua-language-server | brew | binary download | nix |
| marksman | brew | binary download | nix |
| terraform-ls | brew | binary download | nix |
| nil | cargo | cargo | nix |

### Cloud Plugins (Claude Code Marketplace)

| 플러그인 | 용도 | 설치 방식 |
| :--- | :--- | :--- |
| Notion | 문서 관리 (회사 문서 DB) | Claude Code 플러그인 |
| Figma | 디자인 (디자인 팀 협업) | Claude Code 플러그인 |
| oh-my-claudecode | Claude Code 멀티 에이전트 오케스트레이션 | Marketplace |

```bash
# oh-my-claudecode 설치
claude plugin marketplace add https://github.com/Yeachan-Heo/oh-my-claudecode
claude plugin install oh-my-claudecode
```

---

## Prerequisites (pnpm, uv 설치)

Node.js(lts-latest)가 설치되어 있다고 가정. pnpm, uv가 없으면 OS별로 설치.

| 도구 | macOS | SteamOS | Linux (Debian/Ubuntu/Fedora) | NixOS |
| :--- | :--- | :--- | :--- | :--- |
| Node.js | brew / 기존 설치 | mise (`mise use node@lts`) | 기존 설치 | nix 패키지 |
| pnpm | `corepack enable pnpm && pnpm setup` | `corepack enable pnpm && corepack prepare pnpm@latest --activate` | `corepack enable pnpm && pnpm setup` | nix 패키지 (configuration.nix) |
| uv | `brew install uv` | mise (`mise use uv@latest`) 또는 기존 설치 | `curl -LsSf https://astral.sh/uv/install.sh \| sh` | nix 패키지 (configuration.nix) |

```bash
# --- OS 감지 ---
OS=$(cat /etc/os-release 2>/dev/null | grep ^ID= | cut -d= -f2)
KERNEL=$(uname -s)

# --- pnpm ---

# macOS / Linux (Debian/Ubuntu/Fedora)
if [ "$KERNEL" = "Darwin" ] || [ "$OS" != "steamos" -a "$OS" != "nixos" ]; then
  if ! command -v pnpm &>/dev/null; then
    # Node.js 25+에서는 corepack이 미포함될 수 있음
    npm install -g corepack@latest 2>/dev/null
    corepack enable pnpm
    pnpm setup
  fi
fi

# SteamOS - mise로 관리되는 Node.js의 corepack 사용
# npm install -g corepack 불필요 (mise node에 이미 포함)
if [ "$OS" = "steamos" ]; then
  if ! command -v pnpm &>/dev/null; then
    corepack enable pnpm
    corepack prepare pnpm@latest --activate
  fi
fi

# NixOS - configuration.nix에 pnpm 추가 후 nixos-rebuild

# --- uv ---

# macOS
if [ "$KERNEL" = "Darwin" ]; then
  if ! command -v uv &>/dev/null; then brew install uv; fi
fi

# SteamOS - mise 또는 이미 설치된 상태
if [ "$OS" = "steamos" ]; then
  if ! command -v uv &>/dev/null; then
    # mise로 설치 권장
    mise use -g uv@latest 2>/dev/null || curl -LsSf https://astral.sh/uv/install.sh | sh
  fi
fi

# Linux (Debian/Ubuntu/Fedora)
# 설치 후 PATH 리프레시 필요: source ~/.local/bin/env 또는 새 쉘
if [ "$OS" != "steamos" -a "$OS" != "nixos" -a "$KERNEL" != "Darwin" ]; then
  if ! command -v uv &>/dev/null; then
    curl -LsSf https://astral.sh/uv/install.sh | sh
    export PATH="$HOME/.local/bin:$PATH"
  fi
fi

# NixOS - configuration.nix에 uv 추가 후 nixos-rebuild
```

---

## Install (새 머신 셋업)

### 1. Prerequisites 설치

pnpm, uv가 없으면 위 Prerequisites 섹션에 따라 설치.

### 2. 에이전트 설치

#### pnpm (전 OS)

```bash
# @latest 지정 필수: 미지정 시 설치 시점 버전이 lockfile에 고정되어 최신으로 갱신 안 됨
# AI Agents
pnpm add -g @openai/codex@latest @google/gemini-cli@latest oh-my-claude-sisyphus@latest oh-my-codex@latest

# MCP Servers
pnpm add -g mcp-hub@latest @bytebase/dbhub@latest kubernetes-mcp-server@latest
```

#### uv (전 OS)

```bash
# AI Agents
# @latest 지정 필수: 미지정 시 설치 시점 버전이 pin되어 upgrade 불가
# holmesgpt는 azure-mgmt-sql pre-release 의존성으로 --prerelease=allow 필요
uv tool install holmesgpt@latest --prerelease=allow
uv tool install serena-agent@latest
uv tool install shell-gpt@latest

# MCP Servers
uv tool install proxmox-mcp-plus@latest
uv tool install doris-mcp-server@latest
uv tool install postgres-mcp@latest
```

#### LSP Servers

```bash
# pnpm (전 OS) - @latest 지정 필수
pnpm add -g typescript-language-server@latest yaml-language-server@latest bash-language-server@latest pyright@latest vscode-langservers-extracted@latest @ansible/ansible-language-server@latest

# macOS / SteamOS (Linuxbrew)
brew install lua-language-server marksman terraform-ls

# Debian/Ubuntu/Fedora - 각 프로젝트 GitHub release binary

# nil (macOS/SteamOS/Linux) - cargo (mise rust, 소스 빌드)
cargo install --git https://github.com/oxalica/nil nil

# NixOS - configuration.nix (environment.system.packages) 또는 nix profile
nix profile install nixpkgs#lua-language-server nixpkgs#marksman nixpkgs#terraform-ls nixpkgs#nil
```

#### k8sgpt (OS별)

```bash
# macOS - homebrew/core
brew install k8sgpt

# SteamOS - Linuxbrew
brew install k8sgpt

# Debian/Ubuntu/Fedora - GitHub binary
ARCH=$(uname -m | sed 's/x86_64/x86_64/' | sed 's/aarch64/arm64/')
TMPDIR=$(mktemp -d)
curl -fsSL "https://github.com/k8sgpt-ai/k8sgpt/releases/latest/download/k8sgpt_Linux_${ARCH}.tar.gz" -o "${TMPDIR}/k8sgpt.tar.gz" \
  && tar xzf "${TMPDIR}/k8sgpt.tar.gz" -C "${TMPDIR}" k8sgpt \
  && sudo install -m 0755 "${TMPDIR}/k8sgpt" /usr/local/bin/k8sgpt \
  && rm -rf "${TMPDIR}"

# NixOS - 스킵 (nixpkgs로 관리)
```

#### Claude Code Plugins (Marketplace)

```bash
# oh-my-claudecode
claude plugin marketplace add https://github.com/Yeachan-Heo/oh-my-claudecode
claude plugin install oh-my-claudecode
```

### 3. 설치 검증 (버전 출력)

설치 직후 각 CLI로 직접 버전 확인하여 결과 리포트 출력. 실패한 패키지는 FAIL 표시하고 계속 진행.

```bash
# pnpm - AI Agents
codex --version
gemini --version
omc --version
omx --version

# pnpm - MCP Servers
mcp-hub --version
kubernetes-mcp-server --version

# uv - AI Agents
holmes version
serena --version

# uv - MCP Servers (--version 미지원)
uv tool list | grep -E "proxmox-mcp-plus|doris-mcp-server|postgres-mcp"

# pnpm - MCP Servers (--version 미지원)
pnpm list -g --depth=0 | grep -E "dbhub|shell-gpt"

# OS별
k8sgpt version

# pnpm - LSP Servers
typescript-language-server --version
yaml-language-server --version
bash-language-server --version
pyright --version
ansible-language-server --version

# pnpm - LSP (--version 미지원)
pnpm list -g --depth=0 | grep vscode-langservers-extracted

# brew - LSP Servers
brew list --versions lua-language-server marksman terraform-ls

# nil (cargo/nix)
nil --version
```

| 패키지 | 관리 | 상태 | 버전 |
| :--- | :--- | :--- | :--- |
| @openai/codex | pnpm | OK | 0.137.0 |
| @google/gemini-cli | pnpm | FAIL | - |

> **참고**:
> - `holmes`, `k8sgpt`는 `--version` 미지원으로 하위 명령 방식 사용.
> - `sgpt`, `dbhub`, `proxmox-mcp-plus`, `doris-mcp-server`, `postgres-mcp`는 `--version` 미지원으로 `pnpm list` / `uv tool list`로 확인.
> - `vscode-langservers-extracted`는 `--version` 미지원으로 `pnpm list`로 확인. brew LSP(lua-language-server, marksman, terraform-ls)는 `brew list --versions`로 확인.
> - `nil`은 NixOS는 nix, 타 OS는 cargo(`cargo install --git`)로 설치·갱신.

---

## Upgrade (기존 머신 업데이트)

### 1. Prerequisites 확인

pnpm, uv가 없으면 위 Prerequisites 섹션에 따라 설치.

### 2. 사전 버전 수집

업그레이드 전 각 CLI로 직접 버전 확인하여 테이블로 출력.

```bash
# pnpm - AI Agents
codex --version
gemini --version
omc --version
omx --version

# pnpm - MCP Servers
mcp-hub --version
kubernetes-mcp-server --version

# uv - AI Agents
holmes version
serena --version

# uv - MCP Servers (--version 미지원)
uv tool list | grep -E "proxmox-mcp-plus|doris-mcp-server|postgres-mcp"

# pnpm - MCP Servers (--version 미지원)
pnpm list -g --depth=0 | grep -E "dbhub|shell-gpt"

# OS별
k8sgpt version

# pnpm - LSP Servers
typescript-language-server --version
yaml-language-server --version
bash-language-server --version
pyright --version
ansible-language-server --version

# pnpm - LSP (--version 미지원)
pnpm list -g --depth=0 | grep vscode-langservers-extracted

# brew - LSP Servers
brew list --versions lua-language-server marksman terraform-ls

# nil (cargo/nix)
nil --version
```

| 패키지 | 관리 | 현재 버전 |
| :--- | :--- | :--- |
| @openai/codex | pnpm | 0.137.0 |
| ... | ... | ... |

### 3. 사용자 확인

수집한 버전 테이블을 보여주고 진행 확인.

### 4. 업그레이드 실행

#### pnpm (전 OS)

```bash
# AI Agents
pnpm update -g --latest @openai/codex @google/gemini-cli oh-my-claude-sisyphus oh-my-codex

# MCP Servers
pnpm update -g --latest mcp-hub @bytebase/dbhub kubernetes-mcp-server
```

#### uv (전 OS)

```bash
# AI Agents
# holmesgpt는 azure-mgmt-sql pre-release 의존성으로 --prerelease=allow 필요
# install 시 @latest로 설치했다면 upgrade 정상 작동 (pin 해제 상태)
uv tool upgrade holmesgpt --prerelease=allow
uv tool upgrade serena-agent
uv tool upgrade shell-gpt

# MCP Servers
uv tool upgrade proxmox-mcp-plus
uv tool upgrade doris-mcp-server
uv tool upgrade postgres-mcp
```

#### LSP Servers

```bash
# pnpm (전 OS)
pnpm update -g --latest typescript-language-server yaml-language-server bash-language-server pyright vscode-langservers-extracted @ansible/ansible-language-server

# macOS / SteamOS (Linuxbrew)
brew upgrade lua-language-server marksman terraform-ls

# nil (macOS/SteamOS/Linux) - cargo 재설치로 갱신
cargo install --force --git https://github.com/oxalica/nil nil

# NixOS - nix profile upgrade (configuration.nix 관리 시 flake update + nixos-rebuild)
nix profile upgrade '.*lua-language-server.*' '.*marksman.*' '.*terraform-ls.*' '.*nil.*'
```

#### k8sgpt (OS별)

```bash
# macOS / SteamOS
brew upgrade k8sgpt

# Debian/Ubuntu/Fedora - GitHub binary 교체
ARCH=$(uname -m | sed 's/x86_64/x86_64/' | sed 's/aarch64/arm64/')
TMPDIR=$(mktemp -d)
curl -fsSL "https://github.com/k8sgpt-ai/k8sgpt/releases/latest/download/k8sgpt_Linux_${ARCH}.tar.gz" -o "${TMPDIR}/k8sgpt.tar.gz" \
  && tar xzf "${TMPDIR}/k8sgpt.tar.gz" -C "${TMPDIR}" k8sgpt \
  && sudo install -m 0755 "${TMPDIR}/k8sgpt" /usr/local/bin/k8sgpt \
  && rm -rf "${TMPDIR}"

# NixOS - 스킵 (nixos-rebuild로 관리)
```

### 5. 업그레이드 검증 + 결과 리포트

업그레이드 직후 각 CLI로 직접 버전 확인. 사전 버전(step 2)과 비교하여 리포트 출력.

```bash
# Install 섹션 3번과 동일한 CLI 버전 확인 스크립트
```

```text
| 패키지 | 관리 | 이전 | 이후 | 상태 |
| :--- | :--- | :--- | :--- | :--- |
| @openai/codex | pnpm | 0.137.0 | 0.138.0 | OK |
| @google/gemini-cli | pnpm | 0.45.1 | 0.45.1 | — |
| @bytebase/dbhub | pnpm | 0.21.2 | — | FAIL |
```

변경 없으면 "모든 패키지가 최신 버전입니다" 출력.

---

## Key Rules

- **Prerequisites 자동 설치**: pnpm(corepack + setup), uv가 없으면 OS에 맞게 설치
- **멱등성** (install): 이미 설치된 패키지는 스킵
- **dry-run 먼저** (upgrade): 버전 수집 → 사용자 확인 → 실행
- **에러 중단하지 않음**: 실패한 패키지는 리포트에 명시하고 계속 진행
- **Claude Code 제외**: native installer로 자체 관리하므로 안내만 출력
- **NixOS 특례**: 모든 패키지 매니저(pnpm, uv, k8sgpt)와 LSP가 nix로 관리됨. `nil`은 NixOS 외 cargo(mise rust)로 설치
- **SteamOS 특례**: Node.js/corepack은 mise로 관리 → `npm install -g corepack` 불필요, `corepack prepare pnpm@latest --activate`로 활성화. uv도 mise 권장. k8sgpt는 Linuxbrew
- **한국어 리포트**: 결과는 항상 한국어로 출력
