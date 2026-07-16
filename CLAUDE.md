# CLAUDE.md

## 프로젝트 개요

**zzizily** — 개인 자동화 AI Agent Skill 플러그인.

## Quick Start

```bash
# 설치
claude plugin marketplace add deuxksy/ai-agent-skill
claude plugin install deuxksy@zzizily

# 사용
/zzizily:<skill-name>

# 스킬 목록 확인
ls skills/
```

## 플러그인 메타

| 항목 | 값 |
| :--- | :--- |
| Plugin name | `zzizily` (plugin.json) |
| Marketplace plugin name | `deuxksy` (marketplace.json) |
| Marketplace name | `zzizily` |
| 호출 prefix | `/zzizily:<skill-name>` |
| GitHub repo | `deuxksy/ai-agent-skill` |

## 구조

```
.
├── .claude-plugin/
│   ├── plugin.json          # 플러그인 매니페스트
│   └── marketplace.json     # 마켓플레이스 등록 정보
├── agents/
│   └── verify.md            # 검증 subagent (격리 2-Way 교차검증, 루트 자동 발견)
└── skills/
    ├── agents/                    # AI Agent/MCP 설치 자동화
    ├── backdoor-investigation/    # Linux 백도어 포렌식 진단 (read-only)
    │   └── scripts/
    ├── backdoor-remediation/      # 백도어 제거·복구 (파괴적, 승인 필요)
    ├── calendar-sync/             # Notion/GCal → Hermes 일정 동기화
    │   └── scripts/
    ├── code-audit/                # 보안 취약점 점검
    ├── deploy-android-wifi/       # WiFi ADB 배포 자동화
    ├── exchange-rate-tracker/     # 환율 추적 (USD/KRW, USD/VND)
    │   ├── scripts/
    │   └── references/
    ├── handoff/                   # 세션 작업 저장 (/clear 전 수동)
    ├── hot-game-deals-n-news/     # 게임 할인/뉴스 트래커
    │   └── references/
    ├── korean-translation-verify/ # 한국어 번역 품질 검증
    │   ├── scripts/
    │   └── pyproject.toml
    ├── openwrt-initd/             # OpenWrt init.d 서비스 설치
    ├── optimize-images-4k/        # 4K 이미지 최적화
    │   ├── agents/
    │   └── scripts/
    ├── product-planning-dr-pipeline/ # 제품 기획 Deep Research 파이프라인
    │   ├── templates/             # 단계별 RQ/산출물 템플릿 (AGENTS/CONTEXT/ROADMAP/DESIGN)
    │   └── examples/              # 예시 산출물
    ├── proxmox-vm-create/         # Proxmox VE VM 프로비저닝 (qm→pvesh→REST)
    ├── resume/                    # 이전 handoff 복원 (승인 후 TaskCreate)
    ├── verify/                    # 검증 (Codex+Antigravity 2-Way 교차검증 진입점)
    ├── setup/                     # 초기 설정
    ├── system-audit/              # 시스템 감사
    │   └── references/
    └── system-upgrade/            # 시스템 업그레이드
```

## 분류 원칙

신규 스킬은 아래 기준으로 카테고리를 배치한다. 충돌 시 위 번호가 우선.

1. **보안 목적** (탐지/대응) → 보안·감사. 서버 변경이 겹쳐도 보안이 우선 (`backdoor-remediation` 참조)
2. **호스트/OS/VM 상태 변경** → 인프라·프로비저닝
3. **주기적 데이터 수집/동기화** (cron 전제) → 자동화·트래커
4. **빌드/배포/개발 도구** → AI Agent·배포. 단 OS 범용 패키지는 2번이 우선 (`agents`=AI 특화→4번, `system-upgrade`=OS 범용→2번)
5. **파일/문서/번역 콘텐츠 처리** → 콘텐츠·로컬라이제이션

그룹 내 정렬: 읽기전용 → 파괴적 → 생성 순 (안전한 것부터).

## 스킬 카탈로그 (19)

