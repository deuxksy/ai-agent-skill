# zzizily

개인 자동화 AI Agent Skill 플러그인. 보안 감사, 인프라 프로비저닝, 일상 자동화, AI Agent 검증까지 19개 스킬을 한 번에.

## Quick Start

```bash
# 설치
claude plugin marketplace add deuxksy/ai-agent-skill
claude plugin install deuxksy@zzizily

# 사용
/zzizily:<skill-name>

# 스킬 목록 확인
ls skills/
```

## 플러그인 메타

| 항목 | 값 |
| :--- | :--- |
| Plugin name | `zzizily` (plugin.json) |
| Marketplace plugin name | `deuxksy` (marketplace.json) |
| 호출 prefix | `/zzizily:<skill-name>` |
| GitHub repo | `deuxksy/ai-agent-skill` |
| 버전 | 1.8.1 |

## 스킬 카탈로그 (19)

기능 도메인별 그룹핑. 각 스킬은 `skills/<skill-name>/SKILL.md`에 정의.

### 보안 · 감사 (Security & Audit)

| 스킬 | 설명 |
| :--- | :--- |
| `code-audit` | 정적 코드 보안 점검 (SAST/CWE/OWASP) |
| `system-audit` | 시스템 패키지 보안 감사 (CVE/CVSS/KEV) |
| `backdoor-investigation` | Linux 백도어 포렌식 진단 (read-only) |
| `backdoor-remediation` | 백도어 제거·복구 (파괴적, 승인 필요) |

### 인프라 · 프로비저닝 (Infra & Provisioning)

| 스킬 | 설명 |
| :--- | :--- |
| `setup` | 초기 설정 (brew/stow/sops/Tailscale) |
| `system-upgrade` | OS 패키지 업그레이드 (brew/apt/dnf/nix) |
| `proxmox-vm-create` | Proxmox VE VM 프로비저닝 (qm→pvesh→REST) |
| `openwrt-initd` | OpenWrt init.d 백그라운드 서비스 설치 |

### 자동화 · 트래커 (Automation & Trackers)

| 스킬 | 설명 |
| :--- | :--- |
| `calendar-sync` | Notion/GCal → Hermes 일정 동기화 |
| `exchange-rate-tracker` | 환율 추적 (USD/KRW, USD/VND) |
| `hot-game-deals-n-news` | 게임 할인/무료/뉴스 트래커 |

### AI Agent · 배포 (Agents & Deploy)

| 스킬 | 설명 |
| :--- | :--- |
| `agents` | AI Agent/MCP/LSP 설치·업그레이드 자동화 |
| `verify` | Codex+Antigravity 2-Way 교차검증 (격리 snapshot) |
| `deploy-android-wifi` | WiFi ADB React Native 배포 자동화 |

### 워크플로우 · 세션 (Workflow & Session)

| 스킬 | 설명 |
| :--- | :--- |
| `handoff` | 현재 세션 작업을 구조화 저장 (`/clear` 전 수동) |
| `resume` | 이전 handoff 읽어 task preview → 승인 → TaskCreate 복원 |

### 콘텐츠 · 로컬라이제이션 (Content & L10n)

| 스킬 | 설명 |
| :--- | :--- |
| `optimize-images-4k` | 4K 이미지 최적화 (ImageMagick) |
| `korean-translation-verify` | 한국어 번역 품질 검증 |
| `product-planning-dr-pipeline` | 제품 기획 Deep Research 파이프라인 |

## 상세 문서

구조 트리, 분류 원칙, SKILL.md 규격, 개발 워크플로우, 환경별 패키지 관리는 [CLAUDE.md](./CLAUDE.md) 참조.
