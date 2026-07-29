# Instruction Quality Criteria

각 instruction file과 effective hierarchy를 100점으로 평가한다.

| Criterion | Weight | Pass condition |
| :--- | ---: | :--- |
| Commands/workflows | 15 | Build, test, lint, deploy command가 실제 config와 일치 |
| Architecture/key paths | 15 | Entry point, 주요 module, dependency 관계가 현재 codebase와 일치 |
| Currency | 15 | 삭제·이동·rename된 command/path가 없음 |
| Actionability | 15 | 모호한 권고가 아니라 실행·검증 가능한 instruction |
| Common/vendor separation | 15 | 공통 rule은 `.ai/RULES.md`, vendor rule은 해당 vendor file에만 존재 |
| Hierarchy/reference | 15 | Root reference와 nested precedence가 정확하며 중복 import 없음 |
| Non-obvious gotchas | 5 | 반복 가능한 환경·tool·workflow 함정만 포함 |
| Conciseness | 5 | 자명한 설명, 장황함, 중복 없음 |

## Grades

- A: 90-100
- B: 70-89
- C: 50-69
- D: 30-49
- F: 0-29

## Required report

1. 발견한 file과 적용 scope
2. File별 score와 근거
3. Effective hierarchy의 conflict/reference 문제
4. Codebase와 불일치하는 exact command/path
5. Targeted addition, edit, removal 제안
6. 평균 score와 update 필요 file 수

Score는 근거 없는 감점에 사용하지 않는다. 확인할 수 없는 항목은 `미검증`으로 표시하고 전체 score 한계를 명시한다.
