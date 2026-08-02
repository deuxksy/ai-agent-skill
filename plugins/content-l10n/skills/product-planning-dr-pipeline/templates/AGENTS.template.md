# AGENTS.md

## Mission

[제품명]의 MVP를 제품 정의와 확정된 범위 안에서 구현한다. 이 문서는 개발 Agent의
작업 규칙이며 기획 보고서가 아니다.

## Product Definition

- Product: [한 줄 정의]
- Target users: [주요 사용자]
- Core problem: [해결할 문제]
- MVP outcome: [사용자가 완료할 수 있어야 하는 핵심 결과]

## Source of Truth

충돌 시 다음 우선순위를 사용한다.

1. 이 `AGENTS.md`의 작업 및 안전 규칙
2. `CONTEXT.md`의 제품 정의, MVP, 비목표
3. `ROADMAP.md`의 현재 단계와 완료 조건
4. `DESIGN.md`의 UI 및 상호작용 규칙
5. 저장소의 기존 코드, 테스트, 설정

충돌을 발견하면 임의로 범위를 넓히지 말고 가장 작은 일관된 해석을 사용한 뒤
미해결 항목을 기록한다.

## Scope Rules

- 구현 가능: [MVP 기능 ID 또는 범위]
- 구현 금지: [후순위/제외 항목]
- 변경 전 확인 필요: [공유 계약, 데이터 삭제, 외부 프로덕션 등]
- 기술 보류 영역: [과도하게 확정하지 않을 백엔드/인프라 영역]

## Working Rules

- 현재 로드맵 단계의 완료 조건을 먼저 확인한다.
- 기존 저장소 패턴과 유틸리티를 우선 사용한다.
- 새 의존성은 확정된 기술 결정이 있거나 명확한 필요가 있을 때만 추가한다.
- 한 번에 하나의 검증 가능한 사용자 결과를 구현한다.
- 범위 밖 요구는 `ROADMAP.md`의 후순위 또는 제외 항목으로 기록한다.
- 미정 사항을 사실로 가정하지 말고 작은 검증 작업으로 분리한다.

## Design Implementation Rules

- `DESIGN.md`의 제품 전용 규칙을 따른다.
- 모든 화면에 로딩, 빈 상태, 오류, 권한 제한 상태를 구현한다.
- 핵심 흐름과 정보 구조를 시각 장식보다 우선한다.
- 외부 브랜드 디자인을 복제하지 않는다.

## Validation

변경 범위에 맞춰 다음 검증을 실행한다.
명령은 `04-dr-merge.md`의 검증 명령 요약과 저장소 설정에서 추출한다.

```text
[format command]
[lint command]
[typecheck command]
[targeted test command]
[build or smoke command]
```

검증 명령을 알 수 없으면 저장소 설정에서 찾는다. 실행할 수 없는 검증은 이유와
대체 증거를 기록한다.

## Completion Report

완료 보고에는 다음만 포함한다.

- 구현한 사용자 결과
- 변경 파일
- 실행한 검증과 결과
- 남은 위험, 미정, 후순위
