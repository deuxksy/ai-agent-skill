---
name: packages
description: "시스템 패키지 매니저. OS를 감지해 prerequisites(pnpm/uv/mise) 설치, OS 패키지(brew/apt/dnf/nix) 관리, Brewfile 동기화, 시스템 전체 업그레이드 실행. AI 에이전트/MCP/LSP는 /infra:agents 사용. 'install'로 신규 머신 패키지 셋업, 'upgrade'로 기존 머신 시스템 업그레이드."
---
# Packages

시스템 패키지 설치·업그레이드. macOS는 `brew bundle` 중심, Linux는 apt/dnf/nix.

> **범위 구분**: 이 스킬은 시스템 패키지(OS 도구, 런타임, prerequisites)만 담당.
> AI 에이전트·MCP·LSP 설치/업그레이드는 `/infra:agents` 사용.

## OS 감지

```bash
HOSTNAME=$(hostname -s 2>/dev/null || hostname | sed 's/\..*//')

# NixOS 감지
grep -q ^ID=nixos /etc/os-release 2>/dev/null && echo "NixOS"

# macOS 감지
[ "$(uname -s)" = "Darwin" ] && echo "macOS"

# Linux 배포판 감지
cat /etc/os-release 2>/dev/null | grep ^ID=
```

| 감지 결과     | 패키지 매니저 | 업그레이드 명령                                                           |
| :------------ | :------------ | :------------------------------------------------------------------------ |
| macOS         | brew          | `brew update && brew upgrade && brew cleanup` + Brewfile 동기화         |
| NixOS         | nix           | `sudo nixos-rebuild switch --flake ~/git/dotfiles/nix/nixos#<hostname>` |
| Debian/Ubuntu | apt           | `sudo apt update && sudo apt upgrade -y`                                |
| Fedora        | dnf           | `sudo dnf upgrade -y`                                                   |

---

## Prerequisites (pnpm, uv, mise)

Node.js(lts-latest)가 설치되어 있다고 가정. pnpm, uv가 없으면 OS별로 설치.
`/infra:agents` 실행 전 pnpm/uv가 없는 경우에도 이 섹션으로 설치.

| 도구    | macOS                                  | SteamOS                                                             | Linux (Debian/Ubuntu/Fedora)                        | NixOS                          |
| :------ | :------------------------------------- | :------------------------------------------------------------------ | :-------------------------------------------------- | :----------------------------- |
| Node.js | brew / 기존 설치                       | mise (`mise use node@lts`)                                        | 기존 설치                                           | nix 패키지                     |
| pnpm    | `corepack enable pnpm && pnpm setup` | `corepack enable pnpm && corepack prepare pnpm@latest --activate` | `corepack enable pnpm && pnpm setup`              | nix 패키지 (configuration.nix) |
| uv      | `brew install uv`                    | mise (`mise use uv@latest`) 또는 기존 설치                        | `curl -LsSf https://astral.sh/uv/install.sh \| sh` | nix 패키지 (configuration.nix) |
| mise    | 불필요 (brew가 Node 관리)              | 런타임 관리자 (Node.js/corepack/uv)                                 | 불필요                                              | 불필요                         |

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

## OS 패키지 관리

### brew (macOS)

macOS는 Brewfile이 패키지 목록의 Source of Truth. 개별 formula 추가는 Brewfile 수정 후 `brew bundle`.

```bash
brew update
brew install <formula>        # Brewfile에도 추가 필요
```

### apt (Debian/Ubuntu)

```bash
sudo apt update
sudo apt install <package>
```

### dnf (Fedora)

```bash
sudo dnf install <package>
```

### nix (NixOS)

```bash
# configuration.nix (environment.system.packages) 또는 flake에 추가 후
sudo nixos-rebuild switch --flake ~/git/dotfiles/nix/nixos#$HOSTNAME
```

### k8sgpt (OS별)

K8s 리소스 분석 도구. brew formula/binary로 설치.

```bash
# macOS / SteamOS - homebrew (Linuxbrew)
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

---

## Brewfile 관리 (macOS)

`brew bundle --global`이 Brewfile을 자동 탐색. 수동 경로 지정 불필요.

```bash
brew bundle --global
```

> `--global` 탐색 순서: `$HOMEBREW_BUNDLE_FILE_GLOBAL` → `${XDG_CONFIG_HOME}/homebrew/Brewfile` → `~/.homebrew/Brewfile` → `~/.Brewfile`

### brew upgrade / cask

```bash
brew update
brew outdated --verbose
brew upgrade

# Cask 업그레이드 (--greedy: auto-update 미지원 앱도 업그레이드)
brew upgrade --cask --greedy 2>/dev/null || true

