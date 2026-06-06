---
name: install-agents
description: "Install all AI agents from scratch. Detects OS and installs pnpm, uv, and brew packages with platform-specific methods. Use when setting up a new machine or reinstalling agents."
---

# Install Agents

모든 AI Agent를 새로 설치. 새 머신 셋업 또는 재설치 시 사용.

## OS 감지

```bash
uname -s          # Darwin → macOS, Linux → Linux
uname -o 2>/dev/null  # NixOS → NixOS
cat /etc/os-release 2>/dev/null | grep ^ID=  # debian, ubuntu, fedora
```

| 감지 결과 | 분기 |
| :--- | :--- |
| Darwin | macOS (brew) |
| NixOS | NixOS (nix 관리, brew/apt 스킵) |
| Debian/Ubuntu | Linux (apt/binary) |
| Fedora | Linux (dnf/binary) |

## 대상

### pnpm (전 OS 공통)

| 패키지 | CLI 명령 |
| :--- | :--- |
| `@openai/codex` | `codex` |
| `@google/gemini-cli` | `gemini` |
| `mcp-hub` | `mcp-hub` |
| `oh-my-claude-sisyphus` | - |
| `oh-my-codex` | - |

### uv (전 OS 공통)

| 패키지 | CLI 명령 |
| :--- | :--- |
| `holmesgpt` | `holmes` |
| `proxmox-mcp-plus` | - |
| `serena-agent` | `serena` |
| `shell-gpt` | `sgpt` |

### OS별 패키지

| 패키지 | macOS | Debian/Ubuntu | Fedora | NixOS |
| :--- | :--- | :--- | :--- | :--- |
| k8sgpt | brew | binary download | binary download | nix (스킵) |

## Workflow

### 1. 사전 확인

pnpm, uv가 설치되어 있다고 가정. 없으면 설치 필요 메시지 출력 후 중단.

```bash
if ! command -v pnpm &>/dev/null; then
  echo "pnpm이 설치되어 있지 않습니다. 먼저 설치해주세요."
fi
if ! command -v uv &>/dev/null; then
  echo "uv가 설치되어 있지 않습니다. 먼저 설치해주세요."
fi
```

### 2. 설치 실행

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

# Debian/Ubuntu - GitHub binary
ARCH=$(uname -m | sed 's/x86_64/amd64/' | sed 's/aarch64/arm64/')
curl -sL "https://github.com/k8sgpt-ai/k8sgpt/releases/latest/download/k8sgpt_${ARCH}.linux.tar.gz" | tar xz -C /usr/local/bin k8sgpt

# Fedora - 동일 binary 방식
ARCH=$(uname -m | sed 's/x86_64/amd64/' | sed 's/aarch64/arm64/')
curl -sL "https://github.com/k8sgpt-ai/k8sgpt/releases/latest/download/k8sgpt_${ARCH}.linux.tar.gz" | tar xz -C /usr/local/bin k8sgpt

# NixOS - 스킵 (nixpkgs로 관리)
```

### 3. 설치 확인

```bash
codex --version
gemini --version
holmes --version
serena --version
sgpt --version
k8sgpt version
mcp-hub --version
```

### 4. 결과 리포트

| 패키지 | 상태 | 버전 |
| :--- | :--- | :--- |
| @openai/codex | OK | 1.0.0 |
| @google/gemini-cli | FAIL | - |

## Key Rules

- **멱등성**: 이미 설치된 패키지는 스킵 (버전만 확인)
- **에러 중단하지 않음**: 실패한 패키지는 리포트에 명시하고 계속 진행
- **Claude Code 제외**: native installer로 별도 설치하므로 안내만 출력
- **NixOS 특례**: nix로 관리되는 패키지(k8sgpt)는 스킵
- **한국어 리포트**: 결과는 항상 한국어로 출력
