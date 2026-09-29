---
name: agents
description: "모든 AI Agent, MCP server를 설치하거나 업그레이드. OS를 감지해 pnpm, uv, brew, nix를 플랫폼별 방식으로 실행. 'install'로 신규 머신 설정, 'upgrade'로 기존 agent 업데이트. 시스템 패키지(prerequisites 포함)는 /infra:packages, LSP server는 /infra:lsp 사용."
---

# Agents

모든 AI Agent, MCP server를 설치하거나 업그레이드.

> **범위 구분**: 이 스킬은 AI 에이전트·MCP server만 담당.
> pnpm/uv/mise 등 prerequisites와 OS 시스템 패키지는 `/infra:packages` 사용.
> LSP server(typescript-language-server, jdtls 등)는 `/infra:lsp` 사용.

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
| SteamOS | mise (Node.js/corepack/pnpm) + brew (Linuxbrew) |
| NixOS | nix 패키지로 관리 (pnpm, uv 모두) |
| Debian/Ubuntu | apt/binary |
| Fedora | dnf/binary |

## 대상

### AI Agents

#### pnpm

| 패키지 | CLI 명령 |
| :--- | :--- |
| `oh-my-claude-sisyphus` | `omc`, `oh-my-claudecode` |
| `oh-my-codex` | `omx` |

> `codex`는 macOS에서 brew cask(`codex`) 권장 — pnpm `minimumReleaseAge`로 최신 설치가 지연됨. 아래 Brew Cask AI Agents 섹션 참조. 타 OS는 `@openai/codex` pnpm 패키지.

#### uv

| 패키지 | CLI 명령 |
| :--- | :--- |
| `holmesgpt` | `holmes` |
| `serena-agent` | `serena`, `serena-agent`, `serena-hooks` |
| `llm` | `llm` |

#### Brew Cask AI Agents

macOS에서 `codex`·`claude-code`·`antigravity-cli`·`google-gemini`는 brew cask로 관리. pnpm `minimumReleaseAge`·native PATH 충돌·`agy` 자체 업데이터 충돌을 모두 회피.

| 패키지 | CLI/앱 | 설치 (macOS) | 업그레이드 (macOS) |
| :--- | :--- | :--- | :--- |
| `codex` | `codex` | `brew install --cask codex` | `brew upgrade --cask codex` |
| `claude-code` | `claude` | `brew install --cask claude-code` | `brew upgrade --cask claude-code` |
| `antigravity-cli` | `agy` | `brew install --cask antigravity-cli` | `brew upgrade --cask antigravity-cli` (실패 시 `agy update`) |
| `google-gemini` | `Gemini.app` (GUI) | `brew install --cask google-gemini` | `brew upgrade --cask google-gemini` (실패 시 앱 자체 업데이트로 최신 유지) |

> **antigravity-cli**: `auto_updates` cask라 `agy` 자체 업데이터가 바이너리를 덮어쓰면 `brew upgrade --cask`가 "already a Binary at .../agy" 에러로 실패. 이때 `agy update`로 갱신 (`brew info`가 Not installed로 인식하는 상태 불일치도 동일 원인).
> **claude-code**: native installer(`~/.local/bin/claude`)와 PATH 충돌. brew 우선하려면 native 바이너리 제거 → `/opt/homebrew/bin/claude` 사용. `~/.claude/`(설정·플러그인)는 공유 유지.
> **codex**: npm 패키지이나 macOS는 brew cask가 최신을 즉시 제공 (pnpm `minimumReleaseAge` 우회).
> **google-gemini**: Google Gemini 데스크톱 앱(`Gemini.app`, GUI, CLI 없음). `auto_updates` cask라 Google 자체 업데이터가 갱신 → `brew upgrade --cask`가 "already an App" 에러로 실패해도 앱이 이미 최신인 경우가 많음. **cask `gemini`(MacPaw 디스크 클리너)와 혼동 금지.** Gemini CLI(2026-06-18 서비스 중단)·Antigravity CLI(`agy`)·Gemini 데스크톱 앱은 서로 다른 별개 제품.
> **타 OS**: SteamOS/Linux antigravity는 `curl -fsSL https://antigravity.google/cli/install.sh | bash` (자체 `agy update`). NixOS는 `nixpkgs#antigravity-cli`. codex는 타 OS에서 `@openai/codex` pnpm. claude-code는 native installer. Gemini CLI는 2026-06-18 서비스 중단 (데스크톱 앱 `google-gemini`는 별도 제품으로 계속 제공).

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

