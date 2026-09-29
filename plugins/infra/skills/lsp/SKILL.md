---
name: lsp
description: "Use when language servers for Java/Spring, JavaScript/TypeScript, Python, Go, Terraform, Ansible, YAML, shell, Lua, or Markdown are missing or need installation or upgrade."
---

# LSP

코드 심볼 분석에 필요한 language server를 설치·검증·업그레이드한다. 설치 후 실행 파일이 `PATH`에 있어야 Serena/OMC 등의 `lsp_*` 도구가 자동 감지할 수 있다.

> **범위 구분**: 이 스킬은 LSP server의 lifecycle만 담당한다.
> JDK, Node.js, Python, Go, pnpm 등 런타임과 패키지 관리자는 `/infra:packages`에서 준비한다.
> AI 에이전트와 MCP server는 `/infra:agents`에서 관리한다.

## OS 감지

```bash
KERNEL=$(uname -s)
OS=$(grep '^ID=' /etc/os-release 2>/dev/null | cut -d= -f2 | tr -d '"')
```

| 감지 결과 | 설치 방식 |
| :--- | :--- |
| macOS | pnpm + brew |
| SteamOS | pnpm + Linuxbrew |
| Debian/Ubuntu/Fedora | pnpm + 공식 패키지 또는 release binary |
| NixOS | nix |

## 관리 대상

### 요청 언어

| 생태계 | 패키지 | 실행 파일 | 관리 방식 |
| :--- | :--- | :--- | :--- |
| Java/Spring | `jdtls` / `jdt-language-server` | `jdtls` | brew, upstream binary, nix |
| | `spring-boot-language-server` | `spring-boot-language-server` | Spring Tools 4 release vsix / OpenVSX 추출 + wrapper |
| JavaScript/TypeScript | `typescript-language-server` + `typescript` | `typescript-language-server` | pnpm, nix |
| Python | `pyright` | `pyright-langserver` | pnpm, nix |
| Go | `gopls` | `gopls` | brew, `go install`, nix |
| Terraform | `terraform-ls` | `terraform-ls` | brew, 공식 패키지/binary, nix |
| Ansible | `@ansible/ansible-language-server` | `ansible-language-server` | pnpm, nix |

`jdtls`는 Maven/Gradle 기반 Java 프로젝트의 기본 코드 분석(클래스/메서드 정의, 타입 검사)을 수행하며, `spring-boot-language-server`(Spring Tools 4)는 `application.properties`/`application.yml` 자동완성과 Spring Boot 전용 어노테이션 진단을 제공한다. 두 서버를 함께 실행하여 완전한 Spring 개발 환경을 구성한다.

### 추가 범용 서버

| 패키지 | 대상 | 관리 방식 |
| :--- | :--- | :--- |
| `yaml-language-server` | YAML, CI, config | pnpm, nix |
| `bash-language-server` | Bash/Zsh | pnpm, nix |
| `vscode-langservers-extracted` | JSON/HTML/CSS | pnpm, nix |
| `lua-language-server` | Lua | brew, upstream binary, nix |
| `marksman` | Markdown | brew, upstream binary, nix |

## Install

### 1. Prerequisites 확인

필요한 런타임과 패키지 관리자가 없으면 `/infra:packages install`로 먼저 준비한다.

```bash
command -v pnpm >/dev/null || echo "MISSING: pnpm"
command -v java >/dev/null || echo "MISSING: Java 21+ (jdtls)"
command -v go >/dev/null || echo "MISSING: Go (gopls)"
java -version 2>&1 | head -1
go version
```

`jdtls` 실행에는 Java 21 이상이 필요하다. `gopls`는 설치된 Go toolchain과 프로젝트가 사용하는 Go 버전의 호환성도 확인한다.

### 2. 설치

이미 실행 파일이 `PATH`에 있으면 해당 서버를 스킵한다. 한 서버의 실패가 나머지 설치를 중단하지 않도록 개별 결과를 기록한다.

#### macOS / SteamOS

```bash
# Node 기반 LSP
pnpm add -g typescript@latest typescript-language-server@latest yaml-language-server@latest bash-language-server@latest pyright@latest vscode-langservers-extracted@latest @ansible/ansible-language-server@latest

# macOS Homebrew / SteamOS Linuxbrew
brew install lua-language-server marksman terraform-ls jdtls gopls

# Spring Boot LSP (Spring Tools 4)
# release vsix(또는 OpenVSX)에서 language-server를 ~/.local/share/spring-boot-language-server 에 추출하고
# ~/.local/bin/spring-boot-language-server 실행 래퍼 등록 (--version 인자에 버전을 출력하고 종료 — 검증 단계에서 사용)
```

#### Debian / Ubuntu / Fedora

```bash
# Node 기반 LSP
pnpm add -g typescript@latest typescript-language-server@latest yaml-language-server@latest bash-language-server@latest pyright@latest vscode-langservers-extracted@latest @ansible/ansible-language-server@latest

# Go 공식 설치 방식
go install golang.org/x/tools/gopls@latest

# Spring Boot LSP (Spring Tools 4)
# release vsix에서 추출 후 ~/.local/share/ 및 ~/.local/bin 래퍼 등록 (--version 처리 포함)
```

