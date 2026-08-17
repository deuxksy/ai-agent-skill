---
name: notion-sprint-sync
description: Use when synchronizing a local planning/sprint-assignments.json Epic-Story-Task hierarchy to Notion 작업 pages, including dry-run mapping, duplicate detection, 상위 작업 relations, Sprint-derived 우선순위, or an explicitly selected 스프린트 relation.
---

# Notion Sprint Sync

## Overview

로컬 metadata를 source of truth로 사용해 Notion Task 속성을 안전하게 동기화한다. 기본 동작은 dry-run이며, 전체 preflight가 성공한 경우에만 사용자가 명시한 속성을 수정한다.

작업 전 [mapping-contract.md](references/mapping-contract.md)를 읽는다.

## Required inputs

- `planning/sprint-assignments.json` 경로와 대상 Sprint ID
- Notion 작업 Database URL
- 수정할 속성 목록: `상위 작업`, `우선순위`, `스프린트` 중 하나 이상
- `스프린트`를 수정한다면 정확한 Notion Sprint Page 또는 select 값

Sprint ID로 Notion `스프린트` 값을 추론하지 않는다. 과거 매핑이나 번호 규칙도 명시 입력을 대체하지 못한다.

## Workflow

### 1. Build the local manifest

1. Sprint JSON에서 대상 Story 목록을 읽는다.
2. 각 Story directory와 `README.md`를 찾아 `epic_id`, `story_id`, `task_ids`, `target_sprint`를 읽는다.
3. 각 Task Markdown의 `task_id`, `story_id`, `target_sprint`를 교차검증한다.
4. Story 목록을 Task 목록으로 전개한다. Story 수를 Task 수로 보고하지 않는다.
5. `Epic directory > Story directory > Task filename`과 metadata 관계가 다르면 중단한다.

### 2. Resolve Notion pages

1. Story는 `STORY-[A-Z]+-\d{3}`, Task는 `TASK-\d{4}` prefix로 검색한다.
2. title 전체가 아니라 정규화한 prefix를 exact match한다.
3. 각 ID가 정확히 한 Page와 대응하는지 확인한다.
4. Story Page의 `분류=스토리`, Task Page의 `분류=태스크`를 확인한다.
5. 누락, 중복, 분류 불일치가 하나라도 있으면 write를 0건으로 중단한다.

### 3. Compute requested values

- `상위 작업`: 각 Task metadata의 `story_id`에 대응하는 Notion Story Page
- `우선순위`: 사용자가 명시한 값 또는 `S01=P0`, `S02=P1`, ..., `S10=P9`
- `스프린트`: 사용자가 명시한 Notion Page/value만 사용

Notion schema에서 property type, relation target, select option을 확인한다. 기존 값이 요청값과 다르면 conflict로 보고하며, 사용자가 교체를 명시하지 않았다면 덮어쓰지 않는다.

### 4. Produce a dry-run

쓰기 전에 Sprint, Story/Task 수, Page 일치/누락/중복/분류 오류, 속성별 동일/공백/conflict, 변경 예정 `before -> after`, 쓰기 가능 여부를 보고한다.

### 5. Apply only explicit writes

사용자가 적용을 명시한 경우에만 실행한다.

1. query/search 결과 URL에서 32자리 Page UUID를 추출해 `update_page.page_id`로 사용한다. Page URL 전체를 `page_id`에 전달하지 않는다.
2. payload에는 요청된 allowlist 속성만 포함한다.
3. 이미 같은 값은 skip한다.
4. Page별 결과를 기록하며 실패를 숨기지 않는다.
5. 생성, 삭제, 본문 수정, schema 변경은 수행하지 않는다.

### 6. Verify all targets

전체 대상 Page를 다시 읽어 요청값을 확인한다. 요청하지 않은 allowlist 속성과 Page 본문이 바뀌지 않았는지 비교한다. 성공, 실패, 불일치, 부수 변경 수를 각각 보고한다.

## Stop conditions

다음 중 하나면 쓰지 않고 dry-run 결과만 반환한다.

- Notion `스프린트` 값이 필요하지만 명시되지 않음
- local metadata 불일치
- Notion Page 누락, 중복 또는 `분류` 불일치
- relation target 또는 select option 검증 실패
- 기존 값 conflict에 대한 교체 권한 없음

## Example

사용자 요청: `S06 Task의 상위 작업과 우선순위를 동기화하고 스프린트 1에 넣어.`

1. S06 Story를 실제 Task 목록으로 전개한다.
2. Priority를 `P5`로 계산한다.
3. Notion의 정확한 `스프린트 1` Page를 확인한다.
4. dry-run 전체가 통과하면 `상위 작업`, `우선순위`, `스프린트`만 수정한다.
