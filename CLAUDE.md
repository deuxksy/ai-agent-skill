# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 프로젝트 개요

**ecoai** — Claude Code 플러그인. React Native 개발 및 Android WiFi 배포 자동화 Skill 제공.

- Author: Crong (kyolim)
- 버전 관리: Conventional Commits (말머리 영어, 메시지 한국어)

## 구조

```
.claude-plugin/
├── plugin.json          # 플러그인 매니페스트 (이름, 버전, skills 경로)
├── marketplace.json     # 마켓플레이스 등록 정보
└── skills/
    └── deploy-android-wifi/
        └── SKILL.md     # WiFi ADB 배포 자동화 Skill
```

## Skill: deploy-android-wifi

WiFi ADB로 연결된 Android 기기에 React Native 앱을 빌드/배포하는 자동화 Skill.

**핵심 제약사항:**
- 배포: `npx react-native run-android` 우선 시도
- 실패 시(Windows `gradlew.bat` 경로 인식 문제) 폴백: `cd android && ./gradlew app:installDebug`
- WiFi 연결 시 `adb reverse tcp:8081 tcp:8081` 포트 포워딩 필수 (생략 시 "Unable to load script")
- 기본 대상 기기: `10.101.101.120:34593` (SM-F731N)

## 개발 명령

플러그인 자체는 빌드/테스트 과정이 없음. Skill 파일(SKILL.md)을 직접 편집 후 커밋.

새 Skill 추가 시:
1. `.claude-plugin/skills/<skill-name>/SKILL.md` 생성
2. `plugin.json`의 `skills` 경로가 `./skills/`를 가리키므로 자동 인식
