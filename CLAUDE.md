# CLAUDE.md

## 프로젝트 개요

**zzizily** — 개인 자동화 Skill 모음.

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
    └── exchange-rate-tracker/     # 환율 추적 (USD/KRW, USD/VND)
        ├── scripts/
        └── references/
```

## Skill 호출

모든 스킬은 `/zzizily:<skill-name>` 형식으로 호출.

## SKILL.md 구조

각 스킬 디렉토리에 `SKILL.md` 파일이 필수. 최소 구조:

```markdown
---
name: <skill-name>
description: <한 줄 설명>
---

## 지침
<스킬 실행 로직>
```

## 개발 명령

플러그인 자체는 빌드/테스트 과정이 없음. Skill 파일(SKILL.md)을 직접 편집 후 커밋.

새 Skill 추가 시:
1. `skills/<skill-name>/SKILL.md` 생성
2. `plugin.json`의 `skills` 경로가 `./skills/`를 가리키므로 자동 인식
3. `/reload-plugins` 로 플러그인 리로드 후 `/zzizily:<skill-name>` 호출 테스트