### LSP Servers — 위임

LSP server(typescript-language-server, pyright, jdtls, gopls, terraform-ls, lua-language-server 등 전체)는 **`/infra:lsp` 스킬이 담당**한다. 이 스킬에서는 설치·업그레이드·검증하지 않는다 — 대상 목록과 절차는 lsp 스킬 참조.

---

## Install (새 머신 셋업)

### 1. Prerequisites 확인

pnpm, uv가 있어야 함. 없으면 `/infra:packages`의 Prerequisites 섹션으로 먼저 설치.

### 2. 에이전트 설치

#### pnpm (전 OS)

```bash
# @latest 지정 필수: 미지정 시 설치 시점 버전이 lockfile에 고정되어 최신으로 갱신 안 됨
# AI Agents — macOS는 codex를 brew cask로 설치 (아래 Brew Cask AI Agents). pnpm은 타 OS만.
pnpm add -g oh-my-claude-sisyphus@latest oh-my-codex@latest
# codex (macOS 제외 — macOS는 brew cask)
[ "$(uname -s)" != "Darwin" ] && pnpm add -g @openai/codex@latest

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
uv tool install llm@latest

# MCP Servers
uv tool install proxmox-mcp-plus@latest
uv tool install doris-mcp-server@latest
```

#### LSP Servers

LSP server 설치는 `/infra:lsp` 스킬의 Install 절차를 따른다.

#### Brew Cask AI Agents (macOS 분기)

macOS 감지(`uname -s = Darwin`) 시 `codex`·`claude-code`·`antigravity-cli`·`google-gemini`를 brew cask로 설치. macOS는 brew 기반.

```bash
# macOS - brew cask로 codex / claude-code / antigravity-cli / google-gemini 동시 설치
if [ "$(uname -s)" = "Darwin" ]; then
  brew install --cask codex claude-code antigravity-cli google-gemini
  # claude-code: native installer(~/.local/bin/claude) 잔류 시 PATH 충돌 → 제거 후 brew 우선
  # rm ~/.local/bin/claude  # 사용자 승인 후 제거
fi

# SteamOS/Linux - antigravity installer (자체 agy update)
if [ "$(uname -s)" != "Darwin" ] && ! command -v agy &>/dev/null; then
  curl -fsSL https://antigravity.google/cli/install.sh | bash
fi

# NixOS - nix 패키지 (nixpkgs#antigravity-cli)
nix profile install nixpkgs#antigravity-cli
```

### 3. 설치 검증 (버전 출력)

설치 직후 각 CLI로 직접 버전 확인하여 결과 리포트 출력. 실패한 패키지는 FAIL 표시하고 계속 진행.

```bash
# pnpm - AI Agents
codex --version
omc --version
omx --version

# Brew Cask AI Agents (macOS)
agy --version
claude --version
# google-gemini (Gemini desktop) — GUI 앱이라 CLI가 없어 brew로 확인
brew list --cask --versions google-gemini
# pnpm - MCP Servers
mcp-hub --version
kubernetes-mcp-server --version

# uv - AI Agents
holmes version
serena --version

# uv - MCP Servers (--version 미지원)
uv tool list | grep -E "proxmox-mcp-plus|doris-mcp-server"

# pnpm - MCP Servers (--version 미지원)
pnpm list -g --depth=0 | grep -E "dbhub"

# uv - llm
llm --version
```

LSP server 검증은 `/infra:lsp` 스킬의 검증 절차를 따른다.

| 패키지 | 관리 | 상태 | 버전 |
| :--- | :--- | :--- | :--- |
| @openai/codex | pnpm | OK | 0.137.0 |
| agy (Antigravity) | standalone | OK | 1.0.13 |

> **참고**:
> - `holmes`는 `--version` 미지원으로 하위 명령 방식 사용.
> - `dbhub`, `proxmox-mcp-plus`, `doris-mcp-server`는 `--version` 미지원으로 `pnpm list` / `uv tool list`로 확인.

---

## Upgrade (기존 머신 업데이트)

### 1. Prerequisites 확인

pnpm, uv가 있어야 함. 없으면 `/infra:packages`의 Prerequisites 섹션으로 먼저 설치.

### 2. 사전 버전 수집

업그레이드 전 각 CLI로 직접 버전 확인하여 테이블로 출력.

