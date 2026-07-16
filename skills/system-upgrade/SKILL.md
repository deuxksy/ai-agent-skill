---
name: system-upgrade
description: "OS 패키지 매니저로 시스템 패키지 업그레이드. OS 감지해 brew upgrade, apt upgrade, dnf upgrade, 또는 nixos-rebuild 실행. 보안 점검은 /zzizily:system-audit 사용."
---

# System Upgrade

시스템 패키지 매니저로 전체 업그레이드.

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

| 감지 결과 | 패키지 매니저 | 업그레이드 명령 |
| :--- | :--- | :--- |
| macOS | brew | `brew update && brew upgrade && brew cleanup` |
| NixOS | nix | `sudo nixos-rebuild switch --flake ~/git/dotfiles/nix/nixos#<hostname>` |
| Debian/Ubuntu | apt | `sudo apt update && sudo apt upgrade -y` |
| Fedora | dnf | `sudo dnf upgrade -y` |

## Workflow

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

# Cask 업그레이드 (--greedy: auto-update 미지원 앱도 업그레이드)
brew upgrade --cask --greedy 2>/dev/null || true

# Brewfile 정합성 (hostname 기반 자동 선택)
BREWFILE=~/git/dotfiles/$HOSTNAME/Brewfile
if [ -f "$BREWFILE" ]; then
  cd ~ && brew bundle install --file="$BREWFILE"
else
  echo "Brewfile not found: $BREWFILE"
fi

brew cleanup
```

> Brewfile 경로를 `$HOSTNAME`으로 자동 선택 (axiom → axiom/Brewfile, eve → eve/Brewfile).

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

- **AI 에이전트 업그레이드**: `/zzizily:agents upgrade` 실행 권장
- **보안 점검**: `/zzizily:system-audit` 실행 권장
- **Shell 재시작**: zsh/completions 업데이트 시 `exec zsh`
- **재부팅**: 커널 업데이트 포함 시 안내

## Key Rules

- **사용자 확인 후 실행**: 사전 버전과 업그레이드 대상 수를 보여주고 승인 후 실행
- **에러 시 중단하지 않음**: 일부 패키지 실패해도 계속 진행하고 리포트에 명시
- **NixOS flake update는 명시적 요청 시만**: 기본은 `nixos-rebuild`만, `flake update`는 사용자 승인 필요
- **한국어 리포트**: 결과는 항상 한국어로 출력
- **agents upgrade와 분리**: 이 스킬은 시스템 패키지만, AI 에이전트는 `/zzizily:agents upgrade`
- **pip, npm 직접 사용 금지**: Python은 uv tool, Node는 pnpm으로 관리. pip/npm은 전이 의존성만 관리하므로 직접 업그레이드하지 않음
