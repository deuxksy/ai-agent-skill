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
| 3c | Disk I/O | Grafana/Prometheus node·Ceph 패널 | storage path 귀속 후 local block device와 Ceph를 read/write별로 분리 관측·판정 (아래 계약 참조) |
| 4 | 캐시/세션 | Grafana Redis | memory · evicted_keys · hit ratio · latency — 4-2 채팅(`chat:history:*`)·인증 세션 경로 |
| 5 | 커넥션 풀 | Grafana | `hikaricp_connections_active`가 max(**기본 10**, 설정 시 그 값)에 핀 + `pending > 0` → 풀 제약. pod CPU 여유 + pending↑ → 6계층으로. **acquire P95**(`hikaricp_connections_acquire_seconds`)도 함께 기록 — 응답시간 분해의 직접 재료 (2026-08-29 3-4 실측: active 10 핀·pending 20·acquire P95 416ms) |
| 6 | DB | Grafana PostgreSQL/Data + dbhub | pg 활성 커넥션·슬로우. dbhub로 **식별된 API의 쿼리만** `EXPLAIN ANALYZE` — 실행시간 < 응답시간 1%면 DB 무죄 → 앱 레이어. **분해 신호: `spring_data_repository_invocations_seconds` P95(by repository,method)** — repository P95 − EXPLAIN 실행시간 = 앱(JPA 매핑·트랜잭션) 영역 (3-4 실측: repository 523ms − 쿼리 23ms → 앱 레이어 확정) |
| 7 | 디버그 메시지 | K8s MCP pod 로그 (없으면 `kubectl logs --since`) | 대상 pod에서 `Exception`·`WARN`·upstream 에러 검색 — 외부 API 4xx 본문(`API limit has been exceeded` 패턴)·N+1 힌트 |
| 8 | vLLM/GPU | Grafana AI 대시보드 (4-x만) | `vllm:num_requests_waiting/running`, `vllm:kv_cache_usage_perc` |

### 3c Disk I/O 조사 계약

```text
3c Disk I/O
├─ storage path 귀속: pod writable layer/emptyDir/hostPath/PVC → node mount/source 또는 PV/CSI → local 또는 Ceph
├─ local: read/write B/s, IOPS, avg latency, busy, weighted queue
├─ Ceph: client/pool read/write B/s·ops, OSD latency, slow ops/backlog, imbalance, health
└─ verdict: 무죄 | 주범 후보 | 경합 후보 | 미관측 | 비해당
```

먼저 대상 pod의 **모든 쓰기 가능 경로**를 귀속한다: container writable layer, `emptyDir`, `hostPath`, PVC volume. pod의 `spec.nodeName`와 각 container `mountPath`를 확보하고, PVC는 PVC → PV → StorageClass/CSI driver 및 CSI node mount source까지, writable layer/`emptyDir`/`hostPath`는 kubelet·node·container-runtime의 read-only mount metadata에서 source까지 추적한다. 이 Kubernetes storage inspection은 read-only `get`/`describe` 또는 read-only MCP query만 사용하며 `apply`/`patch`/`delete`/`edit`는 금지한다. 각 local 후보는 **pod node + mount/source → 해당 node-exporter instance + exact `device` label**의 읽기 전용 근거로 연결해야 한다. node-exporter device 이름, node, CSI device를 추측하거나 유사 이름으로 대체하지 않는다. 이 exact mapping을 증명할 수 없으면 local 행은 `미관측`이다. local/Ceph 행의 `비해당`은 해당 저장소 유형을 쓰기 가능 경로에서 사용하지 않음이 확인된 경우에만 쓴다(예: `readOnlyRootFilesystem`이고 모든 write path가 `emptyDir.medium: Memory`인 경우 local block storage 미사용). 모든 수치는 런 윈도우와 idle 기준값에 대해 read/write를 분리해 남긴다.

