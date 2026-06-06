# CLAUDE.md

## 프로젝트 개요

**zzizily** — 개인 자동화 AI Agent Skill 플러그인.

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
    ├── deploy-android-wifi/       # WiFi ADB 배포 자동화
    ├── security-audit/            # 보안 취약점 점검
    │   └── references/
    ├── korean-translation-verify/ # 한국어 번역 품질 검증
    │   ├── scripts/
    │   └── pyproject.toml
    ├── openwrt-initd/             # OpenWrt init.d 서비스 설치
    ├── hot-game-deals-n-news/     # 게임 할인/뉴스 트래커
    │   └── references/
    ├── exchange-rate-tracker/     # 환율 추적 (USD/KRW, USD/VND)
    │   ├── scripts/
    │   └── references/
    └── agents/                    # AI Agent/MCP 설치 자동화
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

- NixOS: `k8sgpt`만 nix 관리 (pnpm/uv 패키지 없음). 나머지는 pnpm/uv로 1원화
- 감지: binary 경로가 `/nix/store/` 또는 `/run/current-system/sw/bin/`이면 nix 관리
