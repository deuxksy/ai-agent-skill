# CLAUDE.md

@./.ai/RULES.md

## 프로젝트 개요

**zzizily** — 11개 독립 도메인 플러그인을 통합 제공하는 개인 자동화 AI Agent Skill 마켓플레이스.

## 분류 원칙

신규 스킬은 아래 기준으로 카테고리를 배치한다. 충돌 시 위 번호가 우선.

1. **보안 목적** (탐지/대응) → `security` (KISA 체크리스트 점검은 `kisa`)
2. **호스트/OS/VM 상태 변경** → `infra`
3. **주기적 데이터 수집/동기화** → `trackers`
4. **교차 검증/리뷰** → `review`
5. **빌드/배포/개발 도구** → `dev`
6. **파일/문서/번역 콘텐츠 처리** → `l10n`
7. **세션/작업 보존** → `sessions`
8. **부하 테스트/JMeter 실행** → `jmeter`

## 버전 관리

모든 플러그인 매니페스트·카탈로그 표의 버전은 `.claude-plugin/marketplace.json`을 Source of Truth로 동기화한다. 상세 정책은 `.ai/RULES.md` 참조.
