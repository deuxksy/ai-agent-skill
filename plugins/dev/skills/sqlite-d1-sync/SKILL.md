---
name: sqlite-d1-sync
description: Manually replicate entire SQLite databases to Cloudflare D1 or restore them locally after reviewing table row counts and approving replacement.
---

# SQLite와 Cloudflare D1 전체 복제

Python 3.12 이상과 인증된 Wrangler CLI를 사용한다. 먼저 D1에 대상 DB를 만들고, 이 도구 전용 설정을 사용한다. 도구는 Wrangler에 별도의 빈 구성을 전달해 프로젝트 바인딩의 영향을 피한다.

1. [예제 설정](assets/config.example.toml)을 복사하고 로컬 파일 경로, 계정 ID와 D1 DB 이름을 지정한다. 상대 경로는 설정 파일을 기준으로 해석한다.
2. `CLOUDFLARE_ACCOUNT_ID`를 설정의 계정 ID와 동일하게 설정한다. 수집기와 대상 DB에 쓰는 다른 프로세스 및 Worker를 중지한 뒤 실행한다. 승인 직후의 재검사 이후에도 외부 쓰기를 막는 잠금은 없으므로 검증이 끝날 때까지 중지 상태를 유지한다.
3. D1으로 올리려면 다음 명령을 실행한다.

   ```sh
   python3 /path/to/scripts/sqlite_d1_sync.py --config ./sync.toml --direction local-to-d1
   ```

   로컬로 복원하려면 `--direction d1-to-local`을 사용한다. 로컬 DB가 없는 새 환경에서는 복원 시 생성된다.

4. 각 DB의 방향과 테이블별 건수를 확인한다. 실행자가 `yes`를 직접 입력하면 대상 백업을 만든 뒤 전체 사용자 스키마와 행을 교체한다. 승인 후 내용이 바뀌면 다시 미리보기한다.
5. DB별 검증 결과를 확인한다. 앞선 DB 교체 후 뒤의 DB가 실패할 수 있으므로 완료된 범위를 확인한다.

D1은 Wrangler SQL 내보내기·가져오기를 사용한다. 먼저 폐기 가능한 D1에서 왕복 및 복구를 확인한다. 일일 쓰기 한도에는 기존 객체와 데이터의 교체 비용도 포함될 수 있다. 백업에는 직접 다운로드 URL 등 DB에 있던 값이 포함되므로 Git 밖의 비공개 위치에서 설정과 백업을 관리한다.

## 복구

백업은 설정 파일과 같은 디렉터리의 `sqlite-d1-backups/` 아래에 생성된다. 번호는 설정 순서다.

- 로컬 DB의 백업은 `N-local.sql`이다. `sqlite3 recovered.db < N-local.sql`로 비어 있는 작업 파일에 복원하고 무결성과 건수를 확인한 뒤, 애플리케이션을 종료한 상태에서 기존 파일을 교체한다. `N-local-missing.txt`는 원래 파일이 없었다는 표시다.
- D1 백업은 `N-d1.sql`이다. `sqlite3 recovered.db < N-d1.sql`로 비어 있는 작업 파일에 복원하고, 해당 DB 한 쌍만 들어 있는 설정으로 `local-to-d1`을 실행한다. 기존 DB와 새 원본의 건수를 확인하고 승인한다.