- **Disk local** — exact mapping이 증명된 실제 pod node/device만 대상으로 `node_disk_read_bytes_total`, `node_disk_written_bytes_total`, `node_disk_reads_completed_total`, `node_disk_writes_completed_total`, `node_disk_read_time_seconds_total`, `node_disk_write_time_seconds_total`, `node_disk_io_time_seconds_total`, `node_disk_io_time_weighted_seconds_total`을 확인한다. loop/ram/fd 등 비실장 장치는 제외하되 dm/md/NVMe처럼 실제 경로일 수 있는 장치는 이름만으로 제외하지 않는다. counter는 반드시 `rate()` 또는 `irate()`로 변환한다. read 평균 지연은 `rate(node_disk_read_time_seconds_total[window]) / rate(node_disk_reads_completed_total[window])`, write 평균 지연은 `rate(node_disk_write_time_seconds_total[window]) / rate(node_disk_writes_completed_total[window])`으로 계산한다. 단, 해당 completed-operation rate가 0이고 counter가 관측되면 그 방향은 **IOPS 0, latency `N/A (no operations)`**로 기록한다. 0/0을 latency 결측으로 읽거나 `미관측`으로 바꾸지 않는다; metric 자체가 없거나 exact mapping이 없을 때만 `미관측`이다. busy는 `rate(node_disk_io_time_seconds_total[window])`, weighted queue는 `rate(node_disk_io_time_weighted_seconds_total[window])`으로 기록한다.
- **Disk Ceph** — 먼저 Grafana dashboard query 또는 Prometheus metric discovery로 실제 배포의 metric 명칭과 label을 확인한다. 확인된 metric으로 대상 PVC의 pool 연결을 근거화한 뒤 client/pool read/write bytes·ops, OSD read/write op latency, slow ops/backlog, OSD별 utilization/latency imbalance, Ceph health를 수집한다. exporter 명칭이나 metric을 추측해 사용하지 않는다. 확인된 read 또는 write operation rate가 0이면 해당 방향은 **IOPS 0, latency `N/A (no operations)`**로 기록하며, 이를 metric 부재로 취급하지 않는다.
- **판정** — 처리량 또는 IOPS 단독 상승은 병목 근거가 아니다. `무죄`는 지연·busy/queue 또는 slow ops가 idle 대비 악화되지 않고 API P95 상승과 시간상 겹치지 않을 때, `주범 후보`는 같은 read/write 방향의 지연과 busy/queue(또는 Ceph slow ops/backlog)가 함께 악화되며 API P95와 겹칠 때, `경합 후보`는 특정 node/device/OSD에만 부하·지연이 편중되고 공존 워크로드 또는 OSD 불균형 근거가 있을 때 사용한다. 필요한 관측이 없거나 local exact mapping이 증명되지 않으면 `미관측`이다. `비해당`은 해당 저장소 유형을 쓰기 가능 경로에서 사용하지 않음이 검증된 경우에만 쓴다. 장치 busy 80% 이상은 후보 신호일 뿐이며 지연/queue와 API P95의 동시 악화 없이는 확정하지 않는다.

## 판정 트리

```text
부하원 포화          → 측정 무효 — 재실행
풀 핀 + pod CPU 포화  → 앱 replica 증설 후보
풀 핀 + CPU 여유
  + DB 슬로우        → DB 계층 (쿼리·연결)
  + 쿼리 무죠(<1%)    → 앱 레이어 (N+1 · JPA 매핑 · 동기 로깅)
vllm waiting ↑       → GPU 하드웨어 영역 (pod 대응 불가)
upstream 4xx/429     → 외부 API 의존 (쿼터·QPS)
Disk local 지연+busy/queue ↑ + API P95 동시 상승 → local 디스크 주범 후보
Disk Ceph slow ops/backlog·지연 ↑ + API P95 동시 상승 → Ceph 주범 후보
throughput/IOPS만 ↑  → 디스크 병목 확정 금지 (추가 지연·queue 상관관계 필요)
```

## 산출

1. **계층별 판정표**: `| 계층 | 신호 | 관측값 | 쿼리/근거 | 판정 |` — 관측 순서와 무관하게 아래 두 행을 항상 포함한다.
   - `Disk local`: 대상 node/device, read/write B/s·IOPS·평균 지연·busy/weighted queue, 귀속 근거, 쿼리/패널, `무죄 | 주범 후보 | 경합 후보 | 미관측 | 비해당` 중 하나
   - `Disk Ceph`: 대상 pool/OSD, read/write B/s·ops·지연·slow ops/backlog·imbalance·health, 귀속 근거, 쿼리/패널, `무죄 | 주범 후보 | 경합 후보 | 미관측 | 비해당` 중 하나
2. 느린 API TOP N 표 (uri · P95 · 요청수)
3. 병목 결론 — 계층 + 원인 + 권고 (report 스킬의 병목 스켈레톤 입력)
4. 5-3 등 쓰기 경로면 run 폴더 §5.4 DB 정합 확인 권고

## 규칙

- MCP 부재/실패 시 fallback: Proxmox → pve exporter curl, K8s storage inspection → read-only `kubectl get`/`describe`, Grafana → 없으면 해당 계층 "확인 불가" 기록 (추측 금지). Disk local/Ceph에 필요한 metric·panel·exporter가 없거나 조회가 실패하면 각 최종 행에 시도한 query/panel과 unavailable-metric 근거를 남기고 판정을 반드시 `미관측`으로 기록한다.
- **쓰기 금지**: dbhub는 SELECT/EXPLAIN만, pod 수정·재시작 금지
- 모든 수치는 런 윈도우로 한정하고 idle 기준값(예: NGINX idle rate)과 대비해 기록
- 원인 미확정 시 "미확정 + 다음 프로브 제안"으로 마감 — 단정 금지 (2026-08-28 2-1 hold time 사례: 풀·쿼리 무죄여도 앱 버전 간 회귀 가능)
