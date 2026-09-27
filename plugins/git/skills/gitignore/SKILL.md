---
name: gitignore
description: "Use when the user asks to create, update, or add entries to a project's .gitignore file."
---

# Manage .gitignore

프로젝트에서 확인한 생성물과 사용자가 지정한 경로만 `.gitignore`에 반영한다. 기존 규칙과 주석은 보존한다.

## Workflow

1. 대상 Git repository의 root와 수정할 `.gitignore` 경로를 확인한다. 사용자가 하위 디렉터리를 지정했으면 해당 위치를 사용한다. 대상이 모호하면 root `.gitignore`를 기본으로 한다.
2. 기존 `.gitignore`, 하위 `.gitignore`, 관련 도구 설정과 실제 생성물을 읽는다. 언어 이름만으로 build directory나 IDE 규칙을 추측하지 않는다.
3. 추가할 pattern마다 무시 대상과 근거를 정한다. Secret, 로컬 환경 파일, build output, cache처럼 재생성 가능하거나 추적하면 안 되는 파일을 우선한다. 소스, lockfile, 설정 예시는 실제 추적 정책을 확인한다.
4. 기존 pattern의 적용 범위를 `git check-ignore -v --no-index -- <path>`로 확인한다. Negative pattern(`!`)과 하위 `.gitignore`의 재포함 효과도 확인한다. 이미 충분히 무시되는 경로는 중복 추가하지 않는다.
5. 새 파일이면 관련 항목만 간결하게 작성한다. 기존 파일이면 순서·스타일·주석을 유지하고 필요한 pattern만 인접한 그룹에 추가한다. 넓은 wildcard보다 대상 범위가 명확한 pattern을 사용한다.
6. 기존 파일은 `git diff -- <gitignore-path>`, 새 파일은 파일 내용 확인으로 변경 결과를 검증한다. 대표 경로에 `git check-ignore -v --no-index -- <path>`를 실행한다. 추적 중인 파일은 `.gitignore` 추가만으로 추적이 해제되지 않으므로 `git ls-files -- <path>`로 확인하고 별도 보고한다.

## Pattern 선택

| 대상 | 선택 기준 |
| :--- | :--- |
| root의 특정 directory | `/<name>/`으로 root에 한정 |
| 모든 깊이의 directory | `<name>/`이 실제 요구일 때만 사용 |
| 특정 파일 | 파일명이나 상대 경로를 명시 |
| Secret 파일 | 실제 이름을 확인하고 예시 파일까지 가리는 wildcard는 피함 |

## Safety

- 기존 `.gitignore`를 템플릿으로 덮어쓰지 않는다.
- `git rm --cached`, `git clean`, 파일 삭제, Git index 변경은 이 Skill 범위에 포함하지 않는다. 이미 추적 중인 민감 파일은 즉시 사용자에게 알린다.
- `.git/info/exclude`와 global excludes는 공유 `.gitignore`와 용도가 다르다. 사용자별 항목이면 공유 파일에 넣기 전에 범위를 판단한다.
- 검증에는 실제 존재하는 파일만 의존하지 않는다. `git check-ignore --no-index`로 아직 생성되지 않은 대표 경로도 확인한다.

## Result

추가·유지한 pattern, 검증한 대표 경로, 이미 추적 중이어서 별도 조치가 필요한 파일을 간결하게 보고한다.