```bash
# Install 섹션 3번과 동일한 CLI 버전 확인 스크립트
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
# AI Agents — macOS는 codex를 brew cask로 업그레이드 (아래 Brew Cask). pnpm은 타 OS만.
pnpm update -g --latest oh-my-claude-sisyphus oh-my-codex
# codex (macOS 제외 — minimumReleaseAge 주의)
[ "$(uname -s)" != "Darwin" ] && pnpm update -g --latest @openai/codex

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
uv tool upgrade llm

# MCP Servers
uv tool upgrade proxmox-mcp-plus
uv tool upgrade doris-mcp-server
```

#### LSP Servers

LSP server 업그레이드는 `/infra:lsp` 스킬의 Upgrade 절차를 따른다.

#### Brew Cask AI Agents (macOS 분기)

```bash
# macOS - brew cask로 codex / claude-code / antigravity-cli / google-gemini 업그레이드
if [ "$(uname -s)" = "Darwin" ]; then
  brew upgrade --cask codex claude-code antigravity-cli google-gemini
  # antigravity-cli: auto_updates cask라 agy 자체 업데이터 충돌 시 "already a Binary" 에러 → agy update로 폴백
  # google-gemini: auto_updates + GUI 앱 — "already an App" 에러 시 앱 자체 업데이트로 이미 최신인 경우 다수 → 앱 내 업데이트로 확인
fi

# SteamOS/Linux - 자체 update 서브커맨드
agy update

# NixOS - nix profile upgrade (configuration.nix 관리 시 flake update + nixos-rebuild)
nix profile upgrade '.*antigravity-cli.*'
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
| agy (Antigravity) | standalone | 1.0.11 | 1.0.13 | OK |
| @bytebase/dbhub | pnpm | 0.21.2 | — | FAIL |
```

변경 없으면 "모든 패키지가 최신 버전입니다" 출력.

---

## Key Rules

- **Prerequisites 위임**: pnpm/uv/mise 설치·시스템 패키지는 `/infra:packages` 담당. 이 스킬은 실행 전 존재 여부만 확인
- **LSP 위임**: LSP server 설치·업그레이드·검증은 `/infra:lsp` 담당. 이 스킬은 AI 에이전트·MCP만
- **멱등성** (install): 이미 설치된 패키지는 스킵
- **dry-run 먼저** (upgrade): 버전 수집 → 사용자 확인 → 실행
- **에러 중단하지 않음**: 실패한 패키지는 리포트에 명시하고 계속 진행
- **Brew Cask 우선 (macOS)**: `codex`·`claude-code`·`antigravity-cli`는 brew cask로 관리. brew formula/cask에 존재하면 pnpm/uv/native보다 우선 (`brew search`로 확인)
- **pnpm minimumReleaseAge 주의**: pnpm global은 supply chain 보호로 publish 후 약 24시간 동안 최신 버전 설치 차단 (`ERR_PNPM_NO_MATURE_MATCHING_VERSION`). `(x.xx.x is available)`가 떠도 강제 설치 불가 → macOS는 brew cask로 우회
- **mise/pnpm PATH 충돌 주의**: mise node global bin이 pnpm global bin보다 PATH에서 선행하면 stale 구버전이 실행됨. 업그레이드 후 반드시 `which <cli>` + `--version` 교차 검증. mise node global 중복 패키지는 `npm uninstall -g`로 제거
- **Claude Code**: macOS는 brew cask `claude-code`로 관리 (native installer 대체). `~/.claude/` 설정은 공유. 타 OS는 native installer 유지
- **NixOS 특례**: 모든 패키지 매니저(pnpm, uv)가 nix로 관리됨 (LSP의 nix 관리는 `/infra:lsp` 참조)
- **Antigravity CLI 특례**: macOS는 homebrew-cask (`auto_updates`) — `brew upgrade --cask` 실패 시 `agy update`로 폴백. SteamOS/Linux는 installer 스크립트 (자체 `agy update`), NixOS는 nixpkgs `antigravity-cli` 패키지
- **Gemini desktop**: macOS는 brew cask `google-gemini`(`auto_updates`, Google 자체 업데이터)로 관리. Gemini CLI(2026-06-18 서비스 중단)·Antigravity CLI(`agy`)·Gemini 데스크톱 앱은 별개 제품이며, cask `gemini`(MacPaw 디스크 클리너)와 혼동 금지. GUI 앱이라 버전 검증은 `brew list --cask --versions google-gemini` 사용
- **SteamOS 특례**: Node.js/corepack은 mise로 관리. antigravity는 installer 스크립트
- **한국어 리포트**: 결과는 항상 한국어로 출력
