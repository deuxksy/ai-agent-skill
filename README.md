# AI-AGENT-SKILL

zzizily는 Claude Code, Codex, Antigravity(Gemini) 등 멀티 Agent 런타임을 지원하는 개인 자동화 AI Agent Skill 플러그인 모음입니다. 보안 감사, 인프라 프로비저닝, 일상 자동화, 런타임 교차 검증부터 Git 워크플로우 및 문서 관리까지 26개 전체 스킬을 10개 독립 도메인 플러그인으로 모듈화하여 제공합니다.

## 문서 체계 및 Diátaxis 인덱스

본 프로젝트의 모든 사용 목적 및 형태에 따른 주요 문서는 Diátaxis 프레임워크 기반으로 체계적으로 관리됩니다.

| 영역 (Quadrant) | 대상 문서 | 설명 |
| :--- | :--- | :--- |
| **Tutorials** (학습 / 입문) | [Quick Start](#설치-및-사용-가이드-quick-start) | 런타임별(`claude`, `code`, `agy`) 빠른 설치 및 시작 가이드 |
| **How-To Guides** (실무 / 절차) | [security](./plugins/security/README.md) | SAST, 시스템 패키지 CVE 및 백도어 감사 절차 |
| | [infra](./plugins/infra/README.md) | 머신 초기 설정, OS 패키지 관리/업그레이드, AI Agent lifecycle, Proxmox VM 프로비저닝 |
| | [trackers](./plugins/trackers/README.md) | 일정 동기화, 환율 추적 및 게임 핫딜 알림 |
| | [sessions](./plugins/sessions/README.md) | 세션 작업 저장(handoff) 및 복원(resume) 절차 |
| | [l10n](./plugins/l10n/README.md) | 이미지 4K 최적화, 한국어 번역 검증 및 딥리서치 기획 |
| | [git](./plugins/git/README.md) | Git 커밋, PR 생성 및 스태일 브랜치 정리 절차 |
| | [rules](./plugins/rules/README.md) | 에이전트 지침 파일 구조 감사 및 세션 러닝 반영 |
| | [docs](./plugins/docs/README.md) | README 요약 감사, docs/ 프로젝트 문서, Diátaxis 인덱싱 및 고아 문서 관리 |
| | [review](./plugins/review/README.md) | spec/plan 문서 및 코드 변경 런타임 교차 검증 |
| | [dev](./plugins/dev/README.md) | Android WiFi ADB 빌드 및 배포 |
| **Reference** (참조 / 규격) | [docs/README.md](./docs/README.md) | 서브 문서 디렉토리 역할 및 체계 정의 |
| | [docs/okf/README.md](./docs/okf/README.md) | OKF(Open Knowledge Framework) 명세 허브 및 작성 가이드 |
| | [CLAUDE.md](./CLAUDE.md) | 프로젝트 구조, 분류 원칙, SKILL.md 규격 및 패키지 관리 명세 |
| | [agents/verify.md](./agents/verify.md) | Claude Code runner adapter 및 교차 검증 라우팅 명세 |
| **Explanation** (원리 / 설계) | [분류 원칙](./CLAUDE.md#분류-원칙) | 스킬 분류 배치 원칙 및 아키텍처 배경 설명 |

## 설치 및 사용 가이드 (Quick Start)

런타임 환경(`claude`, `code`, `agy`)별 플러그인 및 스킬 설치 방법입니다.

### 1. Claude Mode (`claude`)

Claude Code CLI 환경에서 마켓플레이스를 추가하고 필요한 도메인 플러그인을 설치합니다.

```bash
# 마켓플레이스 등록
claude plugin marketplace add deuxksy/ai-agent-skill

# 10개 독립 도메인 플러그인 설치 (필요한 도메인만 선택 설치 가능)
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
```

**사용 방법:**
```bash
/security:code-audit                       # 코드 보안 감사 스킬 호출
/infra:setup                               # 초기 설정 스킬 호출
/review:verify                             # 런타임 교차검증 스킬 호출
/sessions:handoff                          # 세션 저장 스킬 호출
/git:commit                                # git 스킬 호출
```

### 2. Code Mode (`code` / Codex / Cursor / VS Code)

Codex CLI 및 VS Code / Cursor AI 환경에서 마켓플레이스를 등록하거나 스킬 디렉토리를 연동합니다.

#### Marketplace 설치 (Codex)
```bash
# 마켓플레이스 등록
codex plugin marketplace add deuxksy/ai-agent-skill

# 원하는 독립 플러그인 설치
codex plugin add security@zzizily
codex plugin add infra@zzizily
codex plugin add trackers@zzizily
codex plugin add sessions@zzizily
codex plugin add l10n@zzizily
codex plugin add git@zzizily
codex plugin add rules@zzizily
codex plugin add docs@zzizily
codex plugin add review@zzizily
codex plugin add dev@zzizily
```

### 3. AGY Mode (`agy` / Antigravity)

Antigravity CLI(`agy`) 환경에서 `agy plugin` CLI 명령어 또는 스킬 경로 연동으로 설치합니다.

```bash
# 원하는 독립 도메인 플러그인 설치
agy plugin install https://github.com/deuxksy/ai-agent-skill/plugins/security
agy plugin install https://github.com/deuxksy/ai-agent-skill/plugins/infra
agy plugin install https://github.com/deuxksy/ai-agent-skill/plugins/trackers
agy plugin install https://github.com/deuxksy/ai-agent-skill/plugins/sessions
agy plugin install https://github.com/deuxksy/ai-agent-skill/plugins/l10n
agy plugin install https://github.com/deuxksy/ai-agent-skill/plugins/git
agy plugin install https://github.com/deuxksy/ai-agent-skill/plugins/rules
agy plugin install https://github.com/deuxksy/ai-agent-skill/plugins/docs
agy plugin install https://github.com/deuxksy/ai-agent-skill/plugins/review
agy plugin install https://github.com/deuxksy/ai-agent-skill/plugins/dev

# 설치된 플러그인 확인
agy plugin list
```

## 플러그인 메타 & 버전 정책

- **마켓플레이스 저장소**: `deuxksy/ai-agent-skill`
- **통합 단일 버전**: `1.11.0` (모든 10개 독립 플러그인 매니페스트 및 마켓플레이스 동기화)

## 독립 도메인 플러그인 카탈로그 (10)

| Plugin | Version | 포함 스킬 | 설치 명령어 |
| :--- | :--- | :--- | :--- |
| `security` | 1.11.0 | `code-audit`, `system-audit`, `backdoor-investigation`, `backdoor-remediation` | `security@zzizily` |
| `infra` | 1.11.0 | `setup`, `packages`, `agents`, `proxmox-vm-create`, `openwrt-initd` | `infra@zzizily` |
| `trackers` | 1.11.0 | `calendar-sync`, `exchange-rate-tracker`, `hot-game-deals-n-news` | `trackers@zzizily` |
| `sessions` | 1.11.0 | `handoff`, `resume` | `sessions@zzizily` |
| `l10n` | 1.11.0 | `optimize-images-4k`, `korean-translation-verify`, `product-planning-dr-pipeline` | `l10n@zzizily` |
| `git` | 1.11.0 | `commit`, `commit-push-pr`, `clean-gone` | `git@zzizily` |
| `rules` | 1.11.0 | `agents-md-management`, `revise-agents-md` | `rules@zzizily` |
| `docs` | 1.11.0 | `docs-md-management`, `revise-readme-md` | `docs@zzizily` |
| `review` | 1.11.0 | `verify` | `review@zzizily` |
| `dev` | 1.11.0 | `deploy-android-wifi` | `dev@zzizily` |

## 상세 문서

구조 트리, 분류 원칙, SKILL.md 규격, 개발 워크플로우, 환경별 패키지 관리는 [CLAUDE.md](./CLAUDE.md) 참조.

## License

MIT License © Crong (kyolim)
