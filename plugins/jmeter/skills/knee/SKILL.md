---
name: knee
description: "점진적 VU 상승 래더로 시나리오별 knee(포화 변곡점)와 MAX TPS를 탐색. 판정룰(이상/평탄/진행 우선순위 테이블)과 런 간 드레인 게이트를 내장해 자동 종료. 'knee 찾기', 'MAX TPS', '래더 테스트'에서 사용."
---

# Knee — 점진 VU 탐색

> **부하 발사 원칙 (절대 — spec §3)**: 부하는 항상 **원격 부하원**(keco-train-01/02 등 master→workers)에서만 발사한다. 래더의 각 포인트 실행도 run 스킬의 원격 실행 절차를 그대로 따른다. 로컬 jmeter는 `-g`(jtl→HTML 리포트) **후처리 전용** — 로컬에서 부하를 발사하지 않는다.

## 인자

`jmx`, `vu_start`(기본 2), `step_policy`(기본 geo2: 2,4,8,16,… / `list:10,30,50` 형식), `ramp`(60), `duration`(120)

**보간 래더 재개(중간 VU부터)**: 남은 포인트만 `list:`로 지정하고, 판정 기준이 될 직전 포인트 TPS를 인자와 함께 전달한다 (2026-08-28 실측 — 세션 중단 후 `list:16,50,100` 재개, 직전 8VU 1,544.9 기준 평탄 판정). 기존 세션의 인접 포인트(예: 1차 캠페인 30VU)도 참조해 교차검증한다.

## 사이클 (포인트마다 — run 스킬의 실행·집계를 재사용)

1. 현재 VU로 run 실행 + `../run/aggregate.py` 집계
2. 아래 판정표로 단일 판정 (첫 매칭 채택)

| 우선순위 | 판정 | 조건 (직전 대비) | 동작 |
| :-: | :-- | :-- | :-- |
| 1 | 이상 종료 | Err ≥ 5% 또는 절대 p95 ≥ 1s | 즉시 종료 |
| 2 | 이상 종료 | TPS 하락(>5%) + p95 ≥ 직전 2배 | 종료 — 직전 피크가 MAX TPS |
| 3 | 이상 재시 | Err 1~5% (1회만) | 동일 VU 재실행, 재발 시 종료 |
| 4 | 평탄 | TPS ±5% 이내 (하락 5% ~ 상승 5%) | 확인 2포인트 추가 후 종료 (잔여 스텝 생략) |
| 5 | 진행 | TPS +5% 초과 + Err < 1% + p95 < 1s | 다음 스텝 |

상승 구간(5)에서는 p95 배수 미적용. 첫 포인트(직전 없음)는 무조건 진행.

**계열별 예외·공백 보완 (2026-08-29 도그푸드 확정)**:

- **4-x 계열(vLLM)**: 응답시간이 본래 초 단위라 판정 1의 "절대 p95 ≥ 1s"를 적용하지 않는다 — TPS 추세 + p95 배수(판정 2)로만 판정한다.
- **하락 >5% + p95 <직전 2배 (판정표 공백)**: 1포인트 더 실행해 추세를 확인한다 — 연속 하락이면 직전 피크를 MAX TPS로 종료, 회복·상승이면 변동으로 보고 진행한다 (5-3 사례: 4VU 150.7 -> 6VU 133.6 -> 8VU 122.6 연속 하락으로 종료).

포인트 집계 호출 (run 스킬이 만든 결과 폴더 대상, 로컬 수집본):

```bash
python3 ../run/aggregate.py results/<OUT>/result.jtl <ramp>
```

## 런 간 드레인 게이트 (다음 포인트 전)

최소 120s 대기 + 잔여 확인 — `sum(rate(nginx_ingress_controller_requests[1m])) < 1`, `hikaricp_connections_pending == 0` (인스턴트), 4-x 계열 후 `vllm:num_requests_waiting == 0`. 미통과 시 30s 간격 재확인(최대 10회 후 경고하고 진행). 쿼리 창구는 jmeter.json metrics.

```bash
curl -s "<metrics_url>/api/v1/query" --data-urlencode 'query=sum(rate(nginx_ingress_controller_requests[1m]))'
curl -s "<metrics_url>/api/v1/query" --data-urlencode 'query=hikaricp_connections_pending'
curl -s "<metrics_url>/api/v1/query" --data-urlencode 'query=vllm:num_requests_waiting'   # 4-x 계열 후
# metrics URL이 로컬에서 직접 닿지 않으면 부하원 ssh 경유:
ssh <master> "curl -s '<metrics_url>/api/v1/query' --data-urlencode 'query=...'"
```

## 산출

VU-TPS 곡선 표 + knee(VU)·MAX TPS(req/s) 판정 + 각 포인트 summary.md 누적(run이 처리)
