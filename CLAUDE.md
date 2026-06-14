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
└── skills/
    ├── agents/                    # AI Agent/MCP 설치 자동화
    ├── code-audit/                # 보안 취약점 점검
    ├── deploy-android-wifi/       # WiFi ADB 배포 자동화
    ├── exchange-rate-tracker/     # 환율 추적 (USD/KRW, USD/VND)
    │   ├── scripts/
    │   └── references/
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
    ├── setup/                     # 초기 설정
    ├── system-audit/              # 시스템 감사
    │   └── references/
    └── system-upgrade/            # 시스템 업그레이드
```

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
2. `plugin.json` `skills` 경로가 `./skills/` → 자동 인식
3. `/reload-plugins` 후 `/zzizily:<skill-name>` 테스트

### 버전 관리

[SemVer](https://semver.org/). `plugin.json` / `marketplace.json` 버전 동기화 필수.

## 환경별 패키지 관리

- NixOS: `k8sgpt`만 nix 패키지로 관리, 나머지는 pnpm/uv 사용
- 감지: binary 경로가 `/nix/store/` 또는 `/run/current-system/sw/bin/`이면 nix 관리
