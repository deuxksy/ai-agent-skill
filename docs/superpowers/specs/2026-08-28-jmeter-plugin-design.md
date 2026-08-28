# jmeter 플러그인 설계

- **작성일**: 2026-08-28
- **상태**: 승인 (사용자 확정)
- **분류**: Explanation / 설계 문서 (구현은 writing-plans 진행)

---

## 목차

- [1. 배경과 목표](#1-배경과-목표)
- [2. 결정 요약](#2-결정-요약)
- [3. 공통 컨텍스트](#3-공통-컨텍스트)
- [4. 스킬 상세 설계](#4-스킬-상세-설계)
- [5. 리포지토리 반영 사항](#5-리포지토리-반영-사항)
- [6. 검증 계획](#6-검증-계획)
- [7. 오늘 실증 근거](#7-오늘-실증-근거)

---

## 1. 배경과 목표

2026-08-28 EcoAI GS 인증 스트레스 캠페인(ecoai-gwageo, 20개 유효 실행)에서 확립된 실행 프로시저를 스킬화한다. 하루치 실전에서 원격 배포·JMeter 기동·분산 실행·래더 판정·결과 수집·보고까지 전 파이프라인이 검증됐고, 그 과정의 실수 원인 3종(CWD, pgrep self-match, 어설션 조기사망)이 특정돼 예방 절차로 전환 가능하다.

**목표**: JMX 프로젝트에서 `배포 → 실행 → 탐색 → 수집 → 보고`를 스킬 호출만으로 수행.
**비목표**: 부하 발생기 자체 개발, GS 심사 문서 자동화(결과서 뼈대까지만), 프로젝트 특화 더미 데이터 시딩.

## 2. 결정 요약

| 항목 | 결정 | 근거 |
| :--- | :--- | :--- |
| 플러그인명 | `jmeter` | 작업 전체가 JMeter 절대 종속 (JMX·jmeter-server·jtl·-G 프로퍼티) |
| 마켓플레이스 | zzizily 공개 등록 (11번째) | 사용자 확정 — 기존 ai-agent-skill 자산 활용 |
| 버전 | 통합 정책 준수, **1.16.0 전체 동기화** | 신규 기능 = MINOR 범프 |
| 스킬 수 | 6종 (`lint` `deploy` `run` `knee` `collect` `report`) | 파이프라인 + 정적 사전검사 |
| `lint` 명명 | doctor 아님 — 정적 규칙 검사라 lint | claude code /doctor(런타임 환경진단) 뉘앙스 회피 |

```text
jmeter:lint (사전) → jmeter:deploy → jmeter:run ─┐
                                                 ├─→ jmeter:collect → jmeter:report
                              jmeter:knee ───────┘
```

## 3. 공통 컨텍스트

- **프로젝트 감지**: cwd에 `src/jmeter/*.jmx` 존재 시 JMeter 프로젝트로 판정. 미존재 시 스킬 중단.
- **대상 서버 설정**: `jmeter.json` (프로젝트 루트) — `master`, `workers[{host, ip}]`, `remote_path`. 미존재 시 인자 또는 질문으로 생성 제안.
- **OS 분기**: 로컬 Darwin/Linux → `rsync`, Windows → `robocopy`(UNC/SMB, 실패 시 scp fallback). 원격 명령은 항상 `ssh`.
- **CWD 절대경로 규칙**: 원격 cd는 반드시 절대경로 (`~`는 zsh 쌍따옴표/PowerShell 확장으로 깨짐 — 실측).

## 4. 스킬 상세 설계

### 4.1 `jmeter:lint` — JMX 정적 검사 (사전, 실행 없음)

**규칙**:
1. `on_sample_error=stopthread`인 ThreadGroup의 sampler마다: 어설션이 응답코드 단일값(예: 200)·JSONPath 경로 존재를 강제하면 → "실데이터 가변(404·빈 배열) 시 조기사망" 위험 지적
2. 무한루프 확인 (`LoopController.loops=-1`) — scheduler duration 의존 여부
3. 파라미터 기본값 유무 (`__P(...)` default) 및 분산 전파용 `-G` 대상 정의
4. 상대경로 에셋 참조 (worker CWD 의존 경고)

**산출**: 위험 목록(파일:엘리먼트) + 수정 템플릿 — ①상태코드 어설션 `200|404` matches + Ignore Status ②JSONPathAssertion 비활성(추출기 기본값 존재 시) — 2026-08-28 2-3/3-2 수정본 그대로.

**차별**: smoke(고빈도, 런타임)와 상호보완 — lint는 저빈도 함정(3-2: 13,803건 중 27건 실패로 스레드 소진 — smoke로 탐지 불가)을 파일만 보고 예측.

### 4.2 `jmeter:deploy` — 설치·배포·기동

1. **Idempotent 설치**: 원격 `jmeter --version`, `java -version` 검사 → 미설치 시 JDK 17 + JMeter 5.6.3 (tarball → `/usr/local/bin` 심링크) → 버전 검증
2. **자산 동기화**: rsync 증분 (제외: `.git`, `results/`, 시크릿 파일) / robocopy 증분 (`/MIR` 금지)
3. **jmeter-server 기동**: 절대경로 CWD에서 nohup 기동, 검증은 **bracket pgrep** (`[j]ava.*ApacheJMeter`) + `/proc/PID/cwd` readlink
4. **내장 gotcha**: Windows ssh 비대화형 명령은 원격 홈에서 시작 (CWD 위반 1순위 원인) — 항상 절대경로 cd

### 4.3 `jmeter:run` — 1회 실행

- **인자**: `jmx`, `vu`(총), `ramp`, `duration`, `[mode=x2|x1]`, `[--smoke]`, `[--verify-db <쿼리세트>]`
- **T 계산**: x2 → `T=vu/2` (짝수 강제, 홀수면 x1 유도), x1 → `T=vu`
- **명명**: `results/{시나리오}-T{t}x{n}_R{r}_D{d}-{yymmdd-hhmmss}/` (result.jtl + jmeter.log)
- **실행 후 자동**: 풀가동 구간(램프 제외, Transaction parent `→` 라벨 제외) 집계 — TPS·p95·stdev·Err% (검증된 python 스크립트 내장) + **run.md 자동 생성**
- **주의 내장**: 콘솔 `summary =` 는 분산 모드 display 오탐 — 판정은 항상 jtl
- **`--smoke`**: T1~2 VU·D5~10 사전 실행 (통과: Err 0 + 핵심 쓰기 201 + worker 분포 균형)
- **`--verify-db`**: 쓰기 시나리오 후 jtl↔DB 정합 — 쿼리세트는 `jmeter.json`의 `verify_db` 섹션(쿼리 + 기대 매핑)으로 정의, 타임존/시퀀스갭 주의 내장

### 4.4 `jmeter:knee` — 점진 VU 탐색

- **인자**: `jmx`, `[vu_start=2]`, `[step_policy=geo2|list:10,30,50]`, `ramp`, `duration`
- **판정룰 (2026-08-28 확정본)**:
  - 진행: TPS +5% 초과 상승 + Err < 1% + 절대 p95 < 1s (상승 구간에서 p95 배수 미적용)
  - 평탄(±5%): 감지 후 **확인 2포인트까지만** 추가 실행 후 종료 — 잔여 스텝 생략
  - 이상 종료: Err ≥ 5%, 절대 p95 ≥ 1s, 또는 TPS 평탄/하락 구간에서 p95 ≥ 직전 2배
- **런 간 게이트**: 최소 120s + 잔여트래픽 확인(NGINX rate < 1, HikariCP pending = 0, 4-x 계열 후 vLLM waiting = 0) — 미통과 시 30s 재확인
- **산출**: VU-TPS 곡선 표 + knee·MAX TPS 판정 + summary 누적

### 4.5 `jmeter:collect` — 결과 수집·리포트

1. master → 로컬 `results/` 증분 수집 (rsync pull / robocopy reverse)
2. **jtl 무결성 3종**: 마지막 라인 필드수 = 헤더, 샘플 span ≈ DURATION, `summary =` 라인 존재 — 중단 run 식별
3. **HTML 리포트 로컬 생성**: `jmeter -g result.jtl -o report/` (부하원 과부하 방지 — 로컬 생성 규칙, not-empty 폴더 치우고 재생성 gotcha 내장)
4. `[--evidence]`: 문제 발생 run의 원격(pod/서버) 로그 수집·보존 (2026-08-28 Kakao 500 증거 패턴)

### 4.6 `jmeter:report` — 결과 보고서

- **입력**: 시나리오명 또는 결과 폴더/summary.md
- **산출**:
  1. 결과서 마크다운 — 테스트 범위 표(VU/Ramp/Duration), VU별 TPS·p95·stdev 추이, **knee·MAX TPS 판정**, 라벨별 스텝 분석, run 폴더 역추적 링크
  2. **차트 자동 생성** — VU-TPS 곡선, VU-p95, 라벨별 분포 (`gen_stress_charts.py` 패턴 일반화)
  3. 병목 판정 스켈레톤 — 클라이언트 지표(JMeter) 기준 + 서버 지표(Grafana) 조회 가이드

## 5. 리포지토리 반영 사항

1. `plugins/jmeter/.claude-plugin/plugin.json` (v1.16.0) + `skills/` 6종 + `plugins/jmeter/README.md` (How-To)
2. `.claude-plugin/marketplace.json`: jmeter 엔트리 추가 + 전체 버전 1.16.0 동기화
3. 각 `plugins/*/.claude-plugin/plugin.json` 버전 1.16.0 동기화 (meridian 제외 — 독립 버전 유지)
4. `README.md`: 카탈로그 10 → 11, Diátaxis How-To 인덱스에 jmeter 라인
5. `CLAUDE.md`: 카탈로그 표 갱신 + **분류 원칙 8번 추가** — "부하 테스트/JMeter 실행 → `jmeter`"

## 6. 검증 계획

- **lint**: 오늘 문제 있던 `2-3.jmx`/`3-2.jmx` 원본(수정 전) 대상 — 위험 2건 검출이 통과 기준
- **deploy**: 신규/기존 서버 양쪽 (idempotency — 재실행 시 no-op)
- **run/knee/collect/report**: ecoai-gwageo 실전 dogfood — 소규모 시나리오 1종(예: 2-1 재활용)로 전 파이프라인 완주
- 문서 검증: 저장소 규약의 lint/정합 확인 절차 준수

## 7. 오늘 실증 근거 (스킬에 내장할 학습)

| 학습 | 출처 |
| :--- | :--- |
| Windows ssh 비대화형 명령 = 원격 홈 시작 → CWD 위반 | jmeter-server `/home/kls` 기동 사고 |
| zsh 쌍따옴표 `~/` 로컬 확장 → 원격 cd 실패 | 재기동 1차 실패 |
| pgrep 패턴이 ssh bash -c cmdline에 self-match | CWD 오탐 (`/home/kls` 위 조회) |
| stopthread + 엄격 어설션 = 저빈도 조기사망 | 2-3 (404), 3-2 (JSONPath, 스레드 17→3) |
| 콘솔 summary = 분산 display 오탐 | 전 run (`summary = 3 in 60s` vs jtl 29,656) |
| created_date 타임존 가변(버전별 UTC/KST) + id 시퀀스 갭 | 5-3 DB 정합 |
| 램프 잔상이 rate[1m]에 남음 → 게이트는 윈도우 밀림 대기 | 드레인 게이트 운용 |
