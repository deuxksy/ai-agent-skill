---
name: agents
description: "모든 AI Agent, MCP server, LSP server를 설치하거나 업그레이드. OS를 감지해 pnpm, uv, brew, nix를 플랫폼별 방식으로 실행. 'install'로 신규 머신 설정, 'upgrade'로 기존 agent 업데이트. 시스템 패키지(prerequisites 포함)는 /infra:packages 사용."
---

# Agents

모든 AI Agent, MCP server, LSP server를 설치하거나 업그레이드.

> **범위 구분**: 이 스킬은 코딩 도구(AI 에이전트·MCP·LSP)만 담당.
> pnpm/uv/mise 등 prerequisites와 OS 시스템 패키지는 `/infra:packages` 사용.

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

### LSP Servers

Serena/OMC LSP 도구(`lsp_*`)가 코드 심볼 분석에 사용. PATH에 있어야 자동 감지. `nil`은 NixOS에서만 설치한다.

#### pnpm

| 패키지 | LSP | 용도 |
| :--- | :--- | :--- |
| `typescript-language-server` | TS/JS | TypeScript/TSX |
| `yaml-language-server` | YAML | Ansible, CI, config |
| `bash-language-server` | Bash/Zsh | shell script |
| `pyright` | Python | Python |
| `vscode-langservers-extracted` | JSON/HTML/CSS | 범용 번들 |
| `@ansible/ansible-language-server` | Ansible | playbook |

#### OS별

