# Notion Sprint Sync Skill Specification

## Goal

로컬 Sprint 계획의 Epic → Story → Task 관계를 Notion `작업` Database에 안전하게 동기화하는 재사용 가능한 Skill을 추가한다.

## Location

```text
plugins/trackers-automation/skills/notion-sprint-sync/
├─ SKILL.md
└─ references/
   └─ mapping-contract.md
```

새 Plugin은 만들지 않고 기존 `trackers-automation` Plugin에 Skill 하나를 추가한다.

## Inputs

- 로컬 `planning/sprint-assignments.json`
- 대상 Sprint ID (`S01`, `S03` 등)
- Notion `작업` Database URL
- Notion `스프린트` Database 또는 대상 Sprint Page URL
- 수정할 속성과 값
  - `상위 작업`: 로컬 Task의 `story_id`에서 계산
  - `우선순위`: 명시값 또는 `S01=P0`, `S02=P1`, `S03=P2` 규칙
  - `스프린트`: 반드시 사용자가 지정한 Notion Sprint Page

`스프린트` Relation은 Sprint ID나 날짜로 암묵적으로 추론하지 않는다.

## Data Flow

1. `sprint-assignments.json`에서 대상 Sprint의 Story ID 목록을 읽는다.
2. 각 Story `README.md`에서 `epic_id`, `story_id`, `task_ids`, `target_sprint`를 읽는다.
3. 각 Task Markdown에서 `task_id`, `story_id`, `target_sprint`를 교차검증한다.
4. Notion `작업 이름`의 `TASK-\d{4}` 또는 `STORY-[A-Z]+-\d{3}` prefix로 Page를 식별한다.
5. Page ID, 분류, 기존 Relation과 대상 값을 포함한 Dry-run Manifest를 만든다.
6. 모든 사전조건이 통과한 경우 사용자가 허용한 속성만 갱신한다.
7. 전체 대상을 재조회해 요청값과 보존값을 검증한다.

## Write Allowlist

Skill이 수정할 수 있는 속성은 다음 세 개뿐이다.

```text
상위 작업
우선순위
스프린트
```

한 실행에서 사용자가 요청하지 않은 allowlist 속성은 payload에 포함하지 않는다.

다음 작업은 금지한다.

- Page 생성 또는 삭제
- Page 본문 수정
- 속성 schema 수정 또는 이름 변경
- `작업 이름`, `분류`, `상태`, `담당자`, `프로젝트`, 날짜 수정
- 기존 Relation 삭제
- ID가 중복되거나 분류가 잘못된 Page 수정

## Preconditions

쓰기 전에 전체 대상에 대해 다음 조건을 검증한다.

1. 로컬 Story와 Task metadata가 대상 Sprint와 일치한다.
2. Notion Task/Story prefix가 각각 정확히 한 Page와 일치한다.
3. Task Page의 `분류`에 `태스크`가 포함된다.
4. Story Page의 `분류`에 `스토리`가 포함된다.
5. `상위 작업` 대상은 동일 `작업` Database의 Story Page다.
6. `스프린트` 대상은 해당 Relation이 참조하는 `스프린트` Database Page다.
7. Select 값이 Notion schema의 허용값에 포함된다.
8. 기존 값이 요청값과 충돌하면 자동으로 덮어쓰지 않고 충돌로 보고한다.

하나라도 실패하면 쓰기를 0건으로 중단한다.

## Update Policy

- 기본 동작은 Dry-run이다.
- 사용자가 동기화 또는 적용을 명시하면 Write 단계로 진행한다.
- 이미 요청값과 같은 속성은 수정하지 않는다.
- 빈 값만 채우는 것이 기본이다.
- 기존 값 교체는 사용자가 교체 대상과 새 값을 명시한 경우에만 허용한다.
- 여러 Page를 갱신하더라도 Page별 결과를 수집하고 실패 대상을 숨기지 않는다.

## Verification

갱신 후 모든 대상 Page를 다시 읽어 다음을 확인한다.

1. 요청한 속성이 정확히 요청값과 일치한다.
2. Relation은 예상 Page URL 하나만 포함한다.
3. 요청하지 않은 `상위 작업` Relation이 변경되지 않았다.
4. Page 본문이 변경되지 않았다.
5. 갱신 오류, 불일치, 부수 변경 건수를 별도로 보고한다.

## Output Contract

Dry-run과 적용 결과는 다음 집계를 포함한다.

```text
Sprint
대상 Story 수
대상 Task 수
일치/누락/중복 Page 수
기존 정상/미설정/충돌 속성 수
적용 요청/성공/실패 수
재검증 성공/불일치/부수 변경 수
```

오류가 있으면 Page ID, 로컬 ID, 실패 단계와 실제 값을 함께 표시한다.

## Acceptance Criteria

1. Skill metadata가 Notion Sprint·Story·Task 동기화 요청을 명확히 trigger한다.
2. Task/Story prefix 기반 Page 식별과 uniqueness 검증을 수행한다.
3. Epic → Story → Task 관계를 로컬 metadata에서 계산한다.
4. `상위 작업`, `우선순위`, `스프린트`만 write allowlist로 사용한다.
5. `스프린트` Relation 대상은 반드시 명시 입력을 요구한다.
6. 사전검증 실패 시 Notion 쓰기를 수행하지 않는다.
7. 적용 후 요청값과 보존값을 전체 재조회한다.
8. 생성·삭제·본문 수정과 비허용 속성 변경을 금지한다.
9. Skill folder가 repository validation을 통과한다.

