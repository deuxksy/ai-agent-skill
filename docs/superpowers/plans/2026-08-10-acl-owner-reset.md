# ACL Owner Reset Skill Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Windows ACL owner/SID 불일치를 현재 실행 사용자 기준으로 정리하는 재사용 skill을 추가한다.

**Architecture:** 단일 `SKILL.md`에 trigger metadata, 안전 규칙, PowerShell/`icacls` 절차, 검증 결과 형식을 둔다. 기존 ACL entry와 `DENY` rule은 보존해 권한 삭제와 owner 변경을 분리한다.

**Tech Stack:** Markdown, PowerShell, Windows `icacls`, Codex Skill metadata.

## Global Constraints

- 대상 경로 미지정 시 현재 작업 디렉터리를 사용한다.
- 현재 실행 사용자와 SID를 동적으로 조회한다.
- recursive 변경은 명시된 디렉터리 범위에만 적용한다.
- 기존 ACL과 `DENY` rule을 자동 삭제하지 않는다.
- 변경 전 preview와 변경 후 verification을 수행한다.

---

### Task 1: ACL Owner Reset Skill

**Files:**
- Create: `plugins/infra-provisioning/skills/acl-owner-reset/SKILL.md`
- Reference: `docs/superpowers/specs/2026-08-10-acl-owner-reset-design.md`

**Interfaces:**
- Consumes: 대상 경로(선택), recursive 범위(디렉터리에서 명시)
- Produces: 현재 사용자 기준 owner/ACL 변경 절차와 검증 결과

- [ ] **Step 1: metadata와 trigger 작성**

`name`은 `acl-owner-reset`으로 지정하고, Windows owner 오류, current-user SID mismatch, Git dubious ownership, ACL access error를 trigger에 포함한다.

- [ ] **Step 2: 안전 경계 작성**

경로 기본값, 사용자 SID 동적 조회, 변경 전 preview, recursive 범위, 기존 `DENY` 보존, escalation 요구를 명시한다.

- [ ] **Step 3: 최소 실행 절차 작성**

다음 핵심 명령을 현재 사용자 변수와 대상 변수로 문서화한다.

```powershell
$currentUser = [System.Security.Principal.WindowsIdentity]::GetCurrent().Name
icacls $target /setowner $currentUser /T /C
icacls $target /grant "${currentUser}:(OI)(CI)F" /T /C
```

파일 대상에는 `/T`, `(OI)`, `(CI)`를 사용하지 않는 조건도 포함한다.

- [ ] **Step 4: verification과 결과 형식 작성**

owner, SID, ACL, inherited/remaining `DENY`, 실패 항목, Git read-only 검증 결과를 보고하도록 작성한다.

- [ ] **Step 5: 문서 검증**

Run: `python C:\Users\deuxk\.codex\skills\.system\skill-creator\scripts\quick_validate.py plugins\infra-provisioning\skills\acl-owner-reset`

Expected: YAML frontmatter와 skill naming 검증 통과. `PyYAML`이 없으면 해당 의존성 누락을 기록하고 frontmatter를 수동 확인한다.

- [ ] **Step 6: 변경 상태 확인**

Run: `git status --short`

Expected: 새 skill과 두 설계 문서만 task 관련 변경으로 표시되고 기존 `.omx/`는 제외한다.
