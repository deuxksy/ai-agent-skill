---
name: db
description: "DB 보안 점검 (PostgreSQL·Doris). 읽기 전용 SQL로 계정·권한·개인정보 필드 평문 저장·백업 상태를 점검 후 양호/조치계획 판정과 증빙 리포트 생성. `/kisa:db`."
---

# Database Security Audit (PostgreSQL·Doris)

PostgreSQL·Apache Doris의 계정·권한·민감컬럼을 읽기 전용 쿼리(SELECT·SHOW·EXPLAIN)로 점검한다. KECO Ⅱ-5(DB 구축)·Ⅴ-2(개인정보) 근거 산출용.

## 핵심 프로세스

```text
사전 조건 확인 (MCP 기동) → 계정·권한 점검 (PG·Doris) → 개인정보 필드 평문 스캔 → 백업 상태 → 판정 → 증빙 리포트 md 생성
```

## 사용법

```bash
/kisa:db          # 기본 대상: ecoai-dev PostgreSQL + mgmt-system Doris
```

- 인자 없이 호출하면 기본 대상(ecoai-dev PG·mgmt-system Doris — ecoai 프로덕션 환경 값)으로 실행한다. 다른 DB 점검 시 DBHub·Doris MCP 접속 설정과 점검 대상 계정·테이블 목록을 먼저 조정한다

## 절차

### 1. 사전 조건

```bash
telepresence connect                    # K8s 네트워크 연결 (Tailscale Split DNS로 .svc.cluster.local 해석)
source <(sops -d ~/.key)                # DB 자격 증명 로드 (평문 기입 금지)
```

| 항목 | 도구 | 접속 |
| :--- | :--- | :--- |
| PostgreSQL | DBHub MCP | `~/.config/dbhub/dbhub.toml` 설정 (`npx @bytebase/dbhub --transport stdio`) |
| Doris | doris-mcp-server | `~/.config/doris-mcp/run.sh` (내부 `.env` 로드, stdio) |

- MCP는 STDIO 모드 — 세션 재시작 시 새로 기동
- **읽기 쿼리만 사용** (SELECT·SHOW·EXPLAIN) — 변경·삭제 금지

### 2. 계정·권한 점검 (PostgreSQL)

```sql
-- 전체 롤·속성 (superuser·만료일·로그인 가능 여부)
SELECT rolname, rolsuper, rolcanlogin, rolvaliduntil, rolcreaterole, rolcreatedb
FROM pg_roles ORDER BY rolname;

-- 앱 계정 테이블스페이스 권한 (최소권한 확인)
SELECT grantee, table_schema, privilege_type
FROM information_schema.role_table_grants
WHERE grantee IN ('<앱 계정 목록>')
ORDER BY grantee, table_schema;
```

- 앱 계정(예: `ecoaiplatform`·`keycloak`)에 superuser·CREATE ROLE·CREATE DB 권한이 없으면 최소권한 충족
- `postgres`·`repmgr` 등 superuser는 운영·HA 필수이므로 앱 계정과 분리돼 있으면 허용

### 3. 계정 점검 (Doris)

```sql
-- 전체 사용자
SELECT User, Host FROM mysql.user;
```

- 앱 전용 계정 없이 `admin@%`·`root@%` 공용 사용이면 계정 분리 미흡
- `%` 와일드카드 host는 접근 제한 미흡 (내부망 전제면 실위험 낮음 — 판정에 병기)

### 4. 개인정보 필드 스캔 (평문 저장 확인)

```sql
-- PG: 컬럼 타입·길이 분포로 평문 여부 판정 (암호화되면 len이 일정)
SELECT length(<개인정보 컬럼>) AS len, count(*) AS cnt
FROM <개인정보 포함 테이블>
GROUP BY len ORDER BY cnt DESC LIMIT 5;

-- PG: 개인정보 컬럼 존재 확인
SELECT column_name, data_type FROM information_schema.columns
WHERE table_name IN (<점검 대상 테이블 목록>)
  AND column_name ~ '(phone|email|address|token|name)'
ORDER BY table_name, column_name;

-- Doris: 개인정보 테이블 존재·행 수
SELECT count(*) FROM <스키마>.<개인정보 테이블>;
```

- 대상 테이블·컬럼은 스키마 조회(`information_schema`)로 먼저 식별한다

### 5. 백업 상태 확인 (K8s)

```bash
export KUBECONFIG=~/.kube/mgmt.config
kubectl get cronjobs -A                              # 정기 백업 자동화 여부
kubectl get pvc -A | grep -E 'NAMESPACE|<DB namespace>'  # -n 중복 불가 → -A 후 필터
```

### 6. 판정

각 항목의 양호/조치계획 조건은 [references/verdict-criteria.md](references/verdict-criteria.md) 참조. 요약:

| 그룹 | 대표 양호 조건 |
| :--- | :--- |
| 계정·권한 | 앱 계정 최소권한, superuser 분리, 계정 만료 정책 |
| 계정 분리 (Doris) | 앱 전용 계정, host 와일드카드 미사용 |
| 개인정보 | 평문 미저장 (length 일정·bytea), password 컬럼 부재(자격증명 K8s Secret·IdP 위임) |
| 백업 | 백업 CronJob 등록 |

**판정 원칙**: 실측 사실만 기록 — 암호화 미적용·만료 정책 없음은 "조치계획"으로 분류 (보수적).

### 7. 증빙 리포트

출력 경로: **`./report/db-<대상>-<YYMMDDhhmm>.md`** (`report/` 없으면 생성)

형식은 linux·web·ai 스킬과 동일한 구조(메타 헤더 → 섹션 → 항목별 판정·쿼리·결과). SQL 점검은 `명령:` 대신 `쿼리:` 블록에 원문을 남긴다.

````markdown
# <DB 대상> DB 보안 점검 증빙
- 대상: PostgreSQL(<namespace/클러스터>), Doris(<namespace>)
- 기준: KECO Ⅱ-5 (DB 구축) · Ⅴ-2 (개인정보)
- 실행: <YYYY-MM-DD KST>, 읽기 전용 쿼리 (SELECT·SHOW·EXPLAIN)
- 요약: **양호 N · 조치계획 M · 해당없음 K**
## 1. 계정·권한 (PostgreSQL)
### 계정 만료 정책 — 판정: **조치계획**
쿼리:
```sql
<실측 쿼리>
```
결과:
```text
<쿼리 출력 원문>
```
````

## 안전 규칙

- **읽기 쿼리만 실행** — SELECT·SHOW·EXPLAIN 외 금지 (INSERT·UPDATE·DELETE·DDL 절대 금지)
- 판정은 실측 사실 기반 — 추측으로 양호 판정 금지
- 증빙에는 자격증명·연결 문자열이 남지 않는지 확인 후 산출물 저장
- 조치(remediation)는 별도 작업 — 이 스킬은 진단만

## 참고

- 점검 근거: KECO(기후에너지환경부) 정보보안점검 매뉴얼 Ⅱ-5·Ⅴ-2
- 판정 기준 상세: [references/verdict-criteria.md](references/verdict-criteria.md)
- 관련 스킬: `kisa:ai`(AI 워크로드·pgvector 인프라), `security:code-audit`(앱 코드)
