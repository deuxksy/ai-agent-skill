# DB 점검 판정 기준 (PostgreSQL·Doris)

- 근거: KECO Ⅱ-5 (DB 구축)·Ⅴ-2 (개인정보) — 실측 환경(ecoai-dev PG HA·mgmt-system Doris) 검증 절차 기반
- 원칙: **실측 사실만 기록 — 미적용·부재는 "조치계획"으로 분류** (보수적 판정)

## 판정표

| 항목 | 양호 (충족) | 취약 (조치계획) |
| :--- | :--- | :--- |
| PG 앱 계정 최소권한 | 앱 계정에 superuser·CREATE ROLE·CREATE DB 없음 | 앱 계정이 superuser 또는 권한 보유 |
| PG 운영 superuser | `postgres`·`repmgr` 등 운영·HA 필수 계정이 앱 계정과 분리 | 앱이 운영 계정 공용 사용 |
| PG 계정 만료 정책 | `rolvaliduntil` 설정 (전 계정 만료일 존재) | `rolvaliduntil = none` 전 계정 만료일 없음 |
| Doris 계정 분리 | 앱 전용 계정 존재 | `admin@%`·`root@%` 공용 사용 |
| Doris host 제한 | 접속처별 host 지정 | `%` 와일드카드 (내부망 전제면 실위험 낮음 — 병기) |
| 개인정보 평문 저장 | `length()` 분포가 일정 (암호화·base64 등) 또는 bytea 타입 | length 분포가 원문 길이와 일치 (전화번호 11·13 등) → 평문 |
| password 컬럼 | password 저장 컬럼 부재 — 자격증명은 K8s Secret·Keycloak 위임 | 테이블에 평문 password 저장 |
| 백업 자동화 | 백업 CronJob 등록·이력 존재 | CronJob 0건 (백업 자동화 미수립) |

## 실측 주의

- 평문 판정은 `length()` 분포로 추정 후 필요 시 샘플값 마스킹 확인 — 증빙에 원문 개인정보를 그대로 남기지 않는다
- 쿼리는 전부 읽기 전용 (SELECT·SHOW·EXPLAIN) — 실행 전 변경 구문 아님 재확인
- 앱 계정 목록·테이블 목록은 점검 대상 DB 스키마(`information_schema`)에서 먼저 식별한다
- 자격증명은 `sops` 복호화로만 로드 — 리포트·커밋에 평문 기입 금지
