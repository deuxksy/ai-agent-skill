# zzizily

zzizily는 Claude Code, Codex, Antigravity(Gemini) 등 멀티 Agent 런타임을 지원하는 개인 자동화 AI Agent Skill 플러그인 모음입니다. 보안 감사, 인프라 프로비저닝, 일상 자동화, 런타임 교차 검증부터 Git 워크플로우 및 문서 관리까지 26개 전체 스킬을 9개 독립 도메인 플러그인으로 모듈화하여 제공합니다.

## 문서 체계 및 Diátaxis 인덱스

본 프로젝트의 모든 사용 목적 및 형태에 따른 주요 문서는 Diátaxis 프레임워크 기반으로 체계적으로 관리됩니다.

| 영역 (Quadrant) | 대상 문서 | 설명 |
| :--- | :--- | :--- |
| **Tutorials** (학습 / 입문) | [Quick Start](#설치-및-사용-가이드-quick-start) | 런타임별(`claude`, `code`, `agy`) 빠른 설치 및 시작 가이드 |
| **How-To Guides** (실무 / 절차) | [security-audit](./plugins/security-audit/README.md) | SAST, 시스템 패키지 CVE 및 백도어 감사 절차 |
| | [infra-provisioning](./plugins/infra-provisioning/README.md) | 머신 초기 설정, OS 업그레이드, Proxmox VM 프로비저닝 |
| | [trackers-automation](./plugins/trackers-automation/README.md) | 일정 동기화, 환율 추적 및 게임 핫딜 알림 |
| | [agent-dev-deploy](./plugins/agent-dev-deploy/README.md) | AI Agent 설치, 교차 검증 및 Android WiFi 배포 |
| | [session-workflow](./plugins/session-workflow/README.md) | 세션 작업 저장(handoff) 및 복원(resume) 절차 |
| | [content-l10n](./plugins/content-l10n/README.md) | 이미지 4K 최적화, 한국어 번역 검증 및 딥리서치 기획 |
| | [commit-commands](./plugins/commit-commands/README.md) | Git 커밋, PR 생성 및 스태일 브랜치 정리 절차 |
| | [agents-md-management](./plugins/agents-md-management/README.md) | 에이전트 지침 파일 구조 감사 및 세션 러닝 반영 |
| | [readme-md-management](./plugins/readme-md-management/README.md) | README 요약 감사, Diátaxis 인덱싱 및 고아 문서 관리 |
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

# 9개 독립 도메인 플러그인 설치 (필요한 도메인만 선택 설치 가능)
claude plugin install security-audit@zzizily
claude plugin install infra-provisioning@zzizily
claude plugin install trackers-automation@zzizily
claude plugin install agent-dev-deploy@zzizily
claude plugin install session-workflow@zzizily
claude plugin install content-l10n@zzizily
claude plugin install commit-commands@zzizily
claude plugin install agents-md-management@zzizily
claude plugin install readme-md-management@zzizily
```

**사용 방법:**
```bash
/security-audit:code-audit                 # 코드 보안 감사 스킬 호출
/infra-provisioning:setup                  # 초기 설정 스킬 호출
/agent-dev-deploy:verify                   # 런타임 교차검증 스킬 호출
/session-workflow:handoff                  # 세션 저장 스킬 호출
/commit-commands:commit                    # commit-commands 스킬 호출
```

### 2. Code Mode (`code` / Codex / Cursor / VS Code)

Codex CLI 및 VS Code / Cursor AI 환경에서 마켓플레이스를 등록하거나 스킬 디렉토리를 연동합니다.

#### Marketplace 설치 (Codex)
```bash
# 마켓플레이스 등록
codex plugin marketplace add deuxksy/ai-agent-skill

# 원하는 독립 플러그인 설치
codex plugin add security-audit@zzizily
codex plugin add infra-provisioning@zzizily
codex plugin add trackers-automation@zzizily
codex plugin add agent-dev-deploy@zzizily
codex plugin add session-workflow@zzizily
codex plugin add content-l10n@zzizily
codex plugin add commit-commands@zzizily
codex plugin add agents-md-management@zzizily
codex plugin add readme-md-management@zzizily
```

### 3. AGY Mode (`agy` / Antigravity)

Antigravity CLI(`agy`) 환경에서 `agy plugin` CLI 명령어 또는 스킬 경로 연동으로 설치합니다.

```bash
# 원하는 독립 도메인 플러그인 설치
agy plugin install plugins/security-audit
agy plugin install plugins/infra-provisioning
agy plugin install plugins/trackers-automation
agy plugin install plugins/agent-dev-deploy
agy plugin install plugins/session-workflow
agy plugin install plugins/content-l10n
agy plugin install plugins/commit-commands
agy plugin install plugins/agents-md-management
agy plugin install plugins/readme-md-management

# 설치된 플러그인 확인
agy plugin list
```

## 플러그인 메타 & 버전 정책

- **마켓플레이스 저장소**: `deuxksy/ai-agent-skill`
- **통합 단일 버전**: `1.9.1` (모든 9개 독립 플러그인 매니페스트 및 마켓플레이스 동기화)

## 독립 도메인 플러그인 카탈로그 (9)

| Plugin | Version | 포함 스킬 | 설치 명령어 |
| :--- | :--- | :--- | :--- |
| `security-audit` | 1.9.1 | `code-audit`, `system-audit`, `backdoor-investigation`, `backdoor-remediation` | `security-audit@zzizily` |
| `infra-provisioning` | 1.9.1 | `setup`, `system-upgrade`, `proxmox-vm-create`, `openwrt-initd` | `infra-provisioning@zzizily` |
| `trackers-automation` | 1.9.1 | `calendar-sync`, `exchange-rate-tracker`, `hot-game-deals-n-news` | `trackers-automation@zzizily` |
| `agent-dev-deploy` | 1.9.1 | `agents`, `verify`, `deploy-android-wifi` | `agent-dev-deploy@zzizily` |
| `session-workflow` | 1.9.1 | `handoff`, `resume` | `session-workflow@zzizily` |
| `content-l10n` | 1.9.1 | `optimize-images-4k`, `korean-translation-verify`, `product-planning-dr-pipeline` | `content-l10n@zzizily` |
| `commit-commands` | 1.9.1 | `commit`, `commit-push-pr`, `clean-gone` | `commit-commands@zzizily` |
| `agents-md-management` | 1.9.1 | `agents-md-management`, `revise-agents-md` | `agents-md-management@zzizily` |
| `readme-md-management` | 1.9.1 | `readme-md-management`, `revise-readme-md` | `readme-md-management@zzizily` |

## 상세 문서

구조 트리, 분류 원칙, SKILL.md 규격, 개발 워크플로우, 환경별 패키지 관리는 [CLAUDE.md](./CLAUDE.md) 참조.
