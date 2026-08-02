# 03 Screen Design Request

## Design Brief

- Product definition: [한 줄 정의]
- Target users and roles: [사용자 및 역할]
- MVP scope input: [`02-dr-merge.md` 경로]
- Fixed MVP feature IDs: [F-ID 목록]
- Core journeys: [J-ID 목록]
- Platform constraints: [웹/모바일/데스크톱, 반응형, 접근성]

## Objective

고정된 MVP 기능과 사용자 여정을 기준으로 IA, 메뉴 구조, 화면 목록, 사용자 흐름,
화면별 요구사항을 정의한다. 고해상도 시안이나 기술 구현을 확정하지 않고, 구현에
필요한 동작과 상태를 명확히 한다.

## Design Rules

- 모든 화면을 하나 이상의 MVP 기능 또는 사용자 여정에 연결한다.
- 후순위 기능을 화면에 숨겨 넣지 않는다.
- 정상 상태뿐 아니라 빈 상태, 로딩, 오류, 권한 제한 상태를 정의한다.
- 데스크톱/모바일 차이가 중요하면 별도로 명시한다.
- 시각 스타일보다 정보 구조와 상호작용 계약을 우선한다.

## Required Output

### Information Architecture

```text
[제품]
├─ [상위 영역]
│  ├─ [하위 화면]
│  └─ [하위 화면]
└─ [상위 영역]
```

### Navigation and Menu Structure

| 영역 | 메뉴/진입점 | 대상 역할 | 연결 화면 | 표시 조건 |
| :--- | :--- | :--- | :--- | :--- |
| [영역] | [메뉴] | [역할] | S-[번호] | [조건] |

### Screen Inventory

| Screen ID | 화면명 | 목적 | 연결 기능 ID | 연결 Journey ID | 주요 역할 |
| :--- | :--- | :--- | :--- | :--- | :--- |
| S-[번호] | [화면] | [목적] | [F-ID] | [J-ID] | [역할] |

### User Flows

각 핵심 여정에 대해 다음을 기록한다.

1. 시작점
2. 화면 이동 순서
3. 사용자 결정 및 입력
4. 시스템 피드백
5. 완료 상태
6. 오류 및 복구 경로

### Screen Requirements

#### S-[번호] [화면명]

- Purpose: [목적]
- Entry points: [진입점]
- Roles/permissions: [권한]
- Primary actions: [핵심 동작]
- Information/data: [표시 및 입력 데이터]
- Components: [필수 UI 구성 요소]
- States: [기본, 빈 상태, 로딩, 오류, 권한 제한]
- Validation: [입력 및 행동 검증]
- Exit/navigation: [이동 및 완료 상태]
- Linked MVP features: [F-ID]
- Open questions: [미정 사항]

### Cross-Screen Requirements

- 전역 탐색 및 검색
- 알림 및 피드백
- 권한 및 접근 제한
- 데이터 갱신 및 저장 상태
- 접근성 및 반응형 요구사항

## Validation

- 모든 MVP 기능 ID가 화면 또는 비화면 요구사항에 연결되었는지 확인한다.
- 모든 핵심 여정에 완료 및 실패 경로가 있는지 확인한다.
- 범위 밖 화면과 기능을 별도 목록으로 이동한다.
- 기술선정 단계가 필요한 UI 능력과 제약을 마지막에 요약한다.

## Handoff to Technology Selection

- 구현 대상 화면 목록
- 복잡한 UI 및 상호작용 요구사항
- 데이터 밀도, 폼, 테이블, 캔버스, 문서 뷰어 요구사항
- 권한, 관측성, 접근성 요구사항
- 성능 또는 플랫폼 제약
- 아직 실험이 필요한 상호작용

## Expected Merge Structure

`03-dr-merge.md`는 다음 구조를 사용한다.

1. 제품 정의와 고정 MVP 기능 및 여정
2. 기준본, 보강본, 선택 근거
3. 통합 IA, 메뉴, 화면 목록
4. 확정 사용자 흐름과 화면별 요구사항
5. 범위 밖 화면, 충돌, 불확실성
6. Technology Selection에 전달할 UI 능력 및 제약 요약
