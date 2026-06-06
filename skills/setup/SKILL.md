---
name: setup
description: "Setup machine from dotfiles. Detects hostname and runs stow, brew bundle, sops decryption, and Tailscale Aperture configuration. Requires ~/git/dotfiles to exist. Use when setting up a new machine or reconfiguring."
---

# Setup

`~/git/dotfiles` 기반으로 호스트별 머신 설정.

## 전제 조건

- `~/git/dotfiles` 존재해야 함. 없으면 중단.
- hostname이 아래 표에 해당해야 함.

## 호스트별 설정

| Hostname | OS | stow 패키지 | 추가 설정 |
| :--- | :--- | :--- | :--- |
| axiom | macOS | `base`, `axiom` | brew bundle, sops, Aperture |
| eve | macOS | `base`, `eve` | brew bundle, sops, Aperture |
| mo | NixOS | `base`, `mo` | nixos-rebuild, sops, Aperture |
| girl | SteamOS | `base`, `girl` | mise |
| walle | Debian | `base`, `walle` | sops |

## Workflow

### 1. dotfiles 존재 확인

```bash
if [ ! -d "$HOME/git/dotfiles" ]; then
  echo "~/git/dotfiles를 찾을 수 없습니다. 먼저 clone 해주세요."
  echo "  git clone git@github.com:deuxksy/dotfiles.git ~/git/dotfiles"
  # 중단
fi
```

### 2. hostname 감지

```bash
HOSTNAME=$(hostname -s 2>/dev/null || hostname | sed 's/\..*//')
```

지원하지 않는 hostname이면 중단.

### 3. stow 배포

```bash
cd ~/git/dotfiles

# 공통 (모든 호스트)
stow -t ~ base

# 호스트별
case $HOSTNAME in
  axiom) stow -t ~ axiom ;;
  eve)   stow -t ~ eve ;;
  mo)    stow -t ~ mo ;;
  girl)  stow -t ~ girl ;;
  walle) stow -t ~ walle ;;
esac
```

stow 충돌 시 기존 파일을 백업 후 제거하거나 `stow --adopt -t ~` 사용.

### 4. 패키지 설치

```bash
# macOS (axiom, eve)
cd ~ && brew bundle --file=~/git/dotfiles/$HOSTNAME/Brewfile

# NixOS (mo)
sudo nixos-rebuild switch --flake ~/git/dotfiles/nix/nixos#mo
```

### 5. secrets 복호화

```bash
# ~/.key 복호화 (sops age 키)
eval "$(sops -d ~/.key)"

# .env.sops 파일이 있는 경우
if [ -f ~/.hermes/.env.sops ]; then
  sops -d ~/.hermes/.env.sops > ~/.hermes/.env
fi
```

### 6. Tailscale Aperture 설정

Tailscale Aperture을 AI 프록시로 사용. 설정은 sops로 관리되는 API key와 연동.

- Aperture이 이미 설정되어 있는지 확인
- 환경변수: `ANTHROPIC_BASE_URL` 등이 Aperture을 가리키는지 확인
- 상세 설정은 `~/git/dotfiles/nix/nixos/hosts/mo/` (mo) 또는 `~/.claude/` (macOS) 참조

### 7. 결과 리포트

| 단계 | 상태 |
| :--- | :--- |
| dotfiles 확인 | OK |
| hostname 감지 | axiom |
| stow 배포 | OK (base, axiom) |
| brew bundle | OK (127 packages) |
| sops 복호화 | OK |
| Aperture | OK |

## Key Rules

- **~/git/dotfiles 없으면 중단**: 복구 불가
- **지원하지 않는 hostname이면 중단**: 수동 설정 안내
- **stow 충돌 시 사용자 확인**: 자동 삭제 금지
- **sops는 age 키 필요**: 키 없으면 복호화 스킵하고 안내
- **한국어 리포트**: 결과는 항상 한국어로 출력
