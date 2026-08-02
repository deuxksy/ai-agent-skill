---
name: setup
description: "dotfiles 기반 머신 설정. hostname 감지해 brew bundle, stow, sops 복호화, Tailscale Aperture 설정 실행. ~/git/dotfiles 존재 필수. Use when 신규 머신 설정이나 재구성 시."
---

# Setup

`~/git/dotfiles` 기반으로 호스트별 머신 설정.

## 전제 조건

- `~/git/dotfiles` 존재해야 함. 없으면 중단.
- hostname이 아래 표에 해당해야 함.

## 호스트별 설정

| Hostname | OS | stow 패키지 | 추가 설정 |
| :--- | :--- | :--- | :--- |
| axiom | macOS | `base`, `axiom` | brew bundle, stow, sops, Aperture |
| eve | macOS | `base`, `eve` | brew bundle, stow, sops, Aperture |
| mo | NixOS | `base`, `mo` | nixos-rebuild, sops, Aperture |
| girl | SteamOS | `base`, `girl` | mise |
| walle | Proxmox (Debian) | `base`, `walle` | sops |

## Workflow

### 1. dotfiles 존재 확인

```bash
if [ ! -d "$HOME/git/dotfiles" ]; then
  echo "~/git/dotfiles를 찾을 수 없습니다. 먼저 clone 해주세요."
  echo "  git clone git@github.com:deuxksy/dotfiles.git ~/git/dotfiles"
  exit 1
fi
```

### 2. hostname 감지

```bash
HOSTNAME=$(hostname -s 2>/dev/null || hostname | sed 's/\..*//')

case $HOSTNAME in
  axiom|eve|mo|girl|walle) ;;
  *)
    echo "지원하지 않는 hostname: $HOSTNAME"
    echo "지원 목록: axiom, eve, mo, girl, walle"
    exit 1
    ;;
esac
```

### 3. 패키지 설치 (stow보다 먼저)

```bash
# macOS (axiom, eve) - Brewfile이 stow를 포함하므로 먼저 실행
cd ~ && brew bundle --file=~/git/dotfiles/$HOSTNAME/Brewfile

# NixOS (mo) - flake가 모든 패키지(stow 포함)를 관리
sudo nixos-rebuild switch --flake ~/git/dotfiles/nix/nixos#mo

# SteamOS (girl) - mise로 런타임 설치
cd ~/git/dotfiles/$HOSTNAME/scripts && ./setup.sh

# Proxmox/Debian (walle) - apt + 스크립트
apt install -y stow sops
cd ~/git/dotfiles/$HOSTNAME/scripts && ./install_nvtools.sh
```

### 4. stow 배포

```bash
cd ~/git/dotfiles

# 충돌 사전 확인
stow -t ~ --simulate --verbose base 2>&1

# 충돌이 있으면 사용자에게 확인 후 처리
# 옵션 1: 기존 파일 백업 후 제거
# 옵션 2: stow --adopt -t ~ (기존 파일을 dotfiles로 이동)

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

stow 충돌 시 `--simulate --verbose`로 먼저 확인. 사용자 승인 후에만 `--adopt` 사용.

### 5. secrets 복호화

```bash
# ~/.key 존재 확인
if [ ! -f ~/.key ]; then
  echo "~/.key 파일이 없습니다. sops 복호화를 스킵합니다."
  echo "age 키를 수동으로 배치해주세요."
else
  # 복호화 성공 여부 확인
  if ! sops -d ~/.key >/dev/null 2>&1; then
    echo "~/.key 복호화 실패. age 키를 확인해주세요."
  else
    eval "$(sops -d ~/.key)"
  fi
fi

# .env.sops 파일이 있는 경우 - 비원자적 덮어쓰기 방지
if [ -f ~/.hermes/.env.sops ]; then
  TMPFILE=$(mktemp)
  if sops -d ~/.hermes/.env.sops > "$TMPFILE" 2>/dev/null; then
    install -m 600 "$TMPFILE" ~/.hermes/.env
    rm -f "$TMPFILE"
  else
    rm -f "$TMPFILE"
    echo "~/.hermes/.env.sops 복호화 실패. 스킵합니다."
  fi
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
| 패키지 설치 | OK (brew bundle 127 packages) |
| stow 배포 | OK (base, axiom) |
| sops 복호화 | OK |
| Aperture | OK |

## Key Rules

- **~/git/dotfiles 없으면 중단**: `exit 1`로 즉시 종료. 복구 불가
- **지원하지 않는 hostname이면 중단**: `exit 1`로 즉시 종료. 수동 설정 안내
- **패키지 설치 → stow 순서**: brew/nix/mise가 stow를 설치하므로 패키지 설치 먼저
- **stow 충돌 시 사용자 확인**: `--simulate`로 사전 확인. `--adopt`는 승인 후만 사용
- **sops는 age 키 필요**: 키 없으면 복호화 스킵하고 안내
- **sops 덮어쓰기 안전**: 임시 파일에 복호화 후 `install -m 600`으로 교체
- **한국어 리포트**: 결과는 항상 한국어로 출력
