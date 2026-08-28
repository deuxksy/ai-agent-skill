---
name: report
description: "스트레스 테스트 결과 보고서 생성. summary.md와 run 폴더에서 VU별 추이·knee·MAX TPS 결과서와 차트를 자동 생성. '결과 리포트', '결과서'에서 사용."
---

# Report — 보고서·차트

## 1. 입력

- 시나리오명 또는 결과 폴더(`results/<OUT>`) — `results/summary.md`(run/knee 누적)에서 해당 시나리오 행 추출, 각 run의 `run.md`에서 상세(형상·명령·특이사항) 확보
- 무결성 exit=1 run은 collect 스킬에서 이미 제외된 상태여야 함 — 결과서에 중단 run을 섞지 않는다

## 2. 결과서 구조 (자동 생성 목차)

```text
1. 개요 — 시나리오·목적·테스트 일시
2. 테스트 범위 — | 시나리오 | VU | Ramp | Duration | 실행시각 |
3. VU별 추이 — VU별 TPS·p95·stdev 표 (summary.md 행 그대로)
4. knee·MAX TPS 판정 — knee 스킬 산출 인용(knee VU, MAX TPS req/s, 판정 근거 행)
5. 라벨별 스텝 분석 — run 폴더 jtl/aggregate 결과 기반 스텝별 TPS·p95
6. 병목 판정 — 아래 스켈레톤
7. 부록 — run 폴더 역추적 링크(results/<OUT> 상대경로) + evidence 목록
```

모든 수치는 표로 — 본문에는 해석만. 산출 경로: `docs/` 또는 사용자 지정.

## 3. 차트

`gen_stress_charts.py` 패턴 — **단일 스크립트, 외부 스타일 상속 없이 자체 생성**(하우스 스타일 상수 내장: tab10 계열 색상, 계열별 고유 마커, 포인트 값 라벨, 한글 폰트). matplotlib로:

- VU-TPS 곡선 — 포인트 마커 + 각 포인트 값 라벨, knee VU에 수직 보조선
- VU-p95 곡선 — 목표 SLA 기준선이 있다면 함께
- 시나리오 비교 막대 — 여러 시나리오 MAX TPS 나란히

```bash
python3 gen_charts.py results/summary.md --scenario <시나리오> --out <결과서 폴더>/
# 산출: <결과서 폴더>/vu-tps.svg, vu-p95.svg, scenario-compare.svg (PNG 옵션)
```

차트 데이터는 summary.md 표 값을 그대로 플롯 — 재계산 금지.

## 4. 병목 판정 스켈레톤

클라이언트 지표(JMeter) **확정 사실**만 먼저 기입:

| 구분 | 지표 | 값 | 근거 run |
| :-- | :-- | :-- | :-- |
| 확정(클라이언트) | knee VU / MAX TPS / p95 급증 시점 | summary.md·knee 판정 | results/<OUT> |
| 조회(서버) | HikariCP active/pending, CPU, vLLM 대기열 | Grafana 조회 가이드 | — |

서버 지표 조회 가이드(Grafana): knee 전후 시각창으로 HikariCP `hikaricp_connections_active/pending`, 노드 CPU, `vllm:num_requests_waiting` 대시보드 확인. **판정 문구는 사용자 확인 후 기입** — 스킬이 임의로 병목 결론을 내리지 않는다.

## 5. 경고

- 차트·수치는 `summary.md`·`run.md`(및 무결성 통과 jtl의 aggregate 출력)에서만 — **재해석·외삽 금지** (예: 측정 VU 범위 밖 TPS 추정)
- 결과서의 모든 표 값에 출처(summary.md 행 또는 results/<OUT>)를 남긴다
