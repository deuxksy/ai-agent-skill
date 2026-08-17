# Windows ACL Owner Reset Skill Specification

## Goal

Windows 파일/디렉터리의 owner와 현재 실행 사용자 기준 ACL을 안전하게 정리하는 재사용 가능한 Codex skill을 추가한다.

## Scope

- 대상 경로는 사용자 지정값을 사용하며, 미지정 시 현재 작업 디렉터리를 사용한다.
- 현재 실행 사용자와 SID는 `whoami /user` 또는 PowerShell API로 조회한다.
- 대상의 owner와 ACL을 변경 전에 preview한다.
- 디렉터리는 명시된 범위에서만 recursive 적용한다.
- owner는 현재 실행 사용자로 설정하고, 현재 사용자에게 `Full Control`을 부여한다.
- 기존 ACL과 `DENY` rule은 자동 삭제하지 않는다.
- 관리자 권한이 필요한 경우 escalation을 사용한다.

## Safety Requirements

- `C:\Users\deuxk` 전체를 기본 대상이나 암묵적 recursive 대상으로 사용하지 않는다.
- 경로를 명령 문자열로 조합하거나 `eval`하지 않는다.
- 변경 후 owner, SID, ACL, 실패 항목을 다시 검증한다.
- Git repository에서는 `git status` 등 read-only 검증만 수행한다.

## Acceptance Criteria

1. Skill metadata가 Windows owner/SID/ACL 오류를 trigger로 설명한다.
2. 경로 미지정 기본값과 지정 경로 동작이 명시되어 있다.
3. 현재 사용자 SID를 동적으로 확인한다.
4. recursive 범위와 기존 `DENY` 보존 정책이 명시되어 있다.
5. 변경 전 preview와 변경 후 verification 절차가 포함되어 있다.
