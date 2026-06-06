---
name: agents
description: "Install or upgrade all AI agents. Detects OS and uses pnpm, uv, brew with platform-specific methods. Use 'install' to set up new machine, 'upgrade' to update existing agents."
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

| 패키지 | macOS | Debian/Ubuntu | Fedora | NixOS |
| :--- | :--- | :--- | :--- | :--- |
| k8sgpt | brew | binary download | binary download | nix (스킵) |

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

### Cloud Plugins (Claude Code 내장)

| 플러그인 | 용도 | 설치 방식 |
| :--- | :--- | :--- |
| Notion | 문서 관리 (회사 문서 DB) | Claude Code 플러그인 |
| Figma | 디자인 (디자인 팀 협업) | Claude Code 플러그인 |

---

## Prerequisites (pnpm, uv 설치)

Node.js(v22+)가 설치되어 있다고 가정. pnpm, uv가 없으면 OS별로 설치.

| 도구 | macOS | Linux (Debian/Ubuntu/Fedora) | NixOS |
| :--- | :--- | :--- | :--- |
| pnpm | `corepack enable pnpm && pnpm setup` | `corepack enable pnpm && pnpm setup` | nix 패키지 (configuration.nix) |
| uv | `brew install uv` | `curl -LsSf https://astral.sh/uv/install.sh \| sh` | nix 패키지 (configuration.nix) |

```bash
# pnpm (macOS/Linux, NixOS 제외)
if ! command -v pnpm &>/dev/null; then
  # Node.js 25+에서는 corepack이 미포함될 수 있음
  npm install -g corepack@latest 2>/dev/null
  corepack enable pnpm
  # PNPM_HOME 설정 및 쉘 프로필에 등록
  pnpm setup
fi

# uv - macOS
if ! command -v uv &>/dev/null; then brew install uv; fi

# uv - Linux (Debian/Ubuntu/Fedora)
# 설치 후 PATH 리프레시 필요: source ~/.local/bin/env 또는 새 쉘
if ! command -v uv &>/dev/null; then
  curl -LsSf https://astral.sh/uv/install.sh | sh
  export PATH="$HOME/.local/bin:$PATH"
fi

# NixOS - configuration.nix에 pnpm, uv 추가 후 nixos-rebuild
```

---

## Install (새 머신 셋업)

### 1. Prerequisites 설치

pnpm, uv가 없으면 위 Prerequisites 섹션에 따라 설치.

### 2. 에이전트 설치

#### pnpm (전 OS)

```bash
# AI Agents
pnpm add -g @openai/codex @google/gemini-cli oh-my-claude-sisyphus oh-my-codex

# MCP Servers
pnpm add -g mcp-hub @bytebase/dbhub kubernetes-mcp-server
```

#### uv (전 OS)

```bash
# AI Agents
uv tool install holmesgpt
uv tool install serena-agent
uv tool install shell-gpt

# MCP Servers
uv tool install proxmox-mcp-plus
uv tool install doris-mcp-server
uv tool install postgres-mcp
```

#### k8sgpt (OS별)

```bash
# macOS - homebrew/core
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
```

| 패키지 | 관리 | 상태 | 버전 |
| :--- | :--- | :--- | :--- |
| @openai/codex | pnpm | OK | 0.137.0 |
| @google/gemini-cli | pnpm | FAIL | - |

> **참고**:
> - `holmes`, `k8sgpt`는 `--version` 미지원으로 하위 명령 방식 사용.
> - `sgpt`, `dbhub`, `proxmox-mcp-plus`, `doris-mcp-server`, `postgres-mcp`는 `--version` 미지원으로 `pnpm list` / `uv tool list`로 확인.

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
uv tool upgrade holmesgpt
uv tool upgrade serena-agent
uv tool upgrade shell-gpt

# MCP Servers
uv tool upgrade proxmox-mcp-plus
uv tool upgrade doris-mcp-server
uv tool upgrade postgres-mcp
```

#### k8sgpt (OS별)

```bash
# macOS
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
- **NixOS 특례**: 모든 패키지 매니저(pnpm, uv, k8sgpt)가 nix로 관리됨
- **한국어 리포트**: 결과는 항상 한국어로 출력