기능 도메인별 그룹핑. 신규 스킬 추가 시 [분류 원칙](#분류-원칙)에 따라 배치.

### 보안 · 감사 (Security & Audit)

| 스킬 | 설명 |
| :--- | :--- |
| code-audit | 정적 코드 보안 점검 (SAST/CWE/OWASP) |
| system-audit | 시스템 패키지 보안 감사 (CVE/CVSS/KEV) |
| backdoor-investigation | Linux 백도어 포렌식 진단 (read-only) |
| backdoor-remediation | 백도어 제거·복구 (파괴적, 승인 필요) |

### 인프라 · 프로비저닝 (Infra & Provisioning)

| 스킬 | 설명 |
| :--- | :--- |
| setup | 초기 설정 (brew/stow/sops/Tailscale) |
| system-upgrade | OS 패키지 업그레이드 (brew/apt/dnf/nix) |
| proxmox-vm-create | Proxmox VE VM 프로비저닝 (qm→pvesh→REST) |
| openwrt-initd | OpenWrt init.d 백그라운드 서비스 설치 |

### 자동화 · 트래커 (Automation & Trackers)

| 스킬 | 설명 |
| :--- | :--- |
| calendar-sync | Notion/GCal → Hermes 일정 동기화 |
| exchange-rate-tracker | 환율 추적 (USD/KRW, USD/VND) |
| hot-game-deals-n-news | 게임 할인/무료/뉴스 트래커 |

### AI Agent · 배포 (Agents & Deploy)

| 스킬 | 설명 |
| :--- | :--- |
| agents | AI Agent/MCP/LSP 설치·업그레이드 자동화 |
| verify | Codex+Antigravity 2-Way 교차검증 (spec/plan 항상 2-Way, 코드 3단계 티어) |
| deploy-android-wifi | WiFi ADB React Native 배포 자동화 |

### 워크플로우 · 세션 (Workflow & Session)

| 스킬 | 설명 |
| :--- | :--- |
| handoff | 현재 세션 작업을 .zzizily/handoff/에 구조화 저장 (/clear 전 수동) |
| resume | 이전 handoff 읽어 task preview → 승인 → TaskCreate 복원 (injection 차단) |

### 콘텐츠 · 로컬라이제이션 (Content & L10n)

| 스킬 | 설명 |
| :--- | :--- |
| optimize-images-4k | 4K 이미지 최적화 (ImageMagick) |
| korean-translation-verify | 한국어 번역 품질 검증 |
| product-planning-dr-pipeline | 제품 기획 Deep Research 파이프라인 |

## SKILL.md 규격

각 스킬 디렉토리에 `SKILL.md` 필수. 최소 구조:

```markdown
---
name: <skill-name>
description: <한 줄 설명>
---

## 지침
<스킬 실행 로직>
```

## 개발 워크플로우

빌드/테스트 과정 없음. SKILL.md 직접 편집 후 커밋.

### 새 Skill 추가

1. `skills/<skill-name>/SKILL.md` 생성
2. [분류 원칙](#분류-원칙)에 따라 카테고리 결정 → 스킬 카탈로그 테이블에 행 추가
3. `plugin.json` `skills` 경로가 `./skills/` → 자동 인식
4. `/reload-plugins` 후 `/zzizily:<skill-name>` 테스트

### 버전 관리

[SemVer](https://semver.org/). `plugin.json` / `marketplace.json` 버전 동기화 필수.

## 환경별 패키지 관리

- macOS: AI Agent(`codex`·`claude-code`·`antigravity-cli`)는 brew cask 우선 관리 — pnpm global(`minimumReleaseAge` 최신 지연)·native installer(PATH 충돌)·agy 자체 업데이터(추적 불일치) 회피. 분기/주의사항은 `skills/agents/SKILL.md` Brew Cask AI Agents 섹션
- zzizily verify: Codex MCP + Antigravity(agy) + gitleaks/sops 의존 — Codex/agy는 `agents` 스킬로 설치, gitleaks/sops는 `setup` 스킬로 관리
- NixOS: `k8sgpt`만 nix 패키지로 관리, 나머지는 pnpm/uv 사용
- 감지: binary 경로가 `/nix/store/` 또는 `/run/current-system/sw/bin/`이면 nix 관리. `/opt/homebrew/bin/`이면 brew
