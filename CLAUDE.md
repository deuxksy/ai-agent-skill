# CLAUDE.md

@./.ai/RULES.md

## 프로젝트 개요

**zzizily** — 9개 독립 도메인 플러그인을 통합 제공하는 개인 자동화 AI Agent Skill 마켓플레이스.

## Quick Start

```bash
# 마켓플레이스 등록
claude plugin marketplace add deuxksy/ai-agent-skill

# 원하는 도메인 플러그인 설치
claude plugin install security-audit@zzizily
claude plugin install infra-provisioning@zzizily
claude plugin install trackers-automation@zzizily
claude plugin install agent-dev-deploy@zzizily
claude plugin install session-workflow@zzizily
claude plugin install content-l10n@zzizily
claude plugin install git@zzizily
claude plugin install rules@zzizily
claude plugin install docs@zzizily
```

## 플러그인 메타 & 버전 정책

- **통합 단일 버전**: `1.10.0`
- **마켓플레이스 매니페스트**: `.claude-plugin/marketplace.json`
- **GitHub repo**: `deuxksy/ai-agent-skill`

## 구조

```
.
├── .claude-plugin/
│   └── marketplace.json     # 9개 전체 도메인 플러그인 등록 마켓플레이스 (v1.10.0)
├── agents/
│   └── verify.md            # Claude runner adapter (격리 reviewer fanout)
└── plugins/
    ├── security-audit/      # 코드/시스템 보안 감사 (code-audit, system-audit, backdoor-*)
    ├── infra-provisioning/  # 인프라 프로비저닝 (setup, system-upgrade, proxmox-vm-create, openwrt-initd)
    ├── trackers-automation/ # 자동화/트래커 (calendar-sync, exchange-rate-tracker, hot-game-deals-n-news)
    ├── agent-dev-deploy/    # 에이전트/배포 (agents, verify, deploy-android-wifi)
    ├── session-workflow/    # 세션 워크플로우 (handoff, resume)
    ├── content-l10n/        # 콘텐츠/번역 (optimize-images-4k, korean-translation-verify, product-planning-dr-pipeline)
    ├── git/                 # Git 워크플로우 (commit, commit-push-pr, clean-gone)
    ├── rules/               # 에이전트 지침 관리 (agents-md-management, revise-agents-md)
    └── docs/                # README 및 프로젝트 문서 관리 (docs-md-management, revise-readme-md)
```

## 분류 원칙

신규 스킬은 아래 기준으로 카테고리를 배치한다. 충돌 시 위 번호가 우선.

1. **보안 목적** (탐지/대응) → `security-audit`
2. **호스트/OS/VM 상태 변경** → `infra-provisioning`
3. **주기적 데이터 수집/동기화** → `trackers-automation`
4. **빌드/배포/개발 도구** → `agent-dev-deploy`
5. **파일/문서/번역 콘텐츠 처리** → `content-l10n`
6. **세션/작업 보존** → `session-workflow`

## 독립 도메인 플러그인 카탈로그 (9)

| Plugin | Version | Skills | 설치 |
| :--- | :--- | :--- | :--- |
| `security-audit` | 1.10.0 | `code-audit`, `system-audit`, `backdoor-investigation`, `backdoor-remediation` | `security-audit@zzizily` |
| `infra-provisioning` | 1.10.0 | `setup`, `system-upgrade`, `proxmox-vm-create`, `openwrt-initd` | `infra-provisioning@zzizily` |
| `trackers-automation` | 1.10.0 | `calendar-sync`, `exchange-rate-tracker`, `hot-game-deals-n-news` | `trackers-automation@zzizily` |
| `agent-dev-deploy` | 1.10.0 | `agents`, `verify`, `deploy-android-wifi` | `agent-dev-deploy@zzizily` |
| `session-workflow` | 1.10.0 | `handoff`, `resume` | `session-workflow@zzizily` |
| `content-l10n` | 1.10.0 | `optimize-images-4k`, `korean-translation-verify`, `product-planning-dr-pipeline` | `content-l10n@zzizily` |
| `git` | 1.10.0 | `commit`, `commit-push-pr`, `clean-gone` | `git@zzizily` |
| `rules` | 1.10.0 | `agents-md-management`, `revise-agents-md` | `rules@zzizily` |
| `docs` | 1.10.0 | `docs-md-management`, `revise-readme-md` | `docs@zzizily` |

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

## 버전 관리

[SemVer](https://semver.org/) 기반으로 관리하며 모든 9개 독립 플러그인 매니페스트 및 문서 표의 버전을 동기화한다.