brew cleanup
```

> **auto_updates cask 주의**: `agy`처럼 자체 업데이터가 있는 cask는 `brew upgrade --cask`가
> "already a Binary at ..." 에러로 실패할 수 있음. 실패 시 해당 도구의 자체 업데이트(`agy update`) 사용.
> 개별 cask 실패는 전체를 중단시키지 않고 리포트에 기록 후 계속 진행.

---

## 시스템 업그레이드 (upgrade 모드)

### 1. 사전 버전 수집

주요 패키지 현재 버전 수집.

```bash
# macOS
brew --version
mise --version 2>/dev/null || echo "mise: not installed"
pnpm --version 2>/dev/null || echo "pnpm: not installed"
uv --version 2>/dev/null || echo "uv: not installed"

# NixOS
nix --version
nixos-version 2>/dev/null

# Debian/Ubuntu
apt --version 2>/dev/null | head -1

# Fedora
dnf --version 2>/dev/null | head -1
```

### 2. 사용자 확인

업데이트 가능 패키지 수를 보여주고 진행 확인.

```bash
# macOS
brew outdated --verbose

# Debian/Ubuntu
apt list --upgradable 2>/dev/null

# Fedora — exit code 100 = updates available (정상)
dnf check-update 2>/dev/null || [ $? -eq 100 ]
```

### 3. 업그레이드 실행

#### macOS (brew)

```bash
brew update
brew outdated --verbose
brew upgrade

# Cask 업그레이드
brew upgrade --cask --greedy 2>/dev/null || true

# Brewfile 정합성
brew bundle --global

brew cleanup
```

#### NixOS (nix)

```bash
# hostname 기반 flake 타겟
HOSTNAME=$(hostname -s 2>/dev/null || hostname | sed 's/\..*//')

# flake update 없이 rebuild — locked inputs 기반 (재현성 보장)
sudo nixos-rebuild switch --flake ~/git/dotfiles/nix/nixos#$HOSTNAME
```

> NixOS는 `nixos-rebuild` 시 locked flake inputs을 사용하므로 재현성 보장.
> 최신 패키지가 필요하면 사용자가 명시적으로 `nix flake update` 실행 후 rebuild.

#### Debian/Ubuntu (apt)

```bash
sudo apt update
apt list --upgradable
sudo apt upgrade -y

# autoremove 전 제거 대상 미리 보여주고 사용자 확인
apt list --autoremovable 2>/dev/null
sudo apt autoremove -y
```

#### Fedora (dnf)

```bash
# check-update: exit code 100 = 업데이트 있음 (정상)
sudo dnf check-update 2>/dev/null || [ $? -eq 100 ]
sudo dnf upgrade -y

# autoremove 전 제거 대상 미리 보여주고 사용자 확인
dnf autoremove --list 2>/dev/null
sudo dnf autoremove -y
```

### 4. 결과 리포트

```text
## System Upgrade 결과

| 항목 | 상태 |
| :--- | :--- |
| OS | macOS (axiom) |
| brew update | OK |
| brew upgrade | OK (23 packages) |
| brew cask | OK (5 casks) |
| brew bundle | OK (99 satisfied) |
| brew cleanup | OK (512MB freed) |
```

### 5. 후속 안내

- **AI 에이전트 업그레이드**: `/infra:agents upgrade` 실행 권장
- **보안 점검**: `/security:system-audit` 실행 권장
- **Shell 재시작**: zsh/completions 업데이트 시 `exec zsh`
- **재부팅**: 커널 업데이트 포함 시 안내

---

## Key Rules

- **시스템 패키지만 담당**: AI 에이전트·MCP·LSP는 `/infra:agents`로 분리
- **사용자 확인 후 실행** (upgrade): 사전 버전과 업그레이드 대상 수를 보여주고 승인 후 실행
- **Brewfile은 `brew bundle --global` 사용**: 수동 경로 지정 불필요. brew가 `$HOMEBREW_BUNDLE_FILE_GLOBAL` → `${XDG_CONFIG_HOME}/homebrew/Brewfile` → `~/.homebrew/Brewfile` → `~/.Brewfile` 순으로 자동 탐색
- **에러 시 중단하지 않음**: 일부 패키지/cask 실패해도 계속 진행하고 리포트에 명시
- **NixOS flake update는 명시적 요청 시만**: 기본은 `nixos-rebuild`만, `flake update`는 사용자 승인 필요
- **pip, npm 직접 사용 금지**: Python은 uv tool, Node는 pnpm으로 관리. pip/npm은 전이 의존성만 관리하므로 직접 업그레이드하지 않음
- **SteamOS 특례**: Node.js/corepack은 mise로 관리 → `npm install -g corepack` 불필요, `corepack prepare pnpm@latest --activate`로 활성화. uv도 mise 권장
- **한국어 리포트**: 결과는 항상 한국어로 출력
