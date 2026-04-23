# EcoAI

Claude Code용 커스텀 Skill 플러그인. React Native Android 배포 자동화 제공.

## Skill 목록

| Skill | 설명 |
| :--- | :--- |
| `deploy-android-wifi` | WiFi ADB로 Android 기기에 React Native 앱 빌드/배포 자동화 |

## 설치

### Marketplace 등록 (최초 1회)

```
claude plugin marketplace add https://repository.kr/crong/ecoai.git
```

### Plugin 설치

```
claude plugin install ecoai
```

### 대화형 명령어로 설치

```
/plugin install ecoai
```

## 사용

Claude Code 대화에서 Skill 트리거 키워드 사용:

```
배포해줘
디플로이
deploy
```

또는 Skill 직접 호출:

```
/ecoai:deploy-android-wifi
```

## 업그레이드

```bash
# Plugin 업데이트
claude plugin update ecoai

# 대화형 명령어
/plugin update ecoai
```

## 제거

```bash
claude plugin uninstall ecoai
```

## Skill 개발

### 새 Skill 추가

1. `.claude-plugin/skills/<skill-name>/SKILL.md` 생성
2. 아래 프론트매터 형식 준수:

```markdown
---
name: skill-name
description: Skill 설명
---

# Skill Title

...
```

3. `plugin.json`의 `version` patch 업그레이드
4. 커밋 & 푸시

### 버전 관리

[Semantic Versioning](https://semver.org/) 준수. `plugin.json`과 `marketplace.json` 버전 동기화 필수.

```bash
# patch 업그레이드 예시 (1.0.0 → 1.0.1)
# plugin.json, marketplace.json 두 파일 모두 수정 후 커밋
```

## 프로젝트 구조

```
.
├── .claude-plugin/
│   ├── plugin.json           # 플러그인 매니페스트
│   ├── marketplace.json      # 마켓플레이스 등록 정보
│   └── skills/
│       └── deploy-android-wifi/
│           └── SKILL.md      # 배포 자동화 Skill
├── CLAUDE.md                 # Claude Code 프로젝트 가이드
└── README.md
```