| 패키지 | macOS/SteamOS | Debian/Ubuntu/Fedora | NixOS |
| :--- | :--- | :--- | :--- |
| lua-language-server | brew | binary download | nix |
| marksman | brew | binary download | nix |
| terraform-ls | brew | binary download | nix |
| nil | — | — | nix |
| gopls | brew | go install | nix |
| jdtls | brew | [Eclipse milestone build](https://github.com/eclipse-jdtls/eclipse.jdt.ls#installation) | nix |
| kotlin-lsp | brew cask | [공식 standalone archive](https://github.com/Kotlin/kotlin-lsp/releases) | 공식 archive |
| sourcekit-lsp | Xcode/Swift toolchain | Swift toolchain | Swift toolchain |

#### Java / Spring Boot

| 서버 | 용도 | 배포 경로 |
| :--- | :--- | :--- |
| Eclipse JDT LS (`jdtls`) | Java 코드 분석, Maven/Gradle 프로젝트 인식 | [Eclipse JDT LS](https://github.com/eclipse-jdtls/eclipse.jdt.ls) |
| Spring Boot Language Server | Spring 코드와 `application.yml`/`application.properties` 지원 | [Spring Boot Tools VS Code 확장](https://github.com/spring-projects/spring-tools/tree/main/vscode-extensions/vscode-spring-boot) 내 JAR |

Spring Boot Language Server의 전체 Java 기능은 실행 중인 JDT LS와의 통신에 의존한다. 두 서버 설치 후 LSP 클라이언트의 Java/Spring 연동도 설정해야 한다. Spring 서버 JAR만 PATH에 두어서는 자동 감지되지 않는다. [Spring Tools 클라이언트 통합 문서](https://github.com/spring-projects/spring-tools/wiki/Developer-Manual-Integrate-Language-Server-Into-Client) 참조.

#### iOS / Android

| 도구 | 용도 | 설치 경로 |
| :--- | :--- | :--- |
| SourceKit-LSP | iOS/Swift 코드 분석 | [Xcode 또는 Swift toolchain에 포함](https://github.com/swiftlang/sourcekit-lsp) |
| Kotlin LSP | Kotlin 코드 분석; Android Gradle Plugin 지원은 experimental | [JetBrains 공식 배포](https://github.com/Kotlin/kotlin-lsp) |
| Android Studio | Android/Kotlin 통합 IDE (별도 LSP 아님) | [Android Studio](https://developer.android.com/studio/install) |

Kotlin LSP의 VS Code 확장 ID는 `jetbrains.kotlin-server`이며, standalone CLI는 macOS에서 `kotlin-lsp` Homebrew cask로 설치한다. Android Studio는 자체 Kotlin 도구를 제공하므로 별도 Kotlin LSP와 중복 실행하지 않는다.

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

```bash
# pnpm (전 OS) - @latest 지정 필수
pnpm add -g typescript-language-server@latest yaml-language-server@latest bash-language-server@latest pyright@latest vscode-langservers-extracted@latest @ansible/ansible-language-server@latest

# macOS / SteamOS (Linuxbrew)
brew install lua-language-server marksman terraform-ls gopls jdtls

# macOS - Kotlin standalone LSP
brew install --cask kotlin-lsp

# Debian/Ubuntu/Fedora - 각 프로젝트 GitHub release binary (gopls는 go install golang.org/x/tools/gopls@latest)

# iOS/macOS - Xcode 또는 Swift toolchain에 포함된 SourceKit-LSP 확인
command -v sourcekit-lsp

# Android Studio (macOS) - GUI IDE; 이미 설치된 경우 스킵
brew install --cask android-studio

# NixOS - configuration.nix (environment.system.packages) 또는 nix profile
nix profile install nixpkgs#lua-language-server nixpkgs#marksman nixpkgs#terraform-ls nixpkgs#nil nixpkgs#gopls nixpkgs#jdt-language-server
```

Java/Spring Boot: `jdtls` 실행에는 JDK 21 이상이 필요하다. Debian/Ubuntu/Fedora에서는 위 Eclipse milestone build를 내려받아 설치한다. Spring Boot Tools를 쓰는 VS Code에서는 Java 확장과 Spring Boot Tools 확장을 설치하면 두 서버가 함께 실행된다. 다른 LSP 클라이언트에서는 [공식 Spring Boot Tools VSIX](https://github.com/spring-projects/spring-tools/wiki/Developer-Manual-Integrate-Language-Server-Into-Client)에서 서버 JAR를 추출하고, 해당 클라이언트에 JDT LS와 Spring Boot LS 실행 및 상호 통신을 설정한다. 설치 파일을 받기 전에 클라이언트의 Spring 연동 지원 여부를 확인한다.

```bash
# VS Code가 설치된 경우에만 Java/Spring 확장 설치
if command -v code >/dev/null; then code --install-extension redhat.java; code --install-extension vmware.vscode-spring-boot; fi
```

Kotlin: VS Code에서는 `jetbrains.kotlin-server` 확장을 설치한다. 다른 클라이언트에서는 OS별 [standalone archive](https://github.com/Kotlin/kotlin-lsp/releases)를 사용한다. Android 프로젝트 import는 experimental이며, 최신 standalone 배포의 JDK 요구사항을 릴리스 노트에서 확인한다. Android Studio는 macOS 외에는 [공식 설치 절차](https://developer.android.com/studio/install)를 따른다. iOS 빌드는 Xcode가 필요하다.

```bash
# VS Code가 설치된 경우에만 Kotlin LSP 확장 설치
command -v code >/dev/null && code --install-extension jetbrains.kotlin-server
```

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

# pnpm - LSP Servers
typescript-language-server --version
yaml-language-server --version
bash-language-server --version
pyright --version
ansible-language-server --version

# pnpm - LSP (--version 미지원)
pnpm list -g --depth=0 | grep vscode-langservers-extracted

# brew - LSP Servers
brew list --versions lua-language-server marksman terraform-ls gopls jdtls

# Kotlin / iOS / Android
command -v kotlin-lsp
command -v sourcekit-lsp
brew list --cask --versions kotlin-lsp android-studio
command -v code >/dev/null && code --list-extensions --show-versions | grep '^jetbrains.kotlin-server@'

# nil (NixOS)
if [ -f /etc/os-release ] && grep -q '^ID=nixos' /etc/os-release; then nil --version; fi

# gopls
gopls version

# Java / Spring Boot - JDT LS 패키지 확인 후 클라이언트에서 두 서버의 초기화/진단 확인
command -v jdtls || command -v jdt-language-server
command -v code >/dev/null && code --list-extensions --show-versions | grep -E '^(redhat.java|vmware.vscode-spring-boot)@'
```

| 패키지 | 관리 | 상태 | 버전 |
| :--- | :--- | :--- | :--- |
| @openai/codex | pnpm | OK | 0.137.0 |
| agy (Antigravity) | standalone | OK | 1.0.13 |

> **참고**:
> - `holmes`는 `--version` 미지원으로 하위 명령 방식 사용.
> - `dbhub`, `proxmox-mcp-plus`, `doris-mcp-server`는 `--version` 미지원으로 `pnpm list` / `uv tool list`로 확인.
> - `vscode-langservers-extracted`는 `--version` 미지원으로 `pnpm list`로 확인. brew LSP(lua-language-server, marksman, terraform-ls, gopls)는 `brew list --versions`로 확인.
> - `nil`은 NixOS에서만 nix로 설치·갱신한다.

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

```bash
# pnpm (전 OS)
pnpm update -g --latest typescript-language-server yaml-language-server bash-language-server pyright vscode-langservers-extracted @ansible/ansible-language-server

# macOS / SteamOS (Linuxbrew)
brew upgrade lua-language-server marksman terraform-ls gopls jdtls

# macOS - Kotlin standalone LSP
brew upgrade --cask kotlin-lsp

# Debian/Ubuntu/Fedora - gopls는 go install golang.org/x/tools/gopls@latest

# NixOS - nix profile upgrade (configuration.nix 관리 시 flake update + nixos-rebuild)
nix profile upgrade '.*lua-language-server.*' '.*marksman.*' '.*terraform-ls.*' '.*nil.*' '.*gopls.*' '.*jdt-language-server.*'
```

SourceKit-LSP는 Xcode/Swift toolchain 업데이트로, Android Studio는 macOS에서 `brew upgrade --cask android-studio`로 갱신한다. Kotlin LSP의 standalone archive를 수동 설치했다면 공식 최신 archive로 교체한다.

Spring Boot Language Server는 배포에 사용한 Spring Boot Tools 확장을 업데이트한다. VSIX에서 수동 추출했다면 새 VSIX로 JAR를 교체한 뒤 LSP 클라이언트를 재시작하고 Java/Spring 진단을 확인한다. JDT LS는 Debian/Ubuntu/Fedora에서 새 Eclipse milestone build로 교체한다.

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
- **멱등성** (install): 이미 설치된 패키지는 스킵
- **dry-run 먼저** (upgrade): 버전 수집 → 사용자 확인 → 실행
- **에러 중단하지 않음**: 실패한 패키지는 리포트에 명시하고 계속 진행
- **Brew Cask 우선 (macOS)**: `codex`·`claude-code`·`antigravity-cli`는 brew cask로 관리. brew formula/cask에 존재하면 pnpm/uv/native보다 우선 (`brew search`로 확인)
- **pnpm minimumReleaseAge 주의**: pnpm global은 supply chain 보호로 publish 후 약 24시간 동안 최신 버전 설치 차단 (`ERR_PNPM_NO_MATURE_MATCHING_VERSION`). `(x.xx.x is available)`가 떠도 강제 설치 불가 → macOS는 brew cask로 우회
- **mise/pnpm PATH 충돌 주의**: mise node global bin이 pnpm global bin보다 PATH에서 선행하면 stale 구버전이 실행됨. 업그레이드 후 반드시 `which <cli>` + `--version` 교차 검증. mise node global 중복 패키지는 `npm uninstall -g`로 제거
- **Claude Code**: macOS는 brew cask `claude-code`로 관리 (native installer 대체). `~/.claude/` 설정은 공유. 타 OS는 native installer 유지
- **NixOS 특례**: 모든 패키지 매니저(pnpm, uv)와 LSP가 nix로 관리됨. `nil`은 NixOS에서만 설치
- **Antigravity CLI 특례**: macOS는 homebrew-cask (`auto_updates`) — `brew upgrade --cask` 실패 시 `agy update`로 폴백. SteamOS/Linux는 installer 스크립트 (자체 `agy update`), NixOS는 nixpkgs `antigravity-cli` 패키지
- **Gemini desktop**: macOS는 brew cask `google-gemini`(`auto_updates`, Google 자체 업데이터)로 관리. Gemini CLI(2026-06-18 서비스 중단)·Antigravity CLI(`agy`)·Gemini 데스크톱 앱은 별개 제품이며, cask `gemini`(MacPaw 디스크 클리너)와 혼동 금지. GUI 앱이라 버전 검증은 `brew list --cask --versions google-gemini` 사용
- **SteamOS 특례**: Node.js/corepack은 mise로 관리. antigravity는 installer 스크립트
- **한국어 리포트**: 결과는 항상 한국어로 출력
