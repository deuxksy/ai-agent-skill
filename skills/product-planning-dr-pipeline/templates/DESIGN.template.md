# Product Design System

이 문서는 [제품명] 전용 UI 구현 규칙이다. 외부 브랜드의 디자인 문서를 복제하지
않고, 제품의 사용자, 작업 밀도, 핵심 흐름에 맞게 재해석한다.

모든 섹션은 제품에 해당하지 않으면 삭제하지 말고 `해당 없음`과 이유를 기록한다.

## Visual Theme

- Product character: [예: 정밀함, 통제감, 빠른 탐색]
- Interface tone: [예: 작업 중심, 낮은 장식성, 높은 정보 명확성]
- Density: [compact/comfortable/spacious 및 적용 기준]
- Motion principle: [모션 사용 목적과 제한]

## Color System

| Token | 역할 | 사용 규칙 |
| :--- | :--- | :--- |
| `color-bg-*` | 배경 계층 | [규칙] |
| `color-text-*` | 텍스트 계층 | [규칙] |
| `color-accent-*` | 핵심 행동 | [규칙] |
| `color-status-*` | 성공/경고/오류/정보 | [규칙] |

- 색상만으로 상태를 전달하지 않는다.
- 대비 기준: [WCAG 목표]
- 다크 모드: [지원 여부와 규칙]

## Typography

| 역할 | 스타일 | 사용 규칙 |
| :--- | :--- | :--- |
| Display/Heading | [크기/굵기] | [규칙] |
| Body | [크기/행간] | [규칙] |
| Label/Meta | [크기/굵기] | [규칙] |
| Code/Data | [고정폭 여부] | [규칙] |

## Layout

- App shell: [탐색, 헤더, 콘텐츠 구조]
- Grid: [열, 최대 폭, 간격]
- Spacing scale: [토큰 또는 기준]
- Responsive behavior: [주요 breakpoint 행동]
- Information hierarchy: [우선순위 표현 규칙]

## Components

- Buttons: [주요/보조/위험 동작 규칙]
- Navigation: [메뉴, 탭, breadcrumb 규칙]
- Cards/panels: [사용 조건과 금지 조건]
- Dialogs/drawers: [선택 기준]
- Feedback: [toast, inline, banner 사용 기준]
- Empty/loading/error states: [공통 패턴]

## Tables

- 사용 조건: [테이블이 필요한 데이터 형태]
- 정렬, 필터, 검색, 페이지네이션 규칙
- 행 선택 및 일괄 동작 규칙
- 긴 값, 상태, 오류 표현 규칙
- 모바일 또는 좁은 화면 대응

## Forms

- 라벨, 도움말, 필수 표시 규칙
- 검증 시점과 오류 메시지 규칙
- 저장, 자동 저장, 취소, 이탈 경고 규칙
- 긴 폼의 섹션 및 진행 상태 규칙
- 접근성과 키보드 사용 규칙

## Workflow Canvas

- 적용 여부: [필요/해당 없음]
- 노드, 연결선, 선택, 편집 상태
- 확대/축소, 미니맵, 탐색 규칙
- 유효하지 않은 연결과 오류 표현
- 캔버스와 상세 패널의 역할 분리

## Trace UI

- 적용 여부: [필요/해당 없음]
- 실행 상태, 시간, 입력/출력, 오류의 정보 계층
- 목록, 타임라인, 상세 패널의 관계
- 민감 정보 마스킹 규칙
- 실시간 갱신과 오래된 상태 표시

## Do / Don't

### Do

- 핵심 작업과 현재 상태를 첫 화면에서 명확히 보이게 한다.
- 반복 작업의 위치와 행동을 일관되게 유지한다.
- 로딩, 빈 상태, 오류, 권한 제한 상태를 설계한다.
- 복잡한 데이터와 흐름에 점진적 공개를 사용한다.

### Don't

- 외부 브랜드의 색상, 컴포넌트, 문구를 그대로 복제하지 않는다.
- 장식 효과로 정보 계층을 대신하지 않는다.
- 모든 기능을 대시보드 첫 화면에 노출하지 않는다.
- 색상만으로 중요도나 오류를 전달하지 않는다.

## AI Coding Agent Prompt Guide

UI 구현을 요청할 때 다음 컨텍스트를 포함한다.

```text
Implement [Screen ID / component] for [product outcome].
Follow this DESIGN.md, especially [relevant sections].
Preserve the MVP boundary from CONTEXT.md.
Required states: [default/loading/empty/error/permission].
Required interactions: [actions and flow].
Validation: [visual, accessibility, test, responsive checks].
Do not introduce: [out-of-scope features or new visual language].
```

Agent는 새 시각 언어를 임의로 만들지 않고 이 문서와 기존 구현을 우선한다. 규칙이
부족하면 가장 작은 일관된 확장을 제안하고 검증한다.
