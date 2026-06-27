# Product Roadmap

## Roadmap Rules

- 단계는 기술 작업 목록이 아니라 검증 가능한 사용자 결과로 정의한다.
- 현재 단계의 완료 조건을 충족하기 전 다음 단계 범위를 구현하지 않는다.
- MVP 밖 기능은 `Later` 또는 `Excluded`에만 둔다.
- 불확실한 기술 결정은 구현 단계가 아니라 시간 제한이 있는 Spike로 정의한다.
- 제품 복잡도에 따라 Phase를 추가하거나 통합하되 각 Phase에 Outcome과 Exit
  Criteria를 유지한다.
- 일정 정보가 입력으로 제공된 경우에만 목표 기간을 기록하고, 추정 일정을 사실처럼
  만들지 않는다.

## Phase 0: Foundations

### Foundation Outcome

[개발과 검증을 시작할 수 있는 최소 기반]

### Deliverables

- [저장소 및 개발 환경 기반]
- [공통 UI 또는 테스트 기반]
- [필수 기술 Spike]

### Foundation Exit Criteria

- [검증 가능한 완료 조건]

## Phase 1: Core Journey

### Core Journey Outcome

[첫 번째 핵심 사용자 여정을 끝까지 완료]

### Core Journey Included

| Item | 연결 Feature/Journey | 연결 Screen | 완료 조건 | 의존성 |
| :--- | :--- | :--- | :--- | :--- |
| [작업 결과] | [F-ID/J-ID] | [S-ID] | [조건] | [의존성] |

### Core Journey Exit Criteria

- [핵심 여정 완료 기준]
- [필수 테스트 또는 smoke 기준]

## Phase 2: MVP Completion

### MVP Completion Outcome

[남은 MVP 여정과 운영 필수 상태 완성]

### MVP Completion Included

| Item | 연결 Feature/Journey | 연결 Screen | 완료 조건 | 의존성 |
| :--- | :--- | :--- | :--- | :--- |
| [작업 결과] | [F-ID/J-ID] | [S-ID] | [조건] | [의존성] |

### MVP Completion Exit Criteria

- 모든 MVP 기능이 수용 기준을 충족한다.
- 로딩, 빈 상태, 오류, 권한 제한 상태가 검증된다.
- 필수 lint, typecheck, test, build 검증이 통과한다.

## Spikes

| Spike ID | 질문 | 최소 실험 | 성공 기준 | 시간 제한 | 다음 결정 |
| :--- | :--- | :--- | :--- | :--- | :--- |
| T-[번호] | [질문] | [실험] | [기준] | [기간] | [결정] |

## Later

- [1차 고도화 기능과 시작 조건]
- [후순위 기능과 재검토 조건]

## Excluded

- [제외 기능과 이유]

## Risks

| 위험 | 영향 | 조기 신호 | 완화 또는 검증 |
| :--- | :--- | :--- | :--- |
| [위험] | [영향] | [신호] | [대응] |
