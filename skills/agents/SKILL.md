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

### pnpm (전 OS 공통)

| 패키지 | CLI 명령 |
| :--- | :--- |
| `@openai/codex` | `codex` |
| `@google/gemini-cli` | `gemini` |
| `mcp-hub` | `mcp-hub` |
| `oh-my-claude-sisyphus` | `omc`, `oh-my-claudecode` |
| `oh-my-codex` | `omx` |

### uv (전 OS 공통)

| 패키지 | CLI 명령 |
| :--- | :--- |
| `holmesgpt` | `holmes` |
| `proxmox-mcp-plus` | `proxmox-mcp`, `proxmox-mcp-plus` |
| `serena-agent` | `serena`, `serena-agent`, `serena-hooks` |
| `shell-gpt` | `sgpt` |

### OS별 패키지

| 패키지 | macOS | Debian/Ubuntu | Fedora | NixOS |
| :--- | :--- | :--- | :--- | :--- |
| k8sgpt | brew | binary download | binary download | nix (스킵) |

---

## Prerequisites (pnpm, uv 설치)

Node.js(v22+)가 설치되어 있다고 가정. pnpm, uv가 없으면 OS별로 설치.

| 도구 | macOS | Linux (Debian/Ubuntu/Fedora) | NixOS |
| :--- | :--- | :--- | :--- |
| pnpm | `corepack enable pnpm` | `corepack enable pnpm` | nix 패키지 (configuration.nix) |
| uv | `brew install uv` | `curl -LsSf https://astral.sh/uv/install.sh \| sh` | nix 패키지 (configuration.nix) |

```bash
# pnpm (macOS/Linux, NixOS 제외)
if ! command -v pnpm &>/dev/null; then
  # Node.js 25+에서는 corepack이 미포함될 수 있음
  npm install -g corepack@latest 2>/dev/null
  corepack enable pnpm
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
pnpm add -g @openai/codex @google/gemini-cli mcp-hub oh-my-claude-sisyphus oh-my-codex
```

#### uv (전 OS)

```bash
uv tool install holmesgpt
uv tool install proxmox-mcp-plus
uv tool install serena-agent
uv tool install shell-gpt
```

#### k8sgpt (OS별)

```bash
# macOS
brew install k8sgpt-ai/k8sgpt/k8sgpt

# Debian/Ubuntu/Fedora - GitHub binary
ARCH=$(uname -m | sed 's/x86_64/x86_64/' | sed 's/aarch64/arm64/')
curl -fsSL "https://github.com/k8sgpt-ai/k8sgpt/releases/latest/download/k8sgpt_Linux_${ARCH}.tar.gz" -o /tmp/k8sgpt.tar.gz
tar xzf /tmp/k8sgpt.tar.gz -C /tmp k8sgpt
sudo install -m 0755 /tmp/k8sgpt /usr/local/bin/k8sgpt

# NixOS - 스킵 (nixpkgs로 관리)
```

### 3. 설치 확인

```bash
codex --version
gemini --version
mcp-hub --version
omc --version
omx --version
holmes --version
proxmox-mcp-plus --version
serena --version
sgpt --version
k8sgpt version
```

### 4. 결과 리포트

| 패키지 | 상태 | 버전 |
| :--- | :--- | :--- |
| @openai/codex | OK | 1.0.0 |
| @google/gemini-cli | FAIL | - |

---

## Upgrade (기존 머신 업데이트)

### 1. Prerequisites 확인

pnpm, uv가 없으면 위 Prerequisites 섹션에 따라 설치.

### 2. 사전 버전 수집

```bash
pnpm list -g --depth=0
uv tool list
k8sgpt version
```

### 3. 사용자 확인

수집한 버전과 업그레이드 대상을 보여주고 진행 확인.

### 4. 업그레이드 실행

#### pnpm (전 OS)

```bash
pnpm update -g --latest @openai/codex @google/gemini-cli mcp-hub oh-my-claude-sisyphus oh-my-codex
```

#### uv (전 OS)

```bash
uv tool upgrade holmesgpt
uv tool upgrade proxmox-mcp-plus
uv tool upgrade serena-agent
uv tool upgrade shell-gpt
```

#### k8sgpt (OS별)

```bash
# macOS
brew upgrade k8sgpt

# Debian/Ubuntu/Fedora - GitHub binary 교체
ARCH=$(uname -m | sed 's/x86_64/x86_64/' | sed 's/aarch64/arm64/')
curl -fsSL "https://github.com/k8sgpt-ai/k8sgpt/releases/latest/download/k8sgpt_Linux_${ARCH}.tar.gz" -o /tmp/k8sgpt.tar.gz
tar xzf /tmp/k8sgpt.tar.gz -C /tmp k8sgpt
sudo install -m 0755 /tmp/k8sgpt /usr/local/bin/k8sgpt

# NixOS - 스킵 (nixos-rebuild로 관리)
```

### 5. 버전 변경 리포트

업그레이드 전후 버전 비교.

```text
| 패키지 | 이전 | 이후 |
| :--- | :--- | :--- |
| @openai/codex | 1.0.0 | 1.1.0 |
```

변경 없으면 "모든 패키지가 최신 버전입니다" 출력.

---

## Key Rules

- **Prerequisites 자동 설치**: pnpm(corepack), uv가 없으면 OS에 맞게 설치
- **멱등성** (install): 이미 설치된 패키지는 스킵
- **dry-run 먼저** (upgrade): 버전 수집 → 사용자 확인 → 실행
- **에러 중단하지 않음**: 실패한 패키지는 리포트에 명시하고 계속 진행
- **Claude Code 제외**: native installer로 자체 관리하므로 안내만 출력
- **NixOS 특례**: 모든 패키지 매니저(pnpm, uv, k8sgpt)가 nix로 관리됨
- **한국어 리포트**: 결과는 항상 한국어로 출력
