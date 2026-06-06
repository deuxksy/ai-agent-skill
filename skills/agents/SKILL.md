---
name: agents
description: "Install or upgrade all AI agents. Detects OS and uses pnpm, uv, brew with platform-specific methods. Use 'install' to set up new machine, 'upgrade' to update existing agents."
---

# Agents

모든 AI Agent를 설치하거나 업그레이드.

## OS 감지

```bash
uname -s          # Darwin → macOS, Linux → Linux
uname -o 2>/dev/null  # NixOS → NixOS
cat /etc/os-release 2>/dev/null | grep ^ID=  # debian, ubuntu, fedora
```

| 감지 결과 | 분기 |
| :--- | :--- |
| Darwin | macOS (brew) |
| NixOS | NixOS (k8sgpt만 nix 관리) |
| Debian/Ubuntu | Linux (binary download) |
| Fedora | Linux (binary download) |

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

---

## Install (새 머신 셋업)

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

# Debian/Ubuntu/Fedora - GitHub binary
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

---

## Upgrade (기존 머신 업데이트)

### 1. 사전 확인

pnpm, uv가 설치되어 있다고 가정. 없으면 설치 필요 메시지 출력 후 중단.

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
pnpm update -g @openai/codex @google/gemini-cli mcp-hub oh-my-claude-sisyphus oh-my-codex
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
ARCH=$(uname -m | sed 's/x86_64/amd64/' | sed 's/aarch64/arm64/')
curl -sL "https://github.com/k8sgpt-ai/k8sgpt/releases/latest/download/k8sgpt_${ARCH}.linux.tar.gz" | tar xz -C /usr/local/bin k8sgpt

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

- **멱등성** (install): 이미 설치된 패키지는 스킵
- **dry-run 먼저** (upgrade): 버전 수집 → 사용자 확인 → 실행
- **에러 중단하지 않음**: 실패한 패키지는 리포트에 명시하고 계속 진행
- **Claude Code 제외**: native installer로 자체 관리하므로 안내만 출력
- **NixOS 특례**: nix로 관리되는 패키지(k8sgpt)는 스킵
- **한국어 리포트**: 결과는 항상 한국어로 출력
