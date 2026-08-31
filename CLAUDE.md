# CLAUDE.md

@./.ai/RULES.md

## 프로젝트 개요

**zzizily** — 11개 독립 도메인 플러그인을 통합 제공하는 개인 자동화 AI Agent Skill 마켓플레이스.

## Quick Start

```bash
# 마켓플레이스 등록
claude plugin marketplace add deuxksy/ai-agent-skill

# 원하는 도메인 플러그인 설치
claude plugin install security@zzizily
claude plugin install infra@zzizily
claude plugin install trackers@zzizily
claude plugin install sessions@zzizily
claude plugin install l10n@zzizily
claude plugin install git@zzizily
claude plugin install rules@zzizily
claude plugin install docs@zzizily
claude plugin install review@zzizily
claude plugin install dev@zzizily
claude plugin install jmeter@zzizily
```

## 플러그인 메타 & 버전 정책

- **통합 단일 버전**: `1.19.0` (비공개 플러그인 `meridian` 제외 — 독립 버전)
- **마켓플레이스 매니페스트**: `.claude-plugin/marketplace.json`
- **GitHub repo**: `deuxksy/ai-agent-skill`

## 구조

```
.
├── .claude-plugin/
│   └── marketplace.json     # 11개 전체 도메인 플러그인 등록 마켓플레이스 (v1.19.0)
├── agents/
│   └── verify.md            # Claude runner adapter (격리 reviewer fanout)
├── docs/                    # 프로젝트 서브 문서 (docs/README.md, docs/okf/)
└── plugins/
    ├── security/            # 코드/시스템 보안 감사 (code-audit, system-audit, backdoor-*)
    ├── infra/               # 인프라 프로비저닝 (setup, packages, agents, proxmox-vm-create, openwrt-initd, acl-owner-reset)
    ├── trackers/            # 자동화/트래커 (calendar-sync, exchange-rate-tracker, hot-game-deals-n-news, notion-sprint-sync)
    ├── sessions/            # 세션 워크플로우 (handoff, resume)
    ├── l10n/                # 콘텐츠/번역 (optimize-images-4k, korean-translation-verify, product-planning-dr-pipeline)
    ├── git/                 # Git 워크플로우 (commit, commit-push-pr, clean-gone, tag-release)
    ├── rules/               # 에이전트 지침 관리 (agents-md-management, revise-agents-md)
    ├── docs/                # README 및 프로젝트 문서 관리 (docs-md-management, docs-restructure, revise-readme-md)
    ├── review/              # 교차 검증 (verify)
    ├── dev/                 # 빌드/배포 (deploy-android-wifi, license, update-openapi)
    ├── jmeter/              # 부하 테스트 (lint, deploy, run, knee, collect, report, bottleneck)
    └── meridian/            # 원격 미디어 파이프라인 — 마켓플레이스 미등록·로컬 전용
```

## 분류 원칙

신규 스킬은 아래 기준으로 카테고리를 배치한다. 충돌 시 위 번호가 우선.

1. **보안 목적** (탐지/대응) → `security`
2. **호스트/OS/VM 상태 변경** → `infra`
3. **주기적 데이터 수집/동기화** → `trackers`
4. **교차 검증/리뷰** → `review`
5. **빌드/배포/개발 도구** → `dev`
6. **파일/문서/번역 콘텐츠 처리** → `l10n`
7. **세션/작업 보존** → `sessions`
8. **부하 테스트/JMeter 실행** → `jmeter`

## 독립 도메인 플러그인 카탈로그 (11)

| Plugin | Version | Skills | 설치 |
| :--- | :--- | :--- | :--- |
| `security` | 1.19.0 | `code-audit`, `system-audit`, `backdoor-investigation`, `backdoor-remediation` | `security@zzizily` |
| `infra` | 1.19.0 | `setup`, `packages`, `agents`, `proxmox-vm-create`, `openwrt-initd`, `acl-owner-reset` | `infra@zzizily` |
| `trackers` | 1.19.0 | `calendar-sync`, `exchange-rate-tracker`, `hot-game-deals-n-news`, `notion-sprint-sync` | `trackers@zzizily` |
| `sessions` | 1.19.0 | `handoff`, `resume` | `sessions@zzizily` |
| `l10n` | 1.19.0 | `optimize-images-4k`, `korean-translation-verify`, `product-planning-dr-pipeline` | `l10n@zzizily` |
| `git` | 1.19.0 | `commit`, `commit-push-pr`, `clean-gone`, `tag-release` | `git@zzizily` |
| `rules` | 1.19.0 | `agents-md-management`, `revise-agents-md` | `rules@zzizily` |
| `docs` | 1.19.0 | `docs-md-management`, `docs-restructure`, `revise-readme-md` | `docs@zzizily` |
| `review` | 1.19.0 | `verify` | `review@zzizily` |
| `dev` | 1.19.0 | `deploy-android-wifi`, `license`, `update-openapi` | `dev@zzizily` |
| `jmeter` | 1.19.0 | `lint`, `deploy`, `run`, `knee`, `collect`, `report`, `bottleneck` | `jmeter@zzizily` |

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

[SemVer](https://semver.org/) 기반으로 관리하며 모든 11개 독립 플러그인 매니페스트 및 문서 표의 버전을 동기화한다.
