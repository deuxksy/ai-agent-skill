---
name: acl-owner-reset
description: "Use when a Windows file or directory has the wrong owner, current-user SID mismatch, Git dubious ownership, or ACL access errors."
---

# Windows ACL Owner Reset

대상 경로의 owner와 ACL을 현재 실행 사용자 기준으로 정리한다. 대상 경로를 지정하지 않으면 현재 작업 폴더를 사용한다.

## 안전 규칙

- `whoami /user`로 현재 사용자와 SID를 조회한다. 사용자명과 SID를 추정하거나 하드코딩하지 않는다.
- `C:\Users\deuxk`의 owner/ACL은 기준 정보로 read-only 조회한다.
- 변경 전 대상의 절대 경로, owner, 사용자 SID, ACL을 preview한다.
- 디렉터리 recursive 변경은 사용자가 명시한 범위에만 적용한다. 범위가 불명확하면 중단한다.
- 기존 계정의 ACL entry와 `DENY` rule은 자동 삭제하지 않는다. 제거하려면 정확한 SID와 범위를 별도로 확인한다.
- `C:\Users\deuxk` 전체처럼 광범위한 경로는 명시적 승인 없이 대상으로 삼지 않는다.
- 권한 변경에는 관리자 권한이 필요할 수 있으므로 escalation을 사용한다.

## 절차

1. `Get-Location`, `whoami /user`, `Get-Acl`로 실행 위치와 현재 사용자를 확인한다.
2. 대상 경로를 확정한다. 미지정이면 현재 폴더를 사용한다.
3. 대상 owner와 ACL을 preview하고 변경 범위를 보고한다.
4. 승인 후 디렉터리에 다음을 실행한다.

```powershell
$currentUser = [System.Security.Principal.WindowsIdentity]::GetCurrent().Name
icacls $target /setowner $currentUser /T /C
icacls $target /grant "${currentUser}:(OI)(CI)F" /T /C
```

파일에는 `/T`, `(OI)`, `(CI)`를 사용하지 않는다. 경로는 별도 PowerShell 인자로 전달하고 `eval`이나 문자열 명령 조합을 사용하지 않는다.

5. 대상 owner, 사용자 SID, ACL을 다시 조회한다.
6. Git repository라면 `git status` 등 최소 read-only 검증을 실행한다.
7. 실패 항목, 남은 `DENY`, inherited ACL, Git 오류를 결과에 명시한다.

## 결과 보고

- 대상 경로와 recursive 범위
- 변경된 owner와 현재 사용자 SID
- 부여한 권한
- 기존 ACL 보존 여부
- 실패/미해결 항목
- 검증 결과
