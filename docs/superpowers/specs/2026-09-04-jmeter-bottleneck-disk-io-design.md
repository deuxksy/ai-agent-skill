# JMeter Bottleneck Disk I/O Design

## 목적

`jmeter:bottleneck`이 기존 8계층 진단에서 뭉뚱그려 다루던 디스크를 local block device와 Ceph 분산 스토리지로 분리하고, 각 경로의 read/write 병목을 계층별 판정표에 반드시 드러내도록 한다.

## 현재 문제

현재 `3b node HW` 행은 `disk`를 한 단어로만 언급한다. 수집 지표, local/Ceph 귀속 방법, 병목 판정 조건이 없어 실행 에이전트가 다음 중 하나로 흔들린다.

- 노드 CPU만 보고 디스크 계층을 생략한다.
- local과 Ceph를 한 행에 합쳐 원인 위치를 특정하지 못한다.
- 높은 처리량만으로 포화라고 단정한다.
- Ceph 지표가 없는데도 정상 또는 병목으로 추측한다.

변경 전 독립 시나리오에서도 local/Ceph가 `Node HW` 한 행에 합쳐졌고, 정확한 PromQL과 판정 기준이 제시되지 않았다.

## 설계

### 계층 구조

기존 순서를 유지하면서 `3c Disk I/O`를 추가한다. 이 계층은 최종 판정표에서 아래 두 행으로 출력한다.

- `Disk local`: 앱 pod가 실제로 사용하는 node/device의 read/write
- `Disk Ceph`: 앱 PVC가 Ceph를 사용할 때 client/pool/OSD read/write

pod writable layer, `emptyDir`, `hostPath`, PVC를 모두 확인해 요청 경로를 먼저 귀속한다. PVC는 StorageClass/PV CSI driver까지, 나머지 경로는 kubelet/node/container-runtime mount metadata의 source까지 추적한다. pod node와 mount/source를 해당 node-exporter instance/device에 읽기 전용 근거로 정확히 연결하지 못하면 local 행은 `미관측`이며, 이름이 비슷한 device를 추측하지 않는다. local과 Ceph 중 해당 저장소 유형을 사용하지 않음이 확인된 경우에만 `비해당`으로 판정한다.

### Local 관측 계약

런 윈도우와 idle 기준값에서 다음을 read/write별로 비교한다.

- 처리량: `node_disk_read_bytes_total`, `node_disk_written_bytes_total`
- IOPS: `node_disk_reads_completed_total`, `node_disk_writes_completed_total`
- 평균 I/O 지연: read/write time 합계를 completed ops로 나눈 값
- 장치 busy: `node_disk_io_time_seconds_total`
- queue pressure: `node_disk_io_time_weighted_seconds_total`

앱 pod의 실제 node/device만 대상으로 하고 loop, ram, fd 같은 비실장 장치는 제외한다. dm/md/NVMe처럼 실제 경로일 수 있는 장치는 이름만 보고 제외하지 않는다. operation rate가 0인 방향은 IOPS 0, latency `N/A (no operations)`로 기록한다. 이는 metric 부재가 아니며 0/0 latency를 계산하거나 `미관측`으로 바꾸지 않는다.

### Ceph 관측 계약

먼저 Grafana 패널 또는 Prometheus metric discovery로 실제 배포의 metric 이름과 label을 확인한다. 확보 가능한 경우 다음 신호를 read/write별로 수집한다.

- client 또는 pool read/write bytes와 ops
- OSD read/write op latency
- slow ops 또는 op queue/backlog
- OSD별 utilization/latency 불균형
- Ceph health 상태

특정 exporter 명칭을 추측해 없는 metric을 사실처럼 제시하지 않는다. 풀 전체 수치만 있으면 대상 PVC의 pool과 연결되는지 확인한 뒤 근거로 사용한다.

### 판정 계약

처리량 또는 IOPS가 높은 사실만으로 병목이라 판정하지 않는다.

- `무죄`: 런 중 평균 지연·busy/queue 또는 slow ops가 idle 대비 유의하게 악화되지 않고 API P95 상승과 시간상 겹치지 않음
- `주범 후보`: 같은 read/write 방향에서 I/O 지연과 busy/queue(또는 Ceph slow ops/backlog)가 함께 악화되고 API P95 상승 구간과 겹침
- `경합 후보`: 특정 node/device/OSD에만 부하와 지연이 편중되고 공존 워크로드 또는 OSD 불균형 근거가 있음
- `미관측`: 필요한 metric, panel, exporter가 없어 판정 불가
- `비해당`: volume 경로 확인 결과 해당 저장소를 사용하지 않음

고정 임계값은 환경 차이로 오판할 수 있으므로 보조 신호로만 쓴다. 장치 busy가 지속적으로 80% 이상이면 포화 후보지만, 병목 확정에는 지연/queue와 API P95의 동시 악화가 필요하다. counter는 반드시 `rate()` 또는 `irate()`로 변환한다.

### 출력 계약

계층별 판정표는 관측 순서와 무관하게 `Disk local`, `Disk Ceph` 두 행을 항상 포함한다. 각 행에는 read/write를 분리한 관측값, 대상 node/device 또는 pool/OSD, 사용한 쿼리/패널, `무죄 | 주범 후보 | 경합 후보 | 미관측 | 비해당` 중 하나를 기록한다.

예상 요약 형태:

```text
3c Disk local  read ... · write ... · await ... · busy ...  무죄
3c Disk Ceph   pool ... · r_lat ... · w_lat ... · slow_ops ...  주범 후보
```

## 범위

- 수정: `plugins/jmeter/skills/bottleneck/SKILL.md`
- 추가: 이 설계 문서와 대응 구현 계획
- 제외: exporter 설치, Grafana dashboard 변경, 실제 클러스터 쓰기, 플러그인/마켓플레이스 버전 변경

## 검증

1. 변경 전과 동일한 5-3 진단 시나리오로 실행해 두 disk 행, read/write 근거, local/Ceph 귀속, 미관측 처리가 모두 나타나는지 확인한다.
2. skill validator로 YAML frontmatter와 스킬 구조를 검사한다.
3. `review:verify`로 spec/plan과 최종 diff를 격리 snapshot에서 교차검증한다.
