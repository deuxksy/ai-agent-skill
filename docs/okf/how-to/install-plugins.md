# 설치 및 사용 가이드 (Quick Start)

런타임 환경(`claude`, `code`, `agy`)별 플러그인 및 스킬 설치 방법입니다.

## 1. Claude Mode (`claude`)

Claude Code CLI 환경에서 마켓플레이스를 추가하고 필요한 도메인 플러그인을 설치합니다.

```bash
# 마켓플레이스 등록
claude plugin marketplace add deuxksy/ai-agent-skill

# 필요한 플러그인만 선택해 설치
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
claude plugin install jmeter@zzizily
claude plugin install kisa@zzizily
claude plugin install email@zzizily
```

**사용 방법:**
```bash
/security:code-audit                       # 코드 보안 감사 스킬 호출
/infra:setup                               # 초기 설정 스킬 호출
/review:verify                             # 런타임 교차검증 스킬 호출
/sessions:handoff                          # 세션 저장 스킬 호출
/git:commit                                # git 스킬 호출
```

## 2. Code Mode (`code` / Codex / Cursor / VS Code)

Codex CLI 및 VS Code / Cursor AI 환경에서 마켓플레이스를 등록하거나 스킬 디렉토리를 연동합니다.

### Marketplace 설치 (Codex)
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
codex plugin add jmeter@zzizily
codex plugin add kisa@zzizily
codex plugin add email@zzizily
```

## 3. AGY Mode (`agy` / Antigravity)

Antigravity CLI(`agy`) 환경에서 설치합니다. URL subpath 설치는 미지원이므로 로컬 디렉토리 설치 또는 타 런타임 import를 사용합니다.

```bash
# 1) 저장소 클론 후 로컬 디렉토리로 설치 (필요한 도메인만 선택 설치 가능)
git clone https://github.com/deuxksy/ai-agent-skill
agy plugin install ./ai-agent-skill/plugins/security
agy plugin install ./ai-agent-skill/plugins/infra
agy plugin install ./ai-agent-skill/plugins/trackers
agy plugin install ./ai-agent-skill/plugins/sessions
agy plugin install ./ai-agent-skill/plugins/l10n
agy plugin install ./ai-agent-skill/plugins/git
agy plugin install ./ai-agent-skill/plugins/rules
agy plugin install ./ai-agent-skill/plugins/docs
agy plugin install ./ai-agent-skill/plugins/review
agy plugin install ./ai-agent-skill/plugins/dev
agy plugin install ./ai-agent-skill/plugins/jmeter
agy plugin install ./ai-agent-skill/plugins/kisa
agy plugin install ./ai-agent-skill/plugins/email

# 2) 또는 claude/gemini에 이미 설치된 플러그인 import
agy plugin import claude

# 설치된 플러그인 확인
agy plugin list
```
