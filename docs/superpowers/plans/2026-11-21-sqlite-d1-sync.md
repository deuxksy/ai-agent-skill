# SQLite–D1 수동 전체 복제 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development or superpowers:executing-plans. Steps use checkbox syntax.

**목표** — SQLite와 D1의 사용자 스키마와 데이터를 선택한 방향으로 수동 교체한다.

**구조** — Python CLI가 미리보기, 승인, 백업, 교체와 검증을 담당한다. 로컬은 sqlite3, 원격은 Cloudflare 공식 CLI 어댑터를 사용한다.

**기술** — Python 3.12+, sqlite3, unittest, Cloudflare CLI.

**설계** — [SQLite와 D1 수동 복제](../specs/2026-11-21-sqlite-d1-sync-design.md)

## 공통 제약

실행마다 방향 하나를 지정한다. 사용자 스키마 전체를 반영한다. 두 DB를 묶는 트랜잭션은 없다. 설정과 로그에 비밀값이나 개인 절대 경로를 기록하지 않는다. 테스트는 원격 명령을 모의 처리한다.

## 파일과 인터페이스

모든 경로는 `plugins/dev/skills/sqlite-d1-sync/` 기준이다.

- `scripts/sqlite_d1_sync.py`에서 `main(argv: list[str]) -> int`, `snapshot_local(path: Path, destination: Path) -> Snapshot`, `restore_local(source_sql: Path, target: Path) -> None`을 제공한다.
- `scripts/d1.py`에서 `export(database: str, destination: Path) -> None`과 `replace(database: str, source_sql: Path) -> None`을 제공한다. CLI 종료 상태와 오류는 호출자에게 전달한다.
- `Snapshot`은 일관된 스냅샷의 사용자 스키마, 테이블별 행 수, 변경 검사용 지문을 담는다.
- `tests/test_sync.py`에서 로컬 임시 DB와 모의 CLI를 사용한다.
- `SKILL.md`와 `assets/config.example.toml`에 인터페이스와 복구 예시를 제공한다.

## 작업 1 — 스냅샷과 로컬 복원

- [ ] 임시 DB로 `test_local_round_trip`을 작성한다. 인덱스, 뷰, 트리거와 행이 복원되고 대상에만 있던 테이블이 사라지는지 검사한다.
- [ ] `test_restore_failure_preserves_target`에서 잘못된 SQL을 주입하고 기존 DB의 행과 파일이 유지되는지 검사한다. `test_missing_is_not_empty`에서 없는 원본은 실패하고 0행 테이블은 스냅샷에 포함되는지 검사한다.
- [ ] 테스트 모듈이 구현 부재로 실패하는지 확인한다.
- [ ] 일관된 로컬 백업을 만든 뒤 덤프와 건수를 계산한다. 복원은 대상과 같은 디렉터리의 임시 DB에서 스키마·무결성·외래 키를 검사한 뒤 교체한다. 교체 전 대상 DB를 사용하는 Vesper-X 프로세스를 종료하도록 안내한다.
- [ ] 스킬 디렉터리에서 `python3 -m unittest discover -s tests -v`를 실행해 통과를 확인한다.

## 작업 2 — D1 교체와 승인 흐름

- [ ] `test_decline_makes_no_writes`, `test_changed_snapshot_requires_approval`에서 거절과 동일 건수 변경이 원격 쓰기로 이어지지 않는지 확인한다.
- [ ] `test_remote_failure_stops_second_pair`와 `test_both_directions_verify_counts`에서 원격 실패 시 후속 쌍에 쓰지 않고, 성공한 각 쌍의 스키마와 건수를 검증하는지 확인한다. `test_cli_output_omits_payload`에서 행 값과 다운로드 URL이 표시되지 않는지 검사한다.
- [ ] 같은 unittest 명령으로 새 테스트의 실패를 확인한다.
- [ ] CLI에 `--config PATH --direction local-to-d1|d1-to-local`을 추가한다. TOML의 `[[databases]]`마다 `local_path`, `d1_database`를 받는다. 읽기 전용으로 미리보기하고 승인 후 재검사와 백업을 수행한다. 누락·중복 대상과 계정 불일치를 적용 전에 검사한다.
- [ ] D1 export로 사용자 스키마를 확인한다. 교체용 SQL의 호환성과 외래 키 순서를 임시 SQLite에서 검증한다. D1이 지원하는 실행 단위와 한도를 공식 문서에서 확인하고 기존 사용자 객체 제거와 원본 재구성을 수행한다. 오류 시 적용을 중단하고 영향받은 DB와 복구에 사용할 백업을 알린다.
- [ ] 전체 unittest를 실행한다. 승인된 테스트 D1에서 별도로 전체 왕복과 복구를 검증한 뒤 실제 데이터에 적용한다.

## 작업 3 — 스킬 등록

- [ ] 두 방향의 실행과 복구 절차, 백업 보관 위치, 미리보기 예시를 `SKILL.md`에 추가한다. 예제 TOML에는 상대 경로와 샘플 D1 이름을 쓴다.
- [ ] dev README와 Claude/Codex 매니페스트·마켓플레이스 메타데이터를 저장소 규칙에 맞춰 동기화한다.
- [ ] 전체 unittest, Python 구문 검사와 매니페스트 JSON 검증을 실행한다.
