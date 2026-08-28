---
name: bottleneck
description: "스트레스 테스트 병목 지점 판별. Grafana Platform API 대시보드로 느린 API를 먼저 식별하고, Proxmox·Grafana(NGINX·Redis·PostgreSQL·병목·AI 대시보드)·K8s pod 로그·dbhub의 8계층 체크로 병목 계층과 원인을 판정. '병목 찾기', '왜 느려', '느린 API 분석'에서 사용."
---

# Bottleneck — 병목 지점 판별

"무엇이 느린가 → 왜 느린가" 2단 진단. **모든 판정에는 근거(쿼리 + 관측값)를 남긴다.**

## 입력

- 런 폴더명(`results/...`) 또는 시간 창 — 폴더명 타임스탬프는 부하원 TZ(UTC) 기준일 수 있어 KST 환산 주의
- 시나리오 계열 (2/3-x 조회 · 4-x AI · 5-3 쓰기) — 8계층 중 vLLM은 4-x 계열만 조사
- 대시보드 UID 기본값은 ecoai 참조값 — `jmeter.json > metrics.dashboards`로 오버라이드

## 1단계 — 느린 API 식별 (Grafana Platform API 대시보드)

1. `get_dashboard_panel_queries(uid=<platform_api>)`로 패널 쿼리 확보
2. 런 윈도우로 `query_prometheus` range 조회 — `http_server_requests` P95/P99 **by uri 랭킹 상위 5**
3. spring_security 지연 패널로 **인증 병목 분리** (토큰 검증이 느린 것은 API 로직 병목이 아님)

→ **느린 API TOP N 확정. 이후 모든 계층 조사를 해당 uri로 한정한다** (전수 조사 금지).

## 2단계 — 8계층 추적 (순서대로)

| # | 계층 | 도구 | 판정 신호 |
| :- | :--- | :--- | :--- |
| 1 | 부하원 | Proxmox MCP (또는 pve exporter) | `pve_cpu_usage_ratio{id=~"qemu/<부하원VM>"}` ≥ 0.85가 60s 지속 → **측정 무효, 여기서 종료** |
| 2 | 게이트웨이 | Grafana NGINX ingress detail | `sum(rate(nginx_ingress_controller_requests[1m])) by (ingress, status)` — 5xx/429 급증은 상류 원인 후보 |
| 3 | pod | Grafana 병목 모니터링 | `rate(container_cpu_usage_seconds_total{pod=~"<앱>.*"})`, CPU throttling, **replicas 수 기록** |
| 3b | node HW | K8s MCP / Grafana node 패널 | pod이 안찬 **노드의 HW CPU·memory·disk** 사용률 — 공존 워크로드(예: dev PG가 앱과 같은 노드)의 자원 경합, 디스크 I/O 포화, memory pressure 판별 |
| 4 | 캐시/세션 | Grafana Redis | memory · evicted_keys · hit ratio · latency — 4-2 채팅(`chat:history:*`)·인증 세션 경로 |
| 5 | 커넥션 풀 | Grafana | `hikaricp_connections_active`가 max(**기본 10**, 설정 시 그 값)에 핀 + `pending > 0` → 풀 제약. pod CPU 여유 + pending↑ → 6계층으로 |
| 6 | DB | Grafana PostgreSQL/Data + dbhub | pg 활성 커넥션·슬로우. dbhub로 **식별된 API의 쿼리만** `EXPLAIN ANALYZE` — 실행시간 < 응답시간 1%면 DB 무죄 → 앱 레이어 |
| 7 | 디버그 메시지 | K8s MCP pod 로그 (없으면 `kubectl logs --since`) | 대상 pod에서 `Exception`·`WARN`·upstream 에러 검색 — 외부 API 4xx 본문(`API limit has been exceeded` 패턴)·N+1 힌트 |
| 8 | vLLM/GPU | Grafana AI 대시보드 (4-x만) | `vllm:num_requests_waiting/running`, `vllm:kv_cache_usage_perc` |

## 판정 트리

```text
부하원 포화          → 측정 무효 — 재실행
풀 핀 + pod CPU 포화  → 앱 replica 증설 후보
풀 핀 + CPU 여유
  + DB 슬로우        → DB 계층 (쿼리·연결)
  + 쿼리 무죠(<1%)    → 앱 레이어 (N+1 · JPA 매핑 · 동기 로깅)
vllm waiting ↑       → GPU 하드웨어 영역 (pod 대응 불가)
upstream 4xx/429     → 외부 API 의존 (쿼터·QPS)
```

## 산출

1. **계층별 판정표**: `| 계층 | 신호 | 관측값 | 쿼리/근거 | 판정 |`
2. 느린 API TOP N 표 (uri · P95 · 요청수)
3. 병목 결론 — 계층 + 원인 + 권고 (report 스킬의 병목 스켈레톤 입력)
4. 5-3 등 쓰기 경로면 run 폴더 §5.4 DB 정합 확인 권고

## 규칙

- MCP 부재/실패 시 fallback: Proxmox → pve exporter curl, K8s → kubectl, Grafana → 없으면 해당 계층 "확인 불가" 기록 (추측 금지)
- **쓰기 금지**: dbhub는 SELECT/EXPLAIN만, pod 수정·재시작 금지
- 모든 수치는 런 윈도우로 한정하고 idle 기준값(예: NGINX idle rate)과 대비해 기록
- 원인 미확정 시 "미확정 + 다음 프로브 제안"으로 마감 — 단정 금지 (2026-08-28 2-1 hold time 사례: 풀·쿼리 무죄여도 앱 버전 간 회귀 가능)
