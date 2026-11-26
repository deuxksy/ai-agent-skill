# sessions Plugin

대화 세션 작업 상태 구조화 저장(`handoff`) 및 새 세션에서의 태스크 이어받기(`pickup`) 스킬을 제공하는 세션 워크플로우 도메인 플러그인입니다.

## 🛠 포함 스킬

- **`handoff`**: 컨텍스트 압축 또는 세션 종료 전 현재 작업을 `~/.local/state/handoff/<project>/`에 안전 저장
- **`pickup`**: 최신 `handoff` 상태를 읽어와 새 세션에서 진행 상황 및 다음 액션 이어받기

## 🚀 설치 방법

```bash
claude plugin install sessions@zzizily
```