- `jdtls`: Eclipse JDT.LS의 최신 milestone archive를 내려받아 압축을 풀고 upstream `bin/jdtls`를 `PATH`에 노출한다. (Java 21+ 필요)
- `spring-boot-language-server`: Spring Tools 4 공식 release vsix에서 `extension/language-server` jar를 추출하고 `~/.local/bin/spring-boot-language-server` 래퍼를 구성한다.
- `terraform-ls`: HashiCorp 공식 apt/RPM 저장소의 `terraform-ls` 패키지 또는 release archive를 사용한다.
- `lua-language-server`, `marksman`: 각 프로젝트의 최신 GitHub release binary를 사용한다.
- release archive를 설치할 때는 제공되는 checksum을 검증하고 임시 디렉터리는 `mktemp -d`로 만든다.

#### NixOS

선언형 `configuration.nix`의 `environment.systemPackages`가 우선이다. 임시 profile 설치가 필요한 경우:

```bash
nix profile install \
  nixpkgs#typescript-language-server nixpkgs#yaml-language-server \
  nixpkgs#bash-language-server nixpkgs#pyright \
  nixpkgs#vscode-langservers-extracted nixpkgs#ansible-language-server \
  nixpkgs#lua-language-server nixpkgs#marksman nixpkgs#terraform-ls \
  nixpkgs#jdt-language-server nixpkgs#gopls
```

### 3. 설치 검증

각 서버를 직접 확인하고 `OK`, `MISSING`, `FAIL` 상태와 버전을 한국어 표로 출력한다. `--version`을 지원하지 않는 서버는 패키지 관리자와 `command -v`를 함께 사용한다.

```bash
# 요청 언어
typescript-language-server --version
pyright --version
gopls version
terraform-ls -version
ansible-language-server --version
command -v jdtls
spring-boot-language-server --version

# 추가 범용 서버
yaml-language-server --version
bash-language-server --version
pnpm list -g --depth=0 | grep vscode-langservers-extracted

# brew 설치 서버
brew list --versions lua-language-server marksman terraform-ls jdtls gopls
```

## Upgrade

### 1. 사전 버전 수집과 사용자 확인

Install의 검증 명령으로 현재 버전을 먼저 수집한다. 결과와 실행할 패키지 관리자별 명령을 보여주고 사용자 확인 후 업그레이드한다.

### 2. 업그레이드 실행

```bash
# macOS / SteamOS / Debian / Ubuntu / Fedora - Node 기반 LSP
pnpm update -g --latest typescript typescript-language-server yaml-language-server bash-language-server pyright vscode-langservers-extracted @ansible/ansible-language-server

# macOS / SteamOS - brew 기반 LSP
brew upgrade lua-language-server marksman terraform-ls jdtls gopls

# Debian / Ubuntu / Fedora - Go 공식 방식
go install golang.org/x/tools/gopls@latest

# Debian / Ubuntu / Fedora - jdtls/terraform-ls/lua-language-server/marksman
# 공식 저장소 패키지를 업그레이드하거나 최신 release binary를 checksum 검증 후 교체

# Spring Boot LSP (Spring Tools 4)
# GitHub release 또는 OpenVSX에서 최신 vsix를 확인하고 버전 변경 시 ~/.local/share/ 에 재추출

# NixOS profile 설치분
nix profile upgrade \
  '.*typescript-language-server.*' '.*yaml-language-server.*' \
  '.*bash-language-server.*' '.*pyright.*' \
  '.*vscode-langservers-extracted.*' '.*ansible-language-server.*' \
  '.*lua-language-server.*' '.*marksman.*' '.*terraform-ls.*' \
  '.*jdt-language-server.*' '.*gopls.*'
```

### 3. 업그레이드 검증

Install의 검증 명령을 다시 실행해 이전/이후 버전과 상태를 비교한다. 변경이 없으면 "모든 LSP server가 최신 버전입니다"를 출력한다.

## Key Rules

- **레이어 분리**: LSP server는 이 스킬, 런타임과 패키지 관리자는 `/infra:packages`, AI Agent/MCP는 `/infra:agents` 담당
- **멱등성**: install 시 이미 설치된 실행 파일은 스킵
- **dry-run 먼저**: upgrade는 현재 버전과 실행 명령을 보여주고 사용자 확인 후 수행
- **PATH 검증**: 설치 직후 `command -v`와 버전 명령을 함께 확인
- **부분 실패 허용**: 실패한 서버는 `FAIL`로 기록하고 나머지 작업을 계속 수행
- **공식 배포 우선**: upstream package, 공식 저장소, 서명/checksum이 제공되는 release artifact를 우선
- **NixOS 선언형 관리 우선**: `nix profile`보다 `configuration.nix`와 `nixos-rebuild`를 우선
- **한국어 리포트**: 결과는 항상 한국어로 출력
