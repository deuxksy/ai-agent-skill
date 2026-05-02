# AI-Agent-Skill

Claude Code용 커스텀 Skill 플러그인. 개인 자동화 스킬 모음.

## Skill 목록

| Skill | 설명 |
| :--- | :--- |
| `deploy-android-wifi` | WiFi ADB로 Android 기기에 React Native 앱 빌드/배포 자동화 |
| `security-audit` | 크로스 플랫폼 보안 취약점 및 업데이트 점검 (brew, npm, pip, mise 등) |
| `korean-translation-verify` | Gemma API로 한국어 기술 문서 번역 품질 검증 |
| `openwrt-initd` | OpenWrt init.d 백그라운드 서비스 설치 (procd 감시) |
| `hot-game-deals-n-news` | Steam/Epic/GOG 게임 할인, 무료 게임, 뉴스 체크 |
| `exchange-rate-tracker` | USD/KRW, USD/VND 환율 수집 및 그래프 시각화 |

## 설치

### Marketplace 등록 (최초 1회)

```
claude plugin marketplace add deuxksy/ai-agent-skill
```

### Plugin 설치

```
claude plugin install crong@github
```

### 대화형 명령어로 설치

```
/plugin install crong@github
```

## 사용

Claude Code 대화에서 Skill 트리거 키워드 사용 또는 Skill 직접 호출:

```
/crong:deploy-android-wifi
/crong:security-audit
/crong:korean-translation-verify
/crong:openwrt-initd
/crong:hot-game-deals-n-news
/crong:exchange-rate-tracker
```

## 업그레이드

```bash
claude plugin update crong@github
```

## 제거

```bash
claude plugin uninstall crong@github
```

## Skill 개발

### 새 Skill 추가

1. `skills/<skill-name>/SKILL.md` 생성
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

## 프로젝트 구조

```
.
├── .claude-plugin/
│   ├── plugin.json           # 플러그인 매니페스트
│   └── marketplace.json      # 마켓플레이스 등록 정보
├── skills/
│   ├── deploy-android-wifi/
│   │   └── SKILL.md
│   ├── security-audit/
│   │   ├── SKILL.md
│   │   └── references/
│   ├── korean-translation-verify/
│   │   ├── SKILL.md
│   │   ├── scripts/
│   │   └── pyproject.toml
│   ├── openwrt-initd/
│   │   └── SKILL.md
│   ├── hot-game-deals-n-news/
│   │   ├── SKILL.md
│   │   └── references/
│   └── exchange-rate-tracker/
│       ├── SKILL.md
│       ├── scripts/
│       └── references/
├── CLAUDE.md
└── README.md
```
