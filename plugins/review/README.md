# review Plugin

spec/plan 문서 및 코드 변경을 멀티 에이전트 런타임(Codex, Antigravity, Tailscale Aperture)으로 격리 snapshot에서 교차 검증하는 리뷰 도메인 플러그인입니다.

## 🛠️ 포함 스킬 (1)

- **`verify`**: 런타임 교차 검증 (3단계 티어, Codex+Antigravity 기본 2-Way + Aperture(qwen3.8-max) 3-Way 옵션, 격리 reviewer fanout)

## 🚀 설치 방법

```bash
claude plugin install review@zzizily
```
