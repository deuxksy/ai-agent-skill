# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 프로젝트 개요

**ecoai** — Claude Code 플러그인. 개인 자동화 Skill 모음.

- Author: Crong (kyolim)
- 버전 관리: Conventional Commits (말머리 영어, 메시지 한국어)

## 구조

```
.claude-plugin/
├── plugin.json          # 플러그인 매니페스트
├── marketplace.json     # 마켓플레이스 등록 정보
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

## Skills

| Skill | 설명 |
| :--- | :--- |
| `deploy-android-wifi` | WiFi ADB로 Android 기기에 React Native 앱 빌드/배포 자동화 |
| `security-audit` | 크로스 플랫폼 보안 취약점 및 업데이트 점검 (brew, npm, pip, mise 등) |
| `korean-translation-verify` | Gemma API로 한국어 기술 문서 번역 품질 검증 |
| `openwrt-initd-service` | OpenWrt init.d 백그라운드 서비스 설치 (procd 감시) |
| `hot-game-deals-n-news` | Steam/Epic/GOG 게임 할인, 무료 게임, 뉴스 체크 |
| `exchange-rate-tracker` | USD/KRW, USD/VND 환율 수집 및 그래프 시각화 |

## 개발 명령

플러그인 자체는 빌드/테스트 과정이 없음. Skill 파일(SKILL.md)을 직접 편집 후 커밋.

새 Skill 추가 시:
1. `skills/<skill-name>/SKILL.md` 생성
2. `plugin.json`의 `skills` 경로가 `./skills/`를 가리키므로 자동 인식
