# sessions Plugin

대화 세션 작업 상태 구조화 저장(`handoff`) 및 새 세션에서의 태스크 자동 복원(`resume`) 스킬을 제공하는 세션 워크플로우 도메인 플러그인입니다.

## 🛠️ 포함 스킬 (2)

- **`handoff`**: 컨텍스트 압축 또는 세션 종료 전 현재 작업을 `.zzizily/handoff/`에 안전 저장
- **`resume`**: 최신 `handoff` 상태를 읽어와 새 세션에서 진행 상황 및 다음 액션 자동 복원

## 🚀 설치 방법

```bash
claude plugin install sessions@zzizily
```
