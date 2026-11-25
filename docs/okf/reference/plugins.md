# 플러그인 카탈로그

## 플러그인 메타 & 버전 정책

- **마켓플레이스 저장소**: `deuxksy/ai-agent-skill`
- **플러그인 버전**: 플러그인별 독립 SemVer (v2.0.0 epoch, 후발 신규 플러그인 `kisa`·`email`은 1.x로 시작) — `.claude-plugin/marketplace.json`이 Source of Truth

## 플러그인 목록

| Plugin | 설명 | Version | 포함 스킬 | 설치 명령어 |
| :--- | :--- | :--- | :--- | :--- |
| [security](../../../plugins/security/README.md) | SAST, 시스템 패키지 CVE 및 백도어 감사 절차 | 2.0.0 | `code-audit`, `system-audit`, `backdoor-investigation`, `backdoor-remediation` | `security@zzizily` |
| [infra](../../../plugins/infra/README.md) | 머신 초기 설정, OS 패키지 관리/업그레이드, AI Agent lifecycle, Proxmox VM 프로비저닝 | 2.4.1 | `setup`, `packages`, `agents`, `lsp`, `proxmox-vm-create`, `openwrt-initd`, `acl-owner-reset` | `infra@zzizily` |
| [trackers](../../../plugins/trackers/README.md) | 일정 동기화, 환율 추적 및 게임 핫딜 알림 | 2.1.0 | `calendar-sync`, `exchange-rate-tracker`, `hot-game-deals-n-news`, `notion-sprint-sync` | `trackers@zzizily` |
| [sessions](../../../plugins/sessions/README.md) | 세션 작업 저장(handoff) 및 복원(resume) 절차 | 2.0.0 | `handoff`, `resume` | `sessions@zzizily` |
| [l10n](../../../plugins/l10n/README.md) | 이미지 4K 최적화, 한국어 번역 검증 및 딥리서치 기획 | 2.0.0 | `optimize-images-4k`, `korean-translation-verify`, `product-planning-dr-pipeline` | `l10n@zzizily` |
| [git](../../../plugins/git/README.md) | Git 커밋, PR 생성, 태그 릴리스, 스태일 브랜치 정리 및 `.gitignore` 관리 절차 | 2.2.0 | `commit`, `commit-push`, `commit-push-pr`, `clean-gone`, `tag-release`, `gitignore` | `git@zzizily` |
| [rules](../../../plugins/rules/README.md) | 에이전트 지침 파일 구조 감사 및 세션 러닝 반영 | 2.0.0 | `agents-md-management`, `revise-agents-md` | `rules@zzizily` |
| [docs](../../../plugins/docs/README.md) | README 요약 감사, 문서 재구성(분리/합병/이동), Diátaxis 인덱싱 및 고아 문서 관리 | 2.1.0 | `docs-md-management`, `docs-restructure`, `revise-readme-md` | `docs@zzizily` |
| [review](../../../plugins/review/README.md) | spec/plan 문서 및 코드 변경 런타임 교차 검증 | 2.1.0 | `verify` | `review@zzizily` |
| [dev](../../../plugins/dev/README.md) | Android WiFi ADB 빌드 배포 및 오픈소스 라이선스 조사 | 2.1.0 | `deploy-android-wifi`, `license`, `update-openapi`, `sqlite-d1-sync` | `dev@zzizily` |
| [jmeter](../../../plugins/jmeter/README.md) | JMeter 스트레스 테스트: JMX 린트, 원격 배포·기동, 실행·knee 탐색, 수집·리포트 | 2.0.0 | `lint`, `deploy`, `run`, `knee`, `collect`, `report`, `bottleneck` | `jmeter@zzizily` |
| [kisa](../../../plugins/kisa/README.md) | KISA·KECO 체크리스트 기반 서버·웹·AI·DB 취약점 점검 절차 | 1.2.1 | `linux`, `web`, `ai`, `db` | `kisa@zzizily` |
| [email](../../../plugins/email/README.md) | hiworks 메일 수신·조회·승인 발송 절차 | 1.2.1 | `hiworks` | `email@zzizily` |
