# JMeter Bottleneck Disk I/O Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** `jmeter:bottleneck`이 local 및 Ceph read/write 병목을 근거 기반으로 분리 판정하고 결과표에 항상 표시하게 한다.

**Architecture:** 기존 8계층 추적 흐름에 `3c Disk I/O` 관측 계약을 삽입한다. storage path를 먼저 귀속한 뒤 local block-device와 Ceph의 read/write 신호를 각각 수집하고, 처리량 단독이 아니라 지연·queue/slow-ops·API P95의 시간 상관으로 판정한다.

**Tech Stack:** Markdown Agent Skill, PromQL, Kubernetes storage metadata, Grafana/Prometheus

**Spec:** `docs/superpowers/specs/2026-09-04-jmeter-bottleneck-disk-io-design.md`

## Global Constraints

- 모든 판정에는 런 윈도우의 쿼리 또는 패널과 관측값을 남긴다.
- final layer table에는 `Disk local`과 `Disk Ceph`를 항상 별도 행으로 출력한다.
- read/write를 분리하고 storage path를 node/device 또는 pool/OSD에 귀속한다.
- 높은 throughput/IOPS만으로 병목을 판정하지 않는다.
- metric 부재는 추측하지 않고 `미관측`, 미사용 경로는 `비해당`으로 기록한다.
- dbhub와 클러스터는 read-only로 유지한다.
- 플러그인 및 marketplace version은 변경하지 않는다.

---

### Task 1: Disk I/O 진단 계약 추가

**Files:**
- Include: `docs/superpowers/specs/2026-09-04-jmeter-bottleneck-disk-io-design.md`
- Include: `docs/superpowers/plans/2026-09-04-jmeter-bottleneck-disk-io.md`
- Modify: `plugins/jmeter/skills/bottleneck/SKILL.md`
- Verify: `plugins/jmeter/skills/bottleneck/SKILL.md`

**Interfaces:**
- Consumes: 기존 `2단계 — 8계층 추적`, 판정 트리, 산출물 계약
- Produces: `3c Disk I/O` 조사 절차와 `Disk local`/`Disk Ceph` 최종 행

- [x] **Step 1: 변경 전 실패 증거 확인**

동일한 5-3 입력을 현재 스킬에 적용했을 때 local/Ceph가 `Node HW`에 합쳐지고 정확한 PromQL·판정 계약이 빠지는지 기록한다.

Expected: 두 디스크 행이 강제되지 않아 구조적 요구를 충족하지 못한다.

- [x] **Step 2: 최소 스킬 변경 구현**

`SKILL.md`에 다음을 추가한다.

```text
3c Disk I/O
├─ storage path 귀속: pod writable layer/emptyDir/hostPath/PVC → node mount/source 또는 PV/CSI → local 또는 Ceph
├─ local: read/write B/s, IOPS, avg latency, busy, weighted queue
├─ Ceph: client/pool read/write B/s·ops, OSD latency, slow ops/backlog, imbalance, health
└─ verdict: 무죄 | 주범 후보 | 경합 후보 | 미관측 | 비해당
```

counter에는 `rate()`/`irate()`를 적용하고, local 평균 지연은 time counter rate를 completed counter rate로 나눈다. operation rate가 0이면 IOPS는 0, latency는 `N/A (no operations)`로 기록하며 이를 telemetry 부재로 취급하지 않는다. busy 80%는 후보 신호로만 사용하며 지연/queue와 API P95 동시 상승 없이는 확정하지 않는다. Ceph metric 명칭은 dashboard query 또는 discovery로 확인한 뒤 사용한다.

- [x] **Step 3: 판정 트리와 산출물 계약 연결**

판정 트리에 local/Ceph 분기를 추가하고, 계층별 판정표에 `Disk local`과 `Disk Ceph` 두 행을 항상 포함하도록 명시한다. 두 행에는 read/write 관측값, 귀속 대상, 근거, 판정을 기록한다.

- [x] **Step 4: 변경 후 행동 검증**

변경 전과 동일한 5-3 요청으로 새 스킬을 적용한다.

Expected:

```text
Disk local: node/device와 read/write B/s·IOPS·latency·busy/queue가 있거나 미관측/비해당
Disk Ceph: pool/OSD와 read/write·latency·slow ops/backlog가 있거나 미관측/비해당
```

두 행 모두 존재하고 throughput 단독으로 병목을 단정하지 않아야 한다.

- [x] **Step 5: 구조 검증**

Run:

```bash
python3 - <<'PY'
from pathlib import Path

path = Path("plugins/jmeter/skills/bottleneck/SKILL.md")
text = path.read_text(encoding="utf-8")
parts = text.split("---\n", 2)
assert len(parts) == 3 and parts[0] == "", "YAML frontmatter delimiters are required"
frontmatter, body = parts[1:]
assert "name: bottleneck" in frontmatter and "description:" in frontmatter
required = (
    "3c Disk I/O", "Disk local", "Disk Ceph", "pod writable layer",
    "emptyDir", "hostPath", "node_disk_read_bytes_total",
    "node_disk_written_bytes_total", "slow ops", "미관측", "비해당",
    "N/A (no operations)",
)
missing = [token for token in required if token not in body]
assert not missing, f"missing contract tokens: {missing}"
print("frontmatter and Disk I/O contract: OK")
PY
rg -n '3c|Disk local|Disk Ceph|pod writable layer|emptyDir|hostPath|node_disk_(read|write|io_time)|slow ops|N/A \(no operations\)|미관측|비해당' plugins/jmeter/skills/bottleneck/SKILL.md
git diff --check
```

Expected: repository-relative frontmatter/contract validation, required-contract search, and whitespace check all exit 0.

Historical caveat: the previously recorded `quick_validate.py` invocation used a personal Codex installation path and therefore is not a portable validation requirement. The repository-relative command above is the current validation procedure; it has no Codex-specific path or dependency.

- [x] **Step 6: Review 교차검증**

`review:verify`를 사용해 spec/plan 및 최종 diff를 격리 snapshot에서 검증한다. blocker가 있으면 수정 후 동일 범위를 재검증한다.
