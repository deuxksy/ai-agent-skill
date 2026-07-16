---
name: handoff
description: "현재 세션 작업을 .zzizily/handoff/에 구조화 저장. /clear 또는 context 압축 전 수동 호출해 작업 상태를 보존. new session에서 /zzizily:resume으로 이어작업. Use when context가 가득 차기 전이나 세션 종료 직전 현재 진행 작업을 저장할 때."
---

## 지침

현재 세션 작업을 handoff 파일로 저장한다. 목표: new session의 `/zzizily:resume`이 TODO·진행상태·다음 액션을 복원할 수 있게.

### 1. 저장 경로 준비

1. repo root 결정: `git rev-parse --show-toplevel`. 실패(비-Git) 시 cwd를 root로 사용하고 frontmatter의 `git_*` 필드를 생략
2. handoff dir: `<root>/.zzizily/handoff/`. 미존재 시 생성
3. `<root>/.zzizily/.gitignore` 가 없으면 생성(내용은 `*` 한 줄). `git check-ignore <root>/.zzizily/handoff/probe` 로 추적 제외 확인(출력되면 무시됨 = OK)
4. handoff 경로가 symlink면 **fail-closed**: `test -L "<root>/.zzizily/handoff"` 로 확인, 참이면 저장 중단하고 사용자에게 symlink임을 통보

### 2. 메타데이터 수집

bash로 수집:

- `project`: `basename "$(git rev-parse --show-toplevel 2>/dev/null || echo "$PWD")"`
- `saved_at`: `date -u +%Y-%m-%dT%H:%M:%SZ`
- `git_branch`: `git rev-parse --abbrev-ref HEAD 2>/dev/null`
- `git_head`: `git rev-parse --short HEAD 2>/dev/null`
- `git_dirty`: `git diff --quiet HEAD 2>/dev/null && echo false || echo true`

### 3. handoff 본문 작성

현재 세션 context에서 아래 규격으로 작성한다. **제약(spec §9)**:

- **repo-relative path만** 기록(절대 경로 금지)
- **secret 미기록**: `.env*`, API key, token, command output, file contents는 어떤 섹션에도 쓰지 않는다
- 빈 세션(의미 있는 작업 없음)이면 본문에 `## 작업 목표\nNo active work.` 만 적고 저장

#### handoff 파일 규격 (canonical)

```markdown
---
schema_version: 1
session_id: <uuid 또는 timestamp>
project: <repo basename>
saved_at: <ISO 8601 UTC>
git_branch: <branch>
git_head: <short SHA>
git_dirty: <true|false>
trigger: manual(handoff)
---

# Handoff — <project>

## 작업 목표
<이 세션 최상위 목표 1-2줄>

## 완료
<done — 커밋 SHA / 파일 경로(repo-relative) / 결정>

## 진행 중
<현재 task + 관련 파일/현재 상태>

## 다음 액션
<resume 즉시 실행할 것 1-3, 우선순위순>

## 블로커 / 의존
<막힌 것, 대기 — 없으면 섹션 생략>

## 비자명 컨텍스트
<gotcha, 결정 사유, 취향 — 없으면 섹션 생략>

## TODO 스냅샷
<현재 TaskList 상태 요약 — resume이 task 재구성에 사용>
```

### 4. 안전한 저장 순서

1. 임시 파일에 write: `<root>/.zzizily/handoff/.tmp-<short8>` (`<short8>`는 `date +%s | tail -c 9` 등 8자리)
2. **secret scan**: `command -v gitleaks >/dev/null && gitleaks detect --source "<tmp>" --no-git -v`. 탐지 시 **저장 중단 + 사용자에게 "secret 감지, 저장 취소" 통보**. gitleaks 미설치 시 건너뛰되 결과 보고에 "gitleaks 미설치로 deterministic 보장 아님" 명시
3. archive로 이동: 파일명 `handoff-<UTC-ts>-<short8>.md` (UTC-ts 형식 `20260716T123456Z`, Windows-safe `:` 회피). `mv "<tmp>" "<root>/.zzizily/handoff/handoff-<ts>-<short8>.md"`
4. latest 갱신(atomic): `cp "<archive>" "<root>/.zzizily/handoff/latest.md.new" && mv "<root>/.zzizily/handoff/latest.md.new" "<root>/.zzizily/handoff/latest.md"` (같은 filesystem rename, race 방지)

### 5. 결과 보고

저장된 archive 경로와 한 줄 요약 출력. 예: `Saved to .zzizily/handoff/handoff-20260716T123456Z-ab12cd34.md. new session에서 /zzizily:resume으로 복원.` secret scan 결과(gitleaks 실행 여부)도 함께 보고.
