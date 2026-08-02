# Design Spec: 9 Domain-Focused Plugins Refactoring

- **Date**: 2026-08-02
- **Status**: Approved Design
- **Author**: Antigravity & User

---

## 1. Overview & Core Objectives

`deuxksy/ai-agent-skill` 모노레포 프로젝트의 26개 전체 스킬을 **9개 독립 도메인 플러그인(`plugins/`)** 구조로 완전히 리팩토링합니다.

### Core Objectives
1. **완전 모듈화 (Full Modularization)**: 루트 디렉토리의 `skills/`에 직접 위치했던 19개 스킬을 6개 신규 도메인 플러그인(`security-audit`, `infra-provisioning`, `trackers-automation`, `agent-dev-deploy`, `session-workflow`, `content-l10n`) 하위로 이동합니다.
2. **모노레포 단일통합 버전 (Unified Version v1.9.1)**: 저장소 전체의 모든 9개 독립 플러그인 매니페스트와 마켓플레이스가 동일한 버전 `1.9.1`을 공유합니다.
3. **멀티 런타임 호환성 (Multi-Runtime Compatibility)**: Claude Code, Codex, Antigravity(Gemini) 등 모든 에이전트 런타임에서 독립 설치(`claude plugin install <domain>@zzizily`) 가능하도록 지원합니다.

---

## 2. Architecture & Plugin Breakdown

전체 26개 스킬은 아래 9개 도메인 플러그인으로 분리 배치됩니다:

| # | 도메인 플러그인명 | 디렉토리 경로 | 포함 스킬 (Total 26) |
| :-: | :--- | :--- | :--- |
| 1 | **`security-audit`** | `plugins/security-audit/` | `code-audit`, `system-audit`, `backdoor-investigation`, `backdoor-remediation` |
| 2 | **`infra-provisioning`** | `plugins/infra-provisioning/` | `setup`, `system-upgrade`, `proxmox-vm-create`, `openwrt-initd` |
| 3 | **`trackers-automation`** | `plugins/trackers-automation/` | `calendar-sync`, `exchange-rate-tracker`, `hot-game-deals-n-news` |
| 4 | **`agent-dev-deploy`** | `plugins/agent-dev-deploy/` | `agents`, `verify`, `deploy-android-wifi` |
| 5 | **`session-workflow`** | `plugins/session-workflow/` | `handoff`, `resume` |
| 6 | **`content-l10n`** | `plugins/content-l10n/` | `optimize-images-4k`, `korean-translation-verify`, `product-planning-dr-pipeline` |
| 7 | **`commit-commands`** | `plugins/commit-commands/` | `commit`, `commit-push-pr`, `clean-gone` |
| 8 | **`agents-md-management`** | `plugins/agents-md-management/` | `agents-md-management`, `revise-agents-md` |
| 9 | **`readme-md-management`** | `plugins/readme-md-management/` | `readme-md-management`, `revise-readme-md` |

---

## 3. Directory & File Structure Spec

```text
ai-agent-skill/
├── .claude-plugin/
│   ├── plugin.json                    # 루트 매니페스트 (v1.9.1)
│   └── marketplace.json               # 9개 도메인 플러그인 등록 (v1.9.1)
├── README.md                          # 9개 플러그인 가이드 및 설치법
├── CLAUDE.md                          # 매핑표 및 프로젝트 구조 지침
└── plugins/                           # 9개 독립 도메인 플러그인 모음
    ├── security-audit/
    │   ├── README.md
    │   ├── .claude-plugin/plugin.json
    │   ├── .codex-plugin/plugin.json
    │   └── skills/ (4개 스킬)
    ├── infra-provisioning/
    │   ├── README.md
    │   ├── .claude-plugin/plugin.json
    │   ├── .codex-plugin/plugin.json
    │   └── skills/ (4개 스킬)
    ├── trackers-automation/
    │   ├── README.md
    │   ├── .claude-plugin/plugin.json
    │   ├── .codex-plugin/plugin.json
    │   └── skills/ (3개 스킬)
    ├── agent-dev-deploy/
    │   ├── README.md
    │   ├── .claude-plugin/plugin.json
    │   ├── .codex-plugin/plugin.json
    │   └── skills/ (3개 스킬)
    ├── session-workflow/
    │   ├── README.md
    │   ├── .claude-plugin/plugin.json
    │   ├── .codex-plugin/plugin.json
    │   └── skills/ (2개 스킬)
    ├── content-l10n/
    │   ├── README.md
    │   ├── .claude-plugin/plugin.json
    │   ├── .codex-plugin/plugin.json
    │   └── skills/ (3개 스킬)
    ├── commit-commands/ (기존)
    ├── agents-md-management/ (기존)
    └── readme-md-management/ (기존)
```

---

## 4. Manifest & Marketplace Standards

### 4.1. `.claude-plugin/plugin.json` Standard
- `"name"`: 도메인 플러그인명 (예: `security-audit`)
- `"version"`: `"1.9.1"`
- `"skills"`: `"./skills/"`

### 4.2. `.codex-plugin/plugin.json` Standard
- `"name"`: 도메인 플러그인명
- `"version"`: `"1.9.1"`
- `"skills"`: `"./skills/"`
- `"interface"`: 직관적인 한국어 `displayName`, `shortDescription`, `longDescription`, `category`, `capabilities`, `defaultPrompt` 명시

### 4.3. `.claude-plugin/marketplace.json` Standard
`plugins` 배열에 9개 전체 도메인 플러그인의 `name`, `source` (`./plugins/<name>`), `description`, `version` (`"1.9.1"`)을 등록합니다.

---

## 5. Safety, Migration & Verification Plan

1. **`git mv` 이력 보존**: 루트 `skills/`의 19개 스킬 폴더를 `git mv` 명령으로 해당 도메인 플러그인의 `skills/` 디렉토리로 안전하게 이동합니다.
2. **루트 `skills/` 제거**: 이동 완료 후 텅 빈 루트 `skills/` 디렉토리를 정리합니다.
3. **문서 갱신**: `README.md`, `CLAUDE.md` 및 신규 6개 `plugins/<domain>/README.md` 문서를 새 구조에 맞게 작성합니다.
4. **로컬 동기화**: `~/.gemini/config/plugins/` 디렉토리에 새로 개편된 플러그인들을 즉시 동기화합니다.
5. **검증**: `git status` 변경사항 확인, JSON 구문 검증, 커밋 및 원격 저장소 푸시를 수행합니다.
