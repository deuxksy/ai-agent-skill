---
name: report
description: "스트레스 테스트 결과 보고서 생성. summary.md와 run 폴더에서 VU별 추이·knee·MAX 처리량 Req/s·TPS tx/s 분리 기록 결과서와 차트를 자동 생성. '결과 리포트', '결과서'에서 사용."
---

# Report — 보고서·차트

## 0. 지표 정의 — 모든 결과서 헤더에 명시 (필수)

| 용어 | 의미 | 예시 |
| :--- | :--- | :--- |
| **Throughput** | 일정 시간 동안 처리한 전체 작업량인 **성능 지표** | 초당 주문 100건, 초당 요청 500건 |
| **Transaction** | 논리적으로 정의한 하나의 **업무 처리 단위** | 주문 생성, 송금, 좌석 예약 |
| **Request** | 클라이언트가 서버에 보내는 하나의 **요청 단위** | HTTP API 호출 1회 |

정량식: `Throughput = 완료된 Transaction 수 ÷ 시간`. 기록 규칙:

- **TPS (tx/s)** = 완료된 Transaction(업무 루프) 수/초 — Req/s ÷ 루프당 HTTP 수(JMX 스텝 수)
- **Req/s (req/s)** = 완료된 Request(HTTP 요청) 수/초 — Transaction parent 제외
- 결과서 헤더의 "측정 지표 정의"에 시나리오별 **루프당 HTTP 수와 TPS 환산식**을 명시한다 (예: 2-1 = 목록+상세 2 HTTP/루프 → TPS = Req/s ÷ 2). "TPS" 라벨에 req/s 값 병기 금지, "사이클" 용어 금지(RULES §3)

## 1. 입력

- 시나리오명 또는 결과 폴더(`results/<OUT>`) — `results/summary.md`(run/knee 누적)에서 해당 시나리오 행 추출, 각 run의 `run.md`에서 상세(형상·명령·특이사항) 확보
- 무결성 exit=1 run은 collect 스킬에서 이미 제외된 상태여야 함 — 결과서에 중단 run을 섞지 않는다

## 2. 결과서 구조 (자동 생성 목차)

```text
1. 개요 — 시나리오·목적·테스트 일시
2. 테스트 범위 — | 시나리오 | VU | Ramp | Duration | 실행시각 |
3. VU별 추이 — VU별 Req/s·TPS (tx/s)·p95·stdev 표 (summary.md 행 그대로)
4. knee·MAX 판정 — knee 스킬 산출 인용(knee VU, MAX Req/s, MAX TPS tx/s, 판정 근거 행)
5. 전체 루프 및 스텝 상세 분석 — 아래 표준 표 2종 기본 포함
   - (1) 기본 전체 루프 성능 표 (TPS (tx/s)와 Req/s (req/s) 분리 병기 + 루프 시간 통계)
   - (2) 측정 대상 API별 세부 지표 (Avg, Stdev, Min, Max, p95, Err%)
   - (3) 다단계/구간 분리 시나리오인 경우: Delta 누적 소요시간 테이블 추가 필수
6. 병목 판정 — 아래 스켈레톤
7. 부록 — run 폴더 역추적 링크(results/<OUT> 상대경로) + evidence 목록
```

### 5.1 기본 전체 루프 성능 표 (Report 기본 필수)

모든 일반 보고서의 5장에는 전체 업무 흐름의 완주 및 HTTP 전송 처리량을 요약하는 아래 테이블을 기본으로 포함한다:

| 시나리오 JMX | 완료 횟수 (회) | 총 HTTP 전송 | TPS (tx/s) | Req/s (req/s) | 루프 Avg (ms) | 루프 Stdev (ms) | 루프 Min (ms) | 루프 Max (ms) |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `scen.jmx` | N 회 | M req | A.B | C.D | E.F ms | G.H ms | I ms | J ms |

### 5.2 다단계 구간 측정 시 필수: Delta 누적 소요시간 테이블

여러 JMX 또는 단계별로 누적/분리되는 시나리오를 측정·보고할 때는 5.1 기본 표와 함께 아래 **Delta 누적 테이블**을 최우선 필수 지표로 작성한다:

| 시나리오 JMX | 단계 구성 | 전체 흐름 평균 시간 | 단계 추가 증가량 (Delta) | 비중 (%) | 상태 / 분석 |
| :--- | :--- | ---: | ---: | ---: | :--- |
| `scen-1.jmx` | `[1단계]` (1 req) | base ms | +base ms | a% | 기본 단계 |
| `scen-2.jmx` | `[1단계]` + `[2단계]` (2 reqs) | T2 ms | +(T2 - T1) ms | b% | 신규 추가 지연 |
| `scen-3.jmx` | `[1단계]` + `[2단계]` + `[3단계]` (3 reqs) | T3 ms | +(T3 - T2) ms | c% | 누적 병목 지연 |

모든 수치는 표로 — 본문에는 해석만. 산출 경로: `docs/` 또는 사용자 지정.

## 3. 차트

`gen_stress_charts.py` 패턴 — **단일 스크립트, 외부 스타일 상속 없이 자체 생성**(하우스 스타일 상수 내장: tab10 계열 색상, 계열별 고유 마커, 포인트 값 라벨, 한글 폰트). matplotlib로:

- VU-Req/s 곡선 — 포인트 마커 + 각 포인트 값 라벨, knee VU에 수직 보조선
- VU-p95 곡선 — 목표 SLA 기준선이 있다면 함께
- 시나리오 비교 막대 — 여러 시나리오 MAX Req/s와 TPS (tx/s) 나란히

```bash
python3 gen_charts.py results/summary.md --scenario <시나리오> --out <결과서 폴더>/
# 산출: <결과서 폴더>/vu-reqs.svg, vu-p95.svg, scenario-compare.svg (PNG 옵션)
```

차트 데이터는 summary.md 표 값을 그대로 플롯 — 재계산 금지.

## 4. 병목 판정 스켈레톤

클라이언트 지표(JMeter) **확정 사실**만 먼저 기입:

| 구분 | 지표 | 값 | 근거 run |
| :-- | :-- | :-- | :-- |
| 확정(클라이언트) | knee VU / MAX Req/s·TPS (tx/s) / p95 급증 시점 | summary.md·knee 판정 | results/<OUT> |
| 조회(서버) | HikariCP active/pending, CPU, vLLM 대기열 | Grafana 조회 가이드 | — |

서버 지표 조회 가이드(Grafana): knee 전후 시각창으로 HikariCP `hikaricp_connections_active/pending`, 노드 CPU, `vllm:num_requests_waiting` 대시보드 확인. **판정 문구는 사용자 확인 후 기입** — 스킬이 임의로 병목 결론을 내리지 않는다.

## 5. 경고

- 차트·수치는 `summary.md`·`run.md`(및 무결성 통과 jtl의 aggregate 출력)에서만 — **재해석·외삽 금지** (예: 측정 VU 범위 밖 처리량 추정)
- 결과서의 모든 표 값에 출처(summary.md 행 또는 results/<OUT>)를 남긴다
