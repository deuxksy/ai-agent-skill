# Mapping Contract

## Identity

| Entity | Local identity | Notion identity |
| --- | --- | --- |
| Epic | `epic_id`, directory name | title prefix `EPIC-[A-Z]+-\d{3}` |
| Story | `story_id`, directory name | title prefix `STORY-[A-Z]+-\d{3}` |
| Task | `task_id`, Markdown filename | title prefix `TASK-\d{4}` |

Task title은 `TASK-0739-...`처럼 뒤에 설명이 붙을 수 있다. 비교 key는 `TASK-0739`이며 임의의 고정 길이 substring보다 정규식을 우선한다.

Notion query 결과의 `url`은 relation 값과 fetch에는 사용할 수 있지만 update 식별자로는 정규화한다. URL 끝의 32자리 hex를 추출해 `update_page.page_id`에 전달한다.

```text
https://app.notion.com/3bad9199464c8132a255e828a80bc3ef
                                    └─ page_id: 3bad9199464c8132a255e828a80bc3ef
```

## Relationship

Notion에서는 Task `상위 작업` relation이 해당 Story Page 하나를 가리켜야 한다. Epic은 검증 context이며 Task `상위 작업`에 직접 연결하지 않는다.

## Priority

```text
S01=P0, S02=P1, S03=P2, ..., S10=P9
```

명시값은 계산값보다 우선하지만 dry-run에 override임을 표시한다.

## Write allowlist

| Property | Expected type | Value source |
| --- | --- | --- |
| `상위 작업` | relation | Task `story_id`의 Notion Story Page |
| `우선순위` | select | 명시값 또는 Sprint priority rule |
| `스프린트` | relation/select | 사용자 명시 Notion Page/value |

요청하지 않은 allowlist property도 payload에서 제외한다. `작업 이름`, `분류`, `상태`, `담당자`, 날짜, 본문은 항상 보존한다.

## Atomic preflight

전체 target manifest가 유효하지 않으면 아무 Page도 수정하지 않는다. API가 transaction을 지원하지 않으므로 apply 중 부분 실패는 숨기지 말고 성공 Page와 실패 Page를 구분한 뒤 전체를 재검증한다.

## Result shape

```text
Sprint: S06
Stories: 7
Tasks: 31
Pages: matched / missing / duplicate / wrong-category
Properties: unchanged / empty / conflict
Apply: requested / succeeded / failed / skipped
Verify: matched / mismatched / collateral-change
```
